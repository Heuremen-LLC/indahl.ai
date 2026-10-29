# AIRLINE: scheduled flight time against flown flight time. Plan, committed before any file is read.

## The claim and the question
Each flight is published with a scheduled elapsed time (CRSElapsedTime in the Bureau of Transportation Statistics on-time file). The government's on-time rate counts a flight as on time when it arrives within 15 minutes of schedule. If schedules get longer while flown times stay the same, the on-time rate rises with no change in how long a flight takes. We measure that gap: scheduled minus flown, per airline, in the same months of 2019, 2025 and 2026.

## Data
BTS Reporting Carrier On-Time Performance monthly files (transtats.bts.gov/PREZIP), January to August of 2019, 2025 and 2026. Rows kept: not cancelled, not diverted, both elapsed times present. Flown time = ActualElapsedTime (gate to gate, the same basis as the scheduled time).

## Rule (fixed now)
- Unit: an airline and a route (origin to destination). Per unit and period, padding = median scheduled minus median flown, minutes. A unit enters a comparison only if it has at least 30 flights in both periods.
- Change = padding in the later period minus padding in 2019 (and 2026 minus 2025). One airline, one comparison.
- Interval: 2,000 bootstrap draws over routes (routes are the independent units, flights on one route are not), 95%, percentile.
- Outcome per airline: ABOVE if the lower end is above +1 minute. BELOW if the upper end is below -1 minute. CONSISTENT if the whole interval is within -1 to +1. Otherwise CANNOT_TELL. One minute is the resolution of the file.
- Beside it, printed and not tested: flights arriving 15 or more minutes late (the file's ArrDel15), per period, and the change in median flown time on the same units.
- Airlines with fewer than 30 routes passing the 30-flight rule are listed as NOTHING_RETURNED.

## Known-good, run before the real files
The same code runs on planted data: padding added of +5, 0 and -5 minutes on synthetic routes with noise. It must return ABOVE, CONSISTENT, BELOW. Then one airline and route is recomputed from the raw rows by hand with a separate command and must equal the code's number.

## Not claimed
Why schedules changed. Schedules can lengthen because of congestion, airport changes or slower taxi, not only to protect an on-time rate. We print the sign and size of the gap and nothing about intent. The file's elapsed times are in whole minutes. Airlines merged or renamed between periods are matched by the file's carrier code only.

## Hand check
Every ABOVE or BELOW airline: open the five routes with the largest change and read their rows.

## Addendum 1 (29 Oct, before any file was read)
The first run of the planted-data gate returned CANNOT_TELL for the zero shift. The planted noise (standard deviation 2 minutes per route and period) is wider than the plus or minus 1 minute that CONSISTENT requires, so the rule was right to refuse. No real file had been read. The planted controls are now: noise 0.5 minute (about the size of whole-minute rounding of a median) for plus 5, zero and minus 5, which must return ABOVE, CONSISTENT, BELOW. A fourth control with noise 4 minutes and shift zero must return CANNOT_TELL, so the bin is tested too. The outcome rule is unchanged.

## Addendum 2 (29 Oct, after the first read and the hand check, before anything was shown)
- Hand check: for the five airlines ABOVE in 2026 against 2025 (AA, AS, MQ, OH, YX), the three routes with the largest change were recomputed from the saved monthly counts by a separate median routine (the sorted list of every flight, not the counter). Every number matched. On those routes the scheduled time rose and the flown time fell (for example MSO to ORD for MQ: scheduled 206 to 221 minutes, flown 204 to 197). Across all routes of those airlines the median change in flown time was 0 to 1 minute (AS: minus 3), and the median change in scheduled time was 2 to 5 minutes.
- The first plan had no row for STACK. A pooled count is added now, after the data, and is labelled that way: airlines with ABOVE, out of airlines compared, for 2026 against 2025. It has no threshold, so its outcome is printed as CANNOT_TELL on STACK and the count is the reading.
- The page prints each airline's share of flights 15 or more minutes late in each period beside the change, as the plan said. It is not tested.
- The page reads from the saved result and rebuilds from the saved monthly counts. A new read of the files is a new addendum.

## Addendum 3 (29 Oct, written before the first live read): the FAA keeper, a live stated-against-delivered record
BTS data comes monthly with a lag of about two months, so the main read cannot be live. The FAA publishes the airport delay programs it is running now, with its own stated delay, on a public feed (nasstatus.faa.gov/api/airport-status-information, updated every few minutes, no key). We keep every snapshot of that feed and later set what the FAA stated against what flights delivered.
- Keeper: every tick of the tick bus (about 6 minutes) one GET of the feed with the user agent heuremen-airline/0.1 (+https://indahl.ai/airline). Stored per snapshot, as published: the update time, then for each ground delay program the airport, reason, stated average and maximum delay; for each ground stop the airport, reason and end time; for each general arrival or departure delay the airport, type, minimum, maximum and trend; for each closure the airport and reason. Nothing is rounded or filtered. A failed read is stored as NOTHING_RETURNED for that tick, never as no delays.
- Live display: the airports with a program or delay now, with the stated figures, the number of snapshots kept, and the first snapshot time. No outcome and no STACK row.
- The later test, written now and run when a BTS month covers the keeper's days: for each airport and UTC hour in which a ground delay program is on in two consecutive snapshots, the FAA's stated average delay for the program is compared with the mean arrival delay in minutes of flights scheduled to arrive at that airport in that hour in the BTS On-Time file (cancelled and diverted flights left out, arrival delay as reported with negatives kept). The unit is the program (an airport and its continuous run), the reading per program is the stated average minus the delivered mean, and the outcome is over programs with at least 10 flights in their hours: ABOVE if the lower end of a bootstrap interval over programs of the median difference is above 5 minutes, BELOW if the upper end is below minus 5 minutes, CONSISTENT if the interval lies within plus or minus 5 minutes, otherwise CANNOT_TELL. A planted program with a known delay in planted flights must return the planted reading before the real files are read.
- Known-good for the keeper: the parser on a planted copy of the feed with one of each program type must return each field, and a feed with no programs must return an empty list, not an error.
- Not claimed: that the FAA's stated delay is wrong or that a flight's delay was caused by the program.
