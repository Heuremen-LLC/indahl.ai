# NOTHING SWEEP -- quantum hardware data 2026-09-24 .. 09-27

Written 2026-09-29 ~02:30Z by Bones (agent sweep). Read-only on every existing file. No hardware runs, no provider calls.
All numbers recomputed from the files on disk with `~/bones-forge/qvenv` (scratch scripts were temporary). IBM per-seat
calibration comes from the cached published snapshots in `holes/cache/ibm/<chip>/<day>.json.gz` (already on disk).

Lens: "the absence is the data" / Plus None. The hunt was for NOTHING-SHAPED things: scatter that is too small, outcomes
that never show up, work that vanished, numbers that froze, gaps in shot order, and every flat result that got filed away.
Method: keep the discarded half, stack the failures, check each one against the other failures before calling it noise.

---

## TOP ITEMS (ranked by how hard the nothing is)

| # | What | Where | Numbers | Plain physics expects | Status |
|---|---|---|---|---|---|
| 1 | **Seat 62 goes quiet at rest and its 1 blinks out** | Marrakesh q62, dark_link balanced, 9/24 20:16-20:22Z | at rest: **2 ones in 32,768 shots** (7 of 8 whole circuits never read a 1); prepared 1: P(1) = **0.476** in one circuit, 128-shot blocks swinging **0.30-0.81** (binomial sd 0.044), runs z **-9.25** | about 0.2-0.4% ones at rest (chip-wide), a steady prepared 1 | new; aligns with 4 other seat-62 items (see ALIGN A) |
| 2 | **Frozen statistic across three independent runs** | dark_floor v2 phase test (real Marrakesh + two simulator rehearsals) | chi2(A1) = **19.438 / 19.478 / 19.444** | three draws from a null with sd 13.5 (mean 28) | new; ~1 in 230,000 raw, ~1 in 2,000-8,000 after look-elsewhere; no mechanism |
| 3 | **The empty box reads "present" on 4 of 4 runs** | three-box corner_11 (3 chips) + unused_10 (11-run) | +0.051, +0.174, +0.087, +0.169 -> stack **+0.121 +/- 0.031 (z 3.9)**, chi2 2.8/3 | 0 (never prepared) | stacked here for the first time; readout asymmetry ruled out; rides on error shots (see (b)/(f)) |
| 4 | **A failure never follows a failure** | Rigetti Cepheus q90, Ring first job (the one with 20 vanished tasks), 9/26 16:25Z | prep1/a: failure->failure **0 of 128** (8.6 expected); prep0/b: **2 of 171** (15.4 expected); P 1.8e-4, 2.8e-5 | independent shots | flagged 9/26 as "runs z +3.2/+3.8", direction never read; ordinary candidate = reset memory |
| 5 | **Seats that never show their thermal 1** | Marrakesh q134, q65, q49 (+ q62) | q134: **20 ones in 83,968** shots at rest over 4 separate jobs, 16 whole circuits with zero; q65 9/32,768; q49 31/32,768 | IBM's own same-day numbers predict >=102, >=64, >=104 | new |
| 6 | **The absence ledger is missing its only IBM absence** | `standoff/absence_ledger.py` reads one IBM key only | the 9/24 6073 failure (job daqmtobt55cs738rvdfg) is not in `absence_ledger.jsonl`; neither is the orphaned Braket step2b task | -- | structural hole in the hole-ledger |

---

## (a) TOO-QUIET NULLS

**a1. Kingston "lucky-tight" -- VERIFIED.** `dark_floor_real_20260924_135201.json` (ibm_kingston, job daqljjqkqcdc73aau0n0,
17:47-17:52Z, 8 pairs, t = 30 us). Recomputed from stored `gap` and `gap_std`:

| subset | n | scatter / shot-noise | chi2 about mean | lower-tail P |
|---|---|---|---|---|
| Kingston t30 | 8 | **0.37x** | 1.93 / 7 | **0.036** (1 in 28) |
| Kingston t30 without dead pair 16-23 | 7 | 0.50x | 1.54 / 6 | 0.043 |
| Marrakesh t30 | 8 | 1.06x | 9.09 / 7 | 0.75 |
| Marrakesh t0 | 8 | 0.73x | 5.95 / 7 | 0.45 |
| all 24 | 24 | 0.65x | 18.0 / 23 | 0.24 |

Plain physics: chi2 near dof. Kingston is 1 in 28 by itself, about 1 in 7 once you remember it was the tightest of four
subsets. It stays open between "lucky" and "the Estimator's stated errors run high"; no replication exists to split them.

**a2. The v2 phase test sits on the quiet side of its TRUE null.** `dark_floor_v2.py` labels the no-modulation expectation "~20".
With sigma estimated from each pair's own 7-dof fit residuals, (a1/se1)^2 is 2*F(2,7), so the real null is mean **28.0**, median 25.3,
sd 13.5 (200k-draw simulation on the run's own 12 thetas). The observed 19.44 has P(<=) = 0.27. Not significant alone; the verdict
(no phase modulation) is unchanged because a real modulation pushes the number UP. It matters for item (d1).

**a3. Checked and NOT too quiet (none found):**
- space = time (`space_time_same_real.json` vs dark_link balanced ENT): the famous agreement at theta = 0 and pi (pair-mean
  differences -0.0005 and -0.0002 vs +/-0.007) is two opposite per-pair offsets cancelling: per pair +0.021/-0.022 at 0,
  -0.012/+0.012 at pi. Per-pair chi2 **33.5 / 16 (P 0.006) -- NOISIER than shot noise**, not quieter (pair tilt offsets).
- arrow LINK+ vs LINK- (3 chips): chi2 60.5/36; Kingston 31.7/12 (noisy).
- dark_link per-pair forward ENT-PROD: 1.49x (run 1), 1.63x (balanced) shot noise.
- dark_edge dF per pair: t=30 chi2 3.7/6 about 0 (normal); t=0 is excess, not deficit.
- Rigetti: Rabi residual 1.02x binomial (chi2 30.4/18); step3 C_not control chi2 15.2/7; energy ledger has no quiet dataset.

---

## (b) NEVER-SEEN OUTCOMES

**b1. Cold seats (thermal 1 absent).** Every shot where a Marrakesh qubit sat untouched in |0> (dark_link PROD/PROD0 partner b,
space_time "ALONE" partner, dark_edge CAL00 and PROD0 partner, kerneled nearest-cloud call), 9/24 20:10-20:38Z:

| seat | shots at rest | ones | rate | IBM P(1\|0) 9/23 / 9/24 / 9/25 | expected (lowest) | P(<= obs) |
|---|---|---|---|---|---|---|
| q62 | 32,768 | **2** | 0.006% | 0.0005 / 0.0005 / 0.0027 | 16 | 1.6e-5 |
| q134 | 83,968 | **20** | 0.024% | 0.0044 / 0.0012 / 0.0022 | 102 | 2.5e-23 |
| q65 | 32,768 | **9** | 0.027% | 0.0034 / 0.0049 / 0.0020 | 64 | 9e-18 |
| q49 | 32,768 | **31** | 0.095% | 0.0054 / 0.0032 / 0.0112 | 104 | 4e-17 |

14 complete 4,096-shot circuits (q62 x7, q134 x6, q65 x1) plus 2 space_time 2,048-shot circuits (q134) never produced a single 1.
q134's rate holds across 4 different jobs and 4 circuit types, including a 30 us idle (1/4096).
Plain physics: a qubit in |0> reads 1 from leftover thermal population plus readout overlap, ~0.2-0.4% chip-wide (9/28 parallax).
Honest brake: the published per-seat number is a weak ruler in BOTH directions -- q123 reads 8.8% vs published 1.1%, q2 1.4%
vs 0.1-0.3%, q151/q152/q47 5-10x high. Across 19 seats the published value ranks them (Spearman +0.53, p 0.02) but misses the
scale by up to 20x. No relation to T1 (rho -0.11). So: the thermal 1 is missing on these seats, 10-50x below the chip median;
"the calibration overstates at rest" is the ordinary reading (IBM calibrates all 156 qubits at once; we read 2-6).

**b2. Checked, NONE found:**
- three-box: the four impossible cells (s0 = 1) are populated in all 16 circuits (39-232 counts each). No zero cells.
- dark_edge "off the map past the 1 cloud": 57 dots vs 29 expected from Gaussian tails (past the 0 cloud: 69 vs 37). More, not fewer.
  (The 9/28 phrase "no dots past the 1 cloud" means ~0.015% and equal across arms -- true, but not below a Gaussian tail.)
- Ring joint (q0, q90) cells: both-1 in cal prep1/b 0 vs 0.7 expected; prep0/a 1 vs 0.6. No power.
- Plus None: binary arms, nothing missing. No completed task anywhere is short of shots.
- dark_link cells that looked "never seen" (zeros vs other pairs' medians of 20-33) are all per-seat readout differences
  (the partner's false-1 rate), i.e. item b1 again, not new cells.

**b3. Filed nothing that is also never-seen:** Rigetti step3 (9/25) qutrit three-box dark branches at the post-selection point:
A_not +0.014, **B_not -0.019** (`step3_abl.json`) -- a readout-corrected probability BELOW zero. Filed "noise". It is the
Rigetti twin of the IBM empty box: there the silent branch stays silent (even overshoots to less than nothing); on IBM it does not (item 3).

---

## (c) VANISHED WORK

| when (UTC) | provider / device | qubits | what vanished | official reason | cost |
|---|---|---|---|---|---|
| 9/24 17:47-17:52 and ~20:53-21:08 | IBM ibm_kingston | **16-23** | a working pair: dark_floor bell gap 0.088 (nulls 0.078/0.089, all dead, sd_D 0.051 = 4-5x others); space Bloch length 1.36-1.43 (impossible); q16 reads 1 on 85% of \|0> shots | none; IBM cal at 19:25Z and 00:05Z said normal | -- |
| 9/24 21:03-21:11 | IBM ibm_kingston | **q1** | a clean \|0>: reads 1 on 33% | none; cal said e01 0.6% | -- |
| 9/24 **~18:41-18:45** (run log) | IBM ibm_marrakesh, job **daqmtobt55cs738rvdfg** | v2's 10 pairs (1-2, 61-62, 71-72, 128-129, 121-122, 133-134, 151-152, 64-65, 29-30, 144-145) | the whole v2 attempt 1 | **error 6073** (classical-control memory) | 12 QPU s, "Not Bones Heuremen" key |
| 9/26 ~01:15-01:16 (between step2 21:14:35 and step2b 21:16:28 EDT 9/25) | AWS Braket Cepheus | q0 | step2b first try: 1 task (delay 0) "likely created before the 4 ns rejection" | client-side: 0.05*1e-6 = 50.0000000004 ns off the 4 ns grid | $0.43 booked |
| 9/26 16:25:03.6-16:25:13.8 | AWS Braket Cepheus | q0 + q90 | **20 / 20** Ring context tasks | "quantum processor rejected the input" (user pulses on the 01 drive frame) | billing unknown |
| 9/25-9/26 | Braket | q0 | grid16q results "vanished" behind the brake (6 x "BRAKE" on --collect) until the trap fix | our own brake | -- |

Findings on the vanished set:
- **The orphan Braket task left no trace in our files and is not in the provider's FAILED/CANCELLED history** (the absence ledger
  pulls both, all time). So it most likely COMPLETED: a finished Rigetti q0 result nobody ever opened. No ARN kept.
  Recoverable for free later (search COMPLETED tasks around 01:15Z 9/26); not done here (no provider calls).
- **The absence ledger cannot see IBM keys 2 and 3.** `absence_ledger.py` builds its IBM service from `.ibm_quantum_key` only
  ("IBM open account: 6 jobs, 0 holes"). The 6073 failure ran on the "Not Bones Heuremen" key and most 9/24 fourth-outcome jobs ran
  on keys 2/3. The ledger of absences is missing the one IBM absence of the period.
- **Timestamp discrepancy:** the Biblioteca puts the 6073 failure at ~19:05Z and the v2 result at ~19:10Z. The run logs say
  14:41:32 EDT (18:41Z) submit, the batched retry started 14:45:03 EDT, and the v2 file was written 14:56:27 EDT. The failure is
  18:41-18:45Z. Not important physically; noted so nobody lines up holes against 19:05Z.
- **The rejected Ring tasks took real time.** Created-to-ended: rejected 2.50 s mean (1.16-3.65); the 6 cal tasks in the SAME
  10-second window completed 1,900 shots in 1.42 s; the same 20 contexts, when they ran 28 min later, took 3.08 s (Mann-Whitney
  p 0.07 vs rejection). The processor spent a normal task's time on each and returned nothing.
- **Clustering: none beyond design.** The three program refusals (18:41Z 9/24; ~01:15Z 9/26; 16:25Z 9/26) are format/size
  limits, 30 h and 15 h apart, on different hardware. Tasks just before (q90 Rabi 16:24:31Z), during (6 cal) and after (Plus None
  16:29Z on q99) the Ring rejection all completed: the refusal followed program content, not a device-down window. Rigetti q0 is in
  both Braket refusals, but q0 is in every Rigetti run that week, so that shared qubit carries no weight.
  The hardware vanishings (Kingston q16, q1) are the two chronic Kingston seats in IBM's own record (q1 rank 2 of 156, 142 flagged
  days; q16 rank 12, 31 days). Checked against the other failures: mundane, as the 9/26 lineup already said.
- Discarded-by-design (the discarded half): dark_floor and v2 kept only mitigated expectation values (no raw counts, no T2,
  frequencies, ZZ, or per-pub timing), so their per-shot story is gone for good.

---

## (d) FROZEN VALUES

**d1. chi2(A1) = 19.438 (real ibm_marrakesh, 10 jobs daqmvdik...), 19.478 (fake_kingston rehearsal `..._142058.json`),
19.444 (fake_marrakesh rehearsal `..._144449.json`).** Span **0.040**. The per-pair pieces are completely different
(real 0.71-3.88; sims 0.03-4.98), so this is not shared code or shared data; it is three independent sums landing on one number.
Under the true null (mean 28, sd 13.5, density 0.039 per unit at 19.45): P(three draws span <= 0.04) ~ **4.3e-6 (1 in 230,000)**;
allowing for the ~30-100 repeated statistics this sweep looked at, ~1 in 2,000-8,000. What makes it nothing-shaped: each copy
looked "textbook" only because the script printed the wrong expectation (~20). Every one of them sits at the number the null was
*thought* to be, and nobody saw that three independent instruments agreed to three digits. No mechanism is proposed.
(Related artifact: the first fake_kingston rehearsal, `..._142017.json`, ran ~0 shots -- 135 of 140 ZZ values exactly -1, 5
exactly +1 -- and returned chi2 = 10.000 exactly, five pairs at 2.000 each. A null-shaped number from no data at all.)

**d2. Three-box Marrakesh A = B.** Weak values +0.5786 (289/999) and +0.5791 (282/974); unconditioned probe +0.1165 / +0.1182.
A and B are equal in the ideal by symmetry, so only the closeness is odd: |diff| 0.0005 against a difference sd of 0.086,
~1 in 225 raw, ~1 in 10 given the other same-expectation pairs checked. Kingston/Fez/11-run A-B pairs differ normally.

**d3. Checked, none found:** no exact duplicate shot sequence among 1,508 per-shot series (the only identical 64-shot windows
are m1 = m2 at theta = 0 or m1 = mb in ENT, same circuit, physically forced). Equal-count coincidences between same-design
tasks: **297 observed vs 293.8 expected** (birthday baseline) -- nothing frozen at the count level. Known and resolved: Kingston
102-103 D = 0.0 exactly (1 in 255 per cell, Shuttle audit). Two Ring q0 cal tasks read exactly 1,759/1,900 (P ~0.025; inside
the birthday count). Empty-slot Kingston +0.174 vs 11-run +0.169 (P ~0.05).

---

## (e) SHOT-ORDER NOTHING

**e1. Rigetti Ring first job: the second failure is missing.** `standoff/ring_results.json` (6 in-job cal tasks, 1,900 shots,
per-shot order). Minority outcome followed by the same minority outcome:

| task | qubit | minority rate | repeat-after-minority | expected at base rate | P |
|---|---|---|---|---|---|
| cal prep1 read a | q90 | 6.74% | **0 of 128** | 8.6 | 1.8e-4 |
| cal prep0 read b | q90 | 9.00% | **2 of 171** | 15.4 | 2.8e-5 |
| cal prep1 read a | q0 | 6.95% | 3 of 132 | 9.2 | 0.019 |
| (all 8 tasks whose success leaves the qubit excited, by my reading of the two readout schemes) | both | -- | **31** | **66.5** | -- |
| (the 2 q0 tasks whose failure leaves it excited) | q0 | -- | 12 | 9.8 | clusters slightly |

Plain physics expects independent shots. The pattern follows one rule: when a success ends in |1>/|2>, failures never repeat;
when a failure ends in |1>, failures repeat a little. Ordinary candidate: **reset memory** -- the reset between shots fails
~7-9% of the time from an excited state and never from |0>. On q90 that means most of its "readout error" (6.7-9%) is carried
from the previous shot, not misreading. On q0 prep0/a (the "heat" series) there is no memory (5 vs 4.0), consistent with 9/28's
finding that q0's prepared-0 error is standing heat. By job: first job Stouffer z -3.13 (12 series); rerun +2.35 (40 series,
mild carry-over); q90 Rabi +1.69; Plus None -0.82. IBM contrast: the 9/28 echo run found IBM erases the previous shot (echo ~0).
Testable in the 9/28 whole-chip "shuffle / blink train" data (out of scope here).

**e2. IBM Marrakesh: the prepared 1 vanishes in spells, only where a 1 must survive.** dark_link (`raw_darklink_all.json`,
994 runs tests): 8 with |z| > 3 vs 2.7 expected, **7 of 8 negative (clustered), all on the partner qubit b**. Split by role:

| series | n | sd of runs z | chi2 P |
|---|---|---|---|
| a qubit, first look | 336 | 0.936 (shuffled control 0.952) | none |
| a qubit, second look | 336 | 0.939 | none |
| partner b, ENT | 128 | 1.016 | none |
| partner b, prepared \|0> | 114 | 0.85-0.87 | none |
| **partner b, prepared \|1> (PROD1)** | 80 | **1.601** | **4e-15** |

The spells (per 128-shot block): q62 at theta pi/4 (bal job 13, pub 3) 0.39 0.33 0.57 0.43 ... 0.81 ... 0.33 (P = 0.476
overall, other q62 circuits 0.83-0.91); q123 (bal job 7, pub 1) 0.73 for ~900 shots, then 0.95 for the rest; q62 theta 5pi/4
opens at 0.77/0.66 then ~0.9; q49 dips to 0.80-0.82 mid-circuit. dark_edge (`dark_edge_real_..._163458.npz`, 96 runs tests):
4 with |z|>3 vs 0.26 expected -- q29 PROD1 t=30 (z -5.25, P(1) 0.468), q48 PROD0 t=30 (-4.12), q28 PROD1 t=30 (-3.18),
q122 PROD0 t=30 (+3.14). Again: where a 1 has to last. Plain physics: T1 fluctuating on sub-second scales (two-level defects).
Textbook physics, nothing-shaped behaviour: the excitation disappears in stretches, then comes back.
Side note (not a nothing): q123 at rest ran HOT and cooled over 25 min -- 12.6-17.1% ones in run 1 (20:10-20:12Z), 4-7.7%
in the balanced run (20:16-20:22Z), 1.05% in dark_edge CAL00 (20:33Z); steady inside each circuit.

**e3. Checked, none found:** three-box (48 series, sd 0.89, 0 flags), arrow/space (373, sd 0.97, 2 flags vs 1.0 expected,
both few-ones artifacts), a-qubit lag-1/2/3/10 autocorrelation (all at the iid value), Rigetti half-vs-half drift (sd 0.97, 0
flags), Plus None longest runs (all inside chance). Timing gaps: IBM dark_link balanced jobs finish every ~18-19 s (serial execution,
textbook); Braket task clocks are created/ended only (no per-shot times), so no within-task periodicity test is possible.

---

## (f) FLAT RESULTS ALREADY FILED (null / textbook / retracted / "not interpreted") -- the stack

IBM 9/24 (Marrakesh unless noted):
1. dark_floor t=0: D = +0.0012 +/- 0.0024 (NULL; 1/pi^4 excluded at 3.7 SE).
2. dark_floor t=30: +0.00758 +/- 0.00252 as reported -> z ~2.2 defensible (audit) -> v2 D_invariant +0.0056 +/- 0.0081,
   D_forward +0.0124 +/- 0.0046, D_reversed -0.0013 +/- 0.0154 (ORDERING artifact). Wild reversed pairs: **61-62 +0.049**, 144-145 -0.047.
3. v2 phase chi2(A1) 19.44 (NULL; true null mean 28), A2 falsifier 21.9 (clean).
4. 1/pi^4 match: RETRACTED. Collective relaxation: DEAD.
5. dark_link run 1: inverse chi2 37.8/42 (NULL); forward -0.0076 +/- 0.0036 (killed by balancing).
6. dark_link balanced: forward -0.0014 +/- 0.0026 (TEXTBOOK); inverse at noise.
7. dark_edge: dF(0) -0.0011 +/- 0.0008, dF(30) -0.0001 +/- 0.0003, time +0.0010 +/- 0.0009 (TEXTBOOK); one cell 122-123 q_a
   t=0 ENT 10 vs PROD 26/30 (~3 sigma, "not interpreted").
8. space = time: textbook (per-pair offsets +/-0.02, chi2 33.5/16).
9. Experiment B flip asymmetry: ENT +0.0245 +/- 0.0065 vs PROD0 +0.0231, PROD1 +0.0228 (same).
10. three-box empty slot: +0.051 +/- 0.064 (Marr, "silent"), +0.087 +/- 0.062 (Fez, "silent"), +0.174 +/- 0.063 (King,
    "noise/crosstalk suspect"), unused_10 +0.169 +/- 0.061 (11-run, "leak"). **Stacked: +0.121 +/- 0.031, z 3.9, 4/4 positive.**
11. corner 11 in its own ledger: +0.60 / +0.30 / +0.55 (2.5-3.7 sigma, "not interpreted").
12. First-look dip: closed 9/28 as entangling-gate energy loss (mean -1.5%, ~5 sigma, tracks gate error rho 0.94).
13. Energy ledger half-excited residual -0.0020 +/- 0.0005 ("balances to 0.2%"). Percent-off clustering p 0.15. EH-dev Fez vs
    pinata arb_5 r +0.78 (x137 -> 0.27). Anomaly lineup 0/24 (nearest outside hole 13.5 d).
14. Mitigation "more than everything": 16/216 dark_floor values outside [-1, +1]; 141-142 t=0 deficit -0.31 (the mirror image of a nothing).

Rigetti Cepheus 9/25-9/26:
15. step3 ABL A 0.92, B 1.15, C 0.205 (ideal 1, 1, 0.2); dark branches A_not +0.014, **B_not -0.019** (below zero).
16. step3 C_not control flat 0.357-0.418 (chi2 15.2/7).
17. grid16q four-way SRBP -0.0179 +/- 0.0022 vs ideal -0.0188 (0.4 sigma).
18. Plus None (q99) a-b: -0.005 +/- 0.015, +0.020 +/- 0.018, -0.025 +/- 0.019, -0.035 +/- 0.015 (claim not met). Stacked: chi2
    8.5/4 (P 0.075), 3 of 4 negative, b above a at 6 us both settings.
19. Ring: beyond-quantum FALSE on both witnesses. **Raw sum BELOW its own prediction**: q0 2.284 vs 2.314 (-1.7 sd), **q90
    2.301 vs 2.422 (-6.7 sd)**. Consistency D_j at 0 us: **10 of 10 negative** (q0 -0.045..-0.091, z -2.3..-4.8; q90 -0.019..
    -0.049, z -1.1..-2.8) where the textbook says 0; sign test 1/1024. Cross-witness phi no |z|>3; both-1 coincidences z +0.67.

---

## ALIGN -- what shares a seat, device, time, position or number

**A. Seat 62, ibm_marrakesh -- the string goes through five holes.**
1. at rest it almost never reads 1 (2 / 32,768; coldest of 19 seats);
2. its prepared 1 blinks (runs z -9.25 and -3.76; the most-blinking of 10 partner seats);
3. its pair 61-62 was the wild reversed pair in v2 (+0.049) that made the v2 headline inconclusive, with the largest v2 fit
   scatter (0.0293 per point, highest of 10) and the largest A2 falsifier (0.0252, highest of 10), ~80 min earlier on the same chip;
4. IBM's own record flags it chronically (rank 5 of 156 on Marrakesh, 180 flagged days, 11 spells; none active on 9/24);
5. same seat on the 6073-failed job (trivially, v2 reused the pairs -- no weight).
Odds if these were independent: coldest AND most-blinking of 10 = 1 in 10; noisiest v2 pair among the 7 pairs shared with
dark_link = 1 in 7; a top-6 chronic seat among 10 partners ~1 in 25. Combined roughly **1 in 1,000-2,000** if independent.
They are probably NOT independent: one defect-plagued seat is expected to be noisy everywhere. That is the ordinary reading, and
it is still the week's one seat where every kind of nothing lands together.

**B. The empty box sits on the error shots.** In the four empty-slot circuits, the shots that landed in the impossible s0 = 1
ledgers (pure error, ideal count 0) carry a probe tilt of **+0.214, +0.228, +0.210, +0.126** (+/-0.04-0.06) -- larger than the
kept-ledger "presence" (+0.05..+0.17). The probe's readout asymmetry from IBM's calibration (probes q55, q138, q136, q147)
predicts only -0.025..+0.033 of weak value. Across all 16 three-box circuits the error-only ledgers lean positive in 26 of 32
cells. So the empty box's +0.12 (z 3.9, chance 4/4 same sign 1 in 16) is carried by shots that went wrong: the 9/25
"correlated error in the decomposed controlled-RY" candidate, now measured from the existing shots rather than guessed.
The nothing shows up as presence only inside the failures.
Side alignment: Kingston's three-box silently used TWO qubit triples (optimization_level 1): A and C on 110/109/108, B and
corner_11 on **152/151/138**. So Kingston's box-to-box comparisons are cross-qubit, and the largest empty-slot lean (+0.174)
sits on 151/152.

**C. Seats 151/152 across the blueprint** (same position on every Heron r2 chip, different physical qubits): Marrakesh
dark_floor 151-152 bell loss 2.83x the T1 prediction (2nd worst of 16); Marrakesh dark_link biggest first-look dip on 151-152
(-6.2/-7.7%); Marrakesh 151-152 chronic bad joint (rank 5/170, 9/28); Kingston three-box empty-slot lean +0.174 on 152/151/138.
Seat choice was driven by the pair-picker and transpiler, and ~15 "notable" seats out of 156 make overlaps easy.
Odds about **1 in 5**. Suggestive only.

**D. q90's missing second failure and q90's missing contextuality.** The Ring corrected its sums with the in-job cal rows,
and on q90 those rows are mostly previous-shot memory (e1). The context tasks leave the qubit excited about half as often as
the cal tasks, so the memory differs task to task, and the correction and S_raw_pred inherit a bias. Candidate link (untested)
to q90's raw sum falling 0.12 (6.7 sd) short of its own prediction and to the 10/10 negative D_j at 0 us. No chance odds; it is a
mechanism to check, not a coincidence. The first Ring job holding both the 20 vanished tasks and the anomalous cal rows is forced
by design (it was the only job with cal rows): **zero weight**.

**E. Circuit position.** Every nothing that involves losing a 1 sits where a 1 must survive to the readout (PROD1 partner,
30 us idles); every cold seat is a partner qubit measured first or alongside the first look; in all four three-box runs the probe
is measured 68-348 ns BEFORE the system qubits, and the system qubits show the 3.5-5% extra 1s (filed as gate error), the
same "last measured runs hot" shape as April's Exp A. Design-confounded: **no odds computable**.

**F. Time.** Every Marrakesh per-shot nothing sits in 20:10-20:38Z on 9/24, because that is when all the per-shot Marrakesh
jobs ran. No information. Rigetti items are 9/25 21:03Z - 9/26 16:55Z on q0/q90/q99: no clustering with the refusals beyond
design. The v2 frozen triple (d1) shares a statistic, not a time or seat. **No time alignment found.**

**G. Numbers.** The frozen chi2 (19.44 x3, d1) is the only number-alignment with long odds. Others checked (0.174/0.169,
A = B 0.579, 1,759 = 1,759) sit inside birthday chance. The empty slot's +0.12 does not match any framework constant and was
not compared to one.

---

## NONE FOUND (plainly)

- No exact repeated shot sequences; no excess of equal counts (297 vs 293.8).
- No missing shots in any completed task (IBM or Braket).
- No never-seen cells in three-box, dark_edge IQ regions, Ring joint cells or Plus None.
- No shot-order structure on the looked-at qubit (a), the three-box probe/system bits, arrow or space; no Rigetti drift.
- No too-quiet scatter anywhere except Kingston dark_floor (1 in 28) and the v2 statistic (mild).
- No clustering of vanished work in time or on qubits beyond what the circuits' content explains.

## OPEN, CHEAP, FROM DATA ALREADY PAID FOR (no new runs)

1. Recover the orphaned step2b delay-0 task (Braket COMPLETED search ~01:15Z 9/26): the one unopened drawer.
2. Extend `absence_ledger.py` to keys 2 and 3 so the 6073 job (and any others) land in the ledger. (Change for Wayfinder/Bones to
   make; this sweep did not modify any file.)
3. Test e1's reset-memory rule on the 9/28 Rigetti shuffle/blink-train data, and re-derive the Ring's q90 correction using
   previous-shot-conditioned confusion rows (does the 6.7 sd shortfall close?).
4. Seat 62: pull its 9/24 hourly calibration and the 9/28 parallax/echo rows for Marrakesh q62, if they exist, to see whether
   the cold-and-blinking pairing holds on another day.
