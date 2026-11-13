# Recount plan: arXiv 2610.18610v1 (Jev-ToM, HKUST), committed before reading predictions
Ack read: no funder statement in the PDF; HKUST is a public university. Eligible free row.
## A. Recount primary_overall.csv (12 models): strict exact match, invalid = wrong, equal-weight mean over nine benchmarks (their scorer's rule).
## B. Pricing
B1 Jev minus GPT-3.5-1106 overall (73.2 vs 71.6), paired bootstrap of questions resampled within each benchmark (5,000 draws, seed 20261025; amended before running, loop cost),
   equal-weight mean recomputed per draw. Also Jev minus GPT-5.6-Luna.
B2 "Excluding controls, Jev 69.1% and GPT-3.5 70.9%" (the "reversal"). Control = a question whose non-text fields contain "control"
   (found only in BigToM, 600 rows). If this rebuilds 69.1 / 70.9, B1's method is applied to the difference; if not, CANNOT_TELL.
   The paper's word "reverses" is judged by whether EITHER ordering resolves.
