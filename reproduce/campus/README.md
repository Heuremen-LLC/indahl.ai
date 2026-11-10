# CAMPUS reproduce kit

Heuremen LLC · https://indahl.ai/campus · https://indahl.ai/reproduce

This kit recomputes the CAMPUS headline number and its outcome label with the desk's own code (its scoring lines, copied as written), from what the kit holds, with its network proxies pointed at a closed port.

## The command

```
python3 run.py --check
```

Needs Python 3.9 or later and nothing else. It prints one line of JSON and checks it against expected.json. The line it must print has sha256 `e5f3789d15dfc9987b79a37085319a0f91401da5d9a8a46ef2b2d0b85944f9b8`.

## What it reproduces

The headline as the live feed https://indahl.ai/campus/live.json served it at the feed stamp 10 Nov 22:48, read by us at 2026-11-10T23:47:02Z. The feed bytes had sha256 `e4229338e17b55845669d34bfb0467c3674e24e4e5f78fe3e3539417a6508dab`.

- number: 271 of 308
- value: 271
- outcome: none, this headline carries no outcome label

The live page can move inside the interval between releases. Each move outside it, or a change of label, gets a new row in our ledger, and a release is refused until this kit reproduces the number that row covers. The headline fields are the ones the ledger reads (`kit.json`, headline).

## Inputs

Not included. Each school keeps its rights to its pages, and the data pack holds only our status counts, so this kit carries no copy of the source data. MANIFEST.json lists each input file the desk's scoring read, with its size, its sha256 and the time it was last written. We keep those exact files and rerun this kit on them before every release.

The input files are what the desk kept from its reads of the sources, with the time of each read where the desk records it. To check them, read the sources below again and compare. With a copy of the input files, `python3 run.py --check --inputs DIR` reruns the kit on them. A file whose sha256 differs from MANIFEST.json is named and the run stops. Sources change, so a later read can differ from ours.

- Every external source cited on https://indahl.ai/oy, read pass after pass. The newest line of data/reads.jsonl holds the status of each address on the newest pass, with the pass time.

## Sources and their terms

As the CAMPUS data pack lists them. Credit each source when you use its values.

- School pages and documents cited on the OY page, https://indahl.ai/oy. Each school keeps its rights. The pack holds only our status counts.

## Input files

| File | Bytes | sha256 |
|---|---|---|
| data/reads.jsonl | 6,084,375 | `231bed0be3f71bb799a2321d7fe2d23f16f1940f6fd2e268751ea0a93421a250` |

## Code

The desk's tick script reads its sources, scores and publishes in one run, so it never runs in a kit. code/campus_score.py is the scoring step of that script and nothing else: campus_tick.py lines 126 to 138, the stnow function and the state_now block. The desk files it follows are under desk/, byte for byte, to read beside it. The scripts that run: code/campus_score.py. Before every release the gate checks that this extract prints the number the desk published.

## Files

- kit.json: the steps, the output file and the headline fields.
- run.py: the command.
- expected.json and expected.sha256: the line run.py must print.
- published.json: the headline as the live feed served it when this kit was made.
- MANIFEST.json: every input and code file with its sha256.
- desk/: the desk scripts the extract follows, where the kit runs an extract.
- SHA256SUMS.txt: the sha256 of every file in this folder.
