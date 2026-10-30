# DM-triangle circuits (arXiv 2609.15411v2) on ibm_kingston, 24 and 29 October 2026

Everything behind the free calibration we sent to Andrey Zhukov. Answers to his two questions are in CLARIFICATIONS.md.

## What ran

Your 76 circuits from Zenodo 10.5281/zenodo.23007728 (raw/003 controls and raw/005 chain-C circuits), loaded from your circuits.qpy as data and sent unchanged on your physical qubits, plus 10 circuits of ours on qubit 16 with a control on qubit 3. 1024 shots, init_qubits on, rep_delay 250 us, twirling off, dynamical decoupling off. Four jobs per night in A B B A order (A = your order then ours, B = A reversed). The same circuit file ran both nights (sha256 531953a6...). IBM's calibration record was saved before every job and after the last.

| Night | Job | IBM job id | Created (UTC) | Running | Finished | QPU s |
|---|---|---|---|---|---|---|
| 24 Oct | A1 | dbe5kkfpc3tc739l5efg | 07:12:17 | 07:12:18 | 07:12:53 | 26 |
| 24 Oct | B1 | dbe5ktngdj9s73fl8d9g | 07:12:54 | 07:12:56 | 07:13:28 | 26 |
| 24 Oct | B2 | dbe5l6nsstms73fbhf3g | 07:13:30 | 07:13:31 | 07:14:29 | 26 |
| 24 Oct | A2 | dbe5llnpc3tc739l5fqg | 07:14:30 | 07:14:32 | 07:15:05 | 26 |
| 29 Oct | A1 | dbht6imne4hc73bdj0gg | 23:14:18 | 23:14:37 | 23:15:33 | 26 |
| 29 Oct | B1 | dbht7642d77s739ddp4g | 23:15:36 | 23:15:37 | 23:16:09 | 26 |
| 29 Oct | B2 | dbht7etep8hs73amrfog | 23:16:12 | 23:16:13 | 23:16:45 | 26 |
| 29 Oct | A2 | dbht7no1h92s7382elkg | 23:16:47 | 23:16:48 | 23:17:21 | 26 |

## Files, per night (24oct/, 29oct/)

- `PLAN_*.md.text`: the plan, committed before the first job. `GIT_LOG.txt` gives the commit times. `PLAN_*.sha256.text` and `CODE_*.sha256.text` hash the plan and code as committed.
- `circuits_zhukov.qpy`: the 86 circuits as submitted. `job_zhukov.json`: job ids, the circuit-to-position map (`set_ids`, in submission order for job A), your qpy hashes, timestamps, QPU seconds.
- `raw_zhukov_<job>.npz`: every shot, decoded to 3-bit codes per lane (code = x1<<2 | x2<<1 | x3, x1 = path[0]). 24oct/src_signcheck/ holds the BitArrays and get_counts() output for chain C, re-fetched from the jobs, with the check that both decode paths agree.
- `props_zhukov_before_<job>.json`, `props_zhukov_after.json`: IBM's calibration record before every job and after the last.
- `zhukov.py` (analysis), `fire_zhukov.py` (submission), `synth_zhukov.py` and `synth_results_*.text` (simulated worlds run before any job, including a first attempt that failed three checks), `known_good_zhukov.text` (your published numbers recovered from your data through our code before reading ours), `dry_run_zhukov.text`, `fire_zhukov.log`.
- `results_zhukov.text` (24 Oct) and `results_zhukov_r2.text` (29 Oct): every reading. `RESULT_ZHUKOV.md.text` and `SIGNCHECK_ZHUKOV.md.text`: our notes on 24 October, including the chain-C sign check.
- 29oct/ only: `date_reading.py`, `readings_date.json`, `results_date.text` (the three-date comparison), `date_floor.py`, `synth_date_floor.text` (simulated nights).
- `sent/`: the summary we emailed. `THEIRS_HASHES.txt`: the hashes of your files as we downloaded them.

## Reproducing

Python 3.12.13, qiskit 2.5.2, qiskit-ibm-runtime 0.49.0, numpy 2.5.3, scipy 1.18.1. The analysis reads your files from a folder `theirs/` beside `zhukov.py`, renamed from your IBM_Data_v2.0 archive: `raw/00N/shots_codes.npz` as `codes_00N.npz`, `raw/00N/counts.json` as `counts_00N.json`, `raw/00N/manifest.json` as `manifest_00N.json`, `raw/00N/job_metrics.json` as `job_metrics_00N.json`, for N = 3, 4, 5. Your MANIFEST_SHA256.json gives the hashes. Then `python3 zhukov.py --real` in each night's folder. `29oct/date_reading.py` reads the 24 October shots from the path on its line 7, which is our working folder; point it at `../24oct`. The C_MIN bootstrap uses numpy default_rng(11). Nothing else is random.

Heuremen LLC
