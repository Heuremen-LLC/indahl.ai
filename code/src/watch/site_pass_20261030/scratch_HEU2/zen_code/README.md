# A Readout Is Not an Idle: Data and Verification Code (version 5.0.0)

Data, plans, analysis code and outputs for "A Readout Is Not an Idle: Phase, Coherence and Entanglement Costs to Untouched Qubits on IBM
Processors" (K. Indahl). Covers every IBM run from 24 September to 23 October 2026 and the Rigetti runs of 25 September to 5 October.

## Contents
- `paper/`: the paper (PDF and LaTeX source), references, figures and figure scripts.
- `experiments/`: one folder per run, as served at https://heuremen.org/experiments/. Each holds the plan and its SHA-256 (pushed to a
  public server before the jobs where the page says so), circuits, analysis and synthetic-test scripts, IBM's calibration record saved at
  firing, job records with IBM job IDs, and the committed outputs (`results_*.text`). `2026-10-07-equal-idle/` holds the recomputation of
  the 7 October equal-idle runs and the inclusion rule for earlier runs (fixed before they were inventoried).
- `experiments/job-index/`: every IBM job on our accounts from 24 September to 22 October 2026 (546 jobs, re-pulled 23 October: ID, processor, creation time,
  status), with counts per day, and every Rigetti task of 25 September to 5 October (3035; account number removed). The 23 October Hahn T2 runs
  (kingston fresh record, boston) are in `experiments/2026-10-22-hahn-t2/` with their own job records.
- `experiments/2026-10-21-measurements/gate_trains/`: the raw IBM job files (13 jobs, 2 and 4 October) behind the paper's section on
  spaced X-gate trains, with verify_xtrain.py, which recomputes every number in that section.
- `extra/2026-10-11-three-box-sweep/`: nine ibm_fez three-box weak-measurement jobs of 11 October (probe strength 0.1 to 0.4), raw
  bits and the circuits read back from IBM. Not used in the paper; read in experiments/2026-10-22-three-box-run.
- `experiments/calibration-records/`: IBM's calibration records saved with the runs, the daily T1/T2 medians of six processors (15 September to
  6 October) and the per-qubit restamp check behind the record notes of the case statement QIA-2026-001.
- `experiments/2026-10-22-hahn-t2/`: Hahn-echo T2 against IBM's stated T2 (twelve runs, six processors), with per-qubit analyses.
- Raw readout files (`*.npz`) are in this record's second file, `A_Readout_Is_Not_an_Idle_raw_v5.zip`, in the same folders and under the same
  names the scripts read, including the per-shot files of the pairs, IQ, flip-check, reach and length runs. Synthetic test files are
  rebuilt by each folder's synth_*.py. Any other raw file is available on request.

## Method in one line
Every readout step is compared with an idle of exactly the published readout length, on the same qubits, in the same job; circuits run
twice per job; medians over qubits with 95 % bootstrap intervals (2000 resamples); four outcomes (ABOVE, BELOW, CONSISTENT, CANNOT TELL).

## License
CC BY 4.0 (Creative Commons Attribution 4.0 International).

Heuremen LLC
“We found it.”
