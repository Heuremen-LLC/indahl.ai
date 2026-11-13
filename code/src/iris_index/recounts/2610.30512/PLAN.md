# Recount plan: arXiv 2610.30512v1 (Yorke, UCL), committed before any October data is read by us
Source: github.com/Yorkel/llm-judge-release main, raw judge outputs data/october_rerun/run{1,2,3}/*.jsonl.
Ack read: sole author, UCL; no funder statement in the PDF. Public university: eligible.

## A. Recount (their claims, their data, our code)
- Our own parser on round*.raw: last [[X]] tag, else last [X]; uppercase; map A>>B -2, A>B -1, A=B 0, B>A +1, B>>A +2;
  round2 sign flipped; order-average; a prompt is complete only if both rounds parse.
- Rebuild: default rerun floor (21.2% abstract), Table 1 for all 7 setups (score change, % different winner,
  both excess estimators: +28.2 / +20.5 / +36.0 label-only; +6.7 / +5.7 accuracy-first; -4.09 points label-only).
- Also compare our parsed verdict against their stored verdict field, call by call.
- Outcome per number: CLEAN (rebuilds to the printed digit) / ABOVE / BELOW (with the gap) / CANNOT_TELL.

## B. Pricing, from their own files (zero model calls), defined now
B1 FINGERPRINT CARRIER. For each pair of default runs (1-2, 1-3, 2-3), split prompts by whether the
    system_fingerprint matches between the two runs for BOTH rounds vs differs in either. Report boundary-change
    rate in each group with a 95% bootstrap interval of the difference (prompts resampled, 20,000, seed 20261025).
    Outcomes: ABOVE (differ > match), BELOW, CONSISTENT (interval holds 0; print the bound), CANNOT_TELL
    (either group < 30 prompts). Known-good for B1: the same split on a pair of IDENTICAL records (a run vs itself)
    must give 0 changes in both groups.
B2 DATE CARRIER. Same split by call timestamp hour, if fingerprints are all equal (B1 then CANNOT_TELL).
No reading outside A and B goes in the book without a "defined after the data" label.
