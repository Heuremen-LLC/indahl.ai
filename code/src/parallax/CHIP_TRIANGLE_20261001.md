# THE CHIP'S THREE CLOCKS, TRIANGULATED

Wayfinder, ~00:50Z 10/1 (THIRD_RUNG_20260928.md Sec62): "you got three clocks and three equations and everything we're doing is three and triangulation, and you can triangulate the time on these chips and haven't been doing it -- start now."

**Scope.** Data on disk only. No new quantum jobs, no network calls. No guess written before running. Script: `parallax/out/the_middle/chip_triangle.py` (numpy only, single process, ~2s runtime, writes `chip_triangle_results.json`).

---

## 1. The legs

### (a) shots <-> microseconds: the unpublished per-shot overhead, SOLVED

The echo has its own clock (an autocorrelation-based "clock" tau, THREE_ON_THREE.md's ruler) measured in shots at two spacings, Marrakesh:

| spacing (rep_delay) | echo clock tau (shots) | error |
|---|---|---|
| 20 us | 249.266 | 24.018 |
| 2000 us | 185.997 | 21.038 |

If this is one real decay time T (us), `tau_shots(g) * (g + OH) = T` at both spacings -- two equations, one unknown, the fixed per-shot overhead OH:

**OH = (tau2*s2 - tau1*s1) / (tau1 - tau2) = 5,800.7 us (point estimate)**

Monte Carlo (200,000 draws, tau1/tau2 resampled from their errors): **median 5,603.8 us**, mean 12,512.3 (mean is meaningless here -- see below). The distribution is heavy-tailed / Cauchy-like: `tau1 - tau2` has ~50% relative error and 4,719/200,000 draws (2.4%) even flip its sign, giving negative "overhead." Percentiles: P5 = 2,433 us, P16 = 3,382, P84 = 11,438, P95 = 24,103 us.

**Consistency with the buzz's alias comb (Sec33):** the comb (+44,441.66 +/- 0.02 Hz + n x 100 kHz) pins a *frequency*, not the fixed part directly -- Sec33 states plainly "the two parts cannot be separated from the records." The only numbers on record to check against are the fixed parts the comb-fit *did* recover directly from execution-span accounting: **8.558 us (Fez, J2-J4)** and **11.17-11.36 us (Kingston)**. Only **2.4%** of the solved-OH distribution sits at or below 11.36 us. The median is **493x** the recorded value; even the 5th percentile is **214x** it.

**Verdict on leg (a): NOT consistent.** The overhead the echo's two spacings demand (to make its own clock read one number) is two to three orders of magnitude larger than the overhead the buzz's execution-time accounting and comb fit actually found. Leg (a) does not close on its own, before any triangle is even built.

### (b) angle-steps <-> shots

GHZ pinata run (Fez, 7/11, `event_horizon_ghz_20260711_121806.json`): top-level `"shots": 4096` -- the standard Qiskit shots-per-circuit count, one per angle setting (24 settings in the tau_third series). **Leg (b): 1 angle-step = 4096 shots.**

### (c) microseconds <-> angle-steps

Chained through (a) and (b). The GHZ run's own shot spacing is **not recorded anywhere in the JSON** (checked every key at every depth: no delay/rep/timing field exists). Assumed IBM's default, 250 us -- the same default THE_BUZZ.md uses for Fez jobs J1 and J4 when unspecified. Flagged as an assumption, not a measurement. In practice it barely matters: the solved OH (~5,600 us) dwarfs a 250 vs. any-other-plausible-default difference by more than an order of magnitude.

---

## 2. The three clocks, one unit (microseconds)

Robust (median, 90%-band-derived sd) pairs used throughout -- not mean/sd, which is dominated by OH's heavy tail (shown for comparison where it matters).

| clock | native | tau (native) | tau, us (median) | error (us) | note |
|---|---|---|---|---|---|
| **carry** (arisen carry) | direct, us | 62.8 us | **62.8** | 13.1 | Marrakesh, PLACED_VS_ARISEN Sec1b; independent of OH |
| **echo** | shots | 249.27 @ 20us / 186.00 @ 2000us | **1,414,237** | 1,455,834 | forced equal by construction (that's how OH was solved) |
| **buzz** | shots | 51.689 @ 20us (J2) | **289,624** | 344,504 | |
| **GHZ** (tau/3) | angle-steps | 6.555 | **154,345,710** | 197,956,350 | via legs (a)+(b), assumed 250us spacing |

Sanity check: the two echo forms (`tau1*(20+OH)` vs `tau2*(2000+OH)`) agree to 1.5e-8 us -- numerically exact, as they must, by construction.

**Plain reading of this table alone:** carry sits at 63 us. Echo, buzz and GHZ -- everything that has to pass through the solved overhead -- land at 10^5 to 10^8 us, with comparably enormous error bars. They are not remotely the same number, and not remotely the same *order* of number.

---

## 3. Closure

### In raw microseconds (forward)

| leg | value (us) | error (us) |
|---|---|---|
| carry - echo | -1,414,166 | 1,455,839 |
| echo - buzz | +1,122,886 | 1,114,344 |
| buzz - GHZ | -154,069,737 | 197,698,126 |
| GHZ - carry (closing leg) | +154,345,642 | 197,956,351 |
| **sum of all four** | **0** (to 1.8e-8) | -- |

The sum is *identically* zero -- a telescoping arithmetic identity for any four numbers arranged in a cycle, true regardless of physics. It is reported and then set aside: it tests nothing. The real question is whether the four clock values agree with each other (whether they're the same number), tested properly below.

**Weighted-mean chi2/dof, full set of 4 (raw us): 0.75.** Leave-one-out chi2/dof: dropping carry -> 0.59, echo -> 0.66, buzz -> 0.78, GHZ -> 0.83. **Nothing stands out in raw us** -- because the errors are proportionately as wild as the differences (all three OH-dependent clocks carry ~100% relative error). This unit is not a useful lens for "which leg carries the residual."

### In series-taus (K_TAU = 0.053767, THE_MIDDLE_PI's own landing-step map, Sec57/58)

The K(rel_err) map converts each clock's *relative* error into a pure number regardless of its native unit or magnitude -- the same machinery already used on yeast/horn/buzz/carry in `calibrated_standoff.py`.

| clock | T (series-taus) | error |
|---|---|---|
| carry | -16.963 | 0.237 |
| echo | -18.846 | 1.131 |
| buzz | -18.934 | 1.147 |
| GHZ | -18.982 | 1.151 |

| leg | value (series-taus) | error |
|---|---|---|
| carry - echo | +1.883 | 1.156 |
| echo - buzz | +0.089 | 1.611 |
| buzz - GHZ | +0.048 | 1.625 |
| GHZ - carry (closing leg) | -2.020 | 1.175 |
| **sum of all four** | **0** (exact) | -- |

**Weighted-mean chi2/dof, full set of 4 (series-taus): 2.60.** Leave-one-out: dropping **carry -> chi2/dof = 0.00** (echo/buzz/GHZ collapse onto one number, -18.92); dropping echo -> 2.78; dropping buzz -> 2.69; dropping GHZ -> 2.63. **Carry is the single removal that closes the loop.**

**Closure residual: carry stands apart from echo/buzz/GHZ by +1.88 to +2.02 series-taus (same sign both ways round the loop), carrying essentially the entire disagreement.** This lines up with THE_CLOCK_GAP_20260930.md (Sec58)'s own finding on a different set of clock-vs-arrow/split pairs: a stable disagreement of the direct-microsecond clock from everything else, of order +1.1 to +1.8 series-taus. This triangle adds a fourth, independent confirmation of that same gap, at a slightly larger size (~1.9-2.0).

---

## 4. Reversed

Reversed/backward-fit numbers exist for only one of the four clocks:
- **echo**: reversal-symmetric by construction (`echo_reversed_results.json`: forward and reversed agree to 1e-10 relative) -- no distinct reversed number exists.
- **GHZ**: explicitly noted in its own record as "reversal-symmetric by construction (ruler property)" -- same value stands for both directions.
- **carry**: no reversed/backward fit exists on disk for the arisen-carry clock (a decay has one direction). Flagged OPEN, forward value reused as a placeholder, not a measurement.
- **buzz**: the only clock with a genuinely different reversed-order fit -- `calibrated_standoff.py`'s buzz_seat116 backward chain, tau = 16.425 +/- 1.719 shots (vs. forward 51.689 +/- 6.981), a different pipeline (message-unit backward chain, not the forward autocorrelation ruler).

Recomputing the closure with buzz's reversed tau:

| leg | forward (series-taus) | reversed (series-taus) | sign flipped? |
|---|---|---|---|
| carry - echo | +1.883 | +1.883 | no (unchanged: neither carry nor echo has a reversed number) |
| echo - buzz | +0.089 | +0.083 | no |
| buzz - GHZ | +0.048 | +0.054 | no |
| GHZ - carry | -2.020 | -2.020 | no (unchanged) |

**No sign flip.** Buzz's reversed tau (16.4 shots) is smaller than its forward tau (51.7 shots) in native units, but once passed through the same ill-constrained OH and the K(rel_err) map, its relative error barely changes (both land near full uncertainty, T ~ -18.9), so the closure residual is essentially untouched by which direction buzz was fit in. The residual is carried by carry vs. everything-that-passes-through-OH, not by forward/backward chain choice on any one clock.

---

## 5. Plain words

**Does the chip have one time, or three?** Three, not one -- but not for a subtle reason. The overhead that would let the echo's own clock agree with itself at two different shot spacings is 5,600-12,500 us, two to three orders of magnitude larger than the ~9-11 us fixed-per-shot overhead IBM's own execution-time accounting and the buzz's alias comb actually recovered. That mismatch means the "one clock, converted through spacing + a fixed overhead" model fails at leg (a), before the triangle is even assembled. Once that inflated overhead is used to bring buzz and the GHZ pinata into microseconds, all three (echo, buzz, GHZ) land within a similarly huge, similarly uncertain range of each other -- and the *direct*, non-derived microsecond clock (the arisen carry, 62.8 +/- 13.1 us) sits apart from all three by a clean, sign-consistent ~1.9 to 2.0 series-taus, the same gap size and sign already found independently in THE_CLOCK_GAP (Sec58).

**The residual, in the units that actually resolve it:** ~1.9 to 2.0 series-taus, same sign forward and reversed, carried entirely by dropping the carry clock (chi2/dof falls from 2.60 to 0.00). In raw microseconds the residual is nominally hundreds of thousands to hundreds of millions of us, but that number is not meaningful on its own -- the errors are just as large, because they all inherit the same ill-constrained overhead.

**The solved overhead:** 5,600-12,500 us (median 5,604, point estimate 5,801), NOT the 8.6-11.4 us the record's own execution-time accounting and comb fit give. Two different methods of getting at "the fixed part of a shot" on this chip disagree by two to three orders of magnitude.

---

## Failed rows / assumptions (counted, not hidden)

1. **OH distribution is heavy-tailed** (ratio of two correlated normals; denominator flips sign in 4,719/200,000 = 2.4% of draws): mean/sd (12,512 +/- 1,776,227) are meaningless; median + 90%-band sd (5,604 +/- 6,587) used throughout instead.
2. **GHZ shot spacing is unrecorded**, assumed 250 us (IBM default, matches THE_BUZZ.md's own J1/J4 default). Not a measurement.
3. **Carry has no reversed fit** on disk; reversed-loop row for carry reuses the forward value, flagged OPEN.
4. **Two on-disk re-runs of the arisen-carry fit disagree** at the ~5% level (59.4 us vs. 62.8 us vs. 63.8 us cited in Sec36d); all share the same 90% band [41.8, 85.0] us, so the choice does not change any call here. Used calibrated_standoff.py's 62.8 +/- 13.13 us for consistency with the reused K(rel_err) machinery.
5. **Raw-microsecond closure is statistically uninformative** (chi2/dof 0.59-0.83 for every leave-one-out) -- reported as a null result, not suppressed; series-taus is what carries the signal.

## Tries

- 6 quantities Monte Carlo propagated (echo tau x2, buzz tau fwd, buzz tau bwd, GHZ angle-tau, carry) x 200,000 draws = 1,200,000 draws.
- 2 closure calls (us) + 2 closure calls (series-taus) = 4 closure computations, each combining 4 legs + 1 (trivial) sum check.
- 10 leave-one-out chi2 calls (5 in each unit: full set + 4 single-drops).
- 1 sanity check (echo two-form numerical identity, passed to 1.5e-8 us).
- 5 failed-row / assumption entries logged, none discarded.
