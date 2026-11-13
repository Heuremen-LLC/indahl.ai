# AIRLINE: plan addendum for Faults and Guards 2.0

Dated 12 November 2026. Written before any reading under the new outcome rule. PLAN.md is not edited.

## What changes and what does not
The outcome rule changes to the reading outcomes of section 6 of Faults and Guards 2.0. The bootstrap gets a named seed and is read again. Data, sources, months, rows kept, the 30-flight and 30-route rules, the known-good, the hand check and the FAA keeper are unchanged. Earlier recorded outcomes stand under the rules they named. The read of 29 October 2026 stays in the record and the new reading is shown beside it. Neither replaces the other.

## What the plan names, as the addendum reads it
Quantity per airline and comparison: the median over routes of the change in padding (scheduled minus flown, median per route and period), later period minus earlier period, in minutes. The null is zero.
Size that matters: 1 minute, in either direction. The plan names plus or minus 1 minute only as the resolution of the file, which says what the file can show and not what matters. The plan's one number is also the only threshold it uses, ABOVE if the lower end is above plus 1 and BELOW if the upper end is below minus 1. Following owner decision on the ABOVE bound, this addendum takes that one minute as the size that matters. A larger size would be a number chosen after the data, so none is used. Whether one minute matters for the on-time rate is not claimed here. The owner may name another size in a later addendum, and it would be a new reading beside this one.
Band: minus 1 to plus 1 minute, closed edges. It is the plan's CONSISTENT bound.
Direction of the both-alternatives test: both. An interval that holds zero and also holds plus 1 or minus 1 reads CANNOT_TELL with reason TOO_WIDE_TO_RESOLVE, even when it lies inside the band.
Edge convention: closed, as the plan says. An interval whose lower end is exactly plus 1 is not ABOVE.

## Interval method, level and seed
Percentile bootstrap over routes, each route one unit, 2,000 draws, 95 percent, of the median change. One call per airline and comparison, each with seed 20261112, and the kit's percentile with linear interpolation between ordered draws. Routes are the independent units and flights on one route are not.
The first read of 29 October used one random stream seeded 20261029 in the code and shared by every airline and both comparisons in file order, with the nearest ordered draw as the percentile. The seed was not named in the plan and each airline's interval depended on the airlines drawn before it. That reading is kept as it was and is printed beside the new one. The new reading is a new reading and is labelled so.

## Minimum sample and the mapping of the desk's own causes of CANNOT_TELL
An airline with fewer than 30 routes that pass the 30-flight rule has no usable sample. Under owner decision O3 it reads CANNOT_TELL with reason TOO_WIDE_TO_RESOLVE, with its route count printed and no interval formed. It was listed as NOTHING_RETURNED before. That was a status of a failed read and these airlines were not failed reads, so the word is no longer used for them. Such airlines are counted in the headline denominator as readings. None is in the current data.
The pooled headline, airlines ABOVE out of airlines compared for 2026 against 2025, has no bound or band in the plan. Addendum 2 of the plan printed CANNOT_TELL on it by decree. A decree is not a closed reason, so under the owner's rule it reads CANNOT_TELL with reason NO_INTERVAL_FORMABLE, because the plan names no figure for a share to be read against. The count and its Wilson 95 percent interval are the reading, as before.
A failed read of a monthly file stops the run. A failed FAA snapshot is stored as NOTHING_RETURNED as the plan says. It is a status of the read, is not an outcome, and no share is printed from the FAA keeper.
The FAA stated-against-delivered test of Addendum 3 has not been run. Before it runs, a new addendum names its size that matters, its band, its edge and its seed.

## REQ-13 beside the headline
The headline carries a block that prints the number of NOTHING_RETURNED reads and the share of CANNOT_TELL among the per-airline readings of 2026 against 2025, split by reason. The same block is given for 2025 against 2019.
