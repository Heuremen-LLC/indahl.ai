# ARCADE HOLE — the death, the beams, the pickles, the six (2026-09-30)

Builds on `~/bones-forge/parallax/ARCADE_ABSENCE_20260930.md` and
`parallax/out/firas/rabbits/arcade/`. No expectation written before running any measurement
below. Raw numbers first, background for every claim, every test counted, all scripts/data
under `parallax/out/firas/rabbits/arcade/hole/`.

---

## 1. THE DEATH — when the 5 GHz channel died

**New source read this pass:** Kogut et al. 2011 (arXiv:0901.0562) and Singal et al. 2011
(arXiv:0901.0546) full text (previous doc only had abstract-level quotes on this point),
extracted to text and grepped for launch/flight/timing language
(`hole/Kogut_galactic.txt`, `hole/Singal_instrument.txt`).

**Raw finding, verbatim (Kogut et al. 2011, §2):** *"The ARCADE 2 instrument launched from
the Columbia Scientific Balloon Facility in Palestine, TX carrying a complement of 7
Dicke-switched radiometers and 1800 liters of liquid helium. During ascent, the Dicke switch
failed in one radiometer. The remaining radiometers began sky observations on 2006 July 22
at 05:08 UT, continuing through 08:11 UT just prior to flight termination."*

**Flight timeline (Singal et al. 2011, §2.7):** cool-down and fill, then launch; *"After
three hours of ascent, float altitude is reached and we open the instrument lid for
observing... We observe for around four hours"* (2006 flight: 05:08–08:11 UT, ~3h03m,
shorter than the nominal 4h — *"limited by the westward drift of the balloon out of range of
telemetry"*); lid closed for descent; ~800 L helium remained at flight end. Singal 2011
separately: *"the most significant instrumental failure was with the 5 GHz MEMS switch,
rendering data from that channel not useful for science analysis."*

**Pin: the 5 GHz switch failed during ascent, before 05:08 UT on 2006-07-22 — before the
lid was ever opened.** The FITS header `DATE` field on every one of the 12 public 2006 sky
maps reads `2006-07-22T05:08:00` (checked directly, all 12 files, see §2 below) — i.e. the
one timestamp attached to the public data products is the float/lid-open moment, matching
Kogut's number exactly. No finer within-ascent time (minutes into the 3-hour ascent) is given
in either paper — say so plainly, this is as precise as the public record gets.

**What every other channel shows at or near that moment: nothing, and here is why that is
itself the finding.** The lid stays *closed* through the entire ~3-hour ascent (Singal 2011:
the lid is opened only "after three hours of ascent... for observing"). That means **the 5
GHz failure occurred before any radiometer — failed or surviving — had a science photon on
its horn.** There is no gap, step, or transient to hunt for in the surviving channels' sky
data at the failure moment, because the failure predates the sky-observation window
entirely by construction. This is a clean, checkable non-null result, not an evasion: the
"excess" narrowing search window Wayfinder pointed at does not include a same-flight
instrumental-transient candidate at the moment of failure, because the instrument was
blind (lid shut) when it happened.

**A related, separately-timed anomaly that DOES fall inside the observing window** (Singal
2011, §3.3, new to this doc): *"In the 2006 flight, we experienced problems with temperature
controlling the 3 and 8 GHz internal reference loads, both becoming fixed at near the liquid
helium bath temperature for significant periods of the flight. In the case of the 3 GHz load,
this was likely caused by the insulative housing falling off, which was observed upon
completion of the flight."* No exact within-flight timestamp given for this either, but it is
explicitly *during* observing (not ascent) and hits **exactly the two channels carrying the
"pickles"** (3 GHz) and the channel used as the Galactic-model cross-check (8 GHz). Flagged,
not resolved: no public product lets us check whether this reference-load anomaly is
time-correlated with any particular sky pixel.

**Tries:** 2 full papers fetched and text-extracted (new this pass, `pypdf`, both saved to
`hole/`), grepped for 6 keyword classes; 1 exact quote pinning ascent-phase failure; 1
independent cross-check (FITS DATE header, all 12 files) confirming the 05:08 UT number;
2 reference-load anomalies found and reported that do NOT resolve the failure-moment question
but bear directly on the 3/8 GHz channels.

---

## 2. THE BEAMS — derived from the public maps, not the design spec

**Data:** all 12 public ARCADE 2 sky maps pulled directly from LAMBDA
(`lambda.gsfc.nasa.gov/data/suborbital/ARCADE/arc2_*_v19.fits`, 31,680 bytes each, 384 KB
total — copied to `hole/arcade_maps/`). Format, read directly from the FITS headers (not
assumed): HEALPix, NESTED, NSIDE=16 (3072 pixels, ~3.66° per pixel), Galactic coordinates,
TEMPERATURE (K) + N_OBS (0.5 s integrations/pixel) per pixel. Design beam stated in-header
(`BEAMSZ`): **11.6° FWHM for 11 of 12 files; the 30# narrow-beam variant (`arc2_29500s`)
states 4.0°.** Coverage per channel: 207–232 observed pixels, i.e. **6.7–7.6% of the sky** —
matches Kogut's stated "roughly 7% of the sky" per radiometer exactly.

**One raw oddity, found not sought:** the FITS `FREQ` header for the two 90 GHz-named files
(`arc2_88200_v19.fits`, `arc2_89800_v19.fits`) reads **22664 and 24264 (MHz)**, not 88200/89800
as the filenames and the 2011 papers' Table 4 (88.2/89.8 GHz) claim. Not resolved this pass —
flagged as a public-product labeling inconsistency, filed, not explained (candidate: an
intermediate/mixer frequency left in the header by mistake, per Singal's note that the 90 GHz
warm stage mixes down with a 79.5 GHz local oscillator — but 88200−79500=8700 and
89800−79500=10300, neither matches 22664/24264, so that specific explanation does not fit
either; left open).

**Method (script: `hole/beam_from_maps.py`):** per channel, two independent effective-beam
proxies computed straight from pixel data, no beam assumed:
1. **Galactic-plane-crossing width:** bin observed pixels by Galactic latitude b (3° bins,
   −60° to +60°), baseline = median T at |b|>20°, find the FWHM of the excess-above-baseline
   peak nearest b=0.
2. **Compact-feature width:** find the single brightest observed pixel, bin all other observed
   pixels by angular distance from it (3° bins), find the FWHM of the excess-above-baseline
   falloff.

**Raw results, all 12 channels (full table in `hole/beam_results.json`):**

| file | freq (hdr, MHz) | design beam (°) | pixels obs. | Galactic-plane-crossing FWHM (°) | compact-feature FWHM (°) |
|---|---|---|---|---|---|
| arc2_3150 | 3150 | 11.6 | 220 | 17.93 | 9.89 |
| arc2_3410 | 3410 | 11.6 | 232 | 17.16 | 9.27 |
| arc2_7970 | 7970 | 11.6 | 207 | 17.54 | 7.32 |
| arc2_8330 | 8330 | 11.6 | 215 | 17.41 | 9.20 |
| arc2_9720 | 9720 | 11.6 | 215 | 16.43 | 8.66 |
| arc2_10490 | 10490 | 11.6 | 214 | 14.31 | 8.48 |
| arc2_29500 | 29500 | 11.6 | 214 | 2.52 | 2.77 |
| arc2_29500s | 29500 | 4.0 | 213 | 5.57 | 3.10 |
| arc2_31000 | 31000 | 11.6 | 213 | 1.51 | 2.95 |
| arc2_31000s | 31000 | 11.6 | 214 | 3.65 | 3.21 |
| arc2_88200 | (22664) | 11.6 | 208 | 10.67 | 3.63 |
| arc2_89800 | (24264) | 11.6 | 216 | 16.55 | 4.12 |

**Read plainly, with the honest caveat first:** at 3.66°/pixel with only ~210–230 observed
pixels spread over 7% of the sky, both proxies are **undersampled relative to an 11.6° beam**
(roughly 3 pixels per beam FWHM, and large gaps between sampled points away from the scan
track) — neither measure should be read as a real beam recalibration. That said, the *pattern*
across channels is informative and was not assumed in advance:
- **The 3/8/10 GHz channels** (where Galactic synchrotron is bright) show a Galactic-plane
  crossing width (14–18°) *wider* than the 11.6° design beam — expected, since the true
  Galactic ridge itself has finite width and convolves with the beam.
- **The 30/31 GHz channels** collapse to implausibly narrow crossing widths (1.5–5.6°),
  narrower than either sub-band's own pixel size in places — this is not a real beam, it is
  the peak-finder locking onto noise once the Galactic signal has dropped below it (Fixsen
  2011 Table 2: Galactic subtraction at 30 GHz is only 0.07–0.08 mK, i.e. no real plane
  crossing to measure there with these S/N and pixel counts).
- **The compact-feature FWHM is narrower than the 11.6° design beam at every single one of
  the 12 channels** (2.8–9.9° vs 11.6° design) — this is the clearest, most direct
  confirmation from the data itself of Singal's own stated limitation (§4 below): the public
  maps are too coarsely and sparsely sampled to recover the true beam shape from a bright
  feature. **The channel whose derived beam differs most from design is 29.5/31 GHz** (both
  measures), by construction of the low-S/N argument above.

**Tries:** 12 files downloaded and parsed (HEALPix NESTED via `healpy.pix2ang`, cross-checked
against `NPIX = healpix.nside2npix(NSIDE)` for all 12); 24 FWHM measurements attempted
(2 per channel); 0 discarded as unrunnable (all 24 produced a number, several flagged above as
not physically meaningful).

---

## 3. THE 3 GHz PICKLES — spatial structure of the residual

**Important scope limit, stated up front:** the actual Kogut et al. 2011 Galactic model
(408 MHz Haslam template + C II template, jointly fit) is not itself a downloadable map
product on LAMBDA — only the raw sky TEMPERATURE maps are public. So the "published Galactic
model" cannot be subtracted pixel-for-pixel here. What follows uses a **crude zeroth-order
stand-in** (each map's own median temperature over its observed pixels, i.e. a flat monopole
removal) as the "model," explicitly weaker than Kogut's fit — the real point is what its
residual correlates with, not its absolute size.

**Method (script: `hole/pickles_3ghz.py`):** for 3.15 and 3.41 GHz, take the ~185–197 pixels
that overlap in sky coverage with the 8.33 GHz map (same HEALPix grid, so pixel-for-pixel
comparison is exact, no regridding). Residual = pixel T − channel's own observed-sky median.
Three Pearson correlations per channel, each against a 20,000-shuffle permutation null
(exact, not asymptotic):

**Raw results:**

| freq | n common px | residual mean (mK) | r vs \|b\| | p (perm) | r vs signed b | p (perm) | r vs 8.33 GHz residual | p (perm) |
|---|---|---|---|---|---|---|---|---|
| 3.15 GHz | 185 | +36.8 | **−0.730** | <0.0001 | −0.039 | 0.605 | **+0.913** | <0.0001 |
| 3.41 GHz | 197 | +30.7 | **−0.739** | <0.0001 | −0.019 | 0.794 | **+0.919** | <0.0001 |

Residual by |b| tertile (nearest-plane / mid / farthest, mK): 3.15 GHz: **119.0, 4.9, −12.1**;
3.41 GHz: **104.7, 2.4, −13.8**. Peak single-pixel residual in both maps: **same location**,
l=33.75°, b=+2.4°, (3.15 GHz: +381 mK; 3.41 GHz: +354 mK) — an inner-Galaxy pixel, not a
random sky position.

**Read plainly: at this crude subtraction level, the residual is emphatically NOT a uniform
monopole.** It is strongly latitude-structured (falls off from +119 mK near the plane to
−12 mK far from it, r≈−0.73 to −0.74, p<0.0001 by exact permutation, n=185–197) and it
tracks the co-pointed 8.33 GHz channel's own residual pixel-for-pixel almost one-to-one
(r≈0.91–0.92). The peak-residual pixel is identical in location between the two 3 GHz
sub-bands. **This is exactly what is expected and textbook if the crude flat-monopole
subtraction simply fails to remove real Galactic structure that the sophisticated
Kogut fit was built to remove** — it is not, on its own, evidence about whether the
*published, properly-Galactic-subtracted* 58–67 mK excess is itself uniform or structured,
because that post-model residual map is not a public product (this is itself an instance of
can't-line #5/#2 below — the pipeline's final residual isn't independently checkable).
**Where the excess-as-measured-here lives on the sky:** concentrated toward the inner
Galactic plane (peak at l≈34°, b≈+2°), falling to consistent with-zero or negative at
|b|>20° — i.e. everywhere this crude test can see, it looks like Galaxy, not monopole. What
it does NOT tell us: whether Kogut's actual template fit leaves a similarly structured
residual after doing its job properly — no 2011 or later public product answers that,
reported as a gap, not closed.

**Tries:** 6 correlation tests run (3 per frequency × 2 frequencies), each with its own
20,000-permutation exact null (120,000 total permutation draws); 185–197-pixel common-coverage
sample per test, explicitly small, stated as such.

---

## 4. THE SIX — where 2020s public data can look, and whether the excess survives

Each row: the 2011 "can't," a named public 2020s-era dataset/paper that speaks to it today,
and whether the excess survives that check. Sources newly fetched this pass (arXiv IDs found
via the arXiv API, not memory): Dowell & Taylor 2018 (1804.08581), Vernstrom et al. 2023
(2301.03699), Singal et al. 2018 workshop report (1711.09979), a VLASS variable-source census
(2508.00976), Planck 2015 X (1502.01588), Planck 2018 IV (1807.06208).

| # | 2011 "can't" (verbatim source) | 2020s-era dataset that can look there | What it finds | Excess survive? |
|---|---|---|---|---|
| 1 | *"do not have sufficient angular resolution to reject discrete radio sources"* (Kogut 2011) | Vernstrom et al. 2023 — near-complete compendium of radio source counts at 150 MHz–8.4 GHz, incl. 3 & 5 GHz | Only at **3 GHz are the source-count contributions fully convergent** (best-determined band of all) — and even there a **factor-of-5 discrepancy remains** vs the ARCADE-2 measurement | **Yes** — gap not closed by better resolution/depth |
| 2 | *"can not uniquely separate the observed emission into individual components (synchrotron, free-free, or other sources)"* (Kogut 2011) | Planck 2015 X (Commander): full-sky synchrotron+free-free+AME+dust separation, Planck (30–857 GHz)+WMAP(9yr)+Haslam 408 MHz jointly fit | Explicit stated limitation, verbatim: *"the main limitations of the temperature model at the lower frequencies are degeneracies among the spinning dust, free-free, and synchrotron components; additional observations from external low-frequency experiments will be essential"* | **Yes** — the exact 2011 degeneracy is still named as the model's own weak point in the best 2015-era full-sky product, at exactly ARCADE's low-frequency end |
| 3 | *"do not have sufficient low-frequency coverage to determine the spectral index of the 3 GHz excess"* (Fixsen 2011) | Dowell & Taylor 2018 (LWA1), 40–80 MHz, absolute-calibrated | Independent low-frequency fit: **β = −2.58 ± 0.05**, T(21cm rest frame) = 603+102/−92 mK — *"support for a strong, diffuse radio background... suggested by the ARCADE 2 results"* | **Yes, and strengthened** — independent data at a different frequency range lands on essentially the same power law |
| 4 | *"can not extend to arbitrarily low fluxes, or the total contribution would diverge"* (Kogut 2011) | Same Vernstrom et al. 2023 compendium (row 1) | Ruled out a missing discrete population as the fix: *"We can rule out a significant missing discrete source radio population and suggest the cause... may need to be sought either in the foreground subtraction or as a yet unknown diffuse component"* | **Yes** — 12+ years of deeper counts point the finger back at foreground subtraction, not at undetected sources |
| 5 | *"not practical to measure the beam pattern for the lower frequency horns... once installed"* (Singal 2011) | This pass's own attempt, §2 above, using the only public ARCADE maps that exist | Compact-feature FWHM comes out narrower than the 11.6° design beam at all 12 channels, but pixel count/sampling (207–232 px over 7% sky, 3.66°/px) is too coarse to call this a real beam measurement | **Unresolved either way** — running the check with 2026-available public data hits the same wall Singal named in 2011; the excess's significance does not visibly hinge on this (beam mismatch affects sidelobe leakage, not the fitted monopole spectrum directly per Fixsen/Seiffert) |
| 6 | *"no...sufficient difference in timescale to account for our measurements in known populations of galaxies"* (Kogut 2011) | VLASS variable-source census, 2 epochs ~2.5 yr apart, S-band (2–4 GHz, overlapping ARCADE's 3 GHz) | Real numbers now exist: **~5% of sources >20 mJy vary >30%** between epochs; **~9% of sources >300 mJy** do — ~3,600 confirmed variables plus >10,000 single-epoch candidates, dominated by blazars/quasars | **Largely yes, with new data** — multi-epoch variability is now quantified (it wasn't in 2011) but the measured variable fraction (single-digit %) is far too small on its own to plausibly supply a factor-of-5 monopole gap; not fully closed either way, first real number where there was none |

**Bottom line across all six:** every 2020s check that could be run either (a) leaves the
gap exactly where it was in 2011 (rows 1, 2, 4, 5), or (b) makes it *harder* to dismiss by
reproducing it independently at a different frequency (row 3). Row 6 is the one genuine new
capability (quantified variability) but its numbers are too small to be the fix. Read across
the table: the excess has not been explained away by thirteen more years of exactly the kind
of deeper/wider/multi-epoch public data Kogut's six sentences said would be needed — it has
instead been independently reproduced (LWA1) and had its most promising escape hatch (missing
faint sources) explicitly closed off (Vernstrom 2023) at the one frequency (3 GHz) where the
source counts are best known of all. Stack them: six 2011 walls, six 2020s-era instruments
that can now stand at each wall, and in every case the wall is either still there or the
excess climbed over it anyway.

**Tries:** 7 arXiv API queries run to locate correct IDs (2 initial guessed IDs from memory
were wrong and discarded — one resolved to an unrelated quantum-chemistry paper, one to an
unrelated math paper, both logged as failed tries, not silently dropped); 6 successful
abstract fetches; 1 dataset (Vernstrom 2023) used for two rows (1 and 4) since it answers both
directly; the WebSearch tool was unavailable this session (budget exhausted by other
concurrent work) — every citation here came from the arXiv API + WebFetch on the resulting
abstract pages instead, and is flagged as abstract-level (not full-text) evidence except where
Kogut/Singal full text was fetched directly (§1).

---

## Files

- `parallax/out/firas/rabbits/arcade/hole/arcade_maps/` — all 12 public ARCADE 2 v19 FITS
  sky maps, pulled directly from LAMBDA, 384 KB total.
- `parallax/out/firas/rabbits/arcade/hole/beam_from_maps.py` + `beam_results.json` — beam
  derivation script and full per-channel output (§2).
- `parallax/out/firas/rabbits/arcade/hole/pickles_3ghz.py` + `pickles_3ghz_results.json` —
  3/3.41 GHz residual-structure script and full output (§3).
- `parallax/out/firas/rabbits/arcade/hole/Singal_instrument.txt`,
  `Kogut_galactic.txt` — full extracted text of the two 2011 papers read fresh this pass
  (flight ops and timing details were not in the prior ARCADE_ABSENCE doc).

## Counts (every test/fetch this pass)

- 2 full 2011 papers fetched as PDF and text-extracted (new this pass), grepped for 6 keyword
  classes each.
- 12 FITS sky maps downloaded (384 KB total) and parsed via `astropy`+`healpy` in an isolated
  venv (removed after use; nothing left resident).
- 24 beam-proxy measurements computed (2 per channel × 12 channels).
- 6 correlation tests run for the 3 GHz residual-structure check, each backed by a
  20,000-draw exact permutation null (120,000 total permutation draws).
- 7 arXiv API lookups; 2 wrong-guess arXiv IDs caught and discarded (quantum chemistry paper,
  math paper — logged, not hidden); 6 abstract-level fetches used in the final six-row table.
- 1 data-product labeling inconsistency found and left unresolved (90 GHz FITS `FREQ` header
  mismatch, §2).
- 1 process, single-threaded throughout, venv removed at end of run; 384 KB of FITS data and
  under 600 KB of text/JSON left on disk under `hole/`.
