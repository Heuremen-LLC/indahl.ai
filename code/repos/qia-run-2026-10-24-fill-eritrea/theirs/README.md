# Ablation-controlled benchmark of dynamic-circuit quantum teleportation on IBM Heron r2

This record accompanies our manuscript. It contains the raw measurement data, the
per-run device-calibration snapshots, the job metadata, the OpenQASM circuit
descriptions, and the analysis code with which we reproduce every quantitative
result in the paper. We deposit it so that our tables and figures can be
regenerated directly from the raw shot counts we collected on the IBM Quantum
processor `ibm_fez` (a 156-qubit Heron r2 device), with no IBM Quantum
credentials.

## Layout

```
teleportation-benchmark/
├── README.md
├── requirements.txt          pinned quantum deps + tested plotting deps
├── LICENSE                   MIT
├── circuits/                 OpenQASM for the three circuits (our Figure 1)
│   ├── full_protocol.qasm
│   ├── no_entanglement.qasm
│   └── no_feedforward.qasm
├── code/
│   ├── analysis.py           counts -> Bloch components, fidelity, SE, Bell, branches
│   ├── circuits.py           builds the three benchmark circuits
│   ├── make_all_tables.py    Tables 1-4, 6, S1, S2
│   ├── make_source_data.py   -> processed_data/source_data_full.csv, _branches.csv
│   ├── figure2.py / figure3.py / figure4.py
│   └── experiment/           data collection on hardware (your own token + CRN)
│       ├── run_experiment.py
│       └── setup_account.py
├── raw_data/
│   ├── raw_counts.json  branch_counts.json  bell_counts.json
│   ├── main_calibration.json  branch_calibration.json  bell_calibration.json
│   └── job_metadata.json     all three jobs: IDs, dates, layouts, calibration links
└── processed_data/
    ├── source_data_full.csv      per mode/angle components, fidelity, SE, shots
    ├── source_data_branches.csv  per angle/branch (X,Z) before and after correction
    └── table_values.csv          machine-readable dump of the exact table numbers
```

## What we measured

We benchmark three-qubit dynamic-circuit teleportation by single-qubit state
tomography of the teleported qubit, sweeping six input angles
(θ = 0, π/6, π/3, π/2, 2π/3, π) prepared by an `RY(θ)` rotation. We isolate the two
resources with two ablation controls: **no-entanglement** (omit the Bell pair, keep
feed-forward) and **no-feedforward** (keep the Bell pair, omit the conditional X/Z
corrections, which are conditioned on the q1 and q0 outcomes respectively).

## Data provenance

We ran the main sweep and the branch-resolved run on physical qubits [0, 1, 2] of
`ibm_fez`, and the Bell-pair check on [1, 2]. Every circuit used 8,192 shots at
optimization level 1. Each deposited run is accompanied by a backend-calibration
snapshot whose last-update timestamp preceded the corresponding recorded submission
time; `raw_data/job_metadata.json` lists all three job IDs, dates, layouts, and the
matching calibration file.

| Run | Job ID | Date | Calibration |
|---|---|---|---|
| Main sweep (54 circuits) | `d8ne35032u0s73fcb6sg` | 2026-06-14 | `main_calibration.json` |
| Branch-resolved (18) | `d8pa06i01fac73d1d560` | 2026-06-17 | `branch_calibration.json` |
| Bell resource (3) | `d8pa1cmkodhs7381h880` | 2026-06-17 | `bell_calibration.json` |

## Reproducing our results

No credentials are needed. From the `code/` folder:

```
pip install -r ../requirements.txt
python make_all_tables.py     # Tables 1-4, 6, S1, S2 (--fast skips the qiskit steps)
python make_source_data.py    # the processed-data CSVs
python figure2.py             # Figure 2
python figure3.py             # Figure 3
python figure4.py             # Figure 4
```

## What is exact, and what is not

We are explicit about which numbers are derived from the deposited data and which
are model or transpiler outputs:

- Tables 1, 2, 4, and Supplementary Tables S1 and S2 are exact: they come only from
  the counts, the calibration snapshot, and the metadata. Standard errors use the
  actual per-measurement shot count read from the counts, not an assumed 8,192.
- In Table 3, the ideal column is analytic and the hardware column is computed from
  `raw_counts.json`; both are exact and version-independent. The noise-model column
  is a device-informed simulation built from the errors in `main_calibration.json`.
  Average gate errors are passed straight into depolarizing channels, the sx error
  is reused for x, and the average readout error becomes a symmetric assignment
  matrix, so it is a rough consistency check rather than a calibrated backend
  model, and it is not fitted. It is a simulation and is not bit-reproducible:
  with the pinned Qiskit packages and tested plotting dependencies its values stay
  within about 0.005 of the manuscript's
  (Full 0.953, No-entanglement 0.752, No-feedforward 0.496), with small differences
  arising from simulator, transpiler, Python, NumPy and platform details.
- Table 6 lists representative transpiler metrics (gate counts and depth from a
  generic transpilation to the rz/sx/x/cz basis). The measurement, conditional-block
  and shot counts are exact; the depth and gate counts are not the exact `ibm_fez`
  compiled circuits.
- In Figure 4, the "after correction" panel is the branch-dependent Pauli correction
  applied in post-processing to the no-feedforward branch data. It is not a second
  hardware measurement.
- The 2/3 line in Figure 2 is the full-Bloch-sphere average classical bound; the
  six-state meridian ensemble we test is a different ensemble, so this line is a
  reference, not by itself a proof of advantage for the sampled states.

Table 5 is a literature comparison (Baur 2012, Steffen 2013, Kang 2025, this work).
It is not computed from data and is not generated here; it is the hand-written table
in the manuscript.

## Re-running on hardware (optional)

To collect fresh data you need your own IBM Quantum account (API token and instance
CRN from https://quantum.ibm.com). We ship no credentials; the scripts read them
only from the `IBM_QUANTUM_TOKEN` / `IBM_QUANTUM_CRN` environment variables, a
previously saved account, a hidden prompt, or `--token`/`--crn` flags.

```
export IBM_QUANTUM_TOKEN="<YOUR_TOKEN>"
export IBM_QUANTUM_CRN="<YOUR_INSTANCE_CRN>"
python code/experiment/setup_account.py     # optional: saves the account once
python code/experiment/run_experiment.py
```

Both scripts also accept `--token` and `--crn` flags, but a token typed on the
command line can be left behind in your shell history, so prefer the environment
variables above or the hidden prompt the scripts fall back to.

`run_experiment.py` runs all 54 main circuits plus the branch-resolved and Bell
circuits, and for each run it writes the counts together with a fresh provenance
bundle: the job ID, a UTC timestamp taken at submission, the backend, the
physical-qubit layout, a per-run backend-calibration snapshot retrieved after the
job completes (`main_calibration.json`, `branch_calibration.json`,
`bell_calibration.json`), and the installed package versions, collected into a new
`job_metadata.json`. Because calibration drifts, a fresh run produces new job IDs
and slightly different numbers from the deposited data, so do not mix them.

## Citation

Please cite the manuscript and this record.
