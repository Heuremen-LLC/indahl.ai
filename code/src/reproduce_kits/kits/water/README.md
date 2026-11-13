# WATER reproduce kit

Heuremen LLC · https://indahl.ai/water · https://indahl.ai/reproduce

This kit recomputes the WATER headline number and its outcome label with the desk's own code (its scoring lines, copied as written), from what the kit holds, with its network proxies pointed at a closed port.

## The command

```
python3 run.py --check
```

Needs Python 3.9 or later and nothing else. It prints one line of JSON and checks it against expected.json. The line it must print has sha256 `9fa82deee3bf63d3989a180ae7ff29fed0d2d341b59a49bcbe5a37f4640537cf`.

## What it reproduces

The headline as the live feed https://indahl.ai/water/live.json served it at the feed stamp 2026-11-12 15:58, read by us at 2026-11-12T16:06:27Z. The feed bytes had sha256 `2fde04377b5b32318be6752e852f96e8ac5aa73ecac5ee321961171711f4a081`.

- number: 42 of 83
- value: 0.51
- interval: 0.299 to 0.701
- outcome: BELOW

The live page can move inside the interval between releases. Each move outside it, or a change of label, gets a new row in our ledger, and a release is refused until this kit reproduces the number that row covers. The headline fields are the ones the ledger reads (`kit.json`, headline).

## Inputs

The exact files the desk's scoring read, stored gzip-compressed under inputs/. run.py checks the sha256 of each one before it runs.

## Sources and their terms

As the WATER data pack lists them. Credit each source when you use its values.

- Reclamation 24-Month Study, https://data.usbr.gov/rise/api/catalog-record/6331. U.S. government work, public domain (17 U.S.C. 105).
- Reclamation HDB, https://www.usbr.gov/pn-bin/hdb/hdb.pl. U.S. government work, public domain (17 U.S.C. 105).
- USGS water data, https://waterdata.usgs.gov/. U.S. government work, public domain (17 U.S.C. 105).
- California CDEC (live panel only), https://cdec.water.ca.gov/. California DWR public data.

## Input files

| File | Bytes | sha256 |
|---|---|---|
| data/water.json | 5,278,423 | `24acba733746253260d2447fa74219eab10bfc593ed07ae9b2a4ccb47c32cde8` |
| summary_water.json | 228,645 | `2df31d8dbf2f879bffbbb32bab78ce5e6e3a7045ea4c7e0d5903470f03ad4bc3` |

## Code

The desk's tick script reads its sources, scores and publishes in one run, so it never runs in a kit. code/water_score.py is the scoring step of that script and nothing else: water_tick.py lines 34, 180 to 186, 213 to 220 and 464, the verdict and the six-month band cells. The desk files it follows are under desk/, byte for byte, to read beside it. The scripts that run: code/water_score.py. Before every release the gate checks that this extract prints the number the desk published.

## Files

- kit.json: the steps, the output file and the headline fields.
- run.py: the command.
- expected.json and expected.sha256: the line run.py must print.
- published.json: the headline as the live feed served it when this kit was made.
- MANIFEST.json: every input and code file with its sha256.
- desk/: the desk scripts the extract follows, where the kit runs an extract.
- SHA256SUMS.txt: the sha256 of every file in this folder.

## Note

data/water.json holds every scored row the run made from the Reclamation 24-Month Study reports and the measured levels. The reports themselves are about 1.6 GB of PDFs, listed with their addresses in the RISE catalog. The run's gate reads two of those reports, so the kit takes its result from summary_water.json.
