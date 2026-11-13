# Plan addendum for Faults and Guards 2.0, OY (12 November 2026)

Written on 12 November 2026 before any reading under Faults and Guards version 2.0.0. The plan (PLAN_OY_INDEX.md) names four outcomes for a claim priced against the record, with CONSISTENT meaning "within the record, printed as a bound", and CANNOT_TELL meaning "no record reaches it". It names no size that matters, no band, no tolerance, no edge convention, no interval method and no reason list. The audit of 12 November 2026 therefore could not judge this desk. This addendum decides them. The author of this addendum decided every value below. None was fixed by the original plan.

## What is unchanged

Sources, the rows files, the school list, the reading dates, the two filing rules for a measured outcome and every recount of a study are unchanged beyond the outcome rule. PLAN_OY_INDEX.md is not edited. Every outcome recorded earlier stands under the rules it named, and its 2.0 reading is printed beside it where it differs.

## What the desk reads

- A filing of a school row into a bin is a filing, not a reading outcome. It carries no outcome word. The counts of rows per bin are shares of the rows that were read.
- A claim priced against the record is a reading. The claim states a figure, and the record is a published study, a released data file or an official document read in full.
- A claim with no number and no test is "no testable claim". It has its own column and no outcome word.

## Size that matters, band, tolerance, edge

- Size that matters, where a priced claim is a departure from a null: 0.20 standard deviations for an effect on a standardised outcome, and 5 percentage points for a share or a rate, in the direction the claim names (both directions where it names none). Where the study's scale is neither, the claim must name the size before the read. Without a named size the both-alternatives test cannot be applied and CONSISTENT is not available for that reading.
- A point figure the claim states has no tolerance unless the claim prints one. Without a tolerance it is read as a bound: ABOVE, BELOW or CANNOT_TELL with reason STRADDLES_EDGE. No tolerance is invented after the data.
- A claim that states a range or a tolerance is read against that band.
- Edge convention: closed at both edges.
- A one-sided claim ("at least", "more than", "no more than") can print only ABOVE, BELOW or CANNOT_TELL.

## Interval method and level

- The interval of the record is the one the study prints, with its own method named in the row. Where the study prints only a standard error, the interval is the estimate plus or minus 1.96 standard errors at 95 percent, and the row says so.
- Where a study releases its data and we rebuild the figure, the interval is a percentile bootstrap over the study's units (students, classes or schools as the study randomised them), 2,000 draws, seed 7, 95 percent. A share of rows is given a Wilson interval at 95 percent.
- A study that prints only a p-value, the words "no significant difference" or a standard error with no multiplier, and releases no data, has no interval under this standard.

## How this desk's CANNOT_TELL causes map to the closed reasons

- "No record reaches it", the record is unread or behind a paywall, the study prints no interval, only a p-value or only "not significant", the study is too small to print a bound, or a row cannot be filed under the rule from what was read: NO_INTERVAL_FORMABLE.
- An interval that overlaps the band or the bound: STRADDLES_EDGE.
- An interval that holds the null and the size that matters: TOO_WIDE_TO_RESOLVE, whatever else it touches.
- A reading under a floor of 30 units read: TOO_WIDE_TO_RESOLVE.

## Failed reads

A school whose pages need a login or refused our reader even in a browser is NOTHING_RETURNED, a status of the read. It is listed apart as not reached. It is outside the numerator and the denominator of every headline share, so a headline share is out of the rows that were read. It is never an outcome and is never counted as none found.

## Counts beside the headline

Beside every headline share the page prints the count of NOTHING_RETURNED and the share of CANNOT_TELL split by reason (REQ-13), built with the kit's req13.
