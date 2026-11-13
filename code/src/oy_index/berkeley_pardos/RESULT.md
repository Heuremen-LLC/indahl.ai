# Pardos & Bhandari (2024) PLOS ONE - recount (Bones, 25 Oct 2026). Data: figshare 23935269 Participants.csv (274 rows: ChatGPT 98,
# Human tutor 86, No-hint control 90). Our code: berkeley_pardos/recount.py (stdlib + numpy, 10,000-draw bootstrap).
B1 REBUILDS (Table 2 overall): pre / post / gain - control 55.15 / 57.01 / +1.85; human tutor 53.46 / 65.09 / +11.62; ChatGPT 43.51 /
   60.52 / +17.00 (percent; all identical to the printed values).
B2 the title's "equivalent": ChatGPT minus human gain +5.38 pts, 95% [-3.94, +14.89], 90% [-2.48, +13.52]. Under the paper's own power-analysis
   effect size (Cohen's d = 0.5 = +/-16.39 pts here) the 90% interval sits inside the bound -> EQUIVALENT at that margin. The margin is
   wider than the human tutor's own gain over no hints (+9.77 [+0.02, +19.53]); equivalence holds at any margin of about 13.4 pts or wider.
   Human tutor vs no hints is NOT shown equivalent at the same margin (90% upper +17.9 vs 16.5). (Corrected after referee.) Equivalence was not tested in the paper; the title's claim rests on a non-significant difference
   (reading defined after the data).
B3 baseline (post-hoc): ChatGPT starts 10-12 pts lower on a 3-question pre-test. Post-test adjusted for pre-test and lesson (OLS):
   human vs control +8.14 (SE 4.15); ChatGPT vs control +11.06 (SE 4.06) -> ABOVE; ChatGPT minus human +2.92 (SE 4.10) -> CONSISTENT
   (bound roughly -5 to +11 pts).
B4 the comparison class: human-tutor hints vs no hints, printed Dunn p = 0.087; our raw-gain interval +9.77 [+0.02, +19.53] (lower end at 0).
Participants: Mechanical Turk adults, not Berkeley students; 30% attrition (paper states it). Funding: internal UC Berkeley grants
("The funders had no role..."). Credit: participant data released (CC BY 4.0); attrition and power analysis reported.
State: RECOUNTED.
