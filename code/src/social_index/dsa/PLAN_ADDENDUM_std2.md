# DSA: plan addendum for Faults and Guards 2.0, 12 November 2026

This addendum is written before any reading under the new outcome rule. PLAN.md and its dated addenda are not edited. The reports, the database aggregates, the matching, the stated and delivered bands, the known-good checks and the readings defined after the data are unchanged. Only the outcome rule is moved onto the kit's read, and the way a cannot tell is named, the status of Nothing returned and the counts beside the page change. Outcomes recorded earlier stand under the rules they named.

## The rule
- Ratio rows. The ratio band is the delivered database count over the stated figure, as a range across the plan's date and scope choices, read against the agreement band 0.90 to 1.10 with closed edges. The range is a rule spread and not a sampling interval, so no level, no draw and no seed apply. The row is read with read(band): inside is CONSISTENT, wholly over 1.10 is ABOVE, wholly under 0.90 is BELOW, and a range that crosses an edge is CANNOT_TELL with reason STRADDLES_EDGE.
- A stated zero has a band of zero to zero, because 10 percent of zero is zero. It is read with read(band, 0 to 0). A database count of zero is CONSISTENT, a count wholly over zero is ABOVE and a count whose range holds zero and more is STRADDLES_EDGE.
- Share rows. The difference band is read against minus 5 points to plus 5 points with read(band), closed edges.
- The floor of 100 statements in Addendum 6.8 is the size that matters in statements. A reading that clears an edge by fewer than 100 statements is CANNOT_TELL with reason STRADDLES_EDGE, as before.
- All of the plan's other results are unchanged. The readings that the later addenda moved to cannot tell keep their reasons in words.

## Nothing returned is no longer an outcome
The plan gives the outcome Nothing returned to a row whose half-year has no report that can be read without a key or login, or whose report is a web page and not a template file. The read found no figure on the stated side, so no interval can be formed. Such a row is CANNOT_TELL with reason NO_INTERVAL_FORMABLE and the plain cause stays in its reason text. The status NOTHING_RETURNED is kept for a failed read of a source, and the desk has none when its gates pass. Rows read as Nothing returned before are counted in the CANNOT_TELL share and in its denominator from now on.

## How the desk's own causes of CANNOT_TELL map
- No stated figure, no stated share, no statements in the database for the platform and period, missing database months, a failed known-good gate, a platform note moving a row (Addenda 4 and 6.3), and opposite readings on one split (Addendum 6.7): NO_INTERVAL_FORMABLE, because the planned quantity cannot be formed or the rule forces the result. These are forced readings with no closed reason and they map to NO_INTERVAL_FORMABLE.
- A range that crosses an edge, and a reading that clears an edge by fewer than 100 statements: STRADDLES_EDGE.
- TOO_WIDE_TO_RESOLVE is not used, because no size that matters is named beside a null.

## Counts beside the headline
The section prints the REQ-13 line for its comparison rows: the NOTHING_RETURNED count, then the CANNOT_TELL share split by reason. The section has no headline number of its own.

## What flips
No decided outcome changes. The rows that read Nothing returned, 27 comparison rows in the reading of 10 November, read CANNOT_TELL with reason NO_INTERVAL_FORMABLE.
