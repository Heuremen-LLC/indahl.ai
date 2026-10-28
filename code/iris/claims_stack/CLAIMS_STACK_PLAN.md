# Public update 2: model claims against the models (28 Oct 2026, his word)
Written and committed before any claim is run. Round 1 of this line checked how models behave on our claims. This one checks the open-weight vendors' own stated results the same way we check hardware vendors in SAD: their number, their setting, our rerun, four outcomes.

## Which claims (all of them or none)
For each of the ten bench models, every numeric benchmark result in the model card or technical report's main results table that has a task in EleutherAI lm-evaluation-harness (MIT) with a matching few-shot count and metric. The claim list (model, verbatim sentence or table cell, source URL and date, stated value, stated shots, stated harness) is committed as claims_stack.csv before any run. No claim is added or dropped after a result is seen. A claim with no matching public task is listed as NOT RUN with the reason, never omitted.

## Instruments
A. Original weights in bf16 on this Mac, one worker (models up to 8B fit), harness at a pinned commit.
B. The quantized copy on our seat (the one the bench uses), same tasks.
The gap A to B is printed for every claim. It is a reading, not an error.

## Known-good first
One result per harness task that an independent public record also reports (for example a leaderboard entry for the same model and shots) is rerun first. If we miss the independent number beyond its own interval, the harness setup is wrong and no claim is read until it is fixed, declared as an addendum.

## Outcomes
BELOW or ABOVE only where the stated value sits outside our 95% interval (the harness's own standard error, widened by the card's rounding) and the stated setting matches ours. CONSISTENT where it sits inside. CANNOT_TELL where the setting is undisclosed, the harness differs, the sample is too small for the claimed precision, or the claim needs a private prompt format. Each BELOW and CANNOT_TELL is recounted by hand and a one-line rebuttal is written for it before it is printed (a rebuttal that only sounds right is tested, never assumed).

## Reading and release
Per model, a list of every claim with its outcome. No ranking, no rate across models, no adjectives. The rerun scripts and the raw harness outputs go with the page and a DOI. The vendor-response path is open on every row from the first day.
