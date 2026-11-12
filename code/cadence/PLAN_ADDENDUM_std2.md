# CADENCE: plan addendum for Faults and Guards 2.0

Dated 12 November 2026. Written before any reading under the new outcome rule. PLAN.md is not edited.

## What changes and what does not
Only the outcome rule changes, to the reading outcomes of section 6 of Faults and Guards 2.0. Data, sources, portals, the interval table, the two-day floor, the series rule, the parsing rules of Addendum 2 and the side check of download dates are unchanged. Earlier recorded outcomes stand under the rules they named. The plan's per-series words CONSISTENT and BELOW were recorded under its own rule, and those records are kept. Counts of series behind their stated cadence are unchanged.

## What the plan names, as the addendum reads it
Quantity per series: the margin, which is twice the stated interval (at least two days, as the plan fixes) minus the age of the series, in days. The age is the portal file's fetch time minus the series' modified date. Both are published values, so the margin is an exact figure with no sampling. Under owner decision O1 it is an interval of zero width.
Bound: zero margin, a one-sided threshold. The plan states no tolerance for it, so there is no band and no CONSISTENT.
Reading: ABOVE if the margin is above zero, which is a series that has changed within twice its stated interval. BELOW if the margin is below zero, which is a series that has not, so delivered updates fall short of the stated cadence. This keeps the plan's word BELOW for the same series as before. A margin of exactly zero has no outcome word. It is counted apart as at the bound and the signed difference, zero, is printed. It is outside the numerator and denominator of every share.
The plan's old CONSISTENT series read ABOVE under 2.0. The plan's old statement that ABOVE is not assigned no longer holds under the one-sided reading, since a one-sided threshold cannot print CONSISTENT. Whether the plan's two-way word is kept or the bound is read on the age scale instead is the owner's call. This addendum chose the margin scale so that the word BELOW and the share BELOW keep their meaning.
Size that matters: none. The reading is a threshold on an exact figure and not a departure from a null, so the both-alternatives test is not applied and TOO_WIDE_TO_RESOLVE is not used by this desk.
Edge convention: closed. A margin of zero is the bound itself.

## Interval method and level
Per-series reading: no interval, exact figure, zero width (O1).
Share of series BELOW: Wilson interval at 95 percent, each series one unit, as before. The share is descriptive. The plan assigns it no outcome and none is printed.

## Mapping of the desk's own causes of CANNOT_TELL
A cadence word that is not in the interval table, and a missing or unreadable modified date, each leave the margin without a value. The series reads CANNOT_TELL with reason NO_INTERVAL_FORMABLE, because no bound or no age can be formed. The counts of these two causes are kept apart in each portal's output as before, and are also given by closed reason.
A portal whose data.json could not be read is NOTHING_RETURNED. It is a status of the read and is listed apart with its name. It is outside numerator and denominator of every share. At the time of this addendum FEMA is such a portal, as the plan's Note 2 says.

## REQ-13 beside each headline share
Each portal's share and the total across portals carry a block that prints the number of NOTHING_RETURNED portals and the share of series that read CANNOT_TELL, split by reason. The denominator of that share is every series of the portals read, readable or not.
