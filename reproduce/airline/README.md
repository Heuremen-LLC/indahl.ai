# AIRLINE reproduce kit

Heuremen LLC · https://indahl.ai/airline · https://indahl.ai/reproduce

This kit recomputes the AIRLINE headline number and its outcome label with the desk's own code (its scoring lines, copied as written), from what the kit holds, with its network proxies pointed at a closed port.

## The command

```
python3 run.py --check
```

Needs Python 3.9 or later and nothing else. It prints one line of JSON and checks it against expected.json. The line it must print has sha256 `f32a4e777ddcb767a5d232aacfb62cb2fdaa988637a2dba251a24714e2230e58`.

## What it reproduces

The headline as the live feed https://indahl.ai/airline/live.json served it at the feed stamp 29 Oct 16:35, read by us at 2026-11-11T00:08:49Z. The feed bytes had sha256 `74cb787d3e003caa806302c3de6bbf2ea41e15093e8664cc344918fe0d41961e`.

- number: 5 of 13
- value: 5
- outcome: none, this headline carries no outcome label

The live page can move inside the interval between releases. Each move outside it, or a change of label, gets a new row in our ledger, and a release is refused until this kit reproduces the number that row covers. The headline fields are the ones the ledger reads (`kit.json`, headline).

## Inputs

The exact files the desk's scoring read, stored gzip-compressed under inputs/. run.py checks the sha256 of each one before it runs.

## Sources and their terms

As the AIRLINE data pack lists them. Credit each source when you use its values.

- BTS Reporting Carrier On-Time Performance, https://www.transtats.bts.gov/. U.S. government work, public domain (17 U.S.C. 105).
- FAA NAS Status airport feed, https://nasstatus.faa.gov/. U.S. government work, public domain (17 U.S.C. 105).

## Input files

| File | Bytes | sha256 |
|---|---|---|
| data/results.json | 5,463 | `37c29945a6e92913cea3ca181df916237593bef70c38205171d5ff4618a45850` |

## Code

The desk's tick script reads its sources, scores and publishes in one run, so it never runs in a kit. code/airline_score.py is the scoring step of that script and nothing else: airline_summary.py lines 12 to 25, the table of 2026 against 2025 and the headline block. The desk files it follows are under desk/, byte for byte, to read beside it. The scripts that run: code/airline_score.py. Before every release the gate checks that this extract prints the number the desk published.

## Files

- kit.json: the steps, the output file and the headline fields.
- run.py: the command.
- expected.json and expected.sha256: the line run.py must print.
- published.json: the headline as the live feed served it when this kit was made.
- MANIFEST.json: every input and code file with its sha256.
- desk/: the desk scripts the extract follows, where the kit runs an extract.
- SHA256SUMS.txt: the sha256 of every file in this folder.

## Note

data/results.json holds the per-airline comparisons airline_tick.py made from the BTS month files (route medians and their bootstrap intervals). This kit starts from that file. The month files are the BTS Reporting Carrier On-Time Performance downloads, about 37 MB, read by airline_tick.py.
