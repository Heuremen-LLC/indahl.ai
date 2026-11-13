# Recount result: arXiv 2610.31135v1 (Mixing Matters). Plan fa0a87d committed before reading.
## A. CLEAN
Table 1 rebuilds from 229,700 records: Pythia-2.8B primacy +0.052 [0.032, 0.072], recency +0.075; Mamba v1 -0.001 / +0.077;
Mamba2 v2 -0.018 / +0.105; floors 0.091 / 0.115 / 0.128, ceilings 0.640 / 0.615 / 0.619; hybrid minus pure +0.019 [-0.006, 0.044] /
-0.028 [-0.055, -0.001]; paired Mamba - Pythia -0.0531 (ours [-0.0769, -0.0288], theirs [-0.0775, -0.0281]: bootstrap seed), Mamba2 - Pythia -0.0700.
## B. Priced
B1 COPY CARRIER. Known-good: Pythia-2.8B and Mamba-2.8B, phase 2 vs phase 4, separate runs (different run ids), same A40 host,
   same seed, greedy: 800 of 800 items identical, copy gap 0 exactly. Cross-GPU copy (Mamba-2.8B, phase 2 A40 vs phase 5 A10G):
   0.95% of items change score; primacy copy gap +0.0019 [-0.0050, +0.0088] CONSISTENT, about 1/28 of the family gap.
B2 PROMPT CARRIER (template in the key; first pass merged two templates and was rerun). Pythia minus Mamba primacy, 200 questions:
   concise +0.080 ABOVE; question_first +0.068 ABOVE; bookend +0.048 [-0.008, +0.105] CONSISTENT; instructional +0.015 CONSISTENT;
   gold_padded +0.010 CONSISTENT. Same 200 questions, baseline prompt (defined after the data): +0.070 [+0.015, +0.125] ABOVE.
   (REFEREE: within-GPU interactions all span zero; the prompt effect is unresolved. Earlier 'holds' sentence withdrawn.)
CONFOUND: every phase 7 variant also changed GPU (T4 for templates, L40S for query position; baseline A40). B1 prices A40 -> A10G
   only, so the GPU share of the prompt effect on T4 / L40S is CANNOT_TELL.
