# FIRAS re-fit — testing Rabbit 1's leak, 2026-09-30

Reuses `~/bones-forge/parallax/THREE_RABBITS_20260930.md` (Rabbit 1: |residual| tracks galaxy-model
size, r=0.410-0.488, p<0.01, survives dropping the edge bin) and
`~/bones-forge/parallax/out/firas/firas_monopole_spec_v1.txt` (Fixsen et al. 1996 Table 4, 43 bins,
2.27-21.33 cm⁻¹). No re-fit had been published against this correlation before this run. Scripts:
`~/bones-forge/parallax/out/firas/refit/refit.py`. No expectation written before running.

## Method

Sky reconstructed per bin as `blackbody(T0=2.728 K) + residual + galaxy_model` (undoing Table 4's
subtraction), all in kJy/sr, Planck function computed directly (no scipy/numpy — pure Python,
Nelder-Mead with 6 random restarts per fit, single process). Four models re-fit to that
reconstructed sky by weighted chi-square (weights = Table 4 sigma column):

- **A**: BB(free T0) + galaxy × 1.0 (fixed) — the published choice
- **B**: BB(free T0) + galaxy × A_gal (free)
- **C**: BB(free T0) + galaxy (free) + power law in freq (free amplitude + index), pivoted at 10 cm⁻¹
- **D**: BB(free T0) alone, no galaxy

## Results

| model | T0 (K) | A_gal | power-law | chi2/dof (dof) |
|---|---|---|---|---|
| A (fixed gal=1) | 2.728000 | 1.0 (fixed) | — | 1.072 (42) |
| B (free gal) | 2.728001 | 0.998 | — | 1.098 (41) |
| C (free gal+PL) | 2.727982 | -0.697 | A=105.46 kJy/sr @10cm⁻¹, β=+2.86 | 1.071 (39) |
| D (BB only) | 2.728110 | — | — | **38.823 (42)** |

Model D confirms the obvious: dropping the galaxy term entirely wrecks the fit (chi2/dof 38.8,
residuals climb to 400+ kJy/sr at high frequency — that IS the galaxy).

**T0 shift vs published 2.728 ± 0.004 K:** A +0.000 mK, B +0.001 mK, C -0.018 mK, D +0.110 mK.
All four are far under the 4 mK published error (largest is 0.03σ). T0 is not the sensitive
parameter here.

## Does the leak survive?

|residual| vs galaxy-model-size correlation, re-run on each model's own refit residuals:

| model | r (43 bins) | p | r (42 bins, edge dropped) | p |
|---|---|---|---|---|
| A (fixed) | 0.488 | 0.000 | 0.410 | 0.007 |
| B (free gal) | 0.489 | 0.000 | 0.414 | 0.007 |
| C (free gal+PL) | 0.471 | 0.000 | 0.340 | 0.028 |
| D (no gal) | 0.894 | 0.000 | 0.973 | 0.000 |

**Freeing the galaxy amplitude does not kill the leak.** A_gal comes out at 0.998 (essentially
identical to the fixed value of 1.0), so the correlation barely moves (0.410 → 0.414). This is not
because the leak resists amplitude adjustment out of some special significance — it's because the
published amplitude was already close to optimal; there was nothing for a free amplitude to fix.

**The power-law term partially absorbs it but does not resolve it.** Adding a free power law drops
the edge-dropped correlation from 0.410 to 0.340, but it stays significant (p=0.028), and the
full-43-bin correlation barely moves (0.488 → 0.471). The chi2 improvement for 2 extra free
parameters is only 45.02 → 41.76 (Δchi2=3.26, not significant at 2 dof). The 1000-shuffle
background test on the power-law amplitude gives null mean -7.6 kJy/sr, std 146.6, **p=0.270** for
the observed amplitude of 105.5 kJy/sr — indistinguishable from noise. The fitted index, β=+2.86,
is the wrong sign entirely versus ARCADE 2's β≈-2.6 to -2.6 excess — this is the optimizer fitting
residual noise shape, not a physical foreground.

**Extrapolation to 1 GHz, stated plainly as unsafe:** RJ brightness temp of the power-law term at
its 10 cm⁻¹ (300 GHz) pivot is 0.038 mK; naive extrapolation using T~ν^(β-2) gives 0.0003 mK at
1 GHz. The pivot sits 300× higher in frequency than 1 GHz, β is fit only over 68-2000 GHz and is
statistically consistent with zero-informative (p=0.27 above), and the sign is already wrong for
an ARCADE-like excess. This number should not be compared to ARCADE 2 at face value — it is not
a measurement of anything at 1 GHz.

## Bottom line

Rabbit 1's correlation is real and reproduces on re-fit (0.41-0.49 either way), but it does not
behave like a hidden radio excess: a free galaxy amplitude doesn't move it (amplitude was already
~1.0), and a free power law only partially and non-significantly absorbs it, with the wrong-sign
index. Most consistent with garden-variety galaxy-model mis-specification inflating residual
variance where the galaxy term is large — the same textbook read as Rabbit 1, now with a real
re-fit behind it instead of just the raw correlation.

## Background counts

1000-shuffle nulls run twice per model (43-bin and 42-bin) for the |residual|-vs-galaxy
correlation = 8 x 1000 = 8000 shuffle fits. Plus 1000 refits of model C on shuffled Table-4
residuals for the power-law-amplitude null. Total: 9000 background trials, all pure-Python,
single process, seed 20260930, ~2 minutes wall time.
