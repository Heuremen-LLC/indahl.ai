# Jabarian & Imas (2025) NBER w34223 - recount + pricing (Bones, 25 Oct 2026). Data: github.com/brianjabarian/DetectionAI (all_json/200_*,
# 4 source-model files x 1,992 records with human and AI verdicts per detector). Our code: uchicago_ji/recount.py (stdlib; ast.literal_eval).
R1 vendor-label rates (our cut; the paper has no 'default': it uses thresholds 0.1-0.9 and Youden) - Pangram: prediction != "Unlikely AI"
   (counts 'Possibly AI', score >= ~0.22); Originality: classification AI; GPTZero: average_generated_prob >= 0.5:
   FPR on the 1,992 human texts: Pangram 1/1,992 = 0.05% [0.009%, 0.28%] at the vendor label (the one hit scores 0.495; 0/1,992 at the
   paper's 0.5, Table 3: 0.0000); Originality 2/1,827 = 0.11% [0.03%, 0.40%] (165 with no verdict);
   GPTZero 15/1,992 = 0.75% [0.46%, 1.24%] (Wilson 95%).
   FNR on AI texts: Pangram 0.65% (GPT-4.1) to 1.61% (Gemini 2.0 Flash); GPTZero 0.20% to 2.91%; Originality 2.70% to 37.33% (Claude Opus 4).
   Printed (paper): Pangram FPR 0.0010-0.0000 across thresholds, FNR 0.0045-0.038; Originality FNR and FPR match exactly; GPTZero 15 here vs
   ~14 printed (one score of exactly 0.5: >= here, > in the paper) -> matches except that tie.
R2 FPR by genre: Pangram's single false positive is an Amazon review (1/200); 0 of 1,000 novels, 0/300 news, 0/200 blogs, 0/192 resumes,
   0/100 restaurant reviews. (A zero in a genre is a bound: e.g. novels 0/1,000 -> upper 95% ~0.38%.)
P1 PRICING (the use, not the study; corrected after referee 25 Oct): UChicago's page makes a COMPARATIVE claim - "AI detectors, including
   Pangram, are not perfect, though research from Booth faculty ... indicates that Pangram is the best tool available" - with hedges beside it
   ("A Pangram result, in isolation, is not enough..."; false positives and non-native-English bias named as concerns; "efficacy ... may
   change"). The study supports that comparison within its corpus: "200 Amazon reviews, 200 blogs, 300 news articles, 1,000 novel excerpts,
   100 restaurant reviews, and 192 resume passages" (pre-2020; no student essays, no non-native-English set). The page states no accuracy
   rate for student writing; the study cannot give one -> student-writing FPR CANNOT_TELL; comparative claim CONSISTENT within the corpus.
   (First draft called the use ABOVE the record - WITHDRAWN as unfair to the page.) The page cites the SSRN 5407424 version (26 Aug 2025);
   we read NBER w34223; versions not compared.
Study facts: NBER: "have not been peer-reviewed"; funding Booth CAAI, Becker-Friedman Institute, Google Cloud Research Program; "no financial
   or personal conflicts of interest"; detectors compared: Pangram, OriginalityAI, GPTZero, RoBERTa (Turnitin not in the set).
   Credit: full code, data and logs released ("Scientific Transparency: Replication Note").
State: RECOUNTED (study) + PRICED (institutional use).
