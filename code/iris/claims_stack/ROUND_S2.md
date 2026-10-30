# Round S2: Phi-4-mini-instruct, stated results rerun (written and committed before any S2 run; 30 Oct 2026, under CLAIMS_STACK_PLAN.md)
Model: microsoft/Phi-4-mini-instruct, original bf16 weights from Hugging Face (MIT license), setup A of CLAIMS_STACK_PLAN.md (this Mac, one worker,
mlx_lm evaluate over EleutherAI lm-evaluation-harness, the same environment as round S1).
Claims: claims_s2.csv, taken from the vendor card's Model Quality table (first column, Phi-4 mini-Ins), every number hand-checked against the card
text saved in cards/ (sha256 c4f34916...). The card says Microsoft scored these on its own internal benchmark platform (Appendix A); our harness
prompts may differ from theirs. That difference is stated beside every outcome.
Runs (run_s2.sh, batch size 4, seed 20281028): mmlu 5-shot, arc_challenge 10-shot, boolq 2-shot, hellaswag 5-shot, openbookqa 10-shot, piqa 5-shot,
social_iqa 5-shot, winogrande 5-shot (log-likelihood, no chat template); gsm8k_cot 8-shot plain and gsm8k_cot 8-shot with the chat template
(few-shot as multi-turn), --max-tokens 512. TruthfulQA MC2 (10-shot) is NOT RUN: the harness task fixes its own shots.
Known-good: the seat's known-good from round S1 (passed 28 Oct: arc_challenge and hellaswag against the old leaderboard record, and the generation
known-good on Qwen1.5-1.8B GSM8K), same harness, same environment, same machine.
Outcomes (CLAIMS_STACK_PLAN.md): BELOW or ABOVE only where the stated value sits outside our 95% interval (the harness standard error, widened by the
card's rounding of 0.05) and the stated setting matches ours; CONSISTENT where it sits inside; CANNOT_TELL otherwise. Both GSM8K variants are reported
side by side; neither is chosen after the result. Parser hand-check of 10 GSM8K replies per variant before any rate is read.
One GPU job at a time; queued in iris_index/queue.json. Nothing goes on a page until the ledger has it.

## Addendum 1 (30 Oct 2026, about 11:10 UTC, before the parser hand-check)
The GSM8K plain result file was printed while we looked for the saved replies, so its rate was seen before the hand-check this plan puts first.
The hand-check and the outcome rule are unchanged. The runs saved no replies (mlx_lm evaluate has no flag for it), so the hand-check regenerates them:
handcheck.py calls the same lm_eval simple_evaluate path as mlx_lm evaluate, with the same model, task, shots, chat settings, max tokens and seed,
limited to the first 10 test questions, and saves every reply with what each filter extracted. Batch size 4 as the run. A reply passes when the
number we read by hand as the model's final answer equals what the filter extracted (strict-match and flexible-extract checked separately).
Any failed parse is printed beside the outcome. Files: handcheck/s2_gsm8k_cot_plain.json, handcheck/s2_gsm8k_cot_chat.json, HANDCHECK_S2.md.

## Addendum 2 (30 Oct 2026, about 11:30 UTC, before any S2 outcome is computed)
Same reconciliation as ROUND_S1.md Addendum 6: the card says Microsoft scored these on its own internal benchmark platform, so the harness differs.
A stated value outside our interval reads CANNOT_TELL with the direction under our harness beside it. CONSISTENT stands as a bound.
