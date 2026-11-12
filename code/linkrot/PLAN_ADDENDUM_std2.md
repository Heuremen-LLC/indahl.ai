# LINKROT: plan addendum for Faults and Guards 2.0 (12 Nov 2026)

Written on 12 Nov 2026 before any new reading. It moves the outcome rules of PLAN.md (links that resolve) and PLAN_REPOS.md (repositories that hold code) onto section 6 of Faults and Guards 2.0. The samples beside arXiv under early/, the landmark read and the own-name read print state shares with no outcome and are not changed.

1. Size that matters. For PLAN.md the rot share is read against zero, the claim that the link leads there. For PLAN_REPOS.md the empty-repository share is read against zero, the claim that code is there. In both the size that matters is 0.10, the ABOVE bound of the plan. The direction is above zero only.
2. Band and edge. The band is [0, 0.05), open at the upper end, as in the plans' "upper end is below 0.05". The dead zone from 0.05 to 0.10 is closed. ABOVE needs the lower end of the interval to be at or above 0.05, and 0.10 is used as the size in the both-alternatives test. CONSISTENT needs the whole interval inside the band.
3. Interval. Wilson at 95 percent, as in both plans. The median interval of the early samples is not an outcome and is not changed.
4. Decision order is section 6.4.
5. Mapping of the desk's own CANNOT_TELL causes.
   a. Fewer than 30 readable links in a cohort (PLAN.md) or fewer than 30 repositories (PLAN_REPOS.md) is TOO_WIDE_TO_RESOLVE.
   b. A cohort with none readable (a zero denominator) is NO_INTERVAL_FORMABLE.
   c. A failed known-good gate, in a link pass or in the repository pass, is NO_INTERVAL_FORMABLE for every cohort. The plans say the pass is CANNOT_TELL for every cohort and the reader is not trusted to form a reading.
   d. An interval that touches the band edge without holding both zero and 0.10 is STRADDLES_EDGE.
6. Failed reads. For links, a link that reads BLOCKED or TIMEOUT returned no answer on whether it leads there. These are the plan's own classes. They are counted apart, never rot and outside every numerator and denominator, and they are the NOTHING_RETURNED count of the headline. For repositories, a repository the API cannot find reads NOT_FOUND, is not counted in the share and is the NOTHING_RETURNED count. A batch with no reply is not stored and is read again at the next tick. A link that was LIVE in one seat and GONE or DNS_FAIL in the other reads BLOCKED, as Addendum 2 of PLAN.md says, and counts as NOTHING_RETURNED. NOTHING_RETURNED stays its own column in the early samples. It is never an outcome.
7. REQ-13. Beside every headline share the page prints the NOTHING_RETURNED count and the share of CANNOT_TELL split by reason.
8. The feed carries a reason beside every outcome and a req13 block on every headline cell.

Data, sources, tests, known-good controls, hand checks and cadence are unchanged. Only the outcome rule changes, and only for readings made after this date. The original PLAN.md and PLAN_REPOS.md is not edited. Earlier recorded outcomes stand under the rules they named.