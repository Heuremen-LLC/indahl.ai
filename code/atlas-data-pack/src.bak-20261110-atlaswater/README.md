# ATLAS Data Pack

Heuremen LLC · https://indahl.ai/atlas

The data behind the ATLAS pages at https://indahl.ai/atlas, as files you can open in a spreadsheet, a GIS tool or Python. Each dataset comes as the original JSON file unchanged, as CSV with one row per record, and for points on a map as GeoJSON. Each dataset carries its own build or pull date, or data year, listed in SOURCES.md. Epoch AI values are as of the pull date, 2026-10-28, and Epoch has updated some sites since.

## What is in each file

Data centers (`json/datacenters.json`): {N_OSM} features from OpenStreetMap and {N_EPOCH} US sites from Epoch AI. They come as `csv/datacenters_osm.csv`, `csv/datacenters_epoch.csv`, `geojson/datacenters_osm.geojson` and `geojson/datacenters_epoch.geojson`. {N_EPOCH_UNPLACED} Epoch sites have no coordinates, so their GeoJSON features have a null geometry. The `place_method` column says how a point was found and `place_match` holds the matched address text when there is one. Each OpenStreetMap row carries its source and its OpenStreetMap object id. Each row in both files carries the pull date in a `pulled` column.

Operating power plants (`json/plants.json`): {N_PLANTS} plants from the EIA monthly generator inventory. They come as `csv/plants.csv` and `geojson/plants.geojson`. Capacity by fuel is in the columns that start with `mw_`. A blank means the plant has no capacity in that fuel.

Planned power plants (`json/planned.json`): {N_PLANNED} plants. They come as `csv/planned.csv`, `csv/planned_generators.csv` and `geojson/planned.geojson`. The `planned_generators.csv` file has one row for each planned generator with its year, megawatts and fuel, taken from the `years` list of each plant. The same list is kept as text in the `years_json` column of `planned.csv`.

Electricity (`json/electricity.json`): prices, sales and generation for {N_STATES} states, including the District of Columbia. They come as `csv/electricity_states.csv`, one row per state with the data center counts kept in the `data_centers_` columns. The national figures are in `csv/electricity_us.csv` and `csv/electricity_us_ownership.csv`.

Utilities (`json/utilities.json`): {N_UTIL} rows of bundled EIA-861 data, one per utility and state, as `csv/utilities.csv`.

Carbon (`json/carbon.json`): EPA eGRID emission rates for {N_CARBON_STATES} states as `csv/carbon_states.csv`, {N_SUBREGIONS} grid regions as `csv/carbon_subregions.csv` and the national figures as `csv/carbon_us.csv`.

Cost to scale (`json/scale.json`): one year of electricity at the stated power of the Epoch AI sites. It comes as `csv/scale_sites.csv` with {N_SITES} sites, `csv/scale_states.csv` with {N_SCALE_STATES} states and `csv/scale_corrections.csv` with {N_CORR} correction. The method and the totals are in `csv/scale_meta.csv`.

Every dataset also has a `csv/<name>_meta.csv` file with two columns, `key` and `value`. It holds the fields that describe the whole dataset, such as the source text, the method, the units, the legend bins and the build date.

## Sources and dates

SOURCES.md lists the upstream sources, their links, their licences and the dates found in the data. NOTICE.txt carries the attribution lines. The OpenStreetMap rows are shared under the ODbL 1.0 with the line © OpenStreetMap contributors.

Only the data center rows carry a source in every row. The plants, planned plants, electricity, utilities, carbon and scale files carry one source statement for the whole dataset, in the `source` or `sources` entry of the JSON and in the `_meta.csv` file. They have no source column per row. Their rows carry the build date or the data year as a column instead.

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

- `json/`: the original files from the ATLAS data folder, unchanged
- `csv/`: one CSV for each table, plus the `_meta.csv` files
- `geojson/`: data centers, operating plants and planned plants as FeatureCollections
- `SOURCES.md`: upstream sources, links, licences and dates
- `TESTED.md`: what the files were opened with and what was compared
- `NOTICE.txt`: upstream licences and attribution
- `verify.py`: recounts and compares the files
- `START_HERE.html`: this guide as a page
- `LICENSE.txt`, `CITATION.cff`

## Links

- ATLAS: https://indahl.ai/atlas
- Electricity: https://indahl.ai/atlas/electricity
- Power plants: https://indahl.ai/atlas/power-plants
- Planned plants: https://indahl.ai/atlas/planned-plants
- Carbon: https://indahl.ai/atlas/carbon
- Code: https://github.com/Heuremen-LLC/indahl.ai
- Data on Hugging Face: https://huggingface.co/indahl
- OpenStreetMap: https://www.openstreetmap.org/copyright
- Epoch AI: https://epoch.ai/data/ai-data-centers
- EIA-861: https://www.eia.gov/electricity/data/eia861/
- EIA-860M: https://www.eia.gov/electricity/data/eia860m/
- EPA eGRID: https://www.epa.gov/egrid

## Notes on the data

The text in `json/scale.json` refers to our build step and names a script and a file path. That file is not in this pack. The JSON files are kept unchanged, so the text stays as it was written.

In `csv/utilities.csv` the column `ba_code` holds the text NA in {N_NA} rows ({NA_STATES}). NA is a code in EIA's file and not a missing value. The pack's data does not define the code and the EIA files we hold do not either, so we leave its meaning to EIA. Pandas and many spreadsheets read the text NA as missing, so in pandas keep it with `pd.read_csv("csv/utilities.csv", keep_default_na=False, na_values=[""])`.

The ATLAS page counts {N_SCALE_NOT_PLACED} sites as not placed in a state, while the Epoch GeoJSON has {N_EPOCH_UNPLACED} points without coordinates. The difference is {N_ADDR_STATE} sites that got their state from the address text without a point.

The `datacenters_epoch` files split the JSON field `placed` in two. `place_method` is one of nominatim address, nominatim city/zip only, address match, corrected, or blank. `place_match` is the matched address text when there is one. The JSON keeps the original `placed` field.

## Known data issues

This list comes from two rough checks and is not complete. It names records whose point may not match the stated state. The records are drawn as given and are not corrected in any file. Colossus 2 in `datacenters_epoch` sits about 57 m from the Tennessee and Mississippi line, and its state in the scale files comes from the simplified state outlines.

{COORD_ISSUES}

## Terms

Each part of this pack keeps the licence of its source, and LICENSE.txt gives them by file. Files derived from OpenStreetMap are under the ODbL 1.0 with © OpenStreetMap contributors, and no further restrictions may be added to them. Files derived from Epoch AI are under CC BY 4.0 with Epoch's citation, and where a file holds both, both apply. EIA, EPA and US Census data are US government works in the public domain.

Heuremen LLC permits anyone to use, copy and change its own parts with attribution to Heuremen LLC and https://indahl.ai/atlas. For its own text files (the README, SOURCES.md, NOTICE.txt, LICENSE.txt, TESTED.md and START_HERE.html) that permission does not include use as AI training data. Its reservation against text and data mining and AI training covers those text files only and does not apply to any OpenStreetMap-derived or Epoch-derived file or to public-domain data.
