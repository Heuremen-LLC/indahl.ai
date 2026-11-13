# STAN v2 prep (12 Nov 2026)

Nothing was trained. The gold test half and runs/*test* were not read or changed. No v1 file was overwritten. No git commit was made. The v2 labels are in data/silver_v2/ (silver_all, train, valid, plus train_meta, valid_meta, unused_cap, dropped_non_quotable). The script is scripts/silver_v2.py. A second run restricted to the 165 papers v1 used is in data/silver_v2_parity/ with results/silver_v2_classes_parity.json, for comparison only.

## 1. What the script does
Inputs are teachers/{gemma,llama,mistral}_round1.jsonl and _round2.jsonl, re-parsed from the raw text, so the teachers' own status and quote are kept. The files have grown since v1: 397 papers carry all three teachers' round 1 (v1 used 165). results/silver_v2_log.json holds the counts. No pool id is in the gold test half (checked against data/gold_split.json).

Rules as built:
- A teacher PRESENT or ABSENT counts as a vote only if its quote is a whitespace-normalised substring of the abstract (common.py ws()). Otherwise it counts toward neither silver nor CT. A teacher CANNOT_TELL with a valid reason and NOT_APPLICABLE are votes as written.
- A (paper, code) pair is silver when all three teachers cast a vote and the three statuses agree. If round 1 does not give that, round 2 labels replace round 1 for the codes the teacher re-answered, as in v1, and the test is repeated.
- PRESENT or ABSENT in a cell QUOTABLE.md marks not quotable is dropped and logged (F3 ABSENT, all of F4 to F7). Only F1 P/A, F2 P/A and F3 PRESENT can be silver P/A.
- Cap by status per code: the largest status is cut to the combined size of the others.
- Split: 29 of 141 papers (20.6 percent) to valid, seed 1112, whole papers only, after the cap.
- Assistant output is JSON in the order quote, status, reason. The user prompt is v1's with only the format line changed to quote first (code_prompt_v2 inside silver_v2.py, common.py untouched).

## 2. Rows dropped by each rule (results/silver_v2_log.json, 397 papers x 7 codes = 2779 pairs)
- Teachers did not agree on three votes: 993 pairs.
- At least one teacher PRESENT/ABSENT call was unquoted or not found in the text, and no agreement after round 2: 1140 pairs.
- A parse failure: 92 pairs.
- Dropped as non-quotable cell (unanimous grounded P/A): 195 pairs. By cell: F4 PRESENT 88, F4 ABSENT 1, F5 PRESENT 1, F5 ABSENT 28, F6 PRESENT 30, F6 ABSENT 29, F3 ABSENT 14, F7 PRESENT 2, F7 ABSENT 2. File: data/silver_v2/dropped_non_quotable.jsonl.
- Silver before cap: 359 rows (68 agreed in round 1, 291 after round 2). Cut by the status cap: 195 rows. Kept: 164 rows (train 131, valid 33).
- Round 1 teacher calls over these 397 papers (8337): 2308 PRESENT or ABSENT calls had no usable quote (PRESENT unquoted 260, not found 578, ABSENT unquoted 916, not found 554), 37 were parse failures, 2764 PRESENT or ABSENT were grounded, 3228 were CANNOT_TELL or NOT_APPLICABLE.
- Reconciliation to v1: v1 had 345 silver rows on 165 papers. On the same 165 papers v2 keeps 46 train and 12 valid rows (results/silver_v2_classes_parity.json).

## 3. Class table
See results/silver_v2_classes.md and results/silver_v2_classes.json. Short form: F2 P 37/A 29/NA 2 train, F3 CT 6/NA 8, F5 CT 18/NA 20, F7 CT 5/NA 6, and F1, F4, F6 have no rows after the cap.

## 4. Positive control and spot-check split
File: review_queue/marks_page/positive_control.json, built by review_queue/marks_page/build_positive_control.py. Ten items are F2 PRESENT with real "up to" quotes from the abstracts in items.json (papers caa68f493f80, 9edf432b337f x2, 7bbe789b0d83, eeeb59274f80 x3, 117e55b1a2f6, d0b570e43454, fad148ca986b). Ten are F2 PRESENT labels with a plain method sentence that holds no number or selection word (a negative by construction). No F1 item was built: no abstract in items.json states a comparison with the device's own stated or calibration figures, so F1 was left out and only F2 was used.
Question wording as in build_marks_page.py: "Does the quote support the label?". I read each item against the F2 definition. Result: 10 of 10 positives yes, 0 of 10 negatives yes. Limits: I wrote the items, so this reading is not blind, and the original blind pass's prompt is not saved on disk (bones_marks.json holds only marks and one-line reasons). It shows the F2 test is passable on a plain quote. It does not show that the original judge would also pass. A blind run of the same 20 items through the original judge setup is still needed to count as a control.

Yes-rates by cell, quotable cells per QUOTABLE.md (F1 P/A, F2 P/A, F3 PRESENT). Source: review_queue/marks_page/items.json, bones_marks.json, and the marks given by Wayfinder for A-13 to A-28.
- Wayfinder, A-13..A-28 (16 rows): quotable cells 1 yes of 4 (yes 1, no 1, ct 2); non-quotable cells 7 yes of 12 (yes 7, no 1, ct 4). Code mix of these 16: F4 PRESENT 6, F5 ABSENT 3, F6 ABSENT 2, F6 PRESENT 1, F1 PRESENT 2, F2 PRESENT 1, F2 ABSENT 1. His quotable yes is A-17 (F1 PRESENT).
- Blind pass, same 16 rows: quotable 0 of 4 (no 3, ct 1); non-quotable 0 of 12.
- Blind pass, all of set A (40 rows): quotable 0 of 14 (no 12, ct 2); non-quotable 0 of 26. Code mix: F4 PRESENT 10, F2 PRESENT 6, F1 PRESENT 5, F5 ABSENT 5, F6 ABSENT 5, F2 ABSENT 3, F6 PRESENT 3, F3 ABSENT 1, F5 PRESENT 1, F7 PRESENT 1.
- Blind pass, set C (20 teacher-PRESENT train rows): quotable 0 of 9, non-quotable 0 of 11.
- Sampling seed: set A is 40 of the v1 silver PRESENT/ABSENT rows after random.Random(4242).shuffle (scripts/spot_check.py, build_marks_page.py). Wayfinder's 16 are positions 13 to 28 of that draw. Set B seed 1112, set C seed 1113.
- Reading: the quotable-cell quotes that v1 produced are mostly weak (A-17's quote only says the experiment ran on a Heron device, A-20, A-03, C-04, C-10 are method sentences). The blind judge's no there is mostly right on the words. The split Wayfinder-yes against blind-no sits almost entirely in non-quotable cells, where his yes rate is 7 of 12 and the judge's is 0 of 12. That supports the cell split in QUOTABLE.md, but only on 16 hand marks.

## 5. The 7 missed twins
They are results/contamination_wall.json "missed_twins": the matcher's positive-control twins of gold items that it failed to flag (105 of 112 flagged). Check file: results/missed_twins_check.json. Method: word-Jaccard of the twin title against every title in the 2300-paper pool (all_pool), against data/pool_with_wall_flags.json, and against results/slice_wall_flagged.jsonl, plus a search for the twin DOI in pool links. No match anywhere (best title Jaccard 0.208, the match line is 0.8, no DOI in any link). So none of the 7 is in the pool.
- 10.5281/zenodo.19812235, gold b3dab6a62172 (dev), best pool title 0.150
- 10.5281/zenodo.18165162, gold 08c4a2608cbe (dev), 0.208
- 10.5281/zenodo.19473977, gold 9862f0571c06 (dev), 0.159
- 10.5281/zenodo.19473978, gold 9862f0571c06 (dev), 0.138 (German-language title)
- 10.5281/zenodo.23246373, gold c8464231d15c (dev), 0.200
- 10.5281/zenodo.22072152, gold c71467663457 (test), 0.184
- 10.5281/zenodo.22072153, gold c71467663457 (test), 0.140
Caveat: a title match only; a twin with a changed title and abstract could still sit in the pool. The hand check Sage asked for (reading the 7 twin records against pool abstracts) is not done. Two of the 7 twin a test-half gold item (c71467663457).

## 6. What makes v2 hard to train
- F1, F4, F6 have no rows after the status cap, so STAN v2 cannot be trained or scored on them. They must be reported as untested.
- F1 has 42 unanimous grounded PRESENT and nothing else (no ABSENT, no CT, no NA): the teachers never agreed on anything else.
- F4 to F7 hold only CT and NA, because P/A is non-quotable there. The model will learn "F5 is CT or NA", a rule, and the per-code plurality predictor will sit near that rule (valid rates 0.33 to 0.40 where it exists, so the gate is not trivial, but the valid sets are 5 to 8 rows).
- CT is not vanishing but most of it came through round 2. Of 89 CT silver rows before the cap (F3 14, F4 28, F5 39, F7 8), 80 were agreed only after round 2 and 9 in round 1 (F5 8, F3 1). Round 2 showed reviewers the other teachers' labels, and showed an unquoted call as "held as CANNOT_TELL METHOD_UNSTATED", so round-2 agreement on CT is likely influenced. That is a risk to flag, not a measured effect. After the cap CT is 12 of 33 valid rows.
- Train rows total 131 (F2 68, F3 14, F5 38, F7 11). Valid is 33 rows. F3 and F7 are under the 15-row line, and every per-code valid slice is 5 to 18 rows.
- Still owed from Sage: the blind positive control with the original judge, the hand check of the 7 twins, the 20 ceiling rows marked, the decided-items split sealed, and the pilot status-token diagnostic (P(CT) by true class on the held-out silver slice) before any gold read.
