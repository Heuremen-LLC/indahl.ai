# Round S3: IBM Granite 4.1 3B, stated results rerun (written and committed before any S3 run; 30 Oct 2026, under CLAIMS_STACK_PLAN.md)
Model: ibm-granite/granite-4.1-3b (the instruction model, Apache 2.0), original bf16 weights from Hugging Face, setup A of CLAIMS_STACK_PLAN.md
(this Mac, one worker, mlx_lm evaluate over EleutherAI lm-evaluation-harness, the same environment as rounds S1 and S2).
Claims: claims_s3.csv, from the card's Evaluation Results table (3B Dense column), hand-checked against the card text saved in cards/ (sha256 7868b8ea...):
MMLU 5-shot 67.02, BBH 3-shot CoT 75.83, GSM8K 8-shot 86.88. The card does not name its evaluation harness or prompts; that is stated beside every outcome.
Runs (run_s3.sh, batch size 4, seed 20281028): mmlu 5-shot (log-likelihood, no chat template); bbh_cot_fewshot 3-shot with the chat template
(few-shot as multi-turn), --max-tokens 512; gsm8k 8-shot plain and gsm8k_cot 8-shot with the chat template (few-shot as multi-turn), --max-tokens 512.
The card says only "8-shot" for GSM8K, so both forms are reported side by side and neither is chosen after the result.
Not run in S3: MMLU-Pro (one overnight slot), GPQA (subset not named), IFEval (the harness stops after generation, S1 addendum 5), the code tasks
(need sandboxed execution), and every judge-scored or aggregate row (claims_s3.csv lists only what runs).
Known-good, outcomes, parser hand-check and publication: as ROUND_S2.md.

## Addendum 1 (30 Oct, about 08:45 UTC)
During the overnight watch, a liveness read of the tail of s3/bbh_cot_chat.log showed the run's BBH rate before the parser hand-check that this plan
puts first. Nothing changes: the outcome rule (stated value against our 95% interval, setting match) was fixed before the run and is mechanical, and the
hand-check of 10 BBH replies still comes before the outcome is computed or published. Watch reads of these logs now take only the progress lines.
Also recorded: the run looked stalled at item 4,850 of 6,511 for 33 minutes and then finished (04:30 local); it was not stopped.

## Addendum 2 (30 Oct 2026, about 11:10 UTC, before the parser hand-check)
Hand-check as ROUND_S2.md Addendum 1 (handcheck.py, same settings as run_s3.sh, replies saved). GSM8K plain and GSM8K CoT chat: the first 10 test
questions. BBH CoT chat: the first test question of each of the first 10 subtasks in alphabetical order. Files: handcheck/s3_*.json, HANDCHECK_S3.md.

## Addendum 3 (30 Oct 2026, about 11:30 UTC, before any S3 outcome is computed)
Same reconciliation as ROUND_S1.md Addendum 6: the card does not name its harness or prompts, so the setting is undisclosed. A stated value outside
our interval reads CANNOT_TELL with the direction under our harness beside it. CONSISTENT stands as a bound.

## Correction (30 Oct 2026, site pass) to Addendum 3
Addendum 3 is headed "about 11:30 UTC, before any S3 outcome is computed". It was committed at 11:07:51 UTC (git d0da402). The S3 outcome file was written at 11:12 UTC and committed at 11:12:36 UTC (git 4907629), so the order stands but the time above is wrong. The heading is left as written.

## Addendum 4 (30 Oct 2026, site pass, about 13:55 UTC)
1. The claim list now holds every row of the card's Evaluation Results table (3B Dense column). The plan said claims_s3.csv "lists only what runs", but CLAIMS_STACK_PLAN.md lists a claim with no matching task as NOT RUN with the reason and never omits it. The 26 rows that were left out are added as NOT RUN with a reason each (judge-scored, runs generated code, no task in the harness, or not run in this round for one overnight slot). The three rows that ran are unchanged. The values were checked against cards/ibm-granite_granite-4.1-3b.md (sha256 7868b8ea...).
2. Known-good scope, as ROUND_S2.md Addendum 3. The round S1 check covers the plain-prompt GSM8K path, which S3 uses for gsm8k. It does not cover mmlu, the bbh_cot_fewshot task or any run with the chat template. state_s3.json now says so.
3. Parser hand-check, counts re-read from handcheck/s3_gsm8k_cot_chat.json. Chat flexible-extract read 9 of 10 replies as written (question 5 took "16" from "for 16 glasses", where the model answered 64). Chat strict-match found no answer on 2 of 10 (questions 5 and 8), 1 of them correct. By the rule applied to round S1 in ROUND_S1.md Addendum 7 (more than 1 of 10 off), chat strict-match is CANNOT_TELL (parser) and no longer counts toward the outcome. The S3-11 outcome does not change, because chat flexible-extract still holds the stated value. BBH chat missed 1 of 10 and stays a counted variant.
