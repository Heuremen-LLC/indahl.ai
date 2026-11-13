# AIRQ plan addendum: outcome rule under Faults and Guards 2.0. Dated 12 Nov 2026, written before any reading under the new rule.

This addendum changes only how an interval is turned into an outcome word. The data, the sources, the two windows, the live panel, the EPA targets, the correction, the cleaning rule, the unit of one sensor per monitor, the tie rule, the Wilson 95 percent interval over monitors, the points guard and the known-good checks are unchanged. Outcomes recorded earlier stand under the rules they named at the time. A reading made after this addendum is a new reading under the new rule and is printed beside the earlier one.

## The figure, the edge and the size that matters
The plan reads the share of monitors whose sensor does not meet the four EPA targets against one line, 0.50. It says ABOVE if the lower end is above 0.50 and CONSISTENT if the upper end is below 0.50. A single line is a one-sided threshold. Under the new rule a reading against one bound is ABOVE, BELOW or CANNOT_TELL, and CONSISTENT is not available for it.
- The bound is 0.50. The edge convention is closed, so a lower end of exactly 0.50 is not above it and an upper end of exactly 0.50 is not below it, as the plan's words say.
- ABOVE is a lower end above 0.50. This is unchanged.
- An upper end below 0.50 now reads BELOW. The plan called it CONSISTENT. No reading in either window, the 2025 one, the 2026 one or the live panel, has been in that range.
- An interval that holds 0.50 reads CANNOT_TELL with reason STRADDLES_EDGE.
- No size that matters is named. The plan states a line and does not say what departure from a null would matter, so the both-alternatives test is not applied, and no outcome is CANNOT_TELL with reason TOO_WIDE_TO_RESOLVE except by the minimum below. No two-sided band is invented now, because that would be a rule written after the data.

## Interval method
Wilson at 95 percent over monitors, one unit per monitor at the sensor of its median-RMSE pair, with the code's tie and the other tie both printed, as in addendum 5. No resampling, so no draws and no seed.

## How the desk's own causes of CANNOT_TELL map to the reasons
- Fewer than 30 monitors, the plan's own minimum: CANNOT_TELL with reason TOO_WIDE_TO_RESOLVE.
- No monitor with a pair at all, which the live panel read as NOTHING_RETURNED until 30 kept days existed: CANNOT_TELL with reason NO_INTERVAL_FORMABLE.
- An interval that holds 0.50 with 30 or more monitors: STRADDLES_EDGE.

## Failed reads
A sensor not read because the points guard stopped the read, a state the AQS service did not answer and a state day it refused are failed reads of sources that feed a reading. They are outside the numerator and the denominator and are counted as NOTHING_RETURNED beside the headline, as the sum of the three for a window. For the live panel the failed reads are the PurpleAir calls of the run that failed or were refused for lack of points. The word NOTHING_RETURNED is a status and is never printed as an outcome. REQ-13 is printed beside every headline reading: the count of failed reads and the share of CANNOT_TELL split by reason.

## Which readings carry this
The map reading and the reading corrected for humidity are shown with equal weight, as addendum 5 says. The raw cf_1 reading, the other-tie readings, the previous window and the live panel carry the same rule. The live outcome is never merged with the main one.
