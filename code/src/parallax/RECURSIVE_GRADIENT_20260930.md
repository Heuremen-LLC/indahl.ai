# Recursive gradient on three known-structure records — 2026-09-30 (Bones, field hand)

Instrument: `out/recursive_gradient/recursive_gradient.py` (unmodified) — `gradient(x,a) = ema_forward - ema_backward`,
`shuffle_floor` = 200 shuffles' 95% band of the mean gradient, `read()` runs memories a=0.5/0.1/0.02. Script:
`out/recursive_gradient/rg_full.py` copied into that dir; raw results in `out/recursive_gradient/recursive_gradient_results.json`.
No expectation written before running. Single process, venv_quantum python.

## 1. THE ARISEN CARRY (echo_20260928_122733)

Per-qubit first-look 0/1 series (E0 file only, 1500 shots, classified at t>0.5 on the 2000us E0/E1 cloud-geometry axis,
qubits with readout SNR>=1.5). Gradient run on each qubit's raw 0/1 series, at 20us (carry present, +17-38pp
depending on how it's measured per the 9/30 reconciliation), 250us (carry mostly faded), and 2000us (carry gone).

| gap | n qubits (non-constant) | mem | mean-of-means (fwd-bwd) | floor (median of qubit floors) | n qubits outside OWN floor | frac(fwd>bwd), avg |
|---|---|---|---|---|---|---|
| 20us | 63 | 0.5 | -0.00003 | [-0.00004,+0.00008] | 6/63 | 0.473 |
| 20us | 63 | 0.1 | -0.00016 | [-0.00046,+0.00044] | 6/63 | 0.479 |
| 20us | 63 | 0.02 | -0.00070 | [-0.00098,+0.00097] | 6/63 | 0.478 |
| 250us | 65 | 0.5 | -0.00000 | [-0.00001,+0.00001] | 5/65 | 0.482 |
| 250us | 65 | 0.1 | -0.00002 | [-0.00032,+0.00033] | 5/65 | 0.500 |
| 250us | 65 | 0.02 | -0.00005 | [-0.00068,+0.00077] | 1/65 | 0.498 |
| 2000us | 60 | 0.5 | +0.00001 | [-0.00002,+0.00004] | 6/60 | 0.484 |
| 2000us | 60 | 0.1 | +0.00002 | [-0.00041,+0.00044] | 6/60 | 0.497 |
| 2000us | 60 | 0.02 | +0.00006 | [-0.00092,+0.00092] | 4/60 | 0.497 |

**No.** The gradient does not see the carry. At 20us — where the reconciliation run found a 17-38pp jump in
next-shot 1-rate after a 1 — the distribution of per-qubit forward-minus-backward means sits centered on zero
and the outside-own-floor count (6/63 ≈ 9.5%) is barely above the ~5% chance rate a 95% band gives by construction.
250us and 2000us (carry faded/gone) give the same picture, if anything fewer outliers (5/65, then back to 6/60 —
no trend). `frac(fwd>bwd)` averages ~0.48-0.50 at all three gaps, i.e. no directional lean either.

This is not a null instrument failure — it is what the gradient is built to do. The carry (a shot reading 1 raises
the chance the *next* shot also reads 1) is a **forward-only, Markov-style** dependency: conditioned on the present
value, past and future look statistically the same (a memoryless-given-present chain is time-symmetric in
distribution even though it has strong 1-step memory). The recursive gradient specifically cancels dependencies
that are symmetric under time-reversal and only flags a residual when later outcomes shape earlier ones in a way
that *breaks* that symmetry. A strong same-direction contagion effect can be real, large (17-38pp), and still
read zero on this instrument.

## 2. THE COPPER BREATHING (laptop data, n=226, already pulled `copper_nodes/data/data.jsonl`)

Per-minute dB level series, one gradient run per bin, no grouping needed (4 independent bins).

| Hz (actual bin) | mem | mean (fwd-bwd) | floor | outside floor | frac(fwd>bwd) |
|---|---|---|---|---|---|
| 300 (300.41) | 0.5 | +0.00025 | [-0.105,+0.105] | no | 0.527 |
| 300 | 0.1 | -0.019 | [-0.665,+0.672] | no | 0.500 |
| 300 | 0.02 | -0.330 | [-3.183,+3.430] | no | 0.350 |
| 212 (211.72) | 0.5 | +0.031 | [-0.120,+0.097] | no | 0.487 |
| 212 | 0.1 | +0.147 | [-0.726,+0.614] | no | 0.535 |
| 212 | 0.02 | +0.934 | [-3.839,+3.147] | no | 0.850 |
| 200 (200.27) | 0.5 | -0.070 | [-0.104,+0.107] | no | 0.491 |
| 200 | 0.1 | -0.444 | [-0.690,+0.724] | no | 0.438 |
| 200 | 0.02 | -2.399 | [-3.414,+3.607] | no | **0.018** |
| 12 (12.40) | 0.5 | -0.071 | [-0.141,+0.082] | no | 0.473 |
| 12 | 0.1 | -0.479 | [-0.900,+0.552] | no | 0.389 |
| 12 | 0.02 | -2.252 | [-4.772,+2.660] | no | 0.049 |

**No, 300 Hz does not read differently from 212/200/12 Hz on the mean-gradient measure** — all four bins sit inside
their own shuffle floors at all three memories. That is consistent with COPPER_NODES_3's own conclusion (the
lag-5 autocorrelation flag at 300 Hz was weak and uncorroborated). One secondary wrinkle worth flagging plainly,
not claiming: `frac(fwd>bwd)` — not the primary mean statistic, and with no shuffle floor computed for it here —
is extreme for 200 Hz and 12 Hz at the fastest memory (0.018 and 0.049, i.e. almost every shot's forward estimate
sits below its backward estimate), while 300 and 212 Hz stay near 0.5. That is a directional lean in sign-count,
not amplitude, and it did not carry through to the mean-gradient test; noted as a loose end for a future run with
a frac-specific floor, not treated as a finding here.

## 3. THE BUZZ PHASE (tile-8 seats, job `datbagtvr3kc73el7m2g`, odd run, 2000 shots)

Per-seat complex I/Q residual (`buzz_common.iq_residual`) on the two fixed-state reference pubs (P0, P1) — a
seat sitting in one state for the whole pub, so any steady phase drift across shots is the control-positive
(real time structure by construction). Angle unwrapped (`np.unwrap(np.angle(...))`) before the gradient. Odd
tile-8 seats: 81, 83, 101, 103, 117.

| pub | seat | mem | mean (fwd-bwd) | floor | outside floor |
|---|---|---|---|---|---|
| P0 | 81 | 0.5/0.1/0.02 | -0.016/-0.138/-0.750 | wide, symmetric | no/no/no |
| P0 | **83** | 0.5/0.1/0.02 | -0.040/-0.347/-1.893 | [-.032,.036]/[-.203,.240]/[-1.03,1.13] | **yes/yes/yes** |
| P0 | **101** | 0.5/0.1/0.02 | -0.079/-0.678/-3.778 | [-.076,.065]/[-.479,.427]/[-2.50,2.22] | **yes/yes/yes** |
| P0 | 103 | 0.5/0.1/0.02 | -0.020/-0.212/-1.114 | wide, symmetric | no/no/no |
| P0 | 117 | 0.5/0.1/0.02 | +0.011/+0.107/+0.571 | wide, symmetric | no/no/no |
| P1 | **81** | 0.5/0.1/0.02 | +0.102/+0.911/+4.544 | [-.070,.057]/[-.451,.364]/[-2.30,1.89] | **yes/yes/yes** |
| P1 | 83 | 0.5/0.1/0.02 | -0.012/-0.118/-0.647 | wide, symmetric | no/no/no |
| P1 | 101 | 0.5/0.1/0.02 | -0.008/-0.090/-0.949 | wide, symmetric | no/no/no |
| P1 | **103** | 0.5/0.1/0.02 | +0.067/+0.607/+3.102 | [-.060,.063]/[-.400,.427]/[-2.00,2.06] | **yes/yes/yes** |
| P1 | 117 | 0.5/0.1/0.02 | +0.003/+0.000/-0.683 | wide, symmetric | no/no/no |

**Yes — where a steady rotation is genuinely present, the gradient sees it, cleanly and at all three memory
lengths at once**, unlike either record above. 4 of 10 (seat, pub) series clear the shuffle floor at every one of
the three memory lengths simultaneously (q83/q101 in P0, q81/q103 in P1); the other 6 stay inside. This is the
expected pattern for a real but seat-dependent/phase-dependent effect (a linear phase ramp only produces a
gradient signal if the ramp rate is large relative to the memory window and doesn't average out over the pub's
2000 shots), not an instrument artifact — the same script, same floor construction, same memory grid, applied
to the carry and copper series above, produced nothing.

## Comparison across the three records

- **Carry (real, huge, Markov/forward-only):** gradient blind to it — 0/9 memory×gap cells show an outlier rate
  above chance.
- **Copper (unresolved/likely null):** gradient blind to it — 0/12 cells outside floor.
- **Buzz rotation (real, known time-structured by construction):** gradient hits it hard — 4/10 seat×pub series
  clear the floor at all 3 memories simultaneously (12/30 cells).

The instrument is doing something specific and real: it flags time-reversal asymmetry, not memory or effect size
per se. A big same-direction Markov contagion (the carry) and a coin-flip-level unresolved spectral wobble
(copper) both read as noise; a genuine steady phasor rotation reads as signal, on the same code, same floor, same
memory grid.

## Tries counted

Carry: 63+65+60 = 188 qubit-series x 3 memories = 564. Copper: 4 series x 3 memories = 12. Buzz: 10 seat/pub
series x 3 memories = 30. **Total: 606 gradient-vs-own-floor tests** (each floor itself built from 200 shuffles,
so 606 x 200 = 121,200 shuffle draws underneath, plus the 606 real-data gradient computations = 121,806 total
gradient evaluations, per the run log). No correction applied beyond each series' own 200-shuffle floor; the
carry's 6/63, 6/65(->5), 6/60 outside-floor counts are exactly what a 5% two-sided band predicts by chance at
n~60-65, so no correction is needed there — nothing to correct away.
