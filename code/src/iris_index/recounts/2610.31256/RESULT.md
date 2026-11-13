# Recount result: arXiv 2610.31256v1 (IndoNutriQA). Plan committed before reading.
## A. CLEAN within rounding
- 22 prediction files, 137 items each. EM rebuilds on all 22. F1 rebuilds to the printed digit on 18; four differ by 0.01-0.02
  F1 points (GPT-4o 0-shot 37.51 vs 37.49, Llama 5-shot 55.57 vs 55.55, MedGemma 5-shot 54.30 vs 54.28, Merak 0-shot 32.45 vs 32.44).
  Cause not found; CONSISTENT, no reading turns on it.
## B. Priced
B1 paired 5-shot gain (same 137 items, paired bootstrap 20,000): every LLM ABOVE zero, +7.01 [+5.06, +9.10] (GPT-4o-mini) to
   +17.74 [+12.92, +22.82] (Llama-3.1-8B). "Every evaluated LLM benefits substantially" holds on the paired ruler.
B2 "frontier GPT-4o (50.33) is matched by Llama-3.1-8B (55.55) ... (overlapping CIs)": paired, Llama leads by +5.24 [+0.91, +9.81],
   ABOVE. Overlapping unpaired intervals were read as a match; the paired reading separates them.
Defined after the data: "top three cluster within overlapping intervals": Llama vs MedGemma +1.27 [-3.00, +5.83] CONSISTENT;
   MedGemma vs GPT-4o +3.97 [+0.09, +8.00] ABOVE; all three ABOVE the best fine-tuned baseline (third: +13.91 [+6.77, +20.86]).
Not priced: the LLM-judge safety column (they already mark it unvalidated, judge-vs-rater 0.133).
