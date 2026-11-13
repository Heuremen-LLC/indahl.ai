# NUMBERS.md -- every number in main.tex and where it comes from

Root S = /Users/heuremen/bones-forge/heuremen.org/ ; T = S/experiments/2026-10-04-three-positions/ ; R = S/experiments/2026-09-28-rigetti-cepheus/
"derived" = computed here from released data by recompute_table.py (same rules/seed as T/verify.py) or simple arithmetic on sourced numbers.

| Number in paper | Source file : location |
|---|---|
| 2.18 / 2.32 / 3.79 us (summary values) | S/index.html "Time" row; S/what-we-measured.html table "Three -- time". NO computation found (TODO in paper). 2.32 equals kingston witness in S/trail/index.html (4 Oct, "Kingston ... 2.32 / 3.66 us") |
| 7 of 7 ordering | S/index.html Time row; S/what-we-measured.html ("The order never changes"). Only partly re-checkable (see Table 3 / TODO aachen) |
| 305 jobs; per-chip 86/75/55/25/24/20/20 | T/runs.json `n_runs`, `by_chip`; T/index.html |
| 302 with submission time; 2026-10-02..2026-10-07 | derived from T/runs.json `submitted_at` (3 are null: aachen 1, kingston 1, pittsburgh 1) |
| dense run ibm_fez 11 Oct, runs 901-903, 4,179 measurements, k=1..128 | T/THE_COUNT_20261011.txt headers; S/index.html Superposition row |
| Rigetti dates "late September and 4 October" | R/index.html |
| maker L: 2.18 (4 chips), 1.66 fez, 1.94 phoenix, 2.684 marrakesh | T/results.json `maker_stated_us`; T/data/clocks/*.json `stated_look_us` |
| rate range 2.91-10.25 deg/us | T/results.json `why_the_cut`; T/index.html |
| Spearman -0.17 to -0.56 | T/verify.py section 1 output (recomputed); T/index.html |
| cut 4 deg/us; keep rule 0.15 / 3 widths; window (-5,60); ladder 1,2,3,4,6,9; delays 10/20/30; WIN 0..240 | T/split_seven_chips.py header + constants; T/DARK_SPAGHETTI_AMENDMENT_01 (root selection) |
| 524 spectator readings; 284 above cut; 30 negative; 254 non-negative | T/verify.py (524; 284; 30); 254 = 284-30 derived |
| per-chip R (cut only) 1.0457 etc., n 43/43/31/27/23/63/54 | T/verify.py section 2 output; T/results.json `witness_over_maker_rate_gt_4` |
| per-chip R (non-negative), widths, neg counts 3/8/5/2/1/9/2 | derived: recompute_table.py (bootstrap 400, seed 20261011) |
| per-chip widths (cut only) | derived (recompute_table.py) -- results.json widths differ (different bootstrap) e.g. fez 0.0157 in both, kingston 0.0198 both |
| spectator us = R x L (2.30, 2.28, ...) | derived |
| per-chip "sigma from 1" 0.1-2.4 | derived from the R and widths in Table 1 |
| pooled 1.0207 +- 0.0092, chi2/dof 0.52, p 0.79, 2.2 sigma | T/results.json `pooled_rate_gt_4`; T/verify.py section 3 |
| pooled 1.0331 +- 0.0083, chi2/dof 0.88, 4.0 sigma, 12/11 7.0 sigma (7.6 before) | T/verify.py section 6; T/DARK_SPAGHETTI_CALL_20261011.txt table |
| 12/11 exclusion 7.6 / 7.0 sigma | same |
| no-cut: chi2/dof 2.93, p 0.0074 | T/results.json `why_the_cut` |
| no-cut: pooled 1.0405, chi2/dof 2.22, p 0.0384 | T/verify.py section 5 output (INCONSISTENT with 2.93/0.0074; flagged) |
| aachen 69% below cut | T/results.json `why_the_cut` |
| two-point scatter 0.0325 vs fit 0.0183; 2.4x | T/results.json `two_estimators`; T/index.html |
| S = -0.036 +- 0.038 (-0.0361 +- 0.0375), chi2/dof 0.18 (0.177, 6 dof) | T/THE_APPARATUS_TERM_20261011.txt "S against ONE CONSTANT"; S/index.html |
| 21 runs, 767 spectators | S/index.html; 767 = 76+113+106+152+85+167+68 from THE_APPARATUS_TERM table |
| Table 3 (S, P, spectators per chip) | T/THE_APPARATUS_TERM_20261011.txt chip table |
| mean P 1.0469, sd 0.0221 ("1.047", "0.022") | same, "ACROSS THE SEVEN" |
| injection: 0/0.2/1.0/5.0 -> 1.0007/1.0011/1.0026/0.9994; recovered intercept -0.0042/0.1907/0.9775/5.0000; also 0.1/0.5/2.0 -> 0.9991/1.0017/1.0009; P 1.0331->1.0342; L=1.66, noise 0.30, 400 fits | T/THE_APPARATUS_TERM_20261011.txt "PLANTED TEST"; T/split_seven_chips.py `planted()`; S/what-we-measured.html |
| Table 2 (three positions): marrakesh 2.80/4.05/1.51/1.45; kingston 2.32/3.66/1.68/1.57; pittsburgh 4 Oct 2.27/3.06/1.40/1.35; pittsburgh 2 Oct 2.37/3.5/1.606/1.477; fez 1.54/1.51 | S/trail/index.html (lines "4 October, three chips", "What the qubits showed", "ONE on a second chip") |
| kingston 1-9 fit 1.59-1.74 | S/trail/index.html ("Read with the 1-9 fit it misses (1.04-1.07 / 1.59-1.74 / 1.50-1.63)") |
| qubit/spectator 1.22-1.35 (boston, pittsburgh, phoenix), 1.45-1.78 (kingston, fez, marrakesh) | S/index.html; S/trail/index.html; T/CHAIN... n/a |
| 30/284 = 10.563% +- 1.824%; 0.28379 +- 0.04477; Spearman -0.067 n=30; +0.893 n=7 p 0.0123 | T/DARK_SPAGHETTI_CALL_20261011.txt |
| edges 8.22% vs middle 2.47%, Fisher p 5.9e-07 | T/DARK_SPAGHETTI_AMENDMENT_01_20261011.txt |
| Rigetti negatives 35.20% (515/1463); rate edges 36.99 vs 35.62; P2 +0.097 / +0.280 vs 0.3; P1 failed, P3 unrunnable | T/DARK_SPAGHETTI_AMENDMENT_02_20261011.txt |
| chip-independence: no pair survives, resolves overlap > ~0.8 | T/DARK_SPAGHETTI_CALL_20261011.txt |
| Rigetti no-tone control 0.9922/0.9881/1.0005/0.9919 (~0.99) | R/THE_SECOND_VENDOR_20261011.txt (s03, s03b, day2, s06) |
| Rigetti P 1.0114 +- 0.0045, S +0.0352 +- 0.0147 (3 jobs); P 0.9930 +- 0.0186, S +0.0544 +- 0.0219 (4 jobs) | R/THE_SECOND_VENDOR_20261011.html (re-read) |
| Rigetti weighted fit: P 0.9561 +- 0.0101, S +0.1018 +- 0.0265; 35.40 vs 36.0 deg/us; difference 0.0552; offset 2.4 / 3.8 sigma | same ("Amendment, same night") |
| withdrawn 1.035 +- 0.014; offset-only ratio 1.020-1.031, 1.058; mean laid 1.75 us | R/index.html; R/THE_SECOND_VENDOR html |
| laid looks 1.0/1.5/2.0/2.5 us; 100 clocks per job | R/THE_SECOND_VENDOR html; R/THE_SECOND_VENDOR_20261011.txt |
| Rigetti device name Cepheus-1-108Q | R/index.html |
| 21 hashed calls: 3 land, 2 edge, 2 partly, 1 all-rulers, 12 miss, 1 unreadable (11 miss before 11 Oct re-read) | S/trail/index.html scoreboard; independent list (11 miss, 4 land) in /Users/heuremen/bones-forge/coin/CHAIN_FIT_EVAL.md F26 |
| 0.99-1.03 up to 9; 1.16-1.18 at 27 | S/index.html Superposition row |
| shape exponents 0.823 +- 0.013 / 1.381 +- 0.074; worst chi2/dof 1.38 | S/index.html; T/THE_COUNT_20261011.txt (per read 0.829/0.809/0.832 and 1.296/1.433/1.415) |
| ~22 GB raw data | T/README.md; results.json `raw_data` |
| Zenodo doi:10.5281/zenodo.23169756 | supplied in the task brief (not checked online) |
| References | arXiv API lookups on 2026-10-21 (titles, authors, journal refs checked) |

## Inconsistencies noticed in the sources
1. 11 vs 12 of 21 missed: current trail says 12 miss, 3 land; CHAIN_FIT_EVAL says 11 miss, 4 land (older count before ONE was re-read).
2. No-cut chi2/dof: results.json 2.93 (p 0.0074) vs verify.py section 5 2.22 (p 0.0384).
3. 2.32 / 3.79 us summary values have no computation in the released files.
4. results.json "witness_over_maker_all_clocks" (e.g. aachen 1.1449) is a different reduction from verify.py section 5.
5. Slope-fit P (mean 1.047, 5.6 widths from 1) differs from the median ratio 1.0331.
6. Index "0.067 of where it started" at 128 looks vs THE_COUNT per-read k=128 levels 0.0694 / 0.0578 / 0.0624 (not used in the paper).
7. runs.json: 3 entries with null submitted_at.
8. "Seven IBM heavy-hex" vs ibm_phoenix described as a square lattice (T/THE... and S/index.html "the one processor with a square lattice").
9. S/index.html cites Rigetti slope 1.0114 +- 0.0045 as support; the re-read shows it moves to 0.9561 under another rate definition.
