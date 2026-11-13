# Ledger commands for lane D (IRIS), site pass 30 Oct 2026
Run from ~/bones-forge/ledger. Run them BEFORE ledger/ship.sh builds the site (ledger edit before surface edit). Every snippet below was checked against a preview render of the changed pages (norm() from check_ledger.py), so after the commands and the build, check_ledger.py should report no drift for iris.* rows.
Where a command says --checks, the CHECKS.md entry is yours to supply (ledger.py add refuses without one).

## 1. D-1: withdraw the two "judge saw items more than once" rows
Evidence: iris_index/judge_counts/tag_audit_20261030.txt (a recount of autonomous_judge.log, 1,779 verdict lines, 374 distinct tags). The tag in parentheses on each verdict line is not an item id. Two tags are adapter names (1,240 verdicts), 16 are one-character buckets, 175 are three-character labels that repeat by chance (6 repeated, about 4 expected), 181 are unique. The log has no field that names the item a verdict was made on. judge_counts.py no longer outputs the three keys, so both rows also show SOURCE drift in check_ledger.py until withdrawn.
```
python3 ledger.py withdraw iris.judge.multi --why "The 24 'items seen more than once' are 2 adapter names, 16 one-character buckets and 6 chance collisions of a short label. The log tag is not an item id." --evidence iris_index/judge_counts/tag_audit_20261030.txt --test "Grouped every verdict line of autonomous_judge.log by its tag and classified the 374 tags: 2 adapter names (1,240 verdicts), 16 one-character labels, 175 three-character labels (6 repeat, about 4 expected by chance), 181 unique. No item id exists in the log."
python3 ledger.py withdraw iris.judge.differ --why "22 of 24 counted differing verdicts between buckets of a short label, not between looks at the same item. It says nothing about the judge's agreement with itself." --evidence iris_index/judge_counts/tag_audit_20261030.txt --test "Same recount as iris.judge.multi: the 24 grouped tags are not items, so the 22 differing is not a count of items judged twice."
```
No other live ledger row carries 24, 374, 22 of 24 or 91.7 (searched ledger.jsonl, build_site.py, the built pages and the HF stage). Not in the ledger but carrying the same claim: the Hugging Face dataset README for indahl/iris-judge-counts says "how often a judge model repeats itself on the same item" (hf_indahl/build.py line 58, outside lane D). Its stage copy of judge_counts.py and summary.json are the old versions.

## 2. New rows for numbers now printed (D-1, D-10, D-26)
```
python3 ledger.py add iris.judge.adapter_names --claim "Judge verdicts logged under the two names of our own adapter" --value 1240 --outcome COUNT --source iris_index/judge_counts/summary.json --grep '"verdicts_under_adapter_names": 1240' --on iris_matrix "1,240" --checks <CHECKS.md>
python3 ledger.py add iris.orch.rounds_three --claim "Orchestration rounds in which three models were asked" --value 6347 --outcome COUNT --source iris_index/judge_counts/summary.json --grep '"rounds_with_three_asks": 6347' --on iris_matrix "6,347" --checks <CHECKS.md>
python3 ledger.py add iris.train.minbeforelast_pre --claim "Sessions before the 26 August validation fix whose lowest validation loss came before their last check" --value 85 --outcome RECORD --source iris_index/training_counts/summary.json --grep '"runs_val_min_before_last": 85' --on iris_matrix "85 of 90" --checks <CHECKS.md>
python3 ledger.py add iris.train.improved_post --claim "Sessions after the validation fix whose last validation loss was below their first" --value 0 --outcome RECORD --source iris_index/training_counts/summary.json --grep '"runs_val_improved": 0' --on iris_matrix "0 of 9" --checks <CHECKS.md>
python3 ledger.py add iris.train.minbeforelast_post --claim "Sessions after the validation fix whose lowest validation loss came before their last check" --value 7 --outcome RECORD --source iris_index/training_counts/summary.json --grep '"runs_val_min_before_last": 7' --on iris_matrix "7 of 9" --checks <CHECKS.md>
python3 ledger.py off iris.train.minbeforelast iris_matrix --why "D-26: the pooled 92 of 99 is no longer printed. The page splits sessions at the 26 August validation fix (85 of 90 before, 7 of 9 after). The row stays as a count."
```
The other iris.judge.* rows (verdicts 1,779, hold, discard, keep, errors) and iris.orch.* rows (rounds 11,057, asks 19,141, forced 14,526) keep their numbers and surfaces.

## 3. D-26: the "36" row keeps its value, new surface text
```
python3 ledger.py off iris.train.improved iris_matrix --why 'D-26, 30 Oct 2026 site pass: sessions split at the 26 August validation fix, this is the before-fix count'
python3 ledger.py on iris.train.improved iris_matrix '36 of 90'
```

## 4. D-5, D-6: the ten model rows of the top table (new cell text, 8 rows change)
The "prompt reworded" cell now prints "k of 200 items" and is cannot tell where more than 10 percent of items were unread (falcon3:3b, smollm2:1.7b, granite3.3:2b, phi4-mini). The exact-repeat cell is a count with a Wilson interval (computed in build_iris_page.py wilson_ from copy_disagree k and n in matrix_v2_results_v2.json). The deepseek-r1:1.5b and qwen3:4b rows are unchanged.
```
python3 ledger.py off iris.r2.falcon3_3b iris_matrix --why 'D-5, D-6, 30 Oct 2026 site pass: the row now carries the items read under the reworded-prompt rate (cannot tell above 10 percent unread) and the exact repeat as a count with a Wilson interval'
python3 ledger.py on iris.r2.falcon3_3b iris_matrix 'falcon3:3b 49.2% -3.1 points [-10.9, +4.1] 42.5% [35.8, 49.2] cannot tell (27 of 200 items readable in the reworded format) 0.5% [0.1, 2.8] 1 of 195'
python3 ledger.py off iris.r2.gemma3_4b iris_matrix --why 'D-5, D-6, 30 Oct 2026 site pass: the row now carries the items read under the reworded-prompt rate (cannot tell above 10 percent unread) and the exact repeat as a count with a Wilson interval'
python3 ledger.py on iris.r2.gemma3_4b iris_matrix 'gemma3:4b 52.5% cannot tell (failed the first-option check) cannot tell (failed the first-option check) 11.3% [7.2, 15.9] 195 of 200 items 0.0% [0.0, 1.9] 0 of 200'
python3 ledger.py off iris.r2.granite3.3_2b iris_matrix --why 'D-5, D-6, 30 Oct 2026 site pass: the row now carries the items read under the reworded-prompt rate (cannot tell above 10 percent unread) and the exact repeat as a count with a Wilson interval'
python3 ledger.py on iris.r2.granite3.3_2b iris_matrix 'granite3.3:2b 46.8% cannot tell (failed the first-option check) cannot tell (failed the first-option check) cannot tell (51 of 200 items readable in the reworded format) 0.0% [0.0, 2.2] 0 of 173'
python3 ledger.py off iris.r2.llama3.1_8b iris_matrix --why 'D-5, D-6, 30 Oct 2026 site pass: the row now carries the items read under the reworded-prompt rate (cannot tell above 10 percent unread) and the exact repeat as a count with a Wilson interval'
python3 ledger.py on iris.r2.llama3.1_8b iris_matrix 'llama3.1:8b 61.5% cannot tell (failed the first-option check) cannot tell (failed the first-option check) 12.0% [7.5, 17.0] 200 of 200 items 0.0% [0.0, 1.9] 0 of 200'
python3 ledger.py off iris.r2.mistral_7b iris_matrix --why 'D-5, D-6, 30 Oct 2026 site pass: the row now carries the items read under the reworded-prompt rate (cannot tell above 10 percent unread) and the exact repeat as a count with a Wilson interval'
python3 ledger.py on iris.r2.mistral_7b iris_matrix 'mistral:7b 53.3% +1.5 points [-4.5, +8.1] 27.3% [21.2, 33.8] 13.1% [8.4, 18.3] 191 of 200 items 0.0% [0.0, 1.9] 0 of 199'
python3 ledger.py off iris.r2.olmo2_7b iris_matrix --why 'D-5, D-6, 30 Oct 2026 site pass: the row now carries the items read under the reworded-prompt rate (cannot tell above 10 percent unread) and the exact repeat as a count with a Wilson interval'
python3 ledger.py on iris.r2.olmo2_7b iris_matrix 'olmo2:7b 53.8% cannot tell (failed the first-option check) cannot tell (failed the first-option check) 20.8% [14.8, 26.2] 183 of 200 items 0.0% [0.0, 1.9] 0 of 195'
python3 ledger.py off iris.r2.phi4-mini iris_matrix --why 'D-5, D-6, 30 Oct 2026 site pass: the row now carries the items read under the reworded-prompt rate (cannot tell above 10 percent unread) and the exact repeat as a count with a Wilson interval'
python3 ledger.py on iris.r2.phi4-mini iris_matrix 'phi4-mini 53.3% +3.5 points [-3.5, +10.1] 27.8% [21.7, 34.3] cannot tell (142 of 200 items readable in the reworded format) 0.0% [0.0, 1.9] 0 of 199'
python3 ledger.py off iris.r2.smollm2_1.7b iris_matrix --why 'D-5, D-6, 30 Oct 2026 site pass: the row now carries the items read under the reworded-prompt rate (cannot tell above 10 percent unread) and the exact repeat as a count with a Wilson interval'
python3 ledger.py on iris.r2.smollm2_1.7b iris_matrix 'smollm2:1.7b 36.2% +2.6 points [-5.2, +9.9] 50.0% [43.2, 57.3] cannot tell (20 of 200 items readable in the reworded format) 0.0% [0.0, 1.9] 0 of 196'
```

## 5. D-8 to D-14, D-25: study "what it shows" text (7 rows, surface sad)
```
python3 ledger.py off iris.study.2610.17203 sad --why 'D-8 to D-14, D-25, 30 Oct 2026 site pass: the study text now carries the caveats and denominators in the finding'
python3 ledger.py on iris.study.2610.17203 sad 'Under our planned scoring rule, which scores a judge by the share of its 16 picks per item, the GPT-5.6-Sol judge scores 72.9 against 74.5 printed. The printed 74.5 rebuilds exactly only under a rule found after the data, which scores the judge by its more-picked answer.'
python3 ledger.py off iris.study.2610.21468 sad --why 'D-8 to D-14, D-25, 30 Oct 2026 site pass: the study text now carries the caveats and denominators in the finding'
python3 ledger.py on iris.study.2610.21468 sad 'The Gemini 3.1 Pro judge agrees with the reader majority 0.657 [0.486, 0.800] of the time on G1 against G2, consistent with chance. On G1 against G0 it agrees 0.839 [0.710, 0.968] of the time, above chance. Both are paired on items decisive for both, 35 and 31 items. Readers agree with themselves 0.930.'
python3 ledger.py off iris.study.2610.25159 sad --why 'D-8 to D-14, D-25, 30 Oct 2026 site pass: the study text now carries the caveats and denominators in the finding'
python3 ledger.py on iris.study.2610.25159 sad 'The GPT labeller the gold labels were reviewed from scores 0.960 accuracy on that gold, ahead of every trained classifier by 0.115 to 0.145. The gold was built by reviewing this labeller’s output, so the lead cannot be separated from anchoring. The labeller is not in the paper’s results table.'
python3 ledger.py off iris.study.2610.25626 sad --why 'D-8 to D-14, D-25, 30 Oct 2026 site pass: the study text now carries the caveats and denominators in the finding'
python3 ledger.py on iris.study.2610.25626 sad 'With seeds as the unit, MapSteal’s lead over the best other method resolves in 2 of 18 settings, uncorrected for 18 tests, is consistent with zero in 15 and is behind in 1. The comparison is a Welch interval on three seeds against three, and the two lower bounds are +0.03 and +0.06 points. The authors’ 12 of 18 is a correct count of means.'
python3 ledger.py off iris.study.2610.25964 sad --why 'D-8 to D-14, D-25, 30 Oct 2026 site pass: the study text now carries the caveats and denominators in the finding'
python3 ledger.py on iris.study.2610.25964 sad 'LLaVA-1.5-7B at 4-bit precision scores differently depending on which yes or no tokens are read: F1 moves 6.13 points [4.43, 7.83] on the adversarial split, 5.37 on popular and 3.15 on random. The authors say the shift exceeds the adversarial gain reported by five of the six papers they surveyed. Against our interval four of those six gains lie below the lower bound, one inside and one above, and the six carry no widths. The paper says the comparison stays unresolved until readout and precision are matched.'
python3 ledger.py off iris.study.2610.30512 sad --why 'D-8 to D-14, D-25, 30 Oct 2026 site pass: the study text now carries the caveats and denominators in the finding'
python3 ledger.py on iris.study.2610.30512 sad 'The same pinned GPT-4.1 judge changed outcomes on 27.3% of prompts where the reported serving backend changed and 17.5% where it did not (+9.8 points [+2.1, +17.6]). This splits prompts by a reported fingerprint and does not name a cause. Prompts with a changed backend sat somewhat nearer the decision boundary, and within margin bands (defined after the data) the gap is +8.0 points [+0.7, +15.3]. In an earlier experiment, run once per judge with no repeat floor, GPT-4.1, Claude Sonnet 4.5 and Gemini 2.5 Flash flip about 3 verdicts in 10 when the two answers swap position.'
python3 ledger.py off iris.study.2610.31135 sad --why 'D-8 to D-14, D-25, 30 Oct 2026 site pass: the study text now carries the caveats and denominators in the finding'
python3 ledger.py on iris.study.2610.31135 sad 'Same model and seed: 8,000 of 8,000 question-position cells identical on the same host. On a different GPU and host, 76 of 8,000 cells (0.95%) change, A40 against A10G. The primacy gap moves by +0.0019 [-0.0050, +0.0088], consistent with zero.'
```

## 6. D-22: Finalists table, one line per round, no semicolon (8 rows, surface iris_lab)
The source lines in iris_index/thunder_results.txt keep their old text, so the rows' source.grep still matches.
```
python3 ledger.py off iris.thunder.p1.smollm2 iris_lab --why 'D-22, 30 Oct 2026 site pass: no semicolon in table text, one line per round'
python3 ledger.py on iris.thunder.p1.smollm2 iris_lab 'Round 12: cannot tell, 30 of 30 unread Round 13: cannot tell, 5 of 30 unread'
python3 ledger.py off iris.thunder.p1.qwen3 iris_lab --why 'D-22, 30 Oct 2026 site pass: no semicolon in table text, one line per round'
python3 ledger.py on iris.thunder.p1.qwen3 iris_lab 'Round 12: cannot tell, 5 of 30 unread Round 13: cannot tell, 5 of 30 unread'
python3 ledger.py off iris.thunder.p2.smollm2 iris_lab --why 'D-22, 30 Oct 2026 site pass: no semicolon in table text, one line per round'
python3 ledger.py on iris.thunder.p2.smollm2 iris_lab 'Round 12: cannot tell, 27 of 30 unread Round 13: cannot tell, 22 of 30 unread'
python3 ledger.py off iris.thunder.p2.qwen3 iris_lab --why 'D-22, 30 Oct 2026 site pass: no semicolon in table text, one line per round'
python3 ledger.py on iris.thunder.p2.qwen3 iris_lab 'Round 12: cannot tell, 28 of 30 unread Round 13: 100% [89, 100], 0 of 30 unread'
python3 ledger.py off iris.thunder.p3.smollm2 iris_lab --why 'D-22, 30 Oct 2026 site pass: no semicolon in table text, one line per round'
python3 ledger.py on iris.thunder.p3.smollm2 iris_lab 'Round 12: cannot tell, 0 of 20 unread Round 13: cannot tell, 0 of 20 unread'
python3 ledger.py off iris.thunder.p3.qwen3 iris_lab --why 'D-22, 30 Oct 2026 site pass: no semicolon in table text, one line per round'
python3 ledger.py on iris.thunder.p3.qwen3 iris_lab 'Round 12: cannot tell, 20 of 20 unread Round 13: cannot tell, 20 of 20 unread'
python3 ledger.py off iris.thunder.p4.smollm2 iris_lab --why 'D-22, 30 Oct 2026 site pass: no semicolon in table text, one line per round'
python3 ledger.py on iris.thunder.p4.smollm2 iris_lab 'Round 12: 0% [0, 11], 0 of 30 unread Round 13: 0% [0, 11], 0 of 30 unread'
python3 ledger.py off iris.thunder.p4.qwen3 iris_lab --why 'D-22, 30 Oct 2026 site pass: no semicolon in table text, one line per round'
python3 ledger.py on iris.thunder.p4.qwen3 iris_lab 'Round 12: cannot tell, 30 of 30 unread Round 13: cannot tell, 29 of 30 unread'
```

## 7. D-16: Falcon table cells now say how many replies were read (12 rows, surface iris_lab)
The old snippet is the start of the new cell text, so these rows do not show drift. Swap only if the printed counts should be ledger-tracked. The counts come from the new "read ..." lines in iris_index/falcon_train/falcon_results.txt.
```
python3 ledger.py off iris.falcon.p1.base iris_lab --why 'D-16, 30 Oct 2026 site pass: the cell now says how many replies were read (source lines "read ..." in iris_index/falcon_train/falcon_results.txt)'
python3 ledger.py on iris.falcon.p1.base iris_lab 'A 0% [0, 12], B cannot tell Replies read: A 29 of 30, B 30 of 30'
python3 ledger.py off iris.falcon.p1.trained iris_lab --why 'D-16, 30 Oct 2026 site pass: the cell now says how many replies were read (source lines "read ..." in iris_index/falcon_train/falcon_results.txt)'
python3 ledger.py on iris.falcon.p1.trained iris_lab 'A 0% [0, 11], B 0% [0, 11] Replies read: A 30 of 30, B 30 of 30'
python3 ledger.py off iris.falcon.p1.mixed iris_lab --why 'D-16, 30 Oct 2026 site pass: the cell now says how many replies were read (source lines "read ..." in iris_index/falcon_train/falcon_results.txt)'
python3 ledger.py on iris.falcon.p1.mixed iris_lab 'A 100% [89, 100], B 100% [89, 100] Replies read: A 30 of 30, B 30 of 30'
python3 ledger.py off iris.falcon.p2.base iris_lab --why 'D-16, 30 Oct 2026 site pass: the cell now says how many replies were read (source lines "read ..." in iris_index/falcon_train/falcon_results.txt)'
python3 ledger.py on iris.falcon.p2.base iris_lab 'A 100% [88, 100], B 100% [88, 100] Replies read: A 29 of 30, B 29 of 30'
python3 ledger.py off iris.falcon.p2.trained iris_lab --why 'D-16, 30 Oct 2026 site pass: the cell now says how many replies were read (source lines "read ..." in iris_index/falcon_train/falcon_results.txt)'
python3 ledger.py on iris.falcon.p2.trained iris_lab 'A 0% [0, 14], B cannot tell Replies read: A 24 of 30, B 23 of 30'
python3 ledger.py off iris.falcon.p2.mixed iris_lab --why 'D-16, 30 Oct 2026 site pass: the cell now says how many replies were read (source lines "read ..." in iris_index/falcon_train/falcon_results.txt)'
python3 ledger.py on iris.falcon.p2.mixed iris_lab 'A cannot tell, B cannot tell Replies read: A 11 of 30, B 12 of 30'
python3 ledger.py off iris.falcon.p3.base iris_lab --why 'D-16, 30 Oct 2026 site pass: the cell now says how many replies were read (source lines "read ..." in iris_index/falcon_train/falcon_results.txt)'
python3 ledger.py on iris.falcon.p3.base iris_lab 'A cannot tell, B cannot tell Replies read: A 20 of 20, B 20 of 20'
python3 ledger.py off iris.falcon.p3.trained iris_lab --why 'D-16, 30 Oct 2026 site pass: the cell now says how many replies were read (source lines "read ..." in iris_index/falcon_train/falcon_results.txt)'
python3 ledger.py on iris.falcon.p3.trained iris_lab 'A 40% [22, 61], B 40% [22, 61] Replies read: A 20 of 20, B 20 of 20'
python3 ledger.py off iris.falcon.p3.mixed iris_lab --why 'D-16, 30 Oct 2026 site pass: the cell now says how many replies were read (source lines "read ..." in iris_index/falcon_train/falcon_results.txt)'
python3 ledger.py on iris.falcon.p3.mixed iris_lab 'A cannot tell, B cannot tell Replies read: A 20 of 20, B 20 of 20'
python3 ledger.py off iris.falcon.p4.base iris_lab --why 'D-16, 30 Oct 2026 site pass: the cell now says how many replies were read (source lines "read ..." in iris_index/falcon_train/falcon_results.txt)'
python3 ledger.py on iris.falcon.p4.base iris_lab 'A 0% [0, 11], B 0% [0, 12] Replies read: A 30 of 30, B 29 of 30'
python3 ledger.py off iris.falcon.p4.trained iris_lab --why 'D-16, 30 Oct 2026 site pass: the cell now says how many replies were read (source lines "read ..." in iris_index/falcon_train/falcon_results.txt)'
python3 ledger.py on iris.falcon.p4.trained iris_lab 'A 0% [0, 11], B 0% [0, 12] Replies read: A 30 of 30, B 29 of 30'
python3 ledger.py off iris.falcon.p4.mixed iris_lab --why 'D-16, 30 Oct 2026 site pass: the cell now says how many replies were read (source lines "read ..." in iris_index/falcon_train/falcon_results.txt)'
python3 ledger.py on iris.falcon.p4.mixed iris_lab 'A 100% [89, 100], B 100% [88, 100] Replies read: A 30 of 30, B 29 of 30'
```
