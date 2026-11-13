# WEIGHTS plan addendum: outcome rule under Faults and Guards 2.0. Dated 12 Nov 2026, written before any reading under the new rule.

This addendum changes only how an interval is turned into an outcome word. The data, the sources, the file-set comparison, the passes and their cadence, the Wilson 95 percent interval, the hand check and the known-good checks are unchanged. Outcomes recorded earlier stand under the rules they named at the time. A reading made after this addendum is a new reading under the new rule.

## The size that matters, the band and the edge
The plan names one number, 1 percent, as the share it would call noticeable, and uses the same number as the line for ABOVE and for CONSISTENT. This addendum states what that number is under the new rule.
- The size that matters is 0.01, the share CHANGED that the plan calls noticeable. The null is 0.
- The band is [0, 0.01), open at the upper edge, because the plan says CONSISTENT if the upper end is below 1 percent.
- The edge convention is '[)'.
- With both numbers equal the rule reads as follows. CONSISTENT needs the whole interval inside [0, 0.01), and such an interval can never reach the size that matters. ABOVE needs the lower end at or above 0.01, where the plan said above 0.01. An interval that holds 0.01 and is not wholly above it reads CANNOT_TELL, with reason TOO_WIDE_TO_RESOLVE when it also holds 0 and with reason STRADDLES_EDGE when it does not.

## Interval method
Wilson at 95 percent over model pairs, one unit per model at its latest pair, as in the plan. No resampling, so no draws and no seed.

## How the desk's own causes of CANNOT_TELL map to the reasons
- An interval that reaches both 0 and 0.01: TOO_WIDE_TO_RESOLVE.
- An interval that overlaps 0.01 without reaching 0: STRADDLES_EDGE.
- No model pair that is SAME or CHANGED yet, which the plan called NOTHING_RETURNED on the first pass: CANNOT_TELL with reason NO_INTERVAL_FORMABLE.
- NOT_COMPARABLE models, models whose repository is GONE and the SAME and CHANGED labels are row labels and not outcomes. NOT_COMPARABLE and GONE stay outside the numerator and the denominator and are listed apart as the plan says.

## Failed reads
A model whose file list could not be read for a reason other than being gone is UNREADABLE in the plan. It is a failed read of a source that feeds a row. It is not scored, is outside the numerator and the denominator, is retried on the next pass, and is counted as NOTHING_RETURNED beside the headline. The word NOTHING_RETURNED is a status and is never printed as the outcome of the headline. REQ-13 is printed beside the headline: the count of failed reads and the share of CANNOT_TELL split by reason.

## Descriptive additions
The share of models that changed on any pass, the table of passes and the list of changes have no outcome and are unchanged.
