# Recount + pricing plan: Jabarian & Imas (2025) NBER w34223 "Artificial Writing and Automated Detection" (UChicago Booth) - P-UC1
Committed BEFORE opening github.com/brianjabarian/DetectionAI (25 Oct 2026). Paper read in full (46 pp, NBER PDF).
Facts from the paper (verbatim): funding "University of Chicago Booth Center for Applied Artificial Intelligence, the Becker-Friedman
Institute Program in Behavioral Economics Research and the Google Cloud Research Program"; "All authors declare that they have no financial
or personal conflicts of interest"; NBER: "have not been peer-reviewed". Detectors compared: Pangram, OriginalityAI, GPTZero, RoBERTa.
Human set: "1,992 human texts, consisting of 200 Amazon reviews, 200 blogs, 300 news articles, 1,000 novel excerpts, 100 restaurant
reviews, and 192 resume passages" (pre-2020); AI sets of 1,992 per source model, matched on length, lexical variety, readability.
P1 (pricing, from the text alone): UChicago's page uses the study to support Pangram for student work ("indicates that Pangram is the best
   tool available"); the human test set contains no student writing and no non-native-English writing set -> the transfer to student
   assignments is ABOVE the record the study built (quote both; CANNOT_TELL on student-writing FPR).
R1 rebuild headline FPR/FNR per detector from the released JSON/logs (Youden and fixed thresholds as printed).
R2 FPR by human genre (does any genre carry the false positives?), with exact binomial intervals; FPR on the shortest passages.
R3 comparison set: Turnitin (the detector most universities license) is absent - noted, not a defect of the study.
Rules: read their notebooks as text only; our code; python3 -I; four outcomes; printed values beside ours.
