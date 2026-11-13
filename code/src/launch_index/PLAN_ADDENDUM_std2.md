# LAUNCH: plan addendum for Faults and Guards 2.0 (12 Nov 2026)

Written on 12 Nov 2026 before any new reading. It moves the outcome rule of PLAN.md onto section 6 of Faults and Guards 2.0.

1. Size that matters. The share of scored launches that slipped more than 24 hours is read against zero, the stated time being the claim. The size that matters is 0.25, the ABOVE bound of the plan, a launch that slips more than a quarter of the time. The direction is above zero only.
2. Band and edge. The band is [0, 0.10), open at the upper end, as in the plan's "upper bound below 0.10". The plan's two bounds left a dead zone from 0.10 to 0.25. The dead zone is closed. ABOVE needs the lower end of the interval to be at or above 0.10, and 0.25 is used as the size in the both-alternatives test. CONSISTENT needs the whole interval inside the band.
3. Interval. Wilson at 95 percent on the share slipped more than 24 hours, as in the plan.
4. Decision order is section 6.4.
5. Scope. The plan states its outcome rule at the 7 day lead and prints the 1 day and 30 day leads without one. The code printed a bare CANNOT_TELL on those cells. A bare CANNOT_TELL has no closed reason, so the same rule is applied at every lead and for every provider cell. The 7 day lead stays the cell the plan names.
6. Mapping of the desk's own CANNOT_TELL causes.
   a. Fewer than 30 scored launches in a cell is TOO_WIDE_TO_RESOLVE. This is the plan's floor. The audit notes that the 7 day cell would otherwise read ABOVE on its interval alone. The floor decides first and the cell stays CANNOT_TELL.
   b. No scored launch (a zero denominator) is NO_INTERVAL_FORMABLE and the cell is not printed, as before.
   c. An interval that touches the band edge without holding both zero and 0.25 is STRADDLES_EDGE.
7. Failed reads. A list read of the launch API that returns nothing is NOTHING_RETURNED. The feed counts the failed list reads of the run that made it, listed apart from the readings. Launches that never flew, cancelled or still waiting are states and are counted apart as before. NOTHING_RETURNED is never an outcome.
8. REQ-13. Beside the headline cells the page prints the NOTHING_RETURNED count and the share of CANNOT_TELL split by reason.
9. The feed carries a reason beside every outcome and a req13 block on every cell.

Data, sources, tests, known-good controls, hand checks and cadence are unchanged. Only the outcome rule changes, and only for readings made after this date. The original PLAN.md is not edited. Earlier recorded outcomes stand under the rules they named.