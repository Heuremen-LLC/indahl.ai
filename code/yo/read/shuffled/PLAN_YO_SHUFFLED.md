# YO Read shuffled-label null (Sage's item 3, 4 Nov 2026). FROZEN when its OpenTimestamps proof reaches a Bitcoin block; no training before that block.
Question: does YO Read's DATES/LINK gain over always-NO depend on the labels, or would any adapter trained on these prompts get it?
Data: shuffled/data/{train,valid}.jsonl = data/{train,valid}.jsonl with the YES/NO completions permuted WITHIN each question (DATES, LINK,
REQUEST separately; random.Random(20261104) train, 20261105 valid), so prompts and base rates are unchanged and the label-to-prompt link is broken.
Training: identical to yr1-3.yaml (Qwen/Qwen3-1.7B, LoRA 16 layers, batch 4, lr 1e-4, 800 iters, mask_prompt, max_seq 2048); seeds 71, 72, 73.
Scoring: the frozen rescore (yr_rescore_eval.py + yr_rescore_score.py, PREREG_YO_RESCORE fe751109) on data/test_items_rescore.jsonl, unchanged.
Prediction (written before data): no shuffled seed clears always-NO on DATES or on LINK (McNemar, Holm across 9, as frozen).
PASS (the label link is shown): 0 of 3 shuffled seeds clear DATES and 0 of 3 clear LINK. KILL (the YO Read gain is not shown to come from the labels;
said on the IRIS lab page): 2 or more shuffled seeds clear DATES, or 2 or more clear LINK. Otherwise CANNOT TELL, and the page says that.
Not in this plan: the "replay-only" arm Sage named. Its definition is not in our record; it waits for her written definition and its own stamp.
One GPU job at a time on the Mac; about 20 min per adapter.
