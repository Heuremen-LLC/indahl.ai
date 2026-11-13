# Recount plan: arXiv 2610.31256v1 (IndoNutriQA, NLP-UB), committed before reading
Ack read: "This research was funded by Universitas Brawijaya." Public university: eligible free row.
Data: data/13-statistical_robustness/predictions/*.json (137 test items, per-item predictions + ground truths), bootstrap_ci.json.
## A. Recount
- Token F1 and EM per file with SQuAD normalisation re-typed from their text (lowercase, strip punctuation, drop a/an/the, split).
- Compare with their bootstrap_ci.json points and the paper text: GPT-4o 37.49 -> 50.33 (+12.8), GPT-4o-mini +7.0,
  Llama-3.1-8B +17.7 (5-shot 55.55), Sahabat-AI +16.5, "every evaluated LLM benefits substantially".
## B. Pricing (zero model calls)
B1 PAIRED FEW-SHOT GAIN. Same 137 items in both arms: per-item F1(5-shot) - F1(0-shot), mean with a paired bootstrap
   95% interval (20,000, seed 20261025), for all 8 LLMs. ABOVE / BELOW / CONSISTENT; CANNOT_TELL if an arm is missing.
   Known-good: an arm against itself gives 0 with zero width.
B2 THE UPSET. Llama-3.1-8B 5-shot vs GPT-4o 5-shot, paired over the same items, same method.
