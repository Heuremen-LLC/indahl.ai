# ARCADE 2 — the instrument's own absences, laid beside the excess (2026-09-30)

Reuses `~/bones-forge/parallax/THREE_RABBITS_20260930.md` (Rabbit 3, already pulled the 2011
fit parameters and the four Fixsen/Seiffert quotes). This document goes one layer deeper into
the same four ApJ 734 (2011) papers — Fixsen (arXiv:0901.0555), Seiffert (arXiv:0901.0559),
Kogut (arXiv:0901.0562), Singal "The ARCADE 2 Instrument" (arXiv:0901.0546) — fetched directly,
plus the fit numbers already in hand. No expectation written before running the counts. Every
fetch and every computed test is logged below.

---

## 1. THE INSTRUMENT'S FAILURES

Nominal design: 6 channels, ~3, 5, 8, 10, 30, 90 GHz, each split low/high sub-band, plus a
second narrower-beam 30 GHz radiometer ("30#").

**Failed in flight:**
- **5 GHz** — Fixsen 2011: *"The 5 GHz switch failed in flight, so there are no useful data
  from that radiometer."* Singal 2011: *"the most significant instrumental failure was with
  the 5 GHz MEMS switch, rendering data from that channel not useful for science analysis."*

**Flown, but excluded from the excess fit anyway:**
- **30 GHz narrow-beam ("30#")** — Fixsen 2011: *"The 30 GHz radiometer with the narrower
  beam is not matched to the beams of the other radiometers and has much higher noise than
  the other 30 GHz radiometer so its data are not used here."* Measured noise (Singal 2011
  Table 2): 885.0 / 418.5 mK/√s (lo/hi) vs 208.2 / 103.3 mK/√s for the standard 30 GHz beam —
  roughly 4x worse. Singal 2011 describes this same channel, elsewhere, as existing to
  *provide "a cross-check on emission in the antenna sidelobes"* — built as a check, then
  dropped from the number that mattered.

**Used in the final excess fit:** 3.20, 3.41, 7.97, 8.33, 9.72, 10.49, 29.5, 31, 90 GHz
(Fixsen 2011 Table 4), plus literature anchors at 22 MHz, 45 MHz, 408 MHz, 1.42 GHz.

**A narrower paper inside the same channel set:** Kogut et al. 2011 (the Galactic-model
paper) restricts itself further: *"Throughout this paper, we consider only data from the 3,
8, and 10 GHz radiometers"* — 30 and 90 GHz are treated as carrying too little Galactic
signal for that fit, even though Fixsen/Seiffert use all five bands for the CMB-excess fit.
Same instrument, same flight, two different exclusion boundaries depending on which
question is being asked.

**Beam pattern:** Singal 2011: *"It is not practical to measure the beam pattern for the
lower frequency horns, or any of the horns once installed in the instrument."* The flight
beams were modeled, not measured in situ.

Noise per channel, mK/√s (Singal 2011 Table 2):

| channel | Lo | Hi |
|---|---|---|
| 3 GHz | 9.3 | 7.8 |
| 8 GHz | 5.5 | 6.1 |
| 10 GHz | 3.7 | 3.7 |
| 30 GHz | 208.2 | 103.3 |
| 30# GHz (excluded) | 885.0 | 418.5 |
| 90 GHz | 50.5 | 25.3 |

---

## 2. WHAT WAS SUBTRACTED

**Galactic model** (Kogut et al. 2011): spatial structure built as a linear combination of
template maps — the 408 MHz Haslam survey and a full-sky C II map — fit two independent ways:
(a) plane-parallel csc|b| binning to the poles, (b) direct correlation against the C II map,
scaled to match the observed C II intensity along selected lines of sight, with *"a single
offset required to force the template model to match."* Scatter between the two methods:
5 mK at 3 GHz, <1 mK at 8–10 GHz. Per-channel Galactic subtraction, low/high band (Fixsen
2011 Table 2, mK): 3 GHz 23.2/19.0, 8 GHz 2.2/1.9, 10 GHz 1.2/1.1, 30 GHz 0.08/0.07,
90 GHz negligible.

**Extragalactic source counts:** no explicit source-count number is *subtracted* from the
ARCADE 2 sky temperature — the papers instead *compare* the excess to source-count
predictions and find it short. Alternatives named and compared: Windhorst et al. 1993 and
Gervasi et al. 2008a "Fit1" (single power law, amplitude 0.88 K at 0.61 GHz, index -2.707,
adopted with a 10% fractional error), Fomalont et al. 2002 VLA 8.4 GHz counts (faint-end
index γ = 2.11 ± 0.13). Estimated point-source contribution: 5–10 mK at 3.2 GHz vs a ~58–67
mK measured excess there — the gap the whole result rests on. Extending source counts far
enough to close the gap would require, per Kogut 2011: *"a source density of ∼8×10^5 per
square arcmin. This extreme scenario is not a plausible distribution of ordinary galaxies."*

**Instrument/calibration terms** (Fixsen 2011 Table 2, mK, low/high band): 3 GHz 10.8–5.8,
8 GHz 36.6–42.2 (the single largest instrument term of any channel — bigger than that
channel's own Galactic term), 10 GHz 2.3–2.9, 30 GHz 4.4–4.8, 90 GHz 16.9–17.2.

**External calibrator:** Steelcast-absorber cones on aluminum cores, held near 2.7 K
(within 300 mK). Thermometer accuracy: *"At 2.7 K, the average total uncertainty in the
resistance versus temperature curves is 1.3 mK"* (Singal 2011); *"absolute calibrations
stable to less than 2 mK"* (Fixsen 2011). Post-flight: 21 thermometers *"were carefully
recalibrated after the flight"* against a NIST-traceable standard, cross-checked against the
2.17 K superfluid-helium lambda transition seen directly in the data, giving an independent
absolute anchor. Stated net calibration uncertainty: 1 mK, common to all channels.

**Atmospheric term:** <1 mK at 10 GHz, 2.2 mK at 30 GHz, 5.8 mK at 90 GHz — rises with
frequency, tracks the channel where the deepest instrument term also sits (90 GHz).

---

## 3. THE EXCESS BY CHANNEL (Fixsen 2011 Table 4, T_CMB = 2725 mK)

| freq (GHz) | T_sky (mK) | ±err | excess = T_sky−2725 (mK) | excess/err |
|---|---|---|---|---|
| 3.20 | 2792 | 10 | +67.0 | **6.70** |
| 3.41 | 2771 | 9 | +46.0 | **5.11** |
| 7.97 | 2765 | 14 | +40.0 | 2.86 |
| 8.33 | 2741 | 16 | +16.0 | 1.00 |
| 9.72 | 2732 | 6 | +7.0 | 1.17 |
| 10.49 | 2732 | 6 | +7.0 | 1.17 |
| 29.5 | 2529 | 155 | −196.0 | −1.26 |
| 31 | 2573 | 76 | −152.0 | −2.00 |
| 90 | 2706 | 19 | −19.0 | −1.00 |

The excess sits almost entirely at the low end: 3 GHz carries both the largest excess in
absolute terms and by far the largest significance (5–7σ per point). By 8–10 GHz the
significance has fallen to ~1σ. At 30 GHz the *central value* runs negative — below the CMB
itself — inside a huge error bar (76–155 mK), and 90 GHz is also nominally negative at low
significance. Read plainly: **the channel with the highest noise (30 GHz, 104–208 mK/√s) is
also the channel whose central value most contradicts the fitted excess power law**, and it
carries an error bar 8–20x any other channel's.

Fraction "known" vs "excess" at 3 GHz (the channel carrying the result): Galactic 23.2 mK +
instrument 10.8 mK + atmosphere <1 mK + point sources 5–10 mK ≈ 39–44 mK of *known,
subtracted* terms, against a 67 mK measured excess over CMB — i.e. the *subtracted* terms are
already 60–65% the size of the *excess itself* at the one channel that carries the whole
claim.

---

## 4. WHAT THEY RAN, AND WHAT THEY SAID THEY COULDN'T

Cross-checks run and reported:
- Free-free spectral-distortion add-on to the fit — run, rejected: *"The addition of the
  free-free amplitude does not improve the reduced χ² of the fit ... and is therefore not
  justified by the data."*
- μ-distortion add-on — run, rejected: *"The addition of the μ distortion as a free
  parameter does not improve the reduced χ²."*
- Star-forming-galaxy population match — run, rejected by spectral shape (β = −2.56 measured
  vs −2.7 expected).
- Extreme deep source-count scenario to close the gap — run, rejected: *"not a plausible
  distribution of ordinary galaxies."*
- Consistency check of the Galactic model extrapolated to 150 MHz against Rogers & Bowman
  2008 — run informally, **not** folded into the primary fit.
- Two independent Galactic-template fitting methods (csc|b| binning vs C II correlation) —
  run, cross-checked against each other (5 mK / <1 mK scatter, reported above).

Said, in their own words, not possible / not separable / beyond the data:
- *"The set of measurements in Table 1 do not have sufficient angular resolution to reject
  discrete radio sources."* (Kogut 2011)
- *"The ARCADE 2 data has only six frequency channels containing significant Galactic
  emission... and can not uniquely separate the observed emission into individual components
  (synchrotron, free-free, or other sources)."* (Kogut 2011)
- *"The ARCADE 2 data alone do not have sufficient low-frequency coverage to determine the
  spectral index of the 3 GHz excess."* (Fixsen 2011) — the index comes from folding in the
  22 MHz/45 MHz/408 MHz/1.42 GHz ground literature, not from ARCADE 2 alone.
- *"Radio source count surveys... can not extend to arbitrarily low fluxes, or the total
  contribution would diverge."* (Kogut 2011)
- *"It is not practical to measure the beam pattern for the lower frequency horns, or any of
  the horns once installed in the instrument."* (Singal 2011)
- *"There does not appear... to be a case for a sufficient difference in timescale to
  account for our measurements in known populations of galaxies."* (Kogut 2011)

---

## 5. STRING THROUGH THE HOLES

Lined up per band (3, 8, 10, 30, 90 GHz): instrument noise (Singal Table 2), Galactic
subtraction size (Fixsen Table 2, low-band value), and mean |excess significance| (§3).

| band | mean noise (mK/√s) | Galactic sub (mK) | mean \|excess/err\| |
|---|---|---|---|
| 3 | 8.55 | 23.2 | 5.91 |
| 8 | 5.80 | 2.2 | 1.93 |
| 10 | 3.70 | 1.2 | 1.17 |
| 30 | 155.75 | 0.08 | 1.63 |
| 90 | 37.90 | 0.0 | 1.00 |

**Tests run: 3** (n=5 bands each — say plainly this is an extremely small sample; exact
permutation null used throughout, all 120 orderings of a 5-element vector, no asymptotic
approximation).

1. Noise vs |significance|: **r = −0.2545**, permutation null mean 0.000/std 0.500,
   two-sided p ≈ 0.767. Not significant, weak negative — if anything, the noisiest channel
   is *not* where the sharpest excess lives, at trend level, but n=5 makes this basically
   unreadable on its own.
2. **Galactic-subtraction size vs |significance|: r = 0.9891**, permutation p ≈ 0.083 (best
   attainable two-sided p at n=5 is ~0.017; 0.083 means this ordering is close to, but not,
   the single most extreme of the 120 possible). The channel with the *largest* Galactic
   subtraction (3 GHz, 23.2 mK) is also the channel with by far the *largest* excess
   significance (5.91σ mean) — a near-monotonic match across all 5 bands.
3. Instrument-term size vs |significance|: **r = −0.036**, permutation p ≈ 0.900. No
   relation.

**Read plainly:** the excess does not sit where the *least* was subtracted, and it does not
sit where the *instrument* removed the most, or where the *noise* was worst. It sits almost
exactly where the *Galactic model* removed the most (test 2, r≈0.99, n=5). That is
consistent with two very different readings, both reported, neither closed: (a) ordinary
covariance — 3 GHz is both the frequency where Galactic synchrotron is intrinsically
brightest *and* where a real cosmological/extragalactic excess with a steep spectral index
(β≈−2.6) would also peak, so both scaling with frequency the same way is not surprising; or
(b) an under-subtracted or mis-modeled Galactic term at exactly the channel carrying the
whole claim, which the paper's own two-method cross-check (5 mK scatter at 3 GHz) does not
rule out at the level needed (23.2 mK subtraction, 67 mK excess — a 5 mK cross-check scatter
is ~7% of the excess, not obviously enough to exonerate it). No 2011-era document runs the
number needed to adjudicate between (a) and (b); this is reported, not resolved.

---

## Files
- `parallax/out/firas/rabbits/arcade/channel_status.txt` — raw per-channel failure/exclusion
  quotes and noise table (Singal, Fixsen, Kogut, verbatim).
- `parallax/out/firas/rabbits/arcade/absence_correlation.txt` — full script output: Table 4
  reprint, per-band noise/subtraction/significance table, all 3 permutation tests.
- Script: `arcade_absence.py` (run from scratchpad, pure stdlib, no numpy).

## Counts
- 4 papers fetched directly (Fixsen 0901.0555, Seiffert 0901.0559, Kogut 0901.0562, Singal
  0901.0546, all ApJ 734, 2011), 1 arXiv ID checked and rejected before finding Singal's
  correct one (0901.0560, unrelated nuclear-physics paper).
- 3 correlation tests run (noise/sig, Galactic-sub/sig, instrument-sub/sig), each with a
  full 120-permutation exact null (n=5, stated as small-sample throughout).
- 6 direct "not possible / not separable / can not" quotes pulled and kept verbatim.
- 2 exclusion decisions documented with the authors' own stated reason each (5 GHz failure,
  30# GHz narrow-beam noise/beam-mismatch).
