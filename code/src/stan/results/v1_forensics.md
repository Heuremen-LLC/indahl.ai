# STAN v1 forensics (read-only)

Written 12 November 2026. Nothing was trained and no repo file other than this one and v1_forensics.json was written. Every number below was read or recomputed from the file named beside it. Machine-readable copy: results/v1_forensics.json. The loss and mask runs used CPU only (mlx on the CPU device, venv python, mlx_lm 0.31.3). The system python3.12 has no mlx_lm.

## 1. The 99 METHOD_UNSTATED training rows

Source: data/silver_v1/silver_all.jsonl, rows with split=train and label CANNOT_TELL / METHOD_UNSTATED. Each row keeps the three teachers' final labels, and each label carries flag (ok or ungrounded) and, if converted, was (the status the teacher actually wrote). data/silver_v1/train.jsonl itself has no flag, so the join is by split=train (271 rows, same class counts as train.jsonl: 99 METHOD_UNSTATED, 15 NOT_RELEASED, 94 PRESENT, 42 ABSENT, 21 NOT_APPLICABLE).

The suspicion is mostly right, but it is not all-or-nothing. A silver label is "unanimous CT" when the three teachers' final labels are all CANNOT_TELL / METHOD_UNSTATED. Each of the three can have said CT itself (flag ok) or been converted by the grounding rule (flag ungrounded).

- All three teachers converted: 40 rows
- Two converted, one said CT itself: 31 rows
- One converted, two said CT themselves: 18 rows
- All three said CT themselves (true abstention): 10 rows
- So 89 of 99 rows contain at least one conversion. Only 10 are pure teacher abstention. 28 have a native-CT majority (10 plus 18).

Across the 297 teacher labels in these rows, 200 were converted (104 had been PRESENT, 96 ABSENT) and 97 were native CT. Of the 40 all-converted rows, 26 had teachers who disagreed about the underlying status before conversion (ABSENT/PRESENT/PRESENT 19, ABSENT/ABSENT/PRESENT 7), so the conversion manufactured the agreement. The other 14 agreed (ABSENT x3 9, PRESENT x3 5).

Per code (all3 converted / two converted / one converted / all3 native):
F1 5 / 10 / 0 / 0. F2 8 / 0 / 2 / 0. F3 2 / 1 / 0 / 2. F4 10 / 15 / 9 / 4. F5 1 / 1 / 3 / 3. F6 14 / 3 / 3 / 0. F7 0 / 1 / 1 / 1.

The 15 CT / NOT_RELEASED training rows have no converted labels at all.

Code path that converts:
- scripts/common.py:42-43, norm_label. If a teacher says PRESENT or ABSENT and the quote is empty or not a whitespace-normalised, case-sensitive substring of the abstract, the label becomes CANNOT_TELL / METHOD_UNSTATED, flag ungrounded, was kept.
- It runs on every teacher call, at scripts/run_teachers.py:26 (round 1) and scripts/crosstalk.py:32 (round 2). The same function also scores base and STAN outputs (scripts/infer_mlx.py:22).
- scripts/silver.py:15-27 calls a pair unanimous when (status, reason) keys match across teachers, copies the first teacher's label (line 26), and silver.py:50-52 writes only status, reason, quote into the training row. The flag and was fields are lost there.

How lossy the grounding check is (teachers/*_round1.jsonl, raw text re-parsed, pool set, 2316 ungrounded PRESENT/ABSENT labels from the three teachers): 1180 had an empty quote, 430 match the abstract once case and punctuation are normalised, 103 have 80 percent or more of the quote as one contiguous match, 603 are not found. Round-1 ungrounded rates: llama 578 of 2800 calls, mistral 480 of 2800, gemma 1258 of 2779.

## 2. The class cap

Code: scripts/silver.py:36-47. Per code, rows are grouped by key(label) = (status, reason) (common.py:44). The largest group is capped to max(number of rows in all other groups, 1) rows, chosen by random.Random(1). All other groups are kept in full. Line 41 (lim=len(rs)//2) is assigned and never used. The 7-paper valid split is cut after the cap (silver.py:48, random.Random(2), max(4, n//20) papers).

Because the key includes the reason, CANNOT_TELL / METHOD_UNSTATED and CANNOT_TELL / NOT_RELEASED are different classes for the cap, while the status-level CT share is what the model sees. The cap also bounds only one group per code.

Status counts per code, before cap (silver_all.jsonl, 345 rows), then after cap (train plus valid, 286 rows), then train only (271 rows):

| code | before | after cap | train |
|---|---|---|---|
| F1 | CT 18, P 23 | CT 18, P 18 | CT 15, P 17 |
| F2 | P 27, A 12, CT 12 | P 24, A 12, CT 12 | P 23, A 12, CT 10 |
| F3 | CT 29, A 3, NA 2 | CT 5, A 3, NA 2 | CT 5, A 3, NA 2 |
| F4 | P 34, CT 43, A 1 | P 34, CT 43, A 1 | P 32, CT 42, A 1 |
| F5 | P 1, CT 19, A 11, NA 6 | same | P 1, CT 18, A 11, NA 6 |
| F6 | CT 22, P 17, A 14, NA 2 | same | CT 20, P 16, A 14, NA 2 |
| F7 | NA 38, CT 4, A 2, P 5 | NA 11, CT 4, A 2, P 5 | NA 11, CT 4, A 1, P 5 |

59 rows were cut (data/silver_v1/unused_cap.jsonl): F1 PRESENT 5, F2 PRESENT 3, F3 CT 24, F7 NA 27. Codes F4, F5, F6 were not capped at all.

Largest status share in train: F4 0.560 (CT), F1 0.531 (P), F7 0.524 (NA), F2 0.511 (P), F3 0.500, F5 0.500, F6 0.385. That reproduces the F4, F1, F7, F2 overshoot. Why: F4 and F5 were never capped, because their largest key (CT/METHOD_UNSTATED, 39 of 78 for F4) is not above the sum of the rest, while CT as a status (including NOT_RELEASED) is 55.1 percent of F4. F1, F2, F7 land at exactly 50.0 percent after the cap and rise above it when the 7 valid papers are removed from train. CT/METHOD_UNSTATED before cap per code: F1 18, F2 12, F3 29, F4 39, F5 8, F6 22, F7 3.

Contradiction to flag: results/silver_classes_v1.json "silver_all" says CANNOT_TELL 5, PRESENT 213, ABSENT 104, NA 23. The file data/silver_v1/silver_all.jsonl has CT 147 (131 METHOD_UNSTATED, 16 NOT_RELEASED), PRESENT 107, ABSENT 43, NA 48. That count seems to use the pre-conversion status (the was field), which would hide exactly the conversions. Its note that the collapse was "not from the grounding check" is not supported by section 1.

## 3. Status-token loss, base against STAN

Computable, yes. Needed artifacts are on disk: the base model in the HF cache, the adapter runs/stan_v1/ckpt250 (the checkpoint named in runs/stan_v1/CHECKPOINT.txt), and data/silver_v1/valid.jsonl. I teacher-forced the exact trained token sequence on CPU (about 1 to 2 minutes per model per 15 rows) and took the negative log likelihood of the tokens that spell the status value inside the JSON. "First token" is the token that decides the class (for CANNOT_TELL it is "C").

Valid, 15 rows, 7 papers (data/silver_v1/valid.jsonl):
- Base: mean status first-token NLL 10.68, whole-answer loss 2.80.
- STAN ckpt250: mean status first-token NLL 0.91, whole-answer loss 0.1015. The log's own iter-250 valid loss is 0.092, so the recompute agrees to bf16/CPU noise.

Train, 40 rows (the selfcheck order, seed 7):
- Base: status first-token NLL 4.74, whole-answer loss 2.13.
- STAN: status first-token NLL 1.39, whole-answer loss 0.069.

What matters is STAN's first-token distribution by true class. It is almost the same for every class:
- Train 40: P(CT) is 0.636 on true CT rows, 0.589 on PRESENT, 0.589 on ABSENT, 0.564 on NOT_APPLICABLE. The probability of the right class is 0.262 on PRESENT rows, 0.121 on ABSENT, 0.057 on NA.
- Valid 15: P(CT) is 0.636 on CT rows, 0.612 on PRESENT, 0.580 on ABSENT.

So the status loss was reduced by learning a marginal prior of about 0.6 for CT, which greedy decoding turns into CT every time. It is not a decision that depends on the abstract. The base model puts 0.000 to 0.006 on CT in every row, so the base's 12.3 percent decided share against its CT majority is the grounding rule at work, not base abstention (see section 7).

Valid is tiny (15 rows, 7 papers, 9 CT rows) and was the selector for ckpt250.

## 4. Mask dump

Config: runs/stan_v1/lora.yaml has mask_prompt: true, batch 2, iters 271, lr 1e-4, rank 8, scale 20, 16 layers. Installed: mlx_lm 0.31.3 in /Users/heuremen/bones-forge/venv (python3.12 -c "import mlx_lm" fails: no module).

Behaviour in that version (mlx_lm/tuner/datasets.py ChatDataset.process and tuner/trainer.py default_loss): tokens = chat template of all messages. offset = length of the chat template of messages[:-1] with add_generation_prompt=True. The loss mask keeps every token from offset onward. The user prompt (RULES, code definition, abstract, format) is fully masked. Trained: the empty think block the Qwen3 template adds to the last assistant turn, the JSON, <|im_end|> and the final newline.

Three rows from data/silver_v1/train.jsonl (full dumps with token pieces in v1_forensics.json q4_mask.rows):
- A PRESENT row: trained answer is {"status": "PRESENT", "reason": "", "quote": "CHSH Bell parameter S = 2.290 ± 0.010"} preceded by <think>, blank, </think>, blank, and followed by <|im_end|> and newline.
- A CANNOT_TELL row: 28 trained tokens: <think> \n\n </think> \n\n {" status ": " C ANNOT _T ELL ", " reason ": " METHOD _UN ST ATED ", " quote ": "" } <|im_end|> \n. The status value is 4 tokens, the reason value 4 tokens.
- An ABSENT row, same layout with a quote.

Prompt tokens and the generation prompt "<|im_start|>assistant\n" are masked (not trained). The empty think block is trained, and inference uses enable_thinking=False, which inserts the same block (selfcheck_train.json train_view_tail and infer_view_tail), so train and test formats agree.

## 5. Valid and train overlap

None found. Train covers 144 papers, valid 7 papers, shared paper ids 0, shared links 0, identical prompt texts 0 (the valid split is by paper id, silver.py:48). Maximum 5-gram Jaccard of any valid abstract against any train abstract is 0.007. Maximum title trigram Jaccard is 0.280. Maximum 5-gram Jaccard of any train or valid abstract against any gold item (data/gold_items.json) is 0.0143, and the contamination wall (results/contamination_wall.json) was run before. Within train, one paper supplies up to 4 rows (60 papers have 1 row, 48 have 2, 29 have 3, 7 have 4).

## 6. Decode order

The answer JSON is {"status", "reason", "quote"} in that order (silver.py:51 builds it, json.dumps keeps order, inference prompt format in common.py:24 lists the same order). Status comes before quote. A greedy decoder therefore emits the status token first, with no quote yet written, and cannot attempt a quote and fall back to CT. On CT rows the quote is empty by construction, and the rules text says "If you cannot quote evidence, use CANNOT_TELL" but the model has to decide that before it quotes. The verbatim check that the rules refer to runs afterwards in code, not in the model.

## 7. Other findings that bear on v2

- The base model's CT is also manufactured. runs/base_test.jsonl: 559 of 665 calls are CT / METHOD_UNSTATED with flag ungrounded, ABSENT 45, PRESENT 37, NA 16, parse failed 8. runs/base_dev.jsonl: 579 of 679 ungrounded. The base never emits CT itself. STAN's CT is its own output: runs/stan_test.jsonl has CT/METHOD_UNSTATED 566 and CT/NOT_RELEASED 99, all flag ok. So "base 12.3 percent CT-free" and "STAN 100 percent CT" compare a rule-converted base to a model that learned the rule's output.
- Teachers' decided shares on dev (results/decided_summary.json): llama 0.600, gemma 0.370, mistral 0.059, base 0.119. Teacher silver is therefore dominated by whichever teachers survive the grounding check.
- results/selfcheck_train.json: gold CT 13 of 40, STAN CT 40 of 40, all outputs CT/METHOD_UNSTATED with empty quote, flag ok.
