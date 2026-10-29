# AIRQ: PurpleAir sensors against the EPA's own targets and the EPA's regulatory monitors. Plan, committed before any sensor or monitor data is read.

## The statements read
1. The EPA report "Performance Testing Protocols, Metrics, and Target Values for Fine Particulate Matter Air Sensors" (February 2021), Table ES-2, base testing. Targets for a PM2.5 sensor compared with a reference monitor, on valid 24-hour averages: bias slope 1.0 plus or minus 0.35; intercept between minus 5 and plus 5 micrograms per cubic metre; coefficient of determination at least 0.70; error as RMSE at most 7 micrograms per cubic metre, or NRMSE at most 30 percent, either one meets it. RMSE is the error between the sensor and the reference values (the report's Eq. 5), not the spread around a fitted line. NRMSE is the RMSE divided by the mean of the reference values, times 100. The precision target needs two sensors at one site and is not tested here.
2. Barkjohn and others, Atmospheric Measurement Techniques 14, 4617 (2021): the PurpleAir PM2.5 correction PM2.5 = 0.524 times PA(cf_1) minus 0.0862 times RH plus 5.75, where PA(cf_1) is the mean of channels A and B and RH is in percent; and the cleaning rule that a 24-hour value is valid when channels A and B differ by less than 5 micrograms per cubic metre or less than 61 percent (percent difference = 2 times |A minus B| over (A plus B)). The same paper says the PurpleAir map shows the lower cf_atm reading and calls it raw.
These are targets and a published correction, not claims by PurpleAir. We measure what the sensors that are publicly reporting do against the numbers the EPA wrote down.

## Data
- Monitors: the EPA Air Quality System (AQS) API, daily data for parameter 88101 (PM2.5, FRM and FEM), calendar year 2025, every state. A monitor-day is valid when the record has at least 75 percent of its hours; one record per site and day (the lowest POC number). Monitor coordinates come from the same API.
- Sensors: the PurpleAir API. For each monitor, outdoor sensors within 200 metres of the monitor coordinates (bounding box, then distance). For each such sensor the 24-hour averages of channels A and B for cf_1 and atm, and humidity, for 2025.
- Budget: the PurpleAir account holds 1,000,000 points. The code reads the balance before every sensor and stops the read when fewer than 400,000 points remain, listing what was not read.

## Rule (fixed now)
- A sensor-day is kept when both channels are present and the A and B cleaning rule above holds, and the monitor-day is valid. A pair is a sensor and a monitor with at least 30 kept days (the 30-day minimum of the EPA base test).
- Three readings per pair, each against the same targets: R1, the mean of the atm channels (what the map shows as raw); R2, the mean of the cf_1 channels; R3, the correction above applied to cf_1 and humidity.
- Per pair and reading: slope and intercept of the sensor on the monitor by ordinary least squares, R squared, RMSE and NRMSE against the monitor values. A pair meets the targets when all four conditions of Table ES-2 hold.
- Headline per reading: among pairs, the share that does NOT meet the targets, with a 95 percent Wilson interval. The unit for the interval is the monitor, so a monitor with several sensors counts once, by taking the pair with the median RMSE. The claim read is the EPA's target, whose natural expectation for a sensor said to be usable is that it meets it. ABOVE if the lower end of the share not meeting is above 0.50. CONSISTENT if the upper end is below 0.50. Otherwise CANNOT_TELL. A share of one half is the point where fewer than half of monitors have a sensor that meets the EPA's own targets.
- With fewer than 30 monitors the outcome is CANNOT_TELL and the count says why.
- Printed beside, not tested: the median slope, intercept, R squared and RMSE for each reading, the number of monitors, sensors, days, and the days removed by the A and B rule.

## Known-good, run before the real reads
Planted series through the metric code: a sensor equal to the monitor must meet all four targets; a sensor reading twice the monitor must fail the slope; one reading the monitor plus 8 must fail the intercept and the RMSE; one with pure noise must fail R squared. The correction is checked at one point by hand (cf_1 of 10 and RH of 50 must give 6.69). The AQS key and the PurpleAir key are tested with one harmless call each before the run.

## Hand check
The five monitors with the largest RMSE for R3 and the five with the smallest are opened: the sensor and monitor coordinates, the distance, and ten paired days are read by hand against the raw responses.

## Not claimed
That a sensor fails a requirement: the targets are for testing and nothing obliges a deployed sensor to meet them. Anything about sensors that are not outdoors, not publicly reporting, or not near a monitor. That the sensors near monitors are typical of sensors elsewhere. Anything about a year other than 2025. The precision target.

## Addendum 1 (29 Oct, before any real data was read)
What was read so far: one AQS response for one small state and one month, to see the record layout, and the PurpleAir point cost of two tiny calls. Nothing was scored. Three things changed in the design, because the PurpleAir history API gives daily averages only on UTC days (checked: the returned times are midnight UTC whatever start time is asked for), and an hourly year per sensor costs about 44,000 points, so the account could read about 20 sensors.
1. Window: 1 June to 30 September 2025 (122 UTC days), not the whole year. It includes the 2025 smoke season, in line with the EPA report's recommendation of at least one 24-hour mean of 25 micrograms per cubic metre or more.
2. Monitor values: built from AQS hourly PM2.5 data (sampleData, parameter 88101, 1 HOUR duration, continuous monitors) into UTC-day means, using the hourly records that carry no qualifier flag, and a day is valid when it has at least 18 of 24 hours. This puts monitor and sensor on the same 24-hour window. Filter-based monitors (24-hour FRM samples that cannot be rebinned) are left out and counted.
3. Sensor fields: A and B channels for cf_1 and atm, plus humidity, as daily UTC averages. With about 610 points per sensor the budget rule (stop below 400,000 remaining) is not expected to bind.
Everything else in the plan stands: the targets, the correction, the cleaning rule, the 200 metre radius, the 30-day minimum, the unit for the interval, the outcome rule and the known-good checks.

Correction to the plan (29 Oct, before any real data was read). The hand check value for the correction was written as 6.69. The equation with cf_1 of 10 and RH of 50 gives 0.524 times 10 minus 0.0862 times 50 plus 5.75, which is 5.24 minus 4.31 plus 5.75, so 6.68. The known-good check uses 6.68.

## Note 1 (29 Oct, after the read and the hand check)
Read: 892 AQS continuous monitors with at least 30 valid UTC days from 1 June to 30 September 2025 (106 sites with only filter samples left out, as planned). 414 PurpleAir outdoor sensors within 200 m of one of them, all read, none left unread by the points guard. 211 pairs with at least 30 kept days, on 147 monitors, 18,213 kept sensor-days, 2,609 sensor-days removed by the A and B rule.
Result by reading, monitors whose sensor does NOT meet the four EPA targets: map reading (atm) 140 of 147, 95 percent [91, 98], ABOVE; cf_1 raw 143 of 147, 97 percent [93, 99], ABOVE; cf_1 corrected for humidity 66 of 147, 45 percent [37, 53], CANNOT_TELL. Median over monitors, map reading: slope 1.61, intercept minus 1.17, R squared 0.79, RMSE 4.75; cf_1 raw: 1.81, minus 2.19, 0.79, 5.37; corrected: 1.00, minus 0.17, 0.82, 1.95.
The raw readings fail the slope target (1.0 plus or minus 0.35) for most monitors while meeting RMSE and R squared; the corrected reading has a median slope of 1.00.
Hand check: the five pairs with the largest and the five with the smallest RMSE for the corrected reading were recomputed from the raw saved responses by a separate routine, from the monitor's UTC-day means and the sensor's A and B channels and humidity. All ten RMSE values equal the code's (largest 4.56 to 5.50, smallest 0.87 to 1.04). Distances are 0.1 to 174 m, the ranges are plausible, and no pair is made of a sensor and a monitor with a stated location error. Not claimed, unchanged: the targets are for testing and nothing obliges a deployed sensor to meet them.
