# CREDIT reproduce kit

Heuremen LLC · https://indahl.ai/credit · https://indahl.ai/reproduce

This kit recomputes the CREDIT headline number and its outcome label with the desk's own code (its scoring lines, copied as written), from what the kit holds, with its network proxies pointed at a closed port.

## The command

```
python3 run.py --check
```

Needs Python 3.9 or later with numpy (PyPI). It prints one line of JSON and checks it against expected.json. The line it must print has sha256 `c4bbbebe5e465479ebda2c9119dd058d7ef97807e75f5c08009462c3ff5bf5ff`.

## What it reproduces

The headline as the live feed https://indahl.ai/credit/live.json served it at the feed stamp 2026-11-10T18:10:06Z, read by us at 2026-11-12T16:06:29Z. The feed bytes had sha256 `f5da55d33a36cdb66ca3db1104ac0703446bb656d85376c85734bb5e83650627`.

- number: 99.5%
- value: 0.995496
- interval: 0.993463 to 0.996788
- outcome: CANNOT_TELL

The live page can move inside the interval between releases. Each move outside it, or a change of label, gets a new row in our ledger, and a release is refused until this kit reproduces the number that row covers. The headline fields are the ones the ledger reads (`kit.json`, headline).

## Inputs

The exact files the desk's scoring read, stored gzip-compressed under inputs/. run.py checks the sha256 of each one before it runs.

## Sources and their terms

As the CREDIT data pack lists them. Credit each source when you use its values.

- CFPB Consumer Complaint Database (company-level counts only, no complaint text or ZIP code), https://www.consumerfinance.gov/data-research/consumer-complaints/. CC0 as the CFPB search service states, U.S. government work.
- CFPB Consumer Response Annual Reports 2021 to 2025, https://www.consumerfinance.gov/data-research/research-reports/. U.S. government work, public domain (17 U.S.C. 105).
- CFPB Terms of Credit Card Plans survey, https://www.consumerfinance.gov/data-research/credit-card-data/terms-credit-card-plans-survey/. U.S. government work, public domain (17 U.S.C. 105).
- Federal Reserve G.19 Consumer Credit, terms of credit, https://www.federalreserve.gov/releases/g19/. Federal Reserve Board data, public.

## Input files

| File | Bytes | sha256 |
|---|---|---|
| data/cache/agg_db66181722a6a49b.json | 22,573,220 | `0430f1e1ce9c9815905c95484834893f1bba4570c03aa588c566b4c6f0960fcb` |

## Code

The desk's tick script reads its sources, scores and publishes in one run, so it never runs in a kit. code/credit_score.py is the scoring step of that script and nothing else: credit_tick.py lines 23, 39, 128 to 150 and 195 to 200, the printed band, the company-month block bootstrap and ruler one for 2025. The desk files it follows are under desk/, byte for byte, to read beside it. The scripts that run: code/credit_score.py. Before every release the gate checks that this extract prints the number the desk published.

## Files

- kit.json: the steps, the output file and the headline fields.
- run.py: the command.
- expected.json and expected.sha256: the line run.py must print.
- published.json: the headline as the live feed served it when this kit was made.
- MANIFEST.json: every input and code file with its sha256.
- desk/: the desk scripts the extract follows, where the kit runs an extract.
- SHA256SUMS.txt: the sha256 of every file in this folder.

## Note

The aggregate file holds company, month, product family, complaints and complaints not answered in time, counted by credit_tick.py from the CFPB complaint database download (about 365 MB, no complaint text kept). Its name carries the first 16 characters of the sha256 of the download it was counted from.
