# FIRAS high-frequency channel — public per-pixel product found, fetched, monopole derived
2026-09-30. Follow-on to Rabbit 2 in `THREE_RABBITS_20260930.md`, which found the CIB monopole
table but not a per-pixel high-channel product. This time the per-pixel product was found,
fetched, and used to derive the monopole directly, per Wayfinder's instruction. No expectation
written before running any of the three cuts below.

## 1. What exists, where, and what was fetched

LAMBDA product-table page (`https://lambda.gsfc.nasa.gov/product/cobe/firas_prod_table.html`)
lists a **third-party HEALPix-format "Destriped Sky Spectra"** product, separate from the
original (non-HEALPix, 4.3 MB/file) FIRAS project data set. The HEALPix version is the smallest
per-pixel product that gives spectra for the high channel:

- Page: `https://lambda.gsfc.nasa.gov/product/cobe/firas_tpp_all_get.html`
- File fetched: `firas_hpx_destriped_sky_spectra_high_v2.fits`, 2,301,120 bytes (2.2 MB), from
  `https://lambda.gsfc.nasa.gov/data/cobe/hpx_firas/destriped_spectra/firas_hpx_destriped_sky_spectra_high_v2.fits`
  HTTP 200, full download verified. Saved at
  `parallax/out/firas/high/firas_hpx_destriped_sky_spectra_high_v2.fits`.
- Sibling low-frequency file also listed at the same path
  (`firas_hpx_destriped_sky_spectra_lowf_v2.fits`) but not needed for this task.
- The original (non-HEALPix) FIRAS project data set page
  (`https://lambda.gsfc.nasa.gov/product/cobe/firas_dss_get.html`) also lists
  `FIRAS_DESTRIPED_SKY_SPECTRA_HIGH.FITS` (4.3 MB) plus three narrower-band splits (HIF2/HIF3/HIF4,
  4.3 MB each) — not fetched, since the HEALPix version is smaller and sufficient.
- Format/anc page `firas_spectral_anc.html` gives no PASS4 calibration citation and no explicit
  high-channel reliability caveat of its own — the calibration-model label comes from the FITS
  header itself (below), not from that page's prose.

### FITS structure (parsed by hand, no numpy/astropy on this machine — stdlib `struct` reader,
`parallax/out/firas/high/parse_firas_high.py`)

Primary header: `TELESCOP=COBE`, `INSTRUME=FIRAS`, `PRODUCT=SKY-DEST-HPX`, `PIXTYPE=HEALPIX`,
`ORDERING=NESTED`, `NSIDE=16`, `NPIX=3072`, `CHANSCAN=HIGH`, **`MODLLABL=PASS4`** (the FIRAS
calibration-model solution label — this is the calibration referenced by name in the file; no
separate calibration paper was fetchable this session, web-search budget for the session was
exhausted mid-task; the standard citation for the PASS4 solution is Fixsen et al. 1994, ApJ 420,
445, "Calibration of the COBE FIRAS instrument" — named from memory, not verified by fetch here,
flagged as such), `MISS_SEG=ENTIRE_MISSION`, `NU_ZERO=612.18729 GHz`, `DELTA_NU=13.604162 GHz`,
`NUM_FREQ=170` (good channels).

Binary table extension: 3072 rows (one per HEALPix pixel), 6 columns: `PIXEL` (int32),
`GAL_LON`/`GAL_LAT` (float32, deg), `WEIGHT` (float32), `STR_USED` (uint8 flag, used in
destriping), `SPECTRUM` (182 x float32, MJy/sr). **No per-channel uncertainty/sigma column exists
in this product** — that is an absence, noted below.

## 2. Absences the product itself flags or leaves empty

- Of the 182 stored spectral channels, only the first **170** are populated (`NUM_FREQ=170`,
  confirmed by direct inspection: channels 0–169 have real values, channels **170–181 are exactly
  zero in all 3072 pixels**, every one). These correspond to 2924.9–3074.5 GHz = **97.56–102.56
  cm⁻¹** — a 12-channel gap the product leaves empty above its stated good range.
- **29 of 3072 pixels have `WEIGHT = 0.0` and `SPECTRUM = 0.0` in every channel** — unobserved/
  masked sky, excluded from every average below (weight-weighted averaging drops them naturally).
- **96 of 3072 pixels have `STR_USED = 0`** (flagged as not used in the destriping solve) but do
  carry non-zero weight and spectrum — included in the averages below since the task asked for
  pixel-coverage weighting, not a destriping-participation cut; flagged so this choice is visible.
- **No per-channel uncertainty is provided** in this HEALPix product (unlike the low-frequency
  Table 4 monopole product, which does carry a sigma column) — residuals below have no attached
  error bar from the product itself.
- Good-channel frequency range actually covered: **20.42–97.11 cm⁻¹** (612.19–2911.29 GHz) —
  slightly wider than the product page's rounded "20–95 cm⁻¹" summary language.

## 3. Derivation method

Script: `parallax/out/firas/high/derive_monopole.py`. For each of the 170 good channels, per cut:
weight-weighted mean of `SPECTRUM` over kept pixels (`WEIGHT`-weighted, pixels with `WEIGHT<=0`
dropped). Residual = weighted-mean observed MJy/sr − Planck function B_ν(2.728 K) at that channel's
center frequency (MJy/sr). ppm = residual / 383.478 MJy/sr (the published low-frequency-channel
peak intensity, same normalization used in `FIRAS_RESIDUALS_20260930.md`, kept consistent across
documents) × 1e6. **No foreground (Galaxy/zodiacal light) model was subtracted** — this is
critical and is the reason the numbers below are large: this is the raw sky-average high-channel
brightness compared to a bare 2.728 K blackbody, not a foreground-cleaned monopole. That is
exactly what "derive the monopole yourself" from the raw per-pixel product means without importing
someone else's foreground fit.

Three groups of three (galactic cuts), pixel counts (of 3043 pixels with nonzero weight, out of
3072 total):
1. `|b|<20°` excluded → **1980 pixels kept**.
2. `|b|<40°` excluded → **1091 pixels kept**.
3. No cut → **3043 pixels kept** (all nonzero-weight pixels).

Full per-bin table (170 rows × 3 cuts): `parallax/out/firas/high/monopole_high_per_bin.tsv`.
Summary/metadata: `parallax/out/firas/high/monopole_high_summary.json`.

## 4. Results — residual per bin, three cuts (selected rows; full 170-row table in the TSV)

| chan | freq cm⁻¹ | BB(2.728K) MJy/sr | cut1 (\|b\|≥20) resid ppm | cut2 (\|b\|≥40) resid ppm | cut3 (no cut) resid ppm |
|---|---|---|---|---|---|
| 0 | 20.42 | 7.112 | 2,719 | 1,673 | 9,929 |
| 20 | 26.72 | 0.203 | 5,589 | 3,762 | 20,245 |
| 50 | 37.42 | 0.00062 | 9,431 | 6,586 | 33,246 |
| 100 | 56.23 | ~0 | 14,656 | 10,168 | 48,825 |
| 150 | 84.67 | ~0 | 24,829 | 20,309 | 78,033 |
| 165 | 95.30 | ~0 | 40,819 | 37,480 | 78,973 |
| 169 (last good) | 97.11 | ~0 | **-55,569** | **-59,274** | **-81,784** |

(Row 169, the single highest-frequency good channel, flips sign in all three cuts — same pattern
as the low-frequency Table 4's flagged edge bin at 21.33 cm⁻¹, which was also the noisiest,
lowest-confidence point. Read as an edge/noise artifact, not a real feature, consistent with how
the low-frequency edge bin was treated in `FIRAS_RESIDUALS_20260930.md`.)

Whole-range summary stats (170 bins, all three cuts):
- Cut 1 (\|b\|≥20°): mean 16,236 ppm, range -55,569 to +49,196 ppm, Pearson r (resid vs freq) =
  **0.500** over all 170 bins, **0.957** restricted to the first 100 bins (20.4–37.0 cm⁻¹, before
  the high-frequency noise floor dominates).
- Cut 2 (\|b\|≥40°): mean 11,072 ppm, range -59,274 to +37,572 ppm, r = **0.477** (all bins),
  **0.959** (first 100 bins).
- Cut 3 (no cut): mean 52,993 ppm, range -81,784 to +127,799 ppm, r = **0.580** (all bins),
  **0.953** (first 100 bins).

**Tests run: 3** (one Pearson r-vs-frequency per cut, each computed twice — full 170-bin range
and first-100-bin sub-range — so 6 numbers reported, 3 independent cuts). No shuffle-null test was
run this pass (unlike the low-frequency shape tests in `FIRAS_RESIDUALS_20260930.md`) — flagged as
a thing not done, not a finding.

## 5. Shape verdict

**Matches thermal dust, not a flat CMB deviation.** All three cuts rise steeply and near-
monotonically with frequency (r = 0.95–0.96 in the cleaner first-100-bin range, weakening only at
the highest, noisiest, sign-flipping edge channels) — this is exactly the shape of Galactic (and,
in the tighter cuts, residual high-latitude/zodiacal) dust emission rising toward the Wien side,
not a flat or oscillating spectral distortion. Magnitude also tracks galactic-plane inclusion
directly: cut 3 (full sky, plane included) sits roughly 3–5× above cut 1/cut 2 (high-latitude
only) at every frequency, exactly as expected if the residual is dominated by real Galactic dust
that was never subtracted here. This is the textbook, published explanation (Fixsen et al. 1998's
CIB monopole paper subtracts precisely this dust + Galaxy + zodi model from the same high channel
to isolate the cosmic infrared background) — reported as such, not treated as a residual anomaly.
The comparison to Rabbit 2's already-published, foreground-subtracted CIB monopole table
(`parallax/out/firas/rabbits/rabbit2_highfreq_residuals.txt`, -6,187 to +15,509 ppm) shows the
size of what foreground subtraction actually removes: roughly an order of magnitude in most bins.

## 6. What stopped further work

- No per-channel uncertainty exists in this product (see §2) — residuals above have no formal
  error bar; only the low-frequency Table 4 product publishes one.
- WebSearch budget for this session was exhausted (200/200 used) partway through — could not
  independently verify the Fixsen et al. 1994 PASS4 calibration-paper citation by fresh search;
  it is stated from memory and flagged, not confirmed by fetch this session.
- No shuffle-null significance test was run on the frequency trend (see §4) — the Pearson r values
  are raw correlations, not tested against a random-shuffle null the way the low-frequency
  residuals were in `FIRAS_RESIDUALS_20260930.md`. Straightforward to add; not done this pass.
- The non-HEALPix, per-scan-mode originals (`FIRAS_DESTRIPED_SKY_SPECTRA_HIGH.FITS` and the
  HIF2/HIF3/HIF4 splits, 4.3 MB each) were not fetched — the HEALPix product already answers the
  task and is smaller; those remain available at
  `https://lambda.gsfc.nasa.gov/data/cobe/firas/destriped_spectra/` if finer per-scan-mode detail
  is ever wanted.

## SHUFFLE FLOOR

2026-09-30, follow-on. The item flagged above ("No shuffle-null significance test was run on the
frequency trend") is closed here, plus a dust-subtraction pass that wasn't in the original scope.
Public data only, single process, pure stdlib (no numpy/scipy on this machine — checked fresh this
pass, still absent). Scripts: `parallax/out/firas/high/shuffle_floor.py` (writes
`shuffle_floor_results.json` and `resid_of_resid_per_bin.tsv`). RNG seed 20260930, fixed and
stated. **12 shuffle-floor tests run, 1000 shuffles each, 12,000 shuffle iterations total** — 3
frequency-trend tests (one per cut) + 9 dust-subtracted shape tests (3 cuts x 3 tests). Counted by
the script itself (`totals` block in the JSON), not asserted by hand. Wall time 17.6 s, single
process, no binary splits.

Methodology matches `FIRAS_RESIDUALS_20260930.md` §3 exactly: (a) monotone = Pearson r of value vs.
bin-order index, p = frac(|shuffled| >= |observed|), two-sided; (b) bump/dip = best
closed-form-amplitude Gaussian fit over a grid (20 centres x 7 widths here, spanning the full
20.4–97.1 cm⁻¹ band), p = frac(|shuffled best-amp| >= |observed best-amp|); (c) ripple = Lomb-Scargle
top normalized power over 60 trial periods (2x bin spacing to full band width), p =
frac(shuffled power >= observed power). Same 1000-shuffle convention throughout.

**Caveat carried forward:** this per-pixel destriped product has no per-channel uncertainty column
(same absence noted in §6 above), so every fit and slope below is unweighted (ordinary least
squares), not inverse-variance weighted. Stated, not smoothed over.

### 1. Frequency-trend shuffle floor (resid_ppm vs freq_cminv, OLS slope, unweighted)

| cut | observed slope (ppm/cm⁻¹) | null mean | null std | p |
|---|---|---|---|---|
| cut1_excl_b20 | 194.62 | -0.50 | 30.70 | **0.000** |
| cut2_excl_b40 | 165.89 | 0.18 | 26.71 | **0.000** |
| cut3_no_cut | 569.24 | 2.08 | 76.32 | **0.000** |

All three: 0/1000 shuffles produced |slope| >= observed. The steep rise-with-frequency reported in
§3–5 above is not an artifact of bin order — it is maximally significant against this null (p <
0.001 at 1000 shuffles; true p is likely far smaller, this test just can't resolve below 1/1000).
Consistent with dust, as expected, but now shown rather than assumed.

### 2. Modified-blackbody dust fit per cut (A x nu^beta x B_nu(T), T and beta free, A closed-form
OLS at each grid point, grid search + local refine, no scipy.optimize used or available)

| cut | T (K) | beta | A | SSE (MJy/sr)^2 |
|---|---|---|---|---|
| cut1_excl_b20 | 28.3 | 0.75 | 7.979e-6 | 1208.3 |
| cut2_excl_b40 | 30.2 | 0.85 | 3.876e-6 | 1121.4 |
| cut3_no_cut | 21.3 | 1.55 | 3.290e-5 | 3910.0 |

T grid scanned 2.0–30.0 K (step 0.5, refined to 0.1), beta grid 0.0–6.0 (step 0.25, refined to
0.05). All three land near-plausible-but-not-identical dust temperatures (T ~21–30 K is in the
right ballpark for warm Galactic dust; beta 0.75–1.55 spans the low end of typical emissivity
indices ~1.5–2). The three cuts do NOT converge to the same (T, beta) — cut3 (full sky, most dust)
pulls to a visibly different fit (lower T, higher beta) than cut1/cut2 (high-latitude only,
b >= 20/40) which land close to each other. A single dust component does not describe all three
cuts identically; not surprising since cut3 mixes plane and high-latitude dust with different mean
temperature, but worth stating plainly: this is a one-component fit, not a validated dust model.

### 3. Dust-subtracted residual-of-residual: shape tests (per cut, ppm units, same 1000-shuffle
convention as above)

| cut | test | observed | null mean | null std | p |
|---|---|---|---|---|---|
| cut1 | monotone | 0.00723 | 0.00174 | 0.0773 | 0.931 |
| cut1 | bump | 3433.5 | 4546.3 | 1341.9 | 0.838 |
| cut1 | ripple | 1.689 | 2.725 | 0.649 | 0.972 |
| cut2 | monotone | -0.00855 | -0.00059 | 0.0774 | 0.915 |
| cut2 | bump | 4278.1 | 4372.3 | 1342.6 | 0.472 |
| cut2 | ripple | 1.853 | 2.633 | 0.600 | 0.920 |
| cut3 | monotone | -0.00658 | 0.00158 | 0.0788 | 0.931 |
| cut3 | bump | 4159.0 | 8364.3 | 2634.6 | 0.976 |
| cut3 | ripple | 1.595 | 2.712 | 0.614 | 0.973 |

**0 of 9 dust-subtracted shape tests reach p < 0.05.** Lowest p is cut2's bump test at 0.472 — not
close to significant. All nine sit at or above the null mean; several (all three ripple tests, two
of three bump tests) score *worse* than a majority of pure-noise shuffles, same "fits worse than
noise" pattern the low-channel report found for its bump test. Net: after removing the fitted
one-component dust model, no monotone trend, no single bump/dip, no periodic ripple survives in
any of the three cuts.

### 4. Cross-cut comparison of the dust-subtracted residual-of-residual (ppm)

Full 170-bin band (20.4–97.1 cm⁻¹):

| | mean | std | min | max |
|---|---|---|---|---|
| cut1 | -17.6 | 6952.2 | — | — |
| cut2 | 71.3 | 6697.1 | — | — |
| cut3 | -20.2 | 12506.1 | — | — |
| cut1 minus cut2 | -88.8 | 1186.2 | -4727.0 | 7641.4 |
| cut1 minus cut3 | +2.6 | 6248.7 | -45391.8 | 58239.7 |
| cut2 minus cut3 | +91.4 | 6848.5 | -52439.2 | 58469.0 |

Per-bin table: `parallax/out/firas/high/resid_of_resid_per_bin.tsv` (170 rows, all 3 cuts + the
cut1-minus-cut3 diff column, ppm).

The full-band std of the cut differences is dominated by a handful of channels at/near the top of
the band (chan 163–169, freq 94.4–97.1 cm⁻¹ — adjacent to the 12 empty padding channels flagged in
§2/summary JSON, i.e. the same weak-edge-of-calibrated-band problem the low-channel report flagged
for its own top bin) plus one isolated in-band spike at chan 95 (63.5 cm⁻¹, cut3 leftover =
+57358 ppm, driving a -45392 ppm cut1-minus-cut3 difference at that single bin). Restricting to the
154 bins below 90 cm⁻¹ (dropping the noisiest edge, a robustness check only, not a re-run shuffle
test): cut1 mean/std = 19.5/2077.3 ppm, cut3 mean/std = 55.0/5555.6 ppm, cut1-minus-cut3 mean/std =
-35.5/4093.7 ppm (still carrying the chan-95 spike in its min/max).

**Plain statement:** the dust-subtracted leftover DOES change with galactic cut, in both the
full-band and edge-trimmed views — cut3's std (12506 ppm full-band, 5556 ppm core-band) is roughly
1.8-2.7x cut1's or cut2's, and cut2-minus-cut3 / cut1-minus-cut3 differences run into the tens of
thousands of ppm at individual bins, not the low tens or hundreds a real cut-independent CMB
signature would produce. Means (aggregate, full band) are all within about +/-90 ppm of zero and of
each other, but the per-bin scatter is not cut-independent. Per the framing given at the top of the
task: a real CMB monopole leftover would not depend on galactic cut; this one visibly does, both in
spread and in the specific bins that spike. That is evidence of residual dust-model leakage (an
imperfect one-component modified-blackbody fit failing differently depending how much dust-laden
sky is in the cut), not evidence of new CMB structure. No claim of a CMB detection is made or
supported by these numbers.

### Files
- `parallax/out/firas/high/shuffle_floor.py` — script (frequency-trend shuffle floor, dust fit,
  dust-subtracted shape tests, cross-cut comparison)
- `parallax/out/firas/high/shuffle_floor_results.json` — full numeric output, all 12 tests, dust
  fit params, per-bin resid-of-resid arrays
- `parallax/out/firas/high/resid_of_resid_per_bin.tsv` — 170 bins x 3 cuts, dust-subtracted
  residual-of-residual in ppm, plus cut1-minus-cut3 diff column
