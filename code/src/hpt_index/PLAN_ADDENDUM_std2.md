# HPT: plan addendum for Faults and Guards 2.0 (12 Nov 2026)

Written on 12 Nov 2026 before any new reading. It moves the outcome rule of PLAN.md onto section 6 of Faults and Guards 2.0. It applies to the three steps of the read.

1. Size that matters. The share DISAGREE among AGREE plus DISAGREE is read against zero, the claim. The size that matters is 0.10, the ABOVE bound of PLAN.md. The direction is above zero only.
2. Band and edge. The band is [0, 0.05), open at the upper end, which is the plan's own wording "upper end is below 0.05". The plan's two bounds left a dead zone from 0.05 to 0.10 where a resolved share printed CANNOT_TELL. The dead zone is closed. ABOVE now needs the lower end of the interval to be at or above 0.05, and 0.10 is used only as the size in the both-alternatives test. CONSISTENT needs the whole interval inside the band.
3. Interval. Wilson at 95 percent on DISAGREE among AGREE plus DISAGREE, as in PLAN.md. No resampling.
4. Decision order is section 6.4. No interval, then the both-alternatives test, then ABOVE, BELOW or CONSISTENT, then STRADDLES_EDGE. BELOW cannot occur against a band that starts at zero.
5. How the desk's own CANNOT_TELL causes map to the closed reasons.
   a. Fewer than 30 comparable domains in a step is TOO_WIDE_TO_RESOLVE. The minimum sample is the plan's and the interval at that size cannot separate zero from 0.10.
   b. No comparable domain in a step (a zero denominator) is NO_INTERVAL_FORMABLE.
   c. A failed known-good gate is NO_INTERVAL_FORMABLE for every step, because the reader is not trusted to form a reading.
   d. Step 1, a cms-hpt.txt at the root. Addendum 1 of PLAN.md fixed this step as CANNOT_TELL because the Wikidata population holds clinics and parts of systems whose file sits on another domain. The planned quantity, the share of hospital websites with no file at the root, cannot be formed from a population that holds non-subjects. The step is therefore NO_INTERVAL_FORMABLE and the page says why. The interval is still printed with its counts. The interval rule is not applied to this step, so the outcome is not a finding that the interval straddles anything.
   e. An interval that touches the band edge without holding both zero and 0.10 is STRADDLES_EDGE.
6. Failed reads. A failed read of a domain is NOTHING_RETURNED and is listed apart from the readings. Outside the numerator and the denominator of every share, as before. For this desk a domain is NOTHING_RETURNED in a step when no usable answer came back: the site could not be reached, a server error of HTTP 500 or higher, or a redirect that could not be followed. A refusal with HTTP 400, 401, 403 or 429 is an answer. It stays NOT_COMPARABLE as the plan says and is counted apart. Websites that are a page on a shared site were not read and are NOT_COMPARABLE. Step 3 rows that are JSON or zip are NOT_COMPARABLE by the plan and are not failed reads. NOTHING_RETURNED is never an outcome of a headline.
7. REQ-13. Beside every step headline the page prints the count of NOTHING_RETURNED and the share of CANNOT_TELL split by reason, from the kit's req13 function.
8. The feed carries a reason beside every outcome and a req13 block on every step.

Data, sources, tests, known-good controls, hand checks and cadence are unchanged. Only the outcome rule changes, and only for readings made after this date. The original PLAN.md is not edited. Earlier recorded outcomes stand under the rules they named.