# Dryad ecology index sweep report

Source: Dryad API v2, listings and sizes only. Screened 2000 records.

| Topic | Screened | Indexed | Dropped | Needs review |
|---|---|---|---|---|
| camera traps | 400 | 382 | 11 | 7 |
| coral | 400 | 384 | 16 | 0 |
| plant traits | 400 | 388 | 12 | 0 |
| animal movement | 400 | 371 | 22 | 7 |
| biodiversity surveys | 400 | 373 | 22 | 5 |

Total indexed 1898, dropped 83, needs review 19.

## Drop reasons

- no data-like files: 72
- defense, military or intelligence funding: 11

## Needs review reasons

- affiliation may be a company (Corporation): 13
- affiliation may be a company (Consulting): 2
- affiliation may be a company (Technologies): 2
- affiliation may be a company (S.A.): 1
- affiliation may be a company (Company): 1

## Classification

- Indexed (company): 22
- Funding not stated: 764

## Method notes

- Funding is read from the Dryad funders field and abstract. A defense funder in a funder field or in a funding sentence drops the record. A defense name in text without a funding sentence goes to needs review.
- Linked paper acknowledgments were not read in this first version. Dryad funding fields are author entered and often empty.
- Company detection uses affiliation patterns and is conservative.
- Cache: /Users/heuremen/bones-forge/dryad_index/cache
- Re-run: python3 -I /Users/heuremen/bones-forge/dryad_index/sweep/dryad_sweep.py
