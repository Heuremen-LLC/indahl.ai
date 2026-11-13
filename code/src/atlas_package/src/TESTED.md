# Tested

Heuremen LLC · https://indahl.ai/atlas

On 2026-11-02 the files were opened with pandas 3.1 at default settings and with geopandas 1.2 using pyogrio. Every count below was compared with the live ATLAS pages and matched.

- Epoch AI data centers: 77
- OpenStreetMap data centers: 1,649
- Operating plants: 14,280 with 1,390.6 gigawatts
- Operating plants of 25 megawatts or more in the contiguous states: 4,634
- Planned plants: 1,608 with 290.2 gigawatts
- Planned plants of 25 megawatts or more in the contiguous states: 979
- Cost to scale: 57 sites, 11,560.33 megawatts and 7,419.0 million dollars, over 25 states
- US average prices: 8.13 cents per kilowatthour industrial, 12.75 commercial and 16.48 residential
- US carbon: 767 pounds per megawatthour
- State industrial prices and state carbon figures for the 49 states drawn on the pages

Spot checks matched the live pages for Grand Coulee (WA, 6,809 MW), Vogtle (GA, 4,658 MW) and Palo Verde (AZ).

All GeoJSON files read as points in EPSG:4326.

The file `verify.py` compares every CSV and GeoJSON file cell by cell with the JSON, and recounts every file.

At default settings pandas reads the text NA in the `ba_code` column of `csv/utilities.csv` as missing. The README explains how to keep it.

On 2026-11-10 the water files and the files of the other ATLAS desks were opened with pandas 3.0.5 at default settings. Every count below was compared with the live desk pages, with the /<desk>/live.json files those pages read, and for water with the desk's own summary file of the same run, and matched.

- Water: {N_WATER_CELLS} cells, one for each lake and each lead from 0 to 23. All of them equal the desk summary in rows, inside, above, below and outcome for both tests.
- Water, six months ahead: Lake Mead 42 of 83 inside the range (interval 30 to 70 percent, below) and 180 of 315 above the Most Probable projection. Lake Powell 49 of 83 inside (39 to 78 percent, below) and 110 of 314 above. These are the counts printed at the top of https://indahl.ai/water.
- Water: {N_WATER_ROWS} rows, with the same count for each lake and outcome as the page's coverage, {N_WATER_REPORTS} reports, {N_WATER_BAND_MONTHS} months with both a Probable Minimum and a Probable Maximum, measured levels through {WATER_MEASURED_LAST}, {N_WATER_VARIANTS} 6.0 maf rows, {N_WATER_NOTABLE} notable rows, {N_WATER_RES} reservoirs, {N_WATER_THRESH} thresholds and {N_WATER_GAUGES} USGS gauges.
- Uptime: {N_UP_VENDORS} vendors, 0 misses in 301 control rounds, every vendor cannot tell.
- Time: {N_TIME_SERVERS} servers, 34 cannot tell and 2 nothing returned.
- CADA: {N_CADA_RES} resolvers at 4 checkpoints, 6,459 fresh domains from 2,048 feed reads.
- SECRECORDS: 20 of 145 HSTS preload headers and 20 of 765 SPF records, {N_SEC_FULL} records read in full, and DMARC counts that sum to the {N_SEC_DOMAINS} domains read. One HSTS mismatch awaits a read in full, so that rule has 19 rows in the read-in-full file against a count of 20.
- SEAT: 344 probes, the last at {SEAT_LAST} UTC, {N_SEAT_INC} incidents and {N_SEAT_FEEDS} feeds.
- SUPPORT: 127 of 512 supported cycles with no release in the window, {N_SUP_BYPROD} products in the product table, {N_SUP_PRODUCTS} products and {N_SUP_CYCLES} cycles read.
- CHANGE: {N_CH_ROWS} rows read since {CH_FIRST}, {N_CH_UP} upcoming shutdowns and {N_CH_LIST} changes. The lifespan file holds 10 of 34 Google preview names and 1 of 20 other Google names under 180 days, with medians of 217 and 454 days, as the page prints them.

The desk pages read a new file on their own schedule. The counts above match the snapshot in this pack, and later counts on the pages may differ.

Not tested: QGIS or ArcGIS desktop, and Excel itself.

On 2026-11-10 the UPTIME, SECRECORDS, SUPPORT and CHANGE files were rebuilt as results only, with the filter each of these desks uses for its own data pack. The build checks that each JSON file equals that filter applied to the snapshot, that no source field (incident text, the record column, end-of-life dates, change notes, dates or links) is left, and that every count above is unchanged. verify.py then compared every CSV cell with the JSON again.
