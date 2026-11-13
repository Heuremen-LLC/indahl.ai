# QUAKE reproduce kit

Heuremen LLC · https://indahl.ai/quake · https://indahl.ai/reproduce

This kit recomputes the QUAKE headline number and its outcome label with the desk's own code (its scoring lines, copied as written), from what the kit holds, with its network proxies pointed at a closed port.

## The command

```
python3 run.py --check
```

Needs Python 3.9 or later and nothing else. It prints one line of JSON and checks it against expected.json. The line it must print has sha256 `91830c21cf5c04d1fdb987c987e5f7b261414c163c96512bba06e1eb7d4e096c`.

## What it reproduces

The headline as the live feed https://indahl.ai/quake/live.json served it at the feed stamp 2026-11-13T11:59:38Z, read by us at 2026-11-13T14:09:17Z. The feed bytes had sha256 `5c95b8f8b2b34c961f4b5f127b422e289788ec99adfef62f6dcf94477413cd3e`.

- number: 30,760 of 31,963
- value: 0.9624
- interval: 0.946 to 0.9776
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
| data/quake_rows.json.gz | 3,795,555 | `7149d9a315c1f06873fddfcf13350a9f4792144791641aee63a466e5be2f3162` |
| summary_quake.json | 183,087 | `8b2c01270f85a52c91b9316e08bbc09f455ca40ffc2711b3b87e888f97c1214c` |

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
