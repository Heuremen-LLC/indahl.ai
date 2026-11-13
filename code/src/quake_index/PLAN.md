# QUAKE: USGS aftershock forecasts against the aftershocks that happened. Plan, written before any stated probability or range was set beside a count.

## Claim read
After significant earthquakes in the United States and its territories, the USGS publishes an aftershock forecast. It is the "oaf" product in the ComCat event service (earthquake.usgs.gov/fdsnws/event/1). Each version states, for windows of one day, one week, one month and one year, and for magnitudes 3, 4, 5, 6 and 7 and above (earlier versions: 3, 5, 6 and 7), the probability of at least one earthquake and a range for the number. The USGS pages say (fetched 10 Nov 2026):
- Overview (https://earthquake.usgs.gov/data/oaf/overview.php): "Forecasts are posted for earthquakes of M4+ in the contiguous United States and M5+ in other U.S. states and territories". "We also compute forecasts for some smaller earthquakes that are of particular public interest". "Forecasts are updated regularly."
- Scientific background (https://earthquake.usgs.gov/data/oaf/background.php): the probability is "The probability of at least one aftershock in the given magnitude range and time period", "prob(N≥1)=1-P(0)". "The likely number of aftershocks is given as the 95% confidence range, Nmin to Nmax, where prob(N≤Nmin)≈0.025 and prob(N≤Nmax)≈0.975". It says "the equalities are approximate due to the inherent discreteness of the P(N) distribution."
- Schedule (https://earthquake.usgs.gov/data/oaf/schedule.php, headed as of December 20, 2021): "Further forecasts are initiated daily at days 1 to 14, every three days for days 16 to 28, every 7 days for days 35 to 357, and a final forecast is issued at day 365."
- No USGS page found states how the forecasts have performed or how well calibrated they should be.

Questions: (a) when the USGS states a probability of at least one earthquake, how often did at least one happen, by bin of stated probability? (b) how often did the number that happened fall inside the stated 95% range?

The 95 percent is the USGS's own figure. A stated probability is read as the share of windows that should see at least one event among windows given that probability. Both readings are the plain reading of the USGS wording.

## Can earlier statements be fetched (scouted before this plan)
Yes. The event service keeps every version of a product when asked with includesuperseded=true. Each version carries its updateTime (when it entered ComCat) and its forecast file. A query for producttype=oaf from 2000 on returned 253 events at scouting time, the first on 6 July 2019 (Ridgecrest) and the last on 10 Nov 2026.

## Data
Stated side. Every event the event service lists with producttype=oaf at run time. For each event, every archived version of its oaf product. For each version, forecast.json (inline in the event record for some 2019 to 2023 versions, otherwise at its own address under earthquake.usgs.gov/product/oaf/). Each window has timeStart, timeEnd, a label and bins of magnitude, probability, p95minimum and p95maximum, and an aboveMainshockMag probability.

Delivered side. The ComCat catalog from the same event service, read at run time: every event of type earthquake from the mainshock time on, inside a circle around the mainshock that reaches the far edge of every zone stated for that event, down to 0.05 below the lowest stated magnitude. Time, epicentre, depth, preferred magnitude and the list of event IDs are kept.

All sources are public and need no key. Requests are paced, with a user agent that names this desk. Every response is kept in data/raw.

## Frame (fixed now)
- Events: every event with an oaf product. None is picked by us.
- Versions: every version with status UPDATE and a readable forecast. A version deleted (status DELETE) or whose forecast cannot be read is counted as product missing, by version, and gives no rows.
- A window counts only if the version's updateTime is at or before the window's timeStart, so the forecast was public before the window opened. A window that opened before its version was public is listed apart and not scored.
- Zone, exactly as the product states it. First the forecast.json model parameters regionType, regionCenterLat, regionCenterLon and regionRadius (km). If forecast.json states no region, the same version's forecast_data.json parameters aftershock_search_region (centre and radius in km) with its min_depth and max_depth (km). forecast.json states no depth, so none is applied when its region is used. A version whose product states no zone reads CANNOT_TELL, zone not stated, counted apart. A zone of another shape than those reads CANNOT_TELL, zone not readable.
- Count. ComCat events of type earthquake with time at or after timeStart and before timeEnd, preferred magnitude at or above the bin magnitude at the precision ComCat serves, epicentre inside the zone (great-circle distance on a sphere of radius 6371 km), depth inside the stated depth range when one is stated. The mainshock is left out: any catalog event sharing an ID with the mainshock event's ID list.
- A window is scored only when timeEnd is at least 7 days before the run and the catalog copy was read at least 7 days after timeEnd. Until then it reads NOTHING_RETURNED, window not closed, or NOTHING_RETURNED, catalog not read. These are counted apart from every outcome.
- One row is one version, one window and one magnitude bin. The aboveMainshockMag probability gives one more row per window, with no range.

## Rules (fixed now)
Row outcome for the range. Stated range is [p95minimum, p95maximum].
- CONSISTENT: the count is inside the range, ends included.
- ABOVE: the count is above p95maximum.
- BELOW: the count is below p95minimum.
- CANNOT_TELL: unreadable (a missing value, a probability outside 0 to 1, or minimum above maximum), zone not stated, zone not readable.
Row outcome for the probability: occurred (count at least 1) or not.

Dependence. Windows from one sequence overlap and are correlated: every version of one event counts the same aftershocks, and the day, week, month and year windows of one version are nested. Two events whose epicentres are within 100 km and whose times are within 365 days are put in one block, chained. Every interval below is computed two ways: a 95% Wilson interval, which treats rows as independent, and a block bootstrap that resamples whole blocks with replacement, 2,000 resamples, seed 20261110, percentile interval. The interval used for every outcome is the union of the two (the lower of the two lower bounds, the higher of the two upper bounds). The page says so.

Range cells. Share of scored rows inside the range.
- Cell outcome against the stated 95 percent: BELOW if the upper bound is under 0.95. ABOVE if the lower bound is over 0.95. CONSISTENT if the lower bound is 0.925 or more and the upper bound is 0.975 or less. Otherwise CANNOT_TELL. Fewer than 30 scored rows or fewer than 10 blocks is CANNOT_TELL.
- Headline cell: M3 and above, every window, every version.
- Further cells: each magnitude (3, 4, 5, 6, 7), every window. M3 and above by window (day, week, month, year). Every magnitude and window together.

Probability cells. Rows with a range (the magnitude bins), grouped by stated probability: 0 to 1, 1 to 5, 5 to 10, 10 to 20, 20 to 40, 40 to 60, 60 to 80, 80 to 90, 90 to 99, and 99 to 100 percent (lower end included, upper end not, 100 percent in the top bin). Observed share is rows with at least one event over scored rows. The stated value of a bin is the mean stated probability of its rows.
- Cell outcome: ABOVE if the lower bound is over the stated value. BELOW if the upper bound is under it. CONSISTENT if the whole interval is within a tolerance of the stated value, where the tolerance is the largest of 0.01 and the smallest of 0.05, half the stated value and half of one minus the stated value. Otherwise CANNOT_TELL. Fewer than 30 scored rows or fewer than 10 blocks is CANNOT_TELL.
- The aboveMainshockMag rows form one more probability cell of their own, by the same rule. They are not mixed into the bins.

Described and not scored: the first version of each event alone (range and probability cells), the range cell split by whether the mainshock was located by the USGS national network (net us) or a regional network, the Brier score of the binned rows, the range outcome with magnitudes rounded to one decimal before the comparison, and the rows farthest outside their range.

## Both alternatives
A. The stated ranges hold the count about 95 percent of the time and the stated probabilities match the observed shares. Cells read CONSISTENT, or CANNOT_TELL with shares near the stated values.
B. They do not. Range cells read ABOVE (the ranges hold the count more often than 95 percent) or BELOW (less often), and probability bins read ABOVE (at least one happened more often than stated) or BELOW (less often).
Either result is printed the same way. A reading says how often the stated figure held. It names no cause.

## Known-good gates (a failed gate turns every outcome into CANNOT_TELL)
1. Format. At least 95 percent of versions parse with a forecast list whose windows carry bins, and the catalog features carry a time and a magnitude.
2. Reader. For three forecast files (first, middle and last by file name), the first bin of the first window read from the raw text with a pattern equals the parsed values. The rows are written into data/known_good_rows.json and CHECKS.md.
3. Counter. Each version reports observations: the number of M3 and above aftershocks USGS had counted when it was issued. For versions whose model name says Sequence Specific, whose zone is stated and whose M3 observation is at least 1, our count of M3 and above in the stated zone from just after the mainshock to the version's creationTime agrees within the larger of 2 and 20 percent in at least 80 percent of at least 20 such versions. A counter that reads the wrong zone or the wrong times fails this. This compares counts before each forecast was issued and never a forecast with what followed.
4. Rule. Synthetic rows with a known answer read ABOVE, BELOW, CONSISTENT and CANNOT_TELL correctly for the range rule, the range cell rule and the probability cell rule, and heuremen_kit's self-test passes.

## Set aside
- Spatial forecasts. The USGS says it does not issue them.
- fractileProbabilities, barLabels and every other field of the product not named above. ETAS and other model parameters are kept in the raw files and not scored.
- Forecasts not posted as an oaf product in ComCat.
- A judgment of the model. A reading is a count against a stated figure.

## Reading done before this plan was written
- The event list (253 events), every event record with its archived versions (metadata and inline bytes), and forecast.json files of versions read so far, to learn the format and count which versions state a zone. Of the forecast files read at plan time, those from 2022 on carry regionType circle, and those from 2019 to 2021 and most from 2022 and 2023 carry no region in forecast.json. Version metadata shows forecast_data.json for some of those earlier versions.
- One forecast_data.json (Ridgecrest, version of 3 Nov 2026) was opened in full. It holds the aftershock_search_region circle (60 km), min_depth -5 and max_depth 700, and USGS's own catalog count for its fit. One forecast.json for the same version and the first Ridgecrest version were opened in full, including their observations (counts USGS had before issuing).
- The USGS overview, scientific background and schedule pages.
No ComCat catalog of aftershocks was read. No stated probability or range was set beside a count of what followed.

## Terms recorded
- USGS-authored or produced data and information are in the public domain (USGS copyright policy, https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits). The event service needs no key. Requests are paced and carry the user agent heuremen-quake/0.1 (+https://indahl.ai/quake). The bulk read of archived forecast files uses at most four connections, each pausing between requests. The rider reads new versions one request at a time.
