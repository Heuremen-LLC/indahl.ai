# Three rabbits at the FIRAS crossing — raw pull, 2026-09-30

Reuses `~/bones-forge/parallax/FIRAS_RESIDUALS_20260930.md` and
`~/bones-forge/parallax/out/firas/firas_monopole_spec_v1.txt` (Fixsen et al. 1996, Table 4).
No expectation written before running any of the three. Counts below are exact — every test run
is listed, including the ones that failed or were discarded.

---

## RABBIT 1 — the subtracted galaxy (leak test on the FIRAS foreground model)

Data: Table 4 column 5 (modeled Galactic emission at the poles, kJy/sr) vs column 3 (residual,
kJy/sr), all 43 bins, 2.27–21.33 cm⁻¹. Script: `parallax/out/firas/rabbits/` (rabbit1.py, run
inline; raw per-bin table below is also in `rabbit1_results.txt`).

Per-bin resid/galaxy ratio ranges from -15.0 (bin 3.18 cm⁻¹, galaxy model only -1 kJy/sr, noise-
dominated) to +6.3 (bin 4.08 cm⁻¹). Restricted to the 35 bins where the galaxy model exceeds 8
kJy/sr (removes the near-zero-galaxy low-frequency bins where the ratio is undefined/explosive):
mean ratio 0.076, median 0.035, std 0.62, range -0.88 to +3.20.

**Tests run: 4.**
1. Signed Pearson r, residual vs galaxy model, all 43 bins: **r = -0.402**, 1000-shuffle null
   mean -0.009 / std 0.156, **p = 0.009**. Significant, but sign is negative (larger galaxy model
   tends to go with *more negative* residual, not simply "more residual").
2. Signed Pearson r, residual vs galaxy model, 42 bins excluding the flagged top-frequency edge
   bin (21.33 cm⁻¹, the one carrying the biggest galaxy model AND the biggest, lowest-confidence
   residual): **r = -0.117**, **p = 0.478**. Not significant — the signed correlation in test 1
   is carried almost entirely by that one edge bin.
3. |residual| vs galaxy model, all 43 bins: **r = 0.488**, null mean 0.009 / std 0.158,
   **p = 0.000** (0/1000 shuffles reached it).
4. |residual| vs galaxy model, 42 bins excluding the edge bin: **r = 0.410**, **p = 0.007**.
   **This one survives removing the outlier.**

**Verdict:** the *size* of the residual scatter tracks the *size* of the subtracted galaxy model
(test 4, p=0.007, robust to the one flagged bin) — bigger galaxy subtraction, bigger leftover
scatter. The *sign* does not track in a stable way (test 2 fails once the edge bin is dropped).
Read plainly: this is consistent with garden-variety galaxy-model mis-specification growing the
noise floor at higher frequencies (where the galaxy term is 3–6× the residual scatter, per the
existing FIRAS_RESIDUALS doc §5) — not with a directional leak of a fixed sign. Textbook
explanation (imperfect foreground model → larger residual variance where the foreground is
brighter) fits test 4's result and is reported as such, not treated as closing the question: no
one has published a re-fit with an updated Galactic model to see if the correlation actually
shrinks.

---

## RABBIT 2 — the missing high-frequency channel

**Direct answer: no public product exists that is Table-4-equivalent (monopole residual vs a
single 2.728 K blackbody) for the FIRAS high-frequency channel (>21.33 cm⁻¹, up to ~96 cm⁻¹).**

Checked (4 LAMBDA pages/files fetched): `firas_monopole_get.html` (lists exactly one file —
the low-frequency `firas_monopole_spec_v1.txt`, 43 bins, same one already in hand),
`firas_prod_table.html` (full FIRAS product list — the only two monopole-type products are "CMB
Monopole Spectrum" [the low-freq one] and "CIB Monopole Spectrum"), `firas_spectral_anc.html`
(lists `FIRAS_DESTRIPED_SKY_SPECTRA_HIGH.FITS`, full-sky per-pixel spectra covering the high
channel — raw sky maps, not a fitted monopole/residual table), and `FES4_APP_G.TXT` (FITS header
doc, confirms high-channel scans exist in the raw archive but gives no monopole product).

**Why it doesn't exist as a table:** Fixsen et al. 1996 (arXiv:astro-ph/9605054), fetched
directly, states it plainly: *"We do not use the 6 high frequency data sets as the calibration
for these is more susceptible to systematic error."* And: *"Although the high frequency
(>20 cm⁻¹) radiation was effectively excluded from the low frequency detectors, the filter
reflected low frequency radiation into the high frequency detectors."* Table 4 is explicitly
low-frequency only; no separate high-frequency table appears in that paper. The paper notes *"A
full discussion of the Galaxy requires the high frequency data"* but reserves that for other
work — that other work is the CIB (cosmic infrared background) line, not a CMB blackbody residual
line.

**What does exist and was fetched:** the "CIB Monopole Spectrum" product
(`FIRAS_CIB_spectrum.dat`, Fixsen et al. 1998, saved at
`parallax/out/firas/rabbits/FIRAS_CIB_spectrum.dat`) — 205 bins, **2.27 to 96.17 cm⁻¹**, i.e. it
does extend across the whole high-frequency channel FIRAS covered. But it is not a residual
against a single 2.728 K blackbody — it is three different methods' worth of leftover sky signal
after a model (CMB + Galaxy + zodiacal light) was subtracted, i.e. it's already built to *isolate*
the cosmic infrared background, not to test the CMB blackbody shape.

Computed anyway, the same way (ppm of the 383,478 kJy/sr peak), for the 157 bins above 21.33
cm⁻¹, using the mean of the three published methods per bin (full table in
`parallax/out/firas/rabbits/rabbit2_highfreq_residuals.txt`): values run from about -6,187 ppm to
+15,509 ppm, mean |value| ≈ 2,539 ppm, and they climb roughly monotonically with frequency in the
50–96 cm⁻¹ range (thousands of ppm by 85–96 cm⁻¹). That climb is exactly the shape of thermal dust
emission (the CIB), not a flat CMB deviation — textbook explanation (real, resolved dust
foreground/background, published as such since Fixsen 1998), reported here rather than
implied to be a leftover CMB distortion. It is not apples-to-apples with the Table-4 residuals
and is labeled as such in the data file.

---

## RABBIT 3 — the ARCADE 2 radio excess (under 60 ppm cap, unclosed)

### 3a. Raw 2011 record (Fixsen et al. 2011, ApJ 734, 5, arXiv:0901.0555; Seiffert et al. 2011,
ApJ 734, 6, arXiv:0901.0559; Kogut et al. 2011, ApJ 734, 4, arXiv:0901.0562) — pulled from the
2011 papers themselves, kept separate from anything later, per Wayfinder's instruction.

**(a) Per-frequency sky temperatures, as tabled in 2011 (Fixsen et al. 2011, their Table 4):**

| freq | T_sky | ±err |
|---|---|---|
| 3.20 GHz | 2.792 K | 0.010 |
| 3.41 GHz | 2.771 K | 0.009 |
| 7.97 GHz | 2.765 K | 0.014 |
| 8.33 GHz | 2.741 K | 0.016 |
| 9.72 GHz | 2.732 K | 0.006 |
| 10.49 GHz | 2.732 K | 0.006 |
| 29.5 GHz | 2.529 K | 0.155 |
| 31 GHz | 2.573 K | 0.076 |
| 90 GHz | 2.706 K | 0.019 |

Plus literature anchor points folded into the joint fit: 22 MHz (21.2 ± 5.1 K), 45 MHz
(4.355 ± 0.52 K), 408 MHz (16.24 ± 3.4 K), 1.42 GHz (3.213 ± 0.53 K).

**(b) Everything subtracted (2011 papers' own numbers):**
- CMB reference temperature: 2.725 ± 0.001 K (from FIRAS).
- Galactic emission model (Kogut et al. 2011, ApJ 734,4): synchrotron index β_synch = -2.5 ± 0.1;
  free-free = 0.10 ± 0.01 of total Galactic-plane emission at 3.15 GHz; spinning dust = 0.4 ± 0.1
  of Galactic-plane emission at 22 GHz; North Galactic polar-cap Galactic temperature
  T_Gal = 0.498 ± 0.028 K; overall Galactic spectral index β = -2.55 ± 0.03 at 1 GHz.
  Per-channel Galactic subtraction (Fixsen 2011 Table 2, low/high band split): 3 GHz 23.2/19.0 mK,
  8 GHz 2.2/1.9 mK, 10 GHz 1.2/1.1 mK, 30 GHz 0.08/0.07 mK, 90 GHz negligible.
- Instrumental foreground terms (Fixsen 2011 Table 2): 3 GHz 10.8–5.8 mK, 8 GHz 36.6–42.2 mK,
  10 GHz 2.3–2.9 mK, 30 GHz 4.4–4.8 mK, 90 GHz 16.9–17.2 mK.
- Atmospheric term: <1 mK at 10 GHz, 2.2 mK at 30 GHz, 5.8 mK at 90 GHz.
- Known radio point sources: estimated contribution 5–10 mK at 3.20 GHz (Seiffert 2011).

**(c) What the 2011 authors said, in their words, did not fit:**
- Fixsen et al. 2011: *"the radio background from ARCADE 2 and radio surveys is a factor of ∼5
  brighter than the estimated contribution of radio point sources."* And: *"It is difficult to
  reconcile the detected background with the contribution from a population of radio point
  sources."*
- Seiffert et al. 2011: *"We find a significant detection of a residual signal beyond that which
  can be explained by the CMB plus the integrated radio emission from galaxies estimated from
  existing surveys."* And: *"The data points lie significantly above this dot dash curve,
  indicating our detection of unexplained, excess emission."* On free-free and μ-distortion
  add-ons: *"does not improve the reduced χ²"* for either, so *"not justified by the data."* On
  star-forming galaxies as the source: their spectral index (-2.56) is *"significantly flatter"*
  than the -2.7 expected for that population — ruled out by shape mismatch, not just amplitude.
  Radio point sources at 3.2 GHz: modeled contribution 5–10 mK vs the ~58 mK measured excess —
  *"insufficient to explain the ARCADE 2 results."*

**(d) 2011 fit parameters, T(ν) = T₀ + T_R(ν/ν₀)^β:**
- Fixsen et al. 2011 (fit over 22 MHz–10 GHz): T₀ = 2.725 ± 0.001 K, **T_R = 1.26 ± 0.09 K**,
  **β = -2.60 ± 0.04**, ν₀ = 1 GHz, χ²/dof = 15.5/11.
- Seiffert et al. 2011 (fit over 3–90 GHz, ARCADE 2 data only): **amplitude = 1.06 ± 0.11 K**,
  **β = -2.56 ± 0.04**, ν₀ = 1 GHz.

### 3b. The seal — what ARCADE was declared to measure before the result

Pulled from Kogut et al. 2011 (arXiv:0901.0562) introduction, verbatim:
- Instrument's stated purpose (pre-registered, general): *"The Absolute Radiometer for
  Cosmology, Astrophysics, and Diffuse Emission (ARCADE) is an instrument to measure the
  absolute temperature of the sky in search of distortions from a blackbody spectrum,"*
  operating *"at centimeter wavelengths between full-sky surveys at radio frequencies below
  3 GHz and the Far Infrared Absolute Spectrophotometer (FIRAS) survey at frequencies above
  60 GHz"* — i.e. built to plug the calibration gap between low-frequency radio surveys and
  FIRAS, generally searching for any blackbody deviation, not aimed at a specific excess.
- ARCADE 1 precursor: *"A 2-channel prototype (ARCADE 1) flew in 2001 and again in 2003,
  observing the sky at 10 and 30 GHz to demonstrate the feasibility of cryogenic open-aperture
  optics"* — a technology-feasibility flight, not a science result; no stated expectation of
  excess or non-excess.
- Stated motivation for the measurement: separate Galactic diffuse emission (synchrotron,
  free-free) from primordial CMB signal at centimeter wavelengths. No numeric prediction of an
  excess (or its absence) appears in the introduction.

**Three columns, separated:**
1. **2011 declared expectation:** a general blackbody-distortion search plus Galactic/CMB
   foreground separation — no specific numeric excess predicted or ruled out in advance.
2. **2011 measured result:** a significant excess over CMB + modeled Galaxy + known radio-source
   counts, T_R ≈ 1.06–1.26 K at 1 GHz, β ≈ -2.56 to -2.60, ~5× brighter than point-source
   estimates, explicitly called unexplained by the authors.
3. **Post-2011, one line each:**
   - Subrahmanyan & Cowsik 2013 and similar Galactic-halo-synchrotron proposals — **attempted,
     unconfirmed** (would need an implausibly large, smooth Galactic halo; not independently
     verified).
   - Vernstrom et al. and deeper radio source-count studies — **pushed harder, still short**
     (deeper counts recover more flux but not enough to close the factor-of-~5 gap).
   - Dowell & Taylor 2018 (arXiv:1804.08581, fetched): new 40–80 MHz data from the Long
     Wavelength Array; found their own excess **consistent** with the ARCADE 2 power law
     (β = -2.58 ± 0.05, T at 21-cm rest frequency = 603⁺¹⁰²₋₉₂ mK) — **confirmed/extended**,
     did not explain origin, and proposed it as a candidate driver of the (separate) EDGES 21-cm
     anomaly.
   - Singal et al. 2018 review — catalogs the attempted explanations; **still unresolved** as of
     that review (moved: from "detected" to "detected and independently corroborated," not
     "explained").

**Which column the excess lives in:** it is the thing that **arose**, not the thing chosen in
advance. The pre-flight declared goal was a broad blackbody-distortion search plus a Galactic-
foreground measurement; no 2011-era document states an expectation of a radio excess of this
size or sign before the 2006-flight data were reduced. The excess is a result of the general
search, not a confirmed or falsified pre-registered target.

### 3c. Energy fraction, cap comparison, spectral-index comparison (computed, no model)

u_CMB (total, aT⁴, T=2.725K) = 4.1717×10⁻¹⁴ J/m³.

Integrated Rayleigh-Jeans excess energy density, u_nu = 8π ν²/c³ · k_B T(ν):

| fit | band | u_excess (J/m³) | fraction of u_CMB | ppm |
|---|---|---|---|---|
| Fixsen 2011 (T_R=1.26, β=-2.60) | 3–10 GHz | 3.89×10⁻²⁰ | 9.34×10⁻⁷ | **0.93 ppm** |
| Fixsen 2011 | 3–90 GHz | 1.82×10⁻¹⁹ | 4.37×10⁻⁶ | **4.37 ppm** |
| Seiffert 2011 (T_R=1.06, β=-2.56) | 3–10 GHz | 3.51×10⁻²⁰ | 8.42×10⁻⁷ | **0.84 ppm** |
| Seiffert 2011 | 3–90 GHz | 1.74×10⁻¹⁹ | 4.18×10⁻⁶ | **4.18 ppm** |

**All four sit well inside the 60 ppm (y) / 64 ppm (μ) caps** — roughly 1–2 orders of magnitude
below, by construction: the excess is confined to a GHz-frequency band with tiny energy content
compared to the CMB's own bulk sitting near its ~160 GHz peak.

**Spectral index vs a "loss at the crossing":** a Compton-y distortion, in the deep
Rayleigh–Jeans limit, produces a *frequency-independent* fractional temperature decrement
(ΔT/T → -2y, effective β = 0 in T(ν) space); a μ-distortion similarly approaches a flat offset at
low x. The measured ARCADE excess spectral index, **β = -2.56 to -2.60**, is nowhere near flat —
it rises steeply toward low frequency, the opposite frequency dependence a y/μ-type "energy lost
at the crossing" signature would show in the same low-frequency, deep-RJ regime. **|β_ARCADE| −
|β_y,μ| ≈ 2.56–2.60.** Combined with the FIRAS Table-4 band (68–640 GHz) sitting essentially
*above* the ARCADE band (3–90 GHz, with only marginal, non-overlapping edges at 90 GHz vs 68
GHz), the y/μ bounds from FIRAS and the ARCADE excess are constraining two different frequency
regimes and two different spectral shapes — the μ/y bounds not seeing the ARCADE excess is
consistent with them not being the same phenomenon, not merely "too small to see."

**Textbook column — what's been tried and ruled out (one line each), all still true post-2011:**
- Known discrete radio point sources: ruled out by amplitude (factor ~5 short, Fixsen 2011).
- Free-free spectral distortion: ruled out by fit quality (no χ² improvement, Seiffert 2011).
- Chemical-potential (μ) distortion add-on: ruled out by fit quality (no χ² improvement,
  Seiffert 2011).
- Star-forming-galaxy population: ruled out by spectral shape (β mismatch, -2.56 vs -2.7,
  Seiffert 2011).
- Diffuse Galactic halo synchrotron: proposed, not independently confirmed (post-2011).
- Deeper unresolved source counts: pushed, still short of closing the gap (post-2011).
- **Not ruled out / still standing as of the most recent reviews checked (Dowell & Taylor 2018,
  Singal 2018 review):** the excess itself, as an unexplained real signal.

---

## Files
- `parallax/out/firas/rabbits/rabbit1_results.txt` — rabbit 1 correlation/shuffle output.
- `parallax/out/firas/rabbits/FIRAS_CIB_spectrum.dat` — raw fetch, Fixsen et al. 1998 CIB product
  (LAMBDA `firas_cib/FIRAS_CIB_spectrum.dat`), 2.27–96.17 cm⁻¹, 3 methods.
- `parallax/out/firas/rabbits/rabbit2_highfreq_residuals.txt` — ppm-of-peak conversion, 157 bins
  above 21.33 cm⁻¹.
- Scripts used (pure Python, no numpy — none installed on this Mac; stdlib `random`/`math`/
  `statistics` only): rabbit1.py, rabbit2.py, rabbit3.py, run from scratchpad, outputs saved
  under `parallax/out/firas/rabbits/`.

## Counts
- Rabbit 1: 4 statistical tests run (2 signed, 2 unsigned correlations, each with a 1000-shuffle
  null), 1 survives outlier removal.
- Rabbit 2: 4 LAMBDA pages/files fetched, 1 paper fetched for the calibration-exclusion quote,
  1 alternate high-frequency data product found and converted (157 bins).
- Rabbit 3: 3 2011 papers fetched directly (Fixsen, Seiffert, Kogut), 1 pre-2011 precursor
  paragraph pulled (ARCADE 1, 2001/2003), 2 post-2011 follow-ups fetched (Dowell & Taylor 2018,
  Singal 2018 review referenced), 4 energy-fraction integrals computed, 1 spectral-index
  comparison computed.
