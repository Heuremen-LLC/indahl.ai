# Addendum for Faults and Guards 2.0 to the RANK plan, 12 Nov 2026

Written before any new reading under the 2.0 reporting rule. PLAN.md and its addenda are not edited. This file is a new addendum. No US News list, public source or figure is read again for it.

## What changes
Only how the reasons for CANNOT_TELL are named and what is printed beside the headline. Data, sources, the per-figure rule in rule.py and its tests, the lists and the years are unchanged.

## The per-figure reading
Every figure is an exact row-level read of a published value against a published value, with no sampling. Under the owner's decision on exact reads it has an interval of zero width. The stated tolerance is rounding: the public figure is rounded to the precision US News prints and then compared for equality. MATCH and MISMATCH stay as the desk's own words for that equality. They are not ABOVE, BELOW or CONSISTENT, there is no null and no size that matters, and so the both-alternatives test does not apply. No interval method, level, draws or seed are needed.

## The reasons for CANNOT_TELL
The desk's own reasons stay as a detail beside the closed reason. They map as follows.

- year, not_found, definition, not_printed, suppressed and paid_tier map to NO_INTERVAL_FORMABLE. In each case one of the two values is missing, unreadable or not the same quantity, so no zero-width comparison can be formed. These causes fit none of the other two closed reasons.
- floor_or_range_unsettled and precision map to STRADDLES_EDGE. The public figure is itself a bin or a coarser value, so its interval overlaps the figure or the floor US News prints and cannot be placed on one side of it.
- A rank recompute that reads CANNOT_TELL because an input is a survey, purchased data or a fitted model maps to NO_INTERVAL_FORMABLE. The planned quantity cannot be computed from public inputs.
- A statement about a rank (the claims table) that reads CANNOT_TELL because it names no edition or list, or an edition not read, maps to NO_INTERVAL_FORMABLE.
- A Blue Ribbon award whose category is not stated by any source maps to NO_INTERVAL_FORMABLE.

No cause maps to TOO_WIDE_TO_RESOLVE because no size that matters is named.

## Failed reads
A public figure that was looked for and not found is a reading that cannot be formed (not_found), not a failed fetch, so it is not NOTHING_RETURNED. A page or file that could not be read at all is logged in research/MANUAL_READS.md and is a failed read. The count of failed reads beside the headline is 0 in the stored data because every row carries one of the reasons above. It is printed anyway.

## Beside the headline
The page and the feed print the kit's REQ-13 line over all figure readings: the NOTHING_RETURNED count and the CANNOT_TELL share split by reason. Each reading carries its closed reason in a field named reason, and the desk's own reason in reason_detail.

## Earlier recorded outcomes
Every outcome recorded before 12 Nov 2026 stands under the rules the plan named then.
