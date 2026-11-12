# REVISE: plan addendum for Faults and Guards 2.0

Dated 12 November 2026. Written before any reading under the new outcome rule. PLAN.md is not edited.

## What changes and what does not
Only the outcome rule changes, to the reading outcomes of section 6 of Faults and Guards 2.0. Data, sources, collectors, windows, tests, the known-good, the hand check and the stated 122 thousand are unchanged. Earlier recorded outcomes stand under the rules they named. The read of 10 November 2026 recorded the third-release count as CONSISTENT and that record is kept. From this date the same counts are also read under 2.0 and the two readings are shown side by side in the record.

## What the plan names, as the addendum reads it
Quantity: the share of months in which a later release moved by more than 122 thousand from the first estimate, for the third release and for the benchmarked value.
Figure: 0.10. The plan expects a share of about 0.10 if the stated interval described the revision. This is a point figure. The plan names no tolerance. Its width of 0.12 is a cap on the interval and is not an equivalence margin, and this addendum does not invent a tolerance now, since that would be a rule written after the data.
Reading: bound 0.10 with no band. ABOVE if the lower end of the interval is above 0.10. BELOW if the upper end is below 0.10. Otherwise CANNOT_TELL with reason STRADDLES_EDGE. CONSISTENT is not available for this figure.
Size that matters: none. The plan reads a point figure and not a departure from a null, so the both-alternatives test is not applied. TOO_WIDE_TO_RESOLVE is therefore not used by this desk.
Edge convention: closed. An interval whose lower end equals 0.10 is not ABOVE and reads CANNOT_TELL STRADDLES_EDGE.

## Interval methods and levels (unchanged, now named in one place)
Plan reading: Wilson interval at 95 percent over months, each month one unit, 120 months per count.
Reading beside it: percentile bootstrap over calendar years, 4,000 resamples, seed 7, 95 percent. It was defined after the first read and keeps that label. It is read with the same bound and the same edge.

## Mapping of the desk's own causes of CANNOT_TELL
A count with no qualifying months, or a bootstrap with fewer than two calendar years, has no interval and reads CANNOT_TELL with reason NO_INTERVAL_FORMABLE. An interval that overlaps 0.10 reads CANNOT_TELL with reason STRADDLES_EDGE. A failed gate stops the pass and publishes nothing, so no outcome is printed for it.
A failed read of the BLS table or of the flat file is NOTHING_RETURNED. It is a status of the read, is listed apart and is outside numerator and denominator of every share. At the time of this addendum each read returned.

## REQ-13 beside each count
Each count carries a block that prints the number of NOTHING_RETURNED reads and the share of CANNOT_TELL among the two readings printed for that count (the plan's interval over months and the interval over calendar years), split by reason.

## What this does to the recorded readings
Third release against first, 13 of 120, Wilson [0.0644, 0.1766]: recorded CONSISTENT, reads CANNOT_TELL with reason STRADDLES_EDGE under 2.0, because 0.10 is a point figure with no tolerance.
Benchmarked value against first, 25 of 120, Wilson [0.1453, 0.2895]: ABOVE, unchanged.
Both readings on the interval over calendar years read CANNOT_TELL with reason STRADDLES_EDGE, as before.
