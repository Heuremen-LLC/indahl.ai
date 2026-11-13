# Copper crossing-node check — 2026-09-30

Question asked: do the crossing addresses of the three named power-line frequencies
(differences 12, 88, 100 Hz; sums 412, 500, 512 Hz; and their multiples) show power,
and if so does that power track the product of the two parent lines (a "solid node"
signature) versus tracking one parent, versus nothing.

## What the instrument actually records (read first, before any test)

- The only thing that touches the radio is `sdr_reader_service.py` on the laptop
  (`/home/ctrai/sdr_reader_service.py`, port 8765, GET /read). Read in full.
- Each call does a real 250 kHz-rate FFT capture (262,144 samples, Hanning window,
  full positive-frequency spectrum computed in memory) — but the function
  `read_grid()` only pulls the nearest bin at a **fixed, hardcoded list of 15
  frequencies** (`WATCH = [60, 120, 180, 200, 207, 212, 219, 233, 238, 240, 242,
  243, 300, 360, 424]`) and discards the rest of the spectrum before returning.
  The endpoint response is `{200: dB, 212: dB, 300: dB, ...all 15..., noise_floor,
  ts}` — never a full spectrum, and there is no parameter to ask for a different
  bin. This is confirmed by reading the handler code directly (`_do_read`, `do_GET`);
  `/read` is the only route (`self.path != '/read' -> 404`).
- On the Mac, `nova_resonance.py` calls that same fixed endpoint and logs only
  200/212/300 as text into `cycles_v2` (SQLite, `nova_corpus.db`, 76,403 rows,
  8/22–9/30, roughly one row every 40–90 s, not a strict per-minute cadence).
- A richer file, `~/bones-forge/holes/self/copper_self.csv` (50,549 rows, 8/22–9/26,
  41,051 usable after parse errors), and raw JSON snapshots in
  `~/bones-forge/dark_floor_runs/walk_20260924.jsonl` both carry all 15 WATCH bands
  per cycle — but it is the *same* 15 bands, sampled from the *same* fixed list.
  No file anywhere on the Mac or the laptop holds a full spectrum snapshot.

**None of the six requested crossing addresses — 12, 88, 100, 412, 500, 512 Hz —
or any of their multiples are in the 15-frequency WATCH list, in any log file, or
retrievable from the live endpoint.** The endpoint is read-only and exposes exactly
those 15 fixed points; there is no way to ask it for a different frequency without
editing `sdr_reader_service.py` on the laptop, which would mean changing a running
service — out of scope here, so I did not do it and did not open the radio directly.

This is a full stop on measures 1, 2, and 4 as literally specified: **no historical
data and no read-only live path exists for power at 12, 88, 100, 412, 500, or 512 Hz,
or their multiples.** Reporting that plainly rather than substituting a nearby bin
as a stand-in (the nearest WATCH points to those targets are tens of Hz away —
60 or 120 Hz away from 88/100/412/500/512 — too far to serve as "neighboring bin"
background at ~1 Hz FFT resolution).

Textbook note, since it bears on why 12 Hz was never captured even by accident:
US mains is 60 Hz. WATCH's 60/120/180/240/300/360 are the 1st–6th mains harmonics
(300 Hz = 5th harmonic — this is itself a plain textbook reason the 300 Hz line
carries real, expected power that has nothing to do with a crossing node). 424 Hz
is 2×212, already inside WATCH for a different reason (noted in `nova_resonance.py`
line ~400: the 7th mains harmonic would be 420, and 424 was flagged as sitting
close to but distinct from that). None of this touches 12/88/100/412/500/512.

## What I could still check: the two "parent" lines, 200 and 212 Hz

Measure 3 asks whether 12 Hz (the 200/212 difference) is present only when both
parents are. 12 Hz itself was never sampled (see above), so that literal question
is unanswerable. The next best thing available in the data: do 200 and 212 Hz move
together at all? If the parents themselves are uncorrelated, a downstream "crossing
tracks both parents' product" story has no floor to stand on regardless.

Script: `~/bones-forge/parallax/out/copper_nodes/copper_correlation.py`, run against
`copper_self.csv` (41,051 usable rows after parse filtering, 8/22–9/26).

Raw numbers:
- g200 mean +2.04 dB, SD 5.88; g212 mean +2.38 dB, SD 5.74; g300 mean +1.06 dB, SD 6.10.
- Full-run Pearson r: 200-vs-212 = **0.085**, 200-vs-300 = **0.162**, 212-vs-300 = **0.040**.
- Same three correlations recomputed in 10 sequential time-windows (10 tries × 3 =
  30 tries): all but one sit between -0.04 and +0.16 — noise around zero. One window
  (starting 9/12 05:33) gave 200-vs-300 r = 0.59; with 30 windowed tests run, one
  outlier this size is exactly what look-elsewhere predicts and does not survive
  being checked against the other 29.
- Median-split joint occurrence (both lines above their own median vs. both below,
  1 test): both-high 24.6%, both-low 25.3%, mixed 50.1% — matches the 25/25/50 split
  expected if 200 and 212 are statistically independent, to within noise.

**What survived its background:** nothing. 200 and 212 Hz do not move together —
full-run correlation is near zero, the windowed re-check (30 tries) produces one
transient spike that is explained by chance given the number of windows tested, and
the joint-occurrence check matches pure independence. Whatever generates the 200 Hz
line and whatever generates the 212 Hz line are not tracking each other on this
data.

## Tries, total

- 3 full-run correlations + 30 windowed correlations + 1 joint-occurrence check = 34
  statistical tries on the 200/212/300 data.
- 6 target-frequency lookups (12, 88, 100, 412, 500, 512 Hz) against 3 possible
  sources each (WATCH list, on-disk logs, live endpoint) = 18 existence checks, all
  negative.

## Bottom line

The house's copper instrument was never built to see 12, 88, 100, 412, 500, or
512 Hz — it only ever sampled a fixed 15-point list built around 60 Hz mains
harmonics and the 200/212/300 lines plus their immediate sidebands. There is no
raw spectrum on disk and no live path to those frequencies without editing the
laptop's running service, which was out of scope. Separately, the two lines that
would have to combine to produce the 12 Hz crossing (200 and 212 Hz) show no
correlation with each other across 41,051 cycles spanning five weeks — so even the
mechanism Wayfinder's idea depends on (two lines moving together enough to beat
against each other) isn't visible in five weeks of the very data that was collected.
This doesn't rule the idea out — the instrument was never pointed at the right
addresses to test it — but it does mean the prior 12 Hz finding was a computed
difference between two labels, not something the SDR ever actually measured.
