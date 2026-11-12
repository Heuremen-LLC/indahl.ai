# QUAKE reproduce kit

Heuremen LLC · https://indahl.ai/quake · https://indahl.ai/reproduce

This kit recomputes the QUAKE headline number and its outcome label with the desk's own code (its scoring lines, copied as written), from what the kit holds, with its network proxies pointed at a closed port.

## The command

```
python3 run.py --check
```

Needs Python 3.9 or later and nothing else. It prints one line of JSON and checks it against expected.json. The line it must print has sha256 `ad1d0ddddf72554eb2d2460f51f4fa3860269cc68e6ddeb4f991a858b3090649`.

## What it reproduces

The headline as the live feed https://indahl.ai/quake/live.json served it at the feed stamp 2026-11-12T14:40:02Z, read by us at 2026-11-12T16:06:35Z. The feed bytes had sha256 `2013151c52aaadd63704bab9e664bcb45079356eace2649fb4d6d0973d36b5ec`.

- number: 30,694 of 31,894
- value: 0.9624
- interval: 0.9459 to 0.9776
- outcome: CANNOT_TELL

The live page can move inside the interval between releases. Each move outside it, or a change of label, gets a new row in our ledger, and a release is refused until this kit reproduces the number that row covers. The headline fields are the ones the ledger reads (`kit.json`, headline).

## Inputs

The exact files the desk's scoring read, stored gzip-compressed under inputs/. run.py checks the sha256 of each one before it runs.

## Sources and their terms

As the QUAKE data pack lists them. Credit each source when you use its values.

- USGS ComCat event service, aftershock forecast product (oaf) and catalog, https://earthquake.usgs.gov/fdsnws/event/1/. U.S. government work, public domain (17 U.S.C. 105).
- USGS aftershock forecast documentation, https://earthquake.usgs.gov/data/oaf/overview.php. U.S. government work, public domain (17 U.S.C. 105).

## Input files

| File | Bytes | sha256 |
|---|---|---|
| data/quake_rows.json.gz | 3,789,068 | `d25d9cd57b30d95cd8ee493710c014508408b9083d2a512c577a90d828d578c4` |
| summary_quake.json | 183,129 | `b552ae6fbb31365233744ad90b243085326fe3bbcc7373c228aff4502f346b2f` |

## Code

The desk's tick script reads its sources, scores and publishes in one run, so it never runs in a kit. code/quake_score.py is the scoring step of that script and nothing else: quake_tick.py lines 17 to 18, 60 to 65, 328 to 348 and 360, the sequence-block bootstrap and the headline cell. The desk files it follows are under desk/, byte for byte, to read beside it. The scripts that run: code/quake_score.py. Before every release the gate checks that this extract prints the number the desk published.

## Files

- kit.json: the steps, the output file and the headline fields.
- run.py: the command.
- expected.json and expected.sha256: the line run.py must print.
- published.json: the headline as the live feed served it when this kit was made.
- MANIFEST.json: every input and code file with its sha256.
- desk/: the desk scripts the extract follows, where the kit runs an extract.
- SHA256SUMS.txt: the sha256 of every file in this folder.

## Note

data/quake_rows.json.gz holds every forecast window the run scored against the USGS catalog (the forecast files and catalog reads are about 460 MB). The block list and the gate result come from summary_quake.json, the summary of the same run.
