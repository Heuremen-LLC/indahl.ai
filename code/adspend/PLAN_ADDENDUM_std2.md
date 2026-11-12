# ADSPEND: plan addendum for Faults and Guards 2.0, 12 November 2026

This addendum is written before any reading under the new outcome rule. PLAN.md and its seven addenda are not edited. The sources, the matching, the Google band, the FEC side, the size that matters, the band factor, the known-good checks and every decided outcome are unchanged. Only the way a cannot tell is named, the status of Nothing returned and the counts beside the headline change. Outcomes recorded earlier stand under the rules they named.

## What the plan already names
The plan names the size that matters, at least 1,000 dollars and at least 10 percent of the Google bound, and the band, a Google band that spans at most a factor of two. It tests both alternatives on every row. The interval is interval arithmetic on stated and filed bounds, with no sampling, so there is no level, no draw and no seed. Each decided row is an exact read of filed amounts against a stated bound. Above and below keep their gap-against-size tests, which are a size rule and not a point inside an interval, so the rule stays in its own function and is not replaced by the kit's read. Consistent keeps its two-sided band.

## Nothing returned is no longer an outcome
The plan's outcome Nothing returned marks a row where Google states spend in the window and the FEC files hold no Schedule B row, no Schedule E row and no summary record. The read of the FEC files succeeded and found no figure, so no interval can be formed on the delivered side. Such a row is CANNOT_TELL with reason NO_INTERVAL_FORMABLE, and the plain cause stays beside the code. The status NOTHING_RETURNED is kept for a failed read of a source, and the desk has none when its gates pass, so the count printed beside the headline is zero. Rows read as Nothing returned before are counted in the CANNOT_TELL share and in its denominator from now on.

## How the desk's own causes of CANNOT_TELL map
- Scope, a committee type that files no operating expenditures: NO_INTERVAL_FORMABLE.
- Cycle, a committee not registered or whose candidate did not run in that cycle: NO_INTERVAL_FORMABLE.
- Nothing, and name only with nothing: NO_INTERVAL_FORMABLE.
- No Google spend listed in the window: NO_INTERVAL_FORMABLE.
- Estimates, unseen, agency, purpose and name: STRADDLES_EDGE, because the reading depends on money or rows that could put it on either side of an edge.
- Near, outside the band by less than the size that matters: STRADDLES_EDGE.
- Band, a timing band wider than a factor of two: TOO_WIDE_TO_RESOLVE, because the band is wider than the plan allows a reading to be.
- A failed known-good gate: NO_INTERVAL_FORMABLE for every row, with the original beside it.

## Counts beside the headline
The headline is the count of cycle rows that read above, below or consistent on the robust rule, out of all cycle rows. Beside it the page prints the REQ-13 line: the NOTHING_RETURNED count, then the CANNOT_TELL share split by reason.

## What flips
No decided outcome changes. The rows that read Nothing returned, 24 in the reading of 10 November, read CANNOT_TELL with reason NO_INTERVAL_FORMABLE. The CANNOT_TELL count rises by that number.
