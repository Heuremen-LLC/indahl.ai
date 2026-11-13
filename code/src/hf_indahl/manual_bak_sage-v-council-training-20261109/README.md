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

Sage V is a council of small open-weight models that answer questions from a private text library. Every claim a seat makes must carry an exact quote from a passage it was shown and a stated probability that the claim is right. We train LoRA adapters for the seats on this job and test each adapter against its own base model on the same job. This page gives the method and the numbers. `results.json` holds every number below, and `code/` holds a copy of the harvest, serving, evaluation and scheduling scripts.

No weights are published. The adapters were trained on the private library and can carry its text, so the weights, the training rows, the prompts and the library stay private.

## The council

Seats are instruction models run locally through [Ollama](https://github.com/ollama/ollama), and through [mlx-lm](https://github.com/ml-explore/mlx-lm) ([PyPI](https://pypi.org/project/mlx-lm/)) once a seat has an adapter. Each question goes to groups of three seats. A seat answers alone, in JSON, with up to four claims. Each claim has one sentence, one quote, the id of the passage it quotes, and p, the seat's probability that the claim is right. CANNOT_TELL is a full answer when the passages do not settle the question.

| Role | Model | License |
|---|---|---|
| Seat | [ibm-granite/granite-3.3-8b-instruct](https://huggingface.co/ibm-granite/granite-3.3-8b-instruct) | Apache-2.0 |
| Seat | [NousResearch/Hermes-3-Llama-3.1-8B](https://huggingface.co/NousResearch/Hermes-3-Llama-3.1-8B) | Llama 3.1 Community License |
| Seat | [mistralai/Mistral-7B-Instruct-v0.3](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3) | Apache-2.0 |
| Seat | [microsoft/Phi-4-mini-instruct](https://huggingface.co/microsoft/Phi-4-mini-instruct) | MIT |
| Seat | [meta-llama/Llama-3.2-3B-Instruct](https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct) | Llama 3.2 Community License |
| General judge | [Qwen/Qwen3-8B](https://huggingface.co/Qwen/Qwen3-8B) | Apache-2.0 |
| Entailment check | [bespokelabs/Bespoke-MiniCheck-7B](https://huggingface.co/bespokelabs/Bespoke-MiniCheck-7B) | CC BY-NC 4.0 |

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

## Results

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

## Tried

A first Granite adapter was trained on planted claims, which are passages paired with claims altered by templates (negation, paraphrase, swapped agents or quantities, reversal) with known answers, together with the seat's own logged answers. On 30 council prompts it had not been trained on, its grounded rate fell from 0.333 to 0.133, -0.200 [-0.405, -0.010], Below. It was never routed to the council, and training moved to the council's own job. This reading used an earlier passage splitter that let the last shown passage run on to the end of the prompt, for both arms.

## Not published

- Adapter weights. They were trained on the private library and can carry its text.
- Training rows, prompts, passages, claims and judge reasons.

## Code

`code/` is copied from [github.com/Heuremen-LLC/sage-v](https://github.com/Heuremen-LLC/sage-v) at commit 7c4517e: harvest.py, train_scheduler.py, promote.py, realjob_eval.py, prepare_paired.py, rejudge_paired.py, judge_audit.py, need_n.py, system_eval.py, scoreboard.py, spotcheck.py, calib_train.py, seats.json and local.example.json. The council module, the training script and the judge test scripts are not copied here. The scripts import the council module, so they do not run from this copy alone. In this copy, home paths and internal names in comments were replaced with neutral ones. The code is otherwise unchanged.

## Terms

The code in `code/` is Apache-2.0 (`code/LICENSE`). The text of this page and the numbers in `results.json` are free to download, read and cite with attribution (Heuremen LLC, with a link to indahl.ai). All rights reserved. Text and data mining, and use of this data to train, fine-tune or build AI models, are not permitted. Policy: https://indahl.ai/terms#ai-training

Page on indahl.ai: https://indahl.ai/iris/lab#sage-v . Code: https://github.com/Heuremen-LLC/sage-v .

Published by Heuremen LLC, https://indahl.ai . We found it.
