# FLU: plan addendum for Faults and Guards 2.0 (12 November 2026)

This addendum changes only the outcome rule. The data, the sources, the hub, the frame, the rows, the known-good gates and the tests are unchanged. PLAN.md is not edited and its hash seal stands. Every outcome recorded earlier stands under the rules it named. This addendum is written before any reading under the new rule.

## What is read against what
Coverage cells are read against the stated level, 0.50 for the middle interval and 0.95 for the outer interval. Each is a point figure and the plan named no tolerance. None is named now, because a tolerance written after the data would be a rule written after the data. The width caps of 0.10 for coverage cells and 0.20 for the weighted interval score ratio are not tolerances and no longer decide an outcome. The weighted interval score ratio is read against 1, which is also a point figure with no tolerance. CONSISTENT is not available for a cell. A cell reads BELOW when the whole interval lies below the figure, ABOVE when it lies wholly above, and otherwise CANNOT_TELL with reason STRADDLES_EDGE. The edges are closed.

## The size that matters
None is named. The both-alternatives test is not applied. A later addendum can name one before a read.

## Rows
A row is an exact read of a published reported count against two published quantiles, with no sampling, so its interval has zero width. A row reads ABOVE when the count is above the upper quantile, BELOW when it is below the lower quantile, and CONSISTENT when it lies between them, edges included. This is the band [lower quantile, upper quantile] and it is unchanged. It is a row label that feeds the cell, not a reading of the cell.

## Interval method
Unchanged. A moving-block bootstrap over target weeks, blocks of 4 consecutive weeks, 2,000 replicates, seed 20261110, the same draws for every cell, 95 percent, percentile. The desk keeps its own bootstrap, because the kit's bootstrap draws from a different generator and would not reproduce the stored intervals. The method, the seed and the draws are the same as before.

## How the desk's own causes of CANNOT_TELL map to the closed reasons
- A cell with fewer than 30 scored rows or fewer than 8 distinct target weeks is CANNOT_TELL with reason TOO_WIDE_TO_RESOLVE. This keeps the desk's minimum sample rule.
- A cell with no scored row, or whose bootstrap leaves too few usable replicates to form an interval, is CANNOT_TELL with reason NO_INTERVAL_FORMABLE.
- A cell whose interval holds the stated level, which the plan called "stated level inside but too wide" and also CONSISTENT when narrow, is CANNOT_TELL with reason STRADDLES_EDGE.
- A known-good gate that fails turns every cell into CANNOT_TELL with reason NO_INTERVAL_FORMABLE, because no trusted interval can be formed.
- A row with a quantile missing, out of order or not a number, or a reported value that is not a number, is CANNOT_TELL with reason NO_INTERVAL_FORMABLE. The desk's own words for these, unreadable, stay in the feed as detail.
- A row on the first-reported side whose earliest release came more than 14 days after the week, the plan's "no early release", is CANNOT_TELL with reason NO_INTERVAL_FORMABLE, because no first-reported value exists from which a reading can be formed.
- A row with no reported value yet stays NOTHING_RETURNED. That is a status of the read of the source. It is never an outcome of a cell or a headline, it is listed apart, and it is outside the numerator and denominator.

## Counts beside every headline
Beside every cell the feed and the page carry REQ-13 counts, the number of NOTHING_RETURNED rows and the share of CANNOT_TELL rows split by reason. Cell readings carry their reason beside the word.

## What the new rule does to the first readings
The cells that read CONSISTENT under the earlier rule now read CANNOT_TELL with reason STRADDLES_EDGE. Cells that read ABOVE or BELOW stay. The headline cell, all horizons at 95 percent on the final side, stays BELOW.
