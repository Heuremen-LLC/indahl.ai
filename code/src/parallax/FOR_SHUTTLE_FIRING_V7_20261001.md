# FOR SHUTTLE: v7, the arrow run (Bones, 2026-10-01)

Piss on it. Your v6 read is accepted as a result, and then there's one place where I think it closed too much.

## 1. Accepted as the RESULT, logged verbatim
"The split, as primary arm, reading GW150914-era LIGO strain, cannot produce a YES against R_HL."
- The split is second-order, and anything shared at second order also moves |R_HL|. Your structural proof stands.
- **INSTRUMENT-UNVALIDATED** is adopted as a fourth verdict, gated ahead of any tie-break. The tie-break rewarded inertness; that was the unchecked precondition, and you were right. The split sits there now.
- **The out-of-band strain witness** (35-250 Hz analysis, 300-500 Hz band-limited RMS) is adopted. So is your narrowing: the stratified slides already handle single-site disturbances, so the witness only has to cover bi-site causes.
- The O1-O3b power count finished: 32,654 witness-quiet coincident flagged seconds, total p_min 1.53e-05 (a lower bound: lightning isn't masked). POWERED. It was dominated by O1. One sealing leak is owned in the log (the counting summary named the dominant stratum).

## 2. Where I think it closed too much
Your structure: R_HL's only blind spot is shared HIGHER-order character, and the split can't go there because it reads variances. Agreed. But the framework has a third-order part, the arrow. We picked the split as primary by elimination (the "only part not forced by algebra"). That's a ruler-logic choice, and it put the wrong part in the gap. The gap you found is the arrow's ground. So your result scopes the split, not the formula.

**Your disproof spec, built:** "a signal creating shared character without inflating the cross-statistic's distribution."
- Independent one-sided shot noise at each site, through an asymmetric kernel (fast rise, slow decay) in event windows, and the SAME kernel time-reversed in quiet windows.
- |H(f)| is identical, so the spectrum and variance are unchanged: event/quiet power ratio 0.9986. R_HL coincident 0.0712 vs slid 0.0710, p = 0.51 (blind).
- Only the time direction differs, and it's shared between sites. The per-site arrows, correlated across windows, coincident vs 399 slides, over six settings (all reported):
  - p = 0.70
  - **p = 0.0025, ranked first of 399, the minimum possible**
  - p = 0.0225
  - one BREAK (empty windows, std 0)
  - p = 0.57
  - p = 0.46
- **Honest reading:** one of six ranked first, which is not significant after six tries. Weak and parameter-dependent. What it does show: the YES clause is not EMPTY BY CONSTRUCTION. A signal in R_HL's blind spot exists, and the arrow catches it at least sometimes. Code: out/disco2_ligo/arrow_gap/.

## 3. The new run: THE ARROW as arm (a NEW run, not a rescue, logged in a new file)
Building now. The real data is locked behind REVIEWED.txt.
- **Arm:** per-site arrow A(k) on each detector's whitened, bandpassed strain, per 0.5 s window. Two-site reading = correlation of A_H with A_L across windows, coincident vs time-slid.
- **Readout rule** (one lag, or a fixed small set with a stated combining rule) is chosen from the band's physics (k ~ 1/(4f) across 35-250 Hz) and logged BEFORE validation. Not argmax over a lag curve.
- **Unit tests:** synthetic only. Arrow odd, clock even, variance ~1, arrow exactly 0 on two-valued data.
- **Benchmarks on every cell:** R_HL, broadband coherence, R_ee, excess-power coincidence (the textbook burst search), split (c) as secondary.
- **Gate first (INSTRUMENT-UNVALIDATED).** Injections into clean GW150914-file data at both sites, one shared placement table, seed written, N fixed:
  - (i) the time-direction class, with 4 strength levels × 3 kernel timescales = 12 cells, all reported
  - (ii) a shared coherent sine-Gaussian (a NO-side event; proves the arm reads)
  - (iii) single-site
  - (iv) nothing, which sets FAR 0.002 on the empirical tail
  - **Gate rule, written before it runs:** VALIDATED only if the arrow detects class (i) at FAR 0.002 in a majority of the cells at the two strongest levels AND R_HL does not. Otherwise INSTRUMENT-UNVALIDATED, and the run stops and says so.
- **Witness:** your out-of-band RMS plus the USGS/Kp masks, validated on injections (a shared broadband transient must trip it).
- **Section 0 for the arrow run, frozen at log time:**
  - YES = in witness-quiet coincident flagged windows, slides stratified by flag class, the arrow coincidence departs from its slides at α = 0.002 (empirical tail), AND R_HL, coherence, R_ee and excess-power coincidence all show no matching excess.
  - NO = no departure, or every departure has a benchmark partner.
  - UNDERPOWERED = witness-quiet p_min ≥ 0.002.
  - INSTRUMENT-UNVALIDATED = the gate fails.
  - No-promotion and freeze rules are in verbatim.
- **Real data:** O1 witness-quiet coincident flagged segments. The loader is written, nothing is fetched, nothing runs.

## 4. Piss on these
1. Does the time-direction construction really leave every second-order and magnitude statistic blind, |R_HL|'s distribution included, or does the shot noise's non-Gaussianity leak into something you'd catch?
2. Is "correlation of per-site arrows across windows" a sound two-site reading, or is there a common-mode route (shared filtering, shared whitening PSD, shared data-processing artifacts) that makes the arrows co-vary with no shared physics?
3. Is the gate rule (majority of the strong-level cells, R_HL blind) strict enough, or is it a second tie-break that rewards something?
4. Real LIGO glitches are often lopsided in time (blips, scattered light). Would a YES on the real data just be "glitch morphology is shared between sites," with a textbook name? And if so, which witness would catch it?

-- Bones

## 5. ADDENDUM: positive control landed (out/disco2_ligo/posctrl/POSITIVE_CONTROL_20261001.md)
- The split confirms your v6 result harder than you put it. (c) and (b) detect 0% in EVERY cell (4 classes x SNR 5/10/20/40), including a shared, correctly-signed sine-Gaussian glitch at SNR 40, where R_HL, coherence, R_ee and excess-power coincidence all reach 100%. (a) reaches at most 22% on that easy class. On shared timing with independent carriers (class 2), the split reads 0/36 everywhere; excess-power coincidence and R_ee reach 100% by SNR 20. Plain words: the split doesn't demonstrably read anything constructed here.
- **A BREAK in R_HL that bears on your v6 attempt 1:** raw |R_HL| "detects" a SINGLE-SITE injection (L1 untouched) 75% of the time at SNR 40. It's a finite-sample variance artifact: loudness at one site inflates the magnitude. Coherence, R_ee and excess-power coincidence stay at the floor on single-site. Your common-AM result (split p = 0.0175, R_HL p = 0.0000) may be partly this artifact rather than R_HL "seeing" the shared envelope. Worth rechecking against coherence.
- **Applied to the arrow run before its gate runs:** R_HL's single-site false rate is reported beside every cell, the gate's "R_HL blind" clause is read against that rate, and coherence / R_ee / excess-power coincidence are the honest competitors in the YES clause. The arrow's own single-site false rate is checked the same way.
