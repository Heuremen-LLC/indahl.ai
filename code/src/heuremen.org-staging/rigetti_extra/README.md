# Two Rigetti Cepheus-1-108Q findings, packaged for checking

`python3 verify_rigetti_extra.py` (standard library only, no network) recomputes every number below from
`data/rigetti_extra.json` (119 KB) and prints each claim beside the recomputed value, marked OK or DIFFERS.
`extract_rigetti_extra.py` shows how the JSON was cut from the private raw files (needs numpy and the private
folders; you do not need to run it). Device: Rigetti Cepheus-1-108Q on Amazon Braket, region us-west-1, 107 qubits
addressed, `disable_qubit_rewiring=True`, every circuit inside a verbatim box. No tasks were submitted for this package.

Words used: **push** = one X gate (native `rx(pi)`, 32 ns); **look** = readout; **clock** = a spectator qubit put on the
equator with `rx(pi/2)`, left free for a window, then turned back with a second `rx(pi/2)` (hand X) or `rz(pi/2)` then
`rx(pi/2)` (hand Y). A clock's phase is the angle of H = (1 - 2 P1[X]) - i (1 - 2 P1[Y]), P1 = fraction of shots reading 1.

---

## Finding A: ten pushes in a row read 1 more often when the neighbours are excited at the look

**What was run** (4 Oct 2026, 17:15-17:21 UTC = 13:15 EDT; 42 Braket tasks, ids in the script output and the JSON;
writer `heuremen.org/experiments/2026-09-28-rigetti-cepheus/rigetti_triangles.py`, functions `b_circ`, `b_round`).
Seven qubits (the *pushed* qubits: 7, 22, 27, 57, 62, 72, 104; every pair at least 5 links apart) get ten pushes back to
back from |0>, then a plain look. Their 22 neighbours (wired directly to them) are in one of three states; three rounds
~3 minutes apart; 900 shots per task:

| arm | what the neighbours do |
|---|---|
| rest | nothing |
| pushed | the same ten pushes, in step with the pushed qubits |
| "equator" | `rx(pi/2)` before the train, `rx(pi/2)` after it |

Circuit, in order, over all 107 qubits: `rz(q, 0)` on every qubit; [equator arm: `rx(pi/2)` on the 22 neighbours]; ten times
{`rx(pi)` on the 7 pushed qubits; [pushed arm: `rx(pi)` on the 22 neighbours]}; [equator arm: `rx(pi/2)` on the neighbours];
measure all. Each round also ran an 8-sequence read-out calibration; this package does not use it (the raw fraction needs no model).

**Result** (recomputed; per-qubit values are in the script output). Read-1 fraction of the 7 pushed qubits, mean:

| round | rest | pushed | equator | equator / rest |
|---|---|---|---|---|
| 1 | 0.0643 | 0.0646 | 0.1102 | 1.71 |
| 2 | 0.0641 | 0.0656 | 0.1010 | 1.57 |
| 3 | 0.0584 | 0.0560 | 0.1038 | 1.78 |

* Pooled over rounds (2700 shots per qubit per arm): equator minus rest = +0.043 +- 0.018 (qubit-to-qubit spread, 6 d.o.f.,
  t = 2.34, short of the 2.447 needed for 95 %; shot noise alone is +-0.003). Ratio 1.69 +- 0.32 (delete-one-qubit jackknife).
  Pushed minus rest = -0.0002 +- 0.012: equal, as claimed. Equator minus pushed: +0.043 +- 0.012, positive on 7 of 7 qubits.
* "About 1.7x" is the pooled / round-1 figure; round 2 alone is 1.57.
* **The rise is not uniform.** Per qubit, equator minus rest: q27 +0.132, q22 +0.077, q7 +0.045, q62 +0.027, q104 +0.021,
  q57 +0.006, q72 -0.010. Each of the first five is well past its own shot noise; the last two show nothing.

**What does not hold up as stated.** The "equator" arm is not neighbours on the equator at the look. They sit on the
equator only during the train; the two half-turns add to one full turn, so at the look **the neighbours are in |1>: 94 % read 1**
(rest arm 3 %, pushed arm 9 %). "On the equator during the train" and "excited at the look" are confounded; the design
has no arm that excites the neighbours once and leaves them, and no arm that puts them on the equator without ending in |1>.

A shot-level check shows what that does and does not settle. In the rest arm a pushed qubit reads 1 in 4.8 % of shots
when all its neighbours read 0, but in 19 % when one of them reads 1 (the looks are correlated between neighbours, by read-out
crosstalk or a shared real excitation; the data cannot say which). In the equator arm, with neighbours reading 1, it reads 1
in 9.9 %, less than that correlation alone would predict. So crosstalk alone is not a quantitative match, and it is not excluded.

**Do known mechanisms predict it?** (the size estimates below are order-of-magnitude reasoning, not computed here)
* *Read-out crosstalk* (a neighbour's state at the look nudges a qubit's read-out): the right kind and sign; usually a
  percent-level effect, so +13 % on q27 is large. It would be tested by a pair-by-pair run with neighbours excited and the pushed qubits idle. Not run.
* *ZZ coupling* (a neighbour's state shifts a qubit's frequency by hundreds of kHz at most): against a 32 ns push, whose
  bandwidth is tens of MHz, the added pulse error is of order 1e-4 per push, far below the 4 % excess. The pushed arm, where
  the neighbours are in |1> half the time during the train, shows no change. Not expected to produce it.
* *Leakage* (pushed qubits leaking to |2>, which mostly reads as 1): pushes can leak, but nothing in the raw counts separates
  it, and a neighbour's state would have to change the leak rate. The private read-out model (not recomputed here) puts the excess on level 1, not 2.

---

## Finding B: a neighbour in |2> shifts a clock's precession rate

**Pair.** The same pair on both days: pushed qubit q0 (put in |2> by `rx(pi)` then a tuned 1<->2 pulse), clock q9, wired
directly to q0. The shift is the clock's phase with q0 in |2> relative to the same circuit with q0 at rest, divided by the window.

| | 28 Sep 2026 | 4 Oct 2026 |
|---|---|---|
| run | `witness_headline.py`, 24 tasks, 20:58-20:59 EDT (29 Sep 00:58-00:59 UTC); data from raw_repull | triA 17:13 UTC (40 tasks); q0_last 16:52 UTC (8 tasks) |
| other clocks | q9 alone, all others idle | 106 clocks driven at once |
| windows, shots | 0.5 1 2 3 4.5 6 us; 1000 (rest) / 2500 (|2>) | 0.5 1 2 4 6 us (triA), 2 us (q0_last); 900 |
| q0 -> |2> pulse | 28 Sep tuning | re-tuned on 4 Oct |

**Sign.** The days used different final rotations, so one physical shift reads with opposite sign in angle(H). The script
simulates each circuit exactly and converts to one convention; both days are then negative (the clock's phase falls).
The agreement of signs does not depend on what `rx`/`rz` mean, as long as it is the same on both days.

**Results** (recomputed; shot-noise widths by the delta method).
* 28 Sep: a straight line through the origin on the unwrapped angle, all 6 windows: **-62.10 deg/us**, shot-noise width
  0.41. The claimed +-0.6 is not reproduced (misfit-scaled width is 1.3). **The slope summarises a poor fit** (chi2 = 48 for
  5 d.o.f.): per-window rates are -55.8, -57.6, -54.1, -60.0, -62.2, -64.1, rising with window length, although q0 should be
  decaying out of |2> (lifetime ~21-24 us per the ledger) and the rate should fall.
* 4 Oct, triA, 0.5 / 1 / 2 us: **-36.09 +- 5.40, -34.64 +- 2.77, -41.43 +- 2.14 deg/us** (reproduced). q0_last, an independent run 20 minutes earlier, 2 us: -34.94 +- 2.14.
* **The later windows do not continue the trend** (4 us: +16.2, 6 us: -1.6 deg/us), and at 2 us the clock keeps only 0.54 of its rest amplitude (q0_last 0.56), against 1.0 at 0.5 and 1 us. Three numbers are the clean stretch, not a ladder.
* Like-for-like (0.5-2 us, inverse-variance mean of per-window rates): 28 Sep -54.9 +- 1.3, 4 Oct -38.6 +- 1.6; ratio 0.70; difference 16 +- 2 deg/us.
* With q0 in |1> the clock barely moves (+0.5, +5.9, +1.7 deg/us at 0.5, 1, 2 us). The shift is local: 101 clocks 3+ links from q0 have a median of +1 deg/us.
  Seven other emitter/neighbour pairs (run triF, same evening) show 1 us shifts from -73 to +31 deg/us: 5 of 22 have the opposite sign, 2 are stronger than q0-q9. Sign and size belong to the pair.

**Is the "drift" comparison valid?** The pair is the same, so it compares one pair. But the days differ in more than time: the
1<->2 pulse was re-tuned (how fully q0 reached |2> on 28 Sep is unknown; on 4 Oct the private model gives 0.89 at 0.5 us,
not recomputed here); one clock versus 106 (the ledger's full-room effect on 28 Sep was ~4 %, too small to matter); a
6-window line fit versus three per-window values; and the chip is recalibrated between days. A ~30 % smaller shift on 4 Oct is
a measurement on this pair. "The coupling drifted" is one reading of it, not shown.

**Do known mechanisms predict it?**
* *ZZ / cross-Kerr coupling*: yes in kind. A neighbour in |2> shifts a transmon's frequency, and by more than |1> does. What is
  striking is the ratio: |2> gives 100-170 kHz-equivalent (36-62 deg/us) while |1> gives ~0 (+-1.2 deg/us on 4 Oct), where simple weakly
  coupled transmons give roughly a factor two. A large ratio can come from a near-resonance between q0's 1<->2 and q9's 0<->1
  transitions (the ledger gives 4.295 vs 4.631 GHz; not recomputed) or a tunable coupler. The size cannot be predicted without the chip's Hamiltonian.
* *The change between days*: expected in kind. The shift depends steeply on the detuning between the two qubits, which moves with
  frequency fluctuations and recalibration.
* *Read-out crosstalk*: not relevant to the clock's phase difference, since q0 is read the same way in both arms. (In triA hand Y only, q0 also gets end-of-circuit pulses; q0_last, which does not, agrees.)
* *Leakage*: q0 in |2> is the intended state. Decay out of |2> during the window would make the rate fall with window length; the 28 Sep data show the opposite.

---

## Checks the script makes: 14 OK, 2 DIFFERS
DIFFERS: the 28 Sep width (claimed +-0.6; this code gets 0.41 shot-noise, 1.3 misfit-scaled) and the q0_last width (claimed 2.20, recomputed 2.14).
Everything else above is reproduced to the printed precision.

## Files
`data/rigetti_extra.json` (counts of 1-reads per qubit per arm; task ids and times); `verify_rigetti_extra.py`; `extract_rigetti_extra.py`.
Source scripts in the published folder `heuremen.org/experiments/2026-09-28-rigetti-cepheus/`: `rigetti_triangles.py` (Finding A circuit, 4 Oct triA),
`rigetti_q0_last.py` (the q0_last run), `rigetti_time.py` (helpers `wait`, `f12`), `rigetti_triangle_f.py`.
The 28 Sep writer `witness_headline.py` exists only in private `standoff/` and is not in the published folder; the circuit it builds
(q9: ry(pi/2), wait, [hand Y: rz(-pi/2)], ry(-pi/2); q0: nothing, or rx(pi) then the 1<->2 pulse before the wait, and rx(pi) after) is what the sign simulation in the script uses.
