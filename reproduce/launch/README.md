# LAUNCH reproduce kit

Heuremen LLC · https://indahl.ai/launch · https://indahl.ai/reproduce

This kit recomputes the LAUNCH headline number and its outcome label with the desk's own code (its scoring lines, copied as written), from what the kit holds, with its network proxies pointed at a closed port.

## The command

```
python3 run.py --check
```

Needs Python 3.9 or later and nothing else. It prints one line of JSON and checks it against expected.json. The line it must print has sha256 `f91d5f1d0e8633f38789842658885b2448ca3376ff7eeeb0e512841cc7c41ba4`.

## What it reproduces

The headline as the live feed https://indahl.ai/launch/live.json served it at the feed stamp 12 Nov 16:04, read by us at 2026-11-12T16:06:22Z. The feed bytes had sha256 `67b6490dc00456692c34fc010a49b789c9338552f2a9c65dce6213fb61702179`.

- number: 11
- value: 11
- outcome: CANNOT_TELL

The live page can move inside the interval between releases. Each move outside it, or a change of label, gets a new row in our ledger, and a release is refused until this kit reproduces the number that row covers. The headline fields are the ones the ledger reads (`kit.json`, headline).

## Inputs

Not included. The Space Devs state no data licence for Launch Library 2, so this kit carries no copy of the source data. MANIFEST.json lists each input file the desk's scoring read, with its size, its sha256 and the time it was last written. We keep those exact files and rerun this kit on them before every release.

The input files are what the desk kept from its reads of the sources, with the time of each read where the desk records it. To check them, read the sources below again and compare. With a copy of the input files, `python3 run.py --check --inputs DIR` reruns the kit on them. A file whose sha256 differs from MANIFEST.json is named and the run stops. Sources change, so a later read can differ from ours.

- Launch Library 2, https://ll.thespacedevs.com/2.3.0/launches/upcoming/?limit=100&mode=normal and .../previous/?limit=100&mode=normal, read every 6 ticks. Each row of data/snapshots.jsonl is one launch as read, with the read time in its read field.

## Sources and their terms

As the LAUNCH data pack lists them. Credit each source when you use its values.

- Launch Library 2, https://thespacedevs.com/llapi. The Space Devs terms, no data licence stated.

## Input files

| File | Bytes | sha256 |
|---|---|---|
| data/snapshots.jsonl | 2,427,958 | `6b9b362045e35766adcff30ff4cb1833edfce4bc73469b87dcbd9c8e0c7f7f54` |

## Code

The desk's tick script reads its sources, scores and publishes in one run, so it never runs in a kit. code/launch_score.py is the scoring step of that script and nothing else: launch_tick.py lines 28 to 58, flown_watched and the cells, without the count still waiting. The desk files it follows are under desk/, byte for byte, to read beside it. The scripts that run: code/launch_score.py. Before every release the gate checks that this extract prints the number the desk published.

## Files

- kit.json: the steps, the output file and the headline fields.
- run.py: the command.
- expected.json and expected.sha256: the line run.py must print.
- published.json: the headline as the live feed served it when this kit was made.
- MANIFEST.json: every input and code file with its sha256.
- desk/: the desk scripts the extract follows, where the kit runs an extract.
- SHA256SUMS.txt: the sha256 of every file in this folder.
