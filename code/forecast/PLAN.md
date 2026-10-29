# FORECAST: stated chance of precipitation against what happened (28 Oct 2026, his word)
Written and committed before any forecast was stored or scored.

## What is stated
The National Weather Service gridpoint forecast (api.weather.gov), probabilityOfPrecipitation for each 12 hour period, at the location of each of 30 major United States airports (stations.json). A forecast is fetched for a station at most once every 6 hours, on Nova's ticks. Each stored forecast keeps every period up to 48 hours ahead with its stated chance and its lead in hours (start of period minus the time fetched). A period whose chance is null is not stated and is dropped and counted. Our user agent names this site.

## What is delivered
The hourly observations of the same station (api.weather.gov observations): an event occurred in a period if any observation in it reports precipitation in the last hour above zero, or a present-weather entry for rain, drizzle, snow, sleet, hail, showers or thunderstorm. A period is unscorable if observations are missing for more than 25% of its hours, and is counted as unscorable. A period is scored after it has ended and the observations for it are held.

## Calibration (the reading)
Stated chances are grouped into bins: 0 to 5, 10 to 20, 30 to 40, 50 to 60, 70 to 80, 90 to 100, and by lead: under 12 hours, 12 to 24, 24 to 48. Per bin and lead: the mean stated chance, the number of scored periods n, the observed event frequency with a Wilson 95% interval. Outcome per bin: ABOVE if the interval lies above the mean stated chance (it rained more often than stated), BELOW if it lies below (less often), CONSISTENT if the stated chance sits inside it, CANNOT_TELL while n is under 30.

## Known limits, stated up front
Hourly reports can miss a short shower between observations, so observed frequency is a floor. The floor is measured: the share of periods with a stated chance of 0 or 5 that nevertheless had an event is published beside every table. Periods from the same storm and neighbouring stations are not independent, so n is not the number of independent events and intervals are read with that in mind. Forecasts for the same period at different leads are separate rows. One forecaster is read, the National Weather Service, and no other is compared in this plan.

## Not claimed
No ranking of forecasters, no claim about any person. A bin that reads above or below says the stated chance and the observed frequency differ for these stations and this method.

## Addendum 1 (28 Oct, after the first round, before any period was scored)
A period that had already started when the forecast was fetched (negative lead) is stored but is not read: part of it was already known. Only periods with a lead from 0 to 48 hours enter the bins.

## Addendum (29 Oct 2026, after publication): Wilson interval corrected
The local Wilson function in this corner omitted the division of the half-width by d = 1 + z squared over n, so published 95% intervals were wider than the Wilson interval this plan names (up to 38% wider at n = 10, about 5% at n = 100). It was found on a read of the code while moving corners onto the shared kit, whose function is tested against planted worlds. The corner now uses the kit function and the page was republished. No verdict changed: FORECAST had no scored cell yet, so no outcome rested on an interval.
