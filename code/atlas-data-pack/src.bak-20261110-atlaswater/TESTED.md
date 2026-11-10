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

Not tested: QGIS or ArcGIS desktop, and Excel itself.
