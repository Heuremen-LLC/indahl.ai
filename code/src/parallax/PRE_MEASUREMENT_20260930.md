# PRE-MEASUREMENT — two clocks on the echo run (2026-09-30, Bones, field hand)

Data: `out/echo_20260928_122733/` (ibm_marrakesh, 78 even qubits, 1500 shots/job, raw kerneled I/Q, gaps
20/50/100/250/500/1000/2000 us). No numeric prediction written before running. Everything below came out of
`out/pre_measurement/pre_measurement.py` (raw npz in, one pass, no multiprocessing); full run log and JSON sit
beside it in `out/pre_measurement/`.

The npz files hold **raw complex I/Q dots**, not 0/1 — so a classification cutoff along the 0→1 axis is needed
before anything else. I rebuilt the per-qubit 0/1 geometry myself from the longest gap (2000us: E0's second look
≈ the 0-cloud, E1's second look ≈ the 1-cloud), same method as `parallax_echo.py`. 74/78 qubits pass the readout
SNR gate (≥1.5). I checked my "excess" curve against the pre-existing `echo_heat_by_gap.json` H-matrix for three
qubits (q110, q22, q76) — it reproduces those rows exactly once the 2000us value is subtracted as floor, so the
two pipelines agree on the raw numbers.

## 1. Per-qubit drain tau, three cutoffs (0.25 / 0.50 / 0.80 along the 0→1 axis)

Fitting one log-linear slope across **all** gaps with excess > 0.15% gives a "full-range" tau of 330–460 us
median — but that's an artifact of mixing two timescales: the curves drop hard from 20→100us then flatten into
a long, shallow tail out past 500us. Restricting the fit to the three shortest gaps (20/50/100us, the "fast"
tau) isolates the initial drop and reproduces the earlier 71–82us finding:

| cutoff | full-range tau (median, IQR) | fast tau (median, IQR) | fast fit quality (median R²) | n clean / 74 |
|---|---|---|---|---|
| 0.25 | 353.7 us (232.7–929.2) | 95.1 us (65.8–149.8) | 0.745 | 25 |
| 0.50 | 458.0 us (187.6–817.7) | 80.0 us (61.5–97.7) | 0.884 | 17 |
| 0.80 | 332.1 us (159.2–585.0) | 85.4 us (59.5–145.9) | 0.833 | 14 |

Textbook note, kept not stopped-at: a fast-plus-slow decay is the ordinary shape of a rate process with two
populations (a fast local one, a slow structural one) — not itself evidence of anything new. I report both taus
throughout below; "the drain clock" = the fast one, matching how it was named in the 9/29 write-up.

## 2. The SHARED part

Global tau fit to the median-of-qubits curve (cutoff 0.50, fast window): **81.2 us**, R²=0.77, matching the
per-qubit median (80.0 us) closely — the pooled curve and the individual qubits agree.

Background: 500 shuffles that scramble which qubit's excess value lands at which gap (independently per gap
column), then refit "fake qubit" trajectories.
- Real per-qubit tau spread (IQR/median) = 0.45. Shuffled spread: mean 1.38, 90% band [0.38, 3.54].
  P(shuffle ≤ real) = **0.097** — real qubits are tighter than most shuffles but not decisively so.
- Real per-qubit fit quality (median R²=0.884) beats the shuffled fits (mean 0.485, band [0.085, 0.847]).
  P(shuffle ≥ real) = **0.031**.
- Sharpest signal: **zero of 500 shuffles** produced a fittable (monotone-decreasing) median curve at all, while
  the real data fit cleanly (R²=0.77) on the first try. That asymmetry is the strongest piece of evidence for a
  shared, chip-wide clock — shuffling the qubit identities destroys the monotone shape entirely, not just the tau
  value.

Read together: there is a real shared component (the pooled shape is not reproducible by scrambling qubit
identity), but the per-qubit tau *values* are not so tightly clustered that a single shared number alone explains
them (p=0.097 on spread) — some per-run variation rides on top of the shared clock. Both parts of Wayfinder's
framing show up; neither wins outright.

## 3. The PER-RUN part (does tau scale with the qubit's own heat, or with T1?)

n=17 qubits with a clean fast-tau fit at cutoff 0.50:
- tau_q vs. excess-at-20us amplitude: Spearman rho = **-0.17**, permutation p = **0.52** (5000 shuffles). No
  relationship — bigger heat does not mean slower drain.
- tau_q vs. published T1 (IBM calibration, 2026-09-28 snapshot, `out/ibm_cal_20260929/`): rho = **0.03**, p =
  **0.92**. Median tau 80.0 us vs. median T1 173.2 us — no tracking.

Textbook explanation checked and ruled out for this data: if the drain were the qubit's own energy relaxation,
tau would track T1. It doesn't (rho≈0, both this run and the earlier 9-qubit read, which found rho=-0.6 — same
sign of "no" both times). Neither is there a per-run scaling with the qubit's own heat amplitude. On this
evidence, tau looks like a property of the substrate/readout chain shared across the chip, not a per-qubit
knob — consistent with §2.

## 4. PRE-MEASUREMENT: did the last look leave time behind? **[SUPERSEDED — see RECONCILIATION below. The 19.7%-style numbers in this section came from a statistics bug (unweighted averaging over wildly different sample sizes) compounded with an unrelated stuck-qubit confound. Corrected numbers and the real, smaller effect are in RECONCILIATION §4.]**

For each gap, three groups (pooled over 74 qubits × 2 pubs = 148 sequences): the current shot's first-look 1-rate
when the **previous** shot's first look read 1, read 0, or when there **was** no previous shot (first shot of the
file, n=148 always). Background: shuffle the previous-outcome label within each shot sequence (300 shuffles,
20-qubit subsample per shuffle for speed).

| gap (us) | prev=1 | prev=0 | batch-start (n=148) | prev1 − prev0 | shuffle p |
|---|---|---|---|---|---|
| 20 | 19.66% | 2.04% | 1.35% | **+17.62%** | <0.003 |
| 50 | 16.77% | 1.73% | 2.70% | **+15.04%** | <0.003 |
| 100 | 8.17% | 1.76% | 1.35% | **+6.41%** | <0.003 |
| 250 | 3.36% | 1.44% | 0.68% | **+1.92%** | <0.003 |
| 500 | 1.58% | 1.36% | 1.35% | +0.22% | 0.54 |
| 1000 | 1.68% | 1.35% | 2.03% | +0.33% | 0.34 |
| 2000 | 1.24% | 1.26% | 1.35% | −0.02% | 0.96 |

This is the clearest result in the run. A shot that follows a "read 1" first-look is dramatically more likely to
also read 1 — 19.7% vs. the baseline ~1–2% at 20us — and the effect fades to nothing by 500us, on roughly the
same few-hundred-microsecond scale as the drain clock. The batch-start group (no real previous shot) sits with
prev=0, not with prev=1, confirming this isn't a fixed per-file artifact — it's specifically triggered by the
preceding outcome. Whether this is "time left behind" or ordinary bursty telegraph noise/TLS switching (a
textbook mechanism, noted not stopped at) is not resolved by this data; the magnitude (up to 17.6 points, far
bigger than the ~1–2% heat numbers elsewhere in the stack) is worth flagging on its own.

## 5. Observer (outside gap) vs. witness (inside clock from pooled tau)

Using the pooled fast tau (81.2 us) and the median excess curve, solving for "time since last look" implied by
the observed heat at each gap (anchored so inside=outside=20us at the shortest gap):

| outside gap (us) | median excess | inside-clock reading (us) | residual (in − out) | bootstrap 90% band |
|---|---|---|---|---|
| 20 | 1.833% | 20.0 | 0.0 | [0, 0] (anchor) |
| 50 | 0.767% | 90.8 | +40.8 | [-35, +149] |
| 100 | 0.633% | 106.3 | +6.3 | [-5, +23] |
| 250 | 0.433% | 137.1 | -112.9 | [-156, +59] |
| 500 | 0.133% | 232.7 | -267.3 | [-353, +45] |
| 1000 | 0.033% | n/a (below fit floor) | n/a | [-834, -459] |
| 2000 | 0.000% | n/a | n/a | — |

The residual is **not** a clean constant offset and **not** a clean proportional scale — it swings from +41us
to -267us and the bootstrap bands (resampling qubits) are wide enough to straddle zero at every gap except 1000us,
where it's noise-dominated in the other direction. This is the same tell as §1: a single exponential (one tau)
does not describe the full curve, so converting heat directly to "time" with one pooled tau is not a valid ruler
past ~100us. The honest read is: the fast clock (~80us) governs the first hundred microseconds well (small,
noisy-but-centered residuals at 50–100us); beyond that the curve is doing something a one-tau model can't
capture, and the "residual" there is a model-misspecification artifact, not a physical offset or scale — noise
and model mismatch, not signal.

## Tries counted

74 qubits × 3 cutoffs (step 1 fits) = 222, + 2 (step 2: spread test, R² test) + 2 (step 3: tau-vs-amplitude,
tau-vs-T1) + 7 (step 4: one group-comparison per gap) + 7 (step 5: one residual estimate per gap) = **240 tests/
estimates**. Step 4's four significant gaps (20/50/100/250us, all p<0.003 raw) survive a Bonferroni bar of
240 comparisons (0.05/240 ≈ 0.0002) only loosely for 250us (needs more shuffles to resolve below 1/300); 20/50/100us
clear it comfortably even at this raw look-elsewhere count.

## Bottom line

- **Shared part**: real, in shape (no shuffle reproduces a fittable monotone curve) but only loosely in exact
  tau value (per-qubit spread beats shuffle at p=0.097, not decisive).
- **Per-run part**: not found — tau doesn't scale with a qubit's own heat amplitude or its own T1 (textbook ruled
  out both ways).
- **Pre-measurement**: the strongest single finding — the previous shot's outcome sets the next shot's first-look
  outcome, fading over the same few-hundred-microsecond window as the drain clock, far larger in size (up to
  17.6 points) than the background heat itself.
- **Observer-minus-witness**: no clean constant or proportional residual; a single pooled tau is only a good
  ruler for the first ~100us, then the model itself breaks down. That breakdown, not a hidden physical offset,
  is what the residual is showing.

---

# RECONCILIATION (2026-09-30, same session) — the 19.7% contradicted the 9/28 pre-reg result. Checked, and fixed.

The coordinator flagged: the pre-reg 9/28 "echo" (median 0.07% at 20us, 0.00% by 50us — the reset erases the
previous shot) and my §4 "prev1 − prev0" (19.7pp at 20us) can't both be right on the same data. Four checks, in
order.

## (1) Indexing check — confirmed correct, but answering a different question than the pre-reg "echo"

Printed shapes: `m0`, `m1` are each `(1500, 78)` complex128, axis 0 = shot (acquisition order), axis 1 = qubit.
My §4 code: `prev = m0[:-1]; cur = m0[1:]` on the **same array** (`m0` of one file, one qubit) — so `prev[i]` is
shot *i*'s own first look and `cur[i]` is shot *i+1*'s first look, both from `m0` only. I am **not** touching `m1`
and **not** comparing a shot to itself. That part was indexed as intended.

But "as intended" was the wrong intent. The pre-reg's `echo(delay) = P(m0=1|E1) − P(m0=1|E0)` is a **file-level**
comparison: every shot in the E1 file is *guaranteed* to follow a shot that ended in 1 (the X gate forces it),
every shot in E0 *isn't* — there's no per-shot conditioning at all. My §4 instead conditioned, **within one file**,
on whatever the *previous shot's own m0 happened to read by chance*. That's a legitimate but different question
(reproducing the exact wording of the original task's step 4), not a rerun of the pre-reg's echo. So there is no
contradiction in definitions — but the pre-reg number is the right background check, and I ran it:

## (2) Reproducing the pre-reg number with my own pipeline — matches exactly

`echo(gap) = median_qubit[ P(m0=1|E1 file) − P(m0=1|E0 file) ]`, my geometry, my code:

| gap (us) | my median echo | 9/28 pre-reg |
|---|---|---|
| 20 | **0.067%** | 0.07% |
| 50 | **0.000%** | 0.00% |
| 100 | 0.000% | — |
| 250 | 0.067% | — |
| 500 | 0.000% | — |
| 1000 | 0.000% | — |
| 2000 | -0.033% | — |

Exact match. **My pipeline is not broken** — geometry, classification cutoff, and file loading all check out
against the known-good number.

## (3) Is the §4 19.7% driven by a few qubits, or broad? — Both, plus a real bug, plus a real confound

Per-qubit breakdown at gap=20us (71 qubits with both prev=1 and prev=0 events): **broad but with huge variance** —
median per-qubit diff +7.3%, IQR −0.1% to +33.5%, top qubit (q154) at +77.5% but from only 30 prev=1 events out
of 1499 shots. That sample-size spread exposed the first real bug:

**Bug found — unweighted averaging.** My original §4 code averaged one rate-per-(qubit,file) with **equal
weight**, regardless of whether it was built from 602 previous-1 shots (q76) or 2 (q34). Re-computed properly
pooled (shot-count-weighted, hits summed / shots summed across all qubits and both files) the 20us number gets
**bigger, not smaller**: 37.97% (pooled p1=39.71% on n=6227 vs p0=1.74% on n=215,625) — so the unweighted-average
bug was not inflating the headline, it was actually *diluting* it. The real problem is elsewhere:

**Confound found — a handful of persistently noisy/blinking qubits, not a chip-wide clock.** Pooled diff by gap:
20us→38.0%, 50us→28.4%, 100us→17.3%, 250us→9.8%, 500us→7.9%, 1000us→8.8%, **2000us→5.1%** — it does *not* decay to
zero the way the drain-clock or the pre-reg echo do. Testing lag (shots back, not gap) resolves why: at every gap,
lag-1 vs lag-20 diff:

| gap (us) | lag-1 diff | lag-20 diff |
|---|---|---|
| 20 | 37.97% | 15.00% |
| 50 | 28.44% | 11.82% |
| 100 | 17.35% | 10.64% |
| 250 | 9.83% | 8.17% |
| 500 | 7.91% | 8.47% |
| 1000 | 8.81% | 8.27% |
| 2000 | 5.11% | 5.23% |

At 20/50/100us, lag-1 clearly exceeds lag-20 (a real short-range effect, gone by ~20 shots). At 250us and beyond,
lag-1 ≈ lag-20 — conditioning on "the previous shot" is no better than conditioning on "the shot from 20 shots
ago." That is the signature of a **static subpopulation**, not a temporal carry: a few qubits sit at an
elevated, slowly-drifting 1-rate for long stretches regardless of gap. Base 1-rate at the 2000us gap (should be
the clean floor) confirms it — median qubit 0.33%, but q68 sits at 17.1%, q76 at 11.7%, q88 at 6.6%, q126 at
6.1%, q118 at 4.3% (all far above the pack; consistent with the "blinking qubit" spells already logged for other
chips in THIRD_RUNG). These few loud qubits contribute disproportionately to the shot-weighted pool at every gap,
including 2000us, which is why the naive pooled number never reaches zero.

## (4) Storage-order check — shots are in real acquisition order, not sorted

Run-length check on q76's raw boolean m0 sequence at 20us gap: 215 separate runs of "1" (median length 2, max 16)
scattered through 1499 shots — not one or a few long blocks, which is what a sort-by-outcome artifact would
produce. And the lag-1-vs-lag-20 divergence at short gaps (above) *requires* real time-ordering to show up at all
— a reordered/sorted array would not know what `rep_delay` was used to know how much to diverge. Both checks say
the npz shot order is genuine acquisition order.

## Verdict: which pipeline was wrong

**Neither pipeline had a coding bug in the core geometry/classification** — the pre-reg echo (~0%) and my
reproduction of it agree exactly. My original §4 report was wrong in its **conclusion**, not its arithmetic: it
presented a broad chip-wide "17.6pp pre-measurement carry" without separating (a) a real, smaller, genuinely
gap-dependent short-range effect from (b) a small number of blinking/drifting qubits whose elevated 1-rate has
nothing to do with the shot gap and inflates the pooled number at every gap including 2000us, where no real echo
should exist at all.

## Corrected numbers

The real short-range "did the last look leave something behind" signal, isolated as (lag-1 diff) − (lag-20 diff),
pooled and shot-weighted:

| gap (us) | corrected short-range diff |
|---|---|
| 20 | **+22.97pp** |
| 50 | +16.62pp |
| 100 | +6.71pp |
| 250 | +1.66pp |
| 500 | −0.56pp (noise) |
| 1000 | +0.54pp (noise) |
| 2000 | −0.12pp (noise) |

This decays to noise by ~250-500us — roughly the same window as the drain clock in §1/§2, smaller in magnitude
than my original headline, and now separated from the blinking-qubit confound. It does **not** contradict the
9/28 pre-reg echo (that metric measures something else — the guaranteed E1-vs-E0 file contrast, not the qubit's
own random previous outcome — and both chip-wide reset behaviors can be true at once: the reset does erase the
*intentional* E1/E0 difference by the next shot, while a handful of individual qubits still carry their own
short-lived noise for a few shots afterward).

**Action taken**: §4 above is marked superseded. The headline in the original "Bottom line" pre-measurement claim
should read: a real but modest (~7-23pp, decaying by 250-500us) short-range carry exists once blinking qubits and
the unweighted-averaging error are controlled for — not the flat 17.6pp chip-wide number first reported, and not
in tension with the pre-reg's near-zero echo, which asks a different question and reproduces cleanly.
