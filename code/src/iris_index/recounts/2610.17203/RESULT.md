# Recount result: arXiv 2610.17203v1 (TutorDuel, MIT). Plan committed before computing.
## A. Partly CLEAN
- Author-author agreement 69.6%: CLEAN.
- Planned rule (judge P(i) = picks / 16): Claude Opus 5 73.7% vs printed 74.0 (CLEAN within 0.5 pp); GPT-5.6-Sol 72.9% vs printed 74.5
  (not rebuilt: CANNOT_TELL under the plan).
- Defined after the data: the favorite rule (judge's more-picked answer, tie = 0.5) gives Sol 74.5% (printed 74.5, exact) and Opus 74.3%
  (printed 74.0). Table 4(c) scores the chat judges by their favorite.
## B. Priced (51-cell paired bootstrap, planned rule)
B1 Sol minus author-author +3.3 pp [-2.8, +9.4]; Opus minus author-author +4.0 pp [-1.9, +9.8]: both CONSISTENT, as the paper says for its
   own judge (+3.9 [-2.5, +10.0]).
B2 Sol minus Opus -0.7 pp [-3.6, +2.1] CONSISTENT. The scoring rule flips which chat judge "leads" (share of picks: Opus; favorite: Sol);
   neither order resolves.
