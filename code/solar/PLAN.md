# SOLAR: stated space-weather chances against what happened. Plan, written and committed before any stated chance was set beside an outcome.

## Claim read
The NOAA Space Weather Prediction Center (SWPC) issues the Report and Forecast of Solar and Geophysical Activity (RSGA) every day at 2200 UTC. The product description (ftp://ftp.swpc.noaa.gov/pub/forecasts/RSGA/README, dated 3 January 2008) defines its stated chances:
- Part III, "Class M and class X: Probability forecast of the occurrence of one or more class-M or class-X x-ray flares for each of the next 3 days."
- Part III, "Proton flare: Probability forecast of a significant proton event at satellite altitudes (at least 10 pfu at energies greater than 10 MeV) for each of the next 3 days."
- Part VI, "Probability forecast of geomagnetic conditions at middle and high latitudes-the probability of at least one 3-hour K index, at the indicated level, for each of the next 3 days. Active: K = 4. Minor storm: K = 5. Major or Severe storm: K >= 6."
The README for the period covered says: "Activity from 2100 UTC the previous day to 2100 UTC on the current day, and predicted activity for next 3 days." Each Part III and Part VI header names the three dates, for example "Event probabilities 06 Nov-08 Nov". Day one is the UTC day after the issue date.

Question: for each stated chance, how often did the event happen, bin by bin, and is the stated chance inside the interval of what happened? A stated 30 percent that holds should see the event on about 30 percent of such days.

## Stated side (as originally published)
The SWPC Warehouse (ftp://ftp.swpc.noaa.gov/pub/warehouse/) holds every RSGA from 1996 "as originally published" (warehouse README). Yearly tar files for 2021 to 2025, daily files for 2026 in /pub/warehouse/2026/RSGA/. A re-issued or corrected copy is never used. Where a day has more than one RSGA file, the one with the earliest ":Issued:" line is used and the others are counted. From the first run on, each run of solar_tick.py also stores the current RSGA (services.swpc.noaa.gov/text/sgarf.txt) and the current files of the Warehouse day directory, at most one fetch per 6 hours, so the stated side is kept even if a later copy changes.

A forecast counts only if its ":Issued:" time is before 00:00 UTC of the day it states. A stated day whose forecast was issued later is counted as issued late and not scored.

## Frame (fixed now)
- Forecasts issued from 1 January 2021 (target days from 2 January 2021) to the newest day that has ended and has a delivered record.
- Why 2021: SWPC moved its primary X-ray input to GOES-16 in December 2019 or January 2020 (secondary sources disagree on the month) and with it stopped applying the 0.7 scaling factor to the 1 to 8 Angstrom flux. Flare classes before and after differ by a factor of about 1.4. Starting a year after the move keeps the frame on one flare scale.
- Lead: day one, day two and day three of each forecast are separate rows and separate cells.

## Delivered side
- Flares: SWPC Edited Solar Events lists, Warehouse yearly tar files 2021 to 2025 and daily files /pub/warehouse/2026/2026_events/. An XRA event (1-8A) counts. An M event is a day with at least one XRA event whose class is M1.0 or more (M or X). An X event is a day with at least one XRA event of X1.0 or more. The day is the UTC day of the event's maximum. A maximum written "////" uses the begin time. A maximum earlier than the begin time (HHMM) is on the next day.
- Proton events: SWPC list "Solar Proton Events Affecting the Earth Environment" (ftp://ftp.swpc.noaa.gov/pub/indices/SPE.txt). Its note: "SWO defines the start of a proton event to be the first of 3 consecutive data points with fluxes greater than or equal to 10 pfu." A proton event day is a UTC day in which an event in the list starts. The list is updated irregularly. Target days after the date of the list's last change (read from the FTP listing on each run) have no delivered record and read NOTHING_RETURNED.
- Geomagnetic: SWPC Daily Geomagnetic Data (DGD), Warehouse yearly files 2021 to 2025 and quarterly files /pub/indices/old_indices/2026Q*_DGD.txt. The RSGA does not name the station behind "middle latitudes" or "high latitudes". The DGD lists eight 3-hour K indices a day under "Middle Latitude, Fredericksburg" and "High Latitude, College". Reading middle latitudes as Fredericksburg and high latitudes as College is our reading and is named as ours where it is printed. A day with any K missing (-1) at that station has no delivered record for that station.
- Planetary Kp from GFZ Potsdam (Kp_ap_Ap_SN_F107_since_1932.txt) is read for a described row only (see Described, not scored). The RSGA probabilities do not name the planetary index.
- A target day is scored once it ended at least 3 days before the run, so edited lists have settled.

## Events scored (fixed now)
Each is one event per target day, stated chance from the RSGA, delivered from the record above.
1. M-class flare: Part III "Class M", event = one or more flares of M1.0 or more. Reading Class M as M or greater is ours. The README text ("one or more class-M or class-X x-ray flares") supports both M or greater and M only. The M-only reading is described beside it.
2. X-class flare: Part III "Class X", event = one or more flares of X1.0 or more.
3. Proton event: Part III "Proton", event = a proton event starts that day.
4. Middle latitude storm, K 5 or more: stated chance = Minor storm + Major-severe storm (Part VI A). The README gives Minor as K = 5 and Major or severe as K >= 6, so for the day's greatest K the two are separate and their chances add. The sum is our reading. Event = Fredericksburg greatest K that day is 5 or more.
5. Middle latitude major or severe storm: stated chance = Major-severe storm (Part VI A). Event = Fredericksburg greatest K is 6 or more. This needs no reading of ours beyond the station.
6. High latitude storm, K 5 or more: as 4, Part VI B, College.
7. High latitude major or severe storm: as 5, Part VI B, College.
A stated sum above 100 is capped at 100 and counted.

## Ruler one: reliability by bin (decides)
Bins of stated percent, every integer in exactly one bin: 0 to 2, 3 to 7, 8 to 17, 18 to 27, 28 to 42, 43 to 57, 58 to 72, 73 to 87, 88 to 100.
Per event, lead day and bin: n scored days, the mean stated chance, the observed event frequency, and its 95% Wilson interval.
Bin outcome, the FORECAST desk's rule: ABOVE if the whole interval is above the mean stated chance (the event happened more often than stated), BELOW if the whole interval is below it, CONSISTENT if the mean stated chance is inside it, CANNOT_TELL while n is under 30.
The interval treats days as independent. They are not. Active regions persist for days and a forecast for day two shares most of its information with the forecast for day one, so the interval can be too narrow. The page says so beside every table. Ruler two uses a block bootstrap for this reason.

## Ruler two: Brier score against climatology (printed beside, decides nothing about bins)
Per event and lead day: Brier score BS = mean of (p - o) squared, p the stated chance as a fraction, o 1 or 0. Reference BS_clim = f(1 - f), f the observed event frequency over the same scored days (sample climatology). Skill BSS = 1 - BS / BS_clim. Interval: moving-block bootstrap over target days in date order, blocks of 27 consecutive days (one solar rotation), 2,000 replicates, seed 27, 2.5 and 97.5 percentiles.
Outcome: ABOVE if the whole interval is above 0 (better than climatology), BELOW if the whole interval is below 0, CONSISTENT if the whole interval is inside -0.05 to 0.05, otherwise CANNOT_TELL. Fewer than 30 scored days or fewer than 5 event days: CANNOT_TELL.

## Headline row (fixed now)
M-class flares, day one. The big number is the count of its bins that read consistent out of bins with 30 or more days. The line gives the bins above and below with their stated and observed figures, and the Brier skill with its interval.

## Counting, never folded
Per event and lead day, apart from the scored days: no RSGA on file for the issue day, a section that does not parse, issued late, no delivered record (missing events file, a missing K, a proton day after the list's last change, a day not yet settled). Each is counted and printed. None is counted as an event or as a non-event.

## Both alternatives
A. The stated chances describe what happened: most bins read CONSISTENT and the skill is above 0.
B. They do not: bins read ABOVE or BELOW, or the skill is not above climatology.
Either result is printed the same way. A bin that reads above or below says the stated chance and the observed frequency differ for this record and this method. It names no cause.

## Known-good gates (a failed gate turns every outcome into CANNOT_TELL)
1. Reader. Three stated rows read directly from the raw text of three RSGA files, picked from the stated side only and written into CHECKS.md, equal the parsed rows.
2. Dates. For every parsed RSGA, the first date in the Part III header is the issue date plus one day. At least 99 percent agree, and those that do not are not scored.
3. Join. On complete years, the day reading "at least one M or X flare" from the events lists agrees with the Daily Solar Data (DSD) X-ray flare counts (M plus X above zero) on at least 95 percent of days both records hold.
4. Rule. Synthetic rows with a known answer read ABOVE, BELOW, CONSISTENT and CANNOT_TELL correctly in both rulers, and heuremen_kit's self-test passes.

## Described, not scored
- M only reading of Class M: event = at least one flare from M1.0 to M9.9 that day.
- Planetary Kp 5 or more from GFZ against the middle latitude storm chance, and Kp 6 or more against major-severe, as a separate table labelled as a record the stated figure does not name.
- Literal reading of Minor storm: at least one K equal to 5, against the Minor storm chance alone.
- Reliability tables with each bin's block bootstrap interval beside the Wilson interval.

## Set aside
- The 3-Day Forecast (R1-R2, R3 or greater, S1 or greater) and the 3-day geomagnetic forecast (Active, Minor, Moderate, Strong-Extreme, planetary). SWPC keeps only the last 75 of each (ftp://ftp.swpc.noaa.gov/pub/forecasts/three_day and geomag_forecast). Each run stores the current ones so a later plan can score them. No outcome is given here.
- PCAF, the 10.7 cm flux and Ap predictions, the 27-day outlook.
- Forecasts before 2021.

## Reading done before this plan was written
- RSGA product README and the Warehouse README. RSGA files of 5 November 2026, 9 November 2026, 20 October 2026 and 15 March 2021 (stated side), and the current 3-day forecast and 3-day geomagnetic forecasts of 24 August, 20 October, 5 November and 9 November 2026, read to learn the formats.
- Delivered side, format only: the 5 November 2026 events file (one M3.5 at 1833 seen), DGD rows for 1 to 13 January 2025 and 8 to 10 November 2026, DSD rows for 1 to 7 January 2025, SPE.txt lines for 2021 and early 2022 and its last entry (12 November 2025), the GFZ file header. Field counts per line of the DGD and DSD files.
- No stated chance was set beside an outcome. No bin, rate or score was computed.

## Terms recorded
- NOAA SWPC products and data: works of the US government, public domain in the United States. The Warehouse README asks users to read the SWPC disclaimer and says the Warehouse holds preliminary reports as originally published, and that SWPC "does not encourage the use of preliminary data for research purposes". The page says the delivered records are SWPC's preliminary records.
- GFZ Kp: CC BY 4.0 (file header), cite Matzka et al. 2021, doi 10.1029/2020SW002641, and the data publication doi 10.5880/Kp.0001. The sunspot numbers in the same file are CC BY-NC 4.0 and are not used or republished.
- Reads are paced, one at a time, with a user agent that names this desk.

## Addendum 1 (10 November 2026, after the first read of outcomes)
Decided after the data and labelled so wherever it shows.
1. Report day. The first read keyed each report by the date on its ":Issued:" line. A report can go out after midnight (the report of 25 April 2024 says ":Issued: 2024 Apr 26 0015 UTC" and "SDF Number 116 Issued at 2200Z on 25 Apr 2024"), so that read put 13 late reports on the next day, where they then displaced that day's own report. From this addendum a report belongs to the day its SDF line names. The issued-late rule is unchanged and uses the ":Issued:" time, so day one of a report issued after midnight is counted as issued late and not scored. No threshold, bin or event changed.
2. Corrections. One Warehouse file is a correction ("SDF Number 152 Correction", report of 1 June 2024, issued 2 June) and one is an amendment ("(AMD)", 3 December 2024, filed as 2024onRSGA.txt). The plan already says a corrected copy is never used. The code now refuses both by name and counts them.
3. Proton events are held. The delivered list (SPE.txt, last changed 13 November 2025) leaves out proton events that SWPC's own daily reports record. The RSGA of 23 March 2024 says "Protons greater than 10 MeV at geosynchronous orbit reached a peak level of 955 pfu at 23/1820Z" and SPE.txt has no event in March 2024. Scored against an incomplete list, a stated chance would read too high. The proton cells read CANNOT_TELL on the page with this reason, and their computed figures stay in the data, labelled as held. A later plan can score proton days from GOES proton flux.
4. Display only, after the data: the proton cells read again with an event day being any day from a listed start through its maximum. It is kept in the data and not printed.

## Addendum 2 (10 November 2026, after the outside referee, solar_index_referee/REFEREE.md)
1. Events reader. The outside recount found that the desk's reader dropped every X-ray line whose event number is under 1000. Those numbers are printed with a leading space, and the reader required a digit at the start of the line. 1,800 of 18,243 X-ray lines were lost. It was found through the Daily Solar Data cross-check (gate 3) and a row-by-row recount, not by reading the forecasts. The reader now allows the leading space and requires the 1-8A channel. M-class days on day one went from 693 to 761 and X-class days from 76 to 87. The headline moved from 7 of 8 bins consistent to 4 of 8. Gate 3 now agrees on 1,810 of 1,821 days, and 10 of the 11 days left are flares that began before midnight and peaked after it, which the Daily Solar Data counts on the begin day and this plan counts on the peak day. The disagreeing days are printed with the gate.
2. The amendment file is now read and refused by name, so two reports are counted as refused.
3. Held proton figures are kept in data/solar.json only. The summary, the feed and the page show the held cells without figures.
4. Display only, after the data: the headline line also gives the M-class day-one bins read on the block bootstrap interval and the count of bins across every scored cell. The middle latitude storm chances are also read against SWPC's estimated planetary K from the same Daily Geomagnetic Data. These decide nothing.
No threshold, bin, event or rule changed.
