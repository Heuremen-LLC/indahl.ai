# LINKROT reproduce kit

Heuremen LLC · https://indahl.ai/linkrot · https://indahl.ai/reproduce

This kit recomputes the LINKROT headline number and its outcome label with the desk's own code (its scoring lines, copied as written), from what the kit holds, with its network proxies pointed at a closed port.

## The command

```
python3 run.py --check
```

Needs Python 3.9 or later and nothing else. It prints one line of JSON and checks it against expected.json. The line it must print has sha256 `a68001ac446bea6ff9593871ffc5973bdd8316e9bf9c737be39e7873f3fd5858`.

## What it reproduces

The headline as the live feed https://indahl.ai/linkrot/live.json served it at the feed stamp 12 Nov 16:04, read by us at 2026-11-12T16:06:15Z. The feed bytes had sha256 `9334903fdeee2a2acf0f3a94f3eb527ad3dbf5837707e20581e7a09e511348db`.

- number: 3.4%
- value: 0.0339
- interval: 0.0268 to 0.0429
- outcome: CONSISTENT

The live page can move inside the interval between releases. Each move outside it, or a change of label, gets a new row in our ledger, and a release is refused until this kit reproduces the number that row covers. The headline fields are the ones the ledger reads (`kit.json`, headline).

## Inputs

The exact files the desk's scoring read, stored gzip-compressed under inputs/. run.py checks the sha256 of each one before it runs.

## Sources and their terms

As the LINKROT data pack lists them. Credit each source when you use its values.

- arXiv API abstracts and comments (links), https://info.arxiv.org/help/api/. CC0 1.0 for metadata.
- Link targets read over HTTP, https://indahl.ai/linkrot. Our own measurements.

## Input files

| File | Bytes | sha256 |
|---|---|---|
| data/links.json | 481,569 | `2a8951301a1173108a3211c5610084a944ce7557c55915a9e4b7d74ab27592d0` |
| summary_linkrot.json | 13,656 | `9334903fdeee2a2acf0f3a94f3eb527ad3dbf5837707e20581e7a09e511348db` |

## Code

The desk's tick script reads its sources, scores and publishes in one run, so it never runs in a kit. code/linkrot_score.py is the scoring step of that script and nothing else: linkrot_tick.py lines 84 to 92 and 101, the cell and combined functions and the all cell. The desk files it follows are under desk/, byte for byte, to read beside it. The scripts that run: code/linkrot_score.py. Before every release the gate checks that this extract prints the number the desk published.

## Files

- kit.json: the steps, the output file and the headline fields.
- run.py: the command.
- expected.json and expected.sha256: the line run.py must print.
- published.json: the headline as the live feed served it when this kit was made.
- MANIFEST.json: every input and code file with its sha256.
- desk/: the desk scripts the extract follows, where the kit runs an extract.
- SHA256SUMS.txt: the sha256 of every file in this folder.

## Note

The outcome needs the desk's own live gate to have passed on the run (a planted live link and a planted dead link read as expected). That gate cannot be replayed, so the kit reads its result from summary_linkrot.json, the summary that run wrote.
