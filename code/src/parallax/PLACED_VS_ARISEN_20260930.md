# PLACED vs ARISEN — three chips, 2026-09-30, Bones's field hand

No numeric prediction written before running. Scripts: `out/placed_vs_arisen/*.py`. Raw outputs:
`out/placed_vs_arisen/*_results.json`, `run_log_marrakesh.txt`, `run_log_kingston.txt`. Single process, no
multiprocessing, no quantum runs, no money.

Recap of the object: on ibm_marrakesh, a 1 PLACED with a gate is erased by the per-shot reset almost completely
(0.067% residual at 20us — the "echo" test, same-shot: place → reset → look). A 1 that ARISES on its own (a
readout/state error, nobody placed it) is NOT erased the same way — it predicts the next shot's first look,
fading over a few hundred microseconds. This file chases that arisen carry's own clock, checks it on two more
chips, and lines all three up.

---

## 1. Marrakesh — the arisen carry's own clock

### 1a. Reproduction of the corrected series (pipeline check)

Using all 74 readable qubits (SNR≥1.5), same geometry as `pre_measurement.py`, pooled shot-weighted
(lag1-diff − lag20-diff), both E0+E1 files:

| gap (us) | lag1 diff | lag20 diff | corrected carry |
|---|---|---|---|
| 20 | 37.97% | 15.00% | **+22.97pp** |
| 50 | 28.44% | 11.82% | **+16.62pp** |
| 100 | 17.35% | 10.64% | **+6.71pp** |
| 250 | 9.83% | 8.17% | **+1.66pp** |
| 500 | 7.91% | 8.47% | −0.57pp (noise) |
| 1000 | 8.81% | 8.27% | +0.54pp (noise) |
| 2000 | 5.11% | 5.23% | −0.12pp (noise) |

Exact match to the RECONCILIATION numbers in `PRE_MEASUREMENT_20260930.md` — pipeline confirmed correct before
fitting anything.

### 1b. Time constant, with bootstrap error

Fit (log-linear, 20/50/100us window, the three points that are clearly decaying) on this exact series:
**tau = 63.8 us, R² = 0.985** (point estimate).

Bootstrap (500 draws, resample all 74 qubits with replacement, rebuild the whole pooled corrected series each
draw, refit): median tau **62.8 us**, 90% band **[41.8, 85.0] us**, 500/500 draws gave a fittable curve.

- vs. the ~80us look-heat drain clock (pooled tau 81.2us from `PRE_MEASUREMENT_20260930.md` §2): the drain
  clock sits at the *upper edge* of the arisen-carry's bootstrap band. They are compatible but the point
  estimate for the carry (63.8us) runs a bit faster than the drain clock (81.2us) — not proof of two separate
  clocks, but not a clean single-number match either.
- vs. published T1 (this chip, calibration snapshot 9/28, same 74→(blinkers excluded)72-qubit set): median T1 =
  **148.2 us** (IQR 103.7–213.2). The carry clock (63.8us) is well under half the median T1 — same shape of
  "no" as the drain-clock-vs-T1 result in the main pre-measurement writeup (§3 there): whatever governs the
  carry, it isn't tracking the qubit's own energy-relaxation time.

### 1c. Per-qubit carry vs. that qubit's own blink rate (arisen-1 rate at 2000us gap)

Named blinkers q68, q76 separated out per the standing instruction (72/74 qubits remain). Per-qubit carry =
(lag1−lag20 diff) at 20us gap; blink rate = base 1-rate at the 2000us gap (the floor, per RECONCILIATION §3-4).

- n=69 (both a fittable carry value and blink rate): **Spearman rho = −0.004, permutation p = 0.974** (5000
  shuffles). No relationship.
- With the two named blinkers put back in (n=71): rho = −0.014, p = 0.916. Still nothing — q76 itself (one of
  the two blinkers) has an outlier carry value (+47.0pp) but that doesn't move the correlation because its own
  blink rate is also extreme, and one point can't drive a rank correlation over 70+ qubits.

**A qubit's tendency to carry a spurious 1 forward one shot is not explained by how often that qubit blinks at
rest.** These look like two different things riding on the same chip.

### 1d. Is the carry size a shared number, or per-qubit?

Binomial-null test at 20us: simulate every qubit under a single shared (p1, p0) pair (the pooled rates, 33.40%
/ 1.30%, n-matched to each qubit's real sample sizes), 1000 draws.

- Observed per-qubit spread (IQR) of the 20us corrected carry: **35.24pp** (median 9.21pp).
- Simulated (shared-number-only) spread: mean 15.45pp, 90% band [10.72, 20.61]pp.
- **P(simulated spread ≥ observed) = 0.000** (0/1000).

The per-qubit spread is far wider than binomial sampling noise around one shared number can explain. **The
carry is per-qubit, not a single shared magnitude** — different from the *time constant* question in §2 of the
main writeup (where the shared clock shape held up); here it's the *size* of the effect that varies chip-wide,
even with the two loudest blinkers already removed.

### 1e. Same shot, second look: real excitation or mislabel?

For shots whose own first look (m0) reads 1 **and** followed a previous shot's first look reading 1 (the
carried-into population) vs. shots reading 1 that followed a previous 0 (baseline), what fraction also read 1
on the *same shot's* second look (m1)?

| gap (us) | carried-1 → m1 also 1 | n | baseline-1 → m1 also 1 | n |
|---|---|---|---|---|
| 20 | **92.7%** | 1375 | 67.2% | 2747 |
| 50 | **92.0%** | 726 | 67.6% | 2478 |
| 100 | **89.5%** | 315 | 64.2% | 2399 |
| 250 | 80.7% | 88 | 64.1% | 1982 |
| 500 | 64.7% | 51 | 63.0% | 1870 |
| 1000 | 63.0% | 54 | 60.0% | 1833 |
| 2000 | 68.1% | 47 | 62.2% | 1884 |

At short gaps, a "carried" first-look 1 is confirmed by the second look 90%+ of the time — well above the
~60-67% baseline rate at which an ordinary spurious first-look 1 (not preceded by another 1) survives to the
second look. That gap between carried (92.7%) and baseline (67.2%) closes by ~500-1000us, on the same
few-hundred-microsecond clock as everything else here. **Read plainly: the carried 1 looks like a real,
still-excited state at the time it's read, not a one-shot misclassification — it's more likely to still be
there a moment later than an ordinary spurious 1 is.**

---

## 2. Kingston — same test, second chip

Run: `out/20260928_123452/` (J1-J4.npz, meta.json). Jobs: J2 (rep_delay 20us), J3 (rep_delay 1000us), J4
(rep_delay default/unspecified), J1 (default, 4000 shots, also carries two-look D0/D1 pubs). Geometry built
from J1's D0_m1/D1_m1 (4000 shots, most data); 77/78 qubits pass SNR≥1.5.

**The placed-1 arm is effectively absent here.** P0/P1 (used for J2-J4) have no reset between placement and
measurement — they're a plain prepare-and-read (matching the SPAM-style fields already in `per_qubit.json`:
e0, e1, e0_heralded...). Checked directly: median (P1 file − P0 file) same-shot 1-rate is **~98% at every
gap** (J2 98.15%, J3 98.30%, J4 98.05%, J1 98.30%) — that's just "placing 1 and reading it back works," not a
reset-erasure test. So Kingston can't answer the PLACED half the way Marrakesh's E0/E1 (place→reset→look) can.
Running the ARISEN half only, as instructed.

**ARISEN test, P0 (rest) file only** — a 1 read here is never an intended placement, so it's arisen by
construction. Same lag1-vs-lag20 recipe:

| job | gap | lag1 diff | lag20 diff | corrected | shuffle p |
|---|---|---|---|---|---|
| J2 | 20us | +13.62% (n=1520) | +2.55% | **+11.07pp** | **0.000** |
| J3 | 1000us | +0.21% (n=1092) | +0.49% | −0.29pp | 0.673 (noise) |
| J4 | default | +1.11% (n=1102) | +1.31% | −0.20pp | 0.053 |
| J1 | default (4000 shots) | +1.31% (n=2259) | +0.87% | +0.44pp | 0.003 |

**Marrakesh (74 qubits) beside Kingston (77 qubits) at 20us: +22.97pp vs +11.07pp — both real (shuffle
p<0.001), same direction, same order of magnitude, Kingston about half the size.** Kingston has no gap between
20us and 1000us, so its own decay clock isn't resolvable the way Marrakesh's is — the signal is gone by 1000us,
consistent with (not proof of) a similar few-hundred-microsecond window. The "default" gap results (J4 vs J1)
disagree in sign at a scale near the shuffle noise floor (both ~0.2-0.4pp) — read as "faded to noise by the
default gap on this chip," not as two contradictory findings; the exact default rep_delay value used isn't
recorded in the run metadata, so it can't be placed precisely on the x-axis.

**Same-shot second look, J1 D0 (rest arm) only, default gap:** carried-1 shots (n=48) → 58.3% also read 1 on
the second look, vs. base-1 shots (n=2212) → 61.7%. No difference here — but this is the *default*-gap
condition, where Marrakesh's own carried-vs-base gap had already closed (64-68% both, no significant split at
gaps ≥500us). Consistent, not a contradiction: Kingston's D0/D1 don't cover the fast gaps where Marrakesh saw
the real-excitation signature.

---

## 3. Rigetti Cepheus — third chip, different maker, from `FREE_CHECKS_20260929.md` §3

(Not re-run here — numbers as reported there, from `reset_memory.py` / `reset_memory_rows.json.gz`, whole-chip
plus q0 detail.)

- **Whole chip** (107 qubits, 3,438 shot series): failure-after-failure is 231,443 vs. 230,392 expected by
  chance — flat, ~0.5% excess, no chip-wide "reset remembers a leftover rung" pattern in general. The one
  candidate for the 9/26-style pure "failure never follows failure" pattern shows in exactly 1 of ~20
  judgeable series (about 5 expected by chance) — none found, chip-wide.
  
- **q0 specifically** (named before looking): reset clears a leftover **rung 1** cleanly (26 vs 24.6 expected —
  no memory). But a leftover **rung 2** is NOT fully cleared: 64 vs 88 expected (P=0.002); isolating the two
  sequences where a leftover rung 2 causes the next shot to fail (`aba`, `bab`): 25 vs 43 (P=0.001). In `bab`,
  the next shot fails 2.3% after a prior failure vs. 6.4% after a prior success — i.e. **the placed/expected
  state (rung 1) is what gets reliably reset; a second, deeper rung is what leaks through.**

**Laid beside IBM, same shape or not:** loosely the same shape, not force-fit. IBM Marrakesh: the placed 1
(the intended, gate-written excitation, analogous to Rigetti's "rung 1" — the expected post-success state) is
almost fully cleared by reset (0.067% residual). What carries instead is a *different* kind of event — a
spontaneous/arisen 1, not an intentional placement. Rigetti's q0 shows the same split along a different axis:
the reset clears the state a *successful* pulse should leave behind (rung 1) but not a *deeper*, less-expected
state (rung 2). Both chips show "the reset does its one designed job well, and something else — not that job —
carries through." Whether Rigetti's "rung 2" is mechanistically the same kind of thing as IBM's "arisen 1" is
not established by this data — noted as a shape match, not claimed as identity.

---

## 4. The three chips, side by side

| | Marrakesh (IBM) | Kingston (IBM) | Cepheus (Rigetti) |
|---|---|---|---|
| Placed-1 arm available? | Yes (E0/E1, place→reset→look) | No (P0/P1 = plain prepare+read, ~98% same-shot echo — not a reset test) | Yes (rung-1 leftover from a success) |
| Placed 1 survives reset? | No — 0.067% residual at 20us | N/A | Yes for rung 1 — cleared (26 vs 24.6 expected) |
| Arisen/leftover carries? | **Yes** — +22.97pp at 20us, corrected vs lag-20 baseline, shuffle p<0.003 | **Yes** — +11.07pp at 20us, shuffle p<0.001; faded to noise by 1000us | **Yes for rung 2** — 64 vs 88 (P=0.002) on q0; chip-wide pattern not found elsewhere |
| Decay clock | tau = 63.8us (boot 90% band 41.8-85.0us) | Signal at 20us, gone by 1000us (no intermediate gap to fit a tau) | Not a time-gap study; "spells" of 10-100 shots within a task (q62, q61, q41) rather than a fixed clock |
| Carry shared or per-qubit? | **Per-qubit** — spread far exceeds a single-shared-number binomial null (P=0.000) | Not tested (single pooled estimate per job; sample too thin per-qubit) | Per-qubit / per-chip-region — a few loud qubits (q62, q61, q41), not chip-wide |
| Carry vs. own blink rate | No relationship (rho≈0, p=0.97) | Not tested | Not directly comparable metric |
| Real excitation or mislabel? | **Real** — carried-1 confirmed by same-shot second look 90-93% at short gaps vs ~65% baseline | No split seen (default gap only, already past the fast window) | N/A (no same-shot second-look design) |

**Bottom line across all three:** every chip shows the same two-part shape — the reset (or the analogous
"success" transition on Rigetti) reliably clears the thing it was built to clear, but something that arose on
its own, not by an intentional operation, gets through and shows up again shortly after. On IBM this has an
actual clock (tens of microseconds, gone by a few hundred), confirmed on a second chip at smaller magnitude,
and confirmed by a same-shot second look to be a real lingering excitation rather than a readout mislabel. On
Rigetti the same asymmetry appears (expected state cleared, deeper state not) but concentrated in specific
qubits rather than chip-wide, and framed as rungs/spells rather than a time-gap decay — a structurally similar
finding, reached by a different method, not force-matched to the same number.

## Tries counted

Marrakesh: 1 pipeline-reproduction check (7 gaps) + 1 tau fit (point estimate) + 1 bootstrap CI (500 draws,
descriptive) + 2 carry-vs-blink-rate correlation tests (with/without named blinkers) + 1 shared-vs-per-qubit
dispersion test (1000-draw null) + 7 same-shot second-look estimates (descriptive, no p-value computed) = **12
formal tests/estimates**, of which 3 carry an explicit p-value (2 correlation tests, 1 dispersion test).

Kingston: 4 placed-echo estimates (descriptive) + 4 arisen-carry tests with shuffle backgrounds (each its own
p-value) + 1 same-shot second-look estimate (descriptive) = **9 formal tests/estimates**, of which 4 carry an
explicit p-value.

Rigetti: not re-run; numbers cited from `FREE_CHECKS_20260929.md` §3, which already reports its own tries count
there.

Total new p-values generated this pass: **7** (2 Marrakesh correlation, 1 Marrakesh dispersion, 4 Kingston
arisen-carry). None were run against a Bonferroni bar in isolation here since each answers a distinct,
pre-specified question from the task rather than a multiple-comparisons sweep; the two clearly real ones
(Marrakesh dispersion p=0.000, Kingston J2 arisen p=0.000) would survive any reasonable correction at this
count.
