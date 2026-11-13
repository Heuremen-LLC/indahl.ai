# STEO: plan addendum for Faults and Guards 2.0 (12 November 2026)

This addendum changes only the outcome rule. The data, the sources, the archive copies, the frame, the rows, the known-good gates and the tests are unchanged. PLAN.md and its Addendum 1 are not edited and the hash seal stands. Every outcome recorded earlier stands under the rules it named. This addendum is written before any reading under the new rule.

## What is read against what
Each cell is read against 0.95, the level EIA states for its interval. It is a point figure and the plan named no tolerance. None is named now, because a tolerance written after the data would be a rule written after the data. The width cap of 0.15 is not a tolerance and no longer decides an outcome. CONSISTENT is not available for a cell. A cell reads BELOW when the whole interval lies below 0.95, ABOVE when it lies wholly above, and otherwise CANNOT_TELL with reason STRADDLES_EDGE. The edges are closed. This applies to the plan's reading and to the Addendum 1 reading alike. The Addendum 1 reading stays labelled as decided after the data.

## The size that matters
None is named. The both-alternatives test is not applied. A later addendum can name one before a read.

## Rows
A row is an exact read of a monthly average spot price against two published bounds, with no sampling, so its interval has zero width. A row reads ABOVE when the price is above the upper bound, BELOW when it is below the lower bound, and CONSISTENT when it lies between them, edges included. This is the band [Lower, Upper] and it is unchanged. It is a row label that feeds the cell, not a reading of the cell.

## Interval method
Unchanged. A moving-block bootstrap over outcome months, blocks of 12 consecutive months, 2,000 replicates, seed 20261110, 95 percent, percentile of the replicate shares. The desk keeps its own bootstrap, because the kit's bootstrap draws from a different generator and would not reproduce the stored intervals. The method, the block length, the seed and the draws are the same as before.

## How the desk's own causes of CANNOT_TELL map to the closed reasons
- A cell with fewer than 30 scored rows or fewer than 24 distinct outcome months is CANNOT_TELL with reason TOO_WIDE_TO_RESOLVE. This keeps the desk's minimum sample rule.
- A cell with no scored row, or whose bootstrap leaves too few usable replicates to form an interval, is CANNOT_TELL with reason NO_INTERVAL_FORMABLE.
- A cell whose interval holds 0.95, which the plan called CONSISTENT when narrow and otherwise CANNOT_TELL, is CANNOT_TELL with reason STRADDLES_EDGE.
- A known-good gate that fails turns every cell into CANNOT_TELL with reason NO_INTERVAL_FORMABLE, because no trusted interval can be formed.
- A row whose Lower or Upper is not a number, whose Lower is above its Upper, or whose sheet has no level of 0.95 is CANNOT_TELL with reason NO_INTERVAL_FORMABLE. The desk's own word for it, unreadable, stays in the feed as detail.
- A row whose issue is unknown, with no note date, no release after it, or a copy made before the release it maps to, is CANNOT_TELL with reason NO_INTERVAL_FORMABLE, because the statement cannot be dated and no reading can be formed. The desk's own words, issue unknown, stay as detail.
- A row with no spot price yet for its month stays NOTHING_RETURNED. That is a status of the read of the source. It is never an outcome of a cell or a headline, it is listed apart, and it is outside the numerator and denominator.

## Counts beside every headline
Beside every cell the feed and the page carry REQ-13 counts, the number of NOTHING_RETURNED rows and the share of CANNOT_TELL rows split by reason. Cell readings carry their reason beside the word.

## What the new rule does to the first readings
The cells that read CONSISTENT under the earlier rule now read CANNOT_TELL with reason STRADDLES_EDGE. Cells that read ABOVE or BELOW stay. The primary WTI all-leads headline stays CANNOT_TELL, now with its reason.
