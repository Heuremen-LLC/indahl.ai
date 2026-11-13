---
license: cc-by-4.0
language:
- en
pretty_name: A Readout Is Not an Idle, data and verification code
tags:
- quantum-computing
- ibm-quantum
- superconducting-qubits
- reproducible-research
size_categories:
- 1K<n<10K
---

# A Readout Is Not an Idle: data and verification code

Data, plans, analysis code and outputs for "A Readout Is Not an Idle: Phase, Coherence and Entanglement Costs to Untouched Qubits on IBM Processors" (K. Indahl, Heuremen LLC). Every IBM run from 24 September to 23 October 2026 on seven IBM processors: one folder per run with its plan and SHA-256, circuits, analysis and synthetic tests, IBM calibration at firing, job IDs and committed outputs.

- `A_Readout_Is_Not_an_Idle_code_and_results_v5.zip` (10 MB): plans, code and committed outputs.
- `A_Readout_Is_Not_an_Idle_raw_v5.zip` (2.95 GB): the raw arrays (`.npz`) behind the figures.

Same files as version 5.0.0 of the Zenodo record, concept DOI https://doi.org/10.5281/zenodo.23169755. The paper, its LaTeX source and a reproducible build are at https://github.com/Heuremen-LLC/indahl.ai (folder `code/papers/a-readout-is-not-an-idle/`). The figure scripts there regenerate figures 1 to 4 pixel for pixel from the unpacked raw bundle: set `READOUT_EXPERIMENTS` to its `experiments/` folder.

SHA-256 of the code and results bundle: `2fa9cd0a215adf2ac214be435580b81a74469291d82cc096baea8cc7b22d6bc6`.

License: Creative Commons Attribution 4.0. Cite the paper and the Zenodo record.

Pages on indahl.ai: https://indahl.ai/qia (the Quantum Idle Audit) and https://indahl.ai/darkwave .
