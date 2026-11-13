# Harvard Kestin et al. (Sci Rep 2025) recount - Bones, 25 Oct 2026. Data: github.com/HarvardAItutor/Study-Data-v4 (one .dta, 316 rows x 9
# fields: rid, lect_AI, post_score, pre_score, engaged/enjoyed/effort_learn/feel_difficult scores, new_total_total_time2). Our code:
# dta118.py (stdlib Stata reader), recount.py.
REBUILDS:
 H1 medians: post AI 4.5 (N=142), AL 3.5 (N=174), pre 2.75 (N=316) - exact AS MEDIANS (text: "higher median (M)"; Fig. 1 caption says
    "mean"; means are AI 4.31, AL 3.57, pre 2.67). Mann-Whitney z = -5.59 on 316 lesson rows (printed -5.6) - exact.
 H3 time: AI median 49.3 min (printed 49), 71% under 60 (printed 70%); every in-class row is 60.0 min (171 of 174 with a value).
 H4 engagement 4.11 (0.98) vs 3.62 (0.92), t(311) = -4.54 (printed -4.5) - exact; "motivation" 3.4 (1.0) vs 3.1 (0.86), t(311) = -3.39
    (printed -3.4) - rebuilds only from the field named feel_difficult_score (3.44 (1.02) vs 3.08 (0.86)); mapping INFERRED by matching
    means and t and by elimination against the four named constructs (the paper gives no item text); no field named motivation or growth
    mindset exists in the release.
 H5 194 students (rid) - exact.
PRICED (readings defined after the data unless in PLAN.md):
 P4 eligibility: 122 students have rows for both lessons, 52 only active learning, 20 only AI. The paper's eligibility sentence ("participation
    in both in-class and AI-tutored instruction", all tests) implies two rows each; the release shows 72 students with one, and 316 = 122x2 + 72
    rows, not 388. Cause CANNOT_TELL (a dropped row for an attended lesson, or the sentence describing the design).
 P1 unit: the headline test compares 316 lesson rows as independent; 122 students contribute to both arms. Within-student (paired,
    122 students, 5000-draw student bootstrap; topic and week confounded, not separable in the release): post AI minus AL +0.65 [+0.40, +0.91] -> ABOVE; gain (post-pre) difference +0.40
    [+0.01, +0.80] -> ABOVE MARGINAL (lower end 0.01). Mann-Whitney on the 122 paired only: z = -4.64.
 Pre-test imbalance in the unpaired comparison: pre mean AI 2.80 vs AL 2.56 (all rows); paired-only 2.85 vs 2.60.
 H4 test type: Fig. 3 caption says "dependent t-tests"; the printed t(311) values rebuild as INDEPENDENT pooled t-tests (df 140+173-2).
    Dependent on the 120 students with both ratings: engagement t(119) = -3.97 (holds); feel_difficult ("motivation") t(119) = -2.15.
 P2 "in less time": AI median 49.3 min against a 60-min class (authors: "we assume 60 minutes" for in-class; "30% spent more than 60"
    - both credited); 29% of AI rows exceed 60 min.
 P3 ceiling: share at max post (6.0) AI 6%, AL 3% (authors' own caveat that the ceiling makes 0.63 an underestimate).
 Order/period/carryover (crossover carriers): NO week/topic/order field in the release -> CANNOT_TELL.
 H2 regression effect sizes (0.63; 0.73-1.3 SD): model specification not in the release -> not rebuilt (pending the paper's methods).
READING: the post-test difference is positive within the 122 students with both lessons (+0.65 [+0.40,+0.91]; topic/week confounded);
the gain difference is marginal; 72 of 194 students have one row where the eligibility sentence implies two (cause CANNOT_TELL); "M" is a
median labelled as a mean in one caption; "motivation" is carried by the field named feel_difficult (inferred); the printed t values are
independent tests where the caption says dependent. Funding: none stated. State: RECOUNTED.
