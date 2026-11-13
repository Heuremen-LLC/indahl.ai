# Black-Hole Merger Stack — Exploratory Pass, 2026-09-30

Field-hand run for Wayfinder. Public GWOSC strain only. No quantum hardware, no spend.
Look-first: every number below is raw output; interpretation is marked separately.

## What was pulled

Reused the existing venv at `~/bones-forge/parallax/out/black/venv` (Python 3.14) and
catalog pull at `~/bones-forge/parallax/out/black/gwtc.json`. Installed `gwpy`, `gwosc`,
`h5py`, `scipy` (all installed cleanly, no version conflicts).

5 loud binary-black-hole events, ±32 s of open strain at 4096 Hz per detector
(262,144 samples/channel — single process, one file at a time, nothing held
concurrently beyond one event's detectors):

| Event | Detectors pulled | Catalog M_final (Msun) | Network SNR |
|---|---|---|---|
| GW150914 | H1, L1 | 61.5 | 26.0 |
| GW170814 | H1, L1, V1 | 53.2 | 17.7 |
| GW190521 | H1, L1, V1 | 147.4 | 14.3 |
| GW190814 | H1, L1, V1 | 25.7 | 25.3 |
| GW200129_065458 | H1, L1, V1 | 60.2 | 26.8 |

14 event-detector strain files total, all fetched successfully on first or
second attempt (GWOSC never refused).

Scripts: `~/bones-forge/parallax/out/black/scripts/fetch_data.py`,
`analyze.py`, `analyze2.py`. Raw strain: `out/black/data/*.hdf5`. Results:
`out/black/results/*.json`.

## Method, stated plainly (so the numbers below are checkable)

1. Whitened each detector's strain against its own off-merger PSD (median
   over the file, 2–8 s FFT segments depending on the cutoff variant), then
   bandpassed.
2. We do **not** have the exact NR-calibrated template LIGO/Virgo fit. As a
   stand-in for "subtract the published waveform, keep the residual," we fit
   (linear least-squares, no nonlinear optimizer, so it's fully
   reproducible) a single damped-sinusoid ringdown at each event's
   catalog-reported final mass, using the standard Berti-Cardoso-Will
   fundamental l=m=2 QNM fit at a fixed fiducial spin of 0.7 (we don't have
   reliable per-event spin in this catalog pull — this is a real
   simplification, flagged, not hidden).
3. On the **residual** after that subtraction: ran an autocorrelation scan
   for a repeating delay from 1 ms–300 ms starting 30 ms after merger.
4. Background: for every on-source statistic, drew up to 20 off-source
   trials from elsewhere in the same 64 s file (excluded ±1 s around the
   real merger), recomputed the same statistic, and z-scored the on-source
   peak against that background's mean/std. This is the try-count basis.
5. Casimir-cutoff sweep: repeated steps 1–4 under 4 different
   whitening/bandpass choices (30–300 Hz/4 s, 20–500 Hz/4 s, 20–1000 Hz/8 s,
   50–250 Hz/2 s) per event-detector.
6. Cross-detector ("three witnesses"): whitened+bandpassed residual
   cross-correlated between every detector pair per event, ±50 ms window
   around merger, again z-scored against 15 off-source time-slide trials.
7. Data-quality / "third state" scan: checked every raw strain file for
   NaN, Inf, and flatlined (zero-derivative) runs.
8. Mass-scaling check: on-source echo delay (wide 20–1000 Hz cutoff) divided
   by each event's horizon light-crossing time 2GM_final/c^3.

**Total tries counted:** 14 event-detectors × 4 cutoffs = 56 echo-autocorrelation
trials, plus 13 detector-pairs × background sweep = 13 cross-detector trials.
69 statistical tests total, each with its own background (not one shared
background reused across tests).

## Raw numbers

**Echo autocorrelation, top 5 |z| out of 56 trials:**

| Event | Det | Cutoff | z |
|---|---|---|---|
| GW190521 | L1 | 30–300 Hz | +4.18 |
| GW190521 | L1 | 50–250 Hz | +3.48 |
| GW190521 | L1 | 20–500 Hz | −2.42 |
| GW190521 | H1 | 20–500 Hz | −1.83 |
| GW200129 | L1 | 20–500 Hz | −1.78 |

All other 51 trials: |z| < 1.6.

**Cross-detector correlation, all 13 pairs:**
Three pairs exceeded |z| = 2.9: GW200129 H1-L1 (+3.96), GW190521 H1-L1
(+3.12), GW170814 H1-L1 (−2.99). All other 10 pairs: |z| < 1.0.

**Data quality / third state:** zero NaN, zero Inf, zero flatlined samples
in all 14 raw strain files, ±32 s around every event. No gaps, no
third-state pipeline flags visible in these windows.

**Mass scaling** (delay ÷ horizon light-crossing time, wide cutoff):
ratios across the 14 event-detectors ranged from 1.3 to 67.3 — no visible
clustering around a common value.

## What survived, what didn't

- **The GW190521-L1 "signal" did not survive its own Casimir-cutoff test.**
  Same detector, same event, same residual, four bandpass/whitening
  choices: z swings from +4.18 to +3.48 to −2.42 to +0.05 across the four
  cutoffs, including a sign flip. By the standing rule (whatever moves with
  the ruler belongs to the ruler), this one is instrument, not object — it
  is exactly the shape the cutoff test was built to catch, and it caught it.
- **The three cross-detector pairs above z=2.9 did not corroborate within
  their own events.** GW200129 H1-L1 was +3.96 but H1-V1 and L1-V1 for the
  same event were 0.00 and −0.80. GW190521 H1-L1 was +3.12 but H1-V1 and
  L1-V1 were −0.27 and +0.78. Three witnesses were asked and only one
  answered each time — fails the standing three-detector consistency check.
  (Plausible textbook reading: our simple analytic ringdown template didn't
  fully remove the true merger signal, so some real-signal leakage between
  the two most-sensitive detectors at the true light-travel delay is
  expected — noted, not treated as the final word.)
- **No mass-scaled echo delay.** The delay-over-horizon-time ratio scattered
  over more than an order of magnitude (1.3–67) with no clustering — nothing
  like the qubit "~75 µs drain" showed up as a fixed, mass-independent, or
  mass-scaled recurring feature here.
- **No data-quality/third-state signal.** Every one of the 14 raw files was
  clean in its ±32 s window — no vetoes, gaps, or flatlines to line up
  across events or detectors, so idea #5 (failures lining up) has nothing to
  report this pass — would need actual GWOSC DQ-segment queries beyond the
  strain files themselves, not done yet.
- **The near-zero-lag (~1–2 ms) autocorrelation "floor"** seen in nearly
  every narrow-band trial (value ~0.5–0.6) is a textbook filter-correlation
  artifact — it changes magnitude and sign under wider bandpass, confirming
  it's the ruler's own smoothing length, not a real feature. Flagged and
  excluded from the "what survived" list above.

## Honest gaps for next pass

- Single-mode fiducial-spin ringdown template is a rough stand-in for the
  real fitted waveform; a residual against pycbc/LALSuite's actual
  best-fit template would be a stronger subtraction.
- DQ scan only checked our own ±32 s pulls for NaN/Inf/flatline — did not
  query GWOSC's DQSEGDB veto-segment API, which is where idea #5 (failures
  lining up) would actually live.
- Only 5 events; GW190814 and GW200129 are informative extremes (very
  asymmetric mass ratio, very high SNR precessing case) but a larger set
  (10–15 events) would tighten the mass-scaling null result.
