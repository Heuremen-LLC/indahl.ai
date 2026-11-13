# FEDSEP: plan addendum for Faults and Guards 2.0

Dated 12 November 2026. Written before any reading under the new outcome rule. PLAN.md is not edited.

## What changes and what does not
Only the outcome rule changes, to the reading outcomes of section 6 of Faults and Guards 2.0. Data, sources, collectors, the September Summaries read, the scoring of inside and outside, the known-good and the hand check are unchanged. Earlier recorded outcomes stand under the rules they named. The read of 10 November 2026 recorded the pooled next-year row, the sensitivity next-year row and three this-year per-variable rows as CONSISTENT, and those records are kept. From this date the same rows are also read under 2.0 and the two readings are shown side by side in the record.

## What the plan names, as the addendum reads it
Quantity: the share of projections whose outcome fell outside the range the Fed states, pooled over four variables for each horizon, and per variable and horizon.
Figure: 0.30. The plan expects about 30 percent outside if the stated 70 percent range described what happened. This is a point figure. The plan names no tolerance. The width cap of 0.45 is a cap on the interval and is not an equivalence margin, and this addendum does not invent a tolerance now, since that would be a rule written after the data. The plan's own Note 3 already said that the cap lets a row read CONSISTENT from an interval of 0.05 to 0.48.
Reading: bound 0.30 with no band. ABOVE if the lower end of the interval is above 0.30. BELOW if the upper end is below 0.30. Otherwise CANNOT_TELL with reason STRADDLES_EDGE. CONSISTENT is not available for this figure.
Size that matters: none. The plan reads a point figure and not a departure from a null, so the both-alternatives test is not applied. TOO_WIDE_TO_RESOLVE is therefore not used by this desk.
Edge convention: closed. An interval whose end equals 0.30 is not ABOVE or BELOW and reads CANNOT_TELL STRADDLES_EDGE.
The sensitivity rows (federal funds rate scored at the year-end target midpoint) are read by the same rule and keep their label as defined after the first read.

## Interval methods and levels (unchanged, now named in one place)
Pooled rows: percentile bootstrap over September years, 4,000 resamples, seed 7, 95 percent, the four variables of one year kept together. The one random stream seeded 7 is shared by the four pooled rows in the order the code draws them, and that order is part of the reading.
Per variable rows: Wilson interval at 95 percent, each year one unit.

## Mapping of the desk's own causes of CANNOT_TELL
An interval that overlaps 0.30 reads CANNOT_TELL with reason STRADDLES_EDGE. A row with no triples or fewer than two years has no interval and reads CANNOT_TELL with reason NO_INTERVAL_FORMABLE. The plan sets no minimum sample, so no row is sent to TOO_WIDE_TO_RESOLVE on size. A failed gate stops the pass and publishes nothing.
Triples that cannot be scored (no median in the page, no stated range for the federal funds rate in 2015 and 2016, outcome not yet available for next-year projections of 2026) are the plan's NOT_COMPARABLE class. They are listed apart with their reasons, are outside the numerator and denominator of every share, and are not counted as readings. They are not failed reads and are not NOTHING_RETURNED.
A failed read of a source (a page, the minutes file or an agency series) is NOTHING_RETURNED, listed apart. The pass stops on a failed gate, so at the time of this addendum each read returned.

## REQ-13 beside each headline share
Each pooled and per variable row carries a block that prints the number of NOTHING_RETURNED reads and the share of CANNOT_TELL among the readings of that row, split by reason, and the count of triples not comparable. The summary carries one block over all pooled and per variable readings.

## What this does to the recorded readings
Pooled next year, 10 of 37, [0.0811, 0.4872]: recorded CONSISTENT, reads CANNOT_TELL with reason STRADDLES_EDGE.
Sensitivity next year (funds rate at year-end), and the per variable rows for the GDP, PCE inflation and funds rate this year: recorded CONSISTENT, read CANNOT_TELL with reason STRADDLES_EDGE. The final counts are in the summary and in the ledger check entry.
Pooled this year, 6 of 41, [0.0256, 0.275]: BELOW, unchanged.
