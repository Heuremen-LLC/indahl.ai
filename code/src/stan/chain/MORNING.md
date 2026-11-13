# MORNING — hand review handoff (2026-11-13)

Read-only run. Nothing edited, nothing sent. Every number is copied from the named file.

## 1. Full-slice read  (sagar/analysis/full_slice.json, rerun 10:19)

Slice: outside 1003 total, 942 with arXiv id; control (LVK) 39 total, 34 with id. Papers read by pipeline: 976. Batches merged: 82.

Papers read / with a two-reader finding / unreadable-table, by arm and type (type letters as in the file: M, R, T, ?):

| arm/type | read | two-reader finding | rate | 95% interval | unreadable |
|---|---|---|---|---|---|
| control/? | 1 | 0 | 0.0 | [0.0, 0.793] | 0 |
| control/M | 14 | 6 | 0.429 | [0.214, 0.674] | 1 |
| control/R | 8 | 0 | 0.0 | [0.0, 0.324] | 0 |
| control/T | 11 | 3 | 0.273 | [0.097, 0.566] | 1 |
| outside/M | 385 | 138 | 0.358 | [0.312, 0.408] | 82 |
| outside/R | 314 | 102 | 0.325 | [0.275, 0.378] | 54 |
| outside/T | 243 | 37 | 0.152 | [0.113, 0.203] | 39 |
| **outside (all)** | 942 | 277 | 0.294 | [0.266, 0.324] | 175 |
| **control (all)** | 34 | 9 | 0.265 | [0.146, 0.431] | 2 |

Control minus outside: -0.029 (interval -0.152 to 0.139). **CANNOT_TELL**: the interval reaches zero and also ±0.14 to 0.15, i.e. a gap of a size that would matter in either direction. Control is only 34 papers and 2 by type are 1 and 8 papers.
Note (the gate): unreadable tables are counted by arm above (outside 175 of 942 read = 18.6%, control 2 of 34 = 5.9%, computed from the file). Type T is read least often (39/243 = 16.0%). Whether unreadable papers are dropped from `read` or kept in it is not stated in the file; check before quoting the rates.
Codes per paper (full_slice.json codes_per_paper): F6 199, F5 85, F2 40, F3 15.

Hand vs pipeline (126 papers, full_slice.json hand_vs_pipeline): both 11, hand-only 4, pipeline-only 32, neither 79. Flips: hand→pipeline-miss 4, pipeline→hand-miss 32. Exact test on the 36 discordant papers (my calculation, two-sided binomial, 4 vs 32): p = 1.9e-06. Direction: the pipeline finds many papers the hand read did not; the reverse is rare. Six papers excluded by name in rules: 2409.16196, 2410.16565, 2503.09731, 2506.21021, 2603.29019, 2610.29436.

Repeat floor (full_slice.json repeat_floor), same setup run twice:

| batch | papers | both | first-only | repeat-only |
|---|---|---|---|---|
| 11 | 12 | 4 | 0 | 2 |
| 12 | 12 | 3 | 2 | 0 |

Floor, both directions: batch 11 lost 0 and gained 2; batch 12 lost 2 and gained 0. So the pipeline moves by 2 papers per 12 in each batch, in opposite signs, and nets to zero across the two. The 32 pipeline-only vs 4 hand-only flips are far above that floor, but the floor itself is 4 of 24 papers, so quote it as a floor of about 2 per 12, not zero.

## 2. Training  (stan/train_e/results/*.json, data/manifest.json)

Model Qwen2.5-7B-Instruct-4bit. Intervals as printed in each file's summary.

| model | set | pos flagged | recall | neg flagged | false-flag | parse fail |
|---|---|---|---|---|---|---|
| base | test_pipeline | 6/23 | [0.125, 0.465] | 0/39 | [0.0, 0.09] | 0 |
| base | test_hand | 9/27 | [0.186, 0.522] | 1/30 | [0.006, 0.167] | 1 |
| lora_v1 | test_pipeline | 0/23 | [0.0, 0.143] | 0/39 | [0.0, 0.09] | 0 |
| lora_v1 | test_hand | 0/27 | [0.0, 0.125] | 0/30 | [0.0, 0.114] | 0 |
| lora_v2 | test_pipeline | 0/23 | [0.0, 0.143] | 0/39 | [0.0, 0.09] | 0 |
| lora_v2 | test_hand | 0/27 | [0.0, 0.125] | 0/30 | [0.0, 0.114] | 0 |

Manifest: 630 papers drafted, 185 with a finding; split papers train 474, valid 50, test 52, hand 54; excluded ambiguous papers 281.

**Did any LoRA beat the base on both measures? No.** Neither LoRA flagged a single positive on either set (0/27 and 0/23), so recall fell from the base's 9/27 and 6/23. False-flag is not distinguishable: base 1/30 (hand) and 0/39 (pipeline) against 0/30 and 0/39 for the LoRAs, and every interval overlaps.
- test_hand recall: base [0.186, 0.522] vs LoRA [0.0, 0.125]. Intervals do not overlap, so both LoRAs are BELOW the base.
- test_pipeline recall: base [0.125, 0.465] vs LoRA [0.0, 0.143]. Intervals overlap, so by the interval rule it **cannot be told** on this set alone (point estimates 6/23 vs 0/23).
- false-flag on both sets: intervals overlap, **cannot be told**. Zero flags also means the LoRAs may simply have learned to say nothing, which would give zero false flags for free.
- v1 and v2 are identical on every count; the two LoRAs cannot be separated.
- Training logs (adapters_v1/v2.train.log): v1 final iter 600 val loss 1.174, train loss 0.146; v2 final iter 1200 val loss 1.450, train loss 0.232. Val loss well above train loss; I did not check whether the validation loss rose over training.

## 3. Failures / blocked stages

- stan/chain/chain.log: all stages ended rc 0 (sagar_read_done, full_slice_numbers, train_set, eval_base, lora_v1, eval_v1, lora_v2, eval_v2). One event: 07:10:22 RESET lora_v1, v1 went NaN (prompts ≥ 3072 tokens masked every target); train_lora.sh now filters >4096 tokens, batch 1, grad checkpoint, NaN fails the stage. v1 was retrained and finished rc 0 at 07:52. The 4096-token filter dropped 0 positives (manifest length_filter).
- sagar/pipeline/pipe.log: 418 lines, 0 lines matching fail/error. Last line 2026-11-13T03:24:56 MERGE batch_57. No stage blocked.
- sagar/pipeline/logs/*: matches for 'fail' are reader/draft prose about papers (and one pypdf import failure in batch_27 draft that the agent worked around), not pipeline failures.
- stan/train_e/logs does not exist; train logs are stan/train_e/adapters_v1.train.log, adapters_v2.train.log, train.log.
- Path note: verified_full.jsonl is at sagar/index/verified_full.jsonl, not under sagar/pipeline/work.

## 4. Hand-review list for Bones

A. Seeded sample, random.seed(20261113), random.sample of 20 rows from sagar/index/verified_full.jsonl (93 rows, file order). Arxiv ids repeat where one paper has two rows (2111.15116, 2407.02908).

| # | arxiv | code | reader verdict | claim (draft quote) |
|---|---|---|---|---|
| 1 | 2506.19911 | F6 | INCONSISTENT | achieves 30–60% lower unfaithfulness thanIMRPhenomXPNRand |
| 2 | 2111.15116 | F5 | INCONSISTENT | 501–555 Hz 35 |
| 3 | 2510.17967 | F2 | SELECTED_HEADLINE | environment with a Bayes factor oflnB envvac ≈ 3.5 |
| 4 | 2303.16553 | F6 | INCONSISTENT | It corresponds to a0 = 0.0023rg≈ 0.0045AU for m1 = m2 = 10M⊙ |
| 5 | 2004.11468 | F3 | UNSUPPORTED_CLAIM | Furthermore, unique events were found on the LIBOR data set of the last 30 years. |
| 6 | 2302.03676 | F6 | INCONSISTENT | L1 0.01% 0.64% 0.28% 0.51% |
| 7 | 2202.05164 | F5 | INCONSISTENT | MBH = Mcrit(a/aKep = 1) (2.41 M⊙ for MTOV = 2M⊙, 2.65 M⊙ for MTOV = 2.2 M⊙) |
| 8 | 2606.17752 | F5 | INCONSISTENT | finding that at most 8% could remain gravitationally bound to globular or nuclear star clusters |
| 9 | 2108.10588 | F6 | INCONSISTENT | we report an eﬃciency in- crease by 5− 40% for the waveforms tested |
| 10 | 2511.04218 | F2 | SELECTED_HEADLINE | reducing total likelihood evaluations and wall times by factors of up to 5.8 and 5.5 |
| 11 | 1304.0670 | F6 | INCONSISTENT | During O1 and O2, Livingston lost over twice as much observing time to earthquakes, microseism noise and wi... |
| 12 | 2202.08671 | F6 | INCONSISTENT | correctly identify 77 out of 83 CBC events from |
| 13 | 2012.08545 | F3 | UNSUPPORTED_CLAIM | identifying all four all four binary black hole mergers previously identiﬁed in this dataset and reporting ... |
| 14 | 2510.02515 | F6 | INCONSISTENT | strain data for GW190412 and GW250114_082203 is known to have |
| 15 | 2005.05693 | F6 | INCONSISTENT | At O3 and design sensitivity, all masses are considered detectable, for both choices of power spectra |
| 16 | 2407.02908 | F5 | INCONSISTENT | in 0.5w intervals, a total of 72 dictionaries. |
| 17 | 2111.15116 | F6 | INCONSISTENT | displayed an increase of 70% or more in excess 2 |
| 18 | 2407.02908 | F2 | SELECTED_HEADLINE | with 1.16 day time windows with mismatch as low as 0.06 |
| 19 | 2108.12044 | F6 | INCONSISTENT | Events are in order of detector frame chirp mass ( Mdet, M⊙). |
| 20 | 2002.04591 | F6 | INCONSISTENT | Even for the worst runs, the number of lost signals remains well below 1% |

B. Review rows: sagar/pipeline/work/review_full.jsonl (5) + review_redraft.jsonl (5) = 10; listed 10, 0 more not listed.

| # | arxiv | code | reader verdict | claim (draft quote) |
|---|---|---|---|---|
| 1 | 2510.22290 | F5 | INCONSISTENT | from ∼ 12%relative uncertainty (for ET-∆) to ∼ 7.5% |
| 2 | 2105.05238 | F2 | SELECTED_HEADLINE | with a maximum Bayes factor of 56 ± 1 (1σ uncertainty) preferring two fundamental modes over one |
| 3 | 2206.14515 | F6 | CANNOT_TELL | the localization capability for a glitch size of 10 −5 Hz is around 132 deg |
| 4 | 2206.11932 | F6 | INCONSISTENT | the SNR reduction is only 1.5 units |
| 5 | 1905.00869 | F2 | SELECTED_HEADLINE | both associated with the dominant angular mode ( 𝓁 =m = 2), with 3.6σ conﬁdence |
| 6 | 2512.08164 | F5 | CANNOT_TELL | 1,500 mock universes, with injected values of ¯ηuniformly distributed between 0 and 1 in steps of ∆¯η= 2/1500 |
| 7 | 2509.17606 | F5 | CANNOT_TELL | NRSur7dq4 FLEX+pocomc 284.3 1.8×10 5 4 109m 19m52s 70% |
| 8 | 2507.01294 | F6 | CANNOT_TELL | to the 60 binary black hole gravitational-wave events from GWTC-3 |
| 9 | 2310.01548 | F6 | INCONSISTENT | telescopes could be able to detect such transient signals from PBHs, with mass rangeM∼10 −1 −10 −2M⊙ |
| 10 | 2405.05318 | F6 | INCONSISTENT | The positions of the 20 flares listed in Table 1 are cross-matched with the sky maps of the GW events liste... |
