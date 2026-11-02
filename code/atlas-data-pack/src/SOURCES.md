# Sources

Heuremen LLC · https://indahl.ai/atlas

Each entry gives the upstream source as the ATLAS pages and the data files state it, with the dates found in the data. Dataset descriptions and licence notes follow https://indahl.ai/atlas and its subpages.

## Data centers (json/datacenters.json)

- OpenStreetMap, pulled {DC_PULLED} through the Overpass service. https://www.openstreetmap.org/ . Licence: ODbL 1.0, © OpenStreetMap contributors. https://opendatacommons.org/licenses/odbl/1-0/ and https://www.openstreetmap.org/copyright . Features tagged `telecom=data_center`, `building=data_center` or `data_center`. Features within 250 m with the same name are merged. The ATLAS page states {OSM_PAGE_COUNT}.
- Epoch AI, AI data centers. https://epoch.ai/data/ai-data-centers . Licence: CC BY 4.0. https://creativecommons.org/licenses/by/4.0/ . Name, owner, power, H100 equivalents and address of AI data centers. Pulled 28 Oct 2026, as stated in `json/scale.json`.
- Addresses were turned into coordinates by us with the US Census geocoder and then OpenStreetMap Nominatim, as the ATLAS page states.
- Per-row source: the `source` column on every row of `datacenters_osm.csv` and `datacenters_epoch.csv`. Pull date: the `pulled` column.

## Operating power plants (json/plants.json)

- U.S. Energy Information Administration, EIA-860M, September 2026, operating generators. https://www.eia.gov/electricity/data/eia860m/ . Nameplate capacity in MW, grouped into plants by fuel. Plant coordinates come from the map link in each row, from EIA-860 2024 where a row has none.
- U.S. government data, as the page states.
- Built {PLANTS_BUILT}. Per-row source: none in the data, the source is stated once for the dataset in `plants_meta.csv`.

## Planned power plants (json/planned.json)

- U.S. Energy Information Administration, EIA-860M, September 2026, Planned sheet. https://www.eia.gov/electricity/data/eia860m/ . Status groups and fuel rules are in the `source` entry, kept in full in `planned_meta.csv`.
- U.S. government data, as the page states.
- Built {PLANNED_BUILT}. Per-row source: none in the data, the source is stated once for the dataset.

## Electricity (json/electricity.json)

- U.S. Energy Information Administration, EIA-861 annual electric power industry report, Sales to Ultimate Customers 2024 (Sales_Ult_Cust_2024.xlsx). https://www.eia.gov/electricity/data/eia861/ . State prices are computed by the rule EIA gives under its table.
- U.S. Energy Information Administration, State Historical Tables, net generation by state and energy source (annual_generation_state.xlsx), 2024. https://www.eia.gov/electricity/data/state/
- Data center counts per state derive from the OpenStreetMap and Epoch AI data above, under the ODbL 1.0 and CC BY 4.0.
- The page states: Read once on 28 October 2026. EIA publishes these tables once a year. Built {ELEC_BUILT}. Price year {ELEC_PRICE_YEAR}, generation year {ELEC_GEN_YEAR}.
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

- Power: Epoch AI, AI data centers (CC BY 4.0), field Current power (MW), pulled 28 Oct 2026. https://epoch.ai/data/ai-data-centers
- Price: EIA-861 {SCALE_PRICE_YEAR}, Sales to Ultimate Customers, as computed for the electricity dataset above.
- Corrections to coordinates use OpenStreetMap Nominatim. The correction entry names its query, the way and the lookup date, and is kept in full in `scale_corrections.csv`.
- The method is stated in `scale_meta.csv`. The figures are arithmetic on published numbers. They are not a forecast and not any site's bill.
- Built {SCALE_BUILT}. Per-row source: none in the data, the sources are stated once for the dataset.

## Not in this pack

The state outlines on the ATLAS map come from us-atlas (ISC licence, US Census boundaries). https://github.com/topojson/us-atlas . They are map drawing files and are not part of the data, so they are left out.
