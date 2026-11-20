# Data and code: A Readout's Kick Is a Turn

This repository holds the data and code cited by the paper *A Readout's Kick Is a Turn: Giving It Back, and How Long the Correction Lasts* (Heuremen LLC, 2026): [`code/readout-correction`](code/readout-correction).

Archived at [doi:10.5281/zenodo.23843468](https://doi.org/10.5281/zenodo.23843468).

## Checking the plan was fixed before the jobs

The paper cites the plan commit `0663d84`. That commit lives in our private archive, not in a public repository. To check the plan yourself, use the files here: `code/readout-correction/run/PREREG_HASHES.text` lists the sha256 of each plan file, and `PREREG_HASHES.text.ots` is its OpenTimestamps proof. Hash the files, compare them with the list, then verify the proof (`ots verify PREREG_HASHES.text.ots`).

Everything else from Heuremen LLC lives at:
- [indahl.ai](https://indahl.ai) and [github.com/indahl-ai/indahl.ai](https://github.com/indahl-ai/indahl.ai)
- [heuremen.org](https://heuremen.org) and [github.com/indahl-ai/heuremen.org](https://github.com/indahl-ai/heuremen.org)
- [quantumidleaudit.com](https://quantumidleaudit.com)
