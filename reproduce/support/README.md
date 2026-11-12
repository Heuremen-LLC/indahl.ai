# SUPPORT reproduce kit

Heuremen LLC · https://indahl.ai/support · https://indahl.ai/reproduce

This kit recomputes the SUPPORT headline number and its outcome label with the desk's own code (its scoring lines, copied as written), from what the kit holds, with its network proxies pointed at a closed port.

## The command

```
python3 run.py --check
```

Needs Python 3.9 or later and nothing else. It prints one line of JSON and checks it against expected.json. The line it must print has sha256 `7b50da5963d4ea65bfbfd163b110d6ef3e64f5a9c2ba3bcd3bb25958f1033c95`.

## What it reproduces

The headline as the live feed https://indahl.ai/support/live.json served it at the feed stamp 12 Nov 15:38, read by us at 2026-11-12T16:06:19Z. The feed bytes had sha256 `1bcaeeaa89763289e331f1723a304ec48e28bc851d45344ac486dce7c73b23f6`.

- number: 24%
- value: 0.2419
- interval: 0.154 to 0.3375
- outcome: ABOVE

The live page can move inside the interval between releases. Each move outside it, or a change of label, gets a new row in our ledger, and a release is refused until this kit reproduces the number that row covers. The headline fields are the ones the ledger reads (`kit.json`, headline).

## Inputs

Not included. The endoflife.date licence was not confirmed for this pack, so this kit carries no copy of the source data. MANIFEST.json lists each input file the desk's scoring read, with its size, its sha256 and the time it was last written. We keep those exact files and rerun this kit on them before every release.

The input files are what the desk kept from its reads of the sources, with the time of each read where the desk records it. To check them, read the sources below again and compare. With a copy of the input files, `python3 run.py --check --inputs DIR` reruns the kit on them. A file whose sha256 differs from MANIFEST.json is named and the run stops. Sources change, so a later read can differ from ours.

- For each product, https://endoflife.date/api/PRODUCT.json, read on the date of the updated field of the feed. The class of each cycle (supported, and no release in more than a year) was set on that date and is stored in each row.

## Sources and their terms

As the SUPPORT data pack lists them. Credit each source when you use its values.

- endoflife.date API, https://endoflife.date/docs/api. Endoflife.date terms.

## Input files

| File | Bytes | sha256 |
|---|---|---|
| data/cycles.json | 1,921,734 | `a9d78aca647a8ef77135506f8cf6905f18b69e6f0fccf2835bfd1d757d6d658f` |
| summary_support.json | 22,393 | `1bcaeeaa89763289e331f1723a304ec48e28bc851d45344ac486dce7c73b23f6` |

## Code

The desk's tick script reads its sources, scores and publishes in one run, so it never runs in a kit. code/support_score.py is the scoring step of that script and nothing else: support_tick.py lines 66 to 87, the counts, the product bootstrap and the all cell. The desk files it follows are under desk/, byte for byte, to read beside it. The scripts that run: code/support_score.py. Before every release the gate checks that this extract prints the number the desk published.

## Files

- kit.json: the steps, the output file and the headline fields.
- run.py: the command.
- expected.json and expected.sha256: the line run.py must print.
- published.json: the headline as the live feed served it when this kit was made.
- MANIFEST.json: every input and code file with its sha256.
- desk/: the desk scripts the extract follows, where the kit runs an extract.
- SHA256SUMS.txt: the sha256 of every file in this folder.
