# Check blocks (watch/readcheck.py). One entry per reading, appended, never edited after commit.

## 2026-11-12 12:05 LAB headline: the untrained base model's agreement with the answer key on gold dev (F1 to F7 pooled), against the pooled majority-class rate
- I: holds: the untrained base model Qwen3-1.7B is the none arm, scored on the same 97 gold dev claims and the same seven codes as the three teachers, with the same agreement rule (predicted PRESENT equals gold PRESENT); 679 code calls pooled, 463 agree, nothing dropped, parse failures counted as disagreement
- II: n/a: one pass per model and claim, no repeated item and no flips between runs are claimed
- III: holds: agreement is unsigned and pooled over seven codes by summing agreements and calls; the majority-class rate is the n-weighted mean of the seven per-code rates and every per-code rate is also in baseline_dev.json
- V: holds: two rulers side by side, the model's agreement and the always-guess-the-commonest-answer rate per code, both read from stan/results/baseline_dev.json by code, with the Wilson 95 percent interval on the agreement only
- VI: n/a: the headline reads a baseline, not a comparison of STAN with anything, and the paired test against base on gold test is run once later under PLAN.md
- R: holds: every number is computed from baseline_dev.json by watch/headlines.py lab(), none typed, plan sha256 a6a7ea11 committed before any label was read, dev half of the answer key only, test untouched
- caught: base answers CANNOT_TELL for most codes, so its agreement mostly reflects the share of claims where the answer key says not present, which is why the majority-class rate sits above it for six of seven codes
- cannot tell: the answer key was made from full text and released files while every model here sees only the abstract, so how much of the gap to the answer key an abstract could ever close is not known

## 2026-11-12 18:00 STAN v1 paired test on gold test, read once (final.py), not kept
- I: holds: keep rule, interval and seed fixed in PLAN.md before any teacher call (committed and stamp submitted), checkpoint chosen by valid loss before any dev or test output, gold test read once by final.py which refuses a second run
- II: holds: flips counted item by item before netting, STAN right and base wrong 24, base right and STAN wrong 13, pooled over codes, per-code intervals printed
- III: holds: signed per-code differences printed separately, F5 is negative (-0.011), no sum claimed beyond the pre-registered pooled mean
- V: holds: paired bootstrap, 2000 resamples over items, seed 7, 95 percent percentile interval, named in the plan
- VI: holds: the pooled interval [0.000, 0.0346] reaches zero, so the reading is CANNOT_TELL (STRADDLES_EDGE) and the rule says not kept
- R: holds: numbers read from stan/results/paired_test.json
- caught: STAN answers CANNOT_TELL on every code of every item (decided share 0), so its agreement is the majority-class rate. It sorts nothing. Said on the page
- cannot tell: input is title and abstract only while the gold labels came from full-text reads, so abstract-only models may be unable to see what the recounts saw

## 2026-11-12 18:30 Lab headline changed to the decided share (Sage break 1), agreement headline withdrawn
- I: holds: the decided share counts a call as decided when it is PRESENT, ABSENT or NOT_APPLICABLE, the same definition score.py used before any result
- II: holds: per-code shares are kept in the source files, the pooled share is n-weighted over seven codes
- III: caught: the earlier agreement headline counted CANNOT_TELL as agreeing with an unflagged recount, a fold. Withdrawn from the page, rows stan.baseline.base and stan.baseline.majority withdrawn
- V: holds: a plain share with its count of calls printed, no interval claimed
- VI: n/a: descriptive share, not a stated-against-delivered comparison
- R: holds: read from stan/results/decided_summary.json, written by decided_summary.py from baseline_dev.json and paired_test.json
- cannot tell: whether the models abstain because the abstract lacks the evidence or because they cannot apply the codes. Sage's ceiling check decides it before v2

## 2026-11-12 19:40 Base CANNOT_TELL on the test half is the quote rule's, not the model's (v1 forensics)
- I: holds: both arms scored by the same norm_label rule (scripts/common.py:42-43) on the same 95 claims and seven codes, 665 calls each
- II: holds: counted call by call from runs/base_test.jsonl and runs/stan_test.jsonl by flag, nothing netted
- III: n/a: counts, no signed difference
- V: holds: plain counts with their denominators, written to results/base_conversion.json
- VI: n/a: descriptive count
- R: holds: base 559 of 665 calls CANNOT_TELL by the quote rule, 0 chosen by the model; STAN 665 of 665 chosen by the model, 0 by the rule. Recounted by Bones from the run files after the forensics agent reported it
- caught: the page's base decided share (0.123) read as the base model deciding; most of what it did not decide was turned into CANNOT_TELL by our own rule, so the base and STAN columns do not measure the same act
- cannot tell: what share of the converted base answers were right; the converted labels were never scored

## 2026-11-12 15:05 Lexical baseline (PLAN_A_v2 s4) on gold dev, as defined
- I: holds: cue rule fixed in PLAN_A_v2 (commit 0004ee3) before the run, cues taken mechanically from each PRESENT line, same top-6 chunks as the ceiling and teachers
- II: holds: flagged and unflagged counted separately per code, nothing pooled
- III: holds: signed difference flagged minus unflagged printed per code
- V: holds: Wilson 95 for each rate, Newcombe 95 for the difference
- VI: holds: F3 difference 0.218 [-0.011, 0.378] reaches zero, so CANNOT_TELL; F1 0.059 [-0.084, 0.142] CANNOT_TELL; F2 and F6 call PRESENT on 35/35 and 29/29 flagged and 56/57 and 62/63 unflagged, so no separation
- R: holds: read from stan/lexical/dev_result.json written by lexical/lexical_baseline.py
- caught: Bones first wrote "F3 separates somewhat" before computing the interval; the interval reaches zero. Fixed before commit
- cannot tell: whether a stricter cue rule would separate; changing the rule now would be a knob, so it goes to Sage before fresh recounts

## 2026-11-12 15:40 Full-text teacher re-baseline on gold dev, scored against PLAN_A_v2 s6 keep line: no teacher passes any code
- I: holds: keep line (grounded PRESENT on flagged minus on unflagged, Newcombe 95, lower bound above zero) committed in 0004ee3 before the full scores were read; a dry run on about a quarter of rows was seen at 14:25 to test the script and is declared in PLAN_A_v2
- II: holds: flagged and unflagged counted separately per teacher per code, nothing pooled across teachers or codes
- III: holds: signed difference printed per cell; signs mixed (Mistral F6 point estimate negative, F1 positive)
- V: holds: Wilson 95 per rate, Newcombe 95 per difference, statuses as written, no call converted
- VI: holds: 0 of 12 teacher-code cells have the whole interval above zero; nearest Mistral F1 [-0.006, 0.423] CANNOT_TELL. Gemma and Mistral call PRESENT on 89 to 100 percent of unflagged pairs; Llama commits on under 10 percent of pairs
- R: holds: read from stan/teachers_ft/summary.json written by score_ft.py over outputs.jsonl (1,104 rows: Mistral on Armature 368, Llama and Gemma on the Mac seat 368 each, no errors, no duplicates)
- caught: grounding is low. Gemma and Mistral often quoted the code's own definition text back as evidence, which the grounding check scores not_found. Grounded share of PRESENT/ABSENT calls is 7 to 51 percent
- cannot tell: whether a different prompt or larger teachers would pass; PLAN_A_v2 s6 closes this route rather than tuning the prompt on dev

## 2026-11-12 16:30 Thresholded lexical rule (Sage 20:15) on gold dev, dev-informed
- I: holds: threshold formula (above the per-code dev median cue count) fixed by Sage's wording before running; it uses the count distribution, not the flags; cues are the same mechanical PRESENT-line words as the registered rule; labelled dev-informed because dev was seen
- II: holds: flagged and unflagged counted separately per code
- III: holds: signed differences printed; F6 negative (-0.044), others positive
- V: holds: Wilson 95 per rate, Newcombe 95 per difference
- VI: holds: F2 0.225 [0.015, 0.408] whole interval above zero; F1, F3, F6 CANNOT_TELL; F2 is one of four codes and with a four-way correction its interval reaches zero, said in the report
- R: holds: read from stan/lexical/thresholded_rule.json; differences recomputed by hand from its counts
- caught: none
- cannot tell: whether F2's separation holds on fresh recounts; the rule is fixed now, before any fresh draw

## 2026-11-13 19:50 STAN-E LoRA ladder (lora_v1..v6, Qwen2.5-7B-Instruct 4-bit) re-read with the paper as the unit, against base
- I: holds: both held-out sets (test_hand, test_pipeline) and base were fixed before the ladder ran; every model scored on the same chunks; unparsed replies counted by arm (base 1 on test_hand, every LoRA 0) and left out of the pairing, so the denominators match by construction
- II: holds: flips counted both ways per set before any rate: recall v4 +9/-0 and +9/-0, v6 +10/-0 and +11/-0; false flags v4 +4/-0 and +4/-0, v6 +6/-1 and +4/-0
- III: holds: signed differences printed (model minus base); every recall difference positive, every false-flag difference positive (worse)
- V: holds: paper-cluster bootstrap (5,000 resamples, seed 20261113) for intervals, because chunks from one paper are not independent; exact two-sided sign test on discordant chunks beside it
- VI: holds: recall ABOVE base in all four cells (lowest lower bound 0.154); false flags ABOVE base for v6 test_pipeline (+0.103 [0.026, 0.19]), CANNOT_TELL in the other three cells (intervals reach 0 and 0.10). Size that matters 0.10, defined after the data
- R: holds: read from train_e/results/<model>_<set>.json written by eval_mlx.py; summary in train_e/results/clustered_read.json by train_e/clustered_read.py
- caught: chunk-level Wilson intervals in the night ladder rows were too narrow (handoff caveat); this read replaces them for any claim. No adapter is kept: the rule is beat base on both measures, and false flags rise
- cannot tell: whether v7 (data_short, lr 1e-5, 1200 iters, running) holds the recall gain with fewer false flags
