# AILUMINATE plan addendum: outcome rule under Faults and Guards 2.0. Dated 12 Nov 2026, written before any reading under the new rule.

This addendum changes only how an interval is turned into an outcome word. The data, the sources, the parsers, the tests A to J, the Wilson 95 percent interval and the known-good checks are unchanged. Outcomes recorded earlier stand under the rules they named at the time. A reading made after this addendum is a new reading under the new rule and is printed beside the earlier one, it does not replace it.

## The size that matters, the band and the edge
The plan states ABOVE if the lower end is above 0.05 and CONSISTENT if the upper end is below 0.15. The two numbers do not agree, and 0 of 27 has an upper end of 0.125. The plan did not say which number is the size that matters. This addendum decides it, as in worked example 6.8 of the standard.
- The size that matters for tests A, B, F, H and I is 0.05, the share of a stated event that the plan treats as a departure from zero. The null is 0.
- The band is [0, 0.15). It is open at the upper edge, because the plan says the upper end is below 0.15.
- The edge convention is '[)'.
- A CONSISTENT reading therefore needs the interval to sit inside [0, 0.15) and not to reach both 0 and 0.05. With 27 systems that means 0 events gives an interval that reaches both, so it reads CANNOT_TELL with reason TOO_WIDE_TO_RESOLVE. CONSISTENT would need an upper end below 0.05, which takes 0 events in 73 or more units. A plan that wanted 0.15 as the size that matters would have had to say so before the read.
- ABOVE needs the lower end at or above 0.15, the band edge. An interval with its lower end between 0.05 and 0.15 and its upper end below 0.15 reads CONSISTENT, and one with its upper end at or above 0.15 reads CANNOT_TELL with reason STRADDLES_EDGE. Under the old rule both would have read ABOVE. No reading has been in that range under this addendum.

## Test G, share up among pairs that moved
The null is 0.5. The band is [0.35, 0.65], both edges closed, as the plan states. The size that matters is 0.15 in either direction, the distance from 0.5 to a band edge, because the plan names no other size. ABOVE needs the lower end above 0.65. BELOW needs the upper end below 0.35. CONSISTENT needs the interval inside [0.35, 0.65] and not reaching both 0.5 and an edge. The old ABOVE at 0.5 and BELOW at 0.5 are replaced by these. Fewer than 30 pairs that moved is CANNOT_TELL with reason TOO_WIDE_TO_RESOLVE, the plan's own minimum sample.

## Interval method
Wilson at 95 percent over the units named in each test. No resampling, so no draws and no seed.

## How the desk's own causes of CANNOT_TELL map to the reasons
- An interval that reaches both the null and the size that matters: TOO_WIDE_TO_RESOLVE.
- An interval that overlaps a band edge without that: STRADDLES_EDGE.
- Fewer than 30 pairs that moved in G: TOO_WIDE_TO_RESOLVE.
- A test that cannot be computed yet, meaning no systems compared in A, no system read twice in B, F or H, no system read under two label tuples in G, and only one label tuple seen in I: CANNOT_TELL with reason NO_INTERVAL_FORMABLE, with the sentence that says why kept beside it. These readings used to carry the outcome word NOTHING_RETURNED, which is not an outcome.

## Failed reads
A system on the page with no readable report, or a report with no page row, is a failed read. It keeps its row status NOTHING_RETURNED, is listed apart, and is outside the numerator and the denominator. A report with no readable label line is counted as unreadable and left out, as in the drift addendum. The count of failed reads is printed beside every headline with the share of CANNOT_TELL split by reason, as REQ-13 requires.

## Tests B and J
Test B is a share of systems and follows the rule above. Test J has no outcome and is unchanged. Tests C, D and E have no outcome and are unchanged.
