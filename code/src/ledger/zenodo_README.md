# A Readout Is Not an Idle: Data and Verification Code (version 4.0.0)

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
- Raw readout files (`*.npz`) are in this record's second file, `A_Readout_Is_Not_an_Idle_raw_v4.zip`, in the same folders and under the same
  names the scripts read, including the per-shot files of the pairs, IQ, flip-check, reach and length runs. Synthetic test files are
  rebuilt by each folder's synth_*.py. The other runs are listed by IBM job ID in experiments/job-index/.

## Changes in this version (30 Oct 2026)
The paper: the Table III phase-kick row no longer carries the coherence-loss clause "excludes it on kingston only" (that clause belongs to the
coherence check in Sec. III D). Values written with a plus-minus are defined as one standard deviation and their kind is named. The final job-list
re-pull is dated 23 October (a 22 October pull missed 26 jobs). Data availability names the raw IQ files of the 21 October IQ run, which are in
this record. One quoted program output and one reference title are corrected, and the PDF carries its title. The method line below is limited to
the runs it describes. The raw readout file of the 23 October ibm_marrakesh fresh-record Hahn run is added to the raw zip. The other raw files are unchanged since version 5.

## Method in one line
In the 21 and 22 October runs every readout step is compared with an idle of exactly the published readout length, on the same qubits,
in the same job, circuits run twice per job, medians over qubits with 95 % bootstrap intervals (2000 resamples), four outcomes (ABOVE,
BELOW, CONSISTENT, CANNOT TELL). The 7 October copies are separate jobs with an idle within 0.24 % of the readout length on the 16-sample
grid. The Rigetti runs and the 2 to 11 October measured-qubit, decay and X-gate-train runs have no readout-against-idle arm. Selected shots
can bias the coherence loss upward, and excitation and leakage are not excluded as the whole cost on fez and kingston (paper, Sec. IV).

## License
CC BY 4.0 (Creative Commons Attribution 4.0 International).

Heuremen LLC
“We found it.”
