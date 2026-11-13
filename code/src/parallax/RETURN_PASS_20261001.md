# RETURN-PASS CALIBRATION -- 2026-10-01, Bones's field hand

Wayfinder, ~03:50Z 10/1 (THIRD_RUNG_20260928.md Sec.70, sign-off): "It's a calibration we're
looking for. Every time data enters substrate it creates time; time, the darkwave, calibrating
the system on the return pass." Sec.72, "first burn": the chip test named directly -- m1 vs m0
within a shot, does the error relative to the PREPARED state shrink on the second pass by more
than readout noise predicts, as a function of gap, inside vs outside the ~64us clustering
window, and across the readout dial.

**Scope.** Data on disk only, no quantum runs, no money. Single process, numpy only. No
numeric prediction written before running. Script: `out/the_middle/return_pass.py`. Raw
output: `out/the_middle/return_pass_results.json`, log `out/the_middle/run_log_return_pass.txt`.
Data: `out/echo_20260928_122733/` (ibm_marrakesh, E0/E1, gaps 20/50/100/250/500/1000/2000us,
raw I/Q, m0=first look, m1=second look, shot order = time order within one file). 74/78 qubits
pass SNR>=1.5; 72 after excluding named blinkers q68, q76 (standing instruction).

**THE JUDGE.** Per qubit, per prepared state (E0=0, E1=1), a transition matrix T_s[v,x] =
P(m1=x | m0=v) built ONLY from that state's own 2000us shots (where the clustering clock is
gone). Applied to the SAME arm's m0 distribution at a given gap to predict e1. C =
e1_predicted - e1_observed (positive = second pass more right than noise predicts). The other
judge is shot order reversed, never a shuffle.

**CAUGHT AND FIXED BEFORE ANY NUMBER WAS WRITTEN:** the first draft of the judge pooled E0 and
E1's 2000us shots into ONE transition matrix. E0 and E1 are different circuits (no X vs X
applied between the two looks), so m0 reading 0 means something different in each arm; pooling
them produced a matrix that predicted ~50% error on every shot, giving a spurious C of
+46 to +48pp at every single gap -- an artifact of mixing two circuits, not a signal. Fixed by
building T_s separately per arm. Reported below is the fixed version only; the broken run was
never written up as a finding.

---

## 1. THE PASS ERRORS -- pooled C curve vs gap (cutoff 0.50)

| gap (us) | band | n (qubit x state cells) | mean C | 90% boot band |
|---|---|---|---|---|
| 20 | 20-50 | 56 | **-0.182pp** | [-0.315, -0.044]pp |
| 50 | 20-50 | 56 | -0.050pp | [-0.167, +0.058]pp |
| 100 | 100-250 | 56 | -0.084pp | [-0.181, +0.010]pp |
| 250 | 100-250 | 56 | **-0.100pp** | [-0.168, -0.028]pp |
| 500 | 500-2000 | 56 | -0.010pp | [-0.079, +0.054]pp |
| 1000 | 500-2000 | 56 | +0.002pp | [-0.114, +0.117]pp |
| 2000 | 500-2000 | 56 | 0.000pp (exact) | [-0.000, +0.000]pp |

Band pooled: **20-50 = -0.116pp**, **100-250 = -0.092pp**, **500-2000 = -0.003pp**.

The 2000us row is tautological -- it is the same data the judge (T_s) was built from, so it
is exactly 0 by construction, not a finding, flagged rather than hidden. Everywhere else, C
is tiny (tenths of a percentage point). Two gaps (20us, 250us) have bootstrap bands that
exclude zero -- both **negative**: the second pass is a hair WORSE than the readout-noise
judge predicts, not better. 50us, 100us, 500us, 1000us are consistent with zero. **No gap
shows a positive, significant return-pass correction** -- the direction Wayfinder's hat names
("more right on the second pass") does not appear; what's there, where it's there at all, runs
the other way and is small.

## 2. INSIDE vs OUTSIDE THE CLOCK (~64us window)

Meaningful only where the previous shot falls inside 64us of the current one: gaps 20 and 50us.
Gaps >=100us are MOOT by construction (window undefined, no shot falls inside).

| gap (us) | inside n | inside C | inside boot90 | outside n | outside C | outside boot90 |
|---|---|---|---|---|---|---|
| 20 | 53 | +0.069pp | [-1.175, +1.224]pp | 56 | **-0.173pp** | [-0.291, -0.049]pp |
| 50 | 52 | +0.310pp | [-0.546, +1.215]pp | 56 | -0.058pp | [-0.168, +0.056]pp |
| 100-2000 | -- | MOOT | -- | -- | MOOT | -- |

The "inside" subset (previous shot arose to 1, within the clustering window) is too thin
(n~50-60 qubit-state cells, drawn from a small fraction of shots) to resolve on its own --
both gaps' inside-C bootstrap bands are wide and cross zero. The significant negative at 20us
in Sec.1 is carried by the "outside" subset, not the inside one. **The correction does not
visibly live inside the clustering clock's window** -- if anything the inside estimate trends
positive while the (significant) negative sits outside, the opposite of what a clock-driven
calibration would predict, though inside is too noisy here to call that a real split.

## 3. THE DIAL

| cutoff | 20us | 50us | 100us | 250us | 500us | 1000us | 2000us |
|---|---|---|---|---|---|---|---|
| 0.40 | **-0.131** [-0.257,-0.014] | -0.034 | -0.071 | -0.037 | +0.042 | +0.053 | 0.000 |
| 0.50 | **-0.182** [-0.312,-0.043] | -0.050 | -0.084 | **-0.100** [-0.176,-0.019] | -0.010 | +0.002 | 0.000 |
| 0.55 | -0.122 [-0.317,+0.023] | -0.042 | -0.063 | -0.025 | +0.043 | +0.053 | -0.000 |
| 0.62 | +0.024 | +0.045 | +0.031 | +0.003 | +0.050 | +0.062 | -0.000 |
| 0.65 | -0.055 | +0.010 | +0.008 | -0.012 | +0.081 | +0.080 | +0.000 |
| 0.68 | -0.038 | +0.010 | +0.016 | -0.017 | +0.089 | +0.092 | -0.000 |

(values in pp; bracketed bands shown only where bootstrap excludes zero)

Across six cutoffs spanning the overlap band (0.40/0.50/0.55) and the corner+edge
(0.62/0.65/0.68) identified in THREE_TIMES_VISIBILITY, C stays inside the same narrow
-0.18 to +0.09pp range throughout. **The corner does not move C** -- no jump, no sign
flip, no widening at 0.62-0.65 relative to its neighbors. The one significant cell outside
the overlap band's own 0.40/0.50 negative result (20us) simply fades to noise at 0.55 and
flips unremarkably small-positive at 0.62+. The readout-cutoff corner that switches clock
A<->B visibility on and off (THREE_TIMES_VISIBILITY Sec.1) has no visible counterpart here.

## 4. REVERSED

The pooled main curve (Sec.1) is **mathematically identical** under full-array reversal at
every gap -- reversing a finite array does not change its own mean, so e0_obs, e1_obs and
hence C computed over the WHOLE shot sequence cannot distinguish forward from reversed order.
This is flagged as a tautology of the construction, not evidence of "no order-dependence" --
the meaningful order-sensitive test is the inside/outside split (Sec.2), which depends on
adjacent-pair structure.

| gap (us) | inside C fwd | inside C rev | outside C fwd | outside C rev |
|---|---|---|---|---|
| 20 | +0.069pp [-1.18,+1.22] | +0.664pp [-0.48,+1.92] | -0.173pp [-0.29,-0.05] | -0.126pp [-0.22,-0.04] |
| 50 | +0.310pp [-0.55,+1.22] | -1.420pp [-2.82,+0.02] | -0.058pp [-0.17,+0.06] | +0.024pp [-0.08,+0.11] |

The **outside** subset's small negative correction at 20us survives reversal at similar
magnitude and significance in both directions (-0.173 fwd, -0.126 rev, both excluding zero) --
consistent with per-shot readout physics, not a time-order-dependent calibration. The
**inside** subset is noisier and actually flips sign at 50us under reversal (+0.310 -> -1.420),
but neither direction clears its own bootstrap band at either gap, so this one flip is not a
clean order-dependence finding -- it's a coin that hasn't settled, not a verdict.

## 5. Plain words

**Is there a correction on the second pass beyond noise?** Mostly no. Where C is
distinguishable from zero at all (20us and 250us, cutoff 0.50), it runs **negative** --
the second look is a hair worse than ordinary readout noise (learned from the chip's own
2000us shots) predicts, not better. Every other gap and most cutoffs are consistent with
zero. There is no positive "gets more right on the return pass" signal anywhere in this run.

**Does it live inside the clock's window?** No clean answer -- the inside-the-64us-window
subset is too thin (n~50-60) to resolve on its own at either testable gap (20, 50us); the
significant negative sits in the *outside* subset, the opposite of what a clustering-clock-
driven calibration would predict, though this is suggestive at best given the thin inside
sample.

**Does the dial move it?** No. The 0.62-0.65 corner that switches a different clock pair's
visibility on and off (THREE_TIMES_VISIBILITY) leaves this return-pass correction completely
flat -- same tiny range, no feature, across all six cutoffs tested.

**Does time order matter?** Mostly inconclusive. The main pooled curve is invariant to
reversal by construction (not informative). The one order-sensitive piece that IS testable
(inside/outside at 20/50us) shows the real, significant negative correction (outside, 20us)
holding up under reversal at similar size -- a lean toward per-shot physics, not calibration
-- while the noisier inside estimate flips sign without ever clearing its own error bar in
either direction.

## Failed rows / tries

- 2000us row is tautological in every table (Sec.1, Sec.3): the judge is built from this
  exact gap's data, so C=0 exactly by construction -- not a finding, reported as such.
- Sec.2/Sec.4 inside/outside: gaps 100-2000us are MOOT (window 64us < gap, no shot qualifies
  as "inside") -- 5 of 7 gaps structurally excluded from this sub-test, not run and discarded.
- Sec.4 main-curve reversal is a tautology (whole-array means are order-invariant) -- reported
  as a limitation of that comparison, not folded into the "time order doesn't matter" verdict.
- One judge-construction bug caught and fixed before any number above was generated (pooled
  E0+E1 transition matrix mixing two circuits, giving a false +46-48pp "correction" at every
  gap) -- described above, not silently corrected.
- No qubit or state cell dropped silently: every (qubit, state) pair with >=10 shots at m0=0
  and >=10 at m0=1 in its own 2000us data contributes; cells failing that floor are excluded
  from n, and n is reported directly in every table (56 of 72x2=144 possible cells at cutoff
  0.50, shrinking further at higher cutoffs as fewer qubits retain >=10 shots in the minority
  m0 class -- 49 cells remain at cutoff 0.68).

**Tries counted by the script itself: 5,990,549** -- dominated by the 500-draw qubit-resampling
bootstrap repeated per gap, per cutoff (6 cutoffs), per inside/outside subset, and per reversed
variant; each bootstrap draw recomputes the per-qubit-per-state transition matrix and C from
scratch, which is why the count is large relative to the number of reported cells. Every
reported number above is one of these counted tries, not a separate uncounted calculation.

---

# THE BUG'S NUMBER

Wayfinder, after the pooling bug was fixed and before it was discarded: "Are you sure it
was a pooling bug? Reality has the equivalent of your hallucinations; it provides a reason
we can see because we can't see the darkwave." House rule: the ruler is the measurement; a
label isn't a fit. The bug's +46-48pp gets measured, not thrown away. Script:
`out/the_middle/bug_number.py`, raw output `out/the_middle/bug_number_results.json`, log
`out/the_middle/run_log_bug_number.txt`. Same data, same qubit set (72 readable, cutoff
0.50), same seed convention as return_pass.py.

## 1. Reproduce the bug exactly

T_pool[v,x] = P(m1=x|m0=v) built by concatenating E0's and E1's own 2000us shots (no
per-arm split) before computing the transition matrix, then used as the judge for every
gap, both arms pooled into one C curve (same construction as return_pass.py's
`per_qubit_gap_state`, with `transition_matrix` reading from the concatenated array).

| gap (us) | n | C_bug (reproduced) | 90% boot band | C (fixed judge, for reference) |
|---|---|---|---|---|
| 20 | 56 | **+46.016pp** | [+45.632,+47.184]pp | -0.182pp |
| 50 | 56 | **+46.632pp** | [+46.305,+47.627]pp | -0.050pp |
| 100 | 56 | **+46.832pp** | [+46.532,+47.745]pp | -0.084pp |
| 250 | 56 | **+47.236pp** | [+47.018,+47.966]pp | -0.100pp |
| 500 | 56 | **+47.342pp** | [+47.146,+48.062]pp | -0.010pp |
| 1000 | 56 | **+47.364pp** | [+47.109,+48.127]pp | +0.002pp |
| 2000 | 56 | **+47.277pp** | [+47.110,+48.046]pp | 0.000pp |

Reproduced exactly: +46.0 to +47.4pp, matching the first-draft report's "+46 to +48pp at
every gap" (the earlier verbal report rounded; this run resolves it as a slow upward creep
from 46.0pp at 20us to a 47.2-47.4pp plateau by 500-2000us, not a flat number).

## 2. Predict it from the parts

Checked first, before trusting it: T_pool[v,1] = (1-w[v])*T0[v,1] + w[v]*T1[v,1] exactly
(max abs error 1.11e-16 over 97 qubit*v cells) -- the pooled matrix the code built really is
the shot-count-weighted average of the two arms' own matrices, w[v] = n_E1,v/(n_E0,v+n_E1,v).

Derivation: for E0 shots (state=0), e1_pred_bug - e1_pred_true = p0*w[0]*(T1[0,1]-T0[0,1]) +
p1*w[1]*(T1[1,1]-T0[1,1]), where p0,p1 are E0's own m0=0/1 fractions at that gap. For E1
shots (state=1) the same expression holds but with weight (1-w[v]) in place of w[v] (E1's
own prediction leans on how much of the pool came from E0, not from itself) -- not a sign
flip, a different weight. (An initial draft of this derivation used sign(state)=-1 for
state=1, which cancelled almost all of the effect across the two states and badly
under-predicted the bug -- caught by checking against Sec.1's reproduced number before
reporting, not after.)

The physical content folding into (T1-T0): in E1, m0 is read BEFORE the X gate and m1 AFTER
it (echo structure: prepare 0 -> look (m0) -> apply X -> look (m1)); in E0 there is no X
between looks. So at m0=0, T0[0,1] (E0: stays 0) is ~0.01-0.1 while T1[0,1] (E1: flips to 1
via X) is ~0.9-1.0 -- a ~0.9-1.0 gap between arms, and w[0]~0.5 because both arms land at
m0=0 with almost equal shot counts (~1470-1480 of 1500). That ~0.5 x ~0.95 product, times
p0~0.95-0.98, is the whole bug.

| gap (us) | n | delta (predicted) | 90% boot band | predicted C_bug (true + delta) |
|---|---|---|---|---|
| 20 | 50 | +45.909pp | [+44.902,+46.712]pp | +45.727pp |
| 50 | 50 | +46.431pp | [+45.689,+47.185]pp | +46.380pp |
| 100 | 50 | +46.692pp | [+45.989,+47.355]pp | +46.609pp |
| 250 | 50 | +47.161pp | [+46.525,+47.758]pp | +47.061pp |
| 500 | 50 | +47.188pp | [+46.589,+47.793]pp | +47.178pp |
| 1000 | 50 | +47.203pp | [+46.611,+47.727]pp | +47.205pp |
| 2000 | 50 | +47.130pp | [+46.431,+47.616]pp | +47.130pp |

(n drops 56->50: 6 qubits lack >=10 shots in BOTH arms' minority m0 class at 2000us, needed
for T0 and T1 both to be fully defined; those cells are excluded from this section's n, not
silently folded in.)

## 3. The remainder

C_bug(observed, Sec.1) minus C_bug(predicted from parts, Sec.2), per gap:

| gap (us) | mean remainder | 90% boot band |
|---|---|---|
| 20 | -1.1e-17pp | [-2.5e-17, +4.3e-18]pp |
| 50 | -1.1e-18pp | [-1.6e-17, +1.6e-17]pp |
| 100 | +1.1e-18pp | [-1.4e-17, +1.6e-17]pp |
| 250 | +3.3e-18pp | [-1.1e-17, +1.6e-17]pp |
| 500 | +8.9e-18pp | [-7.9e-18, +2.5e-17]pp |
| 1000 | +1.6e-17pp | [+3.2e-18, +2.8e-17]pp |
| 2000 | +6.7e-18pp | [-9.6e-18, +2.3e-17]pp |

Every remainder is at the level of floating-point roundoff (1e-17 to 1e-18 pp, against a
46-48pp signal -- 18 orders of magnitude down). This is not "zero within statistical
error" the way the pass-error curve's near-zero C values are (Sec.1 of RETURN_PASS proper,
tenths-of-a-pp bootstrap bands) -- it is an **exact algebraic identity**: C_bug = C_true +
delta by construction, because T_pool is exactly the weighted average verified in Sec.2, and
the rest of the e1_pred/e1_obs machinery is unchanged between the bug and fixed runs. The
one row (1000us) whose boot band nominally "excludes zero" does so only because the band sits
at +3e-18 to +3e-17pp -- noise in the 17th decimal digit, not a finding, flagged rather than
hidden.

**The bug's number is fully measured-explained by the mixing.** Nothing is left over.

## 4. Plain words

Wayfinder's question was right to ask and the answer is: no, there was nothing else in it,
but not because the question was wrong to ask -- because the pooling bug's +46-48pp decomposes
exactly, to 17 decimal places, into two named, physical parts: (1) a near-even split (w~0.5)
of 2000us shot counts between the E0 and E1 arms at m0=0, and (2) the ~0.9-1.0 gap between
P(m1=1|m0=0) in the two arms, which is not noise or a hidden signal but the direct, expected
fingerprint of the X gate E1 applies between its two looks and E0 does not. Mixing two
circuits that disagree by ~90-100pp on this one conditional probability, in a ~50/50 blend,
produces a ~45-48pp artifact by arithmetic necessity -- there is no remainder to chase, no
darkwave-shaped residue, nothing resembling the ~64us clock or the drain. The "pooling bug"
label was correct, and now it is measured rather than merely labeled: every point of the
46-48pp is accounted for, and the account closes to within rounding error.

## Tries

Bug-number script: 11,905 counted tries (transition-matrix builds, pooled/own-arm predictions,
the mixing-identity verification over 97 qubit*v cells, and 500-draw qubit bootstraps per gap
across three sections: reproduce, predict, remainder). One real mistake caught before
reporting: an early version of the Sec.2 formula used a sign flip for the state=1 term
instead of the correct complementary weight (1-w); it predicted deltas near zero (wrongly
cancelling the two states' contributions) until checked against Sec.1's already-reproduced
+46-48pp and corrected -- the error and its fix are reported here, not smoothed over.
