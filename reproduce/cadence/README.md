# CADENCE reproduce kit

Heuremen LLC · https://indahl.ai/cadence · https://indahl.ai/reproduce

This kit recomputes the CADENCE headline number and its outcome label with the desk's own code (its scoring lines, copied as written), from what the kit holds, with its network proxies pointed at a closed port.

## The command

```
python3 run.py --check
```

Needs Python 3.9 or later and nothing else. It prints one line of JSON and checks it against expected.json. The line it must print has sha256 `c02b58f3a52bf8c0d5edd6fec83ad5b45b7ab10e6127dc2cb3a15a0495f8d1c0`.

## What it reproduces

The headline as the live feed https://indahl.ai/cadence/live.json served it at the feed stamp 12 Nov 16:04, read by us at 2026-11-12T16:06:25Z. The feed bytes had sha256 `5bf71d8281ccd92db1fa65b38d7e1f2f8e840c726955f3c97f78cfd8fd6f2c37`.

- number: 15.8 years (5,784 days)
- value: 5784
- outcome: none, this headline carries no outcome label

The live page can move inside the interval between releases. Each move outside it, or a change of label, gets a new row in our ledger, and a release is refused until this kit reproduces the number that row covers. The headline fields are the ones the ledger reads (`kit.json`, headline).

## Inputs

The exact files the desk's scoring read, stored gzip-compressed under inputs/. run.py checks the sha256 of each one before it runs.

## Sources and their terms

As the CADENCE data pack lists them. Credit each source when you use its values.

- Federal agency data.json catalogues (DCAT-US), https://resources.data.gov/resources/dcat-us/. U.S. government work, public domain (17 U.S.C. 105).

## Input files

| File | Bytes | sha256 |
|---|---|---|
| data/portal_bls.json | 827 | `b2158fa348f68bd9014c5af56f248d183adc0abb63debebba5c58b2ff4ed7e2d` |
| data/portal_cdc.json | 120,472 | `b615cd0dee7bdf802f680269ce46573ca48740595c160e59842ff9a9476c8ef9` |
| data/portal_cms.json | 2,268,912 | `256a10a372b3fb7241fef3926b870d0e9d923aff5ecd9fa00ff2da3e8f0d9dcf` |
| data/portal_energy.json | 98,897 | `38bd7e0ef48958a1c9604bb5b528782e0456d921e6f321c4a2e50b27de4e2045` |
| data/portal_healthcare_gov.json | 39,053 | `78c419338337cfd3a3187db9779979ca170d6dad7f0e72c41b1c6a5a9aaa9756` |
| data/portal_healthdata_gov.json | 444,375 | `bde28e3f8b50d06cc3d4616cec03995289b1043ecfa6c97503e49583e54a188c` |
| data/portal_labor.json | 98,683 | `fde6eb31bf3bd6e5b5d36568c0011073e4b62240442b37b1ccf258f0d55ba266` |
| data/portal_veterans_affairs.json | 205,199 | `5818b36b5589f30a83183f5ad8831a21be67980cb047f7e22cb370b0d5aa4be9` |

## Code

The desk's tick script reads its sources, scores and publishes in one run, so it never runs in a kit. code/cadence_score.py is the scoring step of that script and nothing else: cadence_tick.py lines 8 to 32 and 70 to 95, the interval and date readers and the series and overdue loop. The desk files it follows are under desk/, byte for byte, to read beside it. The scripts that run: code/cadence_score.py. Before every release the gate checks that this extract prints the number the desk published.

## Files

- kit.json: the steps, the output file and the headline fields.
- run.py: the command.
- expected.json and expected.sha256: the line run.py must print.
- published.json: the headline as the live feed served it when this kit was made.
- MANIFEST.json: every input and code file with its sha256.
- desk/: the desk scripts the extract follows, where the kit runs an extract.
- SHA256SUMS.txt: the sha256 of every file in this folder.
