# Workload sizing for the GPU purchase

Written 10 Nov 2026 about 11:40Z. We read logs and files only. Nothing was edited, no model was called, no GPU work ran.

Window: 8 Nov 11:00Z to 10 Nov 11:30Z (the last two days). Calendar day 9 Nov is used where a full 24 hours is needed, because the Mac was dark from 05:00Z to 09:23Z on 10 Nov after a reboot.

Machine facts read on the Mac: Apple M5 Max, 40-core GPU, 48 GB (`sysctl`, `system_profiler`). mlx_lm 0.31.3. Armature: RTX 3080 10 GB holding qwen3:8b (judge), with granite-guardian-4.1-8b and the gemma3:4b Ear on its CPU (`seats.json`, `judge_swap/gg_server.py`).

Exclusion rule: no text column or text line naming a `local.json` `excluded_names` entry was read into this file. Rows were filtered in code before printing. Only timing and count columns are used. scheduler.log, calib_train.log and pref.log had no such lines. 14 of 69 flywheel_ledger lines do, and that ledger has no timing columns, so it is not used.

Sources: `sage_v/scheduler.log`, `train/calib_train.log`, `train/harvest/*/{prompts,samples,judged,stats}.json` (file times and counts), `train/harvest_out_*.log`, `train/live_*/train_try*.log` (mlx_lm iteration lines), `pref/pref.log`, `pref/runs/*/{job,result}.json`, `promotions.jsonl`, `sage_v.db` (opened read-only: `turns.ms`, `pq` counts), `sage_v.log` (COUNCIL_WINDOW lines only), `proposed/council_yield/REPORT.md`, `offload/armature_sampler/` (parity file, sample.py notes), `research/PARALLEL_GPU_PLAN.md` (token counts per row), `gap_corpus/`, `qubit_corpus/` (row counts and sizes).

## Headline

1. Today's rate is explained by one product: Mac training-GPU minutes per turn times the share of the day the Mac is allowed to train. On 9 Nov the Mac ran training jobs 11.1 h of 24 (46%), and a turn costs about 61 to 67 Mac-GPU minutes. 24 h × 46% ÷ 64 min ≈ 10.4 turns a day. Measured: 10 paired verdicts and 12 SFT runs on 9 Nov.
2. The 46% is set mostly by the council window (`sage_v.py` line 154: 3 flywheel cycles after every GPU job, cap 3600 s), not by the GPU. Flywheel cycles run a median 765 s (p90 1,413 s), so 3 cycles take 38 to 70 min. The cap was hit 11 times between 9 Nov 04:45Z and 10 Nov 02:31Z.
3. Armature is the second wall. The judge pass after sampling runs a median 27 min per harvest at one claim per call (2.0 to 11 s a claim, 34 s under contention). It sits outside the Mac lock, so it sets turn latency more than turn count.
4. Any of the three cards removes both walls for today's 8B work, because training leaves the Mac (no `PAUSE_MAC`, no window needed) and the judges can move onto the card. The RTX PRO 6000 and 2x RTX 5090 land close together on today's jobs. The 96 GB card is the only one of the three that also runs a 70B teacher, a 70B judge and 70B QLoRA at useful speed. The DGX Spark fits everything in memory but its 273 GB/s makes 70B decode slow (about 5 tokens a second per stream).
5. After a purchase the next limit is a rule, not hardware. 8 of 12 paired verdicts in the window ended "not released (waits on live need_n)", and those seats wait for 58 to 128 live council claims at 22 to 72 a day per seat.

## 1. Time budget of one training turn

A turn (`train_scheduler.py --turn`) is: fresh paired set, harvest 1 to 3 (prompt build, sampling, judge pass, keep), SFT (`train_live.py`), DPO (`train_pref.py`: pair build and judge, then GPU), paired eval (`realjob_eval.py` generation, judge, `rejudge_paired.py`), promotion (`promote.py`). Up to four seats are in flight (`MAXT = 4`), and every Mac GPU step takes `.train.lock`, one at a time.

### Per stage, 8B dense seats (hermes3, mistral, granite), K = 8 era

| Stage | Median | Range | n | Machine it runs on | What it waits on |
|---|---|---|---|---|---|
| Fresh paired set (+ vault on first turn) | 0.8 min | 0.3 to 11.2 min | 9 | Mac CPU, library `/search` | bge-m3 embeds on Ollama :11500 (the 8 to 11 min cases sat inside :11500 stalls) |
| Harvest prompt build (48 prompts) | 0.4 min | 0.2 to 1.8 min (one 32 min library stall) | 30 | Mac CPU, library | same |
| Wait before sampling (council window + lock) | about 20 min | 0 to 60+ min | | none | the council window and other seats' GPU jobs |
| Sampling, 48 prompts × 8 = 384 samples (gen.py to samples.json) | 11.2 min | 10.0 to 14.6 min (granite 17.8) | 11 | Mac GPU | GPU compute (prefill) and bandwidth (decode) |
| Judge pass (qwen3:8b on Armature GPU, in parallel with granite-guardian on Armature CPU + deberta on Mac CPU) | 26.8 min | 12.5 to 77 min, 187 min under contention | 10 | Armature | the 3080 and Armature's CPU, one claim per call |
| Keep + write rows | under 0.1 min | | | Mac CPU | none |
| Wait before SFT (window + lock) | about 50 min | 0 to 81 min | | none | window, other seats |
| SFT (all 8B runs in window) | 31.6 min (1,896 s) | 25 to 63 min | 10 | Mac GPU | GPU compute |
| SFT at today's 300-iteration cap | 25 to 35 min | (hermes 300 it 2,084 s, mistral 209 it 1,517 s) | 2 | Mac GPU | GPU compute |
| DPO pair build + judge | 6 min | 1 to 216 min (1 min since pairs reuse harvest judgments, 10 Nov) | 8 | Armature | judge |
| DPO lock wait | 14 min | 2.4 to 72 min | 7 | none | other seats |
| DPO GPU child, 8B | 13.1 min | 10.7 to 16.0 min (train part 7.4 to 9.6 min) | 3 | Mac GPU | compute; gencheck generation is bandwidth |
| Paired eval generation (adapter arm, base arm cached) | 5.0 min | 5.0 to 10.5 min | 2 | Mac GPU | bandwidth (decode, chunks of 4) |
| Paired eval judge + rejudge | 7 min | 7 to 16 min | 2 | Armature | judge |
| Promotion (paired line to `LIVE ... on :88xx`) | 15 s | 2 to 16 s | 6 | Mac | MLX server reload |

3B (llama3.2) and ERNIE (21B total, 3B active), same stages where they differ:

| Stage | llama3.2:3b | ernie4.5:21b-a3b |
|---|---|---|
| Sampling 384 | 7.4 min (6.8 to 7.9, n 5) | 15.9 min (13.3 to 17.7, n 5). Outputs are 3.5× longer (about 440 vs 130 tokens) |
| Judge pass | 2.5 to 29 min | 18 to 77 min |
| SFT | 14 to 27 min (841 to 1,632 s, 3.3 s per iteration) | never ran. Every ERNIE harvest kept too few rows |
| DPO GPU | 4.3 to 8.8 min (255 to 527 s) | none |

### Whole turns

| Turn kind | n | Median | Range |
|---|---|---|---|
| Turns that reached a paired verdict | 13 | 227 min (3.8 h) | 122 to 514 min |
| Full SFT + DPO + paired turns | 4 | 338 min | 202 to 514 min |
| Turns that stopped early (train rc 1 or 4, refused promote) | 7 | 69 min | 59 to 243 min |

Where the time went in the four full SFT + DPO turns (1,392 turn-minutes in all, from scheduler.log, pref.log and harvest file times):

| Share | Minutes | What |
|---|---|---|
| Waiting for the Mac lock and the council window | about 630 (45%) | other seats' jobs plus window gaps |
| Armature judging on the critical path | about 450 (32%) | harvest 128, DPO pairs 276 (one 3.6 h contention event, now gone with pair reuse), paired about 50 |
| Mac GPU work | about 270 (19%) | sampling 45, SFT 150, DPO 44, paired generation 30 |
| Prompt and paired-set builds | about 45 (3%) | library |

The best recent turn (hermes, 9 Nov 23:23Z to 10 Nov 02:45Z, 202 min) had about 108 min of work and about 103 min of waiting (22 min before sampling, 81 min before SFT).

### Mac GPU accounting for 9 Nov (interval union of every training GPU job)

| Job | Hours |
|---|---|
| SFT | 6.36 |
| Harvest sampling | 3.33 |
| Paired eval generation (approximate, 6 min per verdict) | 1.00 |
| DPO | 0.59 |
| Union, training busy | 11.09 h (46%) |
| Gaps | 42 gaps, 12.5 h. 16 of them are 14 to 112 min long and hold 12.0 h |

Mac-GPU minutes per 8B turn: sampling 11.2 + SFT 31.6 + DPO 13.1 + paired generation 5 ≈ 61 min. Measured over 9 Nov including failed turns and multiple harvests: 11.09 h ÷ 10 verdicts = 67 min.

## 2. What limits each stage, and how it scales

### The arithmetic we start from (our measured tokens and steps)

- SFT rows: 1,927 tokens mean (hermes), 1,899 (llama), 2,293 (granite). 92% of each row is prompt. Batch 2, rank 8, 16 of 32 layers adapted, gradient checkpointing (`train_live.py` lines 104 to 110, `PARALLEL_GPU_PLAN.md`).
- One 8B SFT turn at the 300-iteration cap: 300 × 2 × 1,927 = 1.16M tokens processed. mlx_lm "Trained Tokens" for that run was 78,825 (answer tokens only, the prompt is masked).
- FLOP model for LoRA on the top half of the layers with checkpointing: about 2N per token forward through all layers, plus about 2N for recompute and backward through the adapted half. So about 4N per token. 4 × 8.0e9 × 1.16M = 3.7e16 FLOP.
- Measured on the Mac: 2,084 s. So the Mac delivers 3.7e16 ÷ 2,084 = 17.8 TFLOPS effective on SFT, or 555 processed tokens a second. llama 3B: 490 iterations × 2 × 1,899 = 1.86M tokens in 1,632 s, 1,140 tokens a second.
- Harvest sampling: 384 prompts of about 1,750 tokens (prompt files 6,700 to 7,100 characters. The parity file shows 1,480 to 1,881 prompt tokens). Prefill = 384 × 1,750 = 672k tokens, of which only 48 × 1,750 = 84k are unique (each prompt is copied 8 times). Decode: hermes averages 509 characters, about 130 tokens a sample, so 50k tokens. ERNIE about 440 tokens, 169k. gen.py runs chunks of 8 and every chunk waits for its longest sample (max 700).
- Prefill FLOPs: 2 × 8e9 × 672k = 1.1e16. If forward-only runs at 1.3 to 2× SFT's per-FLOP rate (no backward), that is 5 to 8 min on the Mac, and decode of 48 chunks at their longest sample makes up the other 3 to 6 min. That matches the measured 10 to 13.5 min. So about 60% of sampling is redundant prefill.
- DPO: each iteration is one pair, two sequences of about 2k tokens. hermes run 1: 40 iterations, 160k tokens in 463 train-seconds, 345 tokens a second (139 for mistral, where held-out checks dominate). Around it, 150 to 380 s go to loading, reference scoring and gencheck generation.
- Judge: one claim per call. Prompt about 500 to 800 tokens (claim, quote, chunk excerpt), output about 40 to 60 tokens. About 300 to 425 claims per K = 8 harvest.
- Paired eval: 60 prompts × about 1,800 tokens prefill, up to 700 out, temperature 0, chunks of 4.

### Hardware we scale to

| | Mac M5 Max (today) | RTX PRO 6000 96 GB | DGX Spark 128 GB | 2× RTX 5090 32 GB |
|---|---|---|---|---|
| Memory bandwidth | about 550 to 620 GB/s (assumed. Not measured here. M4 Max was 546) | 1,792 GB/s | 273 GB/s | 1,792 GB/s each |
| BF16 dense peak | not published | about 500 TFLOPS (derived from vendor FP4 figure) | about 125 TFLOPS (derived) | about 209 TFLOPS each (FP32 accumulate) |
| Effective on LoRA SFT | 17.8 TFLOPS (measured) | 100 to 175 (20 to 35% of peak, assumed) | 25 to 44 | 42 to 73 each |
| Compute-bound speed vs Mac | 1× | 5.6 to 9.8× | 1.4 to 2.5× | 2.4 to 4.1× per card |
| Decode-bound speed vs Mac | 1× | about 3× | about 0.45× | about 3× per card |
| Memory free for our jobs | 48 GB shared with four MLX seats, Ollama :11500 and gg_server. Swap was 10.8 of 11.3 GB on 10 Nov | 96 GB | 128 GB shared with the OS | 32 GB per card |

Peak figures are the ones in `HARDWARE_OPTIONS_20261110.md` in this folder. The effective range is our assumption. The first real run on any of these replaces it.

### Stage by stage (8B seat)

| Stage | Limit today | RTX PRO 6000 | DGX Spark | 2× RTX 5090 |
|---|---|---|---|---|
| Prompt and paired-set builds (0.4 to 11 min) | Mac CPU and the library, whose query embed waits on Ollama :11500 | unchanged. Gets faster only because :11500 stops fighting the training jobs for memory | unchanged | unchanged |
| Sampling (11.2 min) | Compute (redundant prefill) then bandwidth (decode in chunks of 8) | vLLM with prefix caching: 84k unique prefill tokens × 1.6e10 = 1.3e15 FLOP, 8 to 13 s. Decode: all 384 in one continuous batch, at most 700 steps, each step reads 16 GB of bf16 weights plus live KV (under 30 GB) in under 25 ms, so under 18 s. With load, **1.5 to 3 min** | Prefill with prefix cache 30 to 55 s (without it, 1.1e16 FLOP is 4 to 7 min). Decode at 273 GB/s: 60 ms a step for weights plus KV, 70 to 120 s. **3 to 6 min** | **1.5 to 3 min** on the sampling card. 32 GB minus 16 GB of weights leaves 16 GB of KV, enough with prefix sharing |
| Judge pass (26.8 min) | Serial calls into a 3080 that also serves the council (97% busy per the brief), and granite-guardian on Armature's CPU (`GLOCK`, one at a time) | Both judges on the card. Same serial client: qwen3 about 0.4 s a claim (prefill 0.05 s, 40 tokens at about 150 tokens a second), so 380 claims in 2.5 min. Batched (8+ in flight): 380 × 700 tokens × 1.6e10 = 4.3e15 FLOP, under 1 min, plus guardian's 570k prefill tokens, about 1 min. **1 to 3 min** | Serial: about 1.3 s a claim (40 tokens at 35 to 45 tokens a second), 8 min. Batched: 4.3e15 + 9e15 FLOP at 30 to 40 TFLOPS, **5 to 6 min** | **1 to 3 min** on the judge card, never contending with training |
| SFT (25 to 35 min at the cap) | Compute | 3.7e16 ÷ 1.0 to 1.75e14 = **3.5 to 6.2 min**. bf16 8B with checkpointing peaks about 22 GB | 3.7e16 ÷ 2.5 to 4.4e13 = **14 to 25 min** | 3.7e16 ÷ 4.2 to 7.3e13 = **8.5 to 15 min**. Fits 32 GB (16 GB weights, about 2.4 GB fp32 logits at 2 × 2.3k × 128k, about 2 GB checkpoints) |
| DPO (13.1 min GPU) | Compute for the pairs, bandwidth for gencheck | **2 to 3 min** | **6 to 10 min** (gencheck slower than the Mac) | **3.5 to 5 min** |
| Paired eval generation (5 min) | Bandwidth | about 1 min on the card. We would keep it on the Mac, so the gate scores what the council serves: 5 min, no change | Mac, 5 min | Mac, 5 min |
| Paired judge (7 to 16 min) | Armature | **about 1 min** | **2 to 3 min** | **about 1 min** |
| Promotion (15 s) | MLX reload on the Mac | unchanged, plus about 1 min to convert a PEFT adapter to MLX (`PARALLEL_GPU_PLAN.md` section 6) | same | same |
| **Card minutes per 8B turn** | Mac 61 min + Armature 35 to 50 min | **9 to 16 min** | **32 to 50 min** | training card 12 to 20 min, judge/sample card 4 to 7 min |

Fidelity notes that change the plan:
- Train on the dequantized MLX 4-bit weights in bf16, not on a bitsandbytes NF4 copy, or every adapter trains against a different base than the council serves. 8B in bf16 is 16 GB and fits all three. ERNIE in bf16 is about 42 GB: fits the PRO 6000 and the Spark, does not fit a 5090, where it would need NF4 (a different base).
- The judges are an instrument. Moving qwen3:8b from Ollama Q4_K_M on the 3080 to another runtime or quantization needs a parity check against `judge_hardset*.json` before its numbers count.

## 3. Turns per day and claims judged per hour

Turns per day, hardware-limited. Today's figure is measured. The others take card minutes per turn at about 80% duty (no council window is needed once training leaves the Mac), with paired generation kept on the Mac.

| | Card minutes per 8B turn | Turns a day, hardware-limited | Single-turn wall time, no queue |
|---|---|---|---|
| Today (Mac + Armature) | 61 to 67 Mac min | **10** measured (9 Nov: 10 verdicts, 12 SFT runs) | 108 min best, 227 min median |
| RTX PRO 6000 96 GB | 9 to 16 | **70 to 130** | 20 to 30 min |
| DGX Spark 128 GB | 32 to 50 | **23 to 36** | 45 to 70 min |
| 2× RTX 5090 | 12 to 20 on the training card | **60 to 95** | 25 to 35 min |

Under today's scheduler rules these ceilings are not reached. A seat retrains at once only after a release or a rollback. Otherwise it waits for `need_n` live claims (58 to 128 by seat). Council output in the window was 22 to 72 live claims per seat per day, roughly half of a day of lanes and flywheel, because `PAUSE_MAC` held the council during every training job. A card doubles council time on the Mac. Our rough read: under the current rule, turns a day land near 15 to 25 on any of the three cards, and the ceilings above apply only if the release rule changes. A turn every 20 to 30 min per seat would also outrun the council's ability to produce a live read on each adapter.

Claims judged per hour (qwen3:8b plus the second judge, the volume a harvest needs):

| | Serial client (today's code) | Batched client (8 or more calls in flight) | One day of today's volume (about 8,000 claims on 9 Nov: 5,341 harvest + about 1,100 DPO pairs + about 1,500 paired eval) |
|---|---|---|---|
| Today | 480 an hour per pass (7.5 s a claim, median). Best 1,450 to 1,800. Worst 107. Day average 9 Nov: about 330 an hour | not possible on the 3080 beside the council | the whole day |
| RTX PRO 6000 | about 7,000 to 9,000 | 15,000 to 25,000 | 20 to 70 min |
| DGX Spark | about 2,500 to 2,800 | 5,000 to 9,000 | 1 to 3 h |
| 2× RTX 5090 (one card judging) | about 7,000 to 9,000 | 15,000 to 25,000 | 20 to 70 min |

## 4. What becomes possible

Volumes used: about 10,000 claims a day if we judged everything (today's 8,000 plus the ungrounded claims harvest now drops unjudged, about 20% more, plus council claims).

### Judging everything with a stronger judge

| Judge | RTX PRO 6000 | DGX Spark | 2× RTX 5090 |
|---|---|---|---|
| 32B (Q4 about 19 GB, or FP8 32 GB) | batched about 0.25 to 0.3 s a claim (500 tokens × 6.4e10 FLOP = 3.2e13 per claim). 10,000 claims in **45 to 60 min a day** | about 1 s a claim batched. **About 3 h a day** | fits one card (Q4). About 0.4 s a claim. **About 1.1 h a day** |
| 70B (Q4 about 40 GB, FP8 about 70 GB fits) | batched 0.5 to 0.6 s a claim (7e13 FLOP per claim). **About 1.5 h a day**. Serial 2.5 s a claim, 7 h | batched 2.2 s a claim, **about 6 h a day**. Serial 15 s a claim (about 5 tokens a second), 240 an hour: cannot keep up | splits across both cards over PCIe (no NVLink). About 1 s a claim batched, **about 3 h a day**, and no training while it runs |

Today none of this fits: Armature's 10 GB holds one 8B, and the Mac's 48 GB is full (swap 10.8 of 11.3 GB on 10 Nov).

### A 70B teacher

| Job | RTX PRO 6000 | DGX Spark | 2× RTX 5090 |
|---|---|---|---|
| Teacher samples for one harvest (48 prompts × 8) | prefill 84k unique × 1.4e11 = 1.2e16 FLOP, about 80 s. Decode in 2 to 3 waves (KV is 328 KB a token on a 70B). **3 to 6 min** | prefill about 6 min, decode 150 to 200 ms a step. **10 to 15 min** (about today's 8B sampling time on the Mac) | **4 to 8 min**, both cards held |
| Gold answers for the gap corpus (1,540 prompts × 1, about 300 tokens out) | prefill 0.77M × 1.4e11 = 1.1e17 FLOP, about 12 min, decode about 4 min. **About 16 min** | prefill about 52 min, decode about 20 min. **About 75 min** | **30 to 40 min** |
| Serving a 70B council seat (a 300-token voice turn) | about 30 tokens a second, **about 10 s a turn** | about 5 tokens a second, **about 60 s a turn**, the same class as ERNIE's timeouts today | about 25 to 30 tokens a second split over two cards |

### QLoRA of 30B to 70B seats (one turn at today's row shape: 1.16M tokens processed)

| Seat size | FLOP | RTX PRO 6000 (80 to 150 TFLOPS effective with 4-bit dequant) | DGX Spark (25 to 40) | 2× RTX 5090 (50 to 65 per card) | Mac today |
|---|---|---|---|---|---|
| 32B | 4 × 32e9 × 1.16M = 1.5e17 | **16 to 31 min** | **62 to 99 min** | **38 to 49 min** on one card (about 25 to 28 GB) | about 2.3 h at 17.8 TFLOPS, with the council paused all of it and the 48 GB already swapping |
| 70B | 3.25e17 | **36 to 68 min** (about 50 GB) | **2.3 to 3.6 h** | only split over both cards via PCIe pipeline: about 1.6 to 2 h, fragile | does not fit |

ERNIE (21B total, 3B active) trains at roughly 3B compute but needs 21B of memory: about 42 GB in bf16.

### Training on the new corpora

Counted from the files (characters ÷ 4 for tokens):

| Corpus | Rows | Tokens a row | Tokens to process |
|---|---|---|---|
| gap_corpus SFT | 1,540 | about 475 | 1.46M for 2 epochs (train_live's rule) |
| gap_corpus DPO | 105 pairs | about 730 processed a pair | 0.23M for 3 passes (train_pref's cap) |
| qubit_corpus SFT | 1,531 | about 770 | 2.36M for 2 epochs |
| qubit_corpus DPO | 550 pairs | about 1,450 processed a pair | 2.39M for 3 passes |

Time per 8B seat, both corpora, full passes (DPO usually stops early at 20 to 40 iterations, so DPO figures are upper bounds):

| | gap SFT | qubit SFT | gap DPO | qubit DPO | One 8B seat | All five seats (about 4 8B-equivalents: three dense 8B, llama at about 0.5, ERNIE at about 0.5) |
|---|---|---|---|---|---|---|
| Mac today (555 tok/s SFT, 140 to 345 tok/s DPO) | 44 min | 71 min | 11 to 27 min | 1.9 to 4.7 h | **4.1 to 7.2 h** | **16 to 29 h of Mac GPU, council paused or windowed** |
| RTX PRO 6000 (5.6 to 9.8×) | 4.5 to 8 min | 7 to 13 min | 1 to 5 min | 12 to 50 min | **25 to 75 min** | **1.7 to 5 h** |
| DGX Spark (1.4 to 2.5×) | 18 to 31 min | 28 to 51 min | 5 to 19 min | 46 min to 3.4 h | **1.6 to 5.1 h** | **6.6 to 20 h** |
| 2× RTX 5090 (2.4 to 4.1× per card, two seats at once) | 11 to 18 min | 17 to 30 min | 3 to 11 min | 28 min to 2 h | **1 to 3 h** | **2 to 6 h** |

No judge pass is needed to train on these corpora (they are built and labelled). Each run still needs its paired eval.

## 5. The cheapest change with no purchase

**Shorten the council window's hold.** `sage_v.py` line 154: `COUNCIL_WINDOW, COUNCIL_CAP = 3, 3600`. Every harvest, SFT and calibration job (`harvest.py` line 47, `train_live.py` line 92, `realjob_eval.py` line 45 unless same-turn) waits until 3 flywheel cycles have finished since the last GPU job, for up to an hour.

What the logs show:
- Flywheel cycles: median 765 s, p90 1,413 s (`turns`, room FLYWHEEL, 51 cycles since 8 Nov 12Z). A healthy cycle is 441 s (`REPORT.md`). So 3 cycles take 38 to 70 min, and the hour cap is reached often: 11 `COUNCIL_WINDOW ... cap reached after 3600 s` lines in `sage_v.log` from 9 Nov 04:45Z to 10 Nov 02:31Z.
- The Mac trained 46% of 9 Nov. Its 16 long gaps (14 to 112 min) hold 12.0 h. Trimming every gap to 25 min removes at most 5.75 h (345 min of excess).
- A cap-hit hour is an hour in which the council did not finish 3 cycles anyway, so most of what a shorter cap takes from the council is time it was stalled.

The change: `COUNCIL_CAP` 3600 to about 1500 s. One constant. Expected: training duty from 46% toward 60 to 70%, so **turns a day from 10 to about 13 to 15 (+30 to 50%)**. The upper end assumes a job was queued in every gap. It costs the council up to about 3 to 6 h a day of Mac time in its slowest hours. This is Sage's 9 Nov rule, so it needs her ruling before it changes.

The same direction with no trade: make cycles faster, so 3 cycles close sooner and the council keeps its full window. `VOICE_TO = 150` is defined in `sage_flywheel.py` and never passed (REPORT fix 2c). In cycle 144, 950 of 1,112 s waited on ERNIE's 420 s timeouts. The `QUIET:NO_ROOM` guard is already in `sage_flywheel.py` line 43. Cycles at the healthy 441 s would put the 3-cycle window at about 22 min instead of 38 to 70.

Next cheapest, smaller:
- Shared prefill in harvest sampling (prototype `speedup/gen_bench.py` option C: prefill each prompt once for its 8 samples). By the arithmetic in section 2, about 6 of 11 min per harvest, so about 10% more turns, and the Mac's council pause shortens too. Not yet run: one-call continuous batching crashed in mlx_lm 0.31.3 (note in `speedup/realjob_eval_fast.py` line 60).
- Concurrent judge calls on Armature (a thread pool in harvest's `_qwen_pass`, with Ollama parallel above 1 for qwen3). Batched decode costs about the same per step on the 3080, so the qwen pass could run 2 to 3× faster, until guardian on the CPU (about 2 s a claim) becomes the limit. This mostly shortens turn latency, by 15 to 20 min a harvest. Armature's Ollama settings were not read (we did not log in to it), and 4 slots of 6,144 context make about 3.6 GB of KV beside 5.2 GB of weights in a 10 GB card that showed 10,026 MiB in use on 9 Nov. So it is unverified.

## What would change these numbers

- The effective-TFLOPS ranges for the three cards are assumptions. One real SFT turn on any of them replaces the range with a number.
- The Mac's bandwidth is assumed, not measured here.
- Paired-eval generation timing rests on 2 runs with park/unpark lines. DPO 8B GPU rests on 3.
- The need_n release rule, not the card, sets the turn rate unless it changes. The same goes for MAXT and the council window.
