# Check blocks (watch/readcheck.py). One entry per reading, appended, never edited after commit.

## Data access and terms (scouted 10 Nov 2026)
- SWPC Warehouse, ftp://ftp.swpc.noaa.gov/pub/warehouse/: RSGA from 1966, yearly tar files for past years, day files for the current year. README: "The historical products in this SWPC Warehouse are the preliminary reports as originally published. SWPC does not encourage the use of preliminary data for research purposes." Edited Solar Events (yearly tar, day files for the current year, each day file re-created for a few days after the day, "Updated every 5 minutes"). DGD and DSD yearly files at year end, quarterly files for the current year in /pub/indices/old_indices/. SPE.txt in /pub/indices/, last changed 13 November 2025.
- The HTTPS mirror of the FTP host timed out on 10 Nov 2026. FTP works. services.swpc.noaa.gov/text/ serves the current sgarf.txt, 3-day-forecast.txt and 3-day-geomag-forecast.txt over HTTPS.
- /pub/forecasts/three_day and /pub/forecasts/geomag_forecast keep the last 75 issues only. Not in the Warehouse. Stored by the rider from its first run, not scored.
- NOAA SWPC products: US government works, public domain in the United States. SWPC disclaimer referenced in the Warehouse README.
- GFZ Potsdam Kp file (https://kp.gfz.de/app/files/Kp_ap_Ap_SN_F107_since_1932.txt, moved from kp.gfz-potsdam.de): "LICENSE: CC BY 4.0, except for the sunspot numbers contained in this file, which have the CC BY-NC 4.0 license". Only Kp is read. No sunspot number is stored in any output.
- Reads: one at a time, about 1 s apart, user agent heuremen-solar/0.1 (+https://indahl.ai/solar).
- Event definitions quoted from ftp://ftp.swpc.noaa.gov/pub/forecasts/RSGA/README (3 January 2008) and the SPE.txt note.
- Reader rows (gate 1) in data/known_good_rows.json, read from the raw text of the RSGA of 15 March 2021, 5 November 2026 and 9 November 2026, stated side only.

## 2026-11-10 SOLAR first read and ship after the outside referee: SWPC RSGA stated chances (as first published) against SWPC edited events and Daily Geomagnetic Data, 2021 on, reliability bins and Brier skill, proton held
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: PLAN.md committed 07b57e8 at 14:19:32Z (sha256 12c748f4, data/plan_seal.json), first comparison 14:25:43Z. Code first committed after the first read (92b157b), referee note 9. Same quantity both sides per event (stated percent for a UTC day, delivered yes or no for the same UTC day). Not-scored days counted apart per cell and never folded
- II: holds: every bin prints n, events, mean stated, observed and interval. Brier score, base rate and skill printed beside, never in place of, the bin reading
- V: holds: ruler one decides (Wilson, n of 30 or more). Ruler two (Brier skill, 27-day block bootstrap, 2000 reps, seed 27, one generator per cell) printed beside. Block bootstrap reading of the M day-one bins (display, Addendum 2): 6 of 8 consistent
- VI: holds: headline M-class day one 4 of 8 bins consistent, 4 above, 0 below, Brier skill 0.2683 (0.2086 to 0.3225) ABOVE. All scored bins: 34 consistent, 16 above, 58 below
- VI row: M day 1 scored 2114 events 761 skill 0.2683 (0.2086 to 0.3225) ABOVE bins {"ABOVE": 4, "CONSISTENT": 4}
- VI row: X day 1 scored 2114 events 87 skill 0.0149 (-0.1167 to 0.1317) CANNOT_TELL bins {"BELOW": 3, "CONSISTENT": 2}
- VI row: MID5 day 1 scored 2047 events 182 skill 0.0085 (-0.0814 to 0.0807) CANNOT_TELL bins {"BELOW": 6, "CONSISTENT": 1}
- VI row: MID6 day 1 scored 2047 events 49 skill 0.0986 (-0.0315 to 0.1983) CANNOT_TELL bins {"BELOW": 2, "CONSISTENT": 2}
- VI row: HI5 day 1 scored 2060 events 889 skill -0.0472 (-0.1027 to 0.0026) CANNOT_TELL bins {"BELOW": 5, "CONSISTENT": 1}
- VI row: HI6 day 1 scored 2060 events 440 skill -0.0904 (-0.1638 to -0.0338) BELOW bins {"BELOW": 6}
- V described: estK5 days 2110 skill 0.1494 (0.1008 to 0.1921)
- V described: gfzKp5 days 2115 skill 0.1325 (0.0839 to 0.1737)
- R: holds: gates reader, dates (2132 of 2134), join (1810 of 1821, 10 of the 11 left are midnight-crossing flares, the other 4 Oct 2022), rule all passed. Outside referee recount (solar_index_referee/code/recount.py, own readers, own Wilson, own bootstrap) reproduced the 15 non-flare cells exactly and caught the flare reader
- P4: holds: no cause named. Middle latitude below readings are printed with the station caveat and the planetary table at the same size
- P6: fixed: referee finding 1, the events reader dropped X-ray lines whose event number is under 1000 (leading space). Headline moved from 7 of 8 to 4 of 8. Findings 3 to 7 fixed in code and copy (PLAN Addendum 2)
- P6 proton: caught: SPE.txt omits events SWPC daily reports record (23 March 2024, 955 pfu). Proton cells held, figures data-only (PLAN Addendum 1 item 3)
- P9: holds: lint_copy.py 0 hits on solar.html, no semicolons, no digits in headings, Heuremen LLC named, our readings marked
- O1: holds: rider on the tick bus every 60 ticks with --publish, puts solar_live in KV, worker serves /solar/live.json
- O5: holds: solar_tick.py chdirs to its folder, standard library only, wrangler by absolute path
- III: holds: above and below bins keep their side and are printed apart with stated and observed percent per bin. M-class reads above in 13 of 24 bins with 30 days or more, the storm events mostly below
- P1: holds: RSGA README definitions ("probability forecast of the occurrence of one or more class-M or class-X x-ray flares", "the probability of at least one 3-hour K index, at the indicated level") and the 23 March 2024 RSGA sentence ("reached a peak level of 955 pfu") copied from the fetched files on 10 Nov 2026
- P2: holds: page figures come from summary_solar.json through build_page.py and solar_headline.py, the feed /solar/live.json is the same summary, every row is in data/solar.json. Sources named with the Warehouse path
- P3: holds: Class M, Class X, minor storm, major-severe storm and K as SWPC prints them. Readings of ours (M or greater, the sum for K 5 or more, Fredericksburg and College) are named as ours on the page
- P5: holds: every bin interval labelled 95% Wilson, the skill interval labelled 95% block bootstrap over 27-day blocks, the independence statement beside the tables
- P7: holds: ledger rows solar.* written before the site edit, release through ledger/ship.sh only, live check after the ship
- P8: cannot tell: checked after the ship on the live page (recorded in the ship report)
- P10: holds: after-data items labelled in PLAN Addendum 1 and 2: report day from the SDF line, corrections refused by name, proton held, reader fixed after the referee, block bootstrap headline count, all-bins count and estimated planetary K rows as display only
- O2: holds: a failed fetch names its source in sources.stale and the run uses the files on disk, a failed KV put is logged as publish FAILED, a failed gate turns every outcome into cannot tell
- O3: n/a: no GPU used, network reads and arithmetic on the CPU only
- O4: holds: the feed carries generated and updated, data/solar_history.jsonl gets one line per run, the live headline row reads it as stale after its cadence
- O6: n/a: no GPU job runs in this rider

## 2026-11-12 10:30 SOLAR migrated to the Faults and Guards 2.0 outcome rule (PLAN_ADDENDUM_std2.md): bins read against the mean stated chance with no CONSISTENT, skill read against the band edges, reasons beside CANNOT_TELL, REQ-13 line
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: data, sources, frame, events, bins, gates, Wilson interval and the 27-day block bootstrap (2,000 draws, seed 27) unchanged. The offline re-run (generated 15:26 UTC) gave the same bin and skill numbers as the 14:40 UTC summary for every cell, only outcome and reason fields and the outcome counts differ
- II: holds: the 34 bins that moved are counted per event and day ahead and kept apart (over the three days ahead: M 11, X 6, MID5 3, MID6 8, HI5 4, HI6 2). ABOVE 16 and BELOW 58 stay as they were, never netted
- III: holds: above and below bins keep their side. The three skill cells that moved (HI5 day 2, HI6 day 1 and day 2) all moved from BELOW to CANNOT_TELL with the same negative sign, nothing turned positive
- V: holds: the ruler is the plan's. The addendum f74e52a and 93bd08c, committed before the new run, retires CONSISTENT for a point figure with no tolerance and reads the 0.05 skill band as the standard defines it. The owner's call is flagged for that second change
- VI: holds: four outcomes with a reason on every CANNOT_TELL (34 STRADDLES_EDGE among scored bins, 27 TOO_WIDE_TO_RESOLVE, 54 NO_INTERVAL_FORMABLE with the held proton cells). Both-alternatives test not applied because the plan names no size that matters, said on the page
- R: holds: the big number 4 of 8 and the REQ-13 line (7 NOTHING_RETURNED, CANNOT_TELL 4 of 8) are computed by K.req13 in solar_tick.py and read from summary_solar.json, nothing typed. The plan seal is untouched
- P1: holds: the quoted RSGA README sentences were not touched by this change
- P2: holds: page figures still come from summary_solar.json through build_page.py and solar_headline.py, the feed carries reason and req13 on the cells, the headline and the forecasters rows
- P3: holds: the column that counted consistent bins is now headed Cannot tell and counts the same bins, and the page says why no bin reads consistent
- P4: holds: no cause named for a bin or a skill that cannot be told
- P5: holds: the Wilson and block bootstrap labels and the independence note beside the tables are unchanged, the rule note lists the three reasons
- P6: fixed: the headline sentence said the share of days fell inside the interval of the stated chance in 4 of 8 bins. It now says the interval held the stated chance and the bins read cannot tell (STRADDLES_EDGE). The block bootstrap sentence no longer says consistent
- P7: holds: ledger row solar.hi6_1.skill set BELOW to CANNOT_TELL before any page ships, only the desk draft solar.html was rebuilt. Nothing shipped, ship.sh not run
- P8: cannot tell: the page was built to solar.html and read as text, it was not rendered in a browser because nothing was deployed
- P9: holds: lint_copy.py 0 hits after rewording one clause, no semicolons in the addendum
- P10: n/a: no label added after the data, the retired rule is stated in the addendum dated before the run
- O1: holds: the rider on the tick bus is unchanged, solar_tick.py --offline re-ran in 23 s with no network, --selftest passed all four gates (reader, dates, join, rule)
- O2: holds: failed gates give CANNOT_TELL with reason NO_INTERVAL_FORMABLE, failed reads are counted as NOTHING_RETURNED beside the headline
- O3: n/a: no GPU used
- O4: holds: the offline run wrote summary, live feed and a history row that carries the reason
- O5: holds: paths and imports unchanged, standard library plus the desk's kit copy
- O6: n/a: no GPU job started by this change
