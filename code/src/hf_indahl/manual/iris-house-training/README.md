---
license: other
license_name: heuremen-attribution-no-ai-training
license_link: https://indahl.ai/terms#ai-training
pretty_name: "IRIS: a small model trained on the house's own answers"
tags:
- fine-tuning
- lora
- reproducibility
- pre-registration
---

# A small model trained on the house's own answers

The released rows behind the IRIS LAB section of the same name (https://indahl.ai/iris/lab). Our open-model triangles answered FaultsBench items, each answer scored by the item's own code. We trained Qwen3-1.7B (Apache-2.0) with LoRA on the answers the code scored correct (P1 and P4 families), with seed 61 in round one and seeds 62, 63 and 64 in round two (seed 64 failed to train twice and was not evaluated), and evaluated on two held-out rounds: three samples per item, temperature 0.7, up to 1,200 tokens, thinking off.

## Files

- `eval/round1_seed61.jsonl`, `eval/round2_seed62.jsonl`, `eval/round2_seed63.jsonl`: every evaluation row, untouched model (`arm: base`, re-run inside every evaluation) and trained model (`arm: trained`), with the item's own score (`cls`: OK, FAULT, MISS or UNREAD) and the full reply text.
- `eval/highest_lowest_middle_all_arms.jsonl`: the list questions (highest, lowest and middle value) for the untouched model and seeds 61, 62, 63.
- `eval/round1_seed61_rerun_check.jsonl`, `eval/round2_seed62_rerun_check.jsonl` and `eval/round2_seed63_rerun_check.jsonl`: seeded reruns of three evaluations (see CHANGES_AFTER_READING.md, item 6).
- `training_set_round1.jsonl`: the 1,880 training rows (Qwen3-1.7B's training data only; nothing here is a claim about any other model). `source_model` is the model whose answer it is, taken from the earliest answer with that exact text; `source_models_all` lists every model that gave that exact text (131 of 1,880 rows match more than one).
- `configs/`: the LoRA configurations (16 layers, rank 8, learning rate 1e-5, batch 4, 470 iterations, prompt masked).
- `round2_READ.txt`, `X2_PER_ARM_BOTH_RULES.txt`: the readings as the pre-set rules computed them, and the post hoc classification of unclassified list answers under both matching rules.
- `stamps/`: SHA256SUMS files for the plan and each change to it, each with its OpenTimestamps proof (`.ots`) anchoring it in a Bitcoin block. The plan texts they hash carry internal working notes and are held back for now; the hashes are public so the texts can be checked against them when released. A proof shows a file existed by its block's time; it does not show that anything ran after it. The pairing of block times with the jobs they precede:

| What | Block (time, UTC, 7 Nov) | First job it should precede | Order |
|---|---|---|---|
| Round one plan and changes (A9b, A10-A12, A13) | 974874 (01:30), 974883 (03:26), 974888 (04:06) | training data built 06:01, training done 06:05 | before |
| Round two plan and changes (A14-A18) and list-question items (P4M) | 974942 (14:40) | first training log created 13:48 | after, as the plan allowed (training produces no reading) |
| same | 974942 (14:40) | first round-two evaluation 18:07 | before |
| Retrain rule after training failures (A19) | 974942 (14:40) | seed 63 retrain started 14:36 | after by about 4 minutes: self-witnessed |
| Round-two reading script and its output (R2READ) | 974981 (20:27) | written after the evaluation rows existed; stamped after its numbers were seen | fixes the reading as reported; not a plan, not before the numbers |
| Secondary read rule for list answers (X2) | 974981 (20:27) | that read, run after 22:00 | before |

- `CHANGES_AFTER_READING.md`: every change and every step that was not strictly fixed in advance, in plain words. It was written after the results and is not covered by any stamp.

## Source models and their terms

Training rows come from answers by these open models (rows per model are in `source_model` and `source_models_all`): Apache-2.0: ministral-3 (8b, 3b), granite4.1:3b, granite3.3:2b, olmo2:7b, mistral:7b, smollm2:1.7b, qwen3:8b, qwen2.5:1.5b. MIT: phi4-mini. Llama 3.1 and 3.2 Community License (llama3.1:8b, llama3.2:3b): Built with Llama; a model trained on these outputs and distributed must carry a name beginning "Llama" (clause 1.b.i). Gemma Terms of Use (gemma3:1b): Google claims no rights in outputs (3.3); a model trained on Gemma outputs may be a Model Derivative under its terms (1.1(e)). Falcon 3 TII Falcon License (falcon3:3b): outputs may not be used against its Acceptable Use Policy. Our reading of these clauses, not legal advice. Releasing these outputs as data is separate from any later release of the trained adapters, which are not released here; an adapter release would need its own check of the Llama naming clause and the Gemma terms.

## Terms

Free to download, read and cite with attribution (Heuremen LLC, with a link to indahl.ai). All rights reserved. Text and data mining, and use of this data to train, fine-tune or build AI models, are not permitted without written permission, except where a source model's own licence grants more for its outputs.
