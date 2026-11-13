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
