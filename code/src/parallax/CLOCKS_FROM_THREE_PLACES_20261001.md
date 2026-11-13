# CLOCKS FROM THREE PLACES -- 2026-10-01, Bones's field hand

THIRD_RUNG_20260928.md Sec.65. Wayfinder, ~00:20Z 10/1: "triangulate those clocks themselves, turning one off at
a time, seeing how one racks to the other -- you're only gonna see one move at a time because they're three
different clocks, so take the measurement from three different places. You took one snapshot and said 'corner
heat, whatever.' Try again."

No numeric prediction written before running. Script: `out/the_middle/clocks_from_three_places.py`. Raw output:
`out/the_middle/clocks_from_three_places_results.json`. Data: `out/echo_20260928_122733/` (ibm_marrakesh, 78
even qubits, 1500 shots/job, raw kerneled I/Q, gaps 20/50/100/250/500/1000/2000us) and, for the T1-third test,
`out/the_middle/one_qubit_triangle_results.json` (already-computed per-qubit A, B(cutoff 0.50), T1, reused
verbatim rather than refit). 74/78 qubits pass the SNR>=1.5 readout gate; named blinkers q68, q76 excluded from
every pooled test per standing instruction. numpy only, single process, ~6.5 seconds runtime.

Each dial is a real split of the same shots ONE OF THE THREE CLOCKS ITSELF is built from or adjacent to, applied
to see whether a DIFFERENT clock moves when that dial is turned. Sign kept throughout; no shuffle used as judge
anywhere below (every verdict is band-vs-band spread vs combined error, or condition-vs-condition, never a
shuffle background).

## 1. THE CARRY (A) IN BANDS OF THE DRAIN (B)'s LOCAL STATE

Per qubit: a trailing 100-shot rolling rate of that qubit's own first-look 1s (computed on the raw m0 sequence,
pooled over E0+E1 and the three fast gaps to fix one pair of tercile cuts per qubit) bands every transition's
PRE-transition instant into low/mid/high thirds of that qubit's own distribution. Inside each band, the
corrected (lag1-minus-lag20) carry is computed at 20/50/100us and tau_A is fit; bootstrap error resamples
band-restricted events with replacement, 150 draws.

| band | n qubits (fittable) | pooled tau_A (us) | chi2/dof |
|---|---|---|---|
| low | 11 | 19.6 +/- 9.4 | 0.21 |
| mid | 14 | 27.3 +/- 9.6 | 0.57 |
| high | 46 | 7.9 +/- 1.8 | 0.19 |

Resolved (fittable decaying 20/50/100us series) in 12/74, 15/74, 47/74 qubits respectively (a qubit can resolve
in more than one band since bands partition transitions, not qubits). **Spread across bands = 19.4us vs combined
error 13.6us -> A MOVES when B's local state is turned.** Plain read: when the drain sits locally HIGH (the
qubit is currently running hot), the carry's own time constant is fast and tight (7.9+/-1.8us, the best-
constrained of the three bands, n=46); at low/mid local drain state the carry is slower and far less certain
(19.6-27.3us, wide errors, n=11-14). The carry is not indifferent to the drain's own instantaneous state.

Failed rows: 74-12=62 qubits fail to resolve A in the low band, 74-15=59 in mid, 74-47=27 in high (148 total
failed (qubit,band) cells, counted).

## 2. THE DRAIN (B) BY THE PREVIOUS SHOT'S OUTCOME

Per qubit, per gap: shots split by whether the immediately preceding shot (same file, same gap job) read 1,
read 0, or there was no preceding shot (batch start, n=1 per file = 2 per qubit, pooled). Excess = rate in that
condition minus the qubit's own unconditioned 2000us floor; tau_B fit on 20/50/100us; bootstrap as above.

| condition | n qubits (fittable) | pooled tau_B (us) | chi2/dof |
|---|---|---|---|
| followed a 1 | 31 | 98.6 +/- 7.8 | 26.73 |
| followed a 0 | 17 | 105.8 +/- 20.3 | 0.86 |
| batch start | 0 | -- (no fittable series anywhere; n=2 events/qubit is too thin) | -- |

Batch-start never resolves -- reported as UNRESOLVED, not zero. Between the two conditions that DO resolve:
spread = 7.1us vs combined error 21.7us -- **on its own this reads DID NOT MOVE**, but the third band is missing
entirely, so the cell is scored **UNRESOLVED** (a verdict needs all three bands; two out of three isn't the test
that was designed). The "followed a 1" pooled fit is a poor fit chip-wide (chi2/dof=26.7, n=31) -- the tau_B
VALUES themselves vary far more across qubits within this one condition than bootstrap error alone explains, an
honest red flag against trusting this pooled mean as "the" answer even before comparing conditions.

Failed rows: 74-31=43 (followed-1), 74-17=57 (followed-0), 74-0=74 (batch-start) = 171 failed (qubit,condition)
cells, counted.

## 3. BOTH CLOCKS BY T1 THIRDS

Reusing `one_qubit_triangle_results.json`'s 20 non-blinker qubits with all three clocks already resolvable
(A, B at cutoff 0.50, T1). Tercile cuts on T1: 143.5us / 213.1us.

| T1 third | n | mean T1 (us) | pooled tau_A (us) | chi2/dof (A) | pooled tau_B (us) | chi2/dof (B) |
|---|---|---|---|---|---|---|
| low | 7 | 86.3 +/- 15.0 | 184.6 +/- 53.9 | 0.22 | 51.1 +/- 4.7 | 6.65 |
| mid | 6 | 180.9 +/- 7.8 | 52.6 +/- 50.3 | 0.04 | 68.8 +/- 9.6 | 0.57 |
| high | 7 | 256.3 +/- 10.5 | 69.0 +/- 35.0 | 1.65 | 53.9 +/- 9.7 | 0.20 |

Spread of tau_A across T1 thirds = 132.0us vs combined error 78.6us -> **A MOVES with T1**, but non-monotonically
(low-T1 qubits carry the SLOWEST arisen carry, not the fastest or the T1-tracking one) -- not the shape a
"carry tracks relaxation" story would predict. Spread of tau_B = 17.7us vs combined error 11.9us -> **B also
MOVES with T1**, likewise non-monotonic (low-T1 fastest drain, mid-T1 slowest). Both move, neither moves the
way "the drain/carry is just T1" would require -- consistent with `PRE_MEASUREMENT_20260930.md` Sec.3's
rho(tau_B,T1)=0.03 null on the correlation, now shown as a real but NON-monotonic band effect instead of no
effect at all. n=6-7 qubits per band is thin; read as suggestive, not settled.

## 4. THE 3x3 TABLE

Nine cells: three dials (drain-state band, previous-shot condition, T1 third) each read against three clocks
(A, B, T1-itself). Three of the nine are near-trivial by construction (a dial built directly from a clock will
of course show that clock moving) and are marked, not hidden.

| dial \ clock | A | B | T1 |
|---|---|---|---|
| drain-state band | **MOVED** (spread 19.4 vs err 13.6) | **MOVED*** (spread 916 vs err 495) | **MOVED** (spread 41.6 vs err 37.4) |
| previous-shot cond. | UNRESOLVED (batch-start empty) | UNRESOLVED* (batch-start empty) | **MOVED** (spread 55.9 vs err 37.9) |
| T1 third | **MOVED** (spread 132.0 vs err 78.6) | **MOVED** (spread 17.7 vs err 11.9) | **MOVED*** (trivial, by construction) |

`*` = near-trivial: the dial and the clock in that cell are built from the same or adjacent raw material
(drain-state band vs clock B itself; previous-shot condition vs clock B itself; T1 third vs T1 itself). Their
"MOVED" verdicts confirm the construction did what it was built to do and are not independent evidence.

The two clean, non-trivial, non-degenerate findings: **drain-state band moves A** (Sec.1) and **T1 third moves
both A and B, non-monotonically** (Sec.3). The (drain-state band, T1) and (previous-shot, T1) cells are real
computed numbers (weighted-average T1 of the qubits/events landing in each band/condition) but read as
population-selection checks, not physics: they ask whether the SAME qubits keep showing up in a given
drain-state or previous-shot bucket, not whether time itself moves.

## 5. THE REVERSAL CONTROL

Same per-qubit A and B recipe (unconditioned, cutoff 0.50), run twice on the identical qubit population: once
forward (real acquisition order) and once with each qubit's m0 sequence reversed before computing lag-diffs /
excess curves.

| clock | order | n | pooled tau (us) | chi2/dof |
|---|---|---|---|---|
| A | forward | 49 | 65.9 +/- 18.5 | 1.34 |
| A | reversed | 47 | 64.7 +/- 14.9 | 0.73 |
| B | forward | 21 | 52.9 +/- 4.1 | 3.38 |
| B | reversed | 21 | 53.0 +/- 3.9 | 2.55 |

**B does not care about direction** (52.9 vs 53.0, near-identical) -- exactly the predicted control outcome for
a clock built from elapsed gap, not shot adjacency. **A also does not care about direction** (65.9 vs 64.7,
well within error of each other) -- this is NOT what "a forward memory" predicts. Read plainly: this diagnostic
(lag1-minus-lag20 lift, lag counted in lookback steps either way) cannot distinguish a one-directional
forward-only memory from a direction-symmetric local autocorrelation (ordinary bursty/telegraph clustering),
because reversing an array preserves adjacency -- a lag-1 pair stays a lag-1 pair, just read tail-to-head. The
carry's SIZE and DECAY did not vanish in reverse; whatever produces it is symmetric under this test, which
means the earlier framing of A as specifically a "forward" carry is not established by this data -- it is a
real, decaying, per-qubit adjacency effect, but this control does not show it has an arrow.

## 6. Plain words

- **A moves when B's local state is turned** (Sec.1): hot local drain -> fast, tight carry (7.9us); cool local
  drain -> slower, looser carry (20-27us). The two are not independent.
- **B does not move cleanly when A's input (the previous shot) is turned** (Sec.2): only two of three
  conditions resolve at all, and the one condition that does resolve ("followed a 1") is itself a bad pooled
  fit (chi2/dof=26.7) -- there is real per-qubit disagreement inside that single condition, before even
  comparing conditions. Read as UNRESOLVED, not "B is independent of A."
- **Both A and B move with T1, but neither tracks it monotonically** (Sec.3) -- consistent with the earlier
  finding that neither clock IS T1, now shown as a real but non-linear T1-band effect rather than a flat null.
- **The reversal control does not support "A is a forward memory"** (Sec.5): both A and B are indifferent to
  shot-order direction at the pooled level. This is the most important honest correction this run produces: the
  earlier language calling A an "arisen carry" implicitly forward in time is not backed by this test.
- One time or three: this data says the three readings interact (turning one dial visibly moves at least one
  other clock in five of the nine non-trivial-adjacent cells), so they are not three fully independent
  processes sitting on one chip by coincidence -- but they also don't collapse into one shared clock either
  (Sec.3's non-monotonic T1 bands, Sec.5's symmetric-under-reversal carry). The honest picture is coupled but
  distinct: three readings that lean on each other's state without being the same clock.

## Tries counted

456 group computations (74 qubits x 3 bands for Test1 + 74 qubits x 3 conditions for Test2, each producing a
point-fit-plus-150-boot result) + 40,102 fits (point fits and their 150-draw bootstrap refits, printed by the
script's own TRIES counter, Test1+Test2+Test4's cross-cells+Test5's forward/reversed refits) + 50,100 bootstrap
draws + 9 movement-verdict tests (the 3x3 table cells) = **51,665 tries counted**, printed by the script itself,
not asserted after the fact. Failed rows: 148 (Test1) + 171 (Test2) = 319 failed (qubit,band/condition) cells,
every one listed in the raw JSON's `test1_failed` / `test2_failed` arrays.
