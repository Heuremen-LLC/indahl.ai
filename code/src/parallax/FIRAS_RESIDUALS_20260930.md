# FIRAS monopole residuals — raw pull + shape tests
Fetched 2026-09-30 from https://lambda.gsfc.nasa.gov/data/cobe/firas/monopole_spec/firas_monopole_spec_v1.txt
(LAMBDA "FIRAS CMB Monopole Spectrum" product page: https://lambda.gsfc.nasa.gov/product/cobe/firas_monopole_get.html)
Source table: Table 4 of Fixsen, Cheng, Gales, Mather, Shafer & Wright 1996, ApJ 473, 576 ("The Cosmic
Microwave Background Spectrum from the Full COBE/FIRAS Data Set"); LAMBDA v1 release May 2005.
Raw file saved at: ~/bones-forge/parallax/out/firas/firas_monopole_spec_v1.txt

43 bins, frequency 2.27–21.33 cm⁻¹ (~68–640 GHz), spacing ~0.4536 cm⁻¹, no gaps within the table.

## 1. What the table is
Column 2 = published spectrum (best-fit 2.725 K blackbody + the residual). Column 3 = **residual**
(observed minus best-fit blackbody), kJy/sr. Column 4 = 1σ uncertainty, kJy/sr. Column 5 = the
modeled Galactic emission at the Galactic poles that was fit and subtracted (along with a CMB dipole
term) before the monopole/residual was derived. This is the "what was subtracted."

Best-fit temperature as published: **T0 = 2.728 ± 0.004 K (95% CL)**, Fixsen et al. 1996. (LAMBDA
also cross-references the later Fixsen & Mather 2002/Fixsen 2009 recalibration, quoted elsewhere as
T0 = 2.72548 ± 0.00057 K — noted for comparison, not substituted.)

## 2. Raw residuals, plain numbers
Peak of the published spectrum: 383.478 MJy/sr (= 383,478 kJy/sr), at 5.45 cm⁻¹.

| freq cm⁻¹ | resid kJy/sr | σ kJy/sr | resid, ppm of peak | Galaxy model kJy/sr |
|---|---|---|---|---|
| 2.27 | 5 | 14 | 13.0 | 4 |
| 2.72 | 9 | 19 | 23.5 | 3 |
| 3.18 | 15 | 25 | 39.1 | -1 |
| 3.63 | 4 | 23 | 10.4 | -1 |
| 4.08 | 19 | 22 | 49.6 | 3 |
| 4.54 | -30 | 21 | -78.2 | 6 |
| 4.99 | -30 | 18 | -78.2 | 8 |
| 5.45 | -10 | 18 | -26.1 | 8 |
| 5.90 | 32 | 16 | 83.5 | 10 |
| 6.35 | 4 | 14 | 10.4 | 10 |
| 6.81 | -2 | 13 | -5.2 | 12 |
| 7.26 | 13 | 12 | 33.9 | 20 |
| 7.71 | -22 | 11 | -57.4 | 25 |
| 8.17 | 8 | 10 | 20.9 | 30 |
| 8.62 | 8 | 11 | 20.9 | 36 |
| 9.08 | -21 | 12 | -54.8 | 41 |
| 9.53 | 9 | 14 | 23.5 | 46 |
| 9.98 | 12 | 16 | 31.3 | 57 |
| 10.44 | 11 | 18 | 28.7 | 65 |
| 10.89 | -29 | 22 | -75.6 | 73 |
| 11.34 | -46 | 22 | -120.0 | 93 |
| 11.80 | 58 | 23 | 151.3 | 98 |
| 12.25 | 6 | 23 | 15.7 | 105 |
| 12.71 | -6 | 23 | -15.7 | 121 |
| 13.16 | 6 | 22 | 15.7 | 135 |
| 13.61 | -17 | 21 | -44.3 | 147 |
| 14.07 | 6 | 20 | 15.7 | 160 |
| 14.52 | 26 | 19 | 67.8 | 178 |
| 14.97 | -12 | 19 | -31.3 | 199 |
| 15.43 | -19 | 19 | -49.6 | 221 |
| 15.88 | 8 | 21 | 20.9 | 227 |
| 16.34 | 7 | 23 | 18.3 | 250 |
| 16.79 | 14 | 26 | 36.5 | 275 |
| 17.24 | -33 | 28 | -86.1 | 295 |
| 17.70 | 6 | 30 | 15.7 | 312 |
| 18.15 | 26 | 32 | 67.8 | 336 |
| 18.61 | -26 | 33 | -67.8 | 363 |
| 19.06 | -6 | 35 | -15.7 | 405 |
| 19.51 | 8 | 41 | 20.9 | 421 |
| 19.97 | 26 | 55 | 67.8 | 435 |
| 20.42 | 57 | 88 | 148.6 | 477 |
| 20.87 | -116 | 155 | -302.5 | 519 |
| 21.33 | -432 | 282 | -1126.5 | 573 |

Residual range across the 43 bins: -432 to +58 kJy/sr, i.e. -1127 to +151 ppm of peak intensity.
Over the 42 bins excluding the top-frequency edge bin (21.33 cm⁻¹), the range is -116 to +58 kJy/sr
(-302 to +151 ppm) — the last bin is a clear outlier, and it also carries by far the largest quoted
uncertainty (282 kJy/sr, i.e. the residual there is only ~1.5σ).

## 3. Shape tests, each against 1000 shuffles of the residuals across frequency bins
Test statistics: (a) monotone — Pearson correlation of residual value against bin-order index;
(b) single bump/dip — best weighted-least-squares-fit Gaussian amplitude over a grid of 20 centre
positions × 7 widths (1–12 cm⁻¹), amplitude solved in closed form per grid point (avoids the
runaway-narrow-width overfit failure mode of a free nonlinear fit on sparse, noisy data — that
was tried first and discarded after it produced amplitudes >10,000 kJy/sr on pure noise); (c)
periodic ripple — Lomb-Scargle on residual vs. frequency, top normalized power in the scanned band.

- (a) Monotone trend: observed stat = -0.271; shuffled null mean = 0.003, std = 0.150.
  **p (two-sided) = 0.044** — borderline "significant" at the 5% level, but it is driven almost
  entirely by the single large negative outlier at the top-frequency edge bin (21.33 cm⁻¹, -432
  kJy/sr, only 282 kJy/sr σ — a low-confidence point at the edge of the calibrated band). Not
  robust; one bin carries the whole result. Noted, not treated as a real trend.
- (b) Single Gaussian bump/dip: observed best-fit amplitude = 7.93 kJy/sr; shuffled null mean =
  110.3, std = 39.7 kJy/sr. **p (≥ observed) = 1.000.** The real residuals fit a bump/dip shape
  *worse* than essentially all 1000 shuffles — no bump or dip survives.
- (c) Periodic ripple (Lomb-Scargle): observed top power = 0.139; shuffled null mean = 0.119, std =
  0.017. **p (≥ observed) = 0.106.** Not significant.

Net: 3 shape tests run, 0 survive at a level that isn't fully explained by one edge bin. The one
borderline result (monotone trend, p=0.044) collapses to non-significant if the top-frequency bin
is excluded — this was checked but not formally re-run as a fourth shuffle test; flagged as a try,
not a finding.

## 4. mu and y spectral-distortion limits (Fixsen et al. 1996, 95% CL) and energy fractions
- |y| < 1.5×10⁻⁵ → ΔE/E ≈ 4y < 6.00×10⁻⁵ = **60 ppm** of the CMB's energy density.
- |μ| < 9.0×10⁻⁵ → ΔE/E ≈ 0.714μ < 6.43×10⁻⁵ = **64 ppm** of the CMB's energy density.
In plain words: whatever additional energy could have been dumped into or pulled out of the CMB
photon bath after it last thermalized, and gone undetected by FIRAS, is capped at roughly six
hundredths of one percent of the total CMB energy, for either kind of distortion (Compton-y-type
or chemical-potential-μ-type).

## 5. The subtracted half — Galactic model amplitude vs. residual scatter, 3 groups of ~14 bins
(Galaxy model = column 5, the poles-Galactic-emission component fit and removed along with the
dipole before the monopole/residual was derived; groups are thirds by bin index, not halves.)

| group | freq range (cm⁻¹) | mean \|Galaxy model\| (kJy/sr) | residual std (kJy/sr) | ratio Gal/residual-std | mean σ (kJy/sr) | ratio Gal/σ |
|---|---|---|---|---|---|---|
| low | 2.27–8.17 | 10.1 | 17.6 | 0.57 | 16.9 | 0.60 |
| mid | 8.62–14.52 | 96.8 | 24.3 | 3.99 | 19.0 | 5.09 |
| high | 14.97–21.33 | 353.9 | 112.9 | 3.13 | 59.1 | 5.98 |

At low frequency the subtracted Galactic term is smaller than the leftover residual scatter (it
barely mattered). By mid and high frequency the subtracted Galactic model is 3–6× larger than
either the residual scatter or the quoted 1σ uncertainty — the thing removed dwarfs what's left
over, meaning the high-frequency residuals ride on top of a much bigger subtraction and are more
exposed to Galactic-model mis-specification than the low-frequency ones are.

## 6. Absence — excluded or flagged bins
None flagged within the table: all 43 published bins are used, contiguous, no missing rows, no
in-table flags. But the absence is at the edges of the table itself: this monopole file only covers
2.27–21.33 cm⁻¹ (43 low-frequency FIRAS channels). FIRAS took data further into the high-frequency
band (up to ~97 cm⁻¹ instrument range); those channels are not merely flagged here, they are not
part of this published monopole-fit table at all — they were excluded from the blackbody-fit
dataset upstream of this table, not dropped as outliers within it. The single highest-frequency bin
that IS included (21.33 cm⁻¹) has by far the largest σ (282 kJy/sr, ~1.8× the next-largest) and the
largest-magnitude residual (-432 kJy/sr) — it sits right at that boundary and behaves like the
table's weakest, most marginal point rather than a clean interior measurement.

## Files
- ~/bones-forge/parallax/out/firas/firas_monopole_spec_v1.txt (raw fetch)
- ~/bones-forge/parallax/out/firas/fetch_date.txt (fetch timestamp, UTC)
- ~/bones-forge/parallax/out/firas/firas_monopole_get.html (LAMBDA product page, saved empty/redirect — see note below)
