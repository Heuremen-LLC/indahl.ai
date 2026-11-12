# TIME plan addendum for Faults and Guards 2.0

Dated 12 November 2026. Written before any reading under the 2.0 outcome rule.

## What this addendum changes
Only the outcome rule and what is printed beside it. The servers, the probe, the rounds, the kept sample, the seats, the removal of the seat's own part and the sources are unchanged. T1 is the only statement scored and stays so. Outcomes recorded before this date stand under the rules they named.

## The reading
For one server on one seat the quantity read is the distance of the server from true time, the absolute value of the median offset o over the rounds held. The server's own stated bound is E, the median over the rounds of root dispersion plus half the root delay. The band is zero to E. The plan has no separate lower statement, so there is no BELOW. The code and the recorded outcomes never assigned one.

## Interval, method and level
The interval of the distance is the absolute offset plus or minus h, where h is the median over the rounds of half the round-trip delay of the kept sample, with the lower end clamped at zero because a distance cannot be negative. This is the worst-case bound on the unknown asymmetry of the path and not a probability interval. It carries no confidence level. Its level is named as a worst-case bound, 100 percent in that sense. No resampling is used, so no draws or seed apply. The sealed plan adds the reference's own logged uncertainty in quadrature. The code has used the half-delay alone since the first run, the reference term is of order 0.01 to 0.1 milliseconds, and it is left out as run. The reading is the one the code computed and no number moves.

## Edge convention
Closed at both edges, as the plan says "at most E".

## Size that matters
The size that matters is E, the server's own stated bound. The plan's T2 sentence says that where the path uncertainty exceeds E no claim smaller than the path can resolve is called met. The null is a distance of zero. The both-alternatives test applies: an interval that holds zero and holds E reads CANNOT_TELL with reason TOO_WIDE_TO_RESOLVE, before any comparison with the band. A bound of zero or less cannot be a size that matters and the test is skipped for it.

## Outcomes
- ABOVE: the lower end of the interval is above E. This is the plan's "the server is further from true time than it states".
- CONSISTENT: the whole interval lies inside zero to E and the both-alternatives test does not fire.
- CANNOT_TELL with TOO_WIDE_TO_RESOLVE: the interval holds both zero and E. This is the plan's path uncertainty exceeding the bound.
- CANNOT_TELL with STRADDLES_EDGE: the interval overlaps E and is not otherwise decided.
- CANNOT_TELL with NO_INTERVAL_FORMABLE: a server with kept replies whose offset, delay or bound cannot be formed.

## The two seat readings
Each server is read twice on a seat, raw and with the seat's own part removed, as Addendum 1 of the plan says. The headline outcome is the shared one where the two readings agree. Where both are CANNOT_TELL with different reasons the reason that comes first in the decision order is kept, TOO_WIDE_TO_RESOLVE before STRADDLES_EDGE. Where the two outcomes differ the headline is CANNOT_TELL with reason STRADDLES_EDGE, because the comparison with the bound changes when the seat's part is allowed to be anywhere between the two, so the interval of the reading overlaps the edge. No new reason is invented.

## Failed reads
A server that returns nothing, or refuses, has no kept reply and no reading. It is recorded as a failed read with status NOTHING_RETURNED or REFUSED, listed apart, and is outside the numerator and denominator. It is never an outcome of the server. The page prints the count of failed reads and the share of CANNOT_TELL split by reason beside the totals, for each seat.

## Not changed
T3 and T4 stay unscored. The stratum equality of T3 is not read here.
