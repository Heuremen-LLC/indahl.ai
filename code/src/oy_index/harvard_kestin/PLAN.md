# Recount plan: Kestin, Miller, Klales, Milbourne, Ponti (Harvard), "AI tutoring outperforms in-class active learning", Sci Rep 15:17458 (2025)
Committed BEFORE opening https://github.com/HarvardAItutor/Study-Data-v4 (25 Oct 2026). Funding: none stated; private university -> IN.
Headlines to rebuild (their printed values):
 H1 post-test means: AI 4.5 (N=142) vs in-class active learning 3.5 (N=174); combined pre-test 2.75 (N=316); Mann-Whitney z=-5.6, p<1e-8.
 H2 effect size: linear regression 0.63; quantile regression 0.73 to 1.3 SD.
 H3 time: AI median 49 min; 70% under 60 min; no correlation of time with post-test.
 H4 perceptions (5-pt Likert): engagement 4.1 (0.98) vs 3.6 (0.92), t(311)=-4.5; motivation 3.4 (1.0) vs 3.1 (0.86), t(311)=-3.4.
 H5 design counts: 233 enrolled, 194 eligible, crossover over two weeks (surface tension, fluid flow).
Pricing (ours, labelled):
 P1 unit of analysis: N=142+174=316 are lesson observations from 194 students in a crossover; each student contributes to both arms.
    Reprice H1 as a within-student paired difference (AI lesson minus active-learning lesson), student-cluster bootstrap, with week/topic
    and order as carriers (period effect, carryover) if the fields exist; four outcomes.
 P2 "in less time": compare AI time-on-task against the in-class session length the data/paper state; print the share over that length.
 P3 ceiling: share of post-tests at the maximum score per arm (their own caveat on the 0.63).
 P4 the 316 vs 2 x 194 = 388 gap: which lesson observations are missing and from which arm (the absence is a reading).
Rules: our code, python3 -I, no code from the repo run; dump schema first; intervals; four outcomes; old printed value beside ours.
