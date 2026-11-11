# FEDSEP reproduce kit

Heuremen LLC · https://indahl.ai/fedsep · https://indahl.ai/reproduce

This kit recomputes the FEDSEP headline number and its outcome label with the desk's own code (its scoring lines, copied as written), from what the kit holds, with its network proxies pointed at a closed port.

## The command

```
python3 run.py --check
```

Needs Python 3.9 or later and nothing else. It prints one line of JSON and checks it against expected.json. The line it must print has sha256 `680a854c4505ecb81bdc0636b200e87c996e7ee0b9ed1ac8b7d7dc322cb1492d`.

## What it reproduces

The headline as the live feed https://indahl.ai/fedsep/live.json served it at the feed stamp 10 Nov 22:48, read by us at 2026-11-11T00:08:50Z. The feed bytes had sha256 `a597069318580396105f05ce649a286f7e55ac3b1c7074883dcbd4425b37b147`.

- number: 10 of 37
- value: 0.2703
- interval: 0.0811 to 0.4872
- outcome: CONSISTENT

The live page can move inside the interval between releases. Each move outside it, or a change of label, gets a new row in our ledger, and a release is refused until this kit reproduces the number that row covers. The headline fields are the ones the ledger reads (`kit.json`, headline).

## Inputs

The exact files the desk's scoring read, stored gzip-compressed under inputs/. run.py checks the sha256 of each one before it runs.

## Sources and their terms

As the FEDSEP data pack lists them. Credit each source when you use its values.

- FOMC Summary of Economic Projections, https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm. U.S. government work, public domain (17 U.S.C. 105).
- BEA NIPA tables, https://www.bea.gov/. U.S. government work, public domain (17 U.S.C. 105).
- BLS unemployment rate LNS14000000, https://www.bls.gov/. U.S. government work, public domain (17 U.S.C. 105).
- Federal Reserve H.15, https://www.federalreserve.gov/releases/h15/. U.S. government work, public domain (17 U.S.C. 105).

## Input files

| File | Bytes | sha256 |
|---|---|---|
| data/projections.json | 4,223 | `389aa46dd55e746079d0426e73bf4de42b087088ec596c0fd7cc821e6b031c3b` |
| data/outcomes_day.json | 2,431 | `0bdf9cc7e86e810e0906027f425f2b194bd44e3f4b9ab6992cbe14da57357587` |

## Code

The desk's tick script reads its sources, scores and publishes in one run, so it never runs in a kit. code/fedsep_score.py is the scoring step of that script and nothing else: fedsep_tick.py lines 24 and 49 to 69, the inside test, the triples and the pooled bootstrap. The desk files it follows are under desk/, byte for byte, to read beside it. The scripts that run: code/fedsep_score.py. Before every release the gate checks that this extract prints the number the desk published.

## Files

- kit.json: the steps, the output file and the headline fields.
- run.py: the command.
- expected.json and expected.sha256: the line run.py must print.
- published.json: the headline as the live feed served it when this kit was made.
- MANIFEST.json: every input and code file with its sha256.
- desk/: the desk scripts the extract follows, where the kit runs an extract.
- SHA256SUMS.txt: the sha256 of every file in this folder.
