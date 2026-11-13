# Earth and station index sweep report

Source: Zenodo API, type dataset, open access, listings and sizes only. Screened 1750 records.

| Topic | Screened | Indexed | Dropped | Needs review |
|---|---|---|---|---|
| earthquakes | 250 | 228 | 17 | 5 |
| seismic waveforms | 250 | 210 | 31 | 9 |
| GNSS and GPS stations | 250 | 199 | 45 | 6 |
| weather and climate stations | 250 | 238 | 12 | 0 |
| hydrology gauges | 250 | 218 | 23 | 9 |
| ocean buoys | 250 | 213 | 31 | 6 |
| air quality monitors | 250 | 205 | 38 | 7 |

Total indexed 1511, dropped 197, needs review 42.

## Drop reasons

- no data-like files: 175
- not English: 15
- defense, military or intelligence funding: 7

## Needs review reasons

- language unclear from text: 17
- too little text to judge language: 13
- affiliation may be a company (Corporation): 3
- affiliation may be a company (Technologies): 2
- affiliation may be a company (S.A.): 1
- affiliation may be a company (AG): 1
- affiliation may be a company (Consulting): 1
- notes mention US Army without a funding statement: 1
- description mention Naval Research Laborator without a funding statement: 1
- description mention US Army without a funding statement: 1
- affiliation may be a company (Company): 1

## Classification

- Indexed (company): 34
- Funding not stated: 1194

## Method notes

- Funding is read from the Zenodo grants field, notes and description. A defense funder in a funder field or in a funding sentence drops the record. A defense name in text without a funding sentence goes to needs review.
- Linked paper acknowledgments and Earth System Science Data papers were not read in this first version.
- Company detection uses affiliation patterns and is conservative.
- Cache: /Users/heuremen/bones-forge/earthdata_index/cache
- Re-run: python3 -I /Users/heuremen/bones-forge/earthdata_index/sweep/earthdata_sweep.py
