# QUAKE reproduce kit

Heuremen LLC · https://indahl.ai/quake · https://indahl.ai/reproduce

This kit recomputes the QUAKE headline number and its outcome label with the desk's own code (its scoring lines, copied as written), from what the kit holds, with its network proxies pointed at a closed port.

## The command

```
python3 run.py --check
```

Needs Python 3.9 or later and nothing else. It prints one line of JSON and checks it against expected.json. The line it must print has sha256 `04c5991de0c9e183eaec21f81776d2391235f2dc1add25d889efa18f9d79794d`.

## What it reproduces

The headline as the live feed https://indahl.ai/quake/live.json served it at the feed stamp 2026-11-10T20:42:24Z, read by us at 2026-11-10T23:47:16Z. The feed bytes had sha256 `3673b8ac606ac795a4c07381b7425840880d0431e9f812826178049c99f45909`.

- number: 30,777 of 31,968
- value: 0.9627
- interval: 0.9465 to 0.9777
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
| data/quake_rows.json.gz | 3,787,407 | `48a3a1b54c07c5dd99500d7a66e660506f070f99475b0ca170f39bdf5b359e6a` |
| summary_quake.json | 174,869 | `a72ecdea15b9b676affeed38a67441b521a10a696f1910e706e9abeac0f2701c` |

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
