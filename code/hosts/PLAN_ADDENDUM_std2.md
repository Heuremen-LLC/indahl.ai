# HOSTS plan addendum: outcome rule under Faults and Guards 2.0. Dated 12 Nov 2026, written before any reading under the new rule.

This addendum changes only how an interval is turned into an outcome word. The data, the sources, the endpoint parser, the 2 percentage point agreement test, the 100 poll and 10 percent absence limits, the Wilson 95 percent interval and the known-good checks are unchanged. Outcomes recorded earlier stand under the rules they named at the time, including the earlier readings of ABOVE. A reading made after this addendum is a new reading under the new rule.

## The size that matters, the band and the edge
The plan states ABOVE if the lower end is above 0.05 and CONSISTENT if the upper end is below 0.15, the same two numbers as worked example 6.8 of the standard. It did not say which one is the size that matters. This addendum decides it.
- The size that matters is 0.05, the share of endpoints whose stated one-day uptime disagrees with our own record that the plan treats as a departure from zero. The null is 0.
- The band is [0, 0.15), open at the upper edge, as the plan says the upper end is below 0.15.
- The edge convention is '[)'.
- CONSISTENT needs the interval to sit inside the band and not to reach both 0 and 0.05. ABOVE needs the lower end at or above 0.15. An interval with its lower end between 0.05 and 0.15 and its upper end below 0.15 reads CONSISTENT, and one that reaches 0.15 reads CANNOT_TELL with reason STRADDLES_EDGE. Under the old rule these read ABOVE.

## Interval method
Wilson at 95 percent over endpoints, one unit per endpoint, as in the plan. No resampling, so no draws and no seed.

## How the desk's own causes of CANNOT_TELL map to the reasons
- An interval that reaches both 0 and 0.05: TOO_WIDE_TO_RESOLVE.
- An interval that overlaps the band edge 0.15 without that: STRADDLES_EDGE.
- No endpoint comparable, which the plan called NOTHING_RETURNED until 24 hours of polls exist or while no span of 100 polls exists: CANNOT_TELL with reason NO_INTERVAL_FORMABLE.
- The row labels NOT_COMPARABLE, AGREE and DISAGREE are not outcomes. Endpoints that are NOT_COMPARABLE are left out of the numerator and the denominator and keep their label.

## Failed reads
A model whose endpoint list could not be fetched in a poll is a failed read. It is stored as the poll's failed list, is outside the numerator and the denominator, and is counted as NOTHING_RETURNED beside the headline. The word NOTHING_RETURNED is a status and is never printed as the outcome of the headline. REQ-13 is printed beside the headline: the count of failed reads and the share of CANNOT_TELL split by reason.

## Display
The counts, the list of flagged endpoints and the quantization table have no outcome and are unchanged.
