# TRIALS reproduce kit

Heuremen LLC · https://indahl.ai/trials · https://indahl.ai/reproduce

This kit recomputes the TRIALS headline number and its outcome label with the desk's own code, from what the kit holds, with its network proxies pointed at a closed port.

## The command

```
python3 run.py --check
```

Needs Python 3.9 or later and nothing else. It prints one line of JSON and checks it against expected.json. The line it must print has sha256 `465d4475aaf21301d6efeaaf2a0c76e2e1f11b3d6cced0694da959dd1886c9d8`.

## What it reproduces

The headline as the live feed https://indahl.ai/trials/live.json served it at the feed stamp 2026-11-10 20:43 UTC, read by us at 2026-11-10T23:47:25Z. The feed bytes had sha256 `b0def2b0e36f55f04324e16b3a64cad9b7eb2ea653737e1a7802263c3ecdf471`.

- number: 21.5%
- value: 0.2147
- interval: 0.2094 to 0.2202
- outcome: CANNOT_TELL

The live page can move inside the interval between releases. Each move outside it, or a change of label, gets a new row in our ledger, and a release is refused until this kit reproduces the number that row covers. The headline fields are the ones the ledger reads (`kit.json`, headline).

## Inputs

The exact files the desk's scoring read, stored gzip-compressed under inputs/. run.py checks the sha256 of each one before it runs.

## Sources and their terms

As the TRIALS data pack lists them. Credit each source when you use its values.

- ClinicalTrials.gov API v2, https://clinicaltrials.gov/data-api/api. U.S. National Library of Medicine, public data, cite ClinicalTrials.gov.

## Input files

| File | Bytes | sha256 |
|---|---|---|
| data/records.jsonl | 7,086,998 | `6b9aea11d1bac0ebeb6bc16d0ee7b78dc0c7b6e9f878ab43292c3136c457f590` |
| data/read_at.txt | 55 | `7a89b133aca86185aa54ff9c70099fb9fe52b7fb27726f610e372509d48a78d6` |

## Code

The desk's own scripts, byte for byte, under code/. They run in this order: code/trials_summary.py. The same files are in the public repository under code/trials/.

## Files

- kit.json: the steps, the output file and the headline fields.
- run.py: the command.
- expected.json and expected.sha256: the line run.py must print.
- published.json: the headline as the live feed served it when this kit was made.
- MANIFEST.json: every input and code file with its sha256.
- desk/: the desk scripts the extract follows, where the kit runs an extract.
- SHA256SUMS.txt: the sha256 of every file in this folder.
