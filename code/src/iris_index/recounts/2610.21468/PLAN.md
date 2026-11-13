# Recount plan: arXiv 2610.21468v1 (nonlinear storytelling; IUT Bangladesh / Utah / USC), committed before reading verdicts
Ack read: no funder statement in the PDF. Eligible free row.
Data: experiments/results/grapharm_pairwise_rows.csv (Gemini 3.1 Pro judge), humaneval/responses2.csv (71 readers).
Reader value A = left condition, B = right (assumed; checked by whether the reader G1-vs-G2 share rebuilds 72%; if not, CANNOT_TELL).
## A. Recount: judge G1 vs G0 31-14 (11 ties); judge G1 vs G2 23-22; readers prefer G1 in 72% of decisive G1-vs-G2 verdicts.
## B. Pricing: the paired item-level test the paper names but does not run
B1 For each (generator, story) in G1-vs-G2 and G1-vs-G0: judge winner vs reader majority on the 'better' measure. Agreement on items
   decisive for both, with a bootstrap over items (20,000, seed 20261025).
B2 Ceiling (known-good for humans): reader test-retest, 'better' vs 'better_repeat' on the same item and reader: agreement share.
   And reader-vs-reader agreement on shared items. The judge's agreement with readers is read against these: ABOVE / CONSISTENT / BELOW.
