# Recount plan: arXiv 2610.31135v1 (Mixing Matters; IIT Roorkee / AISSMS IOIT / independent), committed before reading
Ack read: no funder statement in the PDF. Eligible free row.
Data: dataset/generations.jsonl.gz (229,700 per-item records with score), dataset/position_accuracy.csv.
Definitions (theirs, EXPERIMENT-SOURCE-OF-TRUTH.md): primacy = mean acc at positions 0,1 minus 4,5; recency = 8,9 minus 4,5;
floor = closed_book, ceiling = oracle; score field = their scoring.
## A. Recount
Table 1: Pythia-2.8B +0.052 [0.032, 0.072] / +0.075; Mamba v1 -0.001 / +0.077; Mamba2 v2 -0.018 / +0.105; floors 0.091 / 0.115 / 0.128,
ceilings 0.640 / 0.615 / 0.619; hybrid minus pure +0.019 [-0.006, 0.044] / -0.028 [-0.055, -0.001]; paired Mamba - Pythia
-0.0531 [-0.0775, -0.0281], Mamba2 - Pythia -0.0700. Paired question bootstrap, 20,000, seed 20261025.
## B. Pricing
B1 COPY CARRIER (known-good). Same model, same 800 questions, same prompt, different phase (Pythia-2.8B phase2 vs phase4;
   Mamba-2.8B phase2 vs phase4 vs phase5): per-item score agreement, and primacy(copy A) - primacy(copy B) with a paired
   interval. Expected 0 if decoding is deterministic. Any nonzero copy gap is apparatus; report it beside the family gap.
B2 PROMPT CARRIER. Phase 7 query-position variants (bookend, gold_padded, question_first) and instruction-template:
   Pythia minus Mamba primacy, paired, per variant, if positions 0,1,4,5 are present; else CANNOT_TELL for that variant.
   Does the family gap keep its sign across prompts: four outcomes per variant.
