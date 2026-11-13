# PASS C -- THE OWN CLOCK (the ruler as the measurement), triple pass of 3 October 2026

Seat C, read-only. Every quantum-hardware firing that a claim in 7_PUBLIC.md, LAWS_UPDATE_DRAFT.md or MEASUREMENT_PAPER_DRAFT_20261003.md rests on,
read for the ruler that turned raw counts into the claimed number, with that ruler moved to its nearest honest alternatives.
Nothing in the ledger, reads, data, code or claims was edited. No hardware was contacted.

**Clock key (The Stake).** LAID = laid time and the maker's stated timings (our delays, the 2.180-us stated look, the drive frame).
WITNESS = a spectator qubit or another firing. OWN = the measured qubit's own decay clock. Every number below carries one.
Percentages are of population (level 0 = the same job's lone |0> look, level 1 = the same job's lone |1> look) unless marked.

**What was recomputed (raw jobs on disk, out/qubit_fifth_run/data/fire/; inputs hash-identical to reads_new's).** Scripts and outputs in this folder:

| script | sha256 (16) | what it moves |
|---|---|---|
| seatC_crossing_rulers.py / .txt | e433f42fb27c822a / bc44090b97865482 | the crossing: five decay clocks (one / own / mix / long / once), two state assignments (projection / threshold + assignment matrix), four statistics (mean / median / P300 in (0.1,0.9) / 8-width readable cut); ten arms of run 121 |
| seatC_crossing_rulers2.py / .txt | bb370fad902347b2 / 86f443e945f75218 | the crossing without the clip-bound qubits; by thirds of each qubit's own P300; the early-decay shortfall that would absorb each chip's crossing; run 121's measured shortfall carried to the other jobs (FOREIGN, flagged) |
| seatC_crossing_rulers3.py / .txt | 0e0b8787cf5239d2 / e65521e7555309b3 | run 121: the per-entry clock without per-qubit noise ('own-smooth'); the noise-curvature bias of the claimed per-qubit 'own' book |
| seatC_look_rulers.py / .txt | 06e4d631c9ef5e78 / 2b18b4e0fd2fb07b | the look: the witness's phase-curve ruler and statistic; the qubit's own per-look cost under statistic and clock choices; hand kept; turn per us |
| seatC_park_rulers.py / .txt | bc4962cfb4476305 / 844e5edfb319954f | the park (hold run, stopwatch run) without the clip, and under run 121's shape (FOREIGN) |
| seatC_misc_rulers.py / .txt | c741e85497a03789 / 95a8be8266908d85 | spectator leftover (+0.6 deg) averaging rulers; leakage cap k under assignment/selection; the leakage-plus-TLS need re-solved |
| seatC_carry_rulers.py / .txt | 28373b24a3c826ed / 2c0c5119ba46ddc4 | 'shots don't talk' under three cuts and no cut |
| seatC_frame_split.py / .txt | 2abcd6672c2f064d / 60f20bff07bff613 | the spectator's 3.144 deg/us split into drive frame [LAID] and emitter pull [WITNESS] |

**Reproduction check (claimed ruler, recomputed from raw, before moving anything).** Push run OFF +0.0200 (0.0016), ON +0.0005 (0.0013); hold run +0.0217 (0.0018);
Marrakesh +0.0274, Kingston +0.0287 / ON -0.0124; run 121 A30_30 +0.0126 / -0.0097 and all ten arms as noname_read1.txt; witness 2.3494 / 2.3699 us; hand kept
0.9209 / 0.8256 / 0.7604; turn 3.1444 deg/us; park +0.17 / +0.20 / +0.14 %; leftover +0.596 deg; push shortfall 1.45 deg, k 0.26 %/push; carry -0.0023.
All match the printed reads. Moved numbers below are therefore moves of the ruler only.

**Read first -- the objects this pass found (each is something to describe, not a lane that closes a question):**
1. **The clip-bound qubits.** Four Pittsburgh qubits with 6-18 us clocks (q31, q36, q57, q90; q87 in one job) read ~0 after 300 us; the readers clip that
   to 0.02 and book them as ~77-us clocks. Each then reads +0.06 to +0.46 above its book, from either start. They carry +0.67 / +0.79 / +0.85 % of the push
   run's three job means, +0.76 % of Marrakesh's (11 such qubits), 0.06 % of Kingston's (1). The same qubits lift the park and the ON column.
2. **The early decay restarts at every push.** Of five decay clocks fitted in run 121's own job, the one in which each entry into |1> carries its own
   fast early decay comes closest to the ten arms (sum of (residual/width)^2: 17 with per-qubit levels, 53 with the smooth curve) -- the T1-fluctuation
   mixture leaves 129, one exponential 409; none brings all ten within their widths. The crossing's size and sign are the choice among these clocks.
3. **The look's own time is an estimator family, not one number:** 2.4 to 8.3 us [OWN] depending on which OWN clock converts the loss to time.

---

## Blocks, one per firing-claim

### C1. The crossing, Pittsburgh push run -- "+2.00 +- 0.16 %" (7 F2, F4; LAWS 4; paper Table 6)
- **Firing.** ibm_pittsburgh runs 91/92/93 (jobs davuanc92g1c7399i8kg 13:09, davveh04oijs73e88tsg 14:26, davvf7c92g1c7399k1h0 14:27), 14 circuits x 400 shots,
  all 156 qubits driven, 141/148/149 readable.
- **Rulers that made the number.** Decay clock [OWN]: one exponential through the same job's 300-us |1>-idle level, q = clip(P300, 0.02, 0.98)^(1/10) per
  LAID 30-us stretch. Calibration clouds: same job (lone |0>, |1> looks). State assignment: projection onto the |0>-|1> line (continuous). Statistic:
  mean over qubits with clouds > 4 widths apart. Three jobs averaged with width sqrt(sum w^2)/3 (job-to-job wander not in the width).
- **Moved.**
  - Clip-bound qubits left out (only those with P300 <= 0.02): **+1.27 (0.15)**. Same set, ON start: -0.67 (0.14).
  - Mean over P300 in (0.1, 0.9): +1.23 (0.16). Median of per-qubit residuals: +1.37 (0.22). Clouds > 8 widths (22-28 qubits): +1.70 (0.42), ON -1.55 (0.37).
  - Threshold at the line's midpoint + same-job assignment matrix: +2.09 (0.14); its P300-in-(0.1,0.9) set +1.29 (0.14).
  - By thirds of each qubit's own P300 (clip-free; P300 0.22 / 0.34 / 0.42): +1.52 / +1.08 / +1.20 (0.28-0.30) -- no trend with the qubit's own clock.
  - Decay clock: no within-job short-time arm exists. The chip-wide early-decay shortfall at 30 us that would bring this residual to zero: **0.0062 (0.0008)**
    [OWN]. Measured on this chip only in run 121 (3.5 h later, cross-job): 0.0128 (0.0027) on P300-in-(0.1,0.9) qubits, 0.0094 median, 0.0259 all readable.
    FOREIGN (run 121's typical shortfall applied here): **-0.48 (0.14)**, -1.38 (0.15) on the typical set.
- **Lap up.** Raw I/Q -> projected level per shot -> mean per qubit -> minus a book whose per-stretch survival comes from one 300-us point -> mean over 141-149 qubits.
  Two places set the size: the one-point clock (which cannot see a faster early decay), and the clip (which turns a 6-18-us clock into a 77-us clock).
- **Lap down.** Of +2.00: +0.73 is the clip's (four qubits); the remaining +1.27 equals the book's response to an early decay 0.6 % faster at 30 us than one
  exponential allows, and this chip's own measured early-decay shortfall (run 121) is 1.5-2x that.
- **Ruler's share.** 37 % from the clip alone; with the decay clock moved, 70 % (by run 121's mixture analogue) to more than all of it (per-entry, cross-job).

### C2. The crossing, Pittsburgh hold run -- "+2.17 +- 0.17" (7 F2, F4; reads_new/hold_crossing.txt)
- **Firing.** ibm_pittsburgh runs 71/72/73 (davtdgtj371s73dngms0 12:07, davtfd04oijs73e85n2g 12:11, davth95j371s73dngub0 12:15), 11 x 330, 145/139/139 readable.
  Arm OFF|P9 = the push run's OFF spread circuit.
- **Rulers.** As C1.
- **Moved.** Clip-free (4 clip-bound qubits out): **+1.48 (0.17)**; typical set +1.52 (0.18); median +1.74 (0.23); threshold +2.24 (0.15); 8-width cut +2.45 (0.53).
  Shortfall that zeroes it: 0.0069 (0.0008) [OWN]. FOREIGN (run 121 shortfall): -0.44 (0.16), typical set -1.20 (0.16).
- **Lap up / down.** Same chain as C1. Of +2.17, +0.69 is the four clip-bound qubits.
- **Ruler's share.** 32 % from the clip; the rest sits inside the decay-clock choice as in C1.

### C3. The crossing, Marrakesh -- "+2.74 +- 0.28, one read" (7 F2; paper Table 6)
- **Firing.** ibm_marrakesh run 141 (db023m492g1c7399o9vg, 17:27:51), 14 x 400, 143 readable. Marrakesh decays faster: P300 mean 0.179, 41 qubits below 0.1.
- **Rulers.** As C1.
- **Moved.** Clip-free (11 clip-bound qubits out: q24, 26, 37, 74, 90, 103, 104, 105, 107, 108, 124): **+2.15 (0.29)**; typical set (102 qubits) +2.01 (0.31);
  median +2.29 (0.39); threshold +3.06 (0.20); 8-width cut +2.55 (0.41). By P300 thirds: +2.55 / +2.06 / +1.83. Shortfall that zeroes it 0.0157 (0.0022)
  readable, 0.0129 (0.0020) typical. FOREIGN (Pittsburgh's run-121 shortfall, a foreign chip's ruler): +1.06, typical set **+0.01 (0.30)**.
  No short-time arm was ever fired on Marrakesh in the push protocol. Nearest OWN evidence of a fast early clock there: run 5's gap/level clock 0.61 (0.08)
  (nine qubits, after a look, 10/2 08:47).
- **Ruler's share.** 28 % from the clip; the decay-clock share is unmeasured on this chip (needs ~1.3-1.6 % of early shortfall at 30 us to absorb all of it).

### C4. The crossing, Kingston -- "+2.87 +- 0.28, one read" (7 F2; paper Table 6)
- **Firing.** ibm_kingston run 141 (db023hal7guc73cfnvl0, 17:27:32), 14 x 400, 147 readable; only 5 qubits have clouds > 8 widths apart.
- **Rulers.** As C1.
- **Moved.** Clip-free (q134 out): +2.84 (0.26); typical +2.72 (0.28); median +2.66 (0.36); threshold +2.96 (0.23). By P300 thirds +3.05 / +3.09 / +2.35.
  Shortfall that zeroes it 0.0152 (0.0015). FOREIGN: +0.48, typical **+0.22 (0.27)**. Nearest OWN evidence of an early clock on Kingston: 10/1 run 2 gap/level
  clock 0.60 (0.07), run 3 0.53 (nine qubits, after a look).
- **Ruler's share.** About 0 from the clip or the statistic (this is the crossing that holds its size under every within-job ruler tried); the decay-clock
  share is unmeasured on Kingston and would be all of it at a 1.4-1.5 % early shortfall at 30 us.

### C5. Three-chip mean "2.54 %" against the Bonefish friction 2.65 % (7 F2)
- **Firing.** C1 + C3 + C4.
- **Moved.** Clip-free 2.08 (0.14); medians 2.11; typical sets 1.99; FOREIGN per-entry 0.35 (0.13). Under the claimed ruler the gap to 2.653 is -0.12 (0.14);
  clip-free -0.57; FOREIGN -2.30.
- **Ruler's share.** The 0.1 % agreement is a property of the clip + one-point clock; moving either moves the mean by 0.46-2.2 %, 4-18x the gap it is compared on.

### C6. The ON column "+0.05 / -0.16 / -1.24" and Finding Seven's "Kingston -1.24 +- 0.24 % = rung four 1.216 %" (7 F2, F7)
- **Firing.** As C1, C3, C4 (ON|s10 arm).
- **Rulers.** As C1. The clip lifts ON as much as OFF (a 6-us qubit ends ~1 from either start).
- **Moved.** Pittsburgh: clip-free -0.67 (0.14), typical -0.77, median -0.57, 8-width cut -1.55 (0.37), FOREIGN +1.77. Marrakesh: clip-free -0.93 (0.24),
  typical -1.33, median -0.47, FOREIGN +0.66. **Kingston: clip-free -1.30 (0.26), typical -1.43, median -1.21, threshold -1.11 (0.20), FOREIGN +0.38 (0.26).**
  In run 121 (Pittsburgh, same job's clocks) the ON start B30_30 reads one -0.22 / own -0.21 / own-smooth +1.18 / mixture -1.05 / once -0.13.
- **Lap down.** With the clip out, all three chips read ON below their book (-0.67, -0.93, -1.30) and OFF above it (+1.27, +2.15, +2.84): a mirror, the shape a
  one-point clock makes when the real early decay is faster (the book's slope is -2.0 for OFF and +1.5 for ON per unit of q at q ~ 0.89). "Flat on two chips,
  down on Kingston" is the clip's: clip-free, the ON column is down on all three.
- **Ruler's share.** Finding Seven's 1.24 holds within 0.2 under assignment and statistic rulers, and moves to +0.38 (sign flips) under a per-entry clock carried
  from Pittsburgh. Kingston has no within-job short-time arm, so the rung-four match sits on an untested clock.

### C7. Run 121: the two rulers, the below-zero slope, "T1 fluctuation", and the one arm in ten (7 status, F2, F5; LAWS 4-5; paper Table 8)
- **Firing.** ibm_pittsburgh run 121 (db00t8k92g1c7399m6hg; submitted 16:05:54, landed 17:42), 21 x 216, 150 readable (141 with P300 in (0.1,0.9)). One job.
- **Rulers that made the claims.** Decay clocks [OWN]: 'one' (P300^(L/300)) and 'own' (each stretch booked with the same job's per-qubit |1>-idle level at L,
  L = 10/30/90). Projection; mean over readable. Family-wise 7.6 % = Sidak over the ten arms of z = 1.70/0.64.
- **Moved -- the decay clock, five ways, all fitted in this job** (residual %, mean readable, width ~0.25-0.7):

  | arm | one | own (claimed) | own-smooth | mixture (T1 fluct.) | long only | once |
  |---|---|---|---|---|---|---|
  | N2 (2 pushes) | +2.45 | -0.12 | +0.57 | +0.57 | +1.88 | +0.12 |
  | N6 (6) | +2.07 | -0.58 | -0.56 | +0.86 | +1.96 | +0.83 |
  | A30_30 (10) | +1.26 | -0.97 | -1.44 | +0.38 | +1.30 | +0.56 |
  | A10_30 | +1.47 | -1.39 | -1.74 | +0.68 | +1.67 | +0.69 |
  | A90_30 | +2.70 | -0.07 | +0.12 | +1.33 | +2.35 | +2.02 |
  | A30_10 | +2.91 | +1.70 | +0.77 | +2.22 | +2.84 | +1.79 |
  | A30_90 | -0.50 | -0.62 | -1.05 | -0.87 | -0.28 | -0.56 |
  | A30_30f | -1.33 | +0.91 | +1.38 | -0.44 | -1.36 | -0.62 |
  | B30_30 (ON) | -0.22 | -0.21 | +1.18 | -1.05 | -0.80 | -0.13 |
  | B30_30f | +0.15 | +0.14 | -1.25 | +0.98 | +0.73 | +0.06 |
  | sum (res/width)^2, ten arms | 409 | 17 | 53 | 129 | 290 | 72 |

  Shape fitted in-job: fast fraction 0.020 (0.008), fast clock 20 (11) us [OWN]. Mixture = each shot has a fixed clock drawn from that two-part shape;
  long = the slow part only; once = the fast part only at the shot's first excitation; own-smooth = the fast part at every entry into |1>, from the smooth
  fitted curve instead of noisy per-qubit levels. (Arms share their ruler arms, so the sums are not independent chi-squares.)
- **Moved -- the estimator inside 'own'.** The per-qubit own book carries a noise-curvature bias (216 shots, per-qubit R30 width 0.024; book curvature
  -17 per unit q^2): residual shifted **+0.41 (0.07)** on A30_30, -0.53 on B30_30, +0.34 on A30_10, +0.03 on N2 (simulated). So the claimed -0.97 is about
  -1.4 without the noise term; own-smooth reads -1.44.
- **Moved -- assignment and statistic.** Threshold assignment, own: N2 / N6 / A30_30 = +0.15 / -0.26 / -0.30 (claimed projection: -0.12 / -0.58 / -0.97);
  one: +2.52 / +2.13 / +1.72. Typical set, own: -0.03 / -0.43 / -0.91; one: +1.25 / +1.40 / +0.64.
- **Claims, each with its ruler moved.**
  - "Below zero, deeper with every push, -0.12 / -0.58 / -0.97" (F5): slope per push -0.11 % (own, projection), -0.06 % (own, threshold), -0.25 % (own-smooth),
    -0.15 % with a positive offset (one), about 0 (mixture: +0.57 / +0.86 / +0.38). Below zero under own and own-smooth only.
  - "The short-time and long-time decay sit 2.2-2.7 % apart at every push count" (F2, LAWS 5): one minus own = 2.57 / 2.65 / 2.23 (all readable);
    1.28 / 1.83 / 1.55 (typical set; the outlier qubits carry ~1 % of the gap); 1.88 / 2.63 / 2.70 (one minus own-smooth).
  - "Most of it is non-exponential decay -- T1 fluctuation" (7 status, F2, paper 3.5): under the T1-fluctuation clock fitted here the A30_30 crossing is
    +0.38 (0.38), but that clock leaves the ten arms at 129 (A90_30 +1.33, A30_10 +2.22, B30_30 -1.05, B30_30f +0.98). The clock that comes closest is the
    per-entry one (17 per-qubit / 53 smooth; none of the six books brings all ten within widths): the early decay behaves as if it restarts at each X. That
    is a different object from T1 fluctuation (a per-shot fixed clock), and it is the one this job's arms lean toward.
  - "A30_10 +1.7 +- 0.6 (7.6 % family-wise)": own-smooth **+0.77 (0.49)**; own with its noise term out ~+1.36; threshold own +1.43 (0.52); typical own +1.93 (0.74);
    mixture +2.22 (0.25); one +2.91 (0.23). The 2-width standout is the per-qubit own estimator's.
- **Lap down.** The A30_30 crossing in this job runs from +1.30 (long) to -1.44 % (own-smooth) [OWN] across six books of its own decay curve; the claimed
  numbers are two of the six. The decay curve itself (R10/R30/R90 below one exponential by 0.41 / 1.28 / 1.00 % on typical qubits; 1.41 / 2.59 / 1.85 % on all readable) is the
  measured object; every crossing number is that curve booked one way.
- **Ruler's share.** All of the sign and nearly all of the size (2.7 % swing against a 1.26 % claimed value).

### C8. The idle-|0> arms -- "heating while the qubit idles ... +0.02 +- 0.15 % after 300 us; across chips -0.43 to +0.26 %" (7 F2; LAWS 4; paper control 2)
- **Firing.** OFF|n300 / Z300 arms of C1, C3, C4, C7.
- **Rulers.** The zero is the same job's lone |0> look (it carries whatever the start leaves excited); projection; mean.
- **Moved.** Threshold assignment: Pittsburgh push +0.02 (0.03); run 121 **+0.14 (0.05)** (projection +0.02 (0.15)); Marrakesh -0.30 (0.05) (projection -0.43);
  Kingston +0.24 (0.05). The threshold ruler shrinks the widths 3x.
- **Lap down.** An idle-|0> arm reads (excitation gained) minus (the start's own residual excitation relaxing over 300 us); Marrakesh's negative value has the
  shape of a zero reference that carries excitation which then relaxes. Three positions: heating, relaxation of the start's residual, drift of the zero reference.
- **Ruler's share.** Small in size (all within +-0.43 %) but the cap's meaning (heating < 0.3 %) assumes the second term is zero; on run 121 the threshold
  ruler reads +0.14 (0.05), i.e. a resolved non-zero idle term at 2.8 widths.

### C9. Leakage cap "0.26 +- 0.12 % per push, against 2.96 +- 0.28 % needed" (7 F2; paper control 3d)
- **Firing.** Push runs 91-93, back-to-back arms (2 and 10 X with no delay) for the cap; the C1 spread arms for the need.
- **Rulers.** Cap: model o_N + |u_N| = 2 sin^2(N e/2) + (N/2) k, solved on two counts; projection; mean. Need: the reviewer's two simulated rows
  (leakage 1 %/push: +1.86 / -1.34 / +0.26; TLS 1: -5.30 / +6.08 / -0.67, ledger line 1953; not on disk as code) fitted to the one-clock crossings.
- **Moved.** Cap: projection clip-free k = 0.27 (0.12), e = 1.43 deg; threshold k = 0.34 (0.06), e = 1.39 (0.08); threshold clip-free 0.33 (0.06).
  **Need, on the clip-free crossings (OFF +1.27, ON -0.67, MID -0.41):** leakage-plus-TLS 0.81 (0.28) %/push, TLS 0.07 (0.08), MID off by 4.1 widths;
  leakage alone 0.58 %/push, OFF and ON within 1.2 widths, MID off by 4.0.
- **Ruler's share.** The cap holds its size under every ruler tried (0.26-0.34 %). The need is a ruler product: 2.96 under the clip, 0.58-0.81 without it.
  The margin moves from ~11x to ~2-3x (and the in-between start becomes the arm that misfits).

### C10. "On IBM, shots don't talk (-0.002 +- 0.002)" (LAWS 3; ledger §151; paper control 4)
- **Firing.** Push runs 91-93, OFF|s10 arm, shots in stored order. LAID inter-shot gap: 500-us repetition delay plus the circuit.
- **Rulers.** "Ends 1" = projected level > 0.5; conditional difference; mean over readable.
- **Moved.** Cut 0.3: -0.0040 (0.0031); cut 0.7: -0.0028 (0.0017); no cut (lag-1 correlation of the level): -0.0038 (0.0021). ON|s10 -0.0016 to -0.0026;
  ON|n300 +0.0058 (0.0043) in every cut.
- **Lap down.** The state-assignment ruler does not move it. The LAID gap does: the project's own 9/28-9/29 records at 20-us gaps read +17 points (Marrakesh,
  Kingston) and +7 (Fez) of carried excitation, +23.0 pp arisen carry on Marrakesh, gone by ~500 us (§21, §36b-d).
- **Ruler's share.** About 0 for the assignment ruler; the claim's truth is set by the laid gap (500 us), which the LAWS line does not name.

### C11. The look, maker's clock -- "2.18 us" [LAID] (7 F1; LAWS 5; paper Table 2)
- **Firing.** Static target read 10/2 11:02:53 (reads/maker_look_length_pittsburgh.json): measure duration 2.180 us, the same number on all 156 qubits.
- **Ruler.** The maker's stated instruction duration. It is not a reading of the scheduled mid-circuit block (all 156 qubits are one measurement group).
- **Moved.** Nothing to recompute; its witness reading under moved curve rulers (C12) spans 2.05-3.08 us.
- **Ruler's share.** It is a ruler (LAID) by definition; what it stands for on hardware (pulse only, or the whole scheduled slot) is not on file.

### C12. The look, witness's clock -- "2.37 +- 0.03 us" [WITNESS mapped to LAID] (7 F1; LAWS 5; paper Table 2)
- **Firing.** Look-time runs 101/102/103 (davucks92g1c7399iak0 13:13 and two more 14:26-14:28), 14 x 400, 83 spectators (free Ramsey clocks, emitters held |1>),
  far qubits read 3 or 9 times back to back between barriers.
- **Rulers.** Each spectator's phase over the block is mapped to LAID time on a quadratic through its own 30- and 60-us delay arms (exact two-point fit through
  the origin); time per look = block time / k; median over spectators. Implicit: the spectator turns at the same rate during readout blocks as during idle delays.
- **Moved** (us per look, 3 looks / 9 looks): quadratic 30/60 (claimed) 2.35 (0.06) / 2.37 (0.03); **line through 30 us 2.11 (0.07) / 2.20 (0.03)**;
  line through 60 us 2.32 / 2.36; least-squares quadratic 30/60/120 2.12 / 2.05 (0.05); least-squares line 2.88 / 3.08 (the 120-us arm turns ~180 deg past
  60 us, so its unwrap is fragile); mean over spectators (quadratic) 3.63 / 3.02 (0.08); 10 % trimmed mean 2.59 / 2.65. The three jobs read 2.47 / 2.28 / 2.36
  (9 looks), spread beyond their widths.
- **Lap down.** The 0.19-us excess over 2.18 is the size of the curve-ruler choice (2.05-2.37 among median rulers). Per-look time is constant between 3 and 9
  looks under every curve ruler (no fixed per-block overhead) -- that part holds.
- **Ruler's share.** Witness/maker 1.087 moves to 1.01 (line 30), 0.94 (LS quadratic), 1.39 (mean): the whole excess is inside the curve and statistic choice.

### C13. The look, qubit's own clock -- "3.5 +- 0.2 us (3.5 / 3.6 / 4.1 wherever the look sits)" [OWN] (7 F1; LAWS 5; paper Table 2)
- **Firings.** Hold runs 71-73 (looks on the way: L1 / L3 / L9 inside 300 us LAID); give-back runs 111-113 (one look at 0 / 150 / 270 us, 1000 shots);
  jump runs 11-18 (look, look again, 8 jobs); tail runs 21-23.
- **Rulers.** The extra loss a look causes is turned into time with a decay clock: hold -- 300 x ln(left)/ln(left with nothing) per qubit (one exponential
  through 300 us), median over qubits; give-back -- tau = -300/ln(none) per qubit (clip 0.02-0.98), mean; jump -- the 60/240/300-us fitted clock.
  "+- 0.2" is not computed by any script on disk.
- **Moved** (us per look):
  - Hold L9 (best-measured): bit-by-bit median **2.93 (0.25)**; mean readable 4.01 (0.30); typical mean 4.26 (0.22); median-qubit levels 4.09 (0.36);
    long clock (slow part of run 121's shape) typical mean **4.35 (0.22)**, typical median 3.52 (0.29). Hold L3: 3.50 (0.75) median ... 4.83 (0.57) long-clock mean.
  - Hold L1 (one look at 150 us): median 0.00 -- pinned: 3-9 qubits whose levels are <= 0 get clipped to 1e-6 and read exactly 300 us, and the per-qubit
    spread straddles 300 (76 below, 77 above); typical mean 3.0 (1.8); median-qubit levels 4.9 (3.5). (§132's "costs nothing by the end" is this pin.)
  - Give-back at 0 / 150 / 270: claimed mean 3.53 / 3.56 / 4.05 (0.9); median 1.40 / 3.44 / 3.32 (1.1); typical mean 4.34 / 4.12 / 5.07; long clock
    4.45 / 4.23 / 5.19. Job-to-job spread 2.3-4.1 us against shot widths of 1.6 per job.
  - Jump, immediate pair: per-job medians 3.20-4.26; per-qubit median 3.23 [2.36, 4.97]; long clock extrapolated back to look 2's start **8.27 [3.62, 12.85]**
    (printed, reads/jump_rerack.txt). Converted instead on the clock right after a look (tail run first stretch ~240 us) or right after preparation (lone run
    208 us) rather than the 280-us long clock: x0.85 / x0.74 -> ~2.7-3.6 / ~2.4-3.2 us (reasoned from printed values).
- **Lap down.** "3.5" is one point in an OWN family that runs 2.4-8.3 us; which loss counts as the look's (immediate, piled-up, extrapolated) and which clock
  converts it are both rulers. Every best-measured estimator (L9, eight-job immediate pairs) sits above the maker's 2.18; single give-back looks scatter wider.
- **Ruler's share.** +-0.2 is ~5x narrower than the spread across honest OWN rulers (2.9-4.4 us for the L9 / pair family alone).

### C14. The three ratios -- "1.087 (12/11), 1.606 (phi), 1.477 (phi x 11/12)"; "the look stretches the qubit 1.48x ... the photon ring 1.5" (7 F1, F3, F4, F6)
- **Firing.** C11 + C12 + C13.
- **Moved.** Witness/maker 0.94-1.39 (claimed 1.087); qubit/maker 1.34 (L9 median 2.93) / 1.48 (pair, 3.23) / 2.00 (L9 long-clock mean 4.35) / 3.79 (fit-ON 8.27)
  (claimed 1.606); qubit/witness from 0.95 (2.93/3.08) to 2.12 (4.35/2.05), e.g. 1.24 (L9 median / claimed witness), 1.82 (L9 mean / line-30 witness)
  (claimed 1.477).
- **Ruler's share.** The matches to 12/11, phi and 1.5 sit at widths of 0.015-0.09 that are the shot widths of one estimator each; the estimator choice moves
  every ratio by 0.1-0.6 (more with fit-ON). The calls "1.09, 1.62, 1.48 on a second chip" need their curve, statistic and OWN clock written with them.

### C15. Free-running spectator coherence -- "0.921 +- 0.004, 0.826 +- 0.005, 0.760 +- 0.006 ~ 11/12, 10/12, 9/12" [WITNESS] (7 F3; LAWS 2)
- **Firing.** Look-time runs 101-103, 83 spectators.
- **Rulers.** |hand after| / |hand at no window|, median over spectators. The third point is a LAID 30-us delay, the first two are 3- and 9-look blocks.
- **Moved.** Mean over spectators: **0.883 (0.003) / 0.765 (0.003) / 0.705 (0.003)** (10.6 / 9.2 / 8.5 twelfths). The spectators' own LAID-delay curve in the
  same jobs: 0.760 (30 us), **0.486 (60 us), 0.165 (120 us)**. One exponential through the 30-us point predicts 0.938 at 7.05 us (3 looks x 2.35) and 0.823
  at 21.3 us (9 x 2.37) against 0.921 and 0.826 measured.
- **Lap down.** The 9-look value is the spectator's own free dephasing over the block's length; the 3-look value sits 1.7 % under that curve. The countdown
  stops at 9/12 because the next LAID arm reads 0.486. The call "27 looks leave 0.750" sits against the spectator's own curve at ~64 us: ~0.45-0.49.
- **Ruler's share.** The twelfths spacing is the median statistic plus the LAID windows sampled; under the mean it is gone.

### C16. Spectator precession -- "3.144 +- 0.076 degrees per microsecond ~ pi" (7 F3)
- **Firing.** Look-time runs 101-103 (83 spectators); frame split against the stopwatch run 81 (same role seed; 71 spectators readable in both).
- **Rulers.** median |angle(T30)|/30 in the maker's drive frame [LAID], emitter held |1> [WITNESS pull].
- **Moved.** Signed median **-1.68 (0.12)**; mean |.| 3.25; over 60 us 2.54; over 120 us 1.48; 40 % of spectators turn +. Split: the emitter's pull alone
  (run 81, frame cancelled) signed median -1.69 [-2.29, -1.34], |median| 1.95; the drive-frame part (total minus pull) +0.16 [-1.66, +3.45], |median| 2.35;
  across spectators the total does not follow the pull (r = -0.09).
- **Ruler's share.** Most of it: the number is the median size of the maker's frame offsets plus a pull of ~1.7-1.9 deg/us; a 60-us window gives 2.54.

### C17. Frame-held spectators, run 121 -- "16.9 deg per 30-us |1> stretch ~ golden climb 17.03" (7 F4); "own leftover +0.6 deg" (LAWS Plus None)
- **Firing.** Run 121 witness arms (WA/WB x hands X/Y), 75 witness-emitter pairs on 35 emitters, one job.
- **Rulers.** Coupling: a per-pair model fit (emitter's own fading R30, two-state chain, grid |theta| <= 34.4 deg), median |theta|. Leftover: mean over pairs of
  angle(va vb)/2.
- **Moved.** Coupling: raw half-difference |hd|/5 **8.24 (0.48)**, median 8.01; signed -2.50 (0.99) (52 of 75 negative); model mean 17.34, chip-typical fading
  16.33; 4 pairs on the grid edge; 53 of 75 pair fits jump > 10 deg in a third of resamples (THREE_SEATS_RUN121). The model at 16.9 books 11.7 deg per stretch
  of half-difference (8.24 measured). Leftover: median **-0.38 (4.65)**; circular +2.98 (2.88); length-weighted +3.46 (3.12) (claimed +0.60 (4.57)).
- **Ruler's share.** Coupling: half of 16.9 is the model's (raw 8.24). Leftover: the value is set by the averaging rule within +-3 deg; its width is 5-8x its size.

### C18. The park -- "mean over qubits +0.0017 / +0.0020 / +0.0014" and "0.0648 / 0.1348 vs 0.0647 / 0.1346" (7 F6; LAWS 4; paper 3.2)
- **Firings.** Hold runs 71-73 (P1 2 x 150, P3 4 x 75, P9 10 x 30 us LAID; start |1>); stopwatch run 81 (davtm5ql7guc73cfgtlg 12:25, 39 emitters, 34 readable).
- **Rulers.** One exponential from the same job's 300-us (hold) or 60-us (stopwatch) |1>-idle arm [OWN], clip 0.02-0.98; relaxation only in |1>; mean.
- **Moved** (hold, %, P1 / P3 / P9): claimed +0.17 / +0.20 / +0.14 (0.13-0.15); **clip-free -0.14 / -0.44 / -0.56**; typical -0.24 / -0.55 / -0.67.
  FOREIGN shape (run 121): per-entry -0.04 / +0.17 / **+1.23**; mixture -0.73 / -1.18 / -1.11; once +0.44 / +0.03 / -0.16. The four clip-bound qubits add
  +0.31 / +0.64 / +0.70 to the claimed means. Stopwatch (no clip-bound emitters): one +0.14 (0.27) / +0.48 (0.39); per-entry -0.60 (0.27) / -0.48 (0.38);
  mixture +0.18 / +0.31.
- **Lap down.** The three-scheme closure is a cancellation: on the 135-141 ordinary qubits per job the park sits below the one-exponential book by an amount that
  grows with the number of parks (-0.14 -> -0.56); four 6-18-us qubits lift the mean by +0.3-0.7. P9 is the same circuit as run 121's B30_30 (ON start), whose own decay curve gives
  -0.21 to +1.18 depending on the clock. The emitter park moves within ~+-0.6 % under all three clocks.
- **Ruler's share.** Hold-run park: the whole closure (its sign pattern is the clip's). Stopwatch park: within its widths, about +-0.6 %.

### C19. "A Pittsburgh qubit keeps 0.313-0.335 of itself after 300 us ~ 1/pi" [OWN at LAID 300 us] (7 F3)
- **Firings.** Push run (0.3131), hold run (0.3354), run 121 (0.3286): mean over readable.
- **Moved.** Median: 0.3361 (0.0032), 0.3573 (0.0031), 0.3488 (0.0053); threshold means equal to projection within 0.002.
- **Ruler's share.** The 300 us is LAID (our choice); the mean sits 0.02 under the median (the short-clock qubits pull it). Under the median the range is
  0.336-0.357, which does not hold 1/pi = 0.318.

### C20. "The qubit's two clocks sit at 0.756 (one read) and 0.775 +- 0.009 (eight reads) of each other ~ 3/4" [OWN] (7 F3)
- **Firings.** Lone run 31 (one job); jump runs 11-18.
- **Rulers.** Short clock / long clock, middle-bit pooling; 0.775 = mean of eight per-read middles (0.730-0.806).
- **Moved (printed values).** Bit-by-bit, no earlier look 0.803; one earlier look 0.688 (lone_vs_tail.txt); bit-to-bit 0.779 [0.69, 0.87] (§120). §120's own
  ruler row: one clock plus the no-wait drop gives 0.90; one clock plus the curve's drop gives 0.79.
- **Ruler's share.** 0.69-0.90 across pooling and the look-cost ruler; "3/4" is the middle-bit pooling.

### C21. "The gap clock 0.60" (and 1/0.60 = 1.667, spiral step four) [OWN] (7 F3, F4)
- **Firing.** ibm_kingston 10/1 run 2 (9 qubits, 839 shots; three waits).
- **Rulers.** Gap clock fitted on three waits (look 1 -> look 2) over the level clock; middle bit.
- **Moved (printed).** Kingston run 3: 0.53; Marrakesh 0.61 (0.08); Phoenix 0.68 (0.07); Boston 0.80 (0.11); Pittsburgh 0.83 (0.11) then 0.66 (0.10) next morning.
  §105: "a fixed bite taken by the look would shorten it by itself". §117: single qubits jump 0.2-0.4 within minutes; the chip-to-chip differences sit inside that.
- **Ruler's share.** 1/0.60 moves to 1.20-1.89 across runs of the same ruler.

### C22. "The halfway state's early decay clock at 0.59 of the |1> state's (123 / 208 us, one read)" [OWN] (7 F3)
- **Firing.** Lone run 31 (one job, 400 shots).
- **Moved (printed).** Bit by bit: halfway first stretch 0.263 of its own 60-300-us clock, |1> 0.803 -> ratio ~0.33; halfway over its own later clock 123/277 = 0.44.
- **Ruler's share.** 0.59 is the middle-bit pooling; per-qubit it is ~0.33.

### C23. "A 0.62-0.65 band on 9/28" (7 F3)
- **Firing.** ibm_marrakesh 9/28 echo (78 qubits); re-fired 10/2 (runs 210-237, three reads).
- **Ruler.** The band is a cut position on the |0>-|1> line (a state-assignment setting) at which a clustering statistic (R^2 0.23-0.43) peaked.
- **Moved (printed, §140).** Same code on three 10/2 reads: 0.00-0.11 at those cuts; single qubits entering/leaving move the peak (q14, q154 at 0.66; q142 at 0.67-0.68).
- **Ruler's share.** The number is a ruler setting; the peak did not return on the same chip and qubits four days later.

### C24. The witness stopwatch -- "witness time 35.6 / 48.3 us for our 40 / 60" and §135's triangle (paper 3.3; LAWS Plus None)
- **Firing.** Stopwatch run 81 (one job; 68 spectators with readable hands).
- **Rulers.** Witness time = total turn / the turn rate of the first 20 us of emitter-|1> [WITNESS]. §135's closure uses a fitted model (no producing script on disk).
- **Moved (from printed medians).** With the emitter's own fading as the ruler (60-us survival 0.7896 -> tau 254 us [OWN]) the expected witness time is 38.5 / 55.6 us;
  LAID 40 / 60. Per-stretch ratios: measured 0.78 / 0.65 (median of ratios; 0.83 / 0.85 ratio of medians) against 0.93 / 0.92 under the OWN ruler.
- **Ruler's share.** The witness reads short of both the LAID and the OWN expectation; §135's "OWN ruler closes it" rests on a model that cannot be regenerated.

### C25. "The inside never reads the outside's laid time -- a spectator's clock is blind to how long we waited" (LAWS Plus None; 7 closed list)
- **Firing.** ibm_fez 9/24-9/27, "pair 2" (26 batches; OBSERVER_WITNESS_20260930.md): outside = IBM's reported added duration of a 0-20-us Ramsey wait;
  inside = the phase step of a fixed-frequency tone in the readout records (the buzz), sampled once per shot.
- **Ruler.** The inside clock is the buzz, which reads the shot trigger's period; whether a circuit's wait changes that period is set by how the maker lays out
  shots [LAID]. §146 already named the 1:1 per-run term an identity.
- **Moved.** On 10/2 spectator qubits do read laid time: look-time spectators turn 3.1 deg/us with laid delay (C16), and the stopwatch witness times laid 40 / 60
  as 35.6 / 48.3 us (C24).
- **Ruler's share.** All of it: the firing's inside clock was a readout tone, not a spectator; the LAWS sentence names a spectator.

### C26. The third level -- "a minority of qubits, three behaviours (standing, carried, blinking), on IBM and Rigetti" (LAWS 3; 7 closed; paper 3.4)
- **Firings.** IBM two-look jobs 9/24-9/28 (Marrakesh, Kingston, Fez); Rigetti Cepheus 9/25-9/28 (563 tasks).
- **Rulers.** IBM: shots outside both clouds on both looks against a Gaussian-cloud "expected by chance" (radius not on file); Rigetti: the rung-2 discriminator
  and its "mirror check".
- **Moved (printed, not recomputed).** Rigetti readout-vs-rung-2 correlation -0.55 -> -0.31 after the mirror check ("part of it was the ruler", §5); 25 Rigetti
  qubits where blur and rung 2 trade places; §21: "90 % of the extra dots in the 1 cloud" was the axis/percentile rule's classification, wrong per qubit.
- **Ruler's share.** Unmeasured here; the counts depend on an exclusion radius and a cloud-shape assumption not printed. Recompute needs the 9/2x analysis files.

### C27. "What the reset erases is what was placed (0.067 %); what arose stays (+23 points at 20 us, gone by 500)" (LAWS 4)
- **Firing.** ibm_marrakesh 9/28 echo (E0/E1 files; gaps 20-2000 us); Kingston 9/28 (+11.1 pp, no placed arm).
- **Rulers.** "Arisen" = previous shot's own look cut to 1 (threshold); pooled over qubits; corrected; lag-1 vs lag-20 conditioning.
- **Moved (printed).** The weighting ruler moved it once already: unweighted average 38 % -> 23 % (§36b). Blinking qubits dominate the pooled number
  (q68 17.1 % base, q76 11.7 %, chip median 0.33 %).
- **Ruler's share.** The 23 pp is the weighting and the blinkers'; per qubit the carry is "far beyond a single shared number" (§36d). Not recomputed here.

### C28. "The order of looking sets the heat ... closed, three rulers each" (7 closed list; ledger §154)
- **Firings.** Rigetti rooms 9/28 (+1.1 % full room, -1.6 % middle trio); IBM April + September jobs.
- **Ruler.** q0's flip error as the yardstick.
- **Moved (printed).** §21 (9/29): q0's flip error flickers 5.3-9.9 % between tasks seconds apart; rooms pooled 7.0 / 7.5 / 7.2 / 7.2 %; "NOT supported".
  §154 (10/2) re-lists the rooms as standing.
- **Ruler's share.** The effect (1-1.6 %) sits inside the ruler's own task-to-task wander (4.6 % wide).

### C29. "A qutrit three-box silent branch read below zero too, -0.019 (one run)" (7 F5)
- **Firing.** Rigetti 9/25, step 3 (standoff/braket_round1_step3.py).
- **Ruler.** Readout-corrected probability, a correction that "assumes 2 outcomes (mean of rungs 1 and 2)" (out/discards/DISCARD_MAP.md); no width printed.
- **Ruler's share.** A below-zero corrected probability is what inverting an assignment correction gives when raw counts sit under the correction's own floor;
  without the raw count and its width the sign is the ruler's. Not recomputed.

### C30. The back-to-back pair on three chips -- "-0.048 / -0.027 / -0.020 (start 1)" (paper 3.1)
- **Firings.** Runs 5 (Marrakesh), 9 (Pittsburgh), 7 (Kingston), nine qubits each, one job each.
- **Ruler.** Mean over nine qubits of look 2 minus look 1.
- **Moved (printed).** Per qubit -0.006 to -0.272 (Marrakesh), -0.013 to -0.119 (Pittsburgh), +0.002 to -0.041 (Kingston): the nine-qubit mean is set by one or
  two qubits (Pittsburgh q108); the 156-qubit jump run reads -0.012 to -0.016 per job.
- **Ruler's share.** The chip ordering is the qubit draw's.

### C31. "A Rigetti neighbour in |2> pulls a spectator by -62.1 +- 0.6 deg/us" (paper abstract, 3.3)
- **Firing.** Rigetti 9/28 (§7, §11, §12).
- **Ruler.** Spectator Ramsey frame differenced between q0 in |2> and at rest (the frame cancels in the difference); -62.1 / -62.3 / -59.9 with 0 / 54 / 106
  other spectators.
- **Ruler's share.** Small: the number holds within 4 % across the three crowd sizes printed. Not recomputed.

---

## Table

| claim | ruler used | number | number with the ruler moved | ruler's share |
|---|---|---|---|---|
| Crossing, Pittsburgh push (C1) | one-exp OWN clock from P300, clip 0.02, projection, mean | +2.00 (0.16) % | clip-free +1.27 (0.15); median +1.37 (0.22); threshold +2.09 (0.14); FOREIGN per-entry -0.48 (0.14) | 37 % clip; 70 % to >100 % decay clock |
| Crossing, Pittsburgh hold (C2) | same | +2.17 (0.17) | clip-free +1.48 (0.17); median +1.74; FOREIGN -0.44 (0.16) | 32 % clip; rest as C1 |
| Crossing, Marrakesh (C3) | same | +2.74 (0.28) | clip-free +2.15 (0.29); typical +2.01; threshold +3.06; FOREIGN typical +0.01 (0.30) | 28 % clip; clock share unmeasured on chip |
| Crossing, Kingston (C4) | same | +2.87 (0.28) | clip-free +2.84; median +2.66; threshold +2.96; FOREIGN typical +0.22 (0.27) | ~0 within-job; clock share unmeasured |
| Three-chip mean vs 2.65 (C5) | means of C1, C3, C4 | 2.54 (0.14) | clip-free 2.08 (0.14); medians 2.11; FOREIGN 0.35 (0.13) | the 0.1 % match is the ruler's |
| ON column; Kingston = rung four (C6) | as C1 | +0.05 / -0.16 / -1.24 | clip-free -0.67 / -0.93 / -1.30; Kingston threshold -1.11, FOREIGN +0.38 | sign under the clock; size holds under assignment |
| Run 121 below-zero slope (C7) | per-qubit own OWN clock | -0.12 / -0.58 / -0.97 | own-smooth +0.57 / -0.56 / -1.44; threshold +0.15 / -0.26 / -0.30; mixture +0.57 / +0.86 / +0.38 | sign and slope are the clock's |
| Two rulers 2.2-2.7 % apart (C7) | one minus own, all readable | 2.23-2.65 | typical set 1.28-1.83; one minus own-smooth 1.88-2.70 | ~1 % from outlier qubits |
| "Mostly T1 fluctuation" (C7) | named, not fitted | -- | mixture clock in-job: A30_30 +0.38 (0.38) but ten arms 129; per-entry 17-53 | the arms lean per-entry, not mixture |
| A30_10 one arm in ten (C7) | per-qubit own | +1.70 (0.64), 7.6 % FW | own-smooth +0.77 (0.49); noise term out ~+1.36; mixture +2.22; one +2.91 | the standout is the estimator's |
| Idle-|0> heating cap (C8) | projection, zero = lone |0> | +0.02 (0.15); -0.43 to +0.26 | threshold run 121 +0.14 (0.05); Marrakesh -0.30 (0.05) | small in size; meaning needs the start's residual |
| Leakage cap vs need (C9) | two-count model; reviewer rows on one-exp crossings | 0.26 (0.12) vs 2.96 (0.28) | cap 0.27-0.34; need on clip-free 0.58-0.81 | cap holds; need is ~75 % clip |
| Shots don't talk (C10) | cut 0.5, 500-us LAID gap | -0.002 (0.002) | cuts 0.3/0.7, no cut: -0.004 to -0.003 (0.002-0.003); at 20-us gaps +17 to +23 pp | 0 for assignment; all of it is the laid gap |
| Look, maker (C11) | stated duration LAID | 2.18 us | witness reads 2.05-3.08 under moved curves | a ruler by definition |
| Look, witness (C12) | quadratic 30/60, median | 2.37 (0.03) us | line-30 2.20 (0.03); LS quadratic 2.05 (0.05); mean 3.02 (0.08) | whole 0.19-us excess |
| Look, own (C13) | one-exp clock; pile-up median; "+-0.2" uncomputed | 3.5 (0.2) us | L9 median 2.93 (0.25); L9 long-clock mean 4.35 (0.22); pair 3.23; fit-ON 8.27; early-clock pair ~2.4-3.6 | +-0.2 is ~5x too narrow |
| Ratios 12/11, phi, 1.5 (C14) | C11-C13 | 1.087 / 1.606 / 1.477 | 0.94-1.39 / 1.34-2.00 (3.79 fit-ON) / 0.95-2.12 | each match within one estimator's width only |
| Spectator twelfths (C15) | median of hand ratios | 0.921 / 0.826 / 0.760 | mean 0.883 / 0.765 / 0.705; free-decay curve 0.938 / 0.823; 60 us 0.486 | spacing is statistic + LAID windows |
| 27-look call 0.750 (C15) | twelfths extrapolated | 0.750 | spectator's own curve at ~64 us: ~0.45-0.49 | -- |
| Precession ~ pi (C16) | median |rate| over 30 us, drive frame | 3.144 (0.076) deg/us | signed -1.68 (0.12); 60-us window 2.54; pull alone |1.95|; frame part |2.35| | most of it (frame) |
| Coupling ~ 17.03 deg (C17) | model fit median |theta| | 16.9 (1.8) deg | raw |hd|/5 8.24 (0.48); signed -2.50 (0.99) | half |
| Own leftover +0.6 deg (C17) | mean of half-sums | +0.6 (4.6) deg | median -0.38 (4.65); circular +2.98 (2.88); weighted +3.46 (3.12) | value set by averaging; width 5-8x |
| Park, hold run (C18) | one-exp from N0, clip, mean | +0.17 / +0.20 / +0.14 % | clip-free -0.14 / -0.44 / -0.56; per-entry -0.04 / +0.17 / +1.23; mixture -0.73 / -1.18 / -1.11 | the closure is the clip's |
| Park, emitters (C18) | one-exp from 60-us yardstick | +0.14 / +0.48 % (0.0648 vs 0.0647) | per-entry -0.60 (0.27) / -0.48 (0.38); mixture +0.18 / +0.31 | ~+-0.6 %, inside 2.2 widths |
| Keeps 0.313-0.335 ~ 1/pi (C19) | mean at LAID 300 us | 0.313-0.335 | median 0.336-0.357 | LAID window + statistic |
| Two clocks ~ 3/4 (C20) | middle-bit pooling | 0.756; 0.775 (0.009) | bit-by-bit 0.803 / 0.688; per-read 0.730-0.806; no-wait ruler 0.90 | 0.69-0.90 |
| Gap clock 0.60 -> 1.667 (C21) | three-wait gap fit, Kingston run 2 | 0.60 (0.07) | same ruler other runs 0.53-0.83 | inside the qubits' own minute-scale jumps |
| Halfway early clock 0.59 (C22) | middle-bit pooling | 0.59 | bit by bit ~0.33; own later clock 0.44 | most |
| 9/28 band 0.62-0.65 (C23) | cut position on the I/Q line | R^2 0.23-0.43 | 10/2, same code: 0.00-0.11 | a ruler setting |
| Witness stopwatch (C24) | first-20-us rate | 35.6 / 48.3 us | OWN expectation 38.5 / 55.6; LAID 40 / 60 | closure model not on disk |
| Inside blind to laid time (C25) | buzz tone per shot vs reported duration | "zero, 1:1" | spectators on 10/2 read laid time (3.1 deg/us; 35.6 / 48.3 us) | all: the inside clock was the trigger's |
| Third level, three behaviours (C26) | exclusion radius; rung-2 discriminator | 134 vs 6.5; standing/carried/blinking | Rigetti rho -0.55 -> -0.31 by one ruler row | not recomputed |
| Placed 0.067 % / arisen +23 pp (C27) | cut + weighting | +23 pp | the unweighted-average version printed 38; blinkers dominate | weighting moved it by 15 |
| Order of looking (C28) | q0 flip error | +1.1 / -1.6 % | ruler wanders 5.3-9.9 % task to task | ≥ the effect |
| Qutrit below zero (C29) | 2-outcome readout correction | -0.019 | no raw count or width printed | sign is the correction's until shown |
| Back-to-back pair (C30) | mean of nine qubits | -0.048 / -0.027 / -0.020 | per qubit -0.006 to -0.272 etc.; 156-qubit -0.012 to -0.016 | the draw's |
| Rigetti |2> pull (C31) | frame-differenced Ramsey | -62.1 (0.6) deg/us | -62.3 / -59.9 across crowds | small |

---

## What survived every ruler tried here (within the rulers named)
- **The early decay is faster than the late decay**, on every pooling and chip that has it measured: R10/R30/R90 below one exponential (0.4-2.6 % at 30 us,
  run 121), first stretch 208 vs 275 us (lone run), gap/level clocks 0.53-0.83 on five chips. Its size moves with the ruler; its sign does not.
- **The look costs the qubit more than the maker's 2.18 us** on every best-measured OWN estimator (2.4-8.3 us, the low end being the early-clock conversion
  reasoned from printed values); the witness's per-look time stays constant between 3 and 9 looks under every curve ruler.
- **Kingston's OFF crossing, +2.66 to +2.96 %,** under every within-job ruler (clip, statistic, assignment; the 8-width cut keeps 5 qubits and reads
  +4.4 (1.4)); its decay-clock share is the untested part.
- **The push's own shortfall (1.39-1.45 deg) and the per-push cap (0.26-0.34 %)** under assignment and selection rulers.
- **No shot-to-shot carry at the 500-us laid gap** under every cut (-0.004 to -0.002).
- **The emitter park (run 81)** stays within ~+-0.6 % of its book under one-exp, per-entry and mixture clocks.

Bones (seat C), 3 October 2026.
