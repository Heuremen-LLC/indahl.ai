# ATLAS Data Pack

Heuremen LLC · https://indahl.ai/atlas

The data behind the ATLAS pages at https://indahl.ai/atlas, as files you can open in a spreadsheet, a GIS tool or Python. Each dataset comes as the original JSON file unchanged, as CSV with one row per record, and for points on a map as GeoJSON. Each dataset carries its own build or pull date, or data year, listed in SOURCES.md. Epoch AI values are as of the pull date, 2026-10-28, and Epoch has updated some sites since.

## What is in each file

Data centers (`json/datacenters.json`): 1,649 features from OpenStreetMap and 77 US sites from Epoch AI. They come as `csv/datacenters_osm.csv`, `csv/datacenters_epoch.csv`, `geojson/datacenters_osm.geojson` and `geojson/datacenters_epoch.geojson`. 10 Epoch sites have no coordinates, so their GeoJSON features have a null geometry. The `place_method` column says how a point was found and `place_match` holds the matched address text when there is one. Each OpenStreetMap row carries its source and its OpenStreetMap object id. Each row in both files carries the pull date in a `pulled` column.

Operating power plants (`json/plants.json`): 14,280 plants from the EIA monthly generator inventory. They come as `csv/plants.csv` and `geojson/plants.geojson`. Capacity by fuel is in the columns that start with `mw_`. A blank means the plant has no capacity in that fuel.

Planned power plants (`json/planned.json`): 1,608 plants. They come as `csv/planned.csv`, `csv/planned_generators.csv` and `geojson/planned.geojson`. The `planned_generators.csv` file has one row for each planned generator with its year, megawatts and fuel, taken from the `years` list of each plant. The same list is kept as text in the `years_json` column of `planned.csv`.

Electricity (`json/electricity.json`): prices, sales and generation for 51 states, including the District of Columbia. They come as `csv/electricity_states.csv`, one row per state with the data center counts kept in the `data_centers_` columns. The national figures are in `csv/electricity_us.csv` and `csv/electricity_us_ownership.csv`.

Utilities (`json/utilities.json`): 1,823 rows of bundled EIA-861 data, one per utility and state, as `csv/utilities.csv`.

Carbon (`json/carbon.json`): EPA eGRID emission rates for 51 states as `csv/carbon_states.csv`, 27 grid regions as `csv/carbon_subregions.csv` and the national figures as `csv/carbon_us.csv`.

Cost to scale (`json/scale.json`): one year of electricity at the stated power of the Epoch AI sites. It comes as `csv/scale_sites.csv` with 77 sites, `csv/scale_states.csv` with 25 states and `csv/scale_corrections.csv` with 1 correction. The method and the totals are in `csv/scale_meta.csv`.

Water (`json/water.json` and `json/water_rows.json`): the Bureau of Reclamation 24-Month Study projections for Lake Mead and Lake Powell set against the measured end-of-month elevations, as on https://indahl.ai/water. `json/water.json` is the file the WATER page reads at /water/live.json, as of 2026-11-10 13:21 UTC. `json/water_rows.json` holds the 15,222 rows of the same run. They cover 530 reports issued from 2000-01 to 2026-10 (325 Most Probable, 119 Probable Minimum and 86 Probable Maximum), with measured levels through 2026-10. The page reads a new file about every half hour, and this pack holds one fixed copy.

- `csv/water_cells.csv`: 48 rows, one for each lake and each lead from 0 to 23 months ahead. The `band_` columns hold the band test. They give the rows inside, above and below the range between the Probable Minimum and Probable Maximum projections of the same month, the 95% Wilson interval on water years (`band_lo`, `band_hi` and `band_n_wy`) and the outcome. The `mp_` columns hold the Most Probable test. They give the rows where the lake ended above or below the projection, the interval, the outcome and the error percentiles in feet. The columns with `checks_after_data` in their name hold the same counts read on the other rulers the page prints beside each outcome. They were added after the data and decide no outcome.
- `csv/water_rows.csv`: one row for each report month, lake and target month. `mp`, `pmin` and `pmax` are the projected elevations in feet and `measured` is the end-of-month elevation from Reclamation HDB. `mp_error` is measured minus Most Probable. `outcome` is the band test for the row and `why` gives the reason for a cannot tell. `mp_src` says whether the Most Probable value came from the HDB model run (hdb) or from the report text (text).
- `csv/water_band_sentence_cells.csv`: the band cells counted only on the 79 report months whose Probable Minimum and Probable Maximum reports both print Reclamation's 80 percent sentence.
- `csv/water_variants.csv`: the 144 rows of the 6.0 maf Lake Powell release runs, which the page shows apart.
- `csv/water_notable.csv`, `csv/water_misread_by_era.csv` and `csv/water_flagged_groups.csv`: the notable rows, the rate of misread digits in our reading of the printed reports by era, and the groups of cells that read above or below.
- `csv/water_reservoirs.csv`: storage on the snapshot day against the capacity the operating agency states, for 9 reservoirs. A share of stated capacity is a reading and not a test.
- `csv/water_thresholds.csv`: the 10 elevations named in the governing documents, each with its document, link, section and quote.
- `csv/water_usgs_revisions.csv`: USGS provisional daily values stored by us for 8 gauges, with revisions counted from our first read on 2026-11-10.
- `csv/water_meta.csv`: the coverage counts, the lead-6 headline cells, the cross-checks of the measured side, the live readings of Lake Mead and Lake Powell, and the notes.

The other desks under ATLAS each come as the file the desk page reads at /<desk>/live.json, unchanged, with one CSV for each table and a `_meta.csv` file. Each is one fixed copy. Its `updated` field gives the day, month and time in UTC without the year, and every snapshot here is from 2026. The times are listed in SOURCES.md.

Uptime (`json/uptime.json`): the status pages of 20 vendors against our own probes, as on https://indahl.ai/uptime. `csv/uptime_vendors.csv` has one row for each vendor with its rounds, disagreements, confirmations and blips, its reach from each seat in the `reach_` columns, and the outcome. `csv/uptime_incidents.csv` has the 57 incidents the vendors' own status pages list, with each vendor's title. The control rounds and the floor are in `csv/uptime_meta.csv`.

Time (`json/time.json`): 36 public time servers measured from our reference seat, and from the GitHub runner network in the columns that end in `_2`, as on https://indahl.ai/time. `csv/time_servers.csv` has one row for each server. The reference clock and the part of each offset that belongs to the seat are in `csv/time_meta.csv`.

CADA (`json/cada.json`): public DNS filters against fresh domains from abuse feeds, as on https://indahl.ai/cada. `csv/cada_checkpoints.csv` has one row for each of the 7 resolvers at each checkpoint, given in seconds after a domain was first seen, with the share in percent and its 95% interval in `share_pct`, `lo_pct` and `hi_pct`. `csv/cada_answer_classes.csv` counts each kind of answer by resolver and `csv/cada_alive.csv` counts the domains still alive at each checkpoint. The domains and the feeds are not in this pack.

SECRECORDS (`json/secrecords.json`): the security records of 1,000 domains from the Tranco list of 2026-11-10 against the rules they are meant to meet, as on https://indahl.ai/secrecords. `csv/secrecords_comparison.csv` has one row for each rule with its count, interval, outcome and class counts. `csv/secrecords_read_in_full.csv` has the 39 records read in full, with the record text and the reason. The HSTS and DMARC counts are in `csv/secrecords_descriptive.csv` and `csv/secrecords_dmarc.csv`.

SEAT (`json/seat.json`): an outside seat on the GitHub runner network reads our own pages, as on https://indahl.ai/seat. `csv/seat_now.csv` and `csv/seat_rolling.csv` hold the state at the last probe, 2026-11-10 12:10:00 UTC, and the count over the last probes. `csv/seat_incidents.csv` has 3 incidents and `csv/seat_feeds.csv` has 42 feeds with their age and limit.

SUPPORT (`json/support.json`): stated support windows against release activity, from 489 products and 9,375 release cycles on endoflife.date, as on https://indahl.ai/support. `csv/support_all.csv` holds the headline count and `csv/support_product_level.csv` the two product readings. `csv/support_by_product.csv` has 55 products and `csv/support_unreleased_cycles.csv` has the 127 supported cycles with no release in the window. In that file the text False in `eol` means no end of life is stated. `csv/support_after_eol.csv` counts the last releases by their time against the end of life.

CHANGE (`json/change.json`): announced shutdown dates from the deprecation pages of 4 vendors, kept since 2026-10-29, as on https://indahl.ai/change. `csv/change_upcoming.csv` has 28 upcoming shutdowns and `csv/change_list.csv` has 12 changes seen between snapshots. `csv/change_test.csv`, `csv/change_lifespan.csv`, `csv/change_notice.csv` and `csv/change_kinds.csv` hold the test, the lifespans, the notice periods and the changes by kind. `csv/change_sources.csv` lists the pages read.

Every dataset also has a `csv/<name>_meta.csv` file with two columns, `key` and `value`. It holds the fields that describe the whole dataset, such as the source text, the method, the units, the legend bins and the build date.

## Sources and dates

SOURCES.md lists the upstream sources, their links, their licences and the dates found in the data. NOTICE.txt carries the attribution lines. The OpenStreetMap rows are shared under the ODbL 1.0 with the line © OpenStreetMap contributors.

Only the data center rows carry a source in every row. The water rows name their report in `mp_report` and the source of their Most Probable value in `mp_src`. The plants, planned plants, electricity, utilities, carbon and scale files carry one source statement for the whole dataset, in the `source` or `sources` entry of the JSON and in the `_meta.csv` file. They have no source column per row. Their rows carry the build date or the data year as a column instead.

## How to open the files

Spreadsheet: open any file in `csv/`. The files are UTF-8 with a byte order mark so Excel reads names correctly. Empty text and missing values are both shown as blank cells.

GIS tool: add any file in `geojson/` as a vector layer. Coordinates are in longitude and latitude order in WGS 84. Properties keep their nested structure, and a tool that cannot read nested values will show them as text.

Python, standard library only:

```
import json, csv
rows = list(csv.DictReader(open("csv/plants.csv", encoding="utf-8-sig")))
plants = json.load(open("json/plants.json"))["plants"]
points = json.load(open("geojson/plants.geojson"))["features"]
```

Check the pack with `python verify.py`. It recounts the rows of every file, compares every CSV cell with the JSON and compares the GeoJSON features with the JSON records.

## What is here

- `json/`: the original files from the ATLAS data folder and from the desk pages, unchanged
- `csv/`: one CSV for each table, plus the `_meta.csv` files
- `geojson/`: data centers, operating plants and planned plants as FeatureCollections
- `SOURCES.md`: upstream sources, links, licences and dates
- `TESTED.md`: what the files were opened with and what was compared
- `NOTICE.txt`: upstream licences and attribution
- `verify.py`: recounts and compares the files
- `START_HERE.html`: this guide as a page
- `LICENSE.txt`, `CITATION.cff`

## Cite

Heuremen LLC, ATLAS Data Pack, Zenodo, doi:10.5281/zenodo.23874305

https://doi.org/10.5281/zenodo.23874305

That DOI always points to the newest version on Zenodo. Each version there also has its own DOI.

## Links

- ATLAS: https://indahl.ai/atlas
- Electricity: https://indahl.ai/atlas/electricity
- Power plants: https://indahl.ai/atlas/power-plants
- Planned plants: https://indahl.ai/atlas/planned-plants
- Carbon: https://indahl.ai/atlas/carbon
- Water: https://indahl.ai/water
- Uptime: https://indahl.ai/uptime
- Time: https://indahl.ai/time
- CADA: https://indahl.ai/cada
- SECRECORDS: https://indahl.ai/secrecords
- SEAT: https://indahl.ai/seat
- SUPPORT: https://indahl.ai/support
- CHANGE: https://indahl.ai/change
- Code: https://github.com/Heuremen-LLC/indahl.ai
- Data on Hugging Face: https://huggingface.co/indahl
- OpenStreetMap: https://www.openstreetmap.org/copyright
- Epoch AI: https://epoch.ai/data/ai-data-centers
- EIA-861: https://www.eia.gov/electricity/data/eia861/
- EIA-860M: https://www.eia.gov/electricity/data/eia860m/
- EPA eGRID: https://www.epa.gov/egrid
- Reclamation 24-Month Study archive (RISE): https://data.usbr.gov/rise/api/catalog-record/6331
- Reclamation HDB: https://www.usbr.gov/pn-bin/hdb/hdb.pl
- USGS Water Services: https://waterservices.usgs.gov/
- California CDEC: https://cdec.water.ca.gov/

## Notes on the data

The text in `json/scale.json` refers to our build step and names a script and a file path. That file is not in this pack. The JSON files are kept unchanged, so the text stays as it was written.

In `csv/utilities.csv` the column `ba_code` holds the text NA in 23 rows (AK 11, HI 8, ME 2, NY 2). NA is a code in EIA's file and not a missing value. The pack's data does not define the code and the EIA files we hold do not either, so we leave its meaning to EIA. Pandas and many spreadsheets read the text NA as missing, so in pandas keep it with `pd.read_csv("csv/utilities.csv", keep_default_na=False, na_values=[""])`.

The ATLAS page counts 8 sites as not placed in a state, while the Epoch GeoJSON has 10 points without coordinates. The difference is 2 sites that got their state from the address text without a point.

The `datacenters_epoch` files split the JSON field `placed` in two. `place_method` is one of nominatim address, nominatim city/zip only, address match, corrected, or blank. `place_match` is the matched address text when there is one. The JSON keeps the original `placed` field.

## Known data issues

This list comes from two rough checks and is not complete. It names records whose point may not match the stated state. The records are drawn as given and are not corrected in any file. Colossus 2 in `datacenters_epoch` sits about 57 m from the Tennessee and Mississippi line, and its state in the scale files comes from the simplified state outlines.

Rule 1, state box: a record is listed when its point lies more than 1 degree outside an approximate latitude and longitude box for its stated state. Rule 2, nearest same-state record: plants and planned plants are pooled by stated state, and a record is listed when the nearest other record of its state is more than 140 km away. Alaska and Hawaii are skipped by rule 2. Neither rule catches a wrong point that sits close to other records of the state or inside the box. A flag is a reason to look and not a finding. Some remote plants are flagged by rule 2 alone. The rules list 9 records.

- `plants.json` code 6584 "Stock Island": stated state FL, point at 24.563333, -81.7342. Flagged: 161 km from the nearest record of its state.
- `plants.json` code 64638 "Borderlands Wind, LLC": stated state NM, point at 34.159842, -108.894458. Flagged: 147 km from the nearest record of its state.
- `plants.json` code 59655 "Campbell County Wind Farm": stated state SD, point at 45.753333, -100.275. Flagged: 143 km from the nearest record of its state.
- `plants.json` code 70519 "Rangeley": stated state ME, point at 40.981022, -70.651702, which is in the Atlantic south of Nantucket. Flagged: outside the state box and 250 km from the nearest record of its state.
- `plants.json` code 70557 "AmericoldCA - Plainville, CT": stated state CT, point at 37.429933, -121.925782, which is in California. Flagged: outside the state box and 4125 km from the nearest record of its state.
- `planned.json` code 68296 "Mullin Creek #1 Generating Station": stated state MO, point at 38.00595, -97.92166. Flagged: outside the state box and 293 km from the nearest record of its state.
- `planned.json` code 64670 "Big Creek Solar LLC": stated state AR, point at 34.870404, -117.9656, which is in California. Flagged: outside the state box and 2121 km from the nearest record of its state.
- `planned.json` code 68876 "Okolona Solar": stated state MS, point at 37.693, -87.549. Flagged: outside the state box and 351 km from the nearest record of its state.
- `planned.json` code 68028 "Delta Solar Plant": stated state LA, point at 33.794007, -90.71392, which is in Mississippi, and its utility is Entergy Mississippi LLC. Flagged: 145 km from the nearest record of its state.

## Terms

Each part of this pack keeps the licence of its source, and LICENSE.txt gives them by file. Files derived from OpenStreetMap are under the ODbL 1.0 with © OpenStreetMap contributors, and no further restrictions may be added to them. Files derived from Epoch AI are under CC BY 4.0 with Epoch's citation, and where a file holds both, both apply. EIA, EPA, US Census, Bureau of Reclamation and USGS data are US government works in the public domain. The storage figures for Shasta and Oroville in the water files come from California CDEC, a State of California service, and keep CDEC's terms. The files of the other desks hold Heuremen LLC's own measurements, which may be used, copied and changed with attribution but not used for text and data mining or AI training, as the desk pages state. The endoflife.date values in the SUPPORT files are under the MIT License, and the names and dates from vendor pages keep their vendors' terms.

Heuremen LLC permits anyone to use, copy and change its own parts with attribution to Heuremen LLC and https://indahl.ai/atlas. For its own text files (the README, SOURCES.md, NOTICE.txt, LICENSE.txt, TESTED.md and START_HERE.html) that permission does not include use as AI training data. Its reservation against text and data mining and AI training covers those text files and the measurement files of the other desks only. It does not apply to any OpenStreetMap-derived or Epoch-derived file, to public-domain data or to the endoflife.date values.
