# Addendum 2 to PLAN_YO_SHUFFLED.md (4 Nov 2026): the SELF-LABEL arm (Sage's rulings). Stamped before any self-label is generated or adapter trained.
Name: SELF-LABEL (NEW, 4 Nov). Not "replay-only": that name keeps its 31 Oct meaning (yo/CHECKS.md line 178: replay items alone, YO v4-v8).
Question: does YO Read's gain need new information, or would training on the base model's own answers give it?
Labels: every train and valid prompt (data/train.jsonl, data/valid.jsonl, prompts unchanged) gets the frozen base model's own answer:
  base checkpoint Qwen/Qwen3-1.7B, Hugging Face snapshot 70d244cc86ccca08cf5af4e1e306ecf908b1ad5e, weights sha256:
169ad53ec313c3a34b06c0809216e4fc072cce444a5d4ff2b59690d064130ed5  ~/.cache/huggingface/hub/models--Qwen--Qwen3-1.7B/snapshots/70d244cc86ccca08cf5af4e1e306ecf908b1ad5e/model-00001-of-00002.safetensors
912becff8d60672aa8628ef08c05898d9adf17c2ad4ae3caf99b065622fdeff9  ~/.cache/huggingface/hub/models--Qwen--Qwen3-1.7B/snapshots/70d244cc86ccca08cf5af4e1e306ecf908b1ad5e/model-00002-of-00002.safetensors
  decoding: mlx_lm.generate, greedy (default temperature 0), max_tokens 8, prompt rendered by yo2_data.render exactly as yr_eval.py does;
  parse: yr_eval.py's parse, the first YES or NO word in the reply. A reply with neither word is OFF-FORMAT: that item is left out of the
  self-label training set, and the count left out is printed per question and split.
Base-rate report, written to selflabel/BASE_RATES.text BEFORE any adapter trains: per question and split, self-label YES share, real YES share,
  off-format count. MISMATCH line, fixed now: if a question's self-label YES share differs from its real YES share by more than 0.10, the arm still
  runs, and the page says the self-labels were mostly one answer for that question, so that question's SELF-LABEL comparison is a weak test.
Training: identical to yr1-3.yaml; seeds 74, 75, 76; data selflabel/data/.
Test: YO Read (seeds 61, 62, 63, the rescored outputs) against each SELF-LABEL adapter, per field, same 148 papers, under PREREG_YO_RESCORE.md
  line 15 verbatim (higher accuracy AND Holm-corrected p < 0.05), exact McNemar two-sided (its line 13). Holm family: the 9 comparisons of this arm
  (YO Read seed i vs self-label seed 7(3+i), 3 pairs x 3 fields), separate from the shuffled arm's family of 9.
PASS: YO Read beats all three self-label adapters on DATES (and, separately, on LINK). FAIL: it does not; the page then says the gain is NOT SHOWN to
  need the real labels (never "self-sharpening proven"; three seeds may be underpowered).
Separate sentences: each arm prints its own sentence and neither borrows the other's result. A combined sentence such as "the gain needs the real
  labels" may be printed only if BOTH arms pass.
