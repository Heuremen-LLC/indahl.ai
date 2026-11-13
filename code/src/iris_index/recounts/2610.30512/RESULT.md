# Recount result: arXiv 2610.30512v1 (Yorke, UCL). Plan 223c77d committed before reading.
Data: github.com/Yorkel/llm-judge-release, data/october_rerun (17,000 GPT-4.1 judge calls, pinned gpt-4.1-2025-04-14, temperature 0).

## A. Recount: CLEAN
- Our parser on the raw text agrees with their stored verdict on 17,000 of 17,000 calls.
- Every Table 1 cell rebuilds to two decimals for all 7 setups (n, score change, % different winner, both floors, both excess estimators).
- Abstract figures: rerun floor 21.2% (21.19, mean of 21.1 / 21.5 / 20.9); label-only +28.2 pp (28.24) and -4.09 points;
  accuracy-first +6.7 pp (6.67). Their alternative estimators +20.5 / +36.0 also rebuild (20.46 / 36.02).

## B. Pricing from their own files
B1 FINGERPRINT CARRIER (planned). Default setup, runs 1 vs 2, prompts complete in all three default runs (497):
- same reported backend fingerprint in both rounds: 314 prompts, 17.5% change outcome
- different fingerprint in either round: 183 prompts, 27.3% change outcome
- difference +9.8 pp [+2.1, +17.6]: ABOVE.
- Runs 1-3 and 2-3: run 3 shares no fingerprint with runs 1 or 2 (0 matching prompts): CANNOT_TELL.
- Known-good (a run against itself): 0 changes.
Rebuttal tested (defined after the data): "the changed-backend prompts were just closer to the boundary".
- Partly true: mean |margin| (from run 3, not in the pair) 0.89 differ vs 0.99 match.
- Within margin bands the gap holds: +8.0 pp [+0.7, +15.3], ABOVE. Largest at margin 0: 60.6% vs 32.0%.
What it rules out: that a pinned model name at temperature 0 makes the serving backend irrelevant to a verdict.
It does not name a cause. Even with the same reported backend, 17.5% of outcomes change on a rerun.
Consequence for their estimator: their excess assumes each rerun draws from one distribution; the floor depends on the backend mix
of the runs compared. Whether that moves any Table 1 excess is CANNOT_TELL from what we ran.

## Status
Recount CLEAN, eligible free row. NOT booked yet: the plan books nothing before our own Faults/Guards seed recount.
