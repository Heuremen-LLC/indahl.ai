# SUPPORT: plan addendum for Faults and Guards 2.0 (12 Nov 2026)

Written on 12 Nov 2026 before any new reading. It moves the outcome rule of PLAN.md onto section 6 of Faults and Guards 2.0. It applies to the all-cycles headline, the two product-level shares of Addendum 2 and the by-product cells.

1. Size that matters. The share of tested supported cycles that are unreleased is read against zero, the claim that a supported cycle is still being released. The size that matters is 0.10, the ABOVE bound of the plan. The direction is above zero only.
2. Band and edge. The band is [0, 0.05), open at the upper end, as in the plan's "upper end is below 0.05". The plan's two bounds left a dead zone from 0.05 to 0.10, and the product row "every tested supported cycle is unreleased" sits in it. The dead zone is closed. ABOVE needs the lower end of the interval to be at or above 0.05, and 0.10 is used as the size in the both-alternatives test. CONSISTENT needs the whole interval inside the band.
3. Interval method. The all-cycles headline keeps the bootstrap over products of Addendum 2, 4,000 resamples of whole products, seed 7, 95 percent, percentile interval, and the Wilson interval stays printed beside it. Every other cell keeps the Wilson 95 percent interval of the plan. The product-level shares stay labelled as defined after the first read.
4. Decision order is section 6.4.
5. Mapping of the desk's own CANNOT_TELL causes.
   a. Fewer than 30 units tested in a cell is TOO_WIDE_TO_RESOLVE. The unit is the cycle for the all-cycles headline and the by-product cells, and the product for the two product-level shares. This is the plan's minimum sample.
   b. No unit tested (a zero denominator) is NO_INTERVAL_FORMABLE.
   c. A failed known-good gate is NO_INTERVAL_FORMABLE for every cell.
   d. An interval that touches the band edge without holding both zero and 0.10 is STRADDLES_EDGE.
6. Failed reads. A product whose request returns no cycle record is NOTHING_RETURNED. The code counts it in the field no_cycles and cannot tell a failed request from an empty list, so both are counted there, apart from the readings and outside every numerator and denominator. Cycles counted apart as not tested (no release date, end of life with no date, support ended, too new) are states of a cycle and not failed reads. NOTHING_RETURNED is never an outcome.
7. REQ-13. Beside every headline share the page prints the NOTHING_RETURNED count and the share of CANNOT_TELL split by reason.
8. The feed carries a reason beside every outcome and a req13 block on every headline cell.

Data, sources, tests, known-good controls, hand checks and cadence are unchanged. Only the outcome rule changes, and only for readings made after this date. The original PLAN.md is not edited. Earlier recorded outcomes stand under the rules they named.