# HPT reproduce kit

Heuremen LLC · https://indahl.ai/hpt · https://indahl.ai/reproduce

This kit recomputes the HPT headline number and its outcome label with the desk's own code (its scoring lines, copied as written), from what the kit holds, with its network proxies pointed at a closed port.

## The command

```
python3 run.py --check
```

Needs Python 3.9 or later and nothing else. It prints one line of JSON and checks it against expected.json. The line it must print has sha256 `dac673f0c2d2251f1f72fbd267e6dd77d98bf8effd0ae09d0deb6bf704e77b56`.

## What it reproduces

The headline as the live feed https://indahl.ai/hpt/live.json served it at the feed stamp 09 Nov 02:11, read by us at 2026-11-10T23:47:01Z. The feed bytes had sha256 `6608dc006ccd67be259e16d590dbde1762f60c4b7d1341f99ca2702d5670c46d`.

- number: 12 of 506
- value: 0.0237
- interval: 0.0136 to 0.041
- outcome: CONSISTENT

The live page can move inside the interval between releases. Each move outside it, or a change of label, gets a new row in our ledger, and a release is refused until this kit reproduces the number that row covers. The headline fields are the ones the ledger reads (`kit.json`, headline).

## Inputs

The exact files the desk's scoring read, stored gzip-compressed under inputs/. run.py checks the sha256 of each one before it runs.

## Sources and their terms

As the HPT data pack lists them. Credit each source when you use its values.

- Hospital cms-hpt.txt files under the CMS price transparency rule, https://www.cms.gov/priorities/key-initiatives/hospital-price-transparency. Public files published under a federal rule, presence and header facts only.
- Wikidata (US hospitals with official websites), https://query.wikidata.org/. CC0 1.0.

## Input files

| File | Bytes | sha256 |
|---|---|---|
| data/domains.json | 445,357 | `c7c27d1c1f16b9971925a7b96897f0036b21fdde9c2ea0ba76a0ce9b19bb76db` |
| summary_hpt.json | 5,812 | `6608dc006ccd67be259e16d590dbde1762f60c4b7d1341f99ca2702d5670c46d` |

## Code

The desk's tick script reads its sources, scores and publishes in one run, so it never runs in a kit. code/hpt_score.py is the scoring step of that script and nothing else: hpt_tick.py lines 121 to 124 and 128, the grp function and the comparison block. The desk files it follows are under desk/, byte for byte, to read beside it. The scripts that run: code/hpt_score.py. Before every release the gate checks that this extract prints the number the desk published.

## Files

- kit.json: the steps, the output file and the headline fields.
- run.py: the command.
- expected.json and expected.sha256: the line run.py must print.
- published.json: the headline as the live feed served it when this kit was made.
- MANIFEST.json: every input and code file with its sha256.
- desk/: the desk scripts the extract follows, where the kit runs an extract.
- SHA256SUMS.txt: the sha256 of every file in this folder.

## Note

The outcome needs the desk's own live gate to have passed on the run. That gate cannot be replayed, so the kit reads its result from summary_hpt.json, the summary that run wrote.
