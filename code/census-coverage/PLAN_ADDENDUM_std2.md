# CENSUS COVERAGE: plan addendum for Faults and Guards 2.0, 12 November 2026

This addendum is written before any reading under the new outcome rule. PLAN.md is not edited and its seal is unchanged. The data, the sources, the parser, the known-good gates and the interval are unchanged. Only the outcome rule and the way a cannot tell is named change. The outcomes recorded on 11 November stand under the rules the plan named.

## The dead zone the audit names
PLAN.md reads CONSISTENT when the 90 percent interval holds zero, at any width, with no size that matters and no tolerance. That reads a wide interval as agreement with zero. The plan names no size that matters for a net coverage error, and none is named now, because a size chosen after the first reading would be a rule written after the data. Without a size and without a band around zero, the test of both alternatives cannot be applied and CONSISTENT is not available. The recount says so on the page.

## Rule for an area, the United States cell and a component
- Interval: the published figure plus or minus 1.645 times its published standard error, the normal multiplier for a two-sided 90 percent interval, as in PLAN.md. No resampling, so no draws and no seed.
- Zero, and for a component the national value, is a point figure with no tolerance. The reading is made with heuremen_kit read(lo, hi, bound=figure), edge closed. It reads ABOVE when the lower end is over the figure, BELOW when the upper end is under it, and otherwise CANNOT_TELL with reason STRADDLES_EDGE.
- The areas that read BELOW or ABOVE are the same as before, so the match with the Census asterisks in known-good gate 2 is unchanged. The areas that read CONSISTENT before read CANNOT_TELL with reason STRADDLES_EDGE now.
- TOO_WIDE_TO_RESOLVE is not used, because no size that matters is named.
- No estimate, no standard error, a standard error of zero or below, and the sentinel -9999.9 each give CANNOT_TELL with reason NO_INTERVAL_FORMABLE, because no width can be formed. The plain cause is kept beside the code.
- A failed known-good gate gives CANNOT_TELL with reason NO_INTERVAL_FORMABLE for every reading, and the original outcome is kept beside it.

## Demographic Analysis cell
The three series are scenarios Census gives. They are read as a range from the lowest to the highest series, called a range and not an interval, against zero as a point figure with no tolerance. All three over zero reads ABOVE, all three under zero reads BELOW, and a range that holds zero reads CANNOT_TELL with reason STRADDLES_EDGE. A missing series gives CANNOT_TELL with reason NO_INTERVAL_FORMABLE.

## Exact reads
Reading the census count against the Census asterisks in gate 2, and the household counts against the PDF in gate 1, are exact comparisons of one published value with another. Under owner decision O1 they are intervals of zero width and keep the equality test they already use. They carry no outcome word and no share.

## Counts beside the headline
The headline prints the count of areas by reading as BELOW, ABOVE and CANNOT_TELL, and the CANNOT_TELL count split by reason. It also prints the REQ-13 line: the NOTHING_RETURNED count, then the CANNOT_TELL share split by reason. A failed read of a source stops gate 1 and gives no reading, so the count of failed reads is zero when the gates pass. The CONSISTENT count is printed as zero with the reason it is not available.

## What flips
The 37 areas that read CONSISTENT, the United States cell and the Demographic Analysis cell move from CONSISTENT to CANNOT_TELL with reason STRADDLES_EDGE. The 101 component readings in the summary move the same way where they read CONSISTENT. The 6 BELOW and 8 ABOVE areas hold. The page already prints the components as values and does not read them.
