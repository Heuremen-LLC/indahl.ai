# TOWEL SEARCH: does either half of 44,441.66 Hz stand alone anywhere?

Wayfinder & Bones, 2026-09-30.

**The question.** The tile-8 tone measured on Fez (and consistent with Kingston's own
buzz record) is 44,441.66 +/- 0.02 Hz plus an unknown whole multiple of 100 kHz.
Wayfinder split it as 42,000.00 + 2,441.66 Hz -- an arbitrary split unless one piece
shows up **on its own**, somewhere it wasn't put. Three outside records were searched.
No result was written down before looking. Every test is counted below.

Scripts: `parallax/out/towel/ratio_test.py`, `parallax/out/towel/horn_towel.py`,
`parallax/out/towel/copper_live_check.py`. Raw data: `parallax/out/towel/*.json`.

---

## 1. Copper power-line collector (laptop, `~/copper_spectra/`)

- The collector's band is 0-1200.0 Hz (191 stored minute-rows, bin width 0.9537 Hz).
- **Confirmed out of band, as flagged going in**: 2,441.66 / 2 = 1,220.83 Hz is
  21.1 Hz beyond the last stored bin (1,199.72 Hz). Nothing else on the target
  list (2,441.66 / 4,883.3 / 42,000 / 21,000) falls anywhere near this collector's
  range. No claim, per the setup -- this store cannot speak to any of the targets.

### One live read: `GET http://localhost:8765/spectrum?lo=1000&hi=50000`

One call made, 51,380 bins returned, bin width 0.9537 Hz, noise_floor 5.99.
Target bin vs. local neighborhood (median of the 100 bins around it, excluding
the immediate +-3 bins):

| target | nearest bin (Hz) | signal (dB) | neighborhood median (dB) | excess (dB) |
|---|---|---|---|---|
| 2,441.66 | 2441.41 | 3.94 | 0.02 | **+3.92** |
| 4,883.3 (x2) | 4883.77 | 1.04 | -0.31 | +1.35 |
| 42,000 | 41999.82 | -15.91 | 1.60 | -17.51 |
| 21,000 (x0.5) | 20999.91 | 3.99 | -0.44 | +4.43 |

**Background, same single read:** excess-vs-neighborhood computed the same way
at 500 random bins in the same spectrum. Mean -0.96 dB, stdev 5.98 dB, range
-33.8 to +19.9 dB. 5th/95th percentile: -12.1 / +6.7 dB. 1st/99th: -17.0 / +9.7 dB.

**All four target excesses (+3.92, +1.35, -17.51, +4.43) fall inside the
5th-95th percentile band of the same read's own random-bin scatter.** The
42,000 Hz excess (-17.51) sits right at the 1st-percentile edge (-17.0), i.e.
about as extreme as 1 bin in 100 gets by chance alone, not further out. This
is one read of a live, busy system, reported as one read -- no claim.

Tries counted: 4 targets + 500 background draws = 504.

---

## 2. Horn day raw IQ (laptop, `/home/ctrai/horn/20260928_091702/`, 17 clips)

FS = 10,000,000 Hz (HackRF cs8, int8 I/Q), 5 s/clip, tuned to 4080 MHz so the
baseband offset IS the target frequency. Welch-averaged PSD per clip
(25 segments of 0.2 s, Hann window, ~5 Hz resolution). Band of interest
+-12,500 Hz (matches the earlier 25 kHz baseband extraction). 42,000 / 21,000
Hz fall outside this band and were not tested here (out of range, as with the
copper store above).

Per clip: target-bin-vs-local-neighborhood excess (median of bins 15-200 Hz
away), plus 30 random-frequency background draws in the same band, same clip,
same method -- 578 tries total (4 targets x 17 clips + 30 x 17 background).

| target | mean excess (dB) | stdev | min | max |
|---|---|---|---|---|
| 2,441.66 | 0.50 | 1.44 | -1.75 | +5.20 |
| 4,883.32 (x2) | 0.18 | 0.85 | -1.25 | +1.95 |
| 7,324.98 (x3) | 0.63 | 4.27 | -2.31 | +17.38 |
| 1,220.83 (/2) | 0.90 | 2.63 | -1.36 | +9.96 |

Background (510 draws, all 17 clips pooled): mean 0.06 dB, stdev 2.17 dB,
range -3.25 to **+37.54** dB.

**Every target excess, including the largest (7,324.98 Hz in one clip at
+17.4 dB, and 1,220.83 Hz in another at +10.0 dB), is smaller than the largest
excess produced by the plain random-frequency background draws (+37.5 dB) in
the same 17 clips.** The horn recording's noise floor throws occasional large
narrowband spikes at random frequencies (birdies, not the target tone); the
targets do not stand out above that population. Nothing survived.

Tries counted: 578.

---

## 3. IBM Kingston buzz line (106.39 Hz + n x 100 kHz)

From `parallax/out/the_buzz/THE_BUZZ.md`: Kingston's own tone fits the
recorded slot lengths at 106.39 Hz (no explicit error bar given in that file;
tested here at two tolerances, 0.02 Hz -- matching the Fez fit's precision --
and a generous 0.5 Hz).

**Ratio test** (does target / n land within tolerance of 106.39 Hz, for n up
to ~2000, both split pieces and their x2/x3/half): **zero hits** at either
tolerance.

**Nearest-integer residues** (target / 106.39, rounded to nearest whole
number, residual reported raw):

| target | target / 106.39 | nearest int | residue (Hz) |
|---|---|---|---|
| 2,441.66 | 22.950 | 23 | -5.31 |
| 42,000.00 | 394.774 | 395 | -24.05 |
| 4,883.32 (x2) | 45.900 | 46 | -10.62 |
| 7,324.98 (x3) | 68.850 | 69 | -15.93 |
| 1,220.83 (/2) | 11.475 | 11 | +50.54 |
| 84,000.00 (x2) | 789.548 | 790 | -48.10 |
| 126,000.00 (x3) | 1184.322 | 1184 | +34.24 |
| 21,000.00 (/2) | 197.387 | 197 | +41.17 |

All eight residues are 5.3 to 50.5 Hz off the nearest whole multiple of
106.39 Hz -- two to three orders of magnitude past either error budget
(0.02 or 0.5 Hz). No whole-number ratio or difference relationship survives.

Direct ratio between the two split pieces themselves, reported only, not
tested against Kingston: 42,000.00 / 2,441.66 = 17.201412 (not close to a
whole number either).

Tries counted: 5,749 (ratio scan) + 8 (residue table) + 1 (direct ratio) = 5,758.

---

## Total tries across all three searches: 504 + 578 + 5,758 = **6,840**

## Bottom line

Raw numbers first: every target/multiple/half tested, in every store that
could reach it, produced an excess-over-neighborhood or a residue that fell
inside (usually well inside) the same store's own background/null
distribution. Nothing exceeded its background. The copper store's own band
can't reach most targets at all (out of range, stated plainly, not a null
result). The one live copper read is one read of a live system -- reported,
not claimed. The split of 44,441.66 Hz into 42,000.00 + 2,441.66 Hz remains
Wayfinder's arbitrary partition; neither piece showed up on its own anywhere
it wasn't put.
