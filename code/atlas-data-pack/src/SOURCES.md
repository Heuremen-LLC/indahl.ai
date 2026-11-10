# Sources

Heuremen LLC · https://indahl.ai/atlas

Each entry gives the upstream source as the ATLAS pages and the data files state it, with the dates found in the data. Dataset descriptions and licence notes follow https://indahl.ai/atlas and its subpages.

## Data centers (json/datacenters.json)

- OpenStreetMap, pulled {DC_PULLED} through the Overpass service. https://www.openstreetmap.org/ . Licence: ODbL 1.0, © OpenStreetMap contributors. https://opendatacommons.org/licenses/odbl/1-0/ and https://www.openstreetmap.org/copyright . Features tagged `telecom=data_center`, `building=data_center` or `data_center`. Features within 250 m with the same name are merged. The ATLAS page states {OSM_PAGE_COUNT}.
- Epoch AI, AI data centers. https://epoch.ai/data/ai-data-centers . Licence: CC BY 4.0. https://creativecommons.org/licenses/by/4.0/ . Name, owner, power, H100 equivalents and address of AI data centers. Pulled 2026-10-28, as stated in `json/scale.json`. Epoch fields kept: name, owner (as `operator`), power in MW (`mw`), H100 equivalents (`h100e`), capital cost in billions of US dollars (`capex_usd_b`) and address. Only rows with Country = United States are kept. Epoch values are as of the pull date, 2026-10-28, and Epoch has updated some sites since. The full change statement is in LICENSE.txt.
- Addresses were turned into coordinates by us with the US Census geocoder (U.S. government data, https://geocoding.geo.census.gov/) and then OpenStreetMap Nominatim, as the ATLAS page states. The coordinates in `datacenters_epoch.*`, `scale_sites.csv` and `scale_corrections.csv` are therefore OpenStreetMap-derived where Nominatim found them, and the ODbL 1.0 applies to them as well as CC BY 4.0.
- Per-row source: the `source` column on every row of `datacenters_osm.csv` and `datacenters_epoch.csv`. Pull date: the `pulled` column. In the Epoch CSV and GeoJSON the JSON field `placed` is split into `place_method` (nominatim address, nominatim city/zip only, address match, corrected, or blank) and `place_match` (the matched address text when there is one, or for a corrected point the note after the word corrected). The JSON keeps `placed` as it was.

## Operating power plants (json/plants.json)

- U.S. Energy Information Administration, EIA-860M, 2026-09, operating generators. https://www.eia.gov/electricity/data/eia860m/ . Nameplate capacity in MW, grouped into plants by fuel. Plant coordinates come from the map link in each row, from EIA-860 2024 where a row has none.
- U.S. government data, as the page states.
- Built {PLANTS_BUILT}. Per-row source: none in the data, the source is stated once for the dataset in `plants_meta.csv`.

## Planned power plants (json/planned.json)

- U.S. Energy Information Administration, EIA-860M, 2026-09, Planned sheet. https://www.eia.gov/electricity/data/eia860m/ . Status groups and fuel rules are in the `source` entry, kept in full in `planned_meta.csv`.
- U.S. government data, as the page states.
- Built {PLANNED_BUILT}. Per-row source: none in the data, the source is stated once for the dataset.

## Electricity (json/electricity.json)

- U.S. Energy Information Administration, EIA-861 annual electric power industry report, Sales to Ultimate Customers 2024 (Sales_Ult_Cust_2024.xlsx). https://www.eia.gov/electricity/data/eia861/ . State prices are computed by the rule EIA gives under its table.
- U.S. Energy Information Administration, State Historical Tables, net generation by state and energy source (annual_generation_state.xlsx), 2024. https://www.eia.gov/electricity/data/state/
- Data center counts per state derive from the OpenStreetMap and Epoch AI data above, under the ODbL 1.0 and CC BY 4.0.
- The page states: Read once on 2026-10-28. EIA publishes these tables once a year. Built {ELEC_BUILT}. Price year {ELEC_PRICE_YEAR}, generation year {ELEC_GEN_YEAR}.
- Per-row source: none in the data, the sources are stated once for the dataset in `electricity_meta.csv`.

## Utilities (json/utilities.json)

- U.S. Energy Information Administration, EIA-861, {UTIL_YEAR}. https://www.eia.gov/electricity/data/eia861/ . Bundled (Part A) rows, one per utility and state. Price in cents per kilowatthour, revenue divided by sales.
- U.S. government data, as the pages state.
- Data year {UTIL_YEAR}. The file carries no build date and no per-row source.

## Carbon (json/carbon.json)

- U.S. Environmental Protection Agency, eGRID2023 rev 2 (egrid2023_data_rev2.xlsx), sheets ST23, SRL23 and US23. https://www.epa.gov/egrid . Total output emission rates in pounds per megawatthour of net generation, all fuels.
- U.S. government data, as the page states.
- Data year {CARBON_YEAR}, built {CARBON_BUILT}. Per-row source: none in the data, the source is stated once for the dataset.

## Cost to scale (json/scale.json)

- Power: Epoch AI, AI data centers (CC BY 4.0), field Current power (MW), pulled 2026-10-28. https://epoch.ai/data/ai-data-centers
- Price: EIA-861 {SCALE_PRICE_YEAR}, Sales to Ultimate Customers, as computed for the electricity dataset above.
- Corrections to coordinates use OpenStreetMap Nominatim. The correction entry names its query, the way and the lookup date, and is kept in full in `scale_corrections.csv`.
- The method is stated in `scale_meta.csv`. The figures are arithmetic on published numbers. They are not a forecast and not any site's bill.
- Built {SCALE_BUILT}. Per-row source: none in the data, the sources are stated once for the dataset.

## Water (json/water.json and json/water_rows.json)

- U.S. Bureau of Reclamation, 24-Month Study reports, every report listed in RISE catalog record 6331 from January 2000 on. https://data.usbr.gov/rise/api/catalog-record/6331 . Projected end-of-month water surface elevations for Lake Powell and Lake Mead under the Most Probable, Probable Minimum and Probable Maximum inflow scenarios. The report files were read on 2026-11-09 and 2026-11-10. The catalog was read again on 2026-11-10.
- U.S. Bureau of Reclamation, Hydrologic Database (HDB). https://www.usbr.gov/pn-bin/hdb/hdb.pl . Model runs named by the Model Run ID printed in a report (table M, monthly), and the observed end-of-month elevation (table R, monthly). Lake Powell is sdi 1928 on uchdb2 and Lake Mead is sdi 1930 on lchdb. The daily and hourly readings in the live panel come from the same database. Measured values and live readings are as of {WATER_UPDATED} UTC.
- U.S. Bureau of Reclamation, Lower Colorado Region. Lake Mead end-of-month elevation table, https://www.usbr.gov/lc/region/g4000/hourly/mead-elv.html , used as a cross-check. Daily reservoir report, https://www.usbr.gov/lc/region/g4000/hourly/levels.html , and its JSON feed, https://www.usbr.gov/lc/region/g4000/riverops/webreports/accumweb.json , for storage and stated capacity. Read {WATER_UPDATED} UTC.
- U.S. Bureau of Reclamation, governing documents quoted in `csv/water_thresholds.csv`: the 2007 Interim Guidelines Record of Decision, https://www.usbr.gov/lc/region/programs/strategies/RecordofDecision.pdf , the 2027-2028 Operating Guidelines, https://www.usbr.gov/ColoradoRiverBasin/post2026/decision-doc/2027-2028OperatingGuidelines_Final.pdf , and the October 2026 Most Probable 24-Month Study. Each row names its document, link and section.
- U.S. Geological Survey, Water Services. https://waterservices.usgs.gov/ . Daily values and instantaneous values for 09379900 Lake Powell at Glen Canyon Dam (parameter 62614, NGVD 1929) and daily discharge for the gauges listed in `csv/water_usgs_revisions.csv`. Read {WATER_UPDATED} UTC. Provisional values have been stored by us since {WATER_FIRST_READ}.
- California Department of Water Resources, California Data Exchange Center (CDEC), reservoir report. https://cdec.water.ca.gov/reportapp/javareports?name=RES . Storage and stated capacity for {WATER_CDEC_NAMES}, in {N_WATER_CDEC} rows of `csv/water_reservoirs.csv` and the matching entries of `json/water.json`. Read {WATER_UPDATED} UTC.
- Reclamation and USGS data are U.S. government works in the public domain. CDEC is a State of California service and its figures keep CDEC's terms.
- Per-row source: each row of `water_rows.csv` names its report in `mp_report`, and `mp_src` says whether the Most Probable value came from HDB or from the report text. Each row of `water_reservoirs.csv` names its source in `source`, and each row of `water_thresholds.csv` names its document in `doc` and `url`. The plan, the rules and the reading of the reports are in the desk's plan, https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/water .

## Other ATLAS desks

Each file below is the desk's /<desk>/live.json as served on 2026-11-10, at the UTC time in its `updated` field. Each desk's plan and code are public at https://github.com/Heuremen-LLC/indahl.ai/tree/main/code .

- Uptime (json/uptime.json), https://indahl.ai/uptime . Our own HTTPS probes of each vendor from three seats (two home machines and the GitHub runner network) since 2026-10-28, with https://example.com and https://1.1.1.1 as controls. Each vendor's status indicator and incidents are read from its public status page (the summary.json and incidents.json files of its Statuspage site), and the incident titles are the vendor's own. Snapshot 10 Nov {UPD_UPTIME} UTC.
- Time (json/time.json), https://indahl.ai/time . Our own NTP queries to public time servers since 2026-10-28, from a reference seat on a GPS-disciplined clock and from the GitHub runner network. The stratum, reference ID and stated bound come from each server's own replies. Snapshot 10 Nov {UPD_TIME} UTC.
- CADA (json/cada.json), https://indahl.ai/cada . Our own DNS queries to filtered and unfiltered public resolvers since 2026-10-28, for fresh domains taken from the Phishing.Database active list (https://github.com/mitchellkrogza/Phishing.Database) and the CERT Polska warning list (https://hole.cert.pl/domains/v2/domains.txt). The file holds counts only. No domain from either feed is in it. Snapshot 10 Nov {UPD_CADA} UTC.
- SECRECORDS (json/secrecords.json), https://indahl.ai/secrecords . The top domains of the Tranco list of {SEC_LISTDATE} (https://tranco-list.eu/ , Le Pochat et al., NDSS 2019). Each domain's HTTPS response header is read directly, and its SPF and DMARC records through Cloudflare DNS over HTTPS (https://cloudflare-dns.com/dns-query). Reads began 2026-10-29. Snapshot 10 Nov {UPD_SECRECORDS} UTC.
- SEAT (json/seat.json), https://indahl.ai/seat . Probes of our own pages and feeds run on the GitHub runner network since 2026-10-29. No outside data. Last probe {SEAT_LAST} UTC, snapshot 10 Nov {UPD_SEAT} UTC.
- SUPPORT (json/support.json), https://indahl.ai/support . endoflife.date (https://endoflife.date/api/all.json and https://endoflife.date/api/PRODUCT.json), MIT License, read since 2026-10-28. Release, support and end-of-life dates are as endoflife.date gives them. The shares and intervals are ours. Snapshot 10 Nov {UPD_SUPPORT} UTC.
- CHANGE (json/change.json), https://indahl.ai/change . The deprecation pages of Anthropic (https://platform.claude.com/docs/en/about-claude/model-deprecations), OpenAI (https://developers.openai.com/api/docs/deprecations), Google (https://ai.google.dev/gemini-api/docs/deprecations) and Cloudflare (https://developers.cloudflare.com/deprecations/), read since {CH_FIRST}. Each row names its page in `url`. Snapshot 10 Nov {UPD_CHANGE} UTC.
- Per-row source: the CHANGE rows carry `url`, the SECRECORDS read-in-full rows carry the domain and its record, and the UPTIME incidents carry the vendor. The other desk files state their sources once, on the desk page and here.

## Not in this pack

The state outlines on the ATLAS map come from us-atlas (ISC licence, US Census boundaries). https://github.com/topojson/us-atlas . They are map drawing files and are not part of the data, so they are left out.

The 24-Month Study report files and the raw HDB, USGS and CDEC downloads behind the water files are not in this pack. The links above lead to them.
