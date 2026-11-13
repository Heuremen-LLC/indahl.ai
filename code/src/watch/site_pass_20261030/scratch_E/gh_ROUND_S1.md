# Stated Against Delivered, model claims, round S1: SmolLM2-1.7B-Instruct (28 Oct 2026, his word)
Written and committed before any claim in it is run. This follows CLAIMS_STACK_PLAN.md and adds the specifics for the first model. One round is one model. A round lists every numeric result in the model's own card, and a result with no matching public task is listed as NOT RUN with the reason.

## The claim list
claims_s1.csv, nine results from the Instruction Model table of the card at huggingface.co/HuggingFaceTB/SmolLM2-1.7B-Instruct, fetched 28 October 2026. Six run and three are NOT RUN (MT-Bench is scored by a judge model, OpenRewrite-Eval has no public task, MMLU-Pro MCF is a different formulation from the harness task). The card says all evaluations are zero-shot unless stated, run with lighteval. It does not name the metric variant for HellaSwag, ARC, PIQA, IFEval or GSM8K. Where the variant is not named, every variant listed in the CSV is computed and the claim is read against all of them.

## Instrument
EleutherAI lm-evaluation-harness 0.4.13 through mlx-lm 0.32.2 on this Mac, the original weights in bf16 (HuggingFaceTB/SmolLM2-1.7B-Instruct), batch size 8, a pinned seed, the shots in the CSV. Loglikelihood tasks run without the chat template. IFEval runs with the model's chat template. The quantized Ollama copy is not run in this round because it does not return log-likelihoods. That gap is listed, not filled.

## Known-good first
GPT-2 (openai-community/gpt2) is run on ARC-Challenge 25-shot and HellaSwag 10-shot with the same code path. The independent record is the old Open LLM Leaderboard results file for gpt2 (dataset open-llm-leaderboard-old/results, file results_2024-03-23T06-18-16.565546.json): ARC-Challenge acc_norm 0.2201 and HellaSwag acc_norm 0.3153. If our value is not within two standard errors of each, nothing in this round is read, and the harness setup is corrected in a dated addendum first.

## Outcomes
For each claim and each listed variant the interval is our value plus or minus 1.96 times the harness standard error, widened by 0.05 for the rounding of the printed figure. CONSISTENT where the stated value is inside the interval of at least one listed variant. BELOW where the stated value is above the upper end of every listed variant (the delivered value is lower than stated). ABOVE where the stated value is below the lower end of every listed variant. CANNOT_TELL where the setting is undisclosed beyond what is listed, the sample is too small for the printed precision, or the run did not complete. Each BELOW, ABOVE and CANNOT_TELL is recounted by hand and a one-line rebuttal is written and tested before it is printed.

## Reading and release
Per claim: stated value, our value and interval per variant, outcome, the command, the raw harness output file and its SHA-256. No ranking, no adjectives. The page shows run progress live and each outcome as it is read. The scripts, outputs and DOI go with the round. A right of reply is open on the page from the first day.

## ADDENDUM 1 (28 Oct, found reading the first outputs, before any generation result was printed)
The known-good check covered the log-likelihood tasks (ARC-Challenge, HellaSwag). The first GSM8K 5-shot output read 0.4% against the card's 48.2%, far enough that the instrument is the first suspect. The generation path has no known-good. The BBH run also stopped with a Metal out-of-memory error while other jobs shared the GPU, and IFEval stopped on a missing dependency (langdetect), now installed.
Rules from here: (1) no generation-task result (GSM8K, BBH, IFEval) is printed until a generation known-good passes: the GSM8K path is rerun on 40 questions with batch size 1 and batch size 8, and a model with an independent published GSM8K 5-shot record is run through the same path; (2) generation tasks run one at a time, batch size chosen by that check, with no other GPU job running; (3) the three held rows show "held: generation check pending" on the live block until then.

## ADDENDUM 2 (28 Oct, written before any generation run that follows it)
Cause of the first GSM8K reading: SmolLM2-1.7B-Instruct, given the harness's plain few-shot prompt with no chat template, ends its reply at once (empty output on three questions read by hand). The harness and the model are doing what they were told, and the card does not say which prompt format it used. Variants, all run and all read against the stated value as in the outcome rule: GSM8K plain, GSM8K with the chat template, GSM8K with the chat template and the few-shot examples as turns. BBH plain and with the chat template. IFEval with the chat template only. A claim is CONSISTENT where the stated value is inside the interval of at least one variant, BELOW where it is above every variant, ABOVE where it is below every variant, CANNOT_TELL otherwise.
Generation known-good, declared before it runs: Qwen/Qwen1.5-1.8B (base weights, bf16) on GSM8K 5-shot through the same code path, against the old Open LLM Leaderboard record for the same model (open-llm-leaderboard-old/results, file results_2024-02-18T05-41-51.154248.json): acc 0.3359 with standard error 0.0130. The check passes if the strict-match or the flexible-extract value lies within two combined standard errors (the square root of the two squared standard errors, times two) of 33.59. The old harness and the current one differ in answer extraction, which is why either variant may pass. On a pass the held rows are released, on a fail they stay held and the setup is corrected in addendum 3.
Run order: one GPU job at a time, after the Falcon evaluation ends, batch size 4 (the earlier batch 8 BBH run stopped on a Metal out-of-memory error while other jobs shared the GPU).

## ADDENDUM 3 (29 Oct, written before the BBH chat run starts)
Order change, on Wayfinder's word of 29 Oct that IRIS shows live training: the run bbh_chat, the last run of the round, is deferred and runs after Falcon round 3 (FALCON_TRAIN_PLAN_3.md) instead of before it. The BBH plain run, already running, finishes first and its result is read as planned. Nothing about what is measured, the model, the prompts, the batch size, the seed or the scoring changes, and the BBH chat run is added to the lab queue as the job s1-bbh-chat, which runs run_s1b.sh, skips every finished run and runs only the chat variant. One GPU job at a time still holds. The state file says "BBH chat run deferred behind Falcon round 3" until it has run. The rename of the old-name files, written to run when the round ends, is moved to run when the BBH chat run ends.

## ADDENDUM 4 (30 Oct, written before any BBH result is read and before the rerun)
The BBH plain run (started 29 Oct 01:12 UTC) stopped writing progress at 4,850 of 6,511 items at 21:02 UTC on 29 Oct while the process kept the GPU busy. It was stopped on Wayfinder's word at about 01:05 UTC on 30 Oct, together with the hand-off script that would have read it and the paused round script. The run wrote no output and no BBH result was read. Rerun: both BBH runs (plain and chat) get --max-tokens 256, the generation length the evaluation harness uses when a task sets none. Every other setting is unchanged. Order unchanged from Addendum 3: Falcon round 3 first, then the queue job s1-bbh-chat, which now runs bbh_plain and then bbh_chat. A reply cut at 256 tokens is scored as written.

## ADDENDUM 5 (30 Oct, about 03:20 UTC, after the BBH reruns ended; no BBH or IFEval rate has been read)
IFEval chat (ifeval_chat) has never produced a result: on 28 Oct and again on 29 Oct the harness generated all 541 replies and then stopped with
"ValueError: min() iterable argument is empty" inside mlx_lm's generate_until, before scoring, so no output file exists. Recorded as NOTHING_RETURNED
for the IFEval chat claim (S1-01 setting), not a reading. BBH plain and BBH chat finished under addendum 4 (6,511 samples each).

## Addendum 6 (30 Oct 2026, about 11:30 UTC, the hand recount of the outcomes)
CLAIMS_STACK_PLAN.md, which every round runs under, reads CANNOT_TELL "where the setting is undisclosed, the harness differs ... or the claim needs a
private prompt format". This round's own Outcomes section left the harness clause out. The SmolLM2 card states every figure was run with lighteval,
and we ran EleutherAI lm-evaluation-harness, so the harness differs on every claim. The vendor's rebuttal ("the prompts differ") has not been tested.
Recount: a stated value outside our interval reads CANNOT_TELL, with the direction under our harness printed beside it. CONSISTENT stands, as a bound
under our harness. S1-05 (ARC, printed ABOVE by a margin of 0.002 points) and S1-08 (BBH, printed BELOW) become CANNOT_TELL with their direction
beside. The test that would decide them: the same claims rerun with lighteval at the card's settings, queued as its own plan.
