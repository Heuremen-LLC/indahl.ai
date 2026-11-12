# TRIALS plan addendum: outcome rule under Faults and Guards 2.0. Dated 12 Nov 2026, written before any reading under the new rule.

This addendum changes only how an interval is turned into an outcome word. The registry, the query, the collector, the Phase 1 drug-only exclusion, the lag zone, the states POSTED, NO_RESULTS and IN_REVIEW, the Wilson 95 percent interval, the sponsor-clustered interval printed beside it, the reason classes of the stopped-trial block, the hand checks and the known-good records are unchanged. Outcomes recorded earlier stand under the rules they named at the time, including every earlier CANNOT_TELL on a share that sat between the two thresholds. A reading made after this addendum is a new reading under the new rule and is printed beside the earlier one.

## The dead zone and how it is closed
The plan reads ABOVE if the lower end is above 0.25 and CONSISTENT if the upper end is below 0.10. A resolved share between the two, such as the headline share of records with no results on the record, read CANNOT_TELL although its interval was narrow and wholly on one side of 0.10. The new rule has no such range, so the plan has to say which number is the band edge and which is the size that matters. This addendum decides it, as the standard's worked example 6.8 does.
- The size that matters is 0.25, the ABOVE line of the plan. The null is 0.
- The band is [0, 0.10), open at the upper edge, because the plan says the upper end is below 0.10. The band edge is 0.10.
- The edge convention is '[)'.
- ABOVE needs the lower end at or above 0.10. CONSISTENT needs the interval inside [0, 0.10) and not reaching both 0 and 0.25. An interval that reaches both 0 and 0.25 is CANNOT_TELL with reason TOO_WIDE_TO_RESOLVE. An interval that overlaps 0.10 without that is CANNOT_TELL with reason STRADDLES_EDGE.
- The headline share, 4,772 of 22,210 with the interval [0.2095, 0.2203], now reads ABOVE. It no longer reads CANNOT_TELL. That is a consequence of closing the dead zone and of no new data. No cause and no rule of the law is claimed, the reading is the share with no results on the record against a band of 0 to 10 percent.
- Every group of the page, by sponsor class, by product, by completion year and by lead sponsor, is read the same way.

## The stopped-trial tests
The two tests of addendum 3 are read against the registry's own rule that the share should be zero. The plan reads ABOVE if the lower end is above 0.10 and CONSISTENT if the upper end is below 0.05.
- The size that matters is 0.10. The null is 0. The band is [0, 0.05), open at the upper edge. The edge convention is '[)'.
- Fewer than 30 records is CANNOT_TELL with reason TOO_WIDE_TO_RESOLVE, the plan's own minimum.
- A test whose known-good gate failed reads CANNOT_TELL with reason NO_INTERVAL_FORMABLE. The instrument did not pass its own check, so no interval of the claim can be formed.

## Minimum sample of the groups
The plan states no minimum number of records for the groups of the headline rule, only that a lead sponsor is listed with at least 20 records. This addendum states no new minimum, since one written now would be a rule written after the data. A group with no scored record reads CANNOT_TELL with reason NO_INTERVAL_FORMABLE. The page therefore shows small groups such as the registry class Unknown, with 3 records, as the rule reads them, with their counts beside them.

## Interval method
Wilson at 95 percent, one unit per record, as in the plan. The clustered interval is a second interval beside it, defined after the data and still not the one the outcome is read on. No resampling is used for any outcome, so no draws and no seed. The Wilson interval uses its exact ends, 0 for no event and 1 for all events.

## Records that are not readings
A record IN_REVIEW has a results submission with no post date. It is a descriptive class, outside the numerator and the denominator of every share, and it is not a failed read because the registry answered. The lag zone is shown apart and not scored. NOT_POSTED is a row label and not an outcome.

## Failed reads
The collector stops and publishes nothing when the registry does not answer, and the tick publishes nothing when its two known-good records do not read as the plan says. A published read therefore has no failed read, and REQ-13 beside the headline prints 0 NOTHING_RETURNED together with the share of CANNOT_TELL split by reason.
