# STAN v1 plan

Written and committed 12 November 2026 before any teacher labelled anything and before any score was read. STAN is a sorter that drafts the claim-level checklist of Faults and Guards 2.0 (QIA-F1 to QIA-F7) for a person to confirm. It is never a gate or a certificate.

## Task

Input is the title and abstract of a published claim about an AI or quantum measurement result. For each code F1 to F7 the output is a status (PRESENT, ABSENT, CANNOT_TELL with one reason, or NOT_APPLICABLE) and, for PRESENT and ABSENT, a verbatim quote from the input. Codes, statuses and reasons are those of STANDARD.md version 2.0 and standard_v1.json. Reasons allowed for CANNOT_TELL are NOT_RELEASED, UNREADABLE, METHOD_UNSTATED, and for F7 also STRADDLES_EDGE, TOO_WIDE_TO_RESOLVE and NO_INTERVAL_FORMABLE.

STAN is asked one code at a time (one short call per code). A checklist is seven calls. Teachers are asked for the whole checklist in one call. Both use the same definition text for each code.

Known limit, stated up front: the human gold labels were made from full text and released files. Every model here sees only the abstract. Many codes cannot be tested from an abstract, so CANNOT_TELL will be common and agreement with gold will be capped by that.

## Data

- Gold: the 196 recounts in trackrecord/record.json. Gold label per code: PRESENT if the code is in the study's `codes` list (from the QIA List), otherwise NOT_FLAGGED. The List records only codes found, so ABSENT, CANNOT_TELL and NOT_APPLICABLE cannot be told apart in gold. Only F1 to F7 are scored. Q-codes are ignored.
- Gold split: the 196 recounts sorted by link, shuffled with Python random.Random(20261112), first 98 are dev, last 98 are test. The split is made on the full 196 before any abstract is fetched, so abstract availability cannot steer it. It is written to data/gold_split.json and committed with this plan. Items whose abstract cannot be fetched stay in the split and are counted as unavailable, not dropped silently.
- Gold never enters training, teacher prompts for the pool, or silver.
- Abstract source: OpenAlex (no key, polite rate, cached under data/abstracts_cache/), by DOI or by the arXiv DOI. When OpenAlex has no abstract, the public arXiv API is used as a second source, batched and cached. No one is contacted. An abstract under 300 characters is treated as unavailable.
- Pool: studies in qia_leads/matrix_page/list.json that have a link and a cached text file in qia_leads/sweep_20261101/texts_read, sweep_20261101/texts, backfill_20261101/texts, list_fixes_20261101/rundate_sample/texts or sweep_20261101/old_cut_fix/texts, that are not gold (by arXiv id without version, by DOI or by normalised title), and that are not in ledger/removed_at_request.json or qia_leads/REMOVED_ON_REQUEST.json. Pool labels in the List are never read for training. The pool is shuffled with random.Random(20261112) and the first 240 with a usable abstract are the first slice. Everything runs end to end on that slice.

## Teachers

Three model families, none of them Qwen, because the base is Qwen3.
1. IBM Granite: granite3.3:8b.
2. Mistral: mistral:7b-instruct-v0.3-q8_0 on Armature, or mistral:7b on the Mac if Armature is not free.
3. Meta Llama: llama3.1:8b.

These are the same families as the Sage V council seats (granite3.3:8b, mistral:7b, llama). The council MLX servers on 8801, 8803 and 8806 are parked or down while the house trains and are not touched. Port 8802 is up but carries a Qwen model and others, so it is not used. Teachers are called through the Ollama bases of the same models (Mac 127.0.0.1:11500 and Armature 192.168.8.158:11434), temperature 0, JSON output, no thinking. The endpoint each teacher used is recorded in teachers/config.json. Calls are resumable. Each result is appended to a jsonl file keyed by item and round.

## Pipeline rules

1. Round 1: each teacher labels every pool item blind with the checklist prompt and the standard's definitions in context.
2. Grounding by code: for PRESENT and ABSENT the quote must be an exact substring of the input after collapsing whitespace. No case folding. A label whose quote is not found becomes CANNOT_TELL with reason METHOD_UNSTATED for that teacher, and the original label is kept in the record as ungrounded.
3. Output that cannot be parsed, or has an unknown status or a CANNOT_TELL with no valid reason, is recorded as PARSE_FAILED for that code. PARSE_FAILED never agrees with anything and is never trained on.
4. Crosstalk: for each item with at least one disagreeing code, each teacher is shown the other two teachers' labels and quotes for the disagreeing codes once and may revise or hold. Both rounds are stored. Agreement reached only after crosstalk is flagged via=crosstalk.
5. Agreement: two labels agree when the status is the same and, for CANNOT_TELL, the reason is the same. A silver row is one (item, code) pair on which all three teachers agree with grounded quotes. Unanimity at round 1 is via=round1, at round 2 via=crosstalk. Because three-way unanimity over all seven codes of an item is rare with abstract input, silver is built per code, and fully unanimous items are counted separately in the report. For a quote, the silver target uses the shortest grounded quote among the teachers.
6. Two-of-three pairs go to review_queue/ with all labels and quotes for a person. They are never trained on. Disagreement is kept as data. Every item and code is counted by outcome and reason with no catch-all bin.
7. Class cap: within each code, no one (status, reason) class may exceed half of that code's silver rows. Extra rows of the larger class are dropped by a seeded shuffle (random.Random(1)) and recorded as unused_cap, not deleted.
8. Silver splits into train and a small valid set (about 5 percent) by item, seeded.

## Metrics (standard's rules)

- Per code, agreement with gold: an item agrees when (predicted PRESENT) equals (gold PRESENT). Every other predicted status counts as not PRESENT. 95 percent Wilson interval on the agreement rate. Items without an abstract are excluded from that model's denominator and counted.
- CANNOT_TELL counted separately by reason, per code and per model, plus PARSE_FAILED and UNGROUNDED counts.
- Also reported: gold prevalence per code, the majority-class agreement, and the share of items each model decided (not CANNOT_TELL, not NOT_APPLICABLE).
- Baseline: the untrained base (Qwen3-1.7B with the same per-code prompt) and each of the three teachers, on gold dev and gold test, written to results/baseline.md and baseline.json before training starts.

## Base model and training

- Base: Qwen/Qwen3-1.7B, Apache-2.0, loaded by mlx_lm from the local Hugging Face cache, bf16, thinking off. Qwen3-4B is not cached and is not fetched.
- LoRA with mlx_lm 0.31.3 in ~/bones-forge/venv, mirroring train_live.py: rank 8, scale 20, dropout 0, num_layers 16, batch_size 2, mask_prompt true, max_seq_length 4096, grad_checkpoint, seed 61, steps_per_report 20. Learning rate is 1e-4, not the 1e-5 of the 7B and 8B seats, because train_live.py itself records 1e-4 as the 1.7B precedent (YO). iters = min(300, max(50, train rows)).
- GPU: the Mac GPU is shared through sage_v/.train.lock. STAN takes the same exclusive flock before any MLX job (training and base and STAN inference) and waits if it is held. It does not stop or park the council servers. If the lock is held it queues.
- Armature CUDA lane: not used in v1.

## Paired test and keep rule

- On gold test, STAN and the untrained base answer the same items and codes. Flips are counted in both directions per code (base wrong and STAN right, STAN wrong and base right).
- Paired bootstrap, 2000 resamples over items, seed 7, on the difference in agreement (STAN minus base). Reported per code and pooled across F1 to F7 (mean of the seven per-code differences).
- STAN is kept only if the pooled difference is positive and its 95 percent paired bootstrap interval excludes zero. Otherwise it is reported plainly as not kept. Dev is used only to pick the checkpoint (final or best valid) and to check the output parses. Test is read once for the paired comparison after the checkpoint is chosen.
- Teachers are also scored on test and dev for reference, but the keep decision is only STAN against the base.

## Public record

Results are prepared as rows in the format of sage_library/sage_v_public/results/ (events.jsonl and paired.jsonl, plain strings only, matching the results_push.py guard) and written to stan/results/public_rows/. Nothing is pushed by this work. Weights stay private.

## Amendment 1, 12 November 2026, before any teacher labelled anything

The Mac Ollama on 11500 timed out at 300 seconds on a test call with a dummy text (granite3.3:8b and llama3.1:8b) because the Mac GPU is saturated by the house training jobs, load average above 50. Armature answered in 6 to 21 seconds. All three teachers therefore run on the Armature Ollama at 192.168.8.158:11434. The teacher set is now Meta Llama (llama3.1:8b), Mistral (mistral:7b-instruct-v0.3-q8_0) and Google Gemma (gemma3:4b). No Qwen. The IBM Granite teacher is dropped because it is not reachable at usable speed. The Sage V council MLX servers were not used. The base for STAN is unchanged.

## Amendment 2, 12 November 2026, before any teacher round was finished

Armature serves about one teacher call every 18 seconds when three teachers run together, so 240 pool items plus all gold for three teachers would take most of a day. The first slice is cut to the first 100 items of the seeded pool order (data/pool.json keeps all 240, the other 140 are unused in v1). Gold is unchanged and every gold item with an abstract is still labelled by all three teachers and scored. Every stage still runs to the end on this slice.

## Amendment 3 (12 Nov, before any gemma call): host only
The gemma teacher (gemma3:4b, same model tag) runs on the Mac's Ollama at 127.0.0.1:11500 instead of Armature, so the three teachers label in parallel on two machines. No model, prompt, split, metric or rule changes.
