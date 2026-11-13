## Appendix A. Run log

This appendix records what was fired and what was read.

**Conventions.**
- Source of every count: RUN_INDEX.csv (3261 rows: one per IBM job or Braket task on record since 1 Sep 2026). Completed = IBM DONE or Braket COMPLETED; cancelled = Braket CANCELLED; failed = IBM ERROR or Braket FAILED; queued = IBM QUEUED (shown separately). Entry counts read "N jobs (or tasks): completed/cancelled/failed".
- Dates are the created field of the index. IBM stamps are local (EDT); Braket stamps are UTC, so tasks fired in the evening of one EDT day can carry the next date.
- A family is one date, one vendor and one experiment label of the index; for the 2, 4 and 5 October IBM jobs the label is the run script that fired (the index shows a sibling script's name for some 5 October runs; see the provenance note), and run numbers are listed in the script entry. The 22 drift rounds of 5 October, each its own label in the index, are one entry.
- Source tags: [§n] is entry n of the run ledger parallax/THIRD_RUNG_20260928.md. Other tags are paths relative to  (the Biblioteca is notebook, cited with its dated heading).
- Numbers are copied as recorded. Values taken from JSON read files are shown to four decimals (the files hold more digits). "No read on file" means no read of that family was found in the ledgers or read files searched.
- Chip names are as in the index. Qubit labels (q0, q9, ...) are the vendors' qubit numbers.
- Provenance note (5 October): ten run scripts of 4-6 October (eight fired, 20 runs; two armed for 6 October) name a sibling script in their freeze list, so their freeze records hash that sibling and not the file that fired. The fired files were hashed and timestamped beside the freezes in calls/SIDE_FREEZE_20261005.txt (sha256 a0f2943bb6190d7b...); a three-reader check (freeze, file time, circuits rebuilt against the vendor's stored inputs) is in data_provenance_20261005.txt.

### Totals by vendor and day

| Vendor | Day | Jobs/tasks | Completed | Cancelled | Failed | Queued |
|---|---|---|---|---|---|---|
| IBM (Qiskit Runtime) | 2026-09-24 | 17 | 16 | 0 | 1 | 0 |
| IBM (Qiskit Runtime) | 2026-09-28 | 65 | 65 | 0 | 0 | 0 |
| IBM (Qiskit Runtime) | 2026-10-01 | 3 | 3 | 0 | 0 | 0 |
| IBM (Qiskit Runtime) | 2026-10-02 | 72 | 71 | 0 | 1 | 0 |
| IBM (Qiskit Runtime) | 2026-10-04 | 43 | 42 | 0 | 1 | 0 |
| IBM (Qiskit Runtime) | 2026-10-05 | 26 | 26 | 0 | 0 | 0 |
| Rigetti Cepheus-1-108Q (Braket) | 2026-09-25 | 21 | 21 | 0 | 0 | 0 |
| Rigetti Cepheus-1-108Q (Braket) | 2026-09-26 | 204 | 184 | 0 | 20 | 0 |
| Rigetti Cepheus-1-108Q (Braket) | 2026-09-28 | 94 | 94 | 0 | 0 | 0 |
| Rigetti Cepheus-1-108Q (Braket) | 2026-09-29 | 244 | 244 | 0 | 0 | 0 |
| Rigetti Cepheus-1-108Q (Braket) | 2026-10-04 | 1162 | 1046 | 116 | 0 | 0 |
| Rigetti Cepheus-1-108Q (Braket) | 2026-10-05 | 1310 | 1310 | 0 | 0 | 0 |
| **IBM (Qiskit Runtime)** | **all days** | **226** | **223** | **0** | **3** | **0** |
| **Rigetti Cepheus-1-108Q (Braket)** | **all days** | **3035** | **2899** | **116** | **20** | **0** |
| **Both vendors** | **all days** | **3261** | **3122** | **116** | **23** | **0** |

### Families, in date order

**2026-09-24 ibm_fez, ibm_kingston, ibm_marrakesh -- raw_repull (raw results only)** (14 jobs: 14/0/0)

What was laid: Fourteen jobs whose results exist only as raw re-pulled files [parallax/out/raw_repull/]. Jobs named in the discard map and the Biblioteca: the first idle-pair run on ibm_marrakesh (1 job, estimator, one entangled-pair circuit and two controls per pair) [notebook, 2026-09-24 ~17:20Z; parallax/out/discards/DISCARD_MAP.md, H5]; the second version of that run on ibm_marrakesh (10 jobs; per pair one parameterized circuit with an RZ rotation on qubit b between the CX and the RY, 12 angles in shuffled order, 2048 shots, plus two control circuits at 4096 shots, t = 30 us) [notebook, 2026-09-24 ~20:05Z]; one three-box job on ibm_kingston (weak probe, 8192 shots) [parallax/out/discards/DISCARD_MAP.md, H7; notebook, 2026-09-24 ~22:20Z]; and one three-box job with the dark box in the |11> corner on ibm_marrakesh [notebook, 2026-09-24 ~21:30Z]. One ibm_fez job in this group is not named in the ledgers searched.

What was read: First idle-pair run (ibm_marrakesh): t = 0, D = +0.0012 +/- 0.0024 (8 pairs); t = 30 us, D = +0.0054 +/- 0.0050 [notebook, 2026-09-24 ~17:20Z]. Second version (10 jobs): chi2 of the phase term 19.4 on 20 dof; D with the entangled circuit first +0.0124 +/- 0.0046; D with it last -0.0013 +/- 0.0154; D averaged over both orders +0.0056 +/- 0.0081 [notebook, 2026-09-24 ~19:10Z]. Three-box job on ibm_kingston: A +0.798 +/- 0.056, B +0.843 +/- 0.050, C -0.587 +/- 0.057, corner 11 +0.174 +/- 0.063 [notebook, 2026-09-24 ~21:14Z]. Three-box job with the dark box in the |11> corner (ibm_marrakesh): corner 11 -0.506 +/- 0.057, A_00 +0.773, B_01 +0.763, unused 10 +0.169 +/- 0.061 [notebook, 2026-09-24 ~21:31Z]. No read on file attributable to the ibm_fez job.

**2026-09-24 ibm_kingston, ibm_marrakesh -- NOTHING_SWEEP_sep24_27.md** (2 jobs: 1/0/1)

What was laid: Two jobs. The completed one is the ibm_kingston run of the idle-30-us pair experiment (8 qubit pairs, t = 30 us, entangled-pair circuit, two product-state controls, same mitigation as the ibm_marrakesh run) [parallax/NOTHING_SWEEP_sep24_27.md, item a1; notebook, 2026-09-24 ~17:20Z]. The failed one is attempt 1 of the second version of that experiment on ibm_marrakesh, 30 pubs [parallax/out/discards/DISCARD_MAP.md, H6].

What was read: ibm_kingston, t = 30 us: D = +0.00832 +/- 0.00291, 6 of 8 pairs positive [notebook, 2026-09-24 ~18:05Z]. No read on file for the failed job.

**2026-09-24 ibm_kingston -- FREE_CHECKS_20260929.md** (1 job: 1/0/0)

What was laid: One job named in the free-checks note as the job that read qubit pairs 16-23 and 144-145 on ibm_kingston; it was submitted in the same second as a one-qubit job on the same chip [parallax/FREE_CHECKS_20260929.md, item 1].

What was read: No read on file.

**2026-09-25 Cepheus-1-108Q -- round1** (21 tasks: 21/0/0)

What was laid: Step 1 on q0: find the 1-2 transition drive amplitude. Each circuit is an X gate (0 to 1), an f12 pulse of amplitude a, an X gate (1 to 0), then measure; anything the f12 pulse moved into |2> reads as 1. 21 amplitudes from 0.0 to 0.8, 300 shots each [standoff/braket_round1.py].

What was read: Fitted f12 half-turn amplitude 0.494; measured peak 0.94 at amplitude 0.48; contrast 0.8789; offset 0.0692; rmse 0.0234; 300 shots per point [standoff/round1_fit.json].

**2026-09-26 Cepheus-1-108Q -- step2** (42 tasks: 42/0/0)

What was laid: Step 2 on q0 in three parts: A, prepare |0>, |1>, |2> and read each plainly and after an X gate (1000 shots); B, prepare |2>, wait 0 to 35 us, read both ways (300 shots, 10 delays); C, Ramsey on the 1-2 transition at 4 MHz virtual detuning (300 shots, 16 delays from 0 to 1.5 us) [standoff/braket_round1_step2.py].

What was read: Part A, P(read 1) for prepared 0 / 1 / 2: plain 0.035 / 0.947 / 0.893; after the X gate 0.932 / 0.048 / 0.951. Part B, read after the X gate: 0.94 at 0 us and 0.5233 at 35 us [standoff/step2_results.json].

**2026-09-26 Cepheus-1-108Q -- two_clocks** (2 tasks: 2/0/0)

What was laid: Two tasks whose IDs were first found in the job-list file parallax/out/two_clocks/braket_tasks.json. One is the orphaned first try of the step 2b Ramsey (part C, delay 0, 300 shots; created between step 2 and step 2b and collected on 29 Sep) [standoff/orphan_step2b_4f3a04f7-2eb6-44a4-a063-6c3acbef2454.json]. The other is the random-seed task: rx quarter turn on 80 qubits, 10,000 shots [standoff/dice_refill.py].

What was read: Orphan task: 280 of 300 shots read 1 [standoff/orphan_step2b_4f3a04f7-2eb6-44a4-a063-6c3acbef2454.json]. Seed task: 800000 raw bits, fraction of ones 0.5177 [standoff/pup_seeds.provenance.json].

**2026-09-26 Cepheus-1-108Q -- step2b** (21 tasks: 21/0/0)

What was laid: The Ramsey part of step 2 again at finer delays on a 4 ns grid, 500 shots per delay, q0 [standoff/braket_round1_step2.py; notebook, 2026-09-25 late].

What was read: P(read 1) at delays 0.0 / 0.05 / 0.1 / 0.15 / 0.2 us: 0.926 / 0.738 / 0.194 / 0.122 / 0.512 [standoff/step2b_results.json]. Recorded fit: 1-2 transition offset -0.16 MHz from the vendor frame, T2* about 6.6 us [notebook, 2026-09-25 late].

**2026-09-26 Cepheus-1-108Q -- step3** (35 tasks: 35/0/0)

What was laid: Native three-level three-box circuit on q0: prepare (|0> + i|1> + |2>)/sqrt3, post-select the same state with the |2> sign flipped; one box is opened by a strong measurement, giving branches 'found' and 'not found'; native rx, rz and f12 pulses only; the analysis was written in the script before the data [standoff/braket_round1_step3.py].

What was read: Fringe phase setting x0 = -3.0560. P at the post-selection setting: prepared state 0.0855; A not found 0.0136; B not found -0.0194; C not found 0.6052. Weak-value numbers from the recorded rule: A 0.9224, B 1.1447, C 0.2049 [standoff/step3_abl.json].

**2026-09-26 Cepheus-1-108Q -- grid16q** (16 tasks: 16/0/0)

What was laid: A 16-arm factorial on q0's three levels with four switches: S (the preparation applied twice), R (an X swap between preparation and read), B (post-select the second state instead of undoing the preparation), P (two f12 pulses that return populations unchanged); 3000 shots per arm; the ideal-model values were computed in the script before the data [standoff/grid16q.py].

What was read: Four-way term SRBP measured -0.0179 (+/- 0.0022 in the Biblioteca entry), ideal-model value -0.0188; arm (0,0,0,0) 0.9258 [standoff/grid16q_analysis.json; notebook, 2026-09-26 ~01:35Z].

**2026-09-26 Cepheus-1-108Q -- round2** (18 tasks: 18/0/0)

What was laid: Weak values of the three boxes with a pointer: q0 as the three-level system, q1 as the pointer started at 45 degrees, one native CZ, the box held in |1> chosen by shelving; 9 calibration tasks (q0 parked in 0 / 1 / 2, pointer read in X, Y, Z; 1000 shots) and 9 run tasks (3 shelving configurations x 3 bases; 3000 shots) [standoff/round2_hw.py; standoff/round2_weak.py].

What was read: Fitted W_A +1.015 +/- 0.076, W_B +0.831 +/- 0.073, W_C -0.838 +/- 0.092; CZ phase per level 0 / 1 / 2: -0.03 / 3.02 / 2.47 rad [notebook, 2026-09-26 ~04:00Z; standoff/round2_analysis.json].

**2026-09-26 Cepheus-1-108Q -- ring_rabi_q90** (9 tasks: 9/0/0)

What was laid: A 9-point f12 Rabi scan on q90, amplitudes 0.0 to 0.32 in steps of 0.04, 300 shots each [standoff/ring_rabi_q90_fit.json].

What was read: f12 half-turn amplitude 0.1645; contrast 0.9568; offset 0.0171; rmse 0.0189 [standoff/ring_rabi_q90_fit.json].

**2026-09-26 Cepheus-1-108Q -- ring** (26 tasks: 6/0/20)

What was laid: Two-witness five-context ring on q0 and q90 (qutrit readout): 5 contexts x 2 readout schemes x waits of 0 and 5 us, plus 6 in-job readout-calibration circuits, 26 tasks of 1900 shots; task order from random bytes of pup_seeds.bin [standoff/ring_two_witness.py; notebook, 2026-09-26 'THE RING -- PRE-REGISTRATION'].

What was read: 20 context tasks failed; 6 tasks completed. In-job readout rows, P(read 1) for prepared 0 / 1 / 2: q0 plain [.046, .931, .926], after X gate [.926, .055, .956]; q90 plain [.007, .933, .943], after X gate [.910, .006, .964] [notebook, 2026-09-26 'THE RING -- RESULT: NOT RUN'; standoff/ring_analysis.json].

**2026-09-26 Cepheus-1-108Q -- plus_none** (14 tasks: 14/0/0)

What was laid: Five-step gate chain on q99, then a sixth slot in three variants at the same elapsed time D (2 us and 6 us): (a) an empty delay after the chain, (b) the same delay between steps 1 and 2, (c) X gate, delay, X gate; plus a reference with no D; two analysis settings (S1, S2); 1300 shots per task; task order from random bytes of pup_seeds.bin [standoff/plus_none.py].

What was read: P(1) difference a minus b: -0.005 +/- 0.015 (2 us, S1), +0.020 +/- 0.018 (2 us, S2), -0.025 +/- 0.019 (6 us, S1), -0.035 +/- 0.015 (6 us, S2). Variant c against variant a at S2: 0.22 against 0.74 (2 us), 0.14 against 0.80 (6 us) [notebook, 2026-09-26, 'THE PLUS NONE -- RESULT'; standoff/plus_none_analysis.json].

**2026-09-26 Cepheus-1-108Q -- ring_diag** (1 task: 1/0/0)

What was laid: One acceptance task of 100 shots: ring context 1, 5 us wait, readout scheme b, on q0 and q90, after the 01 rotations were rebuilt from native rx, rz, rx [notebook, 2026-09-26 'THE RING -- RESULT: NOT RUN'; standoff/ring_diag_results.json].

What was read: P(read 1): q0 0.52, q90 0.62 [notebook, 2026-09-26 'THE RING -- RESULT: NOT RUN'].

**2026-09-26 Cepheus-1-108Q -- ring_rerun** (20 tasks: 20/0/0)

What was laid: The 20 ring context tasks again, with the 01 rotations built from native rx, rz, rx 1900 shots each; task order from pup_seeds.bin bytes 49856-49919 [notebook, 2026-09-26 ~16:55Z; standoff/ring_two_witness.py].

What was read: Ring sum S_corr (S_raw): q0, 0 us 2.204 +/- 0.024 (2.284 +/- 0.018); q0, 5 us 2.088 +/- 0.024 (2.183); q90, 0 us 2.114 +/- 0.021 (2.301 +/- 0.018); q90, 5 us 2.067 +/- 0.020. Cross-witness per-task correlation z between -1.7 and +2.6 [notebook, 2026-09-26 ~16:55Z; standoff/ring_analysis.json].

**2026-09-28 ibm_marrakesh -- 20260928_083041** (4 jobs: 4/0/0)

What was laid: The IBM half of the parallax run on ibm_marrakesh, 78 qubits (every even qubit), raw I/Q readout. J1 default shot spacing, 4000 shots (measure; X then measure; measure twice; X then measure twice); J2 spacing 20 us, 2000 shots; J3 spacing 1 ms, 2000 shots; J4 default spacing again, 2000 shots [parallax/parallax_ibm.py].

What was read: Medians over 78 qubits: prepared 0, one look, read 1 on 0.52% of shots; second look after a first look read 0, 0.08%; read 1 on both looks 0.39%; shots 20 us apart 1.15% against 0.40% for shots 1 ms apart; q26 off both clouds on 1.7% of prepared-1 shots [notebook, 2026-09-28 ~12:40Z].

**2026-09-28 ibm_marrakesh -- echo_20260928_122733** (14 jobs: 14/0/0)

What was laid: The echo run on ibm_marrakesh: each shot is a look, then an X gate (E1) or none (E0), then a look; 78 even qubits, 1500 shots, gap between shots 20, 50, 100, 250, 500, 1000 and 2000 us (14 jobs = 2 circuits x 7 gaps) [parallax/parallax_echo.py].

What was read: Median qubit, (after a 1 minus after a 0) first-look reading: 0.07% at a 20 us gap, 0.00% by 50 us. First look reads 1 on 0.70% of shots at 20 us, 0.47% at 50 us, 0.30% by 500 us; after a 0 ending 0.70% and after a 1 ending 0.77%. After the X gate the second look reads 0 on about 1.7% at every gap [notebook, 2026-09-28 ~17:00Z]. Chip-wide (74 readable qubits): 0.84% at a 20 us gap above a 0.31% floor [§17].

In the paper: Partly reported in Section 3.5 (the chip-wide drain numbers of §17); the other reads are given here.

**2026-09-28 ibm_kingston -- 20260928_123452** (4 jobs: 4/0/0)

What was laid: The same parallax run on ibm_kingston [parallax/parallax_ibm.py].

What was read: One look 0.39%, both looks 0.25%; 1 qubit (q146) with no readable separation; crowding 20 us against 1 ms 1.2x [notebook, 2026-09-28 ~17:25Z].

**2026-09-28 ibm_kingston -- darkwave_20260928_124527** (1 job: 1/0/0)

What was laid: Round 1 of the eraser circuit on ibm_kingston (qubits 47, 48, 64 as S, I, C), wait 5 us. Three qubits S (record), I (partner), C (coin), 8 phases, 4000 shots per phase: H on S, CX from S to I, phase on S, H on S, measure S (the record); then a wait; then C is flipped to a quantum coin and measured, and if C = 1 an H is applied to I before I is measured [parallax/darkwave_eraser.py].

What was read: Record alone V 0.026 +/- 0.016; sorted by the later coin: erased V 0.65 / 0.62 (+/- 0.03, for partner 0 / 1), path kept V 0.03 / 0.02 [notebook, 2026-09-28 ~17:55Z].

**2026-09-28 ibm_fez -- witness_crowd** (6 jobs: 6/0/0)

What was laid: The label is an analysis folder, not a run script: parallax/out/witness_crowd/ re-reads 25 finished ibm_fez jobs of 28 Sep from raw_repull and holds the readings of the 6 jobs counted here [parallax/out/witness_crowd/WITNESS_CROWD.md].

Reported in Section 3.4.

**2026-09-28 ibm_marrakesh -- darkwave_ibm_marrakesh_20260928_125452** (3 jobs: 3/0/0)

What was laid: Round 2 on ibm_marrakesh, variants early (coin and partner read before the record), late5 and late50 (record, wait 5 or 50 us, coin) [parallax/PREREG_DARKWAVE.md, Round 2; parallax/darkwave_eraser.py].

What was read: Erased V early 0.96, late5 0.87, late50 0.54 [parallax/PREREG_DARKWAVE.md, Round 2 result].

**2026-09-28 ibm_fez -- darkwave_ibm_fez_20260928_125452** (1 job: 1/0/0)

What was laid: Round 2 on ibm_fez, variant early (coin and partner read before the record), S, I, C = 143, 144, 70 [parallax/PREREG_DARKWAVE.md, Round 2; parallax/darkwave_eraser.py].

What was read: Erased V early 0.94; the same round records late5 0.27 and late50 0.09 for ibm_fez [parallax/PREREG_DARKWAVE.md, Round 2 result].

**2026-09-28 ibm_fez -- 20260928_125537** (4 jobs: 4/0/0)

What was laid: The same parallax run on ibm_fez [parallax/parallax_ibm.py].

What was read: One look 0.29%, both looks 0.21% [notebook, 2026-09-28 ~18:30Z].

**2026-09-28 ibm_marrakesh -- darkwave_ibm_marrakesh_20260928_125804** (1 job: 1/0/0)

What was laid: Round 3 on ibm_marrakesh, variant late0 (record, zero wait, then the coin) [parallax/PREREG_DARKWAVE.md, Round 3; parallax/darkwave_eraser.py].

What was read: late0 erased V 0.98 / 0.95 [parallax/PREREG_DARKWAVE.md, Round 3 result].

**2026-09-28 ibm_fez -- darkwave_ibm_fez_20260928_125951** (1 job: 1/0/0)

What was laid: Round 4 on ibm_fez, variant late50e (50 us wait with X, 25 us, X, 25 us on the partner) [parallax/PREREG_DARKWAVE.md, Round 4; parallax/darkwave_eraser.py].

What was read: late50e erased V 0.27 / 0.27 [parallax/PREREG_DARKWAVE.md, Round 4 result].

**2026-09-28 ibm_marrakesh -- darkwave_ibm_marrakesh_20260928_125951** (1 job: 1/0/0)

What was laid: Round 4 on ibm_marrakesh, variant late50e (50 us wait with X, 25 us, X, 25 us on the partner) [parallax/PREREG_DARKWAVE.md, Round 4; parallax/darkwave_eraser.py].

What was read: late50e erased V 0.59 / 0.59 [parallax/PREREG_DARKWAVE.md, Round 4 result].

**2026-09-28 ibm_fez -- darkwave_ibm_fez_20260928_130429** (5 jobs: 5/0/0)

What was laid: Round 5 on ibm_fez (S, I, C = 143, 144, 70), variants late0, late2, late5, late10, late20 (record, wait of that many us, coin) [parallax/PREREG_DARKWAVE.md, Round 5; parallax/darkwave_eraser.py].

What was read: Erased V at 0 / 2 / 5 / 10 / 20 us: 0.93 / 0.74 / 0.08 / 0.78 / 0.60 [parallax/PREREG_DARKWAVE.md, Round 5 result].

**2026-09-28 ibm_fez -- partner_ibm_fez_130509** (1 job: 1/0/0)

What was laid: Free-evolution coherence of the partner qubit on ibm_fez (S = 143, I = 144): series 'alone' (S left in |0>) and 'after' (S put in |+> and measured first), partner H, wait 0 to 50 us (10 delays), read in X or Y, 2000 shots [parallax/partner_memory.py].

What was read: Coherence alone / after: 0.97 / 0.98 at 5 us, 0.95 / 0.93 at 12 us, 0.77 / 0.77 at 50 us [parallax/PREREG_DARKWAVE.md, Round 5 result].

**2026-09-28 ibm_fez -- beat_ibm_fez_130853** (1 job: 1/0/0)

What was laid: Round 6 on ibm_fez: one job, waits 0 to 24 us (15 values), 4 phases, 2000 shots, eraser variant late<w> [parallax/darkwave_beat.py].

What was read: Erased V at 0 / 1 / 2 / 3 / 4 / 5 / 6 / 7 / 8 / 10 / 12 / 14 / 16 / 20 / 24 us: 0.96, 0.87, 0.76, 0.52, 0.37, 0.07, 0.22, 0.39, 0.58, 0.77, 0.75, 0.54, 0.13, 0.59, 0.56 [parallax/PREREG_DARKWAVE.md, Round 6 result].

**2026-09-28 ibm_fez -- split_ibm_fez_131030** (1 job: 1/0/0)

What was laid: Round 7 on ibm_fez, waits 0, 3, 5, 8, 10 us: (a) the record taken, a wait, then H on the partner always and read (no coin), 4 phases x 2000 shots; (b) entangled-memory arm, H on S, CX, read S, wait, read the partner in X or Y, split by S's outcome [parallax/darkwave_split.py].

What was read: (a) V at 0 / 3 / 5 / 8 / 10 us: 0.97 / 0.57 / 0.11 / 0.57 / 0.78. (b) coherence, S = 0 branch: 0.95 / 0.60 / 0.12 / 0.58 / 0.81 [parallax/PREREG_DARKWAVE.md, Round 7 result].

**2026-09-28 ibm_fez -- culprit_131215** (1 job: 1/0/0)

What was laid: Round 8 on ibm_fez, waits 0, 3, 5, 8, 10 us, 2000 shots: partner 144 started in |+>; arms with CZ(143,144) applied twice, CZ(145,144) applied twice, or no CZ; read 144 in X or Y [parallax/darkwave_culprit.py].

What was read: Coherence at 5 us: no gate 0.98; CZ(143) twice 0.95; CZ(145) twice 0.95 [parallax/PREREG_DARKWAVE.md, Round 8 result].

**2026-09-28 ibm_fez -- ring_131350** (1 job: 1/0/0)

What was laid: Round 9 on ibm_fez, waits 0, 3, 5, 8, 10 us, 2000 shots: H, CX, then either the twin S measured first and the partner waits (arm b), or both wait and S is measured afterwards (arm f); partner read in X or Y, split by S's outcome [parallax/darkwave_ring.py].

What was read: Partner coherence, S = 0 branch, at 0 / 3 / 5 / 8 / 10 us: S measured first 0.96 / 0.66 / 0.35 / 0.62 / 0.81; S measured after the wait 0.96 / 0.68 / 0.37 / 0.61 / 0.80 [parallax/PREREG_DARKWAVE.md, Round 9 result].

**2026-09-28 ibm_fez -- barrier_132014** (1 job: 1/0/0)

What was laid: Round 11 on ibm_fez, one job, waits 0, 3, 5, 8, 10 us, 2000 shots: arm b (twin measured first, no barrier), arm B (the same with a barrier after the twin's measurement), arm f (twin measured after the wait); partner read in X or Y per S outcome [parallax/darkwave_barrier.py].

What was read: Partner coherence S = 0 / S = 1 at 0 / 3 / 5 / 8 / 10 us. b: 0.97/0.96, 0.58/0.55, 0.09/0.12, 0.58/0.55, 0.80/0.78. B: 0.96/0.95, 0.95/0.95, 0.95/0.93, 0.90/0.90, 0.91/0.87. f: 0.97/0.97, 0.59/0.60, 0.12/0.13, 0.57/0.53, 0.80/0.79 [parallax/PREREG_DARKWAVE.md, Round 11 result].

**2026-09-28 ibm_fez -- alone_132136** (1 job: 1/0/0)

What was laid: Round 12 on ibm_fez: plain Ramsey on each of qubits 143 and 144 alone (the other left in |0>, barrier-pinned), waits 0, 2, 3, 5, 8, 11, 14 us, 2000 shots, read in X or Y [parallax/darkwave_alone.py].

What was read: Coherence alone at 0 / 2 / 3 / 5 / 8 / 11 / 14 us: q143 0.99, 0.77, 0.68, 0.29, 0.61, 0.89, 0.60; q144 1.00, 0.98, 0.95, 0.96, 0.93, 0.90, 0.88 [parallax/PREREG_DARKWAVE.md, Round 12 result].

**2026-09-28 ibm_fez -- darkwave_ibm_fez_20260928_132156** (3 jobs: 3/0/0)

What was laid: Round 13 on ibm_fez (S, I, C = 143, 144, 70), 8 phases, 4000 shots, one job per variant: late5 (no barrier), late5B and late50B (a barrier after the record) [parallax/PREREG_DARKWAVE.md, Round 13; parallax/darkwave_eraser.py].

What was read: late5: S alone 0.015, erased 0.130 / 0.137, path kept 0.027 / 0.016. late5B: S alone 0.026, erased 0.887 / 0.901, path kept 0.216 / 0.291. late50B: S alone 0.014, erased 0.317 / 0.330, path kept 0.102 / 0.261 [parallax/PREREG_DARKWAVE.md, Round 13 result].

**2026-09-28 ibm_fez -- listen_ibm_fez_142649** (1 job: 1/0/0)

What was laid: No question written first. Every even qubit of ibm_fez (78), plain Ramsey all at once, 12 waits from 0 to 20 us, read in X and Y, 2000 shots [parallax/listen.py].

What was read: q138 recorded as a second two-tone qubit, beat about 7-8 us [notebook, 2026-09-28 ~13:25 EDT block, entries after 'THE LISTEN']. No other headline number is recorded in the ledgers searched.

**2026-09-28 ibm_fez -- split2_143826** (1 job: 1/0/0)

What was laid: Round 14 on ibm_fez: qubits 143 and 138 alone, Ramsey 0 to 22 us every 1 us, read in X or Y, 1000 shots, a two-tone fit; plus 4000-shot circuits (143 at 5.5 us, 138 at 3.75 us) for shot-to-shot correlation [parallax/darkwave_split2.py].

What was read: q143: second tone on 0.26 of shots, notes 90 kHz apart; q138: 0.17, 139 kHz apart. Consecutive shots agree 0.75 on q143 (0.67 sixteen shots later) and 0.30 on q138 [parallax/PREREG_DARKWAVE.md, Round 14 result].

**2026-09-28 ibm_fez -- oddraw_ibm_fez_144417** (1 job: 1/0/0)

What was laid: Every odd qubit of ibm_fez (78), plain Ramsey all at once, 12 waits from 0 to 20 us, X and Y, 2000 shots, raw I/Q dots kept, two reference circuits (all 0, all 1); job datbagtvr3kc73el7m2g [parallax/listen_raw.py; parallax/out/oddraw_ibm_fez_144417/meta.json].

What was read: No read on file (the folder holds per-qubit tables and images; no headline number is recorded in the ledgers searched).

**2026-09-28 ibm_fez -- the_do_144952** (1 job: 1/0/0)

What was laid: Qubits 113, 72 and 27 on ibm_fez; two looks per shot; barriers pin the order; every circuit has the same number of looks; waits 0, 2, 5, 10, 20 us; 4000 shots; each cut checked on half the references first [parallax/the_do.py].

What was read: Seat 72: 'told-1 lands far only 24%, main->far on 2nd look 6.5%; told-0 far 2.6%'. Seat 113: the second look repeats the first look's landing spot, correlation 0.55 against 0.02 on seat 27. Cut check misfile 22-34% on seats 113 and 72 [notebook, 2026-09-28 14:50 entry].

**2026-09-28 ibm_fez -- ripples_153734** (1 job: 1/0/0)

What was laid: A straight chain of 7 ibm_fez qubits (104 to 110), all in superposition; the middle qubit (107) is looked at either before or after the other six are read; waits 0 and 5 us; 4000 shots; raw dots [parallax/ripples.py].

What was read: q108 tilts 7-10 deg with the answer of the looked-at qubit q107, the same whether q107 is looked at before or after [notebook, 2026-09-28 15:4x entry; job datc3qbojkfs738qfk30].

**2026-09-28 ibm_fez -- yeast_153906** (1 job: 1/0/0)

What was laid: One job of the budding run on ibm_fez, stone q108: the pond is every qubit within 3 hops, read first; the stone is read last; waits 5000 ns, 4000 shots; the next stone is the pond qubit that tilts most with the stone's answer in its own noise units [parallax/yeast.py].

What was read: Generation 1, stone 108: stone cut check 0.01, 10 pond qubits [parallax/out/yeast_153906/yeast.json]. No other read on file for this job.

**2026-09-28 ibm_fez -- yeast_153959** (4 jobs: 4/0/0)

What was laid: The same budding run started from stone q143, four generations (stones 143, 144, 145, 146), brake 15 s [parallax/yeast.py].

What was read: Stone cut check by generation 0.0065 / 0.009 / 0.0155 / 0.007 [parallax/out/yeast_153959/yeast.json]. Recorded tilts along the chain: 143 to 144 12 deg, 144 to 145 24.5 deg, 145 to 146 12.4 deg [notebook, 2026-09-28 15:5x entry].

**2026-09-28 Cepheus-1-108Q -- heatlens** (6 tasks: 6/0/0)

What was laid: Two-point heat measurement on q0: arm A f12 pulse at amplitude 0 and at the f12 half-turn amplitude, X, read (10,000 shots); arm B X, f12 pulse, X, read (500 shots); arm D one look of prepared 0 and prepared 1 (1000 shots); 6 tasks [standoff/braket_heat_vs_lens.py].

What was read: A swing 0.0243, B swing 0.447, heat Pe = 0.0515 +/- 0.0035; one look prepared 0 read 1: 0.046; prepared 1 read 0: 0.095; a+b-1 at rest -0.049 +/- 0.0114 [standoff/heatlens_analysis.json; notebook, 2026-09-28 ~17:45Z].

**2026-09-28 Cepheus-1-108Q -- gamble** (21 tasks: 21/0/0)

What was laid: Whole-qubit gamble on q0 with partner q1: shuffle of the at-rest state across levels 0, 1, 2 (8 gate sequences, 5000 shots), blink-and-train arms (swap 1-2 then flip 0-1, now and after a 60 us wait, 3 batches minutes apart, 3000 shots), and an entangled-versus-product pair read plainly and after the swap (6000 shots); 21 tasks [standoff/rigetti_gamble.py].

Reported in Section 3.5.

**2026-09-28 Cepheus-1-108Q -- tune** (8 tasks: 8/0/0)

What was laid: Whole-chip f12 tune: every qubit in parallel, X, f12 push of amplitude a (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.75), X, read; 8 tasks of 1000 shots [standoff/rigetti_chip.py].

Reported in Sections 3.5 and 3.6.

**2026-09-28 Cepheus-1-108Q -- fine** (8 tasks: 8/0/0)

What was laid: Whole-chip f12 fine tune: the same circuit at amplitudes 0.04, 0.08, 0.12, 0.16, 0.24, 0.28, 0.32, 0.36; 8 tasks of 1000 shots; fitted jointly with the tune tasks [standoff/rigetti_chip.py].

Reported in Sections 3.5 and 3.6.

**2026-09-28 Cepheus-1-108Q -- run** (17 tasks: 17/0/0)

What was laid: Whole-chip shuffle: the at-rest state shuffled across levels 0, 1, 2 with 8 gate sequences on every qubit (5000 shots), then drain arms (swap-then-flip now, after 60 us, plain) in 3 batches minutes apart (2000 shots); 17 tasks [standoff/rigetti_chip.py].

Reported in Section 3.5.

**2026-09-28 Cepheus-1-108Q -- blink** (16 tasks: 16/0/0)

What was laid: The blink hour: whole chip, 8 checks about 7.5 minutes apart (23:34 to 00:27 UTC), each check a plain read, a swap-then-flip read and a 1-2 Ramsey at 1.5 us in two quadratures, 800 shots; the 32 tasks cross 00:00 UTC and are indexed as 16 + 16 [standoff/blink_hour.py].

Reported in Section 3.5.

**2026-09-28 Cepheus-1-108Q -- witness** (18 tasks: 18/0/0)

What was laid: Emitter q0 parked in 0 or 1 or pushed to level 2 and left to fall; clocks q9 and q1 (neighbours) and q10 (two links away) held in superposition through waits of 4, 8, 16 us; emitter read after a flip, each clock read in X or Y; 2000 shots; 18 tasks [standoff/witness.py].

Reported in Section 3.4.

**2026-09-29 Cepheus-1-108Q -- blink** (16 tasks: 16/0/0)

What was laid: The second half of the blink hour (checks continuing past 00:00 UTC; see the 28 Sep entry), 16 tasks of 800 shots [standoff/blink_hour.py].

Reported in Section 3.5.

**2026-09-29 Cepheus-1-108Q -- wchip** (24 tasks: 24/0/0)

What was laid: Whole-chip witness: emitter q0 at rest or pushed to level 2, every other qubit a clock, waits 0.5, 1, 2, 3, 4, 6 us, 2000 shots; 24 tasks [standoff/witness_chip.py].

Reported in Section 3.4.

**2026-09-29 Cepheus-1-108Q -- wobs** (24 tasks: 24/0/0)

What was laid: Who is watching: the same event with different sets of clocks (all clocks on, far clocks only, far clocks plus neighbours q1 and q9), arms rest, push with q0 at rest, and q0 pushed to level 2; waits 2 and 4 us; 2000 shots; 24 tasks [standoff/witness_obs.py].

Reported in Section 3.4.

**2026-09-29 Cepheus-1-108Q -- whead** (24 tasks: 24/0/0)

What was laid: One clock (q9) with every other qubit parked quiet; emitter q0 at rest or pushed to level 2; waits 0.5, 1, 2, 3, 4.5, 6 us; 1000 shots (rest) and 2500 shots (pushed); 24 tasks [standoff/witness_headline.py].

Reported in Section 3.4.

**2026-09-29 Cepheus-1-108Q -- wroom** (48 tasks: 48/0/0)

What was laid: The headline shot (q9 witness, emitter q0) with the room filled with other clocks: half (every other qubit) or full (every qubit); same waits; 1000 and 2500 shots; 48 tasks [standoff/witness_room.py].

Reported in Section 3.4.

**2026-09-29 Cepheus-1-108Q -- walt** (24 tasks: 24/0/0)

What was laid: Alternating rooms: q9 alone and the full room alternate task by task, two rounds, waits 0.5, 1, 2, 3, 4.5, 6 us, 2500 shots, emitter q0 pushed to level 2 each time; 24 tasks [standoff/witness_alt.py].

What was read: Emitter fall time, alone 26.6 us (26.0-27.6), full 31.2 us (30.0-32.4); at the first wait the full room reads 7.5% fell against 6.6% [§12].

**2026-09-29 Cepheus-1-108Q -- stack** (54 tasks: 54/0/0)

What was laid: Two shots with all outcomes kept: START, q0's heat at the start measured by the readout-proof swap trick plus a plain read, in rooms ALONE, HALF (54 clocks), FULL (106 clocks), rotated A,H,F then F,H,A; THREE, q0 at rest or at level 2, q9 the clock, q10 parked in 0 or 1, waits 1, 2, 4 us; 54 tasks [standoff/fuckup_stack.py].

What was read: START: ALONE 3.85% +/- 0.36, HALF 3.81 +/- 0.36, FULL 4.96 +/- 0.38; plain read 4.55 / 4.95 / 6.10%. THREE: q0's pull on q9 -60.9 deg/us (q10 at 0) and -62.2 (q10 at 1) [§13].

**2026-09-29 Cepheus-1-108Q -- edge** (30 tasks: 30/0/0)

What was laid: q0's heat at the start (swap trick plus plain read) with three rooms watching: ALONE, EDGE (q35, q62, q80), MIDDLE (q39, q58, q75); clocks lit at t = 0, 3 us wait; rotated ALONE, EDGE, MIDDLE then MIDDLE, EDGE, ALONE; 30 tasks [standoff/edge_room.py].

What was read: ALONE 3.83% +/- 0.36, EDGE 3.58 +/- 0.35, MIDDLE 2.23 +/- 0.35; MIDDLE 2.29 and 2.17 against ALONE 4.21 and 3.42 in the two rounds [§14].

**2026-10-01 ibm_kingston, ibm_phoenix, ibm_pittsburgh -- qubit_three_runs** (3 jobs: 3/0/0)

What was laid: Run 1 of the three-run qubit experiment on three chips (ibm_kingston, ibm_phoenix, ibm_pittsburgh): one look after a wait; 3 starts (|0>, halfway, |1>) x 3 waits, raw I/Q on every look; qubit groups of three (ibm_kingston: [[82,139,154],[38,92,96],[25,109,135]]) [§96, §97, §100; parallax/QUBIT_THREE_RUNS_APPROVED_20261001.md].

What was read: ibm_kingston: fading time 255.4 +/- 7.6 us; |1> start after 240 / 300 us 0.497 / 0.398; halfway start after 60 / 240 / 300 us 0.509 / 0.232 / 0.196. ibm_phoenix: fading time 177.1 +/- 5.7 us [§101]. ibm_pittsburgh (opened later): fading time, no earlier look, 269 us [§113].

**2026-10-02 ibm_kingston, ibm_phoenix, ibm_pittsburgh -- qubit_three_runs** (6 jobs: 6/0/0)

What was laid: Runs 2 and 3 of the same experiment on the same three chips: run 2 = start, look, wait, look; run 3 = start, look, wait, look, wait, look, with the two waits in mirrored order (short then long, long then short) [§96, §102, §107].

What was read: Run 2, ibm_kingston, look 2 after 60 / 240 / 300 us, |1> start 0.742 / 0.373 / 0.298, halfway 0.366 / 0.179 / 0.147; fading time from levels 261.6 +/- 7.8 us; from the look-to-look gap 157.2 +/- 17 us. ibm_phoenix: |1> start 0.643 / 0.245 / 0.158; fading time 178.2 +/- 6.4 us; from the gap 121.6 +/- 8.5 us [§105]. Run 3, fading time by 0 / 1 / 2 earlier looks: ibm_kingston 248.7 +/- 7.4 / 265.2 +/- 8.6 / 328.2 +/- 28; ibm_phoenix 182.5 +/- 5.4 / 179.5 +/- 6.2 / 184.2 +/- 16; refit on one window: ibm_kingston 253 +/- 10 / 270 +/- 9 / 274 +/- 15, ibm_phoenix 182 +/- 6 / 180 +/- 7 / 177 +/- 9, ibm_pittsburgh 277 +/- 10 / 288 +/- 11 / 286 +/- 15 [§108, §136]. Level at the long wait, |1> start, 0 / 1 / 2 earlier looks: ibm_kingston 0.302 / 0.302 / 0.261; ibm_phoenix 0.197 / 0.160 / 0.163; ibm_pittsburgh 0.314 / 0.347 / 0.319 [§108, §113]. ibm_pittsburgh run 2, look-to-look gap clock 234 us, level clock 283 us [§113].

**2026-10-02 ibm_boston -- qubit_stone_run** (3 jobs: 3/0/0)

What was laid: The three-run experiment on ibm_boston with waits 105 / 260 / 365 us (short + medium = long), 3 starts, 555 shots, blind qubit draw (seed 20261002), one job per run [parallax/QUBIT_STONE_RUN_BUILD_20261002.md; §111, §112].

What was read: ibm_boston: look-to-look gap clock 245 us, level clock 308 us (run 2); fading time with no earlier look 282 us; level clock by 0 / 1 / 2 earlier looks 278 / 310 / 314 us (widths 7-12, last 23-28); level at the long wait, |1> start, 0 / 1 / 2 earlier looks 0.273 / 0.279 / 0.262; qubit-to-qubit lopsidedness of the |0> start at look 1: 0.39 / 0.38, after waits (run 1) 0.74 / 0.78 / 1.12; remainder rms 0.076; third-look twin difference |0> -0.002, halfway -0.006, |1> +0.013 [§113].

**2026-10-02 ibm_marrakesh -- run5.py** (1 job: 1/0/0)

What was laid: One job on ibm_marrakesh, nine qubits drawn by a written seed, nothing written down before the run. Each circuit: start, look, wait, look; 3 starts (|0>, halfway, |1>) x 4 waits (none, 60, 240, 300 us) x 3 copies of the whole set = 36 circuits of 212 shots [parallax/out/qubit_fifth_run/run5.py; §114].

Reported in Sections 3.1 and 3.2.

**2026-10-02 ibm_pittsburgh -- run6.py** (1 job: 0/0/1)

What was laid: The no-wait arm (start, look, look) on ibm_pittsburgh, the same nine qubits, 3 starts x 3 copies = 9 circuits of 60 shots, fired under a 3 s cap [parallax/out/qubit_fifth_run/run6.py; §115].

What was read: No read on file (job status ERROR).

**2026-10-02 ibm_pittsburgh -- run9.py** (1 job: 1/0/0)

What was laid: The whole run-5 circuit set on ibm_pittsburgh (36 circuits of 212 shots), the same nine qubits [parallax/out/qubit_fifth_run/run9.py].

Reported in Sections 3.1 and 3.2.

**2026-10-02 ibm_kingston -- run7.py** (1 job: 1/0/0)

What was laid: The no-wait arm on ibm_kingston, the nine qubits of its run-1 freeze, 3 starts x 3 copies = 9 circuits of 212 shots [parallax/out/qubit_fifth_run/run7.py].

Reported in Sections 3.1 and 3.2.

**2026-10-02 ibm_kingston, ibm_pittsburgh -- run10.py** (2 jobs: 2/0/0)

What was laid: Copies of run 2's short-wait circuits (start, look, wait 60 us, look for |0>, halfway, |1>), three copies, 195 shots each (585 per start); ibm_pittsburgh and ibm_kingston, each on its own nine qubits [parallax/out/qubit_fifth_run/run10.py; §117].

What was read: Pittsburgh, |1> start, look-2 reading after the short wait, middle qubit of the nine: 0.797 (previous night), 0.728 (09:13), 0.797 (09:18); rms change over the nine qubits 0.157 (night to morning) and 0.164 (09:13 to 09:18). Kingston middle qubit 0.738 then 0.745, rms 0.141. Halfway start follows at about half size (rms 0.07-0.09); |0> start rms 0.01-0.02 [§117; parallax/out/qubit_fifth_run/data/reads/short_wait_across_time.txt].

Note: Table 1 of the paper lists this run; the paper reports no read from it.

**2026-10-02 ibm_pittsburgh -- jump.py** (8 jobs: 8/0/0)

What was laid: ibm_pittsburgh, every qubit: one job of 10 circuits x 400 shots fired 8 times, 4 minutes apart (start, look, wait none / 60 / 240 / 300 us, look, for |1> and halfway; |0> at none and 300 us) [parallax/out/qubit_fifth_run/jump.py; §118].

Reported in Section 3.1.

**2026-10-02 ibm_pittsburgh -- tail.py** (3 jobs: 3/0/0)

What was laid: ibm_pittsburgh, every qubit, 3 reads 4 minutes apart, 11 circuits x 400 shots: start, look, wait, look at waits none / 6.7 / 20 / 60 / 300 us for |1> and halfway, |0> at none [parallax/out/qubit_fifth_run/tail.py].

Reported in Sections 3.1 and 3.2.

**2026-10-02 ibm_pittsburgh -- lone.py** (1 job: 1/0/0)

What was laid: ibm_pittsburgh, every qubit, one read of 11 circuits x 400 shots: start, wait, one look, at the waits of the tail run, with no first look [parallax/out/qubit_fifth_run/lone.py].

Reported in Section 3.1.

**2026-10-02 ibm_pittsburgh -- half.py** (3 jobs: 3/0/0)

What was laid: ibm_pittsburgh, every qubit, 3 reads, 14 circuits x 360 shots: start, wait, one look, with the in-between state made by one half-push, or by a full push then a half-push, ON by one full push or by two half-pushes, at waits none / 6.7 / 20 us, and |0> by nothing or by two full pushes [parallax/out/qubit_fifth_run/half.py; §125].

What was read: Maker's stated look length read at 11:02: 2.180 us on all 156 qubits. Middle qubit, three reads, what one look keeps after 6.7 us / 20 us: in-between by one half-push 0.953 0.943 0.950 / 0.890 0.881 0.894; by full push then half-push 0.996 0.985 0.967 / 0.923 0.929 0.923; |1> by one full push 0.970 0.967 0.966 / 0.919 0.919 0.918; |1> by two half-pushes 0.968 0.969 0.971 / 0.919 0.918 0.918. Two-half-push |1> minus one-push |1>: +0.0006 +/- 0.0020 / +0.0006 +/- 0.0006. Far-side in-between minus |1>: +0.025 +/- 0.006 / +0.020 +/- 0.004; one-half-push in-between minus |1>: -0.016 +/- 0.003 / -0.027 +/- 0.002 [§125; parallax/out/qubit_fifth_run/data/reads/half_push.txt].

**2026-10-02 ibm_pittsburgh -- sides.py** (1 job: 1/0/0)

What was laid: ibm_pittsburgh, every qubit, one read of 19 circuits x 360 shots: one half-push with the frame turned 0 / 120 / 240 / 180 degrees, a full push then a half-push, |1>, each at none / 6.7 / 20 us, and |0> [parallax/out/qubit_fifth_run/sides.py; §128].

What was read: Kept minus |1>'s kept at 6.7 / 20 us: half-push frame turned 0 deg -0.010 / +0.003; 120 deg -0.012 / -0.017; 240 deg -0.004 / -0.010; 180 deg -0.020 / -0.016; full push then half-push +0.013 / +0.015. Far-side start minus the 180-degree start +0.039 +/- 0.011 (6.7 us), +0.018 +/- 0.011 (20 us); far-side start higher at no wait by 0.033 +/- 0.004 (0.528 against 0.495) [§129; parallax/out/qubit_fifth_run/data/reads/sides.txt].

**2026-10-02 ibm_pittsburgh -- turns.py** (1 job: 1/0/0)

What was laid: ibm_pittsburgh, every qubit, 20 circuits x 330 shots per read (reads 2 and 3 pulled before firing): start, wait, one look; the in-between reached by 1, 3, 5 and 9 quarter-turns, |1> by 2 and 6, |0> by 0 and 4, at waits none / 6.7 / 20 us [parallax/out/qubit_fifth_run/turns.py; §131].

What was read: One read. Level at none / 6.7 / 20 us (kept minus |1>'s kept at 6.7 / 20 us in brackets): in-between by 1 quarter-turn 0.497 / 0.476 / 0.444 (-0.009 / -0.018); by 3 0.527 / 0.517 / 0.491 (+0.026 / +0.020); by 5 0.465 / 0.438 / 0.417 (-0.014 / -0.012); by 9 0.441 / 0.422 / 0.400 (+0.000 / -0.005); |1> by 6 0.998 (-0.005 / -0.001); |0> by 4 +0.003 [§131].

**2026-10-02 ibm_pittsburgh -- hold.py** (3 jobs: 3/0/0)

What was laid: ibm_pittsburgh, every qubit, 3 reads, 11 circuits x 330 shots: start |1>, 300 us of laid time, last look; inside the 300 us nothing, 1 / 3 / 9 looks, or 1 / 3 / 9 pushes to the far side; plus rulers (|0> with nine looks, |0> with ten pushes, lone looks of |0> and |1>) [parallax/out/qubit_fifth_run/hold.py].

Reported in Sections 3.1, 3.2 and 3.3.

**2026-10-02 ibm_pittsburgh -- witness.py** (1 job: 1/0/0)

What was laid: ibm_pittsburgh, every qubit, one job of 12 circuits x 300 shots: emitters (39, no two within two links) told |1> for 0 / 20 / 40 / 60 us of a 60 us window; every qubit wired to an emitter held as a clock (86), read on two axes [parallax/out/qubit_fifth_run/witness.py].

Reported in Section 3.4.

**2026-10-02 ibm_pittsburgh -- push.py** (3 jobs: 3/0/0)

What was laid: ibm_pittsburgh, every qubit, 3 reads of 14 circuits x 400 shots, one look at the end: starts |0>, |1>, halfway; pushes 0 / 2 back-to-back / 10 back-to-back / 10 spread (one every 30 us over 300 us); plus |1> and |0> left idle for 300 us (14 circuits in all) [parallax/out/qubit_fifth_run/push.py].

Reported in Sections 3.1 and 3.3.

**2026-10-02 ibm_pittsburgh -- looktime.py** (3 jobs: 3/0/0)

What was laid: ibm_pittsburgh, every qubit, 3 reads of 14 circuits x 400 shots: emitters held |1>, every wired qubit a clock, far qubits looked at 3 or 9 times back-to-back inside the clocks' window; window arms 0 / 30 / 60 / 120 us [parallax/out/qubit_fifth_run/looktime.py].

Reported in Sections 3.2 and 3.4.

**2026-10-02 ibm_pittsburgh -- giveback.py** (3 jobs: 3/0/0)

What was laid: ibm_pittsburgh, every qubit, 3 reads of 6 circuits x 1000 shots in one job: |1>, 300 us of laid time, last look, with no look, or one look at 0 / 150 / 270 us; frame circuits [parallax/out/qubit_fifth_run/giveback.py].

Reported in Section 3.2.

**2026-10-02 ibm_marrakesh -- band.py** (24 jobs: 24/0/0)

What was laid: ibm_marrakesh, the 78 qubits of the 28 Sep echo run: each shot a look, an X gate or none, a look; E0 and E1 as separate jobs, 4 gaps (20 / 50 / 100 / 2000 us) x 2 = 8 jobs per read, 3 reads, 1500 shots [parallax/out/qubit_fifth_run/band.py; §137].

What was read: 73-74 of 78 qubits readable; clock A resolves on 51 qubits, clock B on 25-33. Readout-level band 0.62-0.65 (28 Sep values R^2 0.23 / 0.28 / 0.32 / 0.43): read 1 0.02-0.03, read 2 0.00-0.02, read 3 0.00-0.11. Readout-level band 0.40-0.54 (28 Sep 0.33, 0.31 / 0.26 / 0.27, 0.26): read 1 0.00-0.06, read 2 0.00-0.02, read 3 0.00-0.19. Read 3 at levels 0.67-0.68: 0.37, 0.34. Clock A middle 44 us on 28 Sep against 57 / 80 / 64 us on 2 Oct [§140; parallax/out/qubit_fifth_run/data/reads/band.txt].

**2026-10-02 ibm_pittsburgh -- noname.py** (1 job: 1/0/0)

What was laid: ibm_pittsburgh, every qubit, one read of 21 circuits x 216 shots (two more reads were planned): ten pushes with OFF / ON stretch lengths 30/30, 10/30, 90/30, 30/10, 30/90, one more push at the end, 2 and 6 pushes, the |1> start, rulers at 10 / 30 / 90 / 300 us, and emitter-and-spectator arms with frame-holding pulses [parallax/out/qubit_fifth_run/noname.py; §145].

Reported in Sections 3.1, 3.3 and 3.4.

**2026-10-02 ibm_kingston, ibm_marrakesh -- pushrep.py** (2 jobs: 2/0/0)

What was laid: The push run's 14 circuits x 400 shots, circuit for circuit, on ibm_kingston and ibm_marrakesh, one read each (two more per chip were planned) [parallax/out/qubit_fifth_run/pushrep.py; §151].

Reported in Sections 3.1 and 3.3.

**2026-10-04 ibm_kingston, ibm_marrakesh -- time_wide.py** (6 jobs: 6/0/0)

What was laid: ibm_marrakesh and ibm_kingston, every qubit, 3 reads each of 50 circuits x 300 shots: starts |0>, |1>, halfway; pushes 0 / 2 / 10 back-to-back; 10 pushes spread with spacing 5 to 150 us; in the same job the |1> decay at 30 / 100 / 300 / 600 us in three copies, idle |0> at 300 / 600 us and an echo [parallax/out/qubit_fifth_run/time_wide.py; §182].

Reported in Section 3.1.

**2026-10-04 ibm_marrakesh -- look_wide.py** (3 jobs: 3/0/0)

What was laid: ibm_marrakesh, 3 reads of 37 circuits x 400 shots: clocks held while the far qubits are looked at 1 / 2 / 3 / 4 / 6 / 9 times and over laid windows of 0 to 240 us; looked-at qubits' own fading [parallax/out/qubit_fifth_run/look_wide.py; §184].

Reported in Section 3.2.

**2026-10-04 ibm_marrakesh -- count_wide.py** (3 jobs: 3/0/0)

What was laid: ibm_marrakesh, 3 reads of 34 circuits x 300 shots: free clocks (no emitter driven) through 1 to 32 looks at the far qubits and laid windows of 0 to 120 us; distance to the nearest looked-at qubit read afterwards [parallax/out/qubit_fifth_run/count_wide.py; §186].

Reported in Section 3.4.

**2026-10-04 ibm_kingston -- look_wide_kingston.py** (3 jobs: 3/0/0)

What was laid: The look_wide circuits on ibm_kingston, 3 reads [parallax/out/qubit_fifth_run/look_wide_kingston.py; §188].

Reported in Section 3.2.

**2026-10-04 ibm_kingston -- count_wide_kingston.py** (3 jobs: 3/0/0)

What was laid: The count_wide circuits on ibm_kingston, 3 reads [parallax/out/qubit_fifth_run/count_wide_kingston.py; §188].

Reported in Section 3.4.

**2026-10-04 ibm_pittsburgh -- look_wide_pittsburgh.py** (3 jobs: 3/0/0)

What was laid: The look_wide circuits on ibm_pittsburgh, 3 reads [parallax/out/qubit_fifth_run/look_wide_pittsburgh.py; §190, §228].

Reported in Section 3.2.

**2026-10-04 ibm_pittsburgh -- time_wide_pittsburgh.py** (3 jobs: 3/0/0)

What was laid: The time_wide circuits on ibm_pittsburgh, 3 reads [parallax/out/qubit_fifth_run/time_wide_pittsburgh.py; §190, §229].

Reported in Section 3.1.

**2026-10-04 ibm_fez -- five_slope.py** (1 job: 1/0/0)

What was laid: ibm_fez, every qubit, one read of 8 circuits x 800 shots: start |0>, 2 / 6 / 10 pushes with a push after every 30 us; |1> left 30 / 90 / 300 us; frame [parallax/out/qubit_fifth_run/five_slope.py; §202].

Reported in Sections 3.1 and 3.7.

**2026-10-04 ibm_kingston -- five_slope_kingston.py** (1 job: 0/0/1)

What was laid: The five_slope circuits on ibm_kingston, first copy, run 391 [parallax/out/qubit_fifth_run/five_slope_kingston.py; §228].

What was read: No read on file (job status ERROR).

**2026-10-04 ibm_pittsburgh -- count_wide_pittsburgh.py** (3 jobs: 3/0/0)

What was laid: The count_wide circuits on ibm_pittsburgh, 3 reads [parallax/out/qubit_fifth_run/count_wide_pittsburgh.py; §228, §230].

Reported in Section 3.4.

**2026-10-04 ibm_kingston -- five_slope_kingston2.py** (1 job: 1/0/0)

What was laid: The five_slope circuits on ibm_kingston, second copy, run 392, with a 28 s cap [parallax/out/qubit_fifth_run/five_slope_kingston2.py; §235].

Reported in Sections 3.1 and 3.7.

**2026-10-04 ibm_fez -- time_wide_fez.py** (3 jobs: 3/0/0)

What was laid: The time_wide circuits on ibm_fez, 3 reads (runs 401-403), call text hashed before firing [parallax/out/qubit_fifth_run/time_wide_fez.py; §238].

Reported in Sections 3.1 and 3.7.

**2026-10-04 ibm_fez -- look_wide_fez.py** (3 jobs: 3/0/0)

What was laid: The look_wide circuits on ibm_fez, 3 reads (runs 411-413), call text hashed before firing [parallax/out/qubit_fifth_run/look_wide_fez.py; §238].

Reported in Sections 3.2 and 3.7.

**2026-10-04 ibm_fez -- count_wide_fez.py** (3 jobs: 3/0/0)

What was laid: The count_wide circuits on ibm_fez, 3 reads (runs 421-423), call text hashed before firing [parallax/out/qubit_fifth_run/count_wide_fez.py; §238].

Reported in Sections 3.4 and 3.7.

**2026-10-04 ibm_boston -- look_wide_boston.py** (3 jobs: 3/0/0)

What was laid: The look_wide circuits on ibm_boston, 3 reads (runs 431-433), call text hashed before the data existed [parallax/out/qubit_fifth_run/look_wide_boston.py; §240, §241].

Reported in Section 3.7.

Note: The earlier version of this appendix listed this family as 1 job, QUEUED (run 431). The rebuilt index lists runs 431-433, all DONE (runs 432 and 433 created 22:36 and 22:37 on 4 October).

**2026-10-04 ibm_boston -- five_slope_boston.py** (1 job: 1/0/0)

What was laid: The five_slope circuits on ibm_boston, every qubit, one read (run 441) of 8 circuits x 800 shots: start |0>, 2 / 6 / 10 pushes with a push after every 30 us; |1> left 30 / 90 / 300 us; frame; call text hashed before firing [parallax/out/qubit_fifth_run/five_slope_boston.py; §258].

Reported in Section 3.7.

**2026-10-04 Cepheus-1-108Q -- tune** (8 tasks: 8/0/0)

What was laid: Re-tune of the 1-2 swap on all 108 qubits, 8 tasks of 1000 shots [standoff/rigetti_time.py; §192-§193].

Reported in Section 3.6.

**2026-10-04 Cepheus-1-108Q -- read1** (58 tasks: 58/0/0)

What was laid: Batch 1 of the time run on every qubit in parallel: starts 0 / 1 / halfway, ten X pushes after intervals of 0 / 1 / 3 / 8 / 20 us, each qubit's decay read at 3 / 10 / 30 us in three copies, each arm read plain and swap-then-flip with the batch's own 8-sequence readout calibration; 58 tasks [standoff/rigetti_time.py; §192-§193].

Reported in Section 3.6.

**2026-10-04 Cepheus-1-108Q -- read2** (58 tasks: 58/0/0)

What was laid: Batch 2 of the same time run, 188 s after batch 1; 58 tasks [standoff/rigetti_time.py; §194].

Reported in Section 3.6.

**2026-10-04 Cepheus-1-108Q -- read3** (50 tasks: 50/0/0)

What was laid: Batch 3 of the same run with the witness layout: 7 emitters at least 5 links apart, 100 free clocks (22 / 40 / 38 at 1 / 2 / 3+ links), emitters held |1> for trains of 5 / 15 / 40 / 100 us from |0> and from |1>, clock references, an emitter ruler; 50 tasks [standoff/rigetti_time.py; §194].

What was read: Emitters' laid |1> time 5 / 15 / 40 / 100 us; booked from their own decay (25 us) 4.9 / 14.4 / 37.4 / 87.5 us from |0> and 5.1 / 15.5 / 41.1 / 96.8 us from |1>; end state on level 2 1.3-2.7%; clocks' readings of that time spread -50 to +70 us between quartiles. Clock hand kept 0.67 at 3 us and 0.27 at 10 us. Pull per us with emitters held in |1>: 0.059 (1 link), 0.028 (2 links), 0.029 falling to 0.011 (3+ links, 3 to 30 us) [§194; standoff/time20261004/read3_witness_raw.txt].

**2026-10-04 Cepheus-1-108Q -- q0_last** (8 tasks: 8/0/0)

What was laid: q0 at rest, in |1> and in |2>, watched by every other qubit as a clock over one 2 us window; 8 tasks of 900 shots, the last tasks under the day cap [standoff/rigetti_q0_last.py; §195].

What was read: Plain read of q0: rest 0.046, |1> 0.861, |2> 0.903. Clock turn over 2 us, q0 in |1> / in |2> minus at rest (deg/us): q9 +0.31 +/- 1.22 / -34.94 +/- 2.20; q1 -7.48 +/- 2.18 / -20.95 +/- 2.24; q10 -2.69 +/- 2.96 / +0.78 +/- 2.74; 101 clocks at 3+ links, median with q0 in |2> -0.62 (quartiles -2.73, +1.57) [§195; standoff/time20261004/q0_last_raw.txt].

**2026-10-04 Cepheus-1-108Q -- triA** (40 tasks: 40/0/0)

What was laid: q0 at rest / |1> / |2> for 0.5 to 6 us, every other qubit a clock, q0's own |2> population read in the same batch; 40 tasks [standoff/rigetti_triangles.py; §204].

Reported in Section 3.6.

**2026-10-04 Cepheus-1-108Q -- triB** (42 tasks: 42/0/0)

What was laid: The 7 emitters pushed ten times back to back, their 22 neighbours at rest, pushed in step, or held as clocks, interleaved, three rounds 3 minutes apart, each with its own readout calibration; 42 tasks [standoff/rigetti_triangles.py; §204].

Reported in Section 3.6.

**2026-10-04 Cepheus-1-108Q -- triC** (34 tasks: 34/0/0)

What was laid: The 7 emitters' |1> time during a ten-push train from |0> with L = 5 / 10 / 20 us (laid 2.50 / 5.00 / 10.00 us), echoed clocks, own-decay booking; 34 tasks [standoff/rigetti_triangle_c.py; §207].

What was read: Booked from own decay (0.881 / 0.696 / 0.568 / 0.390 at 1 / 5 / 10 / 20 us): 2.44 / 4.82 / 9.54 us; end state level 1 0.181 / 0.190 / 0.194, level 2 0.020 / 0.021 / 0.027. Clocks' medians at 1 / 2 / 3+ links: +2.75 / +1.56 / +1.82 us (L 5), +3.61 / +7.53 / +8.00 us (L 10), +10.77 / +6.91 / +6.23 us (L 20), quartiles spanning +/-10 to +/-30 us; pull from a |1> emitter 0.2-1.5 deg/us; hand kept 0.10-0.48 at L 5 [§207; standoff/time20261004/triC_raw.txt].

**2026-10-04 Cepheus-1-108Q -- triD** (50 tasks: 50/0/0)

What was laid: The push train on the 1-2 pair: 7 emitters pushed 1-2 ten times with a push after every 0.1 / 0.2 / 0.4 us, starts |1>, |2>, |0>, references held |1> and |2>, own-decay rulers; 50 tasks [standoff/rigetti_triangle_d.py; §208].

Reported in Section 3.6.

**2026-10-04 Cepheus-1-108Q -- triE** (86 tasks: 86/0/0)

What was laid: N = 4 / 10 / 20 pushes across L = 1 / 2 / 4 us on the 1-2 pair, starts |1>, |2>, |0>, references held; 86 tasks [standoff/rigetti_triangle_e.py; §210].

Reported in Section 3.6.

**2026-10-04 Cepheus-1-108Q -- triF** (132 tasks: 132/0/0)

What was laid: The 7 emitters held at rest / |1> / |2> for 0.25 to 6 us with every other qubit a clock, three rounds about 3 minutes apart, each with its own readout calibration; 132 tasks [standoff/rigetti_triangle_f.py; §212].

Reported in Section 3.6.

**2026-10-04 Cepheus-1-108Q -- triG** (84 tasks: 84/0/0)

What was laid: Emitters held |1> or |2> for 0.5 / 2 / 4 us with the other qubits in five states (rest; halfway then turned back; the copy used in triF; |1> throughout; |1> at readout only); populations solved with three readout models; 84 tasks [standoff/rigetti_triangle_g.py; §214].

Reported in Section 3.6.

**2026-10-04 Cepheus-1-108Q -- triH** (30 tasks: 30/0/0)

What was laid: Clocks halfway for 0.5 / 2 / 4 us with the emitters at rest, emitters put in |0> / |1> / |2> at readout; the day's pairing of read axes on the held-|2> arm against both-plain and both-swap-then-flip; 30 tasks [standoff/rigetti_triangle_h.py; §216].

Reported in Section 3.6.

**2026-10-04 Cepheus-1-108Q -- sealA** (130 tasks: 130/0/0)

What was laid: After the vendor's recalibration (2026-10-04 18:02Z): emitters held in |2> for 2 / 3.5 / 4 / 4.5 / 6 us, other qubits at rest / the triF copy / |1> at readout only, three readout models, three rounds; 130 tasks [standoff/rigetti_seal.py; §219].

Reported in Section 3.6.

**2026-10-04 Cepheus-1-108Q -- sealB** (50 tasks: 50/0/0)

What was laid: Triangle D's circuits again after the recalibration; 50 tasks [standoff/rigetti_seal.py; §219].

Reported in Section 3.6.

**2026-10-04 Cepheus-1-108Q -- lookT** (18 tasks: 18/0/0)

What was laid: Our own look on Cepheus, step 1: a constant 1 us tone on each of the 7 emitters' readout frames at amplitudes 0 / 0.03 / 0.06 / 0.12 / 0.25 / 0.5, then 0.5 us to empty; emitters halfway (two hands) and in |1>; every other qubit halfway; 18 tasks [standoff/rigetti_look_tune.py; §224].

What was read: Looked-at qubits' coherence kept (mean of 7) at the six amplitudes: 1 / 0.30 / 0.36 / 0.92 / 1.99 / 2.09; |1> read-1 0.878 / 0.850 / 0.831 / 0.752 / 0.946 / 0.967. Clocks at 1 / 2 / 3+ links: kept 0.975-0.996 and turn -1.9 to +0.7 deg at 0.03-0.06; turn -15.4 / -9.7 / -4.3 deg at 0.12; turn -33 to -39 / -31 to -36 / -15 to -22 deg at 0.25-0.5 [§225; standoff/time20261004/lookT_raw.txt].

**2026-10-04 Cepheus-1-108Q -- lookTri** (84 tasks: 42/42/0)

What was laid: The look on Cepheus before the fence: the 1 us tone on the 7 emitters' readout frames at strengths 0.03 / 0.045 / 0.06, 1-6 looks, delays 0-9 us, 100 clocks with frames at +100 kHz, emitters in |1>; 42 tasks x 1500 shots. The same 42 circuits were sent twice [standoff/rigetti_look_triangle.py (backup .bak-20261004-preFence); §227, §228]. The index lists 42 completed and 42 cancelled.

What was read: Clocks turn -39.4 deg/us over the delays (moved frame 36.0). Clocks' time per look 0.484 / 0.508 / 0.500 / 0.497 us (strengths 0.03 / 0.045 / 0.06, wrapped and unwrapped). Looked-at qubits' own fall per 1.5 us look 1.441 / 1.501 / 1.143 us of plain delay (over laid 1.5 us: 0.961 / 1.001 / 0.762) [§231; standoff/time20261004/lookTri_raw.txt].

Note: Section 3.2 mentions this run (the missing fence, §231) and gives no numbers from it.

**2026-10-04 Cepheus-1-108Q -- two** (148 tasks: 74/74/0)

What was laid: A call hashed before firing: 107 qubits from |0>, ten pushes after intervals of 1 / 2.618 / 6.854 / 17.944 / 46.979 us, each against its own decay read three times in the same batch, plus back-to-back arms; 74 tasks. The same 74 circuits were sent twice [standoff/rigetti_two_call.py; §228, §232]. The index lists 74 completed and 74 cancelled.

Reported in Sections 3.6 and 3.7.

**2026-10-04 Cepheus-1-108Q -- lookTri2** (52 tasks: 52/0/0)

What was laid: The look on Cepheus with the fence: one pulse gate on all 107 qubits (barrier, the 1 us tone on the 7 emitters' readout frames, 1 us delay on every other frame, barrier), then the 0.5 us wait; strength 0.0 added as the timing check; 52 tasks of 1500 shots [standoff/rigetti_look_triangle.py; §233].

Reported in Section 3.2.


**2026-10-05 ibm_boston -- count_wide_boston.py** (3 jobs: 3/0/0)

What was laid: ibm_boston, every qubit, 3 reads (runs 451-453) of 34 circuits x 300 shots: free clocks (no emitter driven) through 1 to 32 looks at the far qubits and laid windows of 0 to 120 us; distance to the nearest looked-at qubit read afterwards; call text hashed before firing [parallax/out/qubit_fifth_run/count_wide_boston.py; §258].

What was read: Hand kept through 32 looks over hand kept through the same laid time (mean of 3 reads), at 1 / 2 / 3+ links: 1.000 / 0.901 / 0.991. Laid time per look over the maker's look length on ibm_boston: 0.82-0.85 [§258, §262; parallax/out/qubit_fifth_run/data/reads/three_looks_minus_time_boston_20261005.txt].

In the paper: Partly reported in Section 3.7 (the 32-look ratio); the other reads are given here.

**2026-10-05 ibm_boston -- time_wide_boston.py** (3 jobs: 3/0/0)

What was laid: ibm_boston, every qubit, 3 reads (runs 461-463) of 50 circuits x 300 shots: starts |0>, |1>, halfway; pushes 0 / 2 / 10 back-to-back; 10 pushes spread with spacing 5 to 150 us; in the same job the |1> decay at 30 / 100 / 300 / 600 us in three copies, idle |0> at 300 / 600 us and an echo; call text hashed before the data existed [parallax/out/qubit_fifth_run/time_wide_boston.py; §259].

Reported in Section 3.7.

**2026-10-05 ibm_boston -- time_wide_boston2.py** (3 jobs: 3/0/0)

What was laid: The time_wide circuits on ibm_boston again, a second set of 3 reads (runs 471-473); no call written for it [parallax/out/qubit_fifth_run/time_wide_boston2.py; §265].

What was read: Ladder pace (rungs per e-fold of spacing, against one exponential) in firing order over the six jobs of runs 461-463 and 471-473: 1.314 / 1.268 / 1.088 / 1.110 / 0.940 / 1.081 (02:10 to 08:47 EDT); the chip's own decay time 272-282 us across the six; mean of the last four 1.055 (spread 0.08) [§265; parallax/out/qubit_fifth_run/data/reads/time_wide_boston_reads456_20261005.txt].

Not reported in the paper body.

Note: The freeze record for these runs hashes time_wide_boston.py, not the script that fired; see the provenance note.

**2026-10-05 ibm_phoenix -- look_wide_phoenix.py** (3 jobs: 3/0/0)

What was laid: The look_wide circuits on ibm_phoenix (120 qubits), every qubit, 3 reads (runs 541-543) of 37 circuits x 400 shots; call text hashed before any run [parallax/out/qubit_fifth_run/look_wide_phoenix.py; §261].

Reported in Section 3.7.

Note: The freeze record for these runs hashes look_wide_boston.py, not the script that fired; see the provenance note.

**2026-10-05 ibm_phoenix -- five_slope_phoenix.py** (1 job: 1/0/0)

What was laid: The five_slope circuits on ibm_phoenix, every qubit, one read (run 531) of 8 circuits x 800 shots: start |0>, 2 / 6 / 10 pushes with a push after every 30 us; |1> left 30 / 90 / 300 us; frame; call text hashed before any run [parallax/out/qubit_fifth_run/five_slope_phoenix.py; §261].

Reported in Section 3.7.

Note: The freeze record for this run hashes five_slope_boston.py, not the script that fired; see the provenance note.

**2026-10-05 ibm_phoenix -- count_wide_phoenix.py** (3 jobs: 3/0/0)

What was laid: The count_wide circuits on ibm_phoenix, every qubit, 3 reads (runs 551-553) of 34 circuits x 300 shots: free clocks through 1 to 32 looks at the far qubits and laid windows of 0 to 120 us; distance to the nearest looked-at qubit read afterwards; call text hashed before any run [parallax/out/qubit_fifth_run/count_wide_phoenix.py; §261].

What was read: Free clocks' hand kept 0.07-0.23 by 12-16 looks. Hand kept through 32 looks over hand kept through the same laid time, at 1 / 2 / 3+ links: 1.077 / 1.131 / 0.926; up to 8 looks, 1.03-1.15 in all three classes. Hand e-fold time 12-18 us; clocks' turn 6.8 / 13.2 / 10.2 deg/us; laid time per look 1.46-1.51 us, which is 0.754 / 0.754 / 0.777 of the maker's 1.94 us. Hand kept (1 link): 0.113 at 30 us laid and 0.178 at 60 us (+5.9 sd), 0.107 at 24 looks and 0.188 at 32 looks (+7.6 sd); 3+ links 0.077 and 0.214 (+6.4 sd), 0.077 and 0.191 (+5.5 sd); 2 links 0.085 and 0.112 from 24 to 32 looks (+2.3 sd) [§261-§263; parallax/out/qubit_fifth_run/data/reads/three_looks_minus_time_phoenix_20261005.txt].

In the paper: Partly reported in Section 3.7 (the 32-look call); the other reads are given here.

Note: The freeze record for these runs hashes count_wide_boston.py, not the script that fired; see the provenance note.

**2026-10-05 ibm_phoenix -- ripple_phoenix.py** (2 jobs: 2/0/0)

What was laid: ibm_phoenix, every qubit, 2 reads (runs 561-562) of the count_wide circuits with dense laid windows (0 to 100 us every 10 us, then 120 / 140 / 160 us) and looks 1 / 4 / 8 / 16 / 24 / 28 / 32, 300 shots; no call written [parallax/out/qubit_fifth_run/ripple_phoenix.py; §264].

What was read: Free clocks' hand, per clock, kept against laid time, reads 1 / 2: 1 link 0.123 / 0.122 at 30 us, 0.210 / 0.202 at 60 us, 0.208 / 0.223 at 70 us, 0.100 / 0.090 at 100 us; 2 links 0.079 / 0.076 at 30 us, 0.131 / 0.101 at 60 us, 0.124 / 0.155 at 70 us, 0.084 / 0.087 at 100 us; 3+ links 0.104 / 0.079 at 30 us, 0.212 / 0.245 at 60 us, 0.216 / 0.252 at 70 us, 0.090 / 0.070 at 100 us; widths about 0.012-0.026. The reader marks rises at 60 us (1 link, both reads), 60 / 70 us (2 links), 50 / 60 us (3+ links) and at 120 us in read 2 (1 link, 3+ links) [§264; parallax/out/qubit_fifth_run/data/reads/ripple_phoenix_20261005.txt].

Not reported in the paper body.

Note: The freeze record for these runs hashes count_wide_boston.py, not the script that fired; see the provenance note.

**2026-10-05 ibm_boston -- time_wide_boston3.py** (5 jobs: 5/0/0)

What was laid: The time_wide circuits on ibm_boston, 5 reads back to back (runs 481-485); no call written. Created 08:32 to 09:24 EDT; run 473 (08:47) was created between runs 481 and 482 [parallax/out/qubit_fifth_run/time_wide_boston3.py; §267].

What was read: Ladder pace (rungs per e-fold of spacing, against one exponential) for runs 481-485: 1.054 / 1.055 / 1.071 / 1.045 / 1.281. Across the eleven Boston jobs, a geometric settle fits with chi2 10.0 (3 parameters; flat 17.3), each step 0.42 of the last, settling at 1.056; a damped ring fits with chi2 7.9 (2 more parameters) [§267, §268; parallax/out/qubit_fifth_run/data/reads/time_wide_boston_reads789_20261005.txt].

Not reported in the paper body.

Note: The freeze record for these runs hashes time_wide_boston.py, not the script that fired; see the provenance note.

**2026-10-05 ibm_phoenix -- ripple2_phoenix.py** (2 jobs: 2/0/0)

What was laid: ibm_phoenix, every qubit, 2 reads (runs 571-572) of the count_wide circuits with laid windows 0 / 10 / 30 / 60 / 90 / 100 to 160 every 10 us / 180 / 200 / 220 / 240 us and looks 1 / 8 / 16 / 32, 300 shots; no call written [parallax/out/qubit_fifth_run/ripple2_phoenix.py; §267].

What was read: Free clocks' hand kept at 60 us laid, reads 1 / 2: 1 link 0.181 / 0.204, 2 links 0.109 / 0.109, 3+ links 0.137 / 0.178; past 100 us 0.06-0.10 in every class, as recorded. The reader marks a rise at 60 us in 5 of 6 class-reads, and single later rises at 120 us (2 links, read 2) and 180 us (3+ links, read 1). Over the four dense reads (runs 561-562, 571-572; 21 laid times to 240 us), a damped beat fits with chi2 102 against 438 for a plain decay (1 link), 92 against 228 (2 links), 215 against 434 (3+ links); revival every 62-73 us, damping 22-38 us; the fitted second revival 0.003-0.021 against a floor of 0.08-0.09 [§267, §268; parallax/out/qubit_fifth_run/data/reads/ripple2_phoenix_20261005.txt].

Not reported in the paper body.

Note: The freeze record for these runs hashes count_wide_boston.py, not the script that fired; see the provenance note.

**2026-10-05 ibm_pittsburgh -- look_wide_pittsburgh_oct5.py** (1 job: 1/0/0)

What was laid: The look_wide circuits on ibm_pittsburgh, one read (run 511) after that day's recalibration, 37 circuits x 400 shots; the maker-look and time-leg reads, read against two calls hashed before the data [parallax/out/qubit_fifth_run/look_wide_pittsburgh_oct5.py; §269].

Reported in Section 3.7.

Note: The freeze record for this run hashes look_wide_pittsburgh.py, not the script that fired; see the provenance note.

**2026-10-05 Cepheus-1-108Q -- sealA** (650 tasks: 650/0/0)

What was laid: Step A of the seal circuits again, unchanged, after the vendor's recalibration of 2026-10-05 04:02Z (the chip recalibrates every 30 minutes: 04:02, 04:32, 05:02, 05:32Z): five sets of 130 tasks, the first created from 04:06Z (day 2's own set), four more from 05:00Z to 05:41Z by the riding script, one set after another. Each set: emitters held in |2> for 2 / 3.5 / 4 / 4.5 / 6 us, the other qubits at rest / the triF copy / |1> at readout only, three readout models, three rounds [standoff/rigetti_seal.py; standoff/ride_sealA.sh; §256, §260].

What was read: The four later sets, emitters' |2> after 4 us with the others half-way, em_rest model, rounds then set mean: 0.6129 / 0.6261 / 0.6422, 0.6270; 0.6473 / 0.6449 / 0.6597, 0.6506; 0.6090 / 0.6433 / 0.6016, 0.6180; 0.6602 / 0.6372 / 0.6289, 0.6421. Shared-model set means 0.6389 / 0.6506 / 0.6279 / 0.6510; em_one set means 0.6900 / 0.6912 / 0.6545 / 0.6699. Over the 18 rounds of day 1 and the five day-2 sets: 0.6016 to 0.6602, mean 0.6324. Two sets on the 05:02Z calibration, 11 minutes apart, read 0.651 and 0.618 [§260; standoff/time20261004/sealA_band_all_sets_20261005.txt].

In the paper: Partly reported in Section 3.7 (the first set of 130 tasks, the day-2 call); the four later sets are given here.

**2026-10-05 Cepheus-1-108Q -- drift_r001 to drift_r022 (22 rounds)** (660 tasks: 660/0/0)

What was laid: The drift probe: 22 rounds of 30 tasks (42,000 shots a round), one round about every 6 minutes from 10:58Z to 13:04Z, 2 to 26 minutes after the vendor's recalibrations (five calibrations, 10:32 to 13:02Z); no outcome written beforehand. Each round re-reads every corner of the seal's 4-us row: the three readout rulers (shared, 8 sequences; emitters-only with the others at rest and in |1>, 16 sequences; 1500 shots each) and the emitters held in |2> for 4 us with the other qubits at rest / half-way (the triF copy) / |1> at readout, two arms each, 1000 shots; the round's send time and the chip's calibration stamp are written with it [standoff/rigetti_drift_probe.py; standoff/ride_drift.sh; §266].

What was read: Emitters' |2> after 4 us with the others half-way, em_rest model, rounds 1 to 22 in one line: 0.6409 / 0.6322 / 0.6302 / 0.6174 / 0.6374 / 0.6330 / 0.6103 / 0.6303 / 0.6445 / 0.6308 / 0.6158 / 0.6012 / 0.6139 / 0.6251 / 0.5919 / 0.5978 / 0.6153 / 0.6122 / 0.6195 / 0.6219 / 0.6124 / 0.6072. By minutes since calibration, +2 / +8 / +14 / +20 / +26: 0.6132 / 0.6217 / 0.6266 / 0.6205 / 0.6200. All 22 rounds: 0.6201, spread 0.014, +0.3 % from 0.6180; 8 of 22 rounds within 1 % of 0.6180. Rest witness 0.66-0.68 and |1>-at-readout witness 0.56-0.57 by minutes since calibration [§266; standoff/time20261004/drift_rows_20261005.txt].

Not reported in the paper body.
