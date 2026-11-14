# MORNING — hand review (13 Nov 2026, written by handoff_night_v7)

Sources: sagar/analysis/full_slice.json (re-run 21:23), stan/train_e/results/*.json, stan/train_e/data/manifest.json, stan/chain/chain.log, stan/chain/NIGHT.md, sagar/pipeline/pipe.log. Intervals are as printed in those files. Nothing else was touched.

## 1. Full-slice read (full_slice.json)

Slice: outside 1003 papers (942 with arxiv id), control_LVK 39 (34 with arxiv); read_pipeline 976.

Papers read / with a two-reader finding (found) / unreadable-table, rate [interval]:

| arm/type | read | found | unreadable | rate | interval |
|---|---|---|---|---|---|
| control/? | 1 | 0 | 0 | 0.0 | 0.0-0.793 |
| control/M | 14 | 6 | 1 | 0.429 | 0.214-0.674 |
| control/R | 8 | 0 | 0 | 0.0 | 0.0-0.324 |
| control/T | 11 | 3 | 1 | 0.273 | 0.097-0.566 |
| outside/M | 385 | 138 | 82 | 0.358 | 0.312-0.408 |
| outside/R | 314 | 102 | 54 | 0.325 | 0.275-0.378 |
| outside/T | 243 | 37 | 39 | 0.152 | 0.113-0.203 |

- outside (all types): read 942, found 277, unreadable 175, rate 0.294 [0.266-0.324]
- control (all types): read 34, found 9, unreadable 2, rate 0.265 [0.146-0.431]
- Control minus outside: -0.029 [-0.152, 0.139]. **CANNOT_TELL**: the interval reaches zero and also reaches about ±0.14–0.15 (a gap of that size would matter). Control has only 34 papers read.
- Unreadable-table counts by arm: outside 175, control 2. Unreadable papers are in the read count; found rate is not corrected for them, and outside/T has the fewest found (37/243) with 39 unreadable.
- Findings by code (codes_per_paper): {'F6': 199, 'F3': 15, 'F2': 40, 'F5': 85}
- Hand vs pipeline (126 papers): both 11, hand-only 4 (hand found, pipeline did not), pipeline-only 32 (pipeline found, hand did not), neither 79. Excluded, named in rules: 2409.16196, 2410.16565, 2503.09731, 2506.21021, 2603.29019, 2610.29436.
- Repeat floor, batch 11: 12 papers, both 4, first-only 0, repeat-only 2 (first→repeat lost 0, gained 2).
- Repeat floor, batch 12: 12 papers, both 3, first-only 2, repeat-only 0 (first→repeat lost 2, gained 0).
- Check: verified_full.jsonl holds 93 rows over 81 papers, while full_slice.json found totals 286 papers. They are not the same count; I did not reconcile them.

## 2. Training (results/*.json; base = Qwen2.5-7B-Instruct-4bit)

Recall = flagged positives; false-flag = flagged negatives. Intervals as printed. Parse fail = hand/pipeline.

| model | test_hand recall | test_hand false-flag | test_pipeline recall | test_pipeline false-flag | parse fail |
|---|---|---|---|---|---|
| base | 9/27 (0.186-0.522) | 1/30 (0.006-0.167) | 6/23 (0.125-0.465) | 0/39 (0.0-0.09) | 1/0 |
| lora_v1 | 0/27 (0.0-0.125) | 0/30 (0.0-0.114) | 0/23 (0.0-0.143) | 0/39 (0.0-0.09) | 0/0 |
| lora_v2 | 0/27 (0.0-0.125) | 0/30 (0.0-0.114) | 0/23 (0.0-0.143) | 0/39 (0.0-0.09) | 0/0 |

v1 and v2 flagged 0 on every item on both sets (collapse; recall 0/27 and 0/23). Neither beat the base. v1 first went NaN and was rerun (chain.log 07:10).
Did any LoRA beat the base on both measures? Of v1-v7, none has non-overlapping intervals on both recall and false-flag on both sets. No LoRA beat the base on both measures. v6's recall intervals do not overlap the base's on either set (hand 0.553-0.868 vs 0.186-0.522; pipeline 0.535-0.875 vs 0.125-0.465), but its false-flag intervals do overlap the base's (hand 0.095-0.373 vs 0.006-0.167), so on false-flag it **cannot be told**. v4 and v7 overlap the base on recall too (cannot be told). v1/v2 are below base on recall. Data manifest: {'excluded_ambiguous_papers': 281, 'test_pos': 23, 'train_pos': 153, 'valid_pos': 16, 'train_neg': 396, 'test_neg': 39, 'hand_pos': 27, 'valid_neg': 27, 'hand_neg': 30}.

## 3. Failures / blocked stages

- chain.log: every DONE line is rc 0 (v1-v7 train and eval, decide_*, handoff_*); no rc other than 0. One RESET: lora_v1 went NaN (07:10), fixed in train_lora.sh, rerun passed.
- score_curves is CUED to the mac hot lane at 21:23:47 and has not finished; it is pending, not failed.
- pipe.log: no lines containing fail/error/traceback (last line is the 03:24:56 merge of batch_57). I did not check state.json for draft_failed/second_failed batches.
- stan/train_e/logs does not exist; per-stage logs are in stan/chain/logs.
- Also open (session alert, not from the logs): launchd com.heuremen.qia-audit exit status 1 since 18:10.

## 4. Hand-review list for Bones

A. Seeded sample (random.seed(20261113), random.sample of 20 from the 81 unique arxiv ids in sagar/index/verified_full.jsonl sorted):

- 2012.08545 | F3 | identifying all four all four binary black hole mergers previously identiﬁed in this dataset and reporting no misclassiﬁcations
- 1610.05573 | F6 | 45/50 magnetoro- tational waveforms and none of the extra neutrino mech- anism waveforms can be distinguished from noise.
- 2005.03306 | F6 | the results from LIGO obtained in Ref. [7]
- 2304.09396 | F6 | found to be consistent within∼2–3%
- 1511.02836 | F2 | We ﬁnd that a three-detector network at design sensitivity will be able to detect neutrino-driven CCSN explosions out to ∼ 5.5 kpc
- 2409.02174 | F6 | Photometric observations are provided within Ap- pendix Table 6, where
- 1908.04382 | F6 | ∆ φtraj (4678.96± 40.82 km/s)
- 2505.21261 | F6 | In addition, Table III lists 30 candi-
- 2607.03674 | F6 | J183412.42+365655.3 (−1.12) is strongly disfavoured
- 2003.00072 | F5 | 2,056,663 23.8 Aug 02 00:41:51 876 865 0.73
- 1903.03909 | F6 | The maximum variation in the constrained set case is better than a factor of two smaller than the variability in the unconstrained case and 
- 2311.09159 | F6 | we inject the signal at 9 times spaced 0.025 seconds around the glitch peak time. For each
- 2511.00497 | F5 | The combined posteriors on the amplitude parametersA α are, on average, 19% narrower.
- 2004.10001 | F6 | Q [1,6] [1,100]
- 2208.07762 | F2 | the merger rate of similar events to be 0 .47 Gpc−3 yr−1.
- 1709.00955 | F6 | For the Sch 5 magnetorotational signals there are 741 signals that are detected and 1 is mis-classiﬁed as a glitch.
- 2206.14515 | F5 | Given the frequencies are over 2 kHz, the mean and rms are less than 1%.
- 2503.21417 | F5 | Examplesnotedinthe originalGitHubpullrequest[ 199]seeincreasesinnetworkSNRfrom9 .818to10 .149, anincreaseof3 .6%. Optimisationalgo
- 1304.0670 | F6 | During O1 and O2, Livingston lost over twice as much observing time to earthquakes, microseism noise and wind compared to Hanford.
- 2210.01718 | F6 | reproducing all binary black hole mergers detected in O2 at both the aLIGO detectors

B. Review queue (review_full.jsonl 5 + review_redraft.jsonl 5 rows; listing 10, 0 more not listed):

- 2510.22290 | F5 | review_full | reader INCONSISTENT/low | from ∼ 12%relative uncertainty (for ET-∆) to ∼ 7.5%
- 2105.05238 | F2 | review_full | reader SELECTED_HEADLINE/low | with a maximum Bayes factor of 56 ± 1 (1σ uncertainty) preferring two fundamental modes over one
- 2206.14515 | F6 | review_full | reader CANNOT_TELL/low | the localization capability for a glitch size of 10 −5 Hz is around 132 deg
- 2206.11932 | F6 | review_full | reader INCONSISTENT/low | the SNR reduction is only 1.5 units
- 1905.00869 | F2 | review_full | reader SELECTED_HEADLINE/low | both associated with the dominant angular mode ( 𝓁 =m = 2), with 3.6σ conﬁdence
- 2512.08164 | F5 | review_redraft | reader CANNOT_TELL/low | 1,500 mock universes, with injected values of ¯ηuniformly distributed between 0 and 1 in steps of ∆¯η= 2/1500
- 2509.17606 | F5 | review_redraft | reader CANNOT_TELL/medium | NRSur7dq4 FLEX+pocomc 284.3 1.8×10 5 4 109m 19m52s 70%
- 2507.01294 | F6 | review_redraft | reader CANNOT_TELL/medium | to the 60 binary black hole gravitational-wave events from GWTC-3
- 2310.01548 | F6 | review_redraft | reader INCONSISTENT/low | telescopes could be able to detect such transient signals from PBHs, with mass rangeM∼10 −1 −10 −2M⊙
- 2405.05318 | F6 | review_redraft | reader INCONSISTENT/low | The positions of the 20 flares listed in Table 1 are cross-matched with the sky maps of the GW events listed in Table A1.

## Night ladder (NIGHT.md, chain.json, results/lora_v*_test_*.json)

Routes are pipeline routing, not findings. A rung is called better only if its intervals do not overlap the base's.

| model | data | lr | iters | hand recall | hand false-flag | pipe recall | pipe false-flag | status |
|---|---|---|---|---|---|---|---|---|
| base | - | - | - | 9/27 (0.186-0.522) | 1/30 (0.006-0.167) | 6/23 (0.125-0.465) | 0/39 (0.0-0.09) | ran ok |
| lora_v1 | default data | 1e-5 | 600 | 0/27 (0.0-0.125) | 0/30 (0.0-0.114) | 0/23 (0.0-0.143) | 0/39 (0.0-0.09)  ran ok (rc 0); vs base intervals: hand recall no overlap, hand false overlap, pipe recall overlap, pipe false overlap |
| lora_v2 | default data | 2e-5 | 1200 | 0/27 (0.0-0.125) | 0/30 (0.0-0.114) | 0/23 (0.0-0.143) | 0/39 (0.0-0.09)  ran ok (rc 0); vs base intervals: hand recall no overlap, hand false overlap, pipe recall overlap, pipe false overlap |
| lora_v3 | data_bal | 1e-5 | 600 | 0/27 (0.0-0.125) | 0/30 (0.0-0.114) | 0/23 (0.0-0.143) | 0/39 (0.0-0.09)  ran ok (rc 0); vs base intervals: hand recall no overlap, hand false overlap, pipe recall overlap, pipe false overlap |
| lora_v4 | data_short | 1e-5 | 600 | 19/27 (0.515-0.841) | 5/30 (0.073-0.336) | 15/23 (0.449-0.812) | 4/39 (0.041-0.236)  ran ok (rc 0); vs base intervals: hand recall overlap, hand false overlap, pipe recall overlap, pipe false overlap |
| lora_v5 | data_bal | 2e-5 | 1200 | 0/27 (0.0-0.125) | 0/30 (0.0-0.114) | 0/23 (0.0-0.143) | 0/39 (0.0-0.09)  ran ok (rc 0); vs base intervals: hand recall no overlap, hand false overlap, pipe recall overlap, pipe false overlap |
| lora_v6 | data_short | 2e-5 | 1200 | 20/27 (0.553-0.868) | 6/30 (0.095-0.373) | 17/23 (0.535-0.875) | 4/39 (0.041-0.236)  ran ok (rc 0); vs base intervals: hand recall no overlap, hand false overlap, pipe recall no overlap, pipe false overlap |
| lora_v7 | data_short | 1e-5 | 1200 | 16/27 (0.407-0.755) | 0/30 (0.0-0.114) | 12/23 (0.33-0.708) | 2/39 (0.014-0.169)  ran ok (rc 0); vs base intervals: hand recall overlap, hand false overlap, pipe recall overlap, pipe false overlap |

Routing, one line per rung:
- lora_v1: (no night row; stage ran before the ladder) next: lora_v2 (chain.json)
- lora_v2: (no night row) next: data_bal, lora_v3 (chain.json)
- lora_v3: collapse -> next lora_v4: data_short, lr 1e-5, 600 iters
- lora_v4: partial -> next lora_v5: data_bal, lr 2e-5, 1200 iters
- lora_v5: collapse -> next lora_v6: data_short, lr 2e-5, 1200 iters
- lora_v6: partial -> ladder stopped (v7 then added by hand 19:41 between v4 and v6)
- lora_v7: match_or_beat -> ladder stopped; score_curves cued after decide_v7
- Failed rungs: none (no rc other than 0 in chain.log). v1, v2, v3, v5 collapsed to 0 flags, which is an outcome, not a stage failure.
- Added by hand in NIGHT.md (20:49): paper vote, defined after the data: v6 k>=1 caught 19/23 papers with 5/10 clean papers flagged (hand); k>=2 1/23 and 1/10. Defined after the data, so read as a description, not a test.
- v7 (decide_v7 route match_or_beat): 16/27 and 0/30 on hand, 12/23 and 2/39 on pipeline. Its false-flag point estimates are at or below base; recall intervals overlap base's (and v4/v6's). That is a routing label, not a win: cannot be told from base on recall.
