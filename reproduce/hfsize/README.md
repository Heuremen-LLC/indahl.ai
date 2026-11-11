# HFSIZE reproduce kit

Heuremen LLC · https://indahl.ai/hfsize · https://indahl.ai/reproduce

This kit recomputes the HFSIZE headline number and its outcome label with the desk's own code (its scoring lines, copied as written), from what the kit holds, with its network proxies pointed at a closed port.

## The command

```
python3 run.py --check
```

Needs Python 3.9 or later and nothing else. It prints one line of JSON and checks it against expected.json. The line it must print has sha256 `308cd3c6ee10384ebb7a7d0439a5415567248201d94eb7646b3e3a5aace37119`.

## What it reproduces

The headline as the live feed https://indahl.ai/hfsize/live.json served it at the feed stamp 10 Nov 22:07, read by us at 2026-11-11T00:08:42Z. The feed bytes had sha256 `efb0c84072b9b2fcba1ccd3036e0ed8b768e26f0fab950f7ac1908914e7f2787`.

- number: 12 of 135
- value: 0.0889
- interval: 0.0516 to 0.1489
- outcome: CANNOT_TELL

The live page can move inside the interval between releases. Each move outside it, or a change of label, gets a new row in our ledger, and a release is refused until this kit reproduces the number that row covers. The headline fields are the ones the ledger reads (`kit.json`, headline).

## Inputs

Not included. The Hugging Face API is under its terms of service and not an open licence, so this kit carries no copy of the source data. MANIFEST.json lists each input file the desk's scoring read, with its size, its sha256 and the time it was last written. We keep those exact files and rerun this kit on them before every release.

The input files are what the desk kept from its reads of the sources, with the time of each read where the desk records it. To check them, read the sources below again and compare. With a copy of the input files, `python3 run.py --check --inputs DIR` reruns the kit on them. A file whose sha256 differs from MANIFEST.json is named and the run stops. Sources change, so a later read can differ from ours.

- The 1,000 most downloaded models, https://huggingface.co/api/models?sort=downloads&direction=-1&limit=1000
- For each model, https://huggingface.co/api/models/MODEL (safetensors totals), as hfsize_tick.py reads them. Each row of data/repos.json carries its read time.

## Sources and their terms

As the HFSIZE data pack lists them. Credit each source when you use its values.

- Hugging Face Hub API, https://huggingface.co/docs/hub/api. Hugging Face terms of service, https://huggingface.co/terms-of-service.

## Input files

| File | Bytes | sha256 |
|---|---|---|
| data/repos.json | 217,150 | `28b1118fd2e4f3974be0b0e107ae7f84534434b9534ad84ba29a421dce132932` |
| summary_hfsize.json | 4,478 | `efb0c84072b9b2fcba1ccd3036e0ed8b768e26f0fab950f7ac1908914e7f2787` |

## Code

The desk's tick script reads its sources, scores and publishes in one run, so it never runs in a kit. code/hfsize_score.py is the scoring step of that script and nothing else: hfsize_tick.py lines 56 to 57 and 63, the counts, the interval and the comparison block. The desk files it follows are under desk/, byte for byte, to read beside it. The scripts that run: code/hfsize_score.py. Before every release the gate checks that this extract prints the number the desk published.

## Files

- kit.json: the steps, the output file and the headline fields.
- run.py: the command.
- expected.json and expected.sha256: the line run.py must print.
- published.json: the headline as the live feed served it when this kit was made.
- MANIFEST.json: every input and code file with its sha256.
- desk/: the desk scripts the extract follows, where the kit runs an extract.
- SHA256SUMS.txt: the sha256 of every file in this folder.
