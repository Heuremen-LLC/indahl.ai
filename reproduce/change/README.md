# CHANGE reproduce kit

Heuremen LLC · https://indahl.ai/change · https://indahl.ai/reproduce

This kit recomputes the CHANGE headline number and its outcome label with the desk's own code (its scoring lines, copied as written), from what the kit holds, with its network proxies pointed at a closed port.

## The command

```
python3 run.py --check
```

Needs Python 3.9 or later and nothing else. It prints one line of JSON and checks it against expected.json. The line it must print has sha256 `3da1b7f2707fa3cff0dab7ba2eb91494b96fadb45ee93ef03eeadccd7041c4a8`.

## What it reproduces

The headline as the live feed https://indahl.ai/change/live.json served it at the feed stamp 13 Nov 18:01, read by us at 2026-11-13T18:11:01Z. The feed bytes had sha256 `026839a7474fd5f6a4c3854a0f81e757f3dac52882264c2c5887924ce12c2e4e`.

- number: 10 of 33
- value: 10
- outcome: none, this headline carries no outcome label

The live page can move inside the interval between releases. Each move outside it, or a change of label, gets a new row in our ledger, and a release is refused until this kit reproduces the number that row covers. The headline fields are the ones the ledger reads (`kit.json`, headline).

## Inputs

Not included. The vendor pages carry mixed terms and one bars automated copying, so this kit carries no copy of the source data. MANIFEST.json lists each input file the desk's scoring read, with its size, its sha256 and the time it was last written. We keep those exact files and rerun this kit on them before every release.

The input files are what the desk kept from its reads of the sources, with the time of each read where the desk records it. To check them, read the sources below again and compare. With a copy of the input files, `python3 run.py --check --inputs DIR` reruns the kit on them. A file whose sha256 differs from MANIFEST.json is named and the run stops. Sources change, so a later read can differ from ours.

- The Google model deprecation page and the other vendor pages listed in the sources block of https://indahl.ai/change/live.json. data/rows.json holds each dated row as read, with the first and last time it was seen.

## Input files

| File | Bytes | sha256 |
|---|---|---|
| data/rows.json | 116,248 | `ef7d26bb554f9294cb1de7fbcdc88304febc4751c7dd060fc36dc53264c8f7e2` |

## Code

The desk's tick script reads its sources, scores and publishes in one run, so it never runs in a kit. code/change_score.py is the scoring step of that script and nothing else: change_tick.py lines 128 to 143, the days and life_of functions and the lifespan block. The desk files it follows are under desk/, byte for byte, to read beside it. The scripts that run: code/change_score.py. Before every release the gate checks that this extract prints the number the desk published.

## Files

- kit.json: the steps, the output file and the headline fields.
- run.py: the command.
- expected.json and expected.sha256: the line run.py must print.
- published.json: the headline as the live feed served it when this kit was made.
- MANIFEST.json: every input and code file with its sha256.
- desk/: the desk scripts the extract follows, where the kit runs an extract.
- SHA256SUMS.txt: the sha256 of every file in this folder.
