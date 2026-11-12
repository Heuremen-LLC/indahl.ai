# CHANGE: plan addendum for Faults and Guards 2.0 (12 Nov 2026)

Written on 12 Nov 2026 before any new reading. It moves the outcome rule of item 4 of PLAN.md, the test of whether a stated shutdown date holds, onto section 6 of Faults and Guards 2.0. The descriptive tables carry no outcome and are not changed.

1. Size that matters. The share of tested rows not HELD is read against zero, the claim that a stated date holds. The size that matters is 0.10, the ABOVE bound of the plan. The direction is above zero only.
2. Band and edge. The band is [0, 0.05), open at the upper end, as in the plan's "upper end is below 0.05". The dead zone from 0.05 to 0.10 is closed. ABOVE needs the lower end to be at or above 0.05, and 0.10 is used as the size in the both-alternatives test.
3. Interval. Wilson at 95 percent on the share not HELD, as in the plan.
4. Decision order is section 6.4.
5. Mapping of the desk's own CANNOT_TELL causes.
   a. Fewer than 30 rows in the test is TOO_WIDE_TO_RESOLVE. This is the plan's minimum sample, which is where the desk starts, and an interval from so few rows holds both zero and 0.10 or, where it does not, is still below the plan's floor.
   b. No row in the test (a zero denominator) is NO_INTERVAL_FORMABLE.
   c. An interval that touches the band edge without holding both zero and 0.10 is STRADDLES_EDGE.
6. Failed reads. A failed fetch of a source page, a parser that no longer reads its saved fixtures, or a parse that returns fewer than 80 percent of the previous rows stops the pass and publishes nothing, as the plan says. A published summary therefore carries 0 NOTHING_RETURNED. The count is printed anyway. NOTHING_RETURNED is never an outcome.
7. REQ-13. Beside the test headline the page prints the count of NOTHING_RETURNED and the share of CANNOT_TELL split by reason.
8. The feed carries a reason beside the test outcome and a req13 block.

Data, sources, tests, known-good controls, hand checks and cadence are unchanged. Only the outcome rule changes, and only for readings made after this date. The original PLAN.md is not edited. Earlier recorded outcomes stand under the rules they named.