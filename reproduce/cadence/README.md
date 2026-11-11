# CADENCE reproduce kit

Heuremen LLC · https://indahl.ai/cadence · https://indahl.ai/reproduce

This kit recomputes the CADENCE headline number and its outcome label with the desk's own code (its scoring lines, copied as written), from what the kit holds, with its network proxies pointed at a closed port.

## The command

```
python3 run.py --check
```

Needs Python 3.9 or later and nothing else. It prints one line of JSON and checks it against expected.json. The line it must print has sha256 `bd1fa582abf223661c0665a91e2e38bef375cd629fa2b611f126480bb6be114a`.

## What it reproduces

The headline as the live feed https://indahl.ai/cadence/live.json served it at the feed stamp 11 Nov 00:00, read by us at 2026-11-11T00:08:50Z. The feed bytes had sha256 `0dbfb20b236c662318a075fa701520d6bb2e028c009ad2dd7a70cbcb47bccf35`.

- number: 15.8 years (5,782 days)
- value: 5782
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
| data/portal_bls.json | 829 | `80ba8297c7910cccb595d36ae684175eab9010a67f6aa679241e9c1c3802e424` |
| data/portal_cdc.json | 120,471 | `6be23ce1ddb643b6097d7e3724d278351082fc5260bd573fcf3aa875439c092f` |
| data/portal_cms.json | 2,265,126 | `94757ba75dffcc5e3681add14a9a36f8a0f3b8cf1b19ad2872c2c0eab8923ace` |
| data/portal_energy.json | 98,896 | `84ee4933706210c4694a7bde9774ae3c5269fe57c8faa8d99b63a2fd1ddc284e` |
| data/portal_healthcare_gov.json | 39,052 | `0d55bb796f99eafd82fe64ca8c310dfbc623c90e878ac841db4459dd2f5a0e56` |
| data/portal_healthdata_gov.json | 444,375 | `34e6d5f4be71899dd32686f0db3d9c55d6e985063defbf8a7cd24e67d168e211` |
| data/portal_labor.json | 98,682 | `78133855fac269565e39130f2db646fefc3ef5e12c2d090090a60ef68e9252f1` |
| data/portal_veterans_affairs.json | 205,199 | `aadf42eebfe0f80772eb5819d419ab7ffc30129df8e499f182f15dbbd1e57119` |

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
