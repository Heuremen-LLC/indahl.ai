# PKGLICENSE reproduce kit

Heuremen LLC · https://indahl.ai/pkglicense · https://indahl.ai/reproduce

This kit recomputes the PKGLICENSE headline number and its outcome label with the desk's own code (its scoring lines, copied as written), from what the kit holds, with its network proxies pointed at a closed port.

## The command

```
python3 run.py --check
```

Needs Python 3.9 or later and nothing else. It prints one line of JSON and checks it against expected.json. The line it must print has sha256 `46ab84f4bef32aaa4d529cf50cf780da6697bf1850dab424d7115153b5766933`.

## What it reproduces

The headline as the live feed https://indahl.ai/pkglicense/live.json served it at the feed stamp 10 Nov 21:45, read by us at 2026-11-11T00:08:48Z. The feed bytes had sha256 `b69f4ac5a377856795f48da2d0a3313fcce51dd486e8bd16eccec53217e3052f`.

- number: 7 of 704
- value: 0.0099
- interval: 0.0048 to 0.0204
- outcome: CONSISTENT

The live page can move inside the interval between releases. Each move outside it, or a change of label, gets a new row in our ledger, and a release is refused until this kit reproduces the number that row covers. The headline fields are the ones the ledger reads (`kit.json`, headline).

## Inputs

Not included. PyPI and GitHub metadata are under their terms of service and not an open licence, so this kit carries no copy of the source data. MANIFEST.json lists each input file the desk's scoring read, with its size, its sha256 and the time it was last written. We keep those exact files and rerun this kit on them before every release.

The input files are what the desk kept from its reads of the sources, with the time of each read where the desk records it. To check them, read the sources below again and compare. With a copy of the input files, `python3 run.py --check --inputs DIR` reruns the kit on them. A file whose sha256 differs from MANIFEST.json is named and the run stops. Sources change, so a later read can differ from ours.

- The top PyPI projects list of the list date in summary_pkglicense.json, https://hugovk.github.io/top-pypi-packages/top-pypi-packages.json
- For each project, https://pypi.org/pypi/PROJECT/json and the licenseInfo of its GitHub repository from the GitHub GraphQL API. Each row carries its read time.

## Sources and their terms

As the PKGLICENSE data pack lists them. Credit each source when you use its values.

- PyPI JSON API, https://docs.pypi.org/api/json/. PyPI terms of service.
- Top PyPI Packages, https://hugovk.github.io/top-pypi-packages/. Public list.
- GitHub GraphQL API licenseInfo, https://docs.github.com/en/graphql. GitHub terms of service.

## Input files

| File | Bytes | sha256 |
|---|---|---|
| data/projects.json | 184,496 | `c0bdf2755068f1754a8b62c0a76aace3e768f333ab38bc1bba907d70bf00e53f` |
| summary_pkglicense.json | 2,671 | `b69f4ac5a377856795f48da2d0a3313fcce51dd486e8bd16eccec53217e3052f` |
| pkginstall/data/projects.json | 158,673 | `509f97ec77b330f5516159aac883ef04fa64bd7c834d66c1c7224f815028d59f` |
| pkginstall/data/listdate.txt | 19 | `ce00e09e717676959017c3ccf380945489c8e20154f04283a3e6692ba0b6d399` |

## Code

The desk's tick script reads its sources, scores and publishes in one run, so it never runs in a kit. code/pkglicense_score.py is the scoring step of that script and nothing else: pkglicense_tick.py lines 97 to 102, the rows of the listed names, the counts and the disagree block. The desk files it follows are under desk/, byte for byte, to read beside it. The scripts that run: code/pkglicense_score.py. Before every release the gate checks that this extract prints the number the desk published.

## Files

- kit.json: the steps, the output file and the headline fields.
- run.py: the command.
- expected.json and expected.sha256: the line run.py must print.
- published.json: the headline as the live feed served it when this kit was made.
- MANIFEST.json: every input and code file with its sha256.
- desk/: the desk scripts the extract follows, where the kit runs an extract.
- SHA256SUMS.txt: the sha256 of every file in this folder.

## Note

The desk does not store the list of names it scored. The PKGINSTALL desk stores the same list of the same date with each rank, so this kit reads the names from there and stops if the two list dates differ.
