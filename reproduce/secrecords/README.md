# SECRECORDS reproduce kit

Heuremen LLC · https://indahl.ai/secrecords · https://indahl.ai/reproduce

This kit recomputes the SECRECORDS headline number and its outcome label with the desk's own code (its scoring lines, copied as written), from what the kit holds, with its network proxies pointed at a closed port.

## The command

```
python3 run.py --check
```

Needs Python 3.9 or later and nothing else. It prints one line of JSON and checks it against expected.json. The line it must print has sha256 `143c8e7cbf29f81b88662acb49a55a7073e67f030acfe23a680720cd57ed878b`.

## What it reproduces

The headline as the live feed https://indahl.ai/secrecords/live.json served it at the feed stamp 10 Nov 18:23, read by us at 2026-11-10T23:47:03Z. The feed bytes had sha256 `08328af2090273071ce33394a74c4485548f79f03df2dd0f11a733c24d4a2561`.

- number: 14%
- value: 0.1379
- interval: 0.0911 to 0.2035
- outcome: CANNOT_TELL

The live page can move inside the interval between releases. Each move outside it, or a change of label, gets a new row in our ledger, and a release is refused until this kit reproduces the number that row covers. The headline fields are the ones the ledger reads (`kit.json`, headline).

## Inputs

Not included. The Tranco list draws on a non-commercial input and a share-alike input, so this kit carries no copy of the source data. MANIFEST.json lists each input file the desk's scoring read, with its size, its sha256 and the time it was last written. We keep those exact files and rerun this kit on them before every release.

The input files are what the desk kept from its reads of the sources, with the time of each read where the desk records it. To check them, read the sources below again and compare. With a copy of the input files, `python3 run.py --check --inputs DIR` reruns the kit on them. A file whose sha256 differs from MANIFEST.json is named and the run stops. Sources change, so a later read can differ from ours.

- The domain list: the top 1,000 rows of the Tranco list of the date in data/listdate.txt of the desk, https://tranco-list.eu/
- For each domain, the first HTTPS response of https://DOMAIN/ (no redirect followed) and its SPF record read through DNS over HTTPS, as secrecords_tick.py does. Each row of data/domains.json carries the time it was read in its read field.

## Sources and their terms

As the SECRECORDS data pack lists them. Credit each source when you use its values.

- Tranco list, https://tranco-list.eu/. Tranco terms, built from inputs that include CC BY-NC and share-alike data.
- HTTPS headers and DNS records of each domain, https://indahl.ai/secrecords. Public protocol facts, our own reads.

## Input files

| File | Bytes | sha256 |
|---|---|---|
| data/domains.json | 368,085 | `ad23f873004af332dfddb5b550f39881dffaf448a21d2dc9599952a594c9f167` |
| summary_secrecords.json | 15,162 | `08328af2090273071ce33394a74c4485548f79f03df2dd0f11a733c24d4a2561` |

## Code

The desk's tick script reads its sources, scores and publishes in one run, so it never runs in a kit. code/secrecords_score.py is the scoring step of that script and nothing else: secrecords_tick.py lines 140 to 145, the grp function and the comparison block. The desk files it follows are under desk/, byte for byte, to read beside it. The scripts that run: code/secrecords_score.py. Before every release the gate checks that this extract prints the number the desk published.

## Files

- kit.json: the steps, the output file and the headline fields.
- run.py: the command.
- expected.json and expected.sha256: the line run.py must print.
- published.json: the headline as the live feed served it when this kit was made.
- MANIFEST.json: every input and code file with its sha256.
- desk/: the desk scripts the extract follows, where the kit runs an extract.
- SHA256SUMS.txt: the sha256 of every file in this folder.
