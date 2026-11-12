# TRIALS reproduce kit

Heuremen LLC · https://indahl.ai/trials · https://indahl.ai/reproduce

This kit recomputes the TRIALS headline number and its outcome label with the desk's own code, from what the kit holds, with its network proxies pointed at a closed port.

## The command

```
python3 run.py --check
```

Needs Python 3.9 or later and nothing else. It prints one line of JSON and checks it against expected.json. The line it must print has sha256 `1b18b25916c0caf76c90a0f35d185455a85e83d7411d31301aaf52f22e752213`.

## What it reproduces

The headline as the live feed https://indahl.ai/trials/live.json served it at the feed stamp 2026-11-12 15:31 UTC, read by us at 2026-11-12T16:25:58Z. The feed bytes had sha256 `af589b3274b2fdf5d6eb5978437e57195d3b3ee6fd6d9d93a51c0bcf4e98f681`.

- number: 21.5%
- value: 0.2149
- interval: 0.2095 to 0.2203
- outcome: ABOVE

The live page can move inside the interval between releases. Each move outside it, or a change of label, gets a new row in our ledger, and a release is refused until this kit reproduces the number that row covers. The headline fields are the ones the ledger reads (`kit.json`, headline).

## Inputs

The exact files the desk's scoring read, stored gzip-compressed under inputs/. run.py checks the sha256 of each one before it runs.

## Sources and their terms

As the TRIALS data pack lists them. Credit each source when you use its values.

- ClinicalTrials.gov API v2, https://clinicaltrials.gov/data-api/api. U.S. National Library of Medicine, public data, cite ClinicalTrials.gov.

## Input files

| File | Bytes | sha256 |
|---|---|---|
| data/records.jsonl | 7,088,103 | `b1eb2b32cfbbea14b243c88f1c506b454a18214c3029d6ce27a8db803d8e50de` |
| data/read_at.txt | 55 | `c53514a34e1193b6802a3df2279b6735252047d207aad4ef7c8df49a53fa98c6` |

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
