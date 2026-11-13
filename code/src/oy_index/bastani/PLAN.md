# Recount plan: Bastani et al., "Generative AI without guardrails can harm learning", PNAS 122(26) 2025 (Penn/Wharton; Penn S7)
Committed BEFORE opening github.com/obastani/GenAICanHarmLearning (25 Oct 2026). Funding: Wharton (private) -> IN.
Headlines to rebuild (Table 1, OLS with session, grader, grade-level and teacher fixed effects + prev GPA; HC1 SEs clustered by class;
honors classrooms excluded; 2,848 student-session observations; "nearly a thousand" students):
 B1 practice: GPT Base +0.137 (0.031), GPT Tutor +0.361 (0.032); control mean 0.284 (SD 0.287) -> "48%" and "127%".
 B2 exam (unassisted): GPT Base -0.054 (0.022) *, GPT Tutor -0.004 (0.013); control mean 0.321 (SD 0.277) -> "17% reduction".
Pricing (ours):
 P1 number of clusters (classrooms) and arms per classroom; with few clusters, cluster-robust SEs can understate width: wild cluster
    bootstrap (Rademacher, 9,999 draws, restricted null) p-value for GPT Base on exam; four outcomes on the coefficient.
 P2 student vs student-session unit: 2,848 rows vs ~1,000 students; count sessions per student.
 P3 honors exclusion: report the coefficient with honors classrooms included (labelled post-hoc) if the data carry them.
 P4 "17%" = -0.054 / 0.321: check the ratio and that the percentage is relative to the control mean (not a percentage-point change).
Rules: our code (numpy/stdlib, python3 -I), no code from the repo run; dump schema first; four outcomes; printed value beside ours.
