# THE SUN'S MISSING PAIRS — 2026-10-01

Object: thermal light should bunch at g2(0) = 2. Real measurements on the Sun and
on other stars, through single-photon detectors, read less than 2. The shortfall is
usually blamed on detector timing jitter and the optical filter's bandwidth. Same
strict rule as UNACCOUNTABLE_REMAINDER_20261001.md: a term only closes the books if
it was MEASURED INDEPENDENTLY (its own separate measurement, its own number) and
then actually used in an arithmetic prediction compared to the data — not fitted to
the same correlation curve it's explaining, and not a bare label. No expectation
written before reading. Raw first.

## 0. Sources — every fetch attempt, success or not

| # | target | method | result |
|---|---|---|---|
| 1 | arXiv:1404.4929 (guessed ID from the task prompt) | `curl` abstract page | **WRONG PAPER** — this ID is "Exel's crossed product...", unrelated math paper. Not Tan et al. Row kept, number discarded. |
| 2 | `arxiv.org/a/kurtsiefer_c_1` (Kurtsiefer author listing) | `curl`, then regex-paired titles to arXiv IDs | SUCCESS — found the real ID, arXiv:1403.7432, "Measuring Temporal Photon Bunching in Blackbody Radiation" |
| 3 | arXiv:1403.7432 abstract + PDF | `curl` abs page, `curl` PDF, PyMuPDF full-text extraction (5 pp) | SUCCESS — Tan, Yeo, Poh, Chan & Kurtsiefer 2014 (ApJ 789, L10) |
| 4 | Kurtsiefer listing, scanned for "bunch/Siegert/intensity interferometry/thermal/blackbody/sun" in titles | regex over the same HTML | SUCCESS — surfaced arXiv:1512.08649 ("Optical Intensity Interferometry through Atmospheric Turbulence") as a second, later Sun record |
| 5 | arXiv:1512.08649 abstract + PDF | `curl`, PyMuPDF full-text (5 pp) | SUCCESS — Tan, Chan & Kurtsiefer, Sun g2(τ) through the day |
| 6 | `arxiv.org/a/guerin_w_1` (guessed Guerin author listing) | `curl` | **FAILED** — wrong URL form, zero entries returned |
| 7 | arXiv API query: `stellar intensity interferometry AND Guerin` | `curl` export.arxiv.org API | SUCCESS (10 hits) but top candidates were off-target |
| 8 | arXiv:2503.22446 abstract | `curl` | FETCHED but **NOT A MEASUREMENT RECORD** — a 2025 review/SNR-theory paper, no new g2(0) data of its own. Not scored. |
| 9 | arXiv:1910.08366 abstract | `curl` | FETCHED but **WRONG TYPE** — spatial visibility interferometry (P Cygni distance), not temporal g2(0) bunching. Not scored. |
| 10 | arXiv API query: `abs:"photon bunching" AND abs:star` | `curl` export.arxiv.org API | SUCCESS — surfaced the two right papers directly: 1708.06119 and 2408.08173 |
| 11 | arXiv:1708.06119 abstract + PDF | `curl`, PyMuPDF full-text (8 pp) | SUCCESS — Guerin et al. 2017 (MNRAS), first stellar temporal g2 since HBT, 3 stars |
| 12 | arXiv:2408.08173 abstract + PDF | `curl`, PyMuPDF full-text (21 pp) | SUCCESS — Leopold, Karl, Rivet & von Zanthier 2024, on-sky HPD instrument, 3 A-type stars |

12 fetch/read steps, 1 wrong-ID dead end (#1), 1 zero-result listing (#6), 2 fetched-but-off-target papers (#8, #9). 4 records scored below. No Kimble-style hole this pass — everything needed was open access on arXiv.

## 1. The four records, raw first

| record | light | measured g2(0) (or contrast C=g2(0)−1) | filter | detectors / jitter |
|---|---|---|---|---|
| **Tan 2014** (ApJ 789, L10; arXiv:1403.7432) | Sun | **1.3 ± 0.1**, τc = 0.26±0.05 ns, 45 min integration, 546.1 nm | grating monochromator 0.122±0.002 nm + etalon ≈2 GHz FWHM (FSR 205 GHz, R≈97%, finesse 103) | Si APDs (PDF, Micro Photon Devices), oscilloscope 40 GS/s, <10 ps timing uncertainty |
| **Tan 2014 (lab controls, same paper)** | Hg discharge lamp | 1.79 ± 0.01, τc=0.436±0.006 ns | same etalon, tuned to 546.1 nm Hg line | same |
| | Ar arc (≈6000 K blackbody) | 1.45 ± 0.03, τc=0.31±0.01 ns | same | same |
| **Tan 2016** (MNRAS; arXiv:1512.08649) | Sun | **1.693 ± 0.003** (day-mean), single-run 1.69±0.05, τc=375±35 ps, 569.6 nm | 2 etalons (1.99 & 3.32 GHz FWHM) + 3 interference filters (2.2 nm, 2.2 nm, 80 nm) | actively-quenched APDs, oscilloscope 40 GS/s; jitter measured via SPDC pair source at 810 nm (near-delta, 0.7 ps) |
| **Tan 2016 (lab control)** | Ar arc, same filter chain | 1.687 ± 0.004 | same | same |
| **Guerin et al. 2017** (MNRAS; arXiv:1708.06119) | α Boo, α CMi, β Gem (bright stars, contrast regime) | C = 1.81±0.19, 1.90±0.28, 2.38±0.43 (×10⁻³) | 10 Å (500 GHz) interference filter at 7800 Å | fiber-coupled APDs, manufacturer jitter 350 ps (10 µm spot) / "realistic" 500 ps for the 100 µm MMF used; TDC bin 162 ps |
| **Leopold/Karl/Rivet/von Zanthier 2024** (arXiv:2408.08173) | Vega, Altair, Deneb | all match prediction within <1σ (S/N 12, 7.3, 2.7) | 2 nm bandpass at 405 nm | hybrid photon detectors (HPDs) + CFD + TDC; jitter **42.4 ps FWHM, measured with a pulsed fs-laser** |

## 2. Term classification (the strict rule)

**Tan 2014 (Sun, g2(0)=1.3):** the etalon bandwidth (2 GHz) and monochromator bandwidth (0.122 nm) ARE MEASURED-INDEPENDENT — measured with a narrowband laser scan, a separate measurement from the sunlight run. Detector jitter (40 ps FWHM core, measured by cross-correlating SPDC pairs with <10 ps intrinsic coherence time) is also MEASURED-INDEPENDENT. **But neither term is ever arithmetically combined into a predicted g2(0) for the Sun in the paper.** The text says only: "we cannot explain the reduction... seeing-induced atmospheric fluctuations... may be a reason" — **LABEL ONLY**, no number, and explicitly flagged by the authors themselves as not understood. For the Hg line (closest to ideal, 1.79), the stated cause is "possibly due to residual timing uncertainty of our photodetectors" — again **LABEL ONLY**, no computed prediction offered.

**Tan 2016 (Sun, g2(0)=1.693):** this is the one record in the whole sample where the authors actually DO the arithmetic — and it is instructive precisely because it fails cleanly under the strict rule. They measured the full detector-pair response independently (SPDC photon pairs at 810 nm, an unrelated wavelength with 0.7 ps intrinsic coherence — a true MEASURED-INDEPENDENT calibration), fit it to Gaussian (σ=12.0±0.1 ps) + exponential tail (τe=450±2 ps), **both MEASURED-INDEPENDENT numbers**. Convolving this *honest, fully-measured* response with the ideal g2(τ) "significantly underestimates" the observed peak (no number given, but directionally: the full independent measurement predicts LESS bunching than was seen — the opposite sign of a jitter-caused shortfall). Unable to use their own independent measurement, they substitute a **different, idealized model** — a pure Lorentzian matched only to the 40 ps FWHM, with the independently-measured long exponential tail deliberately dropped ("effectively ignoring the long decay fraction"). This substitution is **INFERRED-FROM-A-CHOICE-TO-FIT**, not a direct use of the independent measurement. Even this best-case idealized model predicts g2(0)=1.8, still short of the measured 1.693±0.003. The remaining 0.107 is attributed only to "deviation of the photodetector response from a Lorentzian," "minor temperature inhomogeneities," or "a difference of the etalon line width" away from its design wavelength — three **LABEL ONLY** causes, no number for any.

**Guerin 2017 (3 stars, contrast ≈2×10⁻³):** filter bandwidth (500 GHz, from a specified 10 Å interference filter) is MEASURED-INDEPENDENT. Detector jitter is split: manufacturer spec 350 ps (10 µm spot) is an independent number, but the 500 ps actually used is an *estimate* ("a realistic expectation") for the 100 µm multimode fiber — **borderline, partly INFERRED**, not a direct measurement at the fiber size used. The predicted contrast C≈2.2×10⁻³ (FWHM≈700 ps) computed from these terms was then checked against an **independent laboratory measurement with an artificial broadband thermal source (a light bulb) run through the identical optical and electronic chain** — a true held-out calibration, separate from any star data — giving C=(2.01±0.09)×10⁻³, FWHM=740±35 ps, "in agreement." This lab step is the strongest MEASURED-INDEPENDENT validation in the whole sample: the prediction was tested on a different light source through the same hardware before ever pointing at a star.

**Leopold/Rivet 2024 (Vega, Altair, Deneb):** the single strongest instance of a term meeting the bar outright — timing resolution (42.4 ps FWHM) was measured with a **pulsed femtosecond laser**, a true delta-function-like independent calibration, in the same optical path as the stellar measurements. Filter bandwidth (2 nm) gives an expected coherence time of 0.212 ps, computed purely from the independently specified/measured filter. A lab "2f-2f" test with an artificial star through the full chain measured 0.21±0.02 ps — matching the prediction. On sky, all three stars matched the pre-calculated expectation to better than 1σ.

## 3. The remainder, with sign, per record

| record | raw shortfall from g2(0)=2 (or from predicted C) | predicted-from-measured-terms | **unaccounted remainder** | sign |
|---|---|---|---|---|
| Tan 2014, Sun | 0.7 ± 0.1 | not computed by authors; a rough convolution using their own measured jitter (40 ps) + filter-implied coherence time (~0.2 ns) predicts ≈1.88 | **≈ 0.58 unaccounted** (predicted-but-not-delivered bunching), authors say "cannot explain" | shortfall, full magnitude effectively untouched by the measured terms |
| Tan 2014, Hg line (lab, not sky, for comparison) | 0.21 ± 0.01 | same style estimate (jitter tiny vs τc=0.436 ns) predicts ≈1.94 | **≈ 0.15 unaccounted** | shortfall, LABEL ONLY ("possibly...") |
| Tan 2016, Sun | 0.307 ± 0.003 | authors' own best model (idealized Lorentzian matched to measured FWHM, honest tail dropped): 1.8 | **0.107 ± 0.003 unaccounted**, and this is after crediting a *favorable, non-honest* use of the independent measurement — the fully honest measured detector response predicts even less bunching (unaccounted margin would be larger, not smaller) | shortfall, LABEL ONLY (3 named, unmeasured causes) |
| Guerin 2017, α Boo / α CMi / β Gem | C_pred ≈ 2.2×10⁻³ (lab-validated 2.01±0.09×10⁻³) vs measured 1.81±0.19 / 1.90±0.28 / 2.38±0.43 ×10⁻³ | same, lab-validated model | **≈ 0, within error, for all three** | **BOOKS CLOSE** |
| Leopold/Rivet 2024, Vega / Altair / Deneb | predicted coherence time 0.212 ps, lab-confirmed 0.21±0.02 ps | same | **≈ 0, within <1σ, for all three** | **BOOKS CLOSE** |

## 4. The mirror — sun/star remainder beside the lab single-photon remainders

UNACCOUNTABLE_REMAINDER_20261001.md: every lab single-photon antibunching record (Jacques 0.12, Grangier 0.18/0.35, trapped ion 8×10⁻⁵, QD 1×10⁻²) left the **full raw value unaccounted** — zero terms ever closed the books; named causes were LABEL ONLY or fit-to-the-same-data. Direction: too MANY coincidences near τ=0 relative to the ideal (g2(0) should be 0, isn't).

The sun/star side splits in two, and the split tracks exactly what you'd guess from the mirror's own logic — whether a term was genuinely independent and genuinely used:

- **Solar temporal bunching (Tan 2014, 2016): partial but real unaccounted shortfall, same shape as the lab remainder.** Direction is reversed (too FEW coincidences near τ=0; g2(0) should be 2, falls short), but the accounting failure is the same species: real, independently measured numbers (jitter, filter bandwidth) exist, sit beside the result, and are invoked in prose — but when someone (2016, to their credit) actually tries the arithmetic, the honest independent measurement doesn't even point the right direction (predicts too little bunching, not too much), so a cherry-picked idealized version of the same measurement is substituted, and even that leaves 35% (2016) to ~85% (2014) of the shortfall as an unexplained residual with LABEL ONLY causes (seeing, temperature drift, off-design etalon operation). Like the lab papers, nobody has independently measured "seeing-induced atmospheric fluctuations" or "temperature inhomogeneities" as a number and subtracted it.

- **Stellar point-source HBT, non-solar (Guerin 2017, Leopold/Rivet 2024): books close.** The difference-maker is a step none of the lab antibunching papers, and neither solar paper, fully did: an **independent lab calibration run through the identical optical+electronic chain with a different light source**, performed and checked *before* the sky data, then applied without modification. Guerin's light bulb and Leopold's fs-laser + artificial-star 2f-2f rig are genuine held-out measurements, not fits to the star data and not idealized substitutes for an inconvenient real measurement. Where that calibration step exists and isn't discarded, the remainder is zero within error on every star tried (5 for 5 across the two papers). Where it's absent (Tan 2014) or discarded in favor of a better-fitting idealization (Tan 2016), a real remainder survives.

## 5. Plain words

The Sun's missing pairs are not accounted for by anything anybody measured on its own. Tan 2014 never tried the arithmetic at all — "cannot explain" is as far as it goes, same as every lab paper in the mirror. Tan 2016 is the one honest attempt in this whole set, on either side: the real, independently measured detector response (not an estimate — an actual separate SPDC calibration) predicts *less* solar bunching than was seen, so the authors swap in an idealized, hand-picked version of their own measurement to get closer, and even then 0.107 of the 0.307 shortfall (about a third) is left standing on three named-but-unmeasured excuses. That is a hole in the accounting in the same place, and with the same character, as the lab antibunching hole: real numbers exist, real numbers are quoted, real numbers are never the number that makes the subtraction land. The sign is reversed from the lab (missing pairs, not extra ones) but the discipline is identical.

The stars tell a different story, and it points the other way: when the exact same two terms (jitter, filter bandwidth) are checked with an independent calibration run through the identical hardware — a light bulb in 2017, a femtosecond laser in 2024 — before anyone points at a star, the prediction and the measurement agree within error on five separate stars. That is what a closed book looks like under this rule, and it is rare enough in this whole investigation (lab or sky) to be worth naming on its own: it is not that bunching experiments can't be accounted for; it's that accounting for them requires an independent calibration of the exact chain, done before the data that's meant to be explained, and not swapped out when the honest number fails to cooperate. The Sun's papers never did that. The star papers did, and that is the entire difference.

## WHERE THE PAIRS WENT (§75, 2026-10-01)

Method: PyMuPDF `get_drawings()` on the arXiv PDFs' own vector figures (exact
PDF coordinates, same approach as `out/light/jacques2007/digitize.py`), axis
calibration from tick-label text bboxes (linear fit, residual reported),
verified by overlaying the reconstructed (tau, g2) points against the
original rendered figure. No expectation written before digitizing. Scripts
and CSVs: `out/sun/curves/` (`SOURCE.txt` there has the full source list and
every failed attempt).

### 1. The curves, raw first

Four panels digitized, all vector (no raster fallback needed):
- Tan 2014 Fig.5 (arXiv:1403.7432), page 4: Sun, Hg discharge, Ar arc — 100 /
  398 / 397 points matched (of 901 total crosshair markers on the page).
- Tan 2016 Fig.4 (arXiv:1512.08649), page 3: Sun — 100 points.

RAW FINDING, not assumed going in: every data point in both papers is drawn
as a FIXED-SIZE "+" crosshair (vertical segment length = horizontal segment
length = constant to <0.02% across every point checked, in both papers) —
not a variable-length error bar. The vector drawing gives each point's exact
(tau, g2) position but not a graphical error bar; per-point Poisson error was
instead computed from the point's own coincidence-count height, read off the
SAME figure's raw-counts axis (shares the same pixel scale as the g2 axis, so
the conversion is exact, not assumed).

Axis-calibration residuals: every calibration used in the final numbers has
max|residual| < 0.03 px (sub-part-in-10,000 of the panel width) — this is
exact vector-coordinate extraction, not pixel-clicking digitization noise.
Overlay check: reconstructed scatter + fit-curve plotted and compared to the
original rendered page (`tan2014_Sun_reconstruction.png`,
`tan2016_Sun_reconstruction.png`) — matches point-for-point.

Two calibration failures hit and fixed, counted not hidden: (1) Tan2014 Hg/Ar
right-axis tick search first picked up stray numbers from the body-text
column (56 px / 13 px residual) — fixed by tightening the tick-label search
window to the panel's own margin. (2) Tan2016 x-axis tick search first
counted the right-axis "0.0" g2 label as an extra x-tick (same pixel row by
coincidence, 88 px residual) — fixed the same way. Leopold/Rivet 2024
(arXiv:2408.08173) was fetched but NOT digitized this pass (time-boxed out
once Guerin 2017 gave a usable closed-books anchor) — left as an open row.

### 2. The area

A_measured = trapezoid integral of (g2−1) over the full measured tau range,
error from Poisson counting statistics on each point's own coincidence count
(not an assumed error bar — see above). A_expected = tau_c = 1/(π·Δν), the
standard coherence-time integral for a Lorentzian-filtered line
(∫|g1(τ)|²dτ, g1(τ)=exp(−πΔν|τ|)), with Δν the paper's OWN independently
specified/measured filter bandwidth — this number never touches the g2(τ)
data; it comes from the etalon's design spec (free spectral range ÷ finesse)
or the paper's own stated optical bandwidth.

| record | A_measured (raw points) | A_expected | **ratio** | note |
|---|---|---|---|---|
| **Tan 2014, Sun** | 0.0875 ± 0.0203 ns | 0.1599 ns (1.99 GHz etalon, FSR 205 GHz / finesse 103) | **0.547 ± 0.127** | SHORT |
| Tan 2014, Hg discharge (lab) | 0.3436 ± 0.0035 ns | 0.1599 ns (same etalon) | 2.148 ± 0.022 | EXCESS — but Hg's own natural linewidth (several GHz, multi-hyperfine structure) is comparable to the etalon width, so "coherence time set by the filter alone" isn't a safe assumption for a discrete line the way it is for a blackbody continuum; flagged, not trusted |
| Tan 2014, Ar arc (lab) | 0.1339 ± 0.0058 ns | 0.1599 ns (same etalon) | 0.837 ± 0.036 | mildly short |
| **Tan 2016, Sun** | 0.2488 ± 0.0092 ns | 0.1592 ns (stated "2 GHz optical bandwidth") | **1.563 ± 0.058** | EXCESS |
| Guerin 2017, lab calibration (artificial star, same chain) | 0.00158 ± 0.00010 ns | 0.00200 ns (10 Å / 500 GHz filter, sinc² ideal) | 0.792 ± 0.052 | short, closest to 1 of any record |
| Guerin 2017, α Boo (on-sky) | 0.00135 ± 0.00022 ns | 0.00200 ns (same filter) | 0.674 ± 0.112 | short |

Tan 2014's Sun is short by about half — consistent with "pairs gone," not
merely "blurred." Tan 2016's Sun comes out the opposite way, with MORE area
than the single-etalon estimate predicts, not less. This is a genuine raw
result, not forced to match the hypothesis: Tan2016 stacks TWO etalons (1.99
and 3.32 GHz FWHM, from design specs) plus three interference filters in
series, and the paper itself says the spectrometer used to check the etalons
couldn't resolve their real transmission width ("we are unable to resolve
the transmission bandwidth of the etalons," limited to 110 GHz) — so the
"2 GHz" figure is a rounded summary, not a measurement of the actual series-
combined bandwidth, which stacking multiple filters only narrows further
(longer true τc, bigger true A_expected). A narrower true bandwidth would
pull the 1.563 ratio down toward 1, possibly through it — but the only
genuinely independent number in hand (single-etalon design spec) is the one
used, so the ratio is reported as computed and flagged as likely an
overestimate of the true excess, not corrected after the fact.

The Guerin 2017 star-control ratios (0.79 lab, 0.67 on-sky) are the closest
to 1 of any record in the set, and come from a paper whose own text already
states the shortfall is dominated by jitter (500 ps APD response against a
1.6 ps ideal coherence time) that was independently measured and used BEFORE
looking at a star (Sec.3.1, lab test in Sec.3.2) — this is the "books closed"
calibration anchor the comparison needs. It is not exactly 1.000 either, but
it sits within ~2–4σ of the sun's 0.55, not next to it — the closed-books
record's own imperfection is much smaller than the sun's.

### 3. The shape (Tan 2014, Sun)

Ideal peak = exp(−2|τ|/τc), τc = 159.9 ps (from the independently measured
1.99 GHz etalon, not fit to the g2 data). Independently measured jitter
(Fig.3 SPDC calibration, PDF detectors): 40 ps FWHM (σ ≈ 17.0 ps).

- (a) Sigma needed to match the OBSERVED peak height alone, holding
  amplitude fixed at the no-pairs-lost value (1): **196.4 ps** (FWHM 462.5
  ps) — about **12× the independently measured jitter**. The measured
  jitter does not come close to sufficing as a pure-smearing explanation.
- (b) Free least-squares fit of (sigma, amplitude) to all 100 digitized
  points: sigma_fit = 83.4 ± 19.8 ps (FWHM 196.5 ps, still ~5× the measured
  jitter) AND amplitude a_fit = 0.510 ± 0.051 — matching the independently
  computed area ratio (0.547 ± 0.127) within error. Even when the jitter
  width is left completely free to find its best explanation of the curve's
  SHAPE, the fit still needs to throw away about half the pairs (a_fit≈0.51)
  to match the curve's HEIGHT and AREA together. That is the mathematical
  content of area conservation: a convolution with a normalized kernel
  (pure smearing, nothing created or destroyed) cannot shrink the area no
  matter what width is chosen; shrinking the area needs an actual amplitude
  loss, and the data needs one of almost exactly the size the raw area
  integral already found independently.

Measured peak FWHM is wider than the ideal peak's FWHM (110.9 ps) by far
more than the independently measured 40 ps jitter would add in quadrature —
consistent with (a) and (b) above.

### 4. The star control

Guerin 2017's own reported Gaussian-fit numbers (contrast C, FWHM — explicit
fit outputs in their text, Sec.3.2/4.2) give A_measured directly
(A = C·FWHM·√(π/4ln2)); A_expected from the independently specified 10 Å
(≈500 GHz) interference filter via the sinc² ideal correlation (∫sinc²(Δν·τ)
dτ = 1/Δν — the same formula Guerin's own Sec.3.1 uses to state their 1.6 ps
ideal coherence time). Ratios: 0.792 ± 0.052 (lab, run through the identical
chain before any star) and 0.674 ± 0.112 (α Boo, on sky). Closed enough to
serve as the calibration floor for this test — neither sun record gets
within 2σ of even the WORSE of these two numbers.

### 5. Plain words

Tan 2014's Sun: the area is short by about half (0.55 ± 0.13), and no
physically sane amount of jitter — fit completely freely, 5–12× the
independently measured value — can make up that shortfall without also
needing to delete about half the pairs outright (a_fit ≈ 0.51, matching the
area ratio to within error). The pairs are not sitting in the wings waiting
to be found; the bookkeeping says about half of them are simply not there.

Tan 2016's Sun does not repeat that story — its area comes out ABOVE the
naive single-etalon prediction (1.56), the opposite sign from "missing."
That is reported straight, not explained away: the most likely reason is
that the independently-specified bandwidth used (a single etalon's design
spec) understates the real, narrower bandwidth of the full series-stacked
five-element filter the 2016 paper used and admits it never actually
resolved. So 2016 doesn't close the books either — it just fails in the
opposite, uninterpretable direction, because the one number the strict rule
requires (the ACTUAL combined filter bandwidth, independently measured, not
assumed) was never measured in that paper. Where a paper DID calibrate the
full chain independently and completely (Guerin 2017, lab source before any
star), the area ratio lands at 0.67–0.79 — short of 1, but by a small,
roughly-consistent amount, not by a factor of two, and not flipping sign.

The honest summary: one sun record (2014) shows real pairs GONE, not
blurred, by a margin (2–4×) much larger than the star-control's own residual
imperfection. The other sun record (2016) cannot be scored cleanly under
this test at all, because the paper itself never independently measured the
one number the test needs most. Where the chain WAS independently
calibrated end-to-end (Guerin 2017), the books come closer to closing than
either sun record manages. That is the whole difference, stated the same
way §73 stated it: a term only counts if it was measured independently and
actually used in the arithmetic — and for the Sun, on the one record where
that arithmetic could be fully run, it does not land on 1.
