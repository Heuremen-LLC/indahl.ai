# MORNING — hand review handoff (2026-11-13)

Read-only run (refreshed with the night ladder). Nothing edited, nothing sent. Every number is copied from the named file.

## 1. Full-slice read  (sagar/analysis/full_slice.json, rerun 19:35 13 Nov, values identical to 10:19)

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

## 2. Training  (stan/train_e/results/{base,lora_v1..v6}_test_{hand,pipeline}.json, data/manifest.json)

Model mlx-community/Qwen2.5-7B-Instruct-4bit. Counts and 95% intervals as printed in each file's summary. data/lr/iters from stan/chain/chain.json (v1, v2 on `data`).

| model | data | lr | iters | hand recall | hand false-flag | pipeline recall | pipeline false-flag | parse fail (hand/pipe) |
|---|---|---|---|---|---|---|---|---|
| base | - | - | - | 9/27 [0.186, 0.522] | 1/30 [0.006, 0.167] | 6/23 [0.125, 0.465] | 0/39 [0.0, 0.09] | 1/0 |
| lora_v1 | data | 1e-5 | 600 | 0/27 [0.0, 0.125] | 0/30 [0.0, 0.114] | 0/23 [0.0, 0.143] | 0/39 [0.0, 0.09] | 0/0 |
| lora_v2 | data | 2e-5 | 1200 | 0/27 [0.0, 0.125] | 0/30 [0.0, 0.114] | 0/23 [0.0, 0.143] | 0/39 [0.0, 0.09] | 0/0 |
| lora_v3 | data_bal | 1e-5 | 600 | 0/27 [0.0, 0.125] | 0/30 [0.0, 0.114] | 0/23 [0.0, 0.143] | 0/39 [0.0, 0.09] | 0/0 |
| lora_v4 | data_short | 1e-5 | 600 | 19/27 [0.515, 0.841] | 5/30 [0.073, 0.336] | 15/23 [0.449, 0.812] | 4/39 [0.041, 0.236] | 0/0 |
| lora_v5 | data_bal | 2e-5 | 1200 | 0/27 [0.0, 0.125] | 0/30 [0.0, 0.114] | 0/23 [0.0, 0.143] | 0/39 [0.0, 0.09] | 0/0 |
| lora_v6 | data_short | 2e-5 | 1200 | 20/27 [0.553, 0.868] | 6/30 [0.095, 0.373] | 17/23 [0.535, 0.875] | 4/39 [0.041, 0.236] | 0/0 |

Manifest (train_e/data/manifest.json): 630 papers drafted, 185 with a finding; split papers train 474, valid 50, test 52, hand 54; excluded ambiguous papers 281.

**Did any LoRA beat the base on both measures? No.**
- v1, v2, v3, v5 flagged nothing on either set (collapse): recall BELOW the base on test_hand (intervals [0.0, 0.125] vs [0.186, 0.522], no overlap); on test_pipeline [0.0, 0.143] vs [0.125, 0.465] overlap, CANNOT_TELL.
- v4: recall hand 19/27 vs base 9/27 (intervals [0.515, 0.841] vs [0.186, 0.522] overlap by 0.007), pipeline 15/23 vs 6/23 ([0.449, 0.812] vs [0.125, 0.465] overlap): CANNOT_TELL on recall. False-flag 5/30 and 4/39 vs base 1/30 and 0/39, intervals overlap: CANNOT_TELL.
- v6: recall hand 20/27 [0.553, 0.868] and pipeline 17/23 [0.535, 0.875], both clear of the base's intervals, so recall is ABOVE the base on both sets. False-flag hand 6/30 [0.095, 0.373] vs base 1/30 [0.006, 0.167], pipeline 4/39 [0.041, 0.236] vs base 0/39 [0.0, 0.09]: intervals overlap, CANNOT_TELL, though the point estimates are higher than the base on both sets. So v6 did not beat the base on both measures: one measure is above, the other cannot be told (and leans worse).
- Two sets, one adapter each, 27 and 23 positives: small. Test sets are chunks, several chunks per paper (items in the result files carry arxiv and chunk), so intervals that treat chunks as independent are probably too narrow; not checked.

## 3. Failures / blocked stages

- stan/chain/chain.log (read 19:34): every DONE line is rc 0 (all rc files in stan/chain/rc present). No rung failed. handoff_night_v6 shows START 19:34:32 with no DONE yet; that is this run.
- One event, 07:10:22 RESET lora_v1: v1 went NaN (prompts >= 3072 tokens masked every target); train_lora.sh now filters >4096 tokens, batch 1, grad checkpoint, NaN fails the stage. v1 retrained, rc 0 at 07:52. The filter dropped 0 positives (manifest length_filter).
- The ladder stopped after v6 by rule (NIGHT.md). Nothing blocked.
- sagar/pipeline/pipe.log: 418 lines, 0 lines matching fail/error. Last line 2026-11-13T03:24:56 MERGE batch_57.
- stan/train_e/logs does not exist; train logs are stan/train_e/adapters_v1..v6.train.log. I did not read their loss curves. stan/chain/logs/*: no stage log matched fail/error except handoff_agent.log, which only states "pipe.log has no failed lines".
- Open alert from the session banner (not from the chain): launchd com.heuremen.qia-audit last exit status 1 since 18:10. Not investigated.
- Path note: verified_full.jsonl is at sagar/index/verified_full.jsonl, not under sagar/pipeline/work. The hand-review lists below are unchanged since 10:19: verified_full.jsonl, review_full.jsonl and review_redraft.jsonl have file times Nov 12 22:43 / 22:43 / 23:45, earlier than that run.

## Night ladder  (stan/chain/NIGHT.md, stan/train_e/results/lora_v*_test_*.json, chain.log)

The routes are pipeline routing, not findings. Counts and intervals only; a rung is called better only if its intervals do not overlap the base's. Base row first. No rung failed (no rc other than 0 in chain.log).

| model | data | lr | iters | hand recall | hand false-flag | pipeline recall | pipeline false-flag | parse fail (hand/pipe) |
|---|---|---|---|---|---|---|---|---|
| base | - | - | - | 9/27 [0.186, 0.522] | 1/30 [0.006, 0.167] | 6/23 [0.125, 0.465] | 0/39 [0.0, 0.09] | 1/0 |
| lora_v1 | data | 1e-5 | 600 | 0/27 [0.0, 0.125] | 0/30 [0.0, 0.114] | 0/23 [0.0, 0.143] | 0/39 [0.0, 0.09] | 0/0 |
| lora_v2 | data | 2e-5 | 1200 | 0/27 [0.0, 0.125] | 0/30 [0.0, 0.114] | 0/23 [0.0, 0.143] | 0/39 [0.0, 0.09] | 0/0 |
| lora_v3 | data_bal | 1e-5 | 600 | 0/27 [0.0, 0.125] | 0/30 [0.0, 0.114] | 0/23 [0.0, 0.143] | 0/39 [0.0, 0.09] | 0/0 |
| lora_v4 | data_short | 1e-5 | 600 | 19/27 [0.515, 0.841] | 5/30 [0.073, 0.336] | 15/23 [0.449, 0.812] | 4/39 [0.041, 0.236] | 0/0 |
| lora_v5 | data_bal | 2e-5 | 1200 | 0/27 [0.0, 0.125] | 0/30 [0.0, 0.114] | 0/23 [0.0, 0.143] | 0/39 [0.0, 0.09] | 0/0 |
| lora_v6 | data_short | 2e-5 | 1200 | 20/27 [0.553, 0.868] | 6/30 [0.095, 0.373] | 17/23 [0.535, 0.875] | 4/39 [0.041, 0.236] | 0/0 |

Routes (NIGHT.md, night_decide.py):
- lora_v3 (data_bal, 1e-5, 600): flagged 0 positives on both sets; routed collapse -> lora_v4 on data_short, lr 1e-5, 600 iters.
- lora_v4 (data_short, 1e-5, 600): hand 19/27 pos, 5/30 neg; pipeline 15/23 pos, 4/39 neg; routed partial -> lora_v5 on data_bal, lr 2e-5, 1200 iters. Against the base: recall intervals overlap, CANNOT_TELL.
- lora_v5 (data_bal, 2e-5, 1200): flagged 0 positives on both sets; routed collapse -> lora_v6 on data_short, lr 2e-5, 1200 iters.
- lora_v6 (data_short, 2e-5, 1200): hand 20/27 pos, 6/30 neg; pipeline 17/23 pos, 4/39 neg; routed partial -> ladder stopped. Against the base: recall intervals do not overlap on either set (above); false-flag intervals overlap (CANNOT_TELL).
- lora_v1 and lora_v2 are the pre-ladder runs on `data`; NIGHT.md has no row for them. Both collapsed (0 flags).
- Pattern in the table (not tested further): both rungs that flagged anything used data_short, both on data_bal collapsed. Two rungs each, so it is a pattern, not a finding.

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
