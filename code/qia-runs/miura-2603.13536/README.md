# AS-SQD (arXiv 2603.13536v1) on ibm_pittsburgh, 24 October 2026

Everything behind the free calibration we sent to Rinka Miura.

## What ran

Your hardware counts and settings are not released, so we used the construction your code releases (build_2.py, read as text and never executed): a Hadamard layer, then a Lie-Trotter step at t = 0.6 (2,400 shots) and t = 1.2 (600 shots), merged into one 3,000-shot sample, at n = 12, for 10 field instances (seeds 100 to 109; your main.py uses 100 to 104). Beside each Trotter pair, a control with the same Hadamard layer and straight to measurement, 3,000 shots. Two readout seat circuits (all 0, all 1, 1,000 shots each). 32 circuits, 62,000 shots, one job. The layout is the 12-qubit ring of pittsburgh with the lowest stated two-qubit plus readout error in the record pulled just before submission: physical 128, 129, 118, 109, 108, 107, 106, 105, 117, 125, 126, 127, so the periodic chain needs no SWAPs. Transpile seed 13536. Twirling and dynamical decoupling off. AS-SQD is our own implementation with your settings K = 50, B = 20, T = 10 (`src/assqd.py`).

| Job | IBM job id | Created (UTC) | Running | Finished | QPU s |
|---|---|---|---|---|---|
| 1 (planned, scored) | dbeecdvgdj9s73flkcn0 | 17:09:12 | 17:48:24 | 17:50:58 | 19 |
| 2 (duplicate, read as a copy) | dbeesuom94ac738rmbs0 | 17:44:27 | 17:48:24 | 17:51:21 | 19 |

Job 2 was a second submission of the same committed circuits after our log buffered and hid job 1. Addendum 2, committed before any counts were read, makes job 1 the scored job and job 2 a copy. `GIT_LOG.txt` has every commit with its time.

## Readings (src/readings.py, fixed in the plan before the job)

Per instance i: a_i = log10 |E_AS(Trotter sample) - E0|, r_i = mean over 5 expansion seeds of log10 |E_Random(Trotter sample) - E0|, c_i = log10 |E_AS(control sample) - E0|. E0 by exact diagonalisation. D1 = mean(a - r), D2 = mean(a - c). Interval: two-sided t(9) at 97.5% over the 10 instances. Outcome, the same rule for both: BELOW if the whole interval is below zero, ABOVE if above, CONSISTENT if it lies inside plus or minus M = 0.5 decade (a factor 3.2 in error), otherwise CANNOT_TELL. Random-expansion seeds are default_rng(instance x 100 + k), and the descriptive extras use default_rng(424242) and default_rng(9000 + 10 i + k).

## Files

- `PLAN_2603.13536.md.text` with its sha256 files, `ADDENDUM_1.md.text`, `ADDENDUM_2.md.text`.
- `circuits_2603.13536.qpy` (sha256 c2609257...), `job1_.../` and `job2_.../`: each job's raw counts (`raw_2603.13536.json`, one entry per circuit with kind, seed, t and counts), job record, IBM record before and after, readings and results. `failed_attempt1/`: the first attempt's log and record.
- `src/`: `circuits.py` (the circuits), `assqd.py` (the solver), `readings.py`, `analyze.py`, `fire.py`, `fetch_job1.py`, `known_good.py`, `synth.py`, `synth_fake_raw.py`.
- `known_good_2603.13536.text`: our Hamiltonian against the one your code builds (to 4e-15), and our solver's simulated errors. `synth_results_*.text`: simulated worlds run before the job, including a first attempt with a bug in D2 and a 5-instance attempt that showed D2 needed 10 instances.
- `RESULT_2603.13536.md.text`: our note. `sent/`: the summary we emailed. `THEIRS_HASHES.txt`: hashes of your files as we read them.

## Reproducing

Python 3.12.13, qiskit 2.5.2, qiskit-ibm-runtime 0.49.0, numpy 2.5.3, scipy 1.18.1. `python3 src/analyze.py job1_dbeecdvgdj9s73flkcn0` rewrites that folder's results from its raw counts in about 4 seconds. Nothing from your repository is needed to rerun the analysis.

Heuremen LLC
