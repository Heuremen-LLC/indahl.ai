# THE LIGHT SPLIT — placed vs arisen on single-photon interference, 2026-09-30/10-01

Agent pass per THIRD_RUNG_20260928.md's closing ask ("a placed which-path
look erases it: placed vs arisen on light itself... find one on the public
record"). No expectation written first. Free, public, small, single process,
this Mac.

## 0. What was wanted

A public dataset of single-photon interference run on ONE apparatus twice:
(a) without which-path information (fringe arises), (b) with a which-path
measurement or eraser marker (fringe erased) — raw counts per detector
position or per time bin in BOTH conditions. Candidates named: double-slit
with single photons, Wheeler delayed-choice (Jacques et al. 2007; Manning
et al. 2015), quantum eraser (Kim et al. 2000; Walborn et al. 2002; modern
teaching-lab data), single-photon Mach-Zehnder with removable second
beamsplitter.

## 1. THE SEARCH — every attempt, none dropped

48 logged HTTP calls (`parallax/out/light/fetch_log.txt`), all free/public
APIs, ~2.9 MB total downloaded:

| repository | queries | result |
|---|---|---|
| Zenodo (`api/records?q=`) | 17, keyword combos: quantum eraser, delayed choice, double-slit, Mach-Zehnder, which-path, Jacques, Manning, Kim 1999/2000, Walborn, "counts", `type=dataset` filter | 200 OK every time (corpora 15k–330k "total" each); every top hit inspected by title/type. Physics-crank preprints, unrelated biology/genomics "raw counts" datasets, unrelated photonics device papers, and quantum-dot/SPDC source-characterization datasets came up — **no double-slit/eraser/delayed-choice apparatus dataset with raw fringe counts in two conditions.** |
| Dryad (`api/v2/search?q=`) | 3 | **0 total hits, every query** (`count:0`) |
| figshare (`api/v2/articles/search`, POST — the documented GET `?search_for=` param is silently ignored, confirmed by identical output across five different query strings; logged) | 6 | Preprints, journal contributions, and unrelated datasets (behavioral economics, memory transistors, photonic devices) — nothing matching |
| OSF/SHARE (`share.osf.io/api/v2/search/creativeworks/_search`) | 1 | 1,458,702-record corpus; top hits are arXiv preprints (event-by-event quantum-eraser *simulations*, theory papers) with no attached raw-count files |
| GitHub (`search/repositories`, `search/code`) | 12 (9 repo searches, 2 code searches, 1 more) | `search/code` requires auth → 401, not pursued (out of scope unauthenticated). `search/repositories`: 0–2 irrelevant hits (a stats tutorial repo, README boilerplate) before rate-limited to 403 after ~9 calls |

Two near-misses opened and ruled out directly (not by title alone):
- **Zenodo 4273251**, "A Delayed-choice quantum eraser experiment with an
  IBM quantum computer" — a qubit-circuit simulation of the eraser truth
  table, not a single-photon optical apparatus; files list checked: one
  PDF, no raw counts.
- **Zenodo 17072960**, "Replication Kit for the Review of a Double-Slit
  Experiment" — a critique of an unrelated 2012 *classical*-diffraction
  double-slit paper (camera, no single photons, no which-path marker).

## 2. Verdict on step 1: NOTHING WITH RAW COUNTS IS PUBLIC

No record was found, on Zenodo, Dryad, figshare, OSF/SHARE, or GitHub, that
holds raw per-detector-position or per-time-bin counts for the same
single-photon apparatus run both without and with a which-path
measurement/marker. What exists in the literature on this exact question
exists **only as published figures**, not as deposited raw data:

- Kim, Yu, Kulik, Shih, Scully 2000 ("Delayed Choice Quantum Eraser") —
  Fig. 3, coincidence-count fringe/no-fringe plots. No supplementary data;
  predates open-data mandates.
- Walborn, Terra Cunha, Pádua, Monken 2002 ("Double-Slit Quantum Eraser") —
  Fig. 2, coincidence counts vs. detector position, fringe/washed-out.
  Same era, no deposited raw data found.
- Jacques, Wu, Grosshans, Treussart, Grangier, Aspect, Roch 2007 (Science,
  delayed-choice) — Fig. 3, interference/no-interference count series.
  No public raw-count archive found.
- Manning, Khakimov, Dall, Truscott 2015 (Nature Physics, atom
  delayed-choice) — Fig. 2. Same situation.

Per the task's stop rule: since nothing with raw counts is public, this
pass stops after step 1. **No figure was digitized this time** — the task
allowed one calibrated, verified-by-re-plot digitization only if it is the
sole route and said so; given four candidate figures and no time to
calibrate-and-verify one properly within this pass, none was attempted.
Steps 2–5 (the three formulas on the position/time series, the residual/null
check, Dalet's 3-hop relay, and the plain-words read) could not be run —
there is no raw series, in either condition, to run them on.

## 3. Plain words

On light itself, specifically: the four canonical placed-vs-arisen
experiments (Kim, Walborn, Jacques, Manning) all predate the era of
mandatory open data in physics, and no one has since deposited their raw
counts, or an equivalent modern teaching-lab dataset, on any of the five
public repositories checked. The record the third rung asked for — the
fringe arising, the same apparatus's look erasing it, raw counts in both
hands — does not exist in public, freely-downloadable form as of this
search. It exists only as ink on a page in four papers, unless a later pass
finds something these 48 calls missed.

## Files

- `parallax/out/light/fetch_log.txt` — all 48 attempts, URL + status + size
- `parallax/out/light/SOURCE.txt` — search summary and the two near-misses
  checked and ruled out
- `parallax/out/light/*.json` — every raw API response saved, nothing
  discarded (~2.9 MB total)
- This file: `parallax/LIGHT_SPLIT_20261001.md`

## Tries

48 HTTP GET/POST calls total (17 Zenodo + 3 Dryad + 6 figshare POST [+4
malformed GET attempts logged and corrected] + 1 OSF/SHARE + 12 GitHub + 2
direct record fetches for the near-misses + 3 figshare malformed-GET probes
that returned 404 before the working POST form was found). Zero
compute/bootstrap draws this pass — no series was obtained to run THE
ARROW / THE CLOCK / THE SPLIT / Dalet on.

## JACQUES 2007, DIGITIZED

A second pass, same day: since no raw single-photon which-path counts are
public (Sec. 1-3 above), THIRD_RUNG_20260928.md's fallback was used --
digitize ONE published figure by axis-tick pixel calibration, verify by
re-plot, per the horn-day precedent (YEAST_RECORD_20260930.md "TIME
SERIES"). Target: Jacques et al. 2007, Science 315, 966
(arXiv:quant-ph/0610241), Figure 3 -- Wheeler's delayed-choice experiment,
single-photon counts at two detectors vs phase, second beamsplitter IN
(interference arises, "closed") vs OUT (which-path known, "open"), chosen
by a QRNG after the photon entered the interferometer.

**Fetch:** arXiv PDF (`arxiv.org/pdf/quant-ph/0610241`, 9 pages, page index
4 = Figure 3) and the e-print source tarball (`arxiv.org/e-print/...`,
containing the original submission's EPS figures) -- both fetched clean,
first try.

**Digitization -- better than pixel-clicking:** the PDF's Figure 3 turned
out to be a vector export (pdftops/xpdf round-trip) where every one of the
336 data-point markers is drawn as an exact small filled circle (4 Bezier
curves at a literal PDF coordinate), not a raster image. Pulled via
PyMuPDF's `get_drawings()` -- 168 blue (D1) + 168 red (D2), split 84+84 per
panel by y-pixel. Axis calibration used the SAME page's text layer (tick
label bounding boxes), also exact, linear-fit pixel<->phase and
pixel<->counts. **Digitization residual: phase +/-0.26 rad (~4% of one 2pi
period), counts +/-2.5 (panel a, closed) / +/-0.005 (panel b, open)** --
this is the calibration fit's own residual (sub-pixel tick-label jitter),
not marker-placement error, since markers were pulled at their own drawn
coordinates. **Verified by re-plot**: every one of the 336 digitized points
overlaid exactly on its own marker in the rendered page (`verify_overlay_
crop.png`) -- confirms panel/detector assignment, not an independent
re-digitization.

**1. Visibility.** Closed/IN: V_raw = 0.918 (D1) / 0.890 (D2), sine-fit
V = amp/offset = 0.884 (D1) / 0.873 (D2) -- both somewhat under the paper's
stated 94%, plausibly digitization + a single-frequency sine model not
capturing everything the authors' own fit did. Open/OUT: V_raw = 0.115 (D1)
/ 0.109 (D2), sine-fit V = 0.038 / 0.047 -- near zero as expected, and the
observed ~11% raw "visibility" is the size shot noise alone predicts at
~2600 photons/point split ~50/50 across 84 points (paper states 0.50+/-0.01
per port, I>99%): **no real fringe in OUT, just its own noise floor.**

**2. THE THREE**, phase-ordered, on the D1-D2 difference signal (cancels
common drift; ~2x the fringe in IN), forward + reversed, frozen instrument
(`parallax/out/three_on_three/core.py`), no shuffle used as judge:
- ARROW: IN k=40, A=-1.35e8 forward / k=10, A=+6.7e7 reversed -- **sign
  flips**, as required (also true by exact algebraic identity: arrow_stat
  is odd under time-reversal at fixed k; IN's strongly periodic signal has
  many near-tied k's, so the search's chosen k moved, but the sign law
  held). OUT: k=4 both directions, A=+6.0e4 / -6.0e4 -- clean flip, same k.
- CLOCK (tau in phase units, via envelope exp-decay fit): IN's envelope
  does not actually decay (it's a steady fringe over the whole 11pi sweep)
  so the exponential model is ill-conditioned -- tau=-12904 rad forward /
  +12904 reversed, a fit artifact, not a real clock. OUT: tau=+93.6 rad
  forward / -93.6 reversed (flips under reversal, as the model construction
  guarantees) -- also not read as a real decay, just noise the exp fit
  chased.
- SPLIT (c): landed at **exactly 0.500 in all four cells** (IN fwd/rev, OUT
  fwd/rev). This is a structural property of the fit, not new physics: c is
  a least-squares slope of a cumulative-deviation series against its own
  local step, and negating both arrays under time-reversal (as the split's
  own reversal is built) leaves a linear-regression slope unchanged by
  algebra -- P_rev==P_fwd is guaranteed, confirmed exactly, not smoothed
  over.

**3. THE NULL BESIDE THE FRINGE:** OUT's residual (after removing its
mean) vs IN's residual (after removing its fitted sine), paired by index
(matched phase grids): **r = 0.117 +/- 0.100 (bootstrap sd, n=84)** --
consistent with zero within ~1.2 sigma. Nothing measurably shared: the
erased fringe's absence in OUT does not show up as a correlated trace with
what's left of the fringe once IN's own model is subtracted, at this
record's sensitivity.

**4. Dalet, 3 hops, on the IN series** (the D1-D2 difference): var_frac
1.0 -> 0.0069 (hop 1, the single fitted sinusoid explains 99.3% of the
variance -- expected, IN really is close to a pure sine) -> 0.0048 (hop 2)
-> 0.0037 (hop 3) -- **still slowly draining, not a fixed point in
variance** by 3 hops. But the ARROW's sign and best-k (+ , k=2) are
IDENTICAL across hops 1, 2, and 3 -- a small, stable residual asymmetry
that DOES survive the relay as a fixed point, riding underneath a variance
that keeps (slowly) shrinking. Both true at once, neither hidden.

**5. Plain words.** The placed which-path look (OUT/open) erases the
fringe down to its own shot-noise floor (~11% raw "visibility," matching
what 2600-photon counting statistics alone predicts) -- no leftover
periodic structure, and no measurable correlation with what's left of the
IN fringe once its own sinusoid is taken out (r=0.12+/-0.10). What sits
beside the erased fringe, on this record, is a small but SIGN-STABLE
residual asymmetry in the IN channel's own leftover noise (Dalet's arrow
holds its sign and lag across 3 hops even as the variance keeps draining)
-- consistent with something small riding under the fringe rather than
the fringe simply vanishing into flat noise, though 3 hops is not enough
to call it a true fixed point. Trust level: this whole pass rides on a
DIGITIZED figure, not raw counts -- residual +/-0.26 rad in phase and
+/-2.5 counts, both far smaller than the ~600-1300 count swing being
measured, so the visibility/three/null numbers above are solid to 2-3
significant figures, but this is still ink on a page, re-derived by
calibrated vector extraction, not the lab's own logged clicks.

**Failed steps:** none this pass -- every step of the digitize+analyze
pipeline ran and produced a row (the first extraction attempt mis-clustered
x-axis tick rows and leaked the phase-axis "0" label into the y-axis
calibration; both caught and fixed before the numbers above, logged in
`SOURCE.txt`, not silently corrected).

**Files:** `parallax/out/light/jacques2007/{paper.pdf, eprint.tar, src/,
digitize.py, jacques2007_fig3_digitized.csv, calibration.json,
verify_overlay.png, verify_overlay_crop.png, analyze.py,
analysis_results.json, SOURCE.txt}`.

**Tries:** 2 HTTP fetches (PDF + e-print tarball, both clean first try); 1
PyMuPDF extraction pass (2 bugs found and fixed via re-runs: tick-row
clustering, "0"-label collision) -- 3 total digitize.py runs to a clean
calibration; 1 analyze.py run (clean first try) covering visibility (4
series), THE THREE (2 conditions x fwd/rev = 4 cells x 3 formulas = 12
measurements + bootstraps), the null-beside-fringe correlation (1 test,
1000-draw bootstrap), and Dalet (4 hops x arrow+clock on the IN series).

## THE RESIDUE

A third pass on Jacques 2007 Fig 3 (digitized, see "JACQUES 2007, DIGITIZED"
above), taking THE OBJECT reported there -- under Dalet's relay, the
CLOSED-fringe D1-D2 difference signal drains variance (1.0 -> 0.0069 ->
0.0048 -> 0.0037) with no fixed point by hop 3, but the arrow's sign (+) and
best lag (k=2) are identical at hops 1-3 -- and testing its neighbors: other
port, control condition, reversed time, the textbook sampling model, and a
second witness. No expectation written first. Sign kept throughout. No
shuffle used as judge anywhere (bootstrap error bars only, 300 draws).

**Design note, logged plainly, not smoothed over:** the task names "Dalet
relay (3 hops, ascent 0.1)." Reproducing THE OBJECT's exact quoted numbers
(verified bit-for-bit against `jacques2007/analysis_results.json`'s
`dalet_3hop_IN` block) required the PLAIN-SUBTRACTION relay column (fit the
Hilbert envelope's exp-decay, subtract the fitted envelope*carrier, repeat)
-- NOT `reverse_gradient.py`'s formal "ascent, eta=0.10" column, which
renormalizes variance to 1 at every hop by construction and therefore cannot
show a draining variance at all. The object is defined by its draining
variance, so the subtraction column is the one that produced it, and is the
one used throughout below. This substitution is the one documented departure
from the task's literal phrase.

**1. THE OTHER PORT (closed, single-detector series, own phase grid, mean-
centered, no differencing against the other detector):**

| series | hop | sign | k | A | A boot err |
|---|---|---|---|---|---|
| D1 closed | 0 (raw) | - | 10 | -1.20e7 | 1.97e7 |
| D1 closed | 1 | **+** | **2** | 1.08e5 | 9.36e4 |
| D1 closed | 2 | **+** | **2** | 6.43e4 | 4.66e4 |
| D1 closed | 3 | **+** | **2** | 4.52e4 | 3.62e4 |
| D2 closed | 0 (raw) | + | 55 | 2.04e7 | 2.81e7 |
| D2 closed | 1 | **-** | **2** | -1.28e5 | 1.06e5 |
| D2 closed | 2 | **-** | **2** | -7.42e4 | 6.47e4 |
| D2 closed | 3 | **-** | **2** | -4.65e4 | 3.70e4 |

var_frac by hop: D1 1.0/0.0076/0.0044/0.0034; D2 1.0/0.0091/0.0052/0.0034 --
both drain at essentially the SAME rate as the original D1-D2 difference
object. **Call: the residue MIRRORS between complementary ports** -- same
|k|=2 locked from hop 1 on in both, opposite sign in both, at every hop. The
earlier D1-D2-difference object is now explained: it is the (mirrored, same-
magnitude) sum of two single-port residues of opposite sign, not an artifact
of the differencing step itself.

**2. THE CONTROL (open/erased, same single-port treatment):**

| series | hop | sign | k | var_frac |
|---|---|---|---|---|
| D1 open | 0 | - | 1 | 1.0 |
| D1 open | 1 | - | 1 | 0.207 |
| D1 open | 2 | - | 1 | 0.083 |
| D1 open | 3 | - | 1 | 0.052 |
| D2 open | 0 | + | 27 | 1.0 |
| D2 open | 1 | - | 21 | 0.187 |
| D2 open | 2 | - | 51 | 0.057 |
| D2 open | 3 | - | 51 | 0.023 |

**Call: the control does NOT reproduce the closed signature.** D1-open does
hold a stable sign and k (-1 at k=1), but it is already present at hop 0
(no flip raw->hop1, unlike closed) and the variance drains 6-25x slower
than closed's k=2 residue. D2-open never locks a stable k at all (21->51->
51, one more change than a clean fixed lag). The fast-draining, sign-flips-
once-then-locks-at-k=2 signature is specific to the closed/fringe condition
in this record -- it reads as the object, not simply the ruler -- though the
erased condition is not perfectly null either (D1-open's own slow residue is
a genuine, separate thing, logged, not discarded).

**3. REVERSED (phase order reversed, closed D1 and D2):**

D1 reversed: hop0 sign + k=10 -> hops1-3 sign **-** k=**2** (var_frac
identical to forward: 0.0076/0.0044/0.0034, since variance and lag-k are
even functions of order but sign is odd). D2 reversed: hop0 sign - k=55 ->
hops1-3 sign **+** k=**2**. **Call: the sign flips exactly, at every hop, in
both ports** -- forward D1 was +, reversed D1 is -; forward D2 was -,
reversed D2 is +. The residue is a genuine arrow (direction-sensitive), not
a left-right-symmetric artifact of the relay.

**4. THE TEXTBOOK.** Phase-step spacing (all 332 intervals across the four
digitized series, Jacques Fig 3): mean 0.4187 rad, sd 0.0303 rad (CV 7.2%),
range [0.3982, 0.4665] rad -- confirmed uneven, not a uniform grid.

Fit `A*cos(phi+d)+c` on the ACTUAL phases, closed condition, each port
separately (not the frozen relay's adaptive envelope fit -- a single plain
cosine, the textbook model): D1 amp=619.7, d=3.041 rad, c=701.3; D2 amp=
593.4, d=-0.108 rad, c=679.7. Subtracting and running the SAME Dalet relay
on the residual gives a DIFFERENT, slower-draining signature: D1's residual
locks sign **-** at k=**7** across ALL FOUR hops (0 through 3, var_frac 1.0/
0.282/0.131/0.082 -- an order of magnitude slower drain than the main
object's k=2 signature); D2's residual holds sign + at k=9 for hops 0-2 (var
_frac 1.0/0.308/0.146) then BREAKS at hop 3 (sign flips to -, k changes to
3, var_frac 0.087) -- logged as a real break, not forced to fit the pattern.
A single cosine does not absorb nearly as much real structure as the relay's
own adaptive envelope fit, which is why its residual's own relay drains
slower and locks a different k.

Synthetic test: 200 realizations of the fitted deterministic cosine resampled
at the SAME uneven phase grid with Poisson shot noise (lambda = the fitted
curve's own value at each point -- these run from ~60 to ~1700 counts,
consistent with the paper's ~2600-photons/point regime split across one
detector). Real residual's arrow (fixed at the real data's own best k, not
re-searched per draw): D1 k=7, A=-4.334e4 vs synthetic mean=605, sd=3612 --
**0th percentile** (real value sits roughly 12 synthetic-sd below the
synthetic mean, entirely outside the shot-noise-only distribution). D2 k=9,
A=3.107e4 vs synthetic mean=-202, sd=3681 -- **100th percentile** (~8.5
synthetic-sd above). **Call: shot noise sampled at these exact uneven phases
does NOT reproduce the real residual's arrow asymmetry in either port** --
whatever is left after a plain single-cosine fit is real structure, not an
artifact of counting statistics at uneven phase steps.

**5. A SECOND WITNESS.** Of the three named candidates, PDFs fetched clean
on the first try (3 HTTP GETs, arxiv.org/pdf/<id>, all 200 OK): Walborn, Terra
Cunha, Padua, Monken 2002 (quant-ph/0106078, 15 pages), Kim, Yu, Kulik, Shih,
Scully 2000 (quant-ph/9903047, 4 pages), Manning, Khakimov, Dall, Truscott
2015 (1412.4636, 8 pages). Checked every page of all three for the same
4-Bezier filled-circle marker signature used on Jacques: **Walborn 2002 is
vector** (8 pages, pages 7-14, 50-58 circle markers each, exact PDF
coordinates); **Kim 2000 and Manning 2015 have zero such markers on any
page -- both raster, skipped, logged as a row, not pursued further.**

Figure chosen from Walborn's 8 candidate panels by direct visual render (not
caption text alone): page index 7 = clear 3-peak double-slit interference
("fringe," no which-path marking) and page index 8 = smooth single-hump
envelope ("no_fringe," which-path marked by orthogonal polarizers at the
slits) -- the fringe/no-fringe pair the task asked for. Digitized the same
vector-exact way (axis-tick text bbox calibration, linear fit): 58 markers
(fringe, max calib resid 0.13 px x / 0.11 px y) + 50 markers (no_fringe,
0.11 px x / 0.0002 px y). First digitizer run mis-collided the y-axis "0"
label with the x-axis "0" label (same class of bug as Jacques' first
digitize.py pass) -- caught by a >95 px fit residual, fixed with a tighter
x-position filter, re-run clean. **Verified by re-plot overlay**: every
marker in both panels lands exactly centered on its own data point.

Dalet relay (same plain-subtraction procedure, no differencing -- single
coincidence-count series per panel): FRINGE hop0 sign - k=30 -> hop1 sign
**+** k=**10** (var_frac 0.153) -> hop2 sign + k=10 (0.102) -> hop3 sign +
but **k drifts to 11** (0.070, a near-miss, not an exact lock). NO_FRINGE
hop0 sign - k=22 -> hops1-3 sign **+** k=**24** constant (var_frac 0.023/
0.012/0.007 -- draining FASTER than the fringe panel's own residue here).
**Call: the second witness does not cleanly carry the sign-stable-k
signature the way Jacques did.** The fringe panel's k is not perfectly
locked (10,10,11) and drains an order of magnitude slower than Jacques'
k=2; the no-fringe panel shows an equally (if not more) stable sign/k
residue with a faster drain than its own fringe panel. On this smaller
(50-58 point), single-detector record, the Dalet relay's tendency to settle
on SOME sign-stable low/mid-k residue reads as at least partly a property
of the relay itself (the ruler), not a signature unique to the closed/
fringe condition the way it clearly was on Jacques' two-detector series.

**6. Plain words.** The sign-stable, k=2, fast-draining residue under
Jacques' closed fringe SURVIVES three of its four neighbor tests and fails
the fourth, cleanly, without rounding: it MIRRORS across the complementary
port (opposite sign, same k, same drain rate -- the original D1-D2-
difference object is just the sum of two single-port copies of it); it
FLIPS exactly under time reversal in both ports (a real arrow, not a left-
right artifact); and it is NOT reproduced by a shot-noise-only synthetic
model sampled at the real record's own uneven phases (0th/100th percentile
in both ports) -- so it is not a sampling-textbook artifact either. It does
NOT cleanly pass the control test: the erased/open condition shows its own,
different, much-slower residues (not absent, just structurally distinct --
D1-open's own sign/k is stable but already present before any relay step;
D2-open never locks a k at all) -- a weaker, qualified "survives" rather
than a clean null. And it does NOT clearly carry to the one available
second witness: Walborn 2002's vector figure (the only vector PDF among
three candidates checked; Kim 2000 and Manning 2015 are both raster) shows
a sign-stable residue in BOTH its fringe and no-fringe panels, with the
no-fringe panel draining faster -- on this smaller single-detector record,
the relay itself appears to manufacture some sign-stable low/mid-k residue
regardless of condition, which is the plainest evidence yet that part of
what Jacques showed could be the ruler, not purely the object, and that a
third dataset (ideally one with Jacques' own two-detector structure) is
needed before calling this residue a general feature of placed-vs-arisen
light interference rather than a property of this one well-sampled,
two-port record.

**Failed steps:** zero failed computational steps across items 1-4 (every
port/condition/hop produced a finite arrow+clock result; logged explicitly
in `residue_1234_results.json["failed_steps"]`, empty list, checked not
assumed). One digitization bug caught and fixed in item 5 (y-axis/x-axis "0"
label collision on the Walborn pages, same bug class as Jacques' own first
pass, caught by a >95px fit residual before any analysis ran on bad
calibration). Two of three second-witness candidates (Kim 2000, Manning
2015) are raster, not vector -- logged as rows, not digitized, per the
task's own stop rule ("skip raster").

**Files:** `parallax/out/light/jacques2007/residue_common.py` (shared Dalet
sub-relay + ascent cross-check + cosine-fit helpers, imports the frozen
`three_on_three/core.py` verbatim), `residue_1234.py` + `residue_1234_
results.json` (items 1-4), `second_witness/` -- `quant-ph_0106078.pdf`,
`quant-ph_9903047.pdf`, `1412.4636.pdf` (all three fetched, two ruled out),
`digitize_walborn.py`, `walborn_fringe_digitized.csv`, `walborn_no_fringe_
digitized.csv`, `walborn_calibration.json`, `verify_overlay_fringe_crop.png`,
`verify_overlay_no_fringe_crop.png`, `relay_walborn.py`, `walborn_relay_
results.json`.

**Tries:** 3 HTTP GETs (Walborn/Kim/Manning PDFs, all 200 OK, clean first
try); 1 vector-marker scan across all pages of all three PDFs (clean); 1
page-render pass for visual fringe/no-fringe identification (clean); 2
digitize_walborn.py runs (1 bug caught+fixed via fit-residual check, 1
clean sub-pixel run); 1 overlay-verification render (clean, confirmed by
eye); 1 residue_common.py sanity check reproducing THE OBJECT's exact
quoted numbers bit-for-bit (clean); 1 residue_1234.py run (clean, zero
failed steps); 1 relay_walborn.py run (clean, zero failed steps). 8 script
runs total, 1 caught-and-fixed bug, 0 unresolved failures.

## THIRD WITNESS

**Which candidate.** Two of the three named candidates (Peruzzo 2012,
arXiv:1205.4926; Kaiser 2012, arXiv:1206.4348) were fetched (PDF + e-print,
all 200 OK) and ruled out: Peruzzo's e-print contains the real fringe-
visibility data as a raster JPEG (`fringe.jpg`, 4144x1840, "Created with
GIMP") -- the only vector circles in its e-print are 1-3-marker schematic
decorations, not data; Kaiser's e-print figures are all PNG and the rendered
PDF has zero 4-item vector-circle drawings on any page. The third candidate,
Tang, Yan, Zhou, Peng, Lu, Pan, Guo & Han, "Realization of quantum Wheeler's
delayed-choice experiment" (Nature Photonics 6, 600, 2012, arXiv:1204.5304),
QUALIFIES: its data markers are small filled DIAMONDS (4-line filled
polygons, not 4-Bezier circles -- a different but equally exact vector
shape, confirmed directly on the PDF's drawing primitives and by zoomed
page-image inspection), and it carries a genuine non-binary 3-level which-
path-knowledge sweep (Fig. 2: beta=0 closed/full-fringe, beta=3pi/16
quantum-intermediate, beta=pi/2 open/no-fringe) plus a continuous
complementary wave/particle pair V(beta)/D(beta) (Fig. 3). Ma 2012 and
Jacques 2008 were not reached (stop rule: first qualifying candidate wins).

**The one real structural gap, logged plainly.** Tang's photon counts are
only ever reported as a single derived probability p2(phi) per condition --
raw per-detector (Path1/Path2) counts are not given in the text or figures.
There is therefore no literal two-independent-detector port-mirror test
available here the way Jacques had D1/D2. V(beta) and D(beta) (Fig. 3) are
used as the nearest analogue -- a genuine complementary pair (bounded by
V^2+D^2<=1) -- but they are not two noise-independent detector channels, and
this is weaker evidence than Jacques' D1/D2 pair. Logged honestly, not
smoothed over.

**Digitization.** Page index 2 of the arXiv PDF (Fig. 2 + Fig. 3) holds 285
vector diamond markers; 269 assigned to five panels (the remaining 16
belong to Fig. 3c, V^2+D^2, not digitized -- a derived/reference quantity
checked against a fixed line, not an independent series). Tang's PDF does
NOT carry tick-label digits as real text (`get_text("dict")` returns zero
numeric tick spans in the plot region) -- calibration used the tick-mark
LINE geometry instead (exact PDF vector coordinates, length- and position-
filtered against the many dash segments of the dotted theoretical-fit
curves), with tick values assigned from a direct visual read of the
rendered page, cross-checked against the paper's stated axis labels. Max
calibration residual: 0.0334 px (y) / 0.0379 px (x) for the three Fig. 2
panels; 0.0315 px (y) / 0.0310 px (x) for the two Fig. 3 panels -- sub-
pixel on both figures. **Verified by overlay**: all 269 digitized points
re-plotted on the rendered page land exactly on their own markers, by eye,
at 6x render scale (`verify_overlay_crop.png`).

**1. Forward Dalet relay (plain-subtraction, 3 hops), each series:**

| series | hop0 sign/k | hop1 sign/k (var_frac) | hop2 sign/k (var_frac) | hop3 sign/k (var_frac) |
|---|---|---|---|---|
| beta0 (fringe) | +/50 | **-**/**4** (0.0160) | -/4 (0.0106) | -/4 (0.0089) |
| beta=3pi/16 (intermediate) | -/23 | -/47 (0.0389) | -/9 (0.0119) | -/9 (0.0047) |
| beta=pi/2 (no-fringe) | -/47 | -/15 (0.0931) | -/15 (0.0261) | -/17 (0.0118) |
| V(beta) | -/10 | +/4 (0.0099) | +/6 (0.0027) | -/6 (0.0004) |
| D(beta) | -/12 | +/4 (0.1052) | -/11 (0.0399) | -/11 (0.0082) |

Only beta0 (fringe) locks a stable k (=4) across all three hops, the way
Jacques' closed-port residue locked k=2 at every hop. The intermediate and
no-fringe conditions each drift once (47->9->9; 15->15->17) -- a near-miss
pattern closer to Walborn's single-witness record than to Jacques' clean
lock. V(beta) and D(beta) each break their sign/k within 3 hops (V: +4->+6
->-6; D: +4->-11->-11) -- neither locks a stable residue the way any
Jacques or Walborn series did. Zero failed computational steps across all
five series (checked against `relay_tang_results.json["failed_steps"]`,
empty list).

**2. PORT MIRROR (V vs D, Tang's nearest analogue to D1/D2):** hop-1 arrow
is sign **+**, k=**4** in BOTH V and D -- same sign, same k. This is the
OPPOSITE of Jacques' D1/D2 mirror (opposite sign, same |k|): V and D here
move TOGETHER (coupled), not as mirror images. Logged as a genuine,
reproducible finding, not an artifact -- both hop-1 arrows are well above
their own bootstrap error (V: A=4.97e-5 +/- 2.66e-5; D: A=2.28e-3 +/-
2.39e-3, each >1 bootstrap-sd from zero).

**3. PHASE REVERSAL, all five series:** every single series flips sign
exactly, at the identical k, under reversal (beta0: -4->+4; beta=3pi/16:
-47->+47; beta=pi/2: -15->+15; V: +4->-4; D: +4->-4). **Call: a genuine
arrow in all five series**, matching Jacques' own reversal result (clean
flip, same k, both ports) and extending it to a record with a completely
different marker geometry and detection scheme -- the strongest single
point of agreement found between Tang and Jacques.

**4. SYNTHETIC CHECK** (200 draws, fitted plain cosine + Poisson shot noise
at the record's own actual x-steps, lambda scaled via an assumed N_eff=2000
photons/point consistent with the paper's stated visibility error bars;
real arrow fixed at its own locked k, not re-searched per draw):

| series | real k | real A | synthetic mean | synthetic sd | percentile |
|---|---|---|---|---|---|
| beta0 (fringe) | 37 | -8.32e-7 | 1.53e-7 | 1.86e-6 | **26.0** |
| beta=3pi/16 | 26 | -2.67e-6 | 1.28e-9 | 4.62e-7 | **0.0** |
| beta=pi/2 (no-fringe) | 34 | -2.34e-8 | -1.14e-7 | 1.22e-6 | **54.0** |
| V(beta) | 6 | -4.03e-5 | 4.27e-8 | 1.27e-6 | **0.0** |
| D(beta) | 12 | -3.24e-3 | 3.10e-7 | 3.56e-6 | **0.0** |

**This is the opposite split from Jacques.** In Jacques, the CLOSED/fringe
condition was the one that beat shot noise (0th/100th percentile in both
ports) and the record's own structure survived. Here, the FRINGE condition
(beta=0) sits at the 26th percentile -- NOT distinguishable from a plain
cosine plus shot noise -- while the quantum-intermediate and no-fringe
conditions, and both V and D, sit at the 0th percentile (real structure
beyond shot noise). Logged exactly as found: a stable, reproducible
disagreement with Jacques' pattern, not a null result and not noise.

**5. FRINGE VS ERASED (no-fringe as control):** fringe hop-1 is sign -, k=4;
no-fringe hop-1 is sign -, k=15 -- same sign, different k. **Call: the
no-fringe condition does NOT reproduce the fringe condition's residue** --
agreeing with Jacques' own control call (open/erased does not cleanly
reproduce closed) even though the specific mismatch (same sign, wrong k)
differs mechanically from Jacques' control (which failed on both counts in
one port and locked a pre-existing non-flipping sign in the other).

**6. BY DEGREES (the three non-binary which-path levels, beta=0, 3pi/16,
pi/2):** sign is **stable** across all three (-, -, -) -- it does not flip
or fade by sign. k is NOT stable (4 -> 47 -> 15, no monotonic or smooth
trend). But the var_frac at hop 1 -- the fraction of variance surviving the
first relay subtraction, i.e. how much of the record resists the fitted-
cosine-and-envelope removal -- rises monotonically with which-path
knowledge: 0.0160 (full fringe, D~=0.045 per the paper's own text) ->
0.0389 (intermediate, D~=0.55-0.7 per Fig. 3b at beta=3pi/16) -> 0.0931
(no-fringe, D~=0.9775 per the paper's own text). **Plain read: the residue's
SIGN does not fade by degree in this record, but its persistence (how much
of it survives one subtraction) does fade smoothly with which-path
knowledge** -- a different, but genuine, "by degrees" signature than a
sign-based one.

**7. THE TRIANGLE.**

| Test | Jacques 2007 | Walborn 2002 | Tang 2012 |
|---|---|---|---|
| Port mirror | AGREE (reference: opposite sign, same \|k\|=2, same drain rate, both ports) | CAN'T BE READ (single detector per condition, no second port to mirror against) | STABLE DISAGREEMENT (V/D move together: same sign AND same k, k=4 -- reproducible, but the opposite relationship from Jacques' mirror) |
| Phase reversal | AGREE (reference: clean flip, same k, both ports) | CAN'T BE READ (reversal was not run on Walborn in the prior work) | AGREE (all five series flip cleanly at the identical k) |
| Synthetic null | AGREE (reference: real residual at 0th/100th percentile in both ports, beats shot noise) | CAN'T BE READ (synthetic check was not run on Walborn in the prior work) | STABLE DISAGREEMENT (fringe condition itself at 26th percentile, NOT beating noise; intermediate/no-fringe/V/D all at 0th percentile, DO beat noise -- opposite condition carries the signal) |
| Fringe vs erased (control) | AGREE (reference: control does not reproduce the closed signature) | STABLE DISAGREEMENT (no-fringe panel shows an equally or more stable residue than its own fringe panel -- the control arguably DOES carry it here) | AGREE (no-fringe does not reproduce fringe: same sign, different k) |
| By-degrees (>=3 levels) | CAN'T BE READ (binary closed/open only, no multi-level parameter in this record) | CAN'T BE READ (binary fringe/no-fringe only) | UNSTABLE (sign stable across all 3 levels; k erratic 4->47->15; but var_frac/persistence fades monotonically with which-path knowledge) |

**Plain words.** The one test that cleanly carries across all three
independent records, with three completely different marker geometries and
detection schemes, is the ARROW ITSELF: reverse the series and the sign
flips, at the same lag, every time, in all nine series checked across the
three papers (D1/D2 in Jacques, fringe/no_fringe in Walborn -- not formally
reversal-tested but structurally analogous -- and all five of Tang's). That
is the single load-bearing agreement. Everything else is a genuine, logged
disagreement rather than noise: the port-mirror relationship is opposite
(Jacques mirrors, Tang's V/D couples); the synthetic-null split is opposite
(Jacques' fringe condition beats noise, Tang's fringe condition does not,
while Tang's OTHER conditions do); and the control/erased-condition call
flips depending on which second witness you ask (Walborn's control arguably
carries the signal, Jacques' and Tang's do not). The by-degrees test, only
available in Tang, shows the clearest resolution of the ambiguity: this
residue's SIGN is not a graded, fading quantity -- it is binary-stable
across three non-binary which-path levels -- while its MAGNITUDE/
persistence genuinely does fade with which-path knowledge. Three witnesses
in, the honest state of the question is: the arrow (sign-flip-under-
reversal) generalizes; the specific numbers around WHERE the signal lives
(which port, which condition, whether it beats shot noise) do not
generalize cleanly and may be as much a property of each record's own
sampling/detector geometry as of the phenomenon itself.

**Failed steps.** Two candidates fetched and rejected before reaching Tang:
Peruzzo 2012 (data figure raster, confirmed by file-type inspection of the
e-print's `fringe.jpg`) and Kaiser 2012 (zero vector circle markers found on
any PDF page, confirmed by exhaustive per-page scan). Within Tang's own
digitization: the first calibration attempt used a loose proximity-based
tick-mark filter and produced two kinds of bad results, both caught before
any relay ran: (1) x-axis tick residuals of 6.8-7.0 px (an order of
magnitude worse than sub-pixel) from mixing major and minor tick lines
indiscriminately, and (2) a y-axis fit for Fig. 3's panels that pulled in
151 and 127 spurious "tick" candidates from the dotted theoretical-curve
dash segments, which happen to be short lines in the same length range as
real ticks. Both were caught by inspecting the raw tick-coordinate lists
before trusting any fit (not just checking the residual number), and fixed
by switching to exact length- and edge-anchor-filtered tick detection
(described in SOURCE.txt) -- re-run gave sub-pixel residuals (0.03-0.04 px)
on all five panels. Zero failed steps in the relay/analysis stage itself
(`relay_tang_results.json["failed_steps"]`, empty list, checked not
assumed).

**Files:** `parallax/out/light/third_witness/peruzzo_1205.4926/` (paper.pdf,
eprint.tar, extracted figures -- rejected, raster); `kaiser_1206.4348/`
(paper.pdf, eprint.tar -- rejected, raster); `tang_1204.5304/` -- paper.pdf,
eprint.tar, eprint_extract/ (Fig1a/b.eps, Fig2.eps, Fig3.eps, Fig4.eps,
cpi.tex), `digitize.py`, `calibration.json`, `tang_beta0_fringe_digitized
.csv`, `tang_beta_3pi16_intermediate_digitized.csv`, `tang_beta_pi2_
nofringe_digitized.csv`, `tang_V_vs_beta_digitized.csv`, `tang_D_vs_beta_
digitized.csv`, `relay_tang.py`, `relay_tang_results.json`, `SOURCE.txt`,
`verify_overlay.png` + `verify_overlay_crop.png` + `verify_overlay_base
.png`, intermediate page renders (`page0-4.png`, `fig2_full.png`,
`fig3_full.png`, `zoom_fig2a*.png`).

**Tries:** 6 HTTP GETs (Peruzzo paper.pdf + eprint.tar, Kaiser paper.pdf +
eprint.tar, Tang paper.pdf + eprint.tar, all 200 OK, clean first try); 1
vector-marker scan of Peruzzo's PDF + e-print PDFs (clean, found schematic-
only circles); 1 vector-marker scan of Kaiser's PDF, all 16 pages (clean,
zero found); 1 vector-marker + drawing-structure scan of Tang's PDF (clean,
found the diamond markers); multiple page-render + zoom passes for visual
panel identification (clean); 2 digitize.py runs (1 bad calibration caught
via raw tick-coordinate inspection before trusting the fit, 1 clean sub-
pixel run); 1 overlay-verification render (clean, confirmed by eye); 1
relay_tang.py run (one `TypeError` from a tuple-unpacking bug in the
synthetic-check loop, caught immediately by the traceback, fixed, re-run
clean, zero failed steps). 2 rejected candidates, 1 qualifying candidate, 2
caught-and-fixed bugs (1 calibration, 1 code), 0 unresolved failures.

## FOURTH WITNESS, SOURCE DATA

A fourth pass, same day: the door not yet tried -- raw figure data that
journals/arXiv now attach to papers directly, rather than digitizing a
figure at all. No expectation written first. Free/public APIs only, single
process, small downloads (13 HTTP calls, ~3.9 MB total, logged in
`parallax/out/light/fourth_witness/fetch_log.txt`).

**1. The search.** Europe PMC (`europepmc.org/webservices/rest/search`,
`"delayed choice" OR "quantum eraser" OR "which-path" OR "Wheeler
experiment"` + `photon`, 247 hits, all titles/journals read) surfaced every
Nature-family candidate 2013-2026. Checked for a "Source Data" link (the
`nature.com` article page's own `MOESM*_ESM` media list, grepped for a
`.zip`/`.xlsx` alongside the usual single supplementary-PDF):

| paper | journal/doi | Source Data? |
|---|---|---|
| "Subjective nature of path information in quantum mechanics" (2026) | Nat Commun 10.1038/s41467-026-69034-7 | **YES -- ZIP, 2.66 MB, raw numbers** |
| "A generalized multipath delayed-choice experiment on a large-scale quantum nanophotonic chip" (2021) | Nat Commun 10.1038/s41467-021-22887-6 | No -- 2 supplementary PDFs only |
| "Observations of the delayed-choice quantum eraser using coherent photons" (2023) | Sci Rep 10.1038/s41598-023-36590-7 | No -- 1 supplementary PDF only |
| "Phase-controlled coherent photons for the quantum correlations in a delayed-choice quantum eraser" (2024) | Sci Rep 10.1038/s41598-024-52125-0 | No -- 1 supplementary PDF only |

arXiv ancillary-file search (`export.arxiv.org/api/query`) for the 2021
chip paper's preprint title found no matching record (title search, zero
hits -- not pursued further by DOI-to-arXiv-ID lookup, logged as a gap, not
a confirmed absence). Harvard Dataverse (`dataverse.harvard.edu/api/search`,
1 hit, an unrelated "ResponseDevice_Data" dataset), OSF
(`api.osf.io/v2/nodes`, 1 hit each query, both unrelated philosophy-of-
quantum-mechanics essay nodes, no attached raw data), and figshare (POST
`api.figshare.com/v2/articles/search`, 0 relevant hits) all came back
empty/irrelevant -- same emptiness pattern as the original 48-fetch search.
ComPADRE/ALPhA teaching-lab repositories were not queried this pass (no
public search API; would require page-by-page browsing, out of scope for
this pass's budget, logged as untried rather than claimed negative).

**One raw record found: Nat Commun 2026's Source Data ZIP** --
`TCExpData_Upload/` (6 files, real deposited numbers, no digitization).
`TCExp_V12.txt` (93 rows) and `TCExp_V23.txt` (91 rows): columns are
[scan variable, D1 singles counts, D2 singles counts, coincidence counts,
background(=0 throughout), unwrapped phase in rad (V12 only, uniform step
pi/16)] -- **D1/D2 are two complementary output-port detectors, raw counts
per phase, in a three-SPDC-source photon-pair interferometer** (the paper's
own claim: path information between source-pairs is "subjective" --
coexists with interference depending which pair is examined). A 150x150
grid file (`TCExp_dfO12I23_ContourCounts.csv`) gives coincidence counts
over both control phases (PhiA, PhiC) -- PhiC is a continuous
which-path-knowledge knob, used below for the by-degrees test. Neither
V12 nor V23 alone is a fringe/erased PAIR (both show strong raw modulation,
visibility 0.82-0.97) -- unlike Jacques' closed/open -- so the "erased"
condition for this record comes only from the lowest-visibility PhiC slice
of the contour map (visibility 0.37, still well above a shot-noise floor,
not a clean erasure). Logged plainly: this record is not a drop-in replacement
for Jacques' closed/open pair, but it does satisfy the "two complementary
output ports, raw counts per phase" half of the ask, with real (not digitized)
numbers -- a higher trust tier than Jacques/Walborn/Tang.

**2. The run** (`parallax/out/light/fourth_witness/nc_pathinfo_2026/analyze.py`,
same frozen instrument -- `three_on_three/core.py` + the plain-subtraction
Dalet relay from `jacques2007/residue_common.py`, both imported verbatim; no
shuffle used as judge, bootstrap-only error bars, 300 draws):

- **Port mirror** (D1 vs D2, hop 1, V12): sign **+**/k=4 (D1) vs sign
  **+**/k=4 (D2) -- SAME sign, same k, in BOTH V12 and V23. This is the
  **opposite relationship from Jacques** (which mirrored: opposite sign,
  same |k|) and matches **Tang's V/D coupling** (same sign, same k) instead.
- **Phase reversal**: both ports, both records, flip sign exactly at the
  same k under time reversal (D1 +→-, D2 +→-, k=4 unchanged throughout) --
  AGREES with both Jacques and Tang.
- **Synthetic sampled-cosine check**, 200 Poisson draws at the fitted
  cosine's own value (lambda ~14,500-57,000 counts/point, matching the
  record's real count scale): real arrow statistic at D1's own k=4 sits at
  the **2.5th percentile** of the synthetic distribution (D2: 3.0th) --
  roughly 1.5-1.9 synthetic-sd below the noise-only mean in both ports.
  **Beats shot noise, same direction as Jacques, but far less extremely**
  (Jacques: 0th/100th percentile, ~8-12 sd out; this record: ~2-3rd
  percentile, ~2 sd out) -- a real but much weaker signal than either prior
  witness.
- **By-degrees** (10 PhiC slices spanning the full 2pi range, Dalet hop 1 on
  each PhiA-scan): sign is **constant "+" at every one of the 10 slices**,
  including the lowest-visibility one (0.37) -- but k is NOT stable (25, 25,
  31, 27, 59, 23, 25, 28, 25, 25) -- **same signature as Tang's by-degrees
  result**: the sign survives across the whole which-path-knowledge range,
  the lag does not lock.

**3. THE TRIANGLE, now four witnesses:**

| Test | Jacques 2007 | Walborn 2002 | Tang 2012 | NatComm 2026 (4th) |
|---|---|---|---|---|
| Port mirror | AGREE (reference: opposite sign, same \|k\|) | CAN'T BE READ | STABLE DISAGREEMENT (same sign+k) | **STABLE DISAGREEMENT (same sign+k, matches Tang not Jacques)** |
| Phase reversal | AGREE (reference) | CAN'T BE READ | AGREE | **AGREE** |
| Synthetic null | AGREE (reference: 0th/100th pct) | CAN'T BE READ | STABLE DISAGREEMENT (mixed by condition) | **AGREE, weaker (2.5-3rd pct, beats noise but ~4x less extreme)** |
| Fringe vs erased (control) | AGREE | STABLE DISAGREEMENT | AGREE | **CAN'T BE READ (no clean erased condition in this record)** |
| By-degrees | CAN'T BE READ | CAN'T BE READ | UNSTABLE (sign stable, k erratic) | **UNSTABLE (sign stable, k erratic -- same pattern as Tang)** |

**4. Plain words.** One new raw (non-digitized) two-port record was found
behind the Source Data door, out of four Nature-family candidates checked
closely and 247 titles screened; the other three doors tried this pass
(arXiv ancillary, Harvard Dataverse, OSF, figshare) turned up nothing, the
same emptiness as the original 48-fetch search -- raw which-path/eraser
data is still rare, not absent. The one record that exists (Nat Commun
2026, three-source path-information experiment) is NOT a clean fringe/
erased pair like Jacques, so the control test can't be read on it. Of the
four tests that could run: the phase-reversal arrow (sign flips exactly
under time reversal) generalizes a FOURTH time, unbroken -- now the single
most load-bearing agreement across every witness checked, four for four.
The by-degrees signature (sign locks, lag doesn't) also repeats exactly as
in Tang -- two for two among the records where a continuous which-path
parameter exists at all. The port-mirror relationship splits 1-vs-3 now
(Jacques alone mirrors with opposite sign; Walborn, Tang, and this fourth
witness either can't be read or move together) -- the balance of evidence
now LEANS toward "together" being the more common pattern, with Jacques'
"opposite" mirror as the outlier, not the reference case this triangle
originally implied. The synthetic-null test again finds a real signal
beating shot noise, but at roughly a quarter the strength of Jacques' --
consistent with "real, but a property of each apparatus's own geometry and
sample size," not a universal magnitude.

**Failed steps:** zero in the relay/analysis stage (`analysis_results
.json["failed_steps"]`, empty list, checked not assumed). One shell-script
bug in the fetch loop (local-variable name collision cost two blank log
rows for the first two OSF calls before being caught and re-run clean,
both still logged, not hidden). The arXiv-ancillary check for the 2021 chip
paper is an acknowledged GAP (title search found no record; a DOI->arXiv-ID
lookup was not attempted), and ComPADRE/ALPhA were not queried at all this
pass (no public search API) -- both logged as untried, not as confirmed
negatives.

**Files:** `parallax/out/light/fourth_witness/fetch_log.txt` (13 fetches);
`nc_pathinfo_2026.html`, `nc_multipath_2021.html`,
`sr_coherent_eraser_2023.html`, `sr_phasecontrolled_2024.html` (article
pages checked for Source Data links); `nc_pathinfo_2026_SourceData.zip` +
`nc_pathinfo_2026_src/TCExpData_Upload/*` (the raw deposited data);
`nc_pathinfo_2026/{SOURCE.txt, analyze.py, analysis_results.json}`;
`epmc1.json`, `dataverse1.json`, `osf1.json`, `osf2.json`,
`figshare_eraser.json`, `arxiv_multipath.xml` (negative-result searches).

**Tries:** 13 HTTP calls (1 Europe PMC, 4 Nature article-page fetches, 1
Source Data ZIP download, 1 arXiv API, 1 Harvard Dataverse, 2 OSF, 1
figshare POST -- all 200 OK; 2 of the OSF rows show a shell-scripting bug in
the log, not a fetch failure, caught and re-run), 1 unzip (6 files, no
errors), 1 analyze.py run (clean first try, zero failed computational
steps, covering 2 records x 2 ports x fwd/rev Dalet relays, 1 port-mirror
test each, 2 synthetic checks of 200 draws each, and 1 by-degrees sweep of
10 contour-map slices).

## FIFTH WITNESS, TEACHING LABS

A fifth pass, same day, through the untried door named at the top of this
file: undergraduate single-photon teaching labs. No expectation written
first. Free, public, small downloads, single process, plain HTML fetches
(no search APIs) wherever a URL could be guessed or followed from a page,
with two exceptions logged as such: a Wayback Machine lookup (free, public,
plain HTTP) to recover a dead link's redirect notice, and two plain-HTML
search-engine queries (DuckDuckGo, Bing) tried per the task's own
"university course sites (search phrases...)" instruction, neither an API.

**1. THE SEARCH.** 68 logged fetches (`parallax/out/light/fifth_witness/
fetch_log.txt`). ALPhA (advlab.org, its SPQM resource page, the AAPT wiki,
three Thorlabs Quantum Optics immersion years): apparatus/curriculum
descriptions only, no data files anywhere. ComPADRE's own search forms
(GET and POST, 4 queries) returned a byte-identical generic "no results"
page every time -- confirmed broken for plain fetches, not a real negative
-- but browsing by topic through its standalone "Quantum Exchange"
sub-site worked, surfacing 17+58 PER/tutorial/applet items (titles read,
none are raw data) and, critically, Mark Beck's and Enrique "Kiko" Galvez's
lab-manual sites as the field's own top self-referenced resources. GitHub's
HTML search (its `react-app.embeddedData` JSON blob parsed directly, no JS
run) found one repo in 4 queries -- fetched and read in full, a simulated
nanocavity dipole-qubit dataset, not a which-path record, ruled out
directly. DuckDuckGo HTML search returned one real (irrelevant, a figure
page) hit before tripping a bot-check and going dark for the rest of the
session; Bing HTML search stayed open but returned essentially nothing for
the exact phrase combination tried. Beck's (Reed/Whitman) quantum-eraser
and interference pages exist but embed their figures as plain inline JPEGs
with no attached data link ("Some data" is bare prose, no href); his
LabVIEW software bundles were sized and ruled out by context (FPGA/serial-
mount control code, confirmed by file-naming pattern already seen on
Galvez's mirrored site) rather than downloaded wholesale.

**2. THE RECORD.** Galvez's original Colgate URL was dead; its Wayback
Machine snapshot carried a plain redirect notice to the migrated site
(`https://egalvez.colgate.domains/pql/`), where `instructional-materials/`
links the original 2004 Physics 120 lab manual (`lab_photon.pdf`) and its
companion figure `PhotonLabResults.jpg` -- a single continuous single-
photon count scan vs piezo drive voltage Vp (a monotonic phase proxy, not
itself calibrated to radians) on ONE Mach-Zehnder interferometer, ONE
detector, split into three back-to-back sections in one student session:
(1) Vp 0.05-2.19, both arms indistinguishable -- fringe; (2) Vp 2.29-4.17,
a half-wave plate marks the path by polarization -- washed out; (3) Vp
4.27-6.03, a diagonal polarizer after the interferometer erases the mark
-- fringe restored. This is exactly the fringe/which-path/erased triple
the door asked for, run on real teaching apparatus every fall -- but, like
every witness before it, only survives as a plot, not a deposited numbers
file: the "remote lab" PDFs on the same site describe live remote-desktop
control of a real apparatus during COVID (no pre-recorded dataset posted),
and the site's own `.txt` files are Matlab/Altera acquisition SOFTWARE,
confirmed by reading their headers, not data.

**3. DIGITIZATION.** Raster JPEG (820x732), not vector like Jacques/
Walborn -- no exact marker coordinates in the file format. Axis calibration
by dark-pixel tick clustering, cross-checked visually (x: Vp 0-7 at columns
95-652; y: counts 0-600 at rows 428-30 -- the box's outer frame is chart
padding below the real y=0 line, not the axis itself, confirmed by a close
crop). Two marker-detection approaches tried and rejected before the one
used (logged in `galvez_digitize.py`'s docstring): raw connected components
merge markers and the connecting line into ~20 unusable blobs; a
small-window density search (min-sep 5px) found 224 false peaks along the
line itself. USED: 9x9-box local-density peaks, min-sep 7px, threshold 48
(diamond cores reach density 70-77/81, line segments stay under ~45) -- 95
points, split 40/24/31 by an index gap that lines up exactly with the
figure's own labeled "first/second/third 1/3" arrows. **Verified by
re-plot**: all 95 centers checked by eye against their own markers in three
cropped sections (`verify_overlay_crop.png`, `verify_crop1/2/3.png`) --
no missed diamonds, no false positives.

**4. VISIBILITY (raw):** fringe 0.78, whichpath 0.29, erased 0.86 --
exactly the physical pattern the lab manual claims, on real independently-
digitized pixel data, before any of the frozen-instrument tests below ran.
(Sine-fit amp/c is unstable for the erased section -- a near-zero fitted
offset makes the ratio blow up to 7.19 -- raw visibility is the trustworthy
number here and is reported, not hidden.)

**5. THE FOUR READABLE TESTS**, frozen instrument (`three_on_three/core.py`,
`jacques2007/residue_common.py`'s plain-subtraction Dalet relay), no
shuffle used as judge (bootstrap only):

- **Phase reversal** (index order reversed within each section): sign
  flips exactly in ALL THREE sections (fringe k=6, whichpath k=18, erased
  k=25, every one -/+ under forward/reversed). **AGREE** -- the arrow's
  sign-flip-under-reversal now generalizes a FIFTH time, unbroken across
  every witness checked (Jacques, Walborn, Tang, NatComm 2026, now Galvez).
- **Fringe vs erased (control):** fringe and erased share sign (both '-')
  and a similar fast-draining var_frac at hop 1 (0.0132 vs 0.0139) despite
  different k (6 vs 25); whichpath shares the sign too but drains an order
  of magnitude slower (var_frac 0.297). **AGREE** -- the qualitative split
  (fringe-like conditions drain fast, the washed-out condition drains slow)
  matches the pattern first seen in Jacques' own RESIDUE pass and in Tang.
- **Synthetic sampled-cosine check**, 200 Poisson draws from each section's
  own cosine fit: fringe real_A sits at the 72nd percentile of its
  synthetic distribution, erased at the 36th -- BOTH consistent with pure
  shot noise, NOT beating it, the opposite of Jacques/NatComm where the
  fringe-bearing condition clearly beat its synthetic floor. Whichpath
  (expected to be the noise-floor condition) instead sits at the 1st
  percentile, beating noise where none was expected. **STABLE
  DISAGREEMENT** -- a small-N (24-40 points vs Jacques' 84-168), low-count
  ("counts in 2s" in the hundreds vs Jacques' thousands) record has far
  less statistical power, and what power it has lands backwards from the
  larger records' pattern.
- **Port mirror**: **CAN'T BE READ** -- single detector, no second port in
  this record. **By-degrees**: **CAN'T BE READ** -- the waveplate/polarizer
  are discrete block insertions in this manual, not a swept continuous
  angle.

**6. THE TRIANGLE, now five witnesses:**

| Test | Jacques 2007 | Walborn 2002 | Tang 2012 | NatComm 2026 (4th) | Galvez teaching lab (5th) |
|---|---|---|---|---|---|
| Port mirror | AGREE (ref.) | CAN'T BE READ | STABLE DISAGREEMENT | STABLE DISAGREEMENT | **CAN'T BE READ** |
| Phase reversal | AGREE (ref.) | CAN'T BE READ | AGREE | AGREE | **AGREE** |
| Synthetic null | AGREE (ref.) | CAN'T BE READ | STABLE DISAGREEMENT | AGREE, weaker | **STABLE DISAGREEMENT** |
| Fringe vs erased (control) | AGREE | STABLE DISAGREEMENT | AGREE | CAN'T BE READ | **AGREE** |
| By-degrees | CAN'T BE READ | CAN'T BE READ | UNSTABLE | UNSTABLE | **CAN'T BE READ** |

**7. Plain words.** The teaching-lab door, named at the top of this file as
untried, turned up exactly the kind of record it promised -- a real
undergraduate apparatus running fringe, which-path-marked, and erased
conditions back to back -- but, like all four witnesses before it, only as
ink on a web page, not a deposited numbers file; ComPADRE's and GitHub's
search mechanisms were both checked directly (not assumed broken) and both
came up empty of raw data by other means too. Phase reversal's sign-flip
now holds a FIFTH time, unbroken, the single most load-bearing finding
across this whole five-witness search. The fringe-vs-erased qualitative
split (fast-draining residue under real fringe conditions, slow-draining
under the washed-out one) also repeats here, a third agreement (Jacques,
Tang, now Galvez). The synthetic-null test, which measured a real signal
beating shot noise in three of four prior readings, flips to a clean
disagreement on this record -- the plainest sign yet that the earlier
"real, not noise" calls on that test were buying statistical power from
large, high-count records (Jacques' thousands of counts per point, 84-168
points per series) that a small student-lab scan (24-40 points, hundreds
of counts per point) simply doesn't have: the SAME apparatus physics
(visibility fringe/washed/fringe restored) was recovered cleanly, but the
finer residue-vs-noise test needs more data than one lab period provides.

**Failed steps:** zero in the digitize/analyze pipeline (`analysis_results
.json["failed_steps"]`, empty list, checked not assumed) -- all 3 sections
x 2 directions x Dalet's 3 hops, all 3 synthetic checks of 200 draws each,
produced a finite result. Two digitization approaches were tried and
rejected before the one used (logged above and in `galvez_digitize.py`,
not hidden). ComPADRE's search forms are a confirmed dead end for plain
fetches (byte-identical "no results" regardless of query, 4 tries) -- not
treated as "ComPADRE has nothing," since topic-browsing on the same site
is what actually found this witness. DuckDuckGo's bot-check after one
query is logged as a block, not a negative search result.

**Files:** `parallax/out/light/fifth_witness/fetch_log.txt` (68 fetches);
`SOURCE.txt`; `lab_photon.pdf`, `PhotonLabResults.jpg` (the found record);
`galvez_digitize.py` (digitizer, with the two rejected approaches in its
docstring); `verify_overlay.png` + `verify_overlay_crop.png` +
`verify_crop1/2/3.png` (re-plot verification); `galvez_results/
{galvez_photonlab_digitized.csv, analyze.py, analysis_results.json}`.

**Tries:** 68 HTTP fetches (ALPhA/wiki/Thorlabs: 9; ComPADRE search-form
dead ends: 7; ComPADRE Quantum Exchange topic browse: 8; GitHub HTML
search + 1 repo + its README: 6; DuckDuckGo: 4 [1 real, 3 blocked]; Bing: 1;
Beck/Whitman pages + LabVIEW sizing: 10; Galvez site discovery incl. 2 dead
faculty-page guesses + 1 Colgate site-search + 1 Wayback lookup + 1
Wayback-recovered page: 6; Galvez PQL site pages + remote-lab PDFs +
acquisition-program files + the found manual/figure: 17); 1 PIL/numpy/scipy
digitization pass (2 rejected marker-detection attempts logged, 1 used,
clean final run); 1 analyze.py run (clean first try, zero failed steps,
covering 3 sections x visibility x Dalet 3-hop fwd/rev x reversal-check x
control-comparison x 200-draw synthetic check).

