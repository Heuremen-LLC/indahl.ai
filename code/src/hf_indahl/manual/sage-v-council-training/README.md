---
license: other
license_name: heuremen-attribution-no-ai-training
license_link: https://indahl.ai/terms#ai-training
pretty_name: "Sage V council training: method and numbers"
language:
- en
tags:
- lora
- mlx
- evaluation
- grounding
- fact-checking
- calibration
---

# Sage V council training

Sage V is a council of small open-weight models that answer questions from a private text library. Every claim a seat makes must carry an exact quote from a passage it was shown and a stated probability that the claim is right. We train LoRA adapters for the seats on this job and test each adapter against its own base model on the same job. This page gives the method and the numbers, updated with the paired evaluations of 9 Nov 2026. `results.json` holds every number below, and `code/` holds a copy of the harvest, serving, evaluation and scheduling scripts.

No weights are published. The adapters were trained on the private library and can carry its text, so the weights, the training rows, the prompts and the library stay private.

## The council

Seats are instruction models run locally through [Ollama](https://github.com/ollama/ollama), and through [mlx-lm](https://github.com/ml-explore/mlx-lm) ([PyPI](https://pypi.org/project/mlx-lm/)) once a seat has an adapter. Each question goes to groups of three seats. A seat answers alone, in JSON, with up to four claims. Each claim has one sentence, one quote, the id of the passage it quotes, and p, the seat's probability that the claim is right. CANNOT_TELL is a full answer when the passages do not settle the question.

| Role | Model | License |
|---|---|---|
| Seat | [ibm-granite/granite-3.3-8b-instruct](https://huggingface.co/ibm-granite/granite-3.3-8b-instruct) | Apache-2.0 |
| Seat | [NousResearch/Hermes-3-Llama-3.1-8B](https://huggingface.co/NousResearch/Hermes-3-Llama-3.1-8B) | Llama 3.1 Community License |
| Seat | [mistralai/Mistral-7B-Instruct-v0.3](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3) | Apache-2.0 |
| Seat until 9 Nov, 23:20 UTC | [microsoft/Phi-4-mini-instruct](https://huggingface.co/microsoft/Phi-4-mini-instruct) | MIT |
| Seat from 9 Nov, 23:20 UTC | [baidu/ERNIE-4.5-21B-A3B-PT](https://huggingface.co/baidu/ERNIE-4.5-21B-A3B-PT) | Apache-2.0 |
| Seat | [meta-llama/Llama-3.2-3B-Instruct](https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct) | Llama 3.2 Community License |
| General judge | [Qwen/Qwen3-8B](https://huggingface.co/Qwen/Qwen3-8B) | Apache-2.0 |
| Second judge, 8 Nov results | [bespokelabs/Bespoke-MiniCheck-7B](https://huggingface.co/bespokelabs/Bespoke-MiniCheck-7B) | CC BY-NC 4.0 |
| Second judge, 9 Nov until 12:18 UTC | [lytang/MiniCheck-RoBERTa-Large](https://huggingface.co/lytang/MiniCheck-RoBERTa-Large) | MIT (CC BY-NC training data) |
| Second judge from 9 Nov, 12:18 UTC, part 1 | [ibm-granite/granite-guardian-4.1-8b](https://huggingface.co/ibm-granite/granite-guardian-4.1-8b) | Apache-2.0 |
| Second judge from 9 Nov, 12:18 UTC, part 2 | [MoritzLaurer/deberta-v3-large-zeroshot-v2.0-c](https://huggingface.co/MoritzLaurer/deberta-v3-large-zeroshot-v2.0-c) | MIT |

Training and evaluation use the 4-bit MLX conversions of the seats from [mlx-community](https://huggingface.co/mlx-community). The council also runs Qwen3-8B to merge the groups' answers and [google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it) (Gemma Terms of Use) to carry each group's answers into the next round. Neither is trained.

## Grounding check

Code, not a model, decides whether a claim is grounded. Quote and passage are both normalised: curly quotes made straight, dashes unified, white space collapsed, case lowered and wrapping quote marks removed. An ellipsis stays literal, so one quote cannot bridge two spans. A claim is grounded when its quote is in the passage it cites. A quote found in a different shown passage is a citation fault. A quote found in no shown passage is a fabrication.

## Judging

A real quote can carry a claim that says more than the quote does. The general judge gives each quoted claim q, its probability that the claim is right, from the claim, the quote and 700 characters of the passage centred on the quote. Bespoke-MiniCheck-7B reads the claim against the whole passage that holds the quote and answers Yes or No. It is built on MiniCheck by Liyan Tang, Philippe Laban and Greg Durrett (EMNLP 2024, [arXiv:2404.10774](https://arxiv.org/abs/2404.10774), [code](https://github.com/Liyan06/MiniCheck)). When it answers No, q is capped at 0.2. A claim is accurate when it is grounded and its capped q is 0.5 or more.

We labelled claims OVERREACH or RIGHT before the test runs, each read in full with its quote and passage.

Hard set: 32 claims (23 OVERREACH, 9 RIGHT) gathered from earlier reads of live claims. 23 of them were chosen because the general judge had scored them 0.5 or higher, and 9 overreaching claims because it had scored them 0, so the set leans hard for that judge.

- General judge: caught 10 of 23 overreaching claims (q below 0.5), 0.43 [0.26, 0.63], and kept 7 of 9 right claims. AUC of q, right against overreach, 0.71 [0.50, 0.89].
- MiniCheck: No on 22 of 23 overreaching claims, 0.96 [0.79, 0.99]. Yes on 6 of 9 right claims, 0.67 [0.35, 0.88].
- A stricter prompt for the general judge left 6 overreaching claims unscored. On the 17 that both prompts scored, mean q rose from 0.44 to 0.51. It was not adopted.

Fresh set: 33 claims (21 OVERREACH, 12 RIGHT) drawn across the general judge's score bands, labelled with its scores hidden, and run once. Both judges read every claim.

- General judge alone: caught 9 of 21 overreaching claims, 0.43 [0.24, 0.63], and kept 9 of 12 right claims.
- MiniCheck: No on 21 of 21 overreaching claims, 1.00 [0.85, 1.00]. Yes on 11 of 12 right claims, 0.92 [0.65, 0.99].
- Capped q: caught 21 of 21 overreaching claims, 1.00 [0.85, 1.00]. The cap pushed 1 of 12 right claims below 0.5, 0.08 [0.01, 0.35]. On the hard set it pushed 2 of 9, 0.22 [0.06, 0.55].

Intervals on counts are Wilson 95 % intervals. The AUC interval is a bootstrap.

## Training

Each seat trains on its own answers to the council's job. A harvest builds fresh questions from the library, never a question the council itself was asked, and the seat (its base model, or its live adapter when it has one) answers each one 4 times at temperature 0.8. Claims are checked and judged as above. Fabrications are never kept. A citation fault is kept with its passage id corrected by code to the passage that holds the quote. Each kept claim's p is set to the general judge's q, so a seat also learns to state low confidence. For each question the sample with the most judged-right quoted content is kept. The seat's own council answers are added, cut the same way.

Rows are kept only where both judges agree: MiniCheck Yes with q of 0.5 or more, or MiniCheck No with q below 0.5. Rows where they disagree are left out, never relabelled. A seat trains once it has 100 rows.

LoRA with mlx-lm, from the base weights each turn: rank 8, scale 20, 16 layers, batch 2, learning rate 1e-5 (5e-6 on a retry after a failed run or a loss that is not a number), prompt masked, up to 4,096 tokens, iterations twice the training rows within 100 to 600, and 5 % of rows held back for validation. An adapter goes live only if its tensors hold no NaN or infinite values and the served model's output on one of its own held-back prompts differs from the base model's. With mlx-lm 0.31.3 in our setup, an adapter named only by `--adapter-path` at server start was not applied, so every request names its adapter.

A live seat keeps its grounded rate from its last 100 rows before the adapter. It is rolled back when its live grounded rate falls more than 0.15 below that rate, read once the live sample is large enough for the 95 % half-width of the difference to be 0.15 or less. It is also rolled back if disagreement across the council falls below half its level before the adapter.

## Evaluation

Each adapter is tested against its own base model on the council's real job: the same prompts at temperature 0, the same check and the same judges. Differences are adapter minus base, with 95 % intervals from a paired bootstrap over prompts (2,000 resamples). Above or Below means the whole interval sits on one side of zero. Cannot tell means it reaches zero.

The adapters below were each tested on 60 council prompts that were not in their training or validation rows. Most of these prompts shared a seed question with training rows (58 of 60 for Granite, 56 of 60 for Hermes), and some showed the same set of passages as a training row. Clean keeps the prompts whose set of passages appears in no training row. The overlap was found after the run, so Clean was defined after the data. The test prompts come from 4 seed questions for Granite and 5 for Hermes, and the bootstrap resamples prompts, not questions, so the intervals do not cover variation across questions.

For later turns, each seat's test set is built before training from seed questions held out by a fixed hash of seat and seed, and harvests skip those seeds. Keeping the seat's own live council answers on those seeds out of its training is a later change than the code copied here.

Both adapters below were trained before the second judge and the agree-only rule were added. Their rows were kept by the grounding check, with p set to the general judge's q.

## Results, 8 Nov

Accuracy and confident-wrong are read with the capped judge, run again on the stored answers. Grounded needs no judge. Confident-wrong is the share of claims with p of 0.8 or more that are not accurate.

Granite 3.3 8B Instruct, round 3 adapter. It was trained on 169 rows, with 8 held back.

| Reading | Prompts | n | Base | Adapter | Difference [95 %] | |
|---|---|---|---|---|---|---|
| Grounded | all | 60 | 0.433 | 0.841 | +0.408 [+0.269, +0.540] | Above |
| Grounded | clean | 43 | 0.408 | 0.848 | +0.440 [+0.285, +0.590] | Above |
| Accuracy | all | 60 | 0.030 | 0.206 | +0.176 [+0.075, +0.283] | Above |
| Accuracy | clean | 43 | 0.041 | 0.109 | +0.068 [-0.018, +0.167] | Cannot tell |
| Confident-wrong | all | 60 | 0.881 | 0.365 | -0.516 [-0.641, -0.385] | Below |
| Confident-wrong | clean | 43 | 0.898 | 0.391 | -0.507 [-0.651, -0.369] | Below |

Hermes 3 Llama 3.1 8B adapter. It was trained on 119 rows, with 6 held back.

| Reading | Prompts | n | Base | Adapter | Difference [95 %] | |
|---|---|---|---|---|---|---|
| Grounded | all | 60 | 0.373 | 0.593 | +0.220 [+0.043, +0.383] | Above |
| Grounded | clean | 41 | 0.293 | 0.500 | +0.207 [0.000, +0.415] | Cannot tell |
| Accuracy | all | 60 | 0.153 | 0.136 | -0.017 [-0.123, +0.098] | Cannot tell |
| Accuracy | clean | 41 | 0.171 | 0.175 | +0.004 [-0.122, +0.131] | Cannot tell |
| Confident-wrong | all | 60 | 0.831 | 0.034 | -0.797 [-0.900, -0.678] | Below |
| Confident-wrong | clean | 41 | 0.829 | 0.025 | -0.804 [-0.926, -0.659] | Below |

Both adapters quote the passage they cite more often on all prompts. On clean prompts Granite's grounding gain clears zero and Hermes's reaches it. Granite is more accurate on all prompts, but its accuracy gain on clean prompts cannot be told from zero. Hermes is not shown to be more accurate. Its accuracy is 0.153 and 0.136 on all prompts while its confident-wrong share falls from 0.831 to 0.034, so that fall comes from lower stated p, not from more right claims.

Prompts answered with at least one claim: Granite 0.900 to 0.983, +0.083 [0.000, +0.183], cannot tell. Hermes 0.983 to 0.983. Brier score from the first real-job pass, where the general judge alone saw the first 700 characters of the cited passage: Granite 0.764 to 0.304, -0.460 [-0.605, -0.297], Below. Hermes 0.725 to 0.068, -0.657 [-0.785, -0.516], Below.

## Method changes on 9 Nov

Second judge. At 12:18 UTC the second judge moved to a licence-clean pair, [ibm-granite/granite-guardian-4.1-8b](https://huggingface.co/ibm-granite/granite-guardian-4.1-8b) (Apache-2.0) and [MoritzLaurer/deberta-v3-large-zeroshot-v2.0-c](https://huggingface.co/MoritzLaurer/deberta-v3-large-zeroshot-v2.0-c) (MIT). Each reads the claim against the passage that holds its quote, and the pair says Yes only when both do (granite-guardian at 0.2, the zero-shot classifier at 0.5, both fixed before any run with the pair). The AND rule was chosen after seeing granite-guardian alone pass wrong claims. On 79 hand-labelled claims (34 right, 45 wrong) the pair kept 27 of 34 right claims, 0.79 [0.63, 0.90], and caught 43 of 45 wrong ones, 0.96 [0.85, 0.99]. Before the switch the second judge was [lytang/MiniCheck-RoBERTa-Large](https://huggingface.co/lytang/MiniCheck-RoBERTa-Large) (MIT weights, trained on CC BY-NC data) at 0.2, with Bespoke-MiniCheck-7B as fallback. After the switch there is no fallback to a MiniCheck model. The table below names the second judge that read each paired evaluation.

SFT then DPO. Each turn now trains the LoRA as before, then runs a DPO step from that SFT adapter on pairs of the seat's own answers to one prompt, the preferred answer with judged-right claims and the other with faults such as fabricated quotes or confident-wrong claims. DPO uses beta 0.1, learning rate 2e-6 and an added likelihood term on the preferred answer, and stops on held-out checks. From about 18:40 UTC SFT runs 2 epochs instead of 4. None of the runs below used that yet.

Per-prompt harm rule. An adapter is rolled back when its paired net per prompt (right claims minus confident-wrong claims, per prompt) is clearly lower, when confident-wrong claims per prompt rise with no clear gain in right claims per prompt, or when the answered rate or right claims per prompt clearly fall. It is released when the intervals rule out a loss larger than 0.05 on grounded rate, accuracy and answered rate and a rise larger than 0.05 in confident-wrong share. An adapter that is neither rolled back nor released keeps serving and is labelled "serving, not released". It does not retrain until the seat has enough live claims.

Champion and challenger. A released adapter is replaced only by a challenger that is released too. Otherwise the champion is restored and the challenger is kept on disk, not served.

Confidence from the judge. The p a seat states carried little information. On 109 hand-labelled claims (55 right, 54 not), seat p ranked right claims above wrong ones with AUROC 0.62 [0.53, 0.71]. The second judge's AND score, the lower of its two probabilities, gave 0.95 [0.90, 0.98]. On the 33 claims labelled after the judge was chosen, seat p gave 0.47 [0.33, 0.63] and the AND score 0.95 [0.86, 1.00]. Intervals are bootstrap intervals over claims. From about 19:30 UTC the council's p is filled from the judge, p = sigmoid(1.017 + 0.531 logit(s)) with s the AND score. Both constants were fitted on the labelled claims after the data and are refit each referee round. Cross-validated Brier score was 0.107, against 0.250 for a constant and 0.252 for seat p. Seats are no longer asked for p and training targets no longer carry it. p and the training filter now come from the same judge, so the hand-labelled referee is the only independent check of both. The paired evaluations below still use the seat's own p for confident-wrong, because their stored test prompts ask for it.

New seat. At 23:20 UTC [baidu/ERNIE-4.5-21B-A3B-PT](https://huggingface.co/baidu/ERNIE-4.5-21B-A3B-PT) (Apache-2.0, a mixture of experts with about 3B active parameters) took the seat of Phi-4-mini-instruct. It serves its base weights through Ollama. It has no adapter and no paired result yet.

Fixes after a red-team read of the promotion path. Harvest rows on held-out seeds were reaching training: 17 rows on 4 of granite R4's 60 test seeds, and 16 rows on 7 of the hermes test seeds in rounds 2 to 4. Training now drops them. Llama, mistral and phi had none. Promotion and the paired evaluation now fail closed when a check cannot be read.

## Results, 9 Nov

Read these with three caveats from the red-team read.

- Within a seat, the same 60 held-out prompts were reused across rounds while the release rules changed. The adapters that were kept were chosen on that set, so their results may read high.
- Held-out seed questions do not hold out passages. The Clean subset (prompts whose exact passage set is in no training row) removed no prompt in any run below, so only all 60 prompts are reported. The seats had seen most of the passages they were tested on, with other questions around them.
- Granite and hermes test prompts come from 60 seed questions. Llama's come from 21, mistral's from 18 and phi's from 17. The bootstrap resamples prompts, not questions.

Each adapter against its own base on 60 held-out council prompts. Differences are adapter minus base with paired bootstrap 95 % intervals (2,000 resamples). ABOVE or BELOW means the whole interval sits on one side of zero. CANNOT_TELL means it reaches zero. For confident-wrong and fabricated, BELOW is the better direction. Status is as of 23:23 UTC on 9 Nov. The second judge column names the judge that read the run.

| Run | Method | Rows (SFT, DPO pairs) | Second judge | Status |
|---|---|---|---|---|
| granite R4 | SFT | 201 | MiniCheck-RoBERTa | serving, not released |
| llama R4 | SFT | 209 | licence-clean pair | serving, not released |
| llama R5 | SFT+DPO | 245, 39 | licence-clean pair | challenger, not serving |
| hermes R2 | SFT | 130 | MiniCheck-RoBERTa | released at 03:17 UTC, later replaced by R4 |
| hermes R3 | SFT | 250 | licence-clean pair | challenger, not serving |
| hermes R4 | SFT+DPO | 290, 35 | licence-clean pair | released at 23:23 UTC |
| mistral | SFT | 142 | MiniCheck-RoBERTa | released at 03:15 UTC, rolled back to base about 17:50 UTC (live seat wrote no claims) |
| phi | SFT | 131 | MiniCheck-RoBERTa | not released, seat given to ERNIE-4.5-21B-A3B at 23:20 UTC |

| Run | Accuracy | Confident-wrong share | Grounded | Answered |
|---|---|---|---|---|
| granite R4 | 0.336 to 0.598, +0.262 [+0.151, +0.387] ABOVE | 0.636 to 0.369, -0.267 [-0.389, -0.160] BELOW | 0.527 to 0.754, +0.227 [+0.121, +0.348] ABOVE | 0.983 to 0.983, 0.000 [-0.050, +0.050] CANNOT_TELL |
| llama R4 | 0.212 to 0.521, +0.309 [+0.155, +0.468] ABOVE | 0.242 to 0.465, +0.223 [+0.039, +0.406] ABOVE | 0.545 to 0.803, +0.258 [+0.067, +0.447] ABOVE | 0.550 to 0.983, +0.433 [+0.317, +0.550] ABOVE |
| llama R5 | 0.212 to 0.478, +0.266 [+0.089, +0.439] ABOVE | 0.242 to 0.507, +0.265 [+0.086, +0.455] ABOVE | 0.545 to 0.851, +0.306 [+0.133, +0.481] ABOVE | 0.550 to 1.000, +0.450 [+0.333, +0.567] ABOVE |
| hermes R2 | 0.338 to 0.623, +0.285 [+0.146, +0.435] ABOVE | 0.634 to 0.377, -0.257 [-0.412, -0.111] BELOW | 0.394 to 0.754, +0.360 [+0.226, +0.503] ABOVE | 0.983 to 1.000, +0.017 [0.000, +0.050] CANNOT_TELL |
| hermes R3 | 0.338 to 0.567, +0.229 [+0.079, +0.386] ABOVE | 0.634 to 0.433, -0.201 [-0.365, -0.041] BELOW | 0.394 to 0.716, +0.322 [+0.175, +0.471] ABOVE | 0.983 to 0.950, -0.033 [-0.100, +0.033] CANNOT_TELL |
| hermes R4 | 0.338 to 0.633, +0.295 [+0.159, +0.428] ABOVE | 0.634 to 0.367, -0.267 [-0.408, -0.117] BELOW | 0.394 to 0.700, +0.306 [+0.154, +0.442] ABOVE | 0.983 to 1.000, +0.017 [0.000, +0.050] CANNOT_TELL |
| mistral | 0.364 to 0.566, +0.202 [+0.071, +0.329] ABOVE | 0.628 to 0.434, -0.194 [-0.316, -0.066] BELOW | 0.504 to 0.607, +0.103 [-0.023, +0.220] CANNOT_TELL | 0.900 to 0.867, -0.033 [-0.150, +0.100] CANNOT_TELL |
| phi | 0.102 to 0.228, +0.126 [+0.021, +0.229] ABOVE | 0.678 to 0.772, +0.094 [-0.069, +0.243] CANNOT_TELL | 0.322 to 0.491, +0.169 [-0.003, +0.343] CANNOT_TELL | 0.867 to 0.950, +0.083 [0.000, +0.183] CANNOT_TELL |

| Run | Right per prompt | Confident-wrong per prompt | Net per prompt | Fabricated |
|---|---|---|---|---|
| granite R4 | 0.617 to 1.217, +0.600 [+0.283, +0.950] ABOVE | not computed | not computed | 0.427 to 0.205, -0.222 [-0.334, -0.127] BELOW |
| llama R4 | 0.117 to 0.617, +0.500 [+0.317, +0.717] ABOVE | 0.133 to 0.550, +0.417 [+0.267, +0.567] ABOVE | -0.017 to 0.067, +0.084 [-0.183, +0.383] CANNOT_TELL | 0.364 to 0.183, -0.181 [-0.370, 0.000] CANNOT_TELL |
| llama R5 | 0.117 to 0.533, +0.416 [+0.233, +0.600] ABOVE | 0.133 to 0.567, +0.434 [+0.283, +0.583] ABOVE | -0.017 to -0.033, -0.016 [-0.300, +0.283] CANNOT_TELL | 0.364 to 0.149, -0.215 [-0.391, -0.041] BELOW |
| hermes R2 | 0.400 to 0.633, +0.233 [+0.067, +0.400] ABOVE | not computed | not computed | 0.380 to 0.213, -0.167 [-0.286, -0.050] BELOW |
| hermes R3 | 0.400 to 0.633, +0.233 [+0.033, +0.450] ABOVE | 0.750 to 0.483, -0.267 [-0.500, -0.050] BELOW | -0.350 to 0.150, +0.500 [+0.150, +0.883] ABOVE | 0.380 to 0.239, -0.141 [-0.259, -0.017] BELOW |
| hermes R4 | 0.400 to 0.633, +0.233 [+0.067, +0.400] ABOVE | 0.750 to 0.367, -0.383 [-0.567, -0.200] BELOW | -0.350 to 0.267, +0.617 [+0.300, +0.917] ABOVE | 0.380 to 0.283, -0.097 [-0.220, +0.033] CANNOT_TELL |
| mistral | 0.733 to 1.150, +0.417 [+0.083, +0.767] ABOVE | not computed | not computed | 0.421 to 0.385, -0.036 [-0.166, +0.101] CANNOT_TELL |
| phi | 0.100 to 0.217, +0.117 [+0.017, +0.233] ABOVE | not computed | not computed | 0.390 to 0.298, -0.092 [-0.224, +0.038] CANNOT_TELL |

Granite R4 is more accurate, 0.336 to 0.598, and its confident-wrong share falls. Its answered rate is the same in both arms and the lower bound of that difference sits exactly at -0.050, while the release rule needs it above -0.05. It serves, not released.

Llama R4 answers far more prompts, 0.550 to 0.983, and writes more right claims per prompt. It also writes more confident-wrong claims per prompt, 0.133 to 0.550, and its net per prompt is CANNOT_TELL. It was kept under the per-prompt rule, which was set after round 3 and before this result. Under the earlier per-claim rule it would have been rolled back. It serves, not released.

Llama R5 was the first SFT then DPO round. On the same 60 prompts its accuracy was 0.478 against R4's 0.521, and its net per prompt -0.033 against R4's 0.067. It was not better than R4, so R4 was restored and R5 kept as a challenger.

Hermes R3 was not released (answered lower bound -0.100), so the released R2 stayed in as champion. Hermes R4, SFT then DPO, was released at 23:23 UTC: accuracy 0.338 to 0.633 and net per prompt -0.350 to 0.267 [+0.300, +0.917]. It is the first DPO round released. Hermes R2 and R3 were read with different second judges, so comparing them does not measure the adapters alone.

The mistral adapter was released, but the live seat wrote no parsable claims in council turns from 04:34 UTC. It was rolled back to base at about 17:50 UTC and retired. The fault is in the live serving path, not shown in the paired evaluation, and is still open. A rollback on silence now fires after 12 council turns with no claims.

Phi is more accurate, but its confident-wrong share cannot be told from zero and it was not released. Its seat went to ERNIE and its adapter was taken down.

Two earlier llama rounds on the same prompts were rolled back. Round 1 stopped answering after training on rows that were 41 % CANNOT_TELL, answered 0.550 to 0.000 [-0.683, -0.433]. Training now caps CANNOT_TELL rows at a quarter of the rows with right claims. Round 3 raised the confident-wrong share, 0.242 to 0.431 [+0.002, +0.373]. Round 2 was refused at promotion and never served.

## Paired referee, 9 Nov

A hand-labelled check of the same paired answers, independent of both judges. One labeller read 166 claims with their quotes and the passage around each quote, blind to seat, round, arm, p and judge scores. Labels were frozen and hashed before unblinding: RIGHT 122, OVER 34, FALSE 10, SKIP 0, with 37 marked borderline. Prompts touching excluded private material were dropped whole by a mechanical filter, unread, so each seat keeps 12 to 24 prompts. Claims whose quote is in no shown passage count as not right in both arms. Intervals come from a paired bootstrap over prompts (10,000 resamples). The outcome rule was set before the numbers were read, on the difference in right claims per prompt: ABOVE or BELOW when the whole interval is on one side of zero, CONSISTENT when it holds zero and stays within 0.5 of it, CANNOT_TELL when it holds zero and reaches past 0.5.

| Run | Prompts | Right per prompt | Right share | Confident-wrong per prompt | Outcome |
|---|---|---|---|---|---|
| granite R4 | 12 | 0.83 to 1.50, +0.67 [+0.17, +1.17] | 0.59 to 0.86, +0.27 [0.00, +0.54] | 0.50 to 0.17, -0.33 [-0.83, +0.17] | ABOVE |
| llama R4 | 24 | 0.04 to 0.96, +0.92 [+0.58, +1.33] | 0.11 to 0.77, +0.66 [+0.41, +0.87] | 0.08 to 0.29, +0.21 [0.00, +0.42] | ABOVE |
| hermes R2 | 19 | 0.68 to 0.79, +0.11 [-0.11, +0.32] | 0.62 to 0.79, +0.17 [-0.05, +0.37] | 0.42 to 0.21, -0.21 [-0.53, +0.05] | CONSISTENT |
| hermes R3 | 19 | 0.68 to 0.95, +0.26 [+0.05, +0.53] | 0.62 to 0.78, +0.16 [-0.02, +0.34] | 0.42 to 0.26, -0.16 [-0.42, +0.05] | ABOVE |
| mistral | 15 | 0.53 to 1.13, +0.60 [+0.07, +1.27] | 0.29 to 0.74, +0.45 [+0.16, +0.77] | 1.33 to 0.40, -0.93 [-1.60, -0.33] | ABOVE |
| phi | 17 | 0.29 to 0.35, +0.06 [-0.12, +0.24] | 0.31 to 0.38, +0.06 [-0.11, +0.27] | 0.47 to 0.59, +0.12 [-0.18, +0.41] | CONSISTENT |
| phi, calibration-only adapter (never served) | 17 | 0.29 to 0.35, +0.06 [-0.24, +0.35] | 0.31 to 0.43, +0.12 [-0.18, +0.42] | 0.47 to 0.00, -0.47 [-0.71, -0.24] | CONSISTENT |

Granite R4, llama R4 and mistral write more right claims than their bases on the same prompts. Llama R4's confident-wrong per prompt also rises, and it states p = 1.0 on every claim. Hermes R2 is CONSISTENT. Hermes R3 is ABOVE with a lower bound of +0.05, and it falls to CANNOT_TELL with borderline labels counted as not right. Seven comparisons were made with no multiplicity correction, and each seat has 12 to 24 prompts. The judges' capped readings and the referee agree on the sign for every run. Hermes R4 and llama R5 were not in this round.

## Tried

A first Granite adapter was trained on planted claims, which are passages paired with claims altered by templates (negation, paraphrase, swapped agents or quantities, reversal) with known answers, together with the seat's own logged answers. On 30 council prompts it had not been trained on, its grounded rate fell from 0.333 to 0.133, -0.200 [-0.405, -0.010], Below. It was never routed to the council, and training moved to the council's own job. This reading used an earlier passage splitter that let the last shown passage run on to the end of the prompt, for both arms.

## Not published

- Adapter weights. They were trained on the private library and can carry its text.
- Training rows, prompts, passages, claims and judge reasons.

## Code

`code/` is copied from [github.com/Heuremen-LLC/sage-v](https://github.com/Heuremen-LLC/sage-v) at commit 7c4517e: harvest.py, train_scheduler.py, promote.py, realjob_eval.py, prepare_paired.py, rejudge_paired.py, judge_audit.py, need_n.py, system_eval.py, scoreboard.py, spotcheck.py, calib_train.py, seats.json and local.example.json. The council module, the training script and the judge test scripts are not copied here. The scripts import the council module, so they do not run from this copy alone. In this copy, home paths and internal names in comments were replaced with neutral ones. The code is otherwise unchanged. It predates the 9 Nov changes. The current scripts are in the repository.

## Terms

The code in `code/` is Apache-2.0 (`code/LICENSE`). The text of this page and the numbers in `results.json` are free to download, read and cite with attribution (Heuremen LLC, with a link to indahl.ai). All rights reserved. Text and data mining, and use of this data to train, fine-tune or build AI models, are not permitted. Policy: https://indahl.ai/terms#ai-training

Page on indahl.ai: https://indahl.ai/iris/lab#sage-v . Code: https://github.com/Heuremen-LLC/sage-v .

Published by Heuremen LLC, https://indahl.ai . We found it.
