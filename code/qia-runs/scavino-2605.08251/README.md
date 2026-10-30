# Ten-graph ZNE batch (arXiv 2605.08251) on ibm_fez, 25 October 2026

Everything behind the free calibration we sent to Vicenzo Scavino Alfaro.

## What ran

Your 10 QAOA MaxCut graphs (seeds 606 to 1506, n = 5, p = 1, gamma 0.8, beta 0.6) at noise scales 1 and 3, rebuilt from your published construction (rx/rz/cx, every gate folded G G^dag G at scale 3) without running your code. Transpiled once at optimization level 0 on physical qubits 0 to 4. Your runner left routing unseeded, so for each circuit we used the first seed from 24 to 83 that reproduces your published gate counts (all 20 matched; seeds per circuit in `job_lima.json`, `transpile_seeds`). 4000 shots per circuit, six jobs, each submitted after the previous one finished. IBM's record was saved before every job and after the last.

The plan was written for ibm_marrakesh. Marrakesh was in maintenance and two attempts there failed on IBM's side with no data. Two addenda, each committed before any job on its chip, moved it to ibm_kingston and then to ibm_fez (kingston's qubit 0 was reading wrong about 78% of the time in another job). Fez has the same coupling map. Nothing else changed. `GIT_LOG.txt` has every commit with its time.

## Jobs, in acquisition order

| Job | Circuits (graph seed x scale) | IBM job id | Created (UTC) | Running | Finished | QPU s |
|---|---|---|---|---|---|---|
| P1 | all 10 graphs, scales 1 and 3 interleaved (20) | dbemji0m94ac738s42eg | 02:30:32 | 02:30:33 | 02:31:00 | 23 |
| S1a | all 10 graphs, scale 1 | dbemjp8m94ac738s431g | 02:31:01 | 02:31:03 | 02:31:18 | 13 |
| S1b | all 10 graphs, scale 3 | dbemjtvpc3tc739m0bb0 | 02:31:19 | 02:31:20 | 02:31:37 | 13 |
| S2a | all 10 graphs, scale 3 | dbemk2ngdj9s73fm38lg | 02:31:38 | 02:31:40 | 02:31:56 | 13 |
| S2b | all 10 graphs, scale 1 | dbemk7fsstms73fcc8ng | 02:31:57 | 02:31:58 | 02:32:14 | 13 |
| P2 | all 10 graphs, scales 1 and 3 interleaved (20) | dbemkbvgdj9s73fm39pg | 02:32:15 | 02:32:16 | 02:32:47 | 23 |

Inside each job the graphs run in seed order 606, 707, 808, 909, 1001, 1102, 1203, 1304, 1405, 1506. `raw_lima_<job>.json` holds one entry per circuit with `graph_seed`, `scale` and `counts`, in submission order.

## Intervals and the shot-noise null (lima.py, fixed in the plan before any job)

- The statistic: mean of your MaxCut observable per graph from the counts, error |m - y_ideal|, MAE over the 10 graphs, Richardson ZNE = 1.5 m(1) - 0.5 m(3).
- Its own interval: each job's counts are resampled multinomially (2000 draws, same shots per circuit), the statistic is recomputed, the draws are re-centred on the observed value, and the 2.5 and 97.5 percentiles are printed.
- The shot-noise null: for each (graph, scale), the counts of every job holding it are pooled into one distribution. Each job is redrawn from that pooled distribution at its own shot count (2000 draws), so the jobs differ only by shot noise. The statistic's 2.5 to 97.5 percentile range over these draws is the null.
- Outcome: ABOVE if the observed value is above the null range, BELOW if below, CONSISTENT if inside. CANNOT_TELL if the null half-width exceeds your published gain 0.03635 (fixed from your number before any job).
- Seeds: numpy default_rng(24) for the analysis, default_rng(5) for the simulated worlds in synth_lima.py. Your graph edges come from default_rng(graph seed), as in your random_graph_edges.

## Files

- `PLAN_LIMA.md.text` with `PLAN_LIMA.sha256.text` and `CODE_LIMA.sha256.text`, then the addenda in commit order (`ADDENDUM_1_resubmit`, `ADDENDUM_REC_1`, `ADDENDUM_REC_2`, `ADDENDUM_HOLD_3`, `ADDENDUM_CHIP_KINGSTON`, `ADDENDUM_CHIP_FEZ`).
- `circuits_lima.qpy` (the 20 transpiled circuits, sha256 c6874575...), `job_lima.json`, `raw_lima_*.json`, `props_lima_before_*.json`, `props_lima_after.json`.
- `lima.py` (analysis), `fire_lima.py` (submission; `service()` opens our IBM account, use your own QiskitRuntimeService), `synth_lima.py` and `synth_results_lima.text` (simulated worlds run before any job), `known_good_lima.text` (your published numbers from your raw counts through our code: MAE 0.06445, 0.02810, 9 of 10), `dry_run_lima.text`, `fire_lima*.log`.
- `results_lima_fez.text`: every reading. `RESULT_LIMA_FEZ.md.text`: our note. `sent/`: the summary we emailed. `THEIRS_HASHES.txt`: hashes of your files as we downloaded them.

## Reproducing

Python 3.12.13, qiskit 2.5.2, qiskit-ibm-runtime 0.49.0, numpy 2.5.3, scipy 1.18.1. Put your Zenodo supplement (10.5281/zenodo.23405717) in a folder `theirs/` beside `lima.py`: `ibm_qaoa_heldout10_counts.csv` and the `raw/` folder of `*_seed_<s>_n5_r1_lambda_<l>_ibm_marrakesh_4000.json.gz` files. `python3 lima.py` checks your numbers (R0). `python3 lima.py --real` reads our six jobs and prints every reading.

Heuremen LLC
