# Recount result: arXiv 2610.25159v1 (Legal Guidance in the Wild). Plan committed before reading.
## A. CLEAN: accuracy / macro-F1 / precision / recall for TF-IDF, ModernBERT-base, ModernBERT-large rebuild exactly from the 200 gold items.
## B. Priced
B1 The silver labeller (GPT) scored as a system on the gold: accuracy 0.960, macro-F1 0.959; ahead of every trained classifier
   by +0.115 to +0.145 accuracy (paired, all ABOVE). The gold was made by reviewing that labeller's output (their own anchoring caveat),
   so how much of the lead is anchoring is CANNOT_TELL without a from-scratch gold set. The strongest system on their gold is the one
   the gold was anchored to, and it is not in their results table.
B2 Items where reviewers corrected the silver label: 8 (< 10): CANNOT_TELL. Descriptive only: classifiers matched the wrong silver label
   on 4, 5, 4 of 8, against error rates 0.14-0.17 elsewhere.
