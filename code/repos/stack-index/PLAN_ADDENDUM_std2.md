# Addendum for Faults and Guards 2.0 to the STACK plan, 12 Nov 2026

Written before any new reading under the 2.0 reporting rule. PLAN.md and its addenda are not edited. This file is a new addendum.

## What changes
Only how the table carries the outcomes it inherits. STACK still adds no reading of its own, still reads the public feeds of the other pages, and still changes no rule of any desk. The rows, the order and the groups stay.

## Outcome and reason, read from the desk
Each row takes its outcome and its CANNOT_TELL reason from the desk's own feed, from the field named reason beside the field named outcome. STACK never assigns a reason and never recomputes an outcome. A desk moves to the 2.0 rule on its own plan addendum, and its feed carries the new outcome and reason only when its own page ships. Until then a row can carry an outcome with no reason.

- A row whose desk feed gives CANNOT_TELL with no reason is counted under MISSING_REASON in the split by reason, and the page says that the desk feed does not yet carry a reason.
- A row whose desk feed gives an outcome that is not one of the four reading outcomes is shown as CANNOT_TELL with reason NO_INTERVAL_FORMABLE, with a note that names the field. The same holds for a TRIALS row whose feed carries no outcome. The earlier plan computed that outcome in STACK from the interval. That computation is removed because STACK adds no reading of its own.
- Outcomes that the desks give for CONSISTENT, ABOVE or BELOW are copied as the desk gives them. They change only when the desk's feed changes.

## Failed reads
A feed or block that cannot be fetched or parsed is the status NOTHING_RETURNED. It is listed apart as a failed read, with the page, the test and the cause. It is outside the numerator and the denominator of every tally. A feed that still gives the old value NOTHING_RETURNED as an outcome is treated the same way, because STACK cannot tell what that value stood for. A reading that a migrated desk could not compute yet arrives as CANNOT_TELL with NO_INTERVAL_FORMABLE and is counted as a reading.

## Beside the tally
The page prints the kit's REQ-13 line over all rows: the NOTHING_RETURNED count and the CANNOT_TELL share split by reason. Each page that reports many separate items is tallied the same way. Where a desk gives only a count of cannot-tell items with no reasons, that count is shown under MISSING_REASON.

## Earlier recorded outcomes
Every outcome copied before 12 Nov 2026 stands under the rules its desk named then.
