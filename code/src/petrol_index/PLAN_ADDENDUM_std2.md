# PETROL plan addendum for Faults and Guards 2.0

Dated 12 November 2026. Written before any reading under the 2.0 outcome rule. PLAN.md is not edited and its seal in data/plan_seal.json is unchanged.

## What this addendum changes
Only the outcome rule and what is printed beside it. The data, the sources, the collectors, the parsers, the target tables, the widths, the gates and the frame of PLAN.md and its Amendment A1 are unchanged. Outcomes recorded before this date stand under the rules they named. The numbers of every row are unchanged and only the reason beside a CANNOT_TELL is new.

## The readings
Part 1 reads one number per member and month, the gap between the delivered figure and the required level. Part 2 reads one number per month, the weekly average minus the monthly figure. Both compare a published value with a published value. Nothing is sampled. Under owner decision O1 each is a reading with an interval of zero width, so no interval method, level, draws or seed apply.

## Band, tolerance and edge convention
The tolerance is the stated width w of the sealed plan, the 90th percentile of OPEC's own first-to-second-print revision for the nine OPEC members, the pooled 7.7 percent times the delivered figure for the ten non-OPEC members, and the 2015 to 2019 spread for Part 2. The band is minus w to plus w with both edges closed, as the plan says "edges included". A gap above w reads ABOVE. A gap below minus w reads BELOW. A gap inside the band reads CONSISTENT. The code reads this with read_exact and a band.

## Size that matters
The plan names no separate size that matters. The width w is the tolerance of the band. A reading of zero width cannot reach both the null and an alternative, so the both-alternatives test cannot fire and is not applied.

## Reasons for CANNOT_TELL
The desk's own causes map to the closed list as follows.
- Exempt, no required level (Libya, IR Iran, Venezuela): NO_INTERVAL_FORMABLE. The planned quantity, a gap against a required level, cannot be formed for a member that has none.
- No target table transcribed: NO_INTERVAL_FORMABLE. The required level is not stated for that month.
- No delivered value (a printed ".." or a missing value): NO_INTERVAL_FORMABLE.
- No monthly value (Part 2): NO_INTERVAL_FORMABLE.
- Gate failed or plan changed: NO_INTERVAL_FORMABLE. The run is not a reading, and the gates already turn every outcome into CANNOT_TELL.
- No width, which arises only when a member has fewer than 24 revision rows, when fewer than 30 pooled non-OPEC rows exist, or when fewer than 48 baseline months exist for Part 2: TOO_WIDE_TO_RESOLVE, under owner decision O3 for a reading below a minimum sample.
- Fewer than four weeks in a month (Part 2): TOO_WIDE_TO_RESOLVE, under O3.
STRADDLES_EDGE cannot arise, because a zero-width reading is never on both sides of an edge. The prose reason of the sealed plan stays in the rows file beside the code.

## Failed reads
A failed fetch or parse of a source is NOTHING_RETURNED, is listed apart and is outside the numerator and denominator. The gates turn a failed parse into a gate failure. No row-level read has failed in the window, so the count beside each headline is 0. A printed ".." is a published value that says nothing and is read as no delivered value above.

## Beside each headline
The page and the feed print the REQ-13 line, the NOTHING_RETURNED count and the share of CANNOT_TELL split by reason, for the latest month of Part 1, for the whole Part 1 window and for Part 2.

## What stays as it was
The lead number, the count below the required level for the latest month, was chosen after the run and stays labelled so. The widths are yardsticks of ours and not published widths.
