# Recount plan: arXiv 2610.17203v1 (TutorDuel; Puech, Salakhutdinov, Bertsimas; MIT), committed before computing
Ack read: no funder statement in the PDF. Eligible free row (MIT is not on the cut list).
Data: HF romainpuech/tutorduel human_labels/labels.jsonl (204 comparisons, two authors) and chat_judges.jsonl (GPT-5.6-Sol, Claude Opus 5:
picks of persona i among 4 samples on each of 4 prompts).
## A. Recount Table 4(c) and the author-author figure: judge P(i) = picks of i / 16; agreement with an author = P(i) if the author chose i,
   else 1 - P(i); averaged over both authors and 204 comparisons. Printed: Sol 74.5, Opus 74.0; authors agree 69.6%.
   If the rule does not rebuild 74.5 / 74.0 to 0.5 pp, A is CANNOT_TELL for that row.
## B. Pricing: paired cell bootstrap (51 (student, question) cells, as theirs; 20,000 draws, seed 20261025)
B1 each chat judge's agreement minus author-author agreement (the luna judge's +3.9 [-2.5, +10.0] is theirs; these two are not printed).
B2 Sol minus Opus agreement.
