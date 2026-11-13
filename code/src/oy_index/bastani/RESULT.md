# Bastani et al., PNAS 122(26) 2025 - recount (Bones, 25 Oct 2026). Data: github.com/obastani/GenAICanHarmLearning main_regressions/
# final_data.csv (3,255 rows; 356 honors). Our code: bastani/recount.py (numpy OLS with teacher/session/grader/year dummies, CR1 SEs by Class).
REBUILDS (Table 1, honors excluded, 2,849 rows = printed 2,848 + 1 row with Grader = NA (R's lm drops it; ours absorbs it in a singleton dummy; coefficients unaffected), 825 students, 44 classes, one arm per class: control 17, GPT Tutor 14,
GPT Base 13):
 practice: GPT Base +0.137 (0.031), GPT Tutor +0.361 (0.032) (printed identical); control mean 0.284 (SD 0.287) on all 1,076 control rows -> +48%, +127%
 exam: GPT Base -0.054 (0.022), GPT Tutor -0.004 (0.013) (printed identical); control mean 0.321 (SD 0.277) on all 1,076 control rows (our first
   draft used the 1,062 regression rows: 0.285/0.324 - corrected after referee) -> -17%, -1%
RULERS ON THE HEADLINE "17% reduction" (exam, GPT Base; defined after the data except where in PLAN.md):
 R1 their CR1 cluster-robust SE: t = -2.42 (44 clusters) -> p ~ 0.02 -> BELOW.
 R2 wild cluster bootstrap (Rademacher, restricted null; known-good: practice GPT Base p = 0.005): p = 0.110 at 1,999 draws (deviation from the
    planned 9,999); referee rerun at 9,999 draws: p = 0.106 -> CONSISTENT.
 R3 permutation test (arm labels permuted across classes within grade level, 2,000 draws): p = 0.038. NOT design-based: the paper assigned arms
    by "an integer program that matched observable characteristics while satisfying scheduling constraints", not a lottery; R3 is a
    hypothetical permutation reading and is not counted as a ruler of record.
 READING: the point estimate rebuilds exactly; whether it is distinguished from zero depends on the ruler (their CR1 p ~ 0.02; wild cluster
 bootstrap p ~ 0.11) -> CANNOT_TELL between rulers. With 13 GPT Base classrooms the inference is at the edge; printed as resolved without that caveat. (R2 can be
 conservative with few treated clusters; R3 assumes randomization within grade, which the paper does not state as the design.)
 Honors included (post-hoc): exam GPT Base -0.064 (0.026), practice +0.101 (0.032) - same signs.
 Unit: 2,849 student-session rows from 825 students ("nearly a thousand" in the abstract = 928 with honors).
Funding: Wharton (private) -> IN. State: RECOUNTED.
