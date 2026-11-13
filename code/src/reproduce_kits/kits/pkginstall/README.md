# PKGINSTALL reproduce kit

Heuremen LLC · https://indahl.ai/pkginstall · https://indahl.ai/reproduce

This kit recomputes the PKGINSTALL headline number and its outcome label with the desk's own code (its scoring lines, copied as written), from what the kit holds, with its network proxies pointed at a closed port.

## The command

```
python3 run.py --check
```

Needs Python 3.9 or later and nothing else. It prints one line of JSON and checks it against expected.json. The line it must print has sha256 `50cd23a1327ebbdd6bf56db81e4b2200c5bb37460a70de0ef4d75659518d6baa`.

## What it reproduces

The headline as the live feed https://indahl.ai/pkginstall/live.json served it at the feed stamp 12 Nov 14:40, read by us at 2026-11-12T16:06:22Z. The feed bytes had sha256 `4565f5836a271baba26ecf2c5c140ccd8d14b64c59a078a5eb4b7ade04e09bc0`.

- number: 522 of 523
- value: 0.0019
- interval: 0.0003 to 0.0108
- outcome: CONSISTENT

The live page can move inside the interval between releases. Each move outside it, or a change of label, gets a new row in our ledger, and a release is refused until this kit reproduces the number that row covers. The headline fields are the ones the ledger reads (`kit.json`, headline).

## Inputs

Not included. PyPI metadata is under the PyPI terms of service and not an open licence, so this kit carries no copy of the source data. MANIFEST.json lists each input file the desk's scoring read, with its size, its sha256 and the time it was last written. We keep those exact files and rerun this kit on them before every release.

The input files are what the desk kept from its reads of the sources, with the time of each read where the desk records it. To check them, read the sources below again and compare. With a copy of the input files, `python3 run.py --check --inputs DIR` reruns the kit on them. A file whose sha256 differs from MANIFEST.json is named and the run stops. Sources change, so a later read can differ from ours.

- The top PyPI projects list of the date in data/listdate.txt, https://hugovk.github.io/top-pypi-packages/top-pypi-packages.json
- For each project, https://pypi.org/pypi/PROJECT/json, and pip install --dry-run of the command its description gives. Each row carries its read time.

## Sources and their terms

As the PKGINSTALL data pack lists them. Credit each source when you use its values.

- PyPI JSON API, https://docs.pypi.org/api/json/. PyPI terms of service.
- Top PyPI Packages, https://hugovk.github.io/top-pypi-packages/. Public list.

## Input files

| File | Bytes | sha256 |
|---|---|---|
| data/projects.json | 157,673 | `69c1fd56b2a43d721258baee7adb19233dee709a91204380fef071a0ba248bbe` |
| data/listdate.txt | 19 | `ce00e09e717676959017c3ccf380945489c8e20154f04283a3e6692ba0b6d399` |
| summary_pkginstall.json | 1,172 | `da4867f008603169a9a3d0aaa4d8a6b30289b07197ea4a85e3665047405b60c2` |

## Code

The desk's tick script reads its sources, scores and publishes in one run, so it never runs in a kit. code/pkginstall_score.py is the scoring step of that script and nothing else: pkginstall_tick.py lines 112 to 116, the counts, the interval and the comparison block. The desk files it follows are under desk/, byte for byte, to read beside it. The scripts that run: code/pkginstall_score.py. Before every release the gate checks that this extract prints the number the desk published.

## Files

- kit.json: the steps, the output file and the headline fields.
- run.py: the command.
- expected.json and expected.sha256: the line run.py must print.
- published.json: the headline as the live feed served it when this kit was made.
- MANIFEST.json: every input and code file with its sha256.
- desk/: the desk scripts the extract follows, where the kit runs an extract.
- SHA256SUMS.txt: the sha256 of every file in this folder.

## Note

This kit recounts the class pip gave each command when the desk read it. pip resolves against the live PyPI index, which cannot be replayed, so those classes are inputs here.
