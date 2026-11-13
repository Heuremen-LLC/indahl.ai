# Recount plan: arXiv 2610.15732v1 (NepPlural; IRIIS Nepal / independent), committed before reading model outputs
Ack read: no funder statement in the PDF. Eligible free row.
Data: data/pools/sample/step3/gold_final.csv (300 human-adjudicated), results/forced_single/*.jsonl, results/abstention_baseline/*.jsonl.
## A. Recount Table 4 "Gold" column for the Forced and Abstain rows (GPT, Gemini, Claude, Majority): mean over four axes of macro-F1,
   labels = classes present in the reference (their protocol_audit.py rule), against gold_final. Printed: forced 0.49 / 0.48 / 0.47 /
   0.50; abstain 0.70 / 0.75 / 0.67 / 0.74. NP F1 0.83 / 0.87 / 0.79; false abstention 15.8 / 4.9 / 8.2% on the 184 persona comments.
## B. Pricing (zero model calls)
B1 widths: comment bootstrap (2,000 draws, seed 20261025; sklearn per draw; amended before running) on every A cell (Table 4 prints none).
B2 abstain minus forced, paired per model: does the abstention gain clear its width.
B3 the model ranking under abstention (Gemini 0.75 > GPT 0.70 > Claude 0.67): paired pairwise differences, four outcomes each.
