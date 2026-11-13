# TORNADO: plan addendum for Faults and Guards 2.0, 12 Nov 2026

This addendum is written before any new reading under the 2.0 outcome rule. PLAN.md is not edited and its seal in data/plan_seal.json is unchanged. The data, the sources, the grid, the frame, the cells, the bands, the warning definitions, the known-good checks and the day-level bootstrap are unchanged. Only the outcome rule changes, to the reading outcomes of the standard (section 6). Outcomes recorded earlier stand under the rules they named.

## Bands and the hatched reading
- Each band is a two-sided band, so CONSISTENT stays available. The edge convention is the plan's own. A band is closed at its lower edge and open at its upper edge, as in [0.10, 0.15), and the last band [0.60, 1] and the hatched band [0.10, 1] are closed at both ends.
- The reading is ABOVE if the whole interval is above the top of the band, BELOW if the whole interval is below the bottom of the band, CONSISTENT if the whole interval lies inside the band, and otherwise CANNOT_TELL with reason STRADDLES_EDGE. This is what PLAN.md already said, now with the standard's edge handling and a reason.
- Size that matters: none named, so the both-alternatives test is not applied to the bands. The page says so.
- Interval: the plan's day-level block bootstrap, 2,000 resamples of the days in the cell with every row of a drawn day kept together, fixed seed 20261110 plus the cell's offset, 95 percent percentile interval. It stays in the desk's own code. It draws day weights with a multinomial draw on array sums, and the kit's bootstrap draws from another random stream and would move the stored intervals. The interval method is unchanged.

## Brier skill against climatology
- A one-sided bound at zero. The reading is ABOVE if the whole interval is above zero, BELOW if the whole interval is below zero, otherwise CANNOT_TELL with reason STRADDLES_EDGE. Closed edge. It never prints CONSISTENT, as PLAN.md already said. Interval as above.

## The warning goals
- POD at least 0.72, lead at least 13 minutes and FAR at most 0.71 are one-sided thresholds. They may print only ABOVE, BELOW or CANNOT_TELL, and CONSISTENT is retired for them. The plan's CONSISTENT meant the goal was met.
- POD and lead are read against the bound with the goal itself counting as met. ABOVE means the whole interval is at or above the goal, which meets it. BELOW means the whole interval is under the goal. Otherwise CANNOT_TELL with reason STRADDLES_EDGE.
- FAR is read against the bound with the goal itself counting as met. BELOW means the whole interval is at or under 0.71, which meets the goal. ABOVE means the whole interval is over 0.71, which misses it. Otherwise CANNOT_TELL with reason STRADDLES_EDGE. A reading of BELOW for FAR is therefore a met goal and a reading of ABOVE is a missed one, and the page says so beside the table.
- No size that matters is named for the goals and the both-alternatives test is not applied.
- The plan names no minimum sample for a warning reading, and none is added. A fiscal year with few tornadoes or warnings reads whatever its interval says. The current fiscal year is preliminary and often thin, and its wide interval reads CANNOT_TELL on its own.

## How the desk's own CANNOT_TELL causes map
- A band with fewer than 30 days with a row in it reads CANNOT_TELL with reason TOO_WIDE_TO_RESOLVE (minimum sample rule, owner decision O3). A band with no days at all reads CANNOT_TELL with reason NO_INTERVAL_FORMABLE.
- A reading whose bootstrap forms no interval reads CANNOT_TELL with reason NO_INTERVAL_FORMABLE.
- The hatched reading of the preliminary window stays CANNOT_TELL, because no preliminary report carries a rating and an EF2 or stronger tornado cannot be told apart. The planned quantity cannot be formed, so its reason is NO_INTERVAL_FORMABLE.
- A failed known-good check turns every outcome into CANNOT_TELL with reason NO_INTERVAL_FORMABLE and keeps the original outcome beside it, as before. The old bare CANNOT_TELL had no closed reason and this is the closest one.
- Interval overlaps an edge or the bound: STRADDLES_EDGE.

## Display readings
The reading of a band against the contour value, which the page prints beside the band reading, is a point figure with no tolerance. It is read against the contour value as a bound, ABOVE, BELOW or CANNOT_TELL with reason STRADDLES_EDGE, and never CONSISTENT. It is display only and decides nothing, as before.

## Counts beside every headline (REQ-13)
- Beside the headline the page prints the REQ-13 line over the eight bands of the United States closed-years cell. Beside the warnings table it prints the line over the detection, lead and false alarm readings of every row of that table.
- NOTHING_RETURNED counts the failed reads the plan names: days with no 1300 UTC outlook in the archive, outlook days whose tornado layer could not be read, preliminary days whose file could not be fetched and fiscal years whose warning file could not be fetched. They are listed apart and are outside the numerator and denominator. The summary also carries a REQ-13 line over every band, hatched, Brier and warning reading of the desk.

## Expected effect, stated before the new run
The band readings of the eight-band tables stay as they are. The two yearly false alarm rows that read CONSISTENT, for the fiscal years 2022 and 2025, read BELOW, which means the goal is met. Detection and lead readings keep their words. The six display readings against the contour value that read CONSISTENT read CANNOT_TELL with reason STRADDLES_EDGE. No number other than an outcome moves.

## Correction to the expected effect, 12 Nov 2026
The paragraph above counted the display readings against the contour value in the three closed-year cells only. The yearly United States tables carry the same display column. Across the closed and preliminary cells and the yearly tables 24 display readings read CONSISTENT before this addendum, and they read CANNOT_TELL with reason STRADDLES_EDGE after it. Nothing else in the expected effect changes.
