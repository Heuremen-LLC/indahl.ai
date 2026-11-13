# Check blocks (watch/readcheck.py). One entry per reading, appended, never edited after commit.

## 2026-11-10 10:05 SEASONAL desk first read: CPC 3-month outlook chances (0.5-month lead, 2 degree grid) against the observed tercile, and our Heidke recompute against CPC's stated scores
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: PLAN.md committed 11d602cf at 09:42:56 -05:00 (data/plan_seal.json), first comparison after it. Same files CPC verifies with. 380 seasons (JFM 1995 to ASO 2026), 232 land cells, 3 forecasts waiting per variable, 0 unreadable rows
- II: holds: each category and bin read apart, observed frequency beside mean stated chance
- V: holds: plan ruler moving-block bootstrap over seasons, block 12, 2,000 draws. Second ruler Heidke recompute, unweighted
- VI: holds: temperature leaning ABOVE (stated 48.2, observed 60.1, 54.9 to 64.2). Precipitation leaning CONSISTENT (45.3 against 45.5, 42.0 to 48.5). Temperature above-normal bins from 31 percent up all ABOVE, below-normal bins under 36 BELOW, near normal at equal chances BELOW (33.3 against 28.7). Heidke recompute CONSISTENT for both variables and both scores (temperature 380 of 380 seasons within 1 point, precipitation 373 of 374)
- P6: caught: first selftest run failed: the chance-level Heidke case had one correct cell of six, not two. The planted case was fixed. A float32 broke the summary write. Neither run printed an outcome
- P4: holds: no cause named. The normals period behind the observed thirds is not stated in CPC's files and the page says so
- P9: holds: lint_copy.py 0 hits
- O2: holds: failed fetches name the file in sources.stale and the run uses the last copies
- O5: holds: seasonal_tick.py chdirs to its folder, numpy plus standard library

## Data access and terms (scouted 10 Nov 2026)
- CPC verification directory, keyless, read at most once a day. Gridded files tracked in data/raw/cpc_verif_grid as a dated copy.
- NOAA/NWS: public domain (weather.gov/disclaimer), credited, not presented as NWS material.
- No division-level archive of past outlooks with observed categories found. Shapefiles (2007 on) hold contours for all leads and are set aside.

## 2026-11-10 10:10 SEASONAL ship after the outside referee: fixes R1 to R5 and R8 in the page, headline and summary, ledger rows for the leaning cells, the bins and the Heidke check, page at /seasonal under HERMES beside FORECAST, feed /seasonal/live.json, rider on the tick bus
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the referee recount (seasonal_index_referee/code, own reader, binning, bootstrap and Heidke) reproduces all 44 reliability cells with 0 differences, and shows that a shift of one record or a flipped grid destroys the Heidke match (about 13 to 27 points off), so alignment and orientation hold
- V: holds: plan ruler unchanged. Referee sweep: the headline reads the same at blocks of 6, 12 and 24 seasons and under 10 other seeds
- VI: holds: temperature leaning ABOVE (48.2 stated, 60.1 observed, 54.9 to 64.2), precipitation leaning CONSISTENT. Heidke recompute CONSISTENT in all four rows
- P6: caught: referee R1. CPC's tutorial states the observed categories use 1981-2010 as the reference period. The page said the files do not state it. Fixed, with CPC's sentence and the all-rows shares (temperature above 51.6, near 28.6, below 19.9 percent) on the page and in the headline. Display after the data
- P6: caught: referee R2. Six precipitation seasons are all equal chances. CPC lists no first score and an all score of 0. Our all score now reads 0 there as the plan's formula gives (coverage 0), so the all-score check covers 380 seasons. No reading changed
- P6: caught: referee R4. Bin labels now state the edges (25 to under 31 and so on)
- P6: caught: referee R5. The temperature leaning cell is mostly above-normal rows (28,312 of 30,834). The split is shown, described and not scored
- P6: caught: referee R3, R8. The one precipitation season outside 1 point (JFM 2021, 1.26) has 4 cells with a category that is not a whole number, now named. The Heidke check is described as a check on pairing, not on the chances
- P9: holds: lint_copy.py 0 hits
- O1: holds: rider on the tick bus with --publish (KV seasonal_live), CPC files fetched at most once a day

## 2026-11-10 10:20 SEASONAL ship, complete check block (after the outside referee, before the site edit)
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: referee recount reproduces all 44 reliability cells with 0 differences. Drops: unreadable rows 0, forecasts waiting 3 per variable, Heidke cells with a non-whole category left out (10 cells over all seasons)
- II: holds: each category and bin read apart, observed beside stated, never netted
- III: holds: temperature above-normal bins read above and below-normal bins read below, printed apart with their sides
- V: holds: reliability with the moving-block bootstrap and the Heidke recompute against CPC's stated score, side by side
- VI: holds: temperature leaning ABOVE, precipitation leaning CONSISTENT, Heidke CONSISTENT in all four rows
- R: holds: counts from summary_seasonal.json of this run, CPC files dated in data/raw/cpc_verif_grid. After-data displays labelled
- P1: holds: both CPC formula quotes and the 1981-2010 sentence verbatim from the tutorial fetched 10 Nov 2026
- P2: holds: every figure in summary_seasonal.json and data/seasonal.json
- P3: holds: above, near and below normal as CPC names them, bins state their edges
- P4: holds: no cause named, the 1981-2010 reference period is named as a definition
- P5: holds: every interval labelled a block bootstrap 95 percent interval over seasons
- P6: holds: headline carries the reference period and the all-rows shares
- P7: holds: ledger rows seasonal.* before the site edit, release by ship.sh only
- P8: holds: seasonal.html parsed and read in full
- P9: holds: lint_copy.py 0 hits
- P10: holds: after-data displays labelled (observed shares, leaning split, largest Heidke gap)
- O1: holds: rider on the tick bus every 264 ticks with --publish (KV seasonal_live), files once a day
- O2: holds: failed fetches named in sources.stale
- O3: n/a: no GPU used, arithmetic on the CPU
- O4: holds: data/seasonal_history.jsonl one line per run
- O5: holds: absolute paths, /opt/homebrew/bin/python3 -P
- O6: n/a: no GPU job runs in this rider
