# FORECAST: plan addendum for Faults and Guards 2.0 (12 November 2026)

This addendum changes only the outcome rule. The data, the sources, the stations, the bins, the leads, the event rules (the NWS rule is primary and the original committed rule is kept beside it), the one count per period per cell and the Wilson 95 percent interval are unchanged. PLAN.md is not edited. Every outcome recorded earlier stands under the rules it named. This addendum is written before any reading under the new rule.

## The figure and the tolerance
Each cell is read against its mean stated chance, a point figure. The plan named no tolerance and none is named now, because a tolerance written after the data would be a rule written after the data. A point figure with no tolerance has no two-sided band, so CONSISTENT is not available. A cell reads ABOVE when the whole Wilson interval lies above the mean stated chance, BELOW when it lies wholly below, and otherwise CANNOT_TELL with reason STRADDLES_EDGE. The edges are closed, so an interval that touches the mean stated chance straddles it.

## The size that matters
None is named. The both-alternatives test is not applied and no cell reads TOO_WIDE_TO_RESOLVE from it. A plan that names a size that matters before a read can add one in a new addendum.

## Interval method
Unchanged. The Wilson interval at 95 percent over the periods in the cell, as named in PLAN.md. The plan says the periods are not independent events, and the interval is read with that in mind.

## How the desk's own causes of CANNOT_TELL map to the closed reasons
- A cell with fewer than 30 periods is CANNOT_TELL with reason TOO_WIDE_TO_RESOLVE. The interval of so few periods is read as too wide to separate the stated chance from a departure, and the desk's minimum sample rule is kept as it was.
- A cell with no periods has no interval and is CANNOT_TELL with reason NO_INTERVAL_FORMABLE.
- A cell whose interval touches or holds the mean stated chance is CANNOT_TELL with reason STRADDLES_EDGE.

## Counts beside every headline
Beside each table the page prints the count of NOTHING_RETURNED and the share of CANNOT_TELL split by reason (REQ-13). A failed read of a source is a status of the read and is outside the numerator and the denominator. Periods that are unscorable, waiting for the archive, with no stated chance or in no cell are counted apart as before and are not readings of a cell.

## What the new rule does to the first readings
The cells that read CONSISTENT under the earlier rule, the stated chance inside the interval at any width, now read CANNOT_TELL with reason STRADDLES_EDGE. Cells that read ABOVE or BELOW stay. The earlier rule's outcomes are kept in the record as recorded.
