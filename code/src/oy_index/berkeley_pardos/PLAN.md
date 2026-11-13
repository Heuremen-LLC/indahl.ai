# Recount plan: Pardos & Bhandari, PLOS ONE 2024, "ChatGPT-generated help produces learning gains equivalent to human tutor-authored help on
# mathematics skills" (UC Berkeley; internal Berkeley grants -> IN). Committed BEFORE opening figshare 23935269 Participants.csv (25 Oct 2026).
From the paper (read): MTurk adults, 3 hint conditions x 4 subjects, N = 274 after 30% attrition (control 90, human tutor 86, ChatGPT 98);
pre/post = same 3 questions; learning gain = post - pre (percent). Printed: control +1.85% (p = 0.192), human +11.62% (p = 0.001), ChatGPT
+17.00% (p << 0.001); condition main effect F(2,262) = 5.037, p = 0.0071 (two-way ANOVA on ranks); Dunn: ChatGPT vs control p = 0.011,
human vs control p = 0.087. Pre-test means: control 55.15%, human 53.46%, ChatGPT 43.51%.
B1 rebuild Table 2 means and pre/post per condition and subject.
B2 EQUIVALENCE (the title's claim): ChatGPT minus human gain with a 95% CI (bootstrap); two one-sided tests at the paper's own power-analysis
   bound (Cohen's d = 0.5, in gain units) - EQUIVALENT only if the 90% CI sits inside +/- d=0.5; otherwise CANNOT_TELL (not "equivalent").
B3 baseline: gains are post - pre on 3 questions; ChatGPT starts 10-12 points lower; rebuild gains adjusted for pre-test (ANCOVA-style
   regression of post on condition + pre + subject) and print beside the raw gains (labelled post-hoc).
B4 human vs control: the printed comparison class for "equivalent" is not distinguished from no hints (p = 0.087); print that interval too.
Rules: our code (stdlib/numpy, python3 -I), schema dumped first; four outcomes; printed values beside ours. Participants are adults on MTurk,
not Berkeley students - the row says so.
