# CENSUS: plan addendum for Faults and Guards 2.0, 12 November 2026

This addendum is written before any reading under the new outcome rule. PLAN.md is not edited and its seal is unchanged. The data, the sources, the collectors, the known-good gates and the row rule are unchanged. Only the outcome rule of a cell and the way a cannot tell is named change. Outcomes recorded earlier stand under the rules they named.

## What is read
The reading is the share of scored rows in a cell where the later value sits inside the 90 percent interval stated for the first print. The figure it is read against is 0.90. The plan names no tolerance around 0.90 and no size that matters, and none is invented now, because that would be a rule written after the data.

## Cell rule
- Interval: Wilson, 95 percent, over the scored rows of the cell, as in PLAN.md. No resampling, so no draws and no seed.
- The figure 0.90 is a point figure with no tolerance. The cell is read with heuremen_kit read(lo, hi, bound=0.90), edge closed. It reads ABOVE when the lower end is above 0.90, BELOW when the upper end is below 0.90, and otherwise CANNOT_TELL with reason STRADDLES_EDGE.
- CONSISTENT is not available for a cell. A cell whose interval holds 0.90 therefore reads CANNOT_TELL with reason STRADDLES_EDGE where it read CONSISTENT before.
- The both-alternatives test is not applied, because no size that matters is named for a point figure with no tolerance. The page says so.
- A cell with fewer than ten scored rows keeps the plan's minimum. It reads CANNOT_TELL with reason TOO_WIDE_TO_RESOLVE. A cell with no scored row at all, because no width exists or because the known-good gate failed, reads CANNOT_TELL with reason NO_INTERVAL_FORMABLE. This covers the regions of housing starts and building permits.

## Row rule and the exact read
A row compares one published value with one stated interval. There is no sampling in that read. Under owner decision O1 it is an interval of zero width and is read with heuremen_kit read_exact against the band from the first print minus the stated half-width to the first print plus the stated half-width, edges included as in PLAN.md. Inside is CONSISTENT, above is ABOVE, below is BELOW. A row outcome is a record of one comparison. The share of CONSISTENT rows is the reading, and it is read by the cell rule above.

## How the desk's own causes of CANNOT_TELL map
A row that cannot be compared is CANNOT_TELL with reason NO_INTERVAL_FORMABLE for each of the four causes in PLAN.md. The plain cause is kept beside the code.
- No width: no stated interval exists.
- Missing vintage: the later value does not exist yet.
- Universe break: the later value measures a different universe from the stated interval, so the planned quantity cannot be formed.
- Annual revision in window: the later value is not the revision the interval was stated for, so the planned quantity cannot be formed.
- Gate failed: a known-good gate failed, so no row is read.
None of these has an interval that straddles an edge or is too wide, so none maps to those two reasons.

## Failed reads and the counts beside the headline
A failed fetch or parse of a source is NOTHING_RETURNED, a status of the read. It is never an outcome and the failed reads are listed apart. The desk reads from cached ALFRED files and dated Census copies, so a failed read stops the format gate and is counted here as zero rows read. The headline prints the REQ-13 line for the rows of the four headline cells at the second print: the NOTHING_RETURNED count, then the CANNOT_TELL count split by reason.

## Headline and what flips
The headline cells are the national totals of sales, starts, completions and retail at the second print, with the third print and the current value in the table. Cells that held ABOVE keep ABOVE. The three cells that held 0.90 inside their interval, retail third print and the Northeast sales cells at the third print and the current value, move from CONSISTENT to CANNOT_TELL with reason STRADDLES_EDGE.
