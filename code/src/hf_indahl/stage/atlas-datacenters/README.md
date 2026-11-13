---
license: odbl
pretty_name: "ATLAS: United States data centers"
tags:
- data-centers
- infrastructure
- openstreetmap
- geospatial
---

# ATLAS: United States data centers

Sites mapped in two open sources, pulled 2026-10-28: features tagged as data centers in OpenStreetMap (merged when within 250 m with the same name), and the United States AI data centers in Epoch AI's dataset, with coordinates added by us from the US Census geocoder and OpenStreetMap Nominatim. This is what those sources hold, not a count of every data center. Map and context: https://indahl.ai/atlas .

Files: `datacenters.json` (records with their source), `summary.json` (counts), `build_atlas.py` and `geocode_epoch.py` (the scripts).

Licences: the OpenStreetMap part is (c) OpenStreetMap contributors under the ODbL 1.0 (https://www.openstreetmap.org/copyright), and this combined database is shared under the ODbL 1.0. The Epoch AI fields are CC BY 4.0: Epoch AI, 'AI data centers', epoch.ai/data/ai-data-centers.

Reference: HLC-BAD4BB03
