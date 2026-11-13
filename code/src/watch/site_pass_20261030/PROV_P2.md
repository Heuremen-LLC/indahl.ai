# QIA provenance pass, lane P2 (28 rows, one or two numbers not found), 30 Oct 2026

Read only. Every number in each row's measured and qia_calibration cells was checked, not only the listed missing ones. Verdicts: 23 KEEP, 3 FIX, 2 PULL (28 rows).

Verdict key: KEEP = every number traced, recomputed or recounted and matching. FIX = a number is off or needs rewording (right figure given). PULL = a number cannot be traced, recomputed or recounted from surviving files or the authors' public data.

## Summary

| row id | verdict | why in one line |
|---|---|---|
| free_2409.02575 | KEEP | 1.90e-2 recounted from released data (1.897e-2); 5 repetitions confirmed by README and data; 6/2/2 counts not recoverable from a kept list, see row |
| bayer_qcnn | KEEP | 93.36 and 10.57 printed in paper; 93.3 recounted (2-parameter logistic regression on mean pixel intensity, 1,974/2,115) |
| bluequbit_rcs | PULL | 1.19 and 0.77 cannot be traced (source deleted); all other numbers traced |
| cleveland_thermolysin | FIX | -2.55 versus the 2.54 the text prints; timings recounted from Fig. 5 |
| cleveland_msu | KEEP | 47.7 recomputed from Table 1 energies |
| recount_2411.15536 | KEEP | 0.625 and 22.86 recomputed; classical value cannot be below 10/16 |
| deloitte_fireopal | FIX | eight-bar mean re-digitised is 36.3, cell says 36.4 (use "about 36") |
| eon_hhl | KEEP | all four errors recomputed from Table 1 |
| hsbc_rfq | KEEP | 54 = 0.97/0.63 - 1, in kept output |
| ibm_flagship_sampling | KEEP | all numbers in kept AUDIT.md and recompute_output.txt |
| kipu_bfdcqo | KEEP | 12 of 14, 0.126 and 0.215 recomputed from the paper's own parameters |
| kipu_dcqs | PULL | 6.4 s and 9.7 s not in any kept file; kept record says 0.07-0.87 s at 67-91 M/s |
| qunova_nh3 | KEEP | 1.66 mHa recounted (top-5,000 amplitude selection 1.664, CIPSI-type 1.60); SHCI points read from Fig. 4; 2.80 traced |
| free_2501.04649 | KEEP | 100,000 shots per circuit recounted from released counts; 1.0e6 / 1.2e6 per experiment |
| free_2607.09368 | KEEP | z values recomputed from printed means and SDs |
| recount_10.5281/zenodo.21960772 | FIX | alpha x pi^2/4 is 0.0180055, not 0.0180056; gap 127.1 not 127.07 (finding unchanged) |
| recount_2511.14821 | KEEP | Table VII means recomputed |
| recount_10.5281/zenodo.22848316 | KEEP | 10.1 degrees and p 0.0078 recomputed |
| recount_10.5281/zenodo.20352903 | KEEP | 0.00061 recomputed |
| fill_2602.20614 | KEEP | RB factors and 95% bootstrap traced to kept sweep_run files |
| recount_10.5281/zenodo.21682087 | KEEP | 500 us = 125,000 x 4 ns, dt in kept job file |
| recount_10.5281/zenodo.21479684 | KEEP | 0.0078 and 0.13 sigma recomputed |
| recount_10.5281/zenodo.22050177 | KEEP | 54.5 sigma recomputed |
| free_2508.10593 | KEEP | -65.05331 and all other Table VII sums recomputed |
| free_2510.08719 | KEEP | 2.0x and 5.0x recomputed |
| free_2603.16973 | KEEP | 0/28 fit 1/153, 24/28 fit 1/156, 4/4 PL-Real fit 1/38 |
| k2025_tara_2512.04016 | KEEP | S 2.679 recounted from our raw counts; 2.732 recounted from their CSV |
| recount_2512.14513 | KEEP | 47/1.18 = 39.8 |

## Detail


Paths: BF = /Users/heuremen/bones-forge. SP = /private/tmp/claude-501/-Users-heuremen/80087010-0cb3-4ae5-9e13-362e6d5086ad/scratchpad/p2 (my scratch; scripts and downloads are there). Paper text = BF/qia_leads/recheck_published/src/<id>.txt unless another path is given (read with grep -a, some files contain binary bytes).


### free_2409.02575 - KEEP (one caveat on the 6/2/2 counts)
- 5 repetitions released: RECOUNTED. Zenodo 10.5281/zenodo.15147087 (data.zip, saved SP/z15147087). The dataset README says bias_reduction/data.json holds "each of the 5 repetitions" and the file has dataset_0 to dataset_4. The paper says the experiment was repeated 10 times (paper text L237, L256, L272).
- 1.90e-2 (no-QDT error on the released data): RECOUNTED. Script SP/recount_2409.py (qvenv python, data read only). Estimator: the ideal locally-biased Pauli-6 effects from the dataset's own hdf5 file (scaling_experiments/povm_effects_8q_lbcs.hdf5; the per-qubit biases match the outcome frequencies in data.json to 0.003), 361-term S0 8-qubit Hamiltonian from hamiltonians/S0_hamiltonian_8q.json, 70,000 settings x 100 shots per repetition. Absolute errors against the true energy -1702.1928357500 (which I confirmed independently: it equals the energy of the computational basis state 11001100 from the Hamiltonian's Z terms): 1.770e-2, 1.992e-2, 1.878e-2, 2.132e-2, 1.715e-2; mean over the 5 released repetitions 1.897e-2 = 1.90e-2. The paper prints 3.83e-2 as the average over 10 repetitions (text L252); none of the five released repetitions is near it.
- 6 reproduce, 2 do not, 2 cannot tell: the original ten-item list was in qia_leads/free_index_20261024/FREE_INDEX_RESULTS.jsonl, deleted 25 Oct, and I found no copy. I rebuilt a ten-item list from the numbers the paper prints in its bias-reduction section, with my own recount of each. Reproduce (6): 7e4 settings, 100 shots per setting, 7e6 shots per repetition, 111,200 = 278 jobs x 4 x 100 shots per QDT circuit (paper "1.11e5", text L242-244), 12 circuits x 111,200 = 1.334e6 QDT shots (paper "1.33e6"), 278 jobs (implied by the same product). Do not reproduce (2): 10 repetitions (5 released); no-QDT error 3.83e-2 (1.90e-2). Cannot tell (2): with-QDT error 2.72e-3 and QDT standard error 1.75e-3, because only 5 of 10 repetitions are released. My QDT recount (SP/recount_2409_qdt.py) gives with-QDT errors 1.84e-3, 4.29e-3, 3.11e-3, 6.48e-3, 1.08e-3, mean 3.36e-3 (spread consistent with 2.72e-3 at 5 repetitions); standard error from per-setting estimates 1.31e-3 against the paper's 1.75e-3, whose Eq. (6) variance I did not implement. The QDT qubit order matters: reading the QDT bitstrings left to right in the same order as the outcome strings gives the 3.36e-3; reversed gives 9.9e-3 (the "document the QDT qubit order" item). This rebuilt list gives exactly 6/2/2, but I cannot show it is the original list; the cell would be safer naming the ten items or dropping the counts.

### bayer_qcnn - KEEP
- 93.36 +- 10.57 (CNN, 22 parameters): TRACED, paper text BF/qia_leads/recheck_published/src/bayer_qcnn.txt L1693 (Table 5) and L934 ("93.4% ... 10.6% standard deviation").
- 71.74 and 96.08: TRACED, same file L37-38, L1028-1029.
- 93.3 (2-parameter model): RECOUNTED. SP/bayer/lr2.py on the kept MNIST file BF/qia_leads/audits/qml/data/mnist.npz (sha256 prefix 731c5ac602752760, the one AUDIT.md names). Logistic regression with weight and bias on mean pixel intensity, MNIST 0-vs-1 test set (2,115 images): 1,974/2,115 = 93.33%. A threshold on the same feature gives the same 0.93333. Caveat: the kept files never define the 2-parameter model, so the cell should name it ("logistic regression on mean pixel intensity").

### bluequbit_rcs - PULL (1.19 and 0.77 only; everything else traced)
- 91-115 Frontier-years: TRACED, BF/qia_leads/audits/bluequbit_rcs/bones_rerun.txt L26-30 (91.4, 99.4, 111.4, 115.3).
- "four estimators": TRACED, same lines (3-patch, 4-patch, mirror point, mirror fit).
- 2.01e-3: TRACED, same file L31 (2.012e-03); AUDIT.md L27.
- 0.137 and 0.872: RECOMPUTED, paper (BF/qia_leads/audits/bluequbit_rcs/src/paper.txt L146, L705): 0.872 per cycle; -ln(0.872) = 0.1371, and 0.0596 x ln 10 = 0.1372.
- 1.19 and 0.77: NOT FOUND. Their source file (qia_leads/reverse_lookup/out/p1_bluequbit_bracket.txt) was deleted on 25 Oct and no copy survives. The inputs do survive (phoenix RB, BF/arxiv_one_readout/sweep_run/results_sweep_ibm_phoenix.text L7-8: SX 1.931 [1.741, 2.027], CZ 1.257 [1.203, 1.324], readout CONSISTENT; stated errors BF/arxiv_one_readout/sweep_run/props_sweep_ibm_phoenix.json; the paper gives 25.5 CZ per cycle, 61 qubits, and its own log-F model), but the script that turned them into 1.19 and 0.77 is gone. My simple reconstructions give measured/predicted of about 1.4 to 1.9 for stated figures; a 128-way search over conversion factors finds one combination near (1.18, 0.77), which is a fit and not a trace. Cannot be shown from kept files. To keep the row: write the bracket as a kept script from the inputs above and replace the figures with its output.

### cleveland_thermolysin - FIX (minor)
- 2400 min: TRACED, BF/qia_leads/audits/cleveland_thermolysin/AUDIT.md L14, L19; bones_rerun.txt L6-7; paper text L841 (SI sentence). 50 x 4 x 6 x 2 = 2,400.
- 1e-5 cutoff: TRACED, AUDIT.md L14 (Fig. 5 caption).
- 1.1e4 s and 4.4e3 s: RECOUNTED from the authors' Figure 5 (https://arxiv.org/html/2604.09857v2/fig5.png, saved SP/thermo/fig5.png). Pixel read on the log axis: SQD dashed line 1.07e4 s, HCI 8 CPU at 1e-5 4.40e3 s. The cell's "about 1.1e4" and "4.4e3" match.
- about 2.5x: 1.1e4 / 4.4e3 = 2.5 (cell arithmetic); the figure read gives 2.44. Matches within reading error.
- -2.55 kcal/mol: the paper's text prints a deviation of 2.54 kcal/mol (paper text L106, AUDIT.md L7). Figure 6 labels (SP/thermo/fig6.png) are experimental 4.10 and LUCJ-SQD-extSQD 1.55, so 1.55 - 4.10 = -2.55. FIX: write "the 2.54 kcal/mol deviation printed in the text (Fig. 6 labels give 4.10 and 1.55)" or use 2.54 as AUDIT.md does. The two values differ only by rounding, but the sign and value as written are not what the text prints.

### cleveland_msu - KEEP
- 47.7: RECOMPUTED. Table 1 energies (paper BF/qia_leads/audits/chemistry/src/2512.17130.txt L1067-1073): (7354.1413 - 7354.0653) x 627.5095 = 47.69 kcal/mol (also printed as 47.70 for the CCSD row). AUDIT.md L60.
- 59.61: TRACED, same file L1052 (text) and L1069 (Table 1 MP2 row, whose energy cells are identical to the CCSD row).

### recount_2411.15536 - KEEP
- 0.8535 = cos^2(pi/8): RECOMPUTED, cos^2(pi/8) = 0.853553 (SP/g2411/chsh4.py); paper prints 0.8535 (paper text L214, L230).
- 6.25 (W game): printed quantum 0.7499, classical 0.6875, gap 6.25% (paper text L238-239, L253-254); 0.75 - 0.6875 = 0.0625.
- 0.625: RECOMPUTED. SP/g2411/chsh4.py checks all 65,536 four-variable Boolean functions: for a parity-winning game the best classical strategy wins at least 10/16 = 0.625 on every one (equality for bent functions). The paper prints 0.6225 (text L217, L230, L281, L335, L450), which is not a multiple of 1/16 and is below the minimum; the same paper prints classical 0.625 in its critical-state tables (L284-285). Note: my brute force of the plain algebraic form of Eq. (9) gives 11/16, because the overlines in the paper's equation were lost in the text extraction; the 10/16 bound does not depend on that.
- 22.86: RECOMPUTED, 0.853553 - 0.625 = 0.228553 = 22.86 percentage points (printed gap 22.5 at text L8, L207, L231, L503; neither 0.6225 nor 0.625 gives 22.5).

### deloitte_fireopal - FIX (36.4 should be 36.3, or say "about 36")
- 36.4: RECOUNTED. I re-extracted Fig. 3 from the arXiv PDF (https://arxiv.org/pdf/2406.09341, image on page 3, SP/deloitte/img_p3_Im3.png) and ran the kept digitiser (BF/qia_leads/audits/deloitte_fireopal/digitize_fig3.py, copied to SP/deloitte/fresh) on it. Eight per-bar improvements 29.8, 36.9, 47.4, 45.0, 42.9, 20.3, 34.5, 33.8; mean of the eight = 36.30. The 36.4 in AUDIT.md L34 is the mean of the two rounded sub-means (39.8 and 32.9 gives 36.35). Per-bar KL values are read off a figure (+-0.01 KL), so one decimal is over-precise: use "about 36%" as the calibration cell already does.
- 20-47% per circuit: TRACED/RECOUNTED, per-bar min 20.3, max 47.4 (check_fig3_output.txt L1-2; same in the fresh re-extraction).
- ~36% (calibration cell): matches 36.30.

### eon_hhl - KEEP
- 34 and 39 (R off): RECOMPUTED from Table 1 (paper BF/qia_leads/audits/eon_hhl/src/paper.txt L332-335: true 0.064, noiseless 0.042, IBM 0.089): 0.022/0.064 = 34.4%, 0.025/0.064 = 39.06%. Also check_hhl_output.txt L1.
- 130 and 113 (L off): RECOMPUTED (true 2.64e-5, noiseless 6.07e-5, IBM 5.63e-5): 129.9% and 113.26% (paper prints 113.28 for IBM); check_hhl_output.txt L2.
- 32x32 classical solve "microseconds": TRACED, check_hhl_output.txt section C: 9.5 microseconds per evaluation; 32 x 32 from paper L299.

### hsbc_rfq - KEEP
- 0.97 and 0.63: TRACED, paper text BF/qia_leads/audits/hsbc_rfq/src/paper.txt L352, L366, L386 (0.63 +- 0.03, 0.97 +- 0.02).
- +34 points: 97 - 63 = 34; check_hsbc_output.txt row "All" (table diff +34).
- 54: RECOMPUTED, 0.97/0.63 - 1 = 53.97%; check_hsbc_output.txt row "All", ratio_gain 54.0.

### ibm_flagship_sampling - KEEP
- 0.384: TRACED, BF/qia_leads/audits/ibm_flagship_2607_25941/outputs/recompute_output.txt L4 (F_raw = 1 - 2 x 0.30786 = 0.3843, from the released fig4_data.pkl); AUDIT.md L44, L56.
- 0.26 and 0.038% (README, 70x70): TRACED, AUDIT.md L18 (README quoted verbatim), L6.
- 0.32 and 0.0590% (paper v1): TRACED, AUDIT.md L19, L21-22.
- 250,000 (num_shots field) and 125,000 per basis: TRACED, AUDIT.md L45 and recompute_output.txt L7-8, L13 (5 M shots / 40 bases = 125,000).

### kipu_bfdcqo - KEEP
- 12 of 14: RECOUNTED from BF/qia_leads/audits/kipu_bfdcqo/src/tables_raw.json t2: BF-DCQO energy worse than SA-10000 in 12, equal 0, better 2. Also bones_recount_table2.text L1.
- 48 cores: TRACED, AUDIT.md L13, L21 (paper Table 1 and Sec. I). 1e-4 s per shot: paper src/kipu.txt L154.
- 4 s (SA) and 0.506 s (BF-DCQO): printed (src/kipu.txt L172). 7,000 sweeps x 100 runs x 0.6e-5 = 4.2 s; BF-DCQO (500 x 100 + 100 x 1 x 10) x 0.6e-5 + 2,000 x 1e-4 = 0.306 + 0.2 = 0.506 s, so the parameters (L171, L163) reproduce their time.
- 0.126: RECOMPUTED, 7,000 sweeps x ceil(100/48) = 3 rounds x 0.6e-5 = 0.126 s.
- 0.215: RECOMPUTED, same convention on the pre-processing term: (500 x 3 + 100 x 1 x 10) x 0.6e-5 = 0.015 s, plus 0.2 s QPU = 0.215 s.
- 6 s (SA, n_sweep 10000, 100 reads): 10,000 x 100 x 0.6e-5 = 6.0 s (src/kipu.txt L160).

### kipu_dcqs - PULL (6.4 s and 9.7 s; about 90 M/s needs rewording)
- 8.7 M attempts/s: TRACED, AUDIT.md L9-10 (paper Sec. III.2.2, App. D.3: 12-thread rate divided by 12).
- about 90 M/s: kept record says 67-91 M/s (AUDIT.md L34; BF/qia_leads/audits/kipu_dcqs/summary_table.txt rows 66.9-81.3 M/s per instance). 90 is the top of the range; the median is near 78.
- 6.4 s and 9.7 s: NOT FOUND. Not in the paper (grep), AUDIT.md, summary_table.txt, check_dcqs_output.txt, pt_throughput_output.txt, or any kept dir. The kept record gives 0.07-0.87 s (median/max over 8 seeds, three instances, 67-91 M/s; AUDIT.md L35, L38, L45; summary_table.txt). 6.4 s at 90 M/s would be 576 M updates, 11,500 times the 50,000 DCQS samples, far outside the 91x-1,372x kept.
- FIX available from kept files: "a single-core parallel tempering at 67-91 M attempts/s reached the converged ln Z in 0.07-0.87 s on three instances of the same class" (AUDIT.md L38).

### qunova_nh3 - KEEP
- 2.80 mHa at 19,881 determinants (HI-VQE): TRACED, BF/qia_leads/audits/qunova_nh3/check_nh3_output.txt ("HI-VQE m=2e4 ... err=2.797 mHa ... dets=19,881"); paper Table 2 energies in AUDIT.md L9.
- 0.0002 mHa (SHCI): TRACED, AUDIT.md L12; Table 2 energies in AUDIT.md L9 differ by 1.8e-7 Ha = 0.00018 mHa.
- about 0.01 mHa (SHCI): RECOUNTED from the authors' Figure 4 (https://arxiv.org/html/2503.06292v2/Figures/NH3-30qubit-energy-dff.png, saved SP/qun/fig4.png). Two SHCI points only. Pixel read on the log axis: 1.20e-5 Ha = 0.012 mHa at about 4e5 determinants, and 1.76e-7 Ha = 0.00018 mHa. The cell's "0.0002 and about 0.01" match.
- 1.66 mHa at 5,000 determinants: RECOUNTED. SP/nh3/cipsi2.py (pyscf 2.14; geometry and basis taken from the kept BF/qia_leads/audits/qunova_nh3/check_nh3_sweep.py; the full CI energy I get, -56.29236296 Ha, equals the kept value in check_nh3_output.txt). Taking the 5,000 determinants with the largest full-CI amplitude and re-diagonalising gives E - E_FCI = 1.6643 mHa, which is the cell's 1.66. A PT2-ranked (CIPSI-type) growth to 5,000 determinants gives 1.5961 mHa (3,200: 2.258; 1,600: 3.702). So "a determinant-wise selection reaches about 1.6-1.7 mHa at 5,000 determinants" holds under both; the 1.66 is the amplitude-ranked one. Geometry is assumed (the paper gives none), as the cell says. Note that a selector that needs the exact full-CI vector to rank is a bound, not a method; the CIPSI-type figure is the usable one.
- 1.6 mHa threshold and 5,000: paper Fig. 5 caption "<1.6 mHa" (BF/qia_leads/audits/qunova_nh3/src/paper.txt L219); 5,000 is the determinant count above.

### free_2501.04649 - KEEP
- 100,000 shots per circuit: RECOUNTED. Zenodo 10.5281/zenodo.15395335 (concept DOI, resolves to record 15846899, Dataset.zip, saved SP/z15846899). I decoded ibm_data/counts_*.json (qiskit RuntimeEncoder format: base64 + zlib + .npy, loaded with allow_pickle=False, script SP/z15846899/shots2.py). All 7 files, every register of every circuit: 100,000 shots.
- 10^6 for L=9 and 1.2e6 for L=11, 13, 15: L=9 has 10 circuits (10 x 100,000 = 1.0e6); each of L=11, 13, 15 has 12 circuits in two files of 6 (12 x 100,000 = 1.2e6). The paper says "a total of 10^6 shots" for Fig. 9 (paper text L1275); the dataset README says 10^6 shots per run.

### free_2607.09368 - KEEP
- All means and SDs: printed in Table II (paper text L552-561). ER-10 ND-A vs Standard 0.990 (+-0.008) vs 0.981 (+-0.012); ER-20 0.992 (+-0.010) vs 0.994 (+-0.009); RG-3 0.996 (+-0.004) vs 0.991 (+-0.005). AR at iteration 10: 0.983/0.968, 0.990/0.987, 0.994/0.991 (same lines).
- Differences and z (n = 10 instances per class, paper L443, L493): RECOMPUTED, SE = sqrt(s1^2/10 + s2^2/10): ER-10 +0.009, z +1.97; ER-20 -0.002 (the 0.002), z -0.47; RG-3 +0.005, z +2.47 (the 2.5). The cell's +2.0, -0.5, +2.5 match.

### recount_10.5281/zenodo.21960772 - FIX (minor, 7th digit)
- 127.07 and 0.0180056: the paper prints theory 0.01800555 and plateau 0.01813262 (paper text L56-58, L219-226). 0.01813262 - 0.01800555 = 127.07 microrad exactly as printed. But alpha x pi^2/4 with alpha = 1/137.036 is 0.0180055 (0.01800550; with 0.00729735 it is 0.01800549, so the paper's printed "0.00729735 x 2.4674 = 0.01800555" is high by 5e-8). The cell's 0.0180056 is one digit above the true product, and the gap from the true product is 127.12 microrad. Finding unchanged (printed "~127 microrad", L227, still equals the gap to the printed precision). FIX: "0.0180055 (the paper prints 0.01800555) and gap about 127.1 microrad".
- +0.7%: RECOMPUTED, 0.01813262/0.01800555 - 1 = 0.706%.
- "~127 microrad": TRACED, paper L227.
- "fez is Heron r2" (not a figure): IBM's public backend listing; no kept file states it (qia_runs props files give only the backend name). The paper says "IBM Eagle" (L57).

### recount_2511.14821 - KEEP
- 84.90 and 26.12: RECOMPUTED from Table VII's 11 rows (paper text L1249-1262). Noisy emulation 87.0, 88.4, 88.6, 85.2, 91.4, 83.9, 89.0, 85.4, 82.2, 81.7, 71.1: sum 933.9, mean 84.90. Hardware 68.3, 75.7, 30.7, 4.1, 2.4, 47.1, 45.3, 8.4, 1.8, 3.5, 0.0: sum 287.3, mean 26.118 (the table's "~2.4" and "~0.0" entered as 2.4 and 0.0). Body prints 84.9 and 26.1 (L955).
- 58.8: 84.90 - 26.12 = 58.78; printed 58.8 (L14, L1040).
- 85.2 and 26.4 (abstract): printed (L13-14); 85.2 coincides with the single 'symmetric' row (L1249), not with the table mean 84.90.

### recount_10.5281/zenodo.22848316 - KEEP
- 10.1: RECOMPUTED, spherical separation of (RA 42.41, Dec +16.26) and (RA 41.69, Dec +6.17) = 10.115 degrees (paper text L85-101); RA difference alone 0.72 (printed L21, L108).
- 0.0078: (1 - cos 10.1146 deg)/2 = 0.00777 (0.00775 at exactly 10.1), the chance of two random directions within that angle.
- p 0.002 printed (L22, L111: 0.72/360).

### recount_10.5281/zenodo.20352903 - KEEP
- 22.500: RECOMPUTED, arctan(sqrt 2 - 1) = 22.500000 deg; paper prints 22.5000 (L318-320) and "22.48 (two-decimal rounding)" (L22).
- 0.00061: RECOMPUTED, tan 22.47 deg - tan 22.50 deg = -0.000613; paper prints |delta tan| = 0.0006 (L23).
- 0.09 deg spread: printed (L23, L325).
- Q = 4.17, I2 = 0%: printed (L32-33, L939); I2 = max(0, (Q - df)/Q) = 0 since Q = 4.17 is below df (5 as printed at L999).

### fill_2602.20614 - KEEP
- fez SX 1.450 [1.367, 1.534] and CZ 1.244 [1.191, 1.303]; marrakesh SX 1.344 [1.205, 1.519] and CZ 1.616 [1.541, 1.750]: TRACED, BF/arxiv_one_readout/sweep_run/results_sweep_3.text L8-9 and L32-33 (jobs dbdsnpom94ac738qs3sg and dbdso8fsstms73fb3o3g, IBM record 23 Oct 2026). Also AUDIT.md L29-30.
- fez second session SX 1.417 [1.336, 1.528] and CZ 1.269 [1.206, 1.338]: TRACED, results_sweep_r2_part.text L8-9.
- 95%: TRACED, BF/arxiv_one_readout/sweep_run/sweep.py L158: bootstrap, np.percentile(..., [2.5, 97.5]).
- readout consistent, "median distance outside the bracket 0": TRACED, results_sweep_3.text L6 (fez +0.0000 [+0.0000, +0.0000]) and L30 (marrakesh +0.0000 [-0.0016, +0.0000]).
- "CZ 1.24-1.27 and 1.62 times stated": rounding of the above.

### recount_10.5281/zenodo.21682087 - KEEP
- 500: RECOMPUTED, 125,000 x 4 ns = 500 microseconds. dt = 4e-09 s for ibm_fez is in a kept job file, BF/arxiv_one_readout/length_run/job_ibm_fez.json (key "dt"). The paper prints 125,000 dt = 562.5 us (text L18, L65), which implies 4.5 ns.
- 860/1024 = 83.98%: RECOMPUTED, 0.839844; paper L71.

### recount_10.5281/zenodo.21479684 - KEEP
- 1/sqrt(4096) = 0.0156 and 1.20 sigma: RECOMPUTED, 0.015625 and 0.0187/0.0156 = 1.20; paper L353.
- 0.0078 and 0.13: RECOMPUTED, 1/sqrt(16384) = 0.0078125; 0.0010/0.0078 = 0.128 = 0.13 sigma. Printed -0.0010 and +0.0007 "At noise floor" (paper L344-348).

### recount_10.5281/zenodo.22050177 - KEEP
- 54.5: RECOMPUTED, (0.718 - 0.5)/0.004 = 54.5; F = 0.718 +- 0.004 and "60 sigma" printed (paper text L1220). The cell's "other figures rebuild" is a bundled statement with no itemised numbers; not rechecked here.

### free_2508.10593 - KEEP
- Table VII rows (paper text L858-866) summed with exact decimals: P3+ state-vector -64.97721 - 0.41085 - 0.41085 = -65.79891; QASM -64.97719 - 0.41084 - 0.41084 = -65.79887; hardware -64.94349 - 0.05491 - 0.05491 = -65.05331 (printed -64.99840 = S0 plus one clique). S4+ state-vector -75.69358 - 2 x 0.51610 = -76.72578; QASM -75.69318 - 2 x 0.51602 = -76.72522; hardware -75.69271 - 2 x 0.05601 = -75.80473. All as in the cell.

### free_2510.08719 - KEEP
- 2.0x: 676/337 = 2.006; 5.0x: 777/155 = 5.013. Printed in Sec. VI (paper text L1156-1160); Table IV labels Torino "(Fake backend)" (L1039) and Fig. 10 "mocked backend" (L1099); abstract "threefold" (L21).

### free_2603.16973 - KEEP
- 134 and 156 (and 153, 38): RECOUNTED, SP/t6/t6.py over the 28 accuracies of Table 6 (paper text L735-739). Cells that equal k/n rounded or truncated to 4 decimals: 0 of 28 for n = 153; 24 of 28 for n = 156 (every column except PL-Real); all 4 PL-Real cells for n = 38 (0.8421 = 32/38, 0.8684 = 33/38, 0.6579 = 25/38, 0.7895 = 30/38). 134/156 = 0.858974, printed 0.8589 (truncated). Table 1 gives 153 (L569).

### k2025_tara_2512.04016 - KEEP
- 2.679 +- 0.012 and S - 2 = +0.679: RECOUNTED from our raw counts BF/qia_runs/2026-10-24-fill-tara/raw_tara.json (40 CHSH circuits, 15,000 shots per setting): E00 0.6864, E01 0.6509, E10 0.6472, E11 -0.6945, S = 2.6791, binomial SE = 0.0121. Same as results_tara.text L2-4. Job date 2026-10-24 (job_tara.json).
- 2.732: RECOUNTED from the authors' released CSV (github.com/detasar/QCE, QCE-main/P1_TARA_Conformal_Quantum/data/ibm_hardware_real.csv, 60,000 rows, saved SP/tara_dl): E = 0.6976, 0.6673, 0.6653, -0.7017, S = 2.7320, SE 0.0119. Also KNOWN_GOOD.md L23, L44.

### recount_2512.14513 - KEEP
- 47 s and 1.18 s: printed (paper text L558-563, Table II L575, L579); 47/1.18 = 39.83, the 39.8.
- 40x is a per-run ratio: totals in Table II (L575, L579) are 5 h 20 min 10 s = 19,210 s (IBM) and 105 h 58 min 55 s = 381,535 s (IonQ), a ratio of 19.9, not 40.

