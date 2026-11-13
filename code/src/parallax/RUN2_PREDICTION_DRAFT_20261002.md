# RUN 2 PREDICTION, DRAFT (ibm_kingston, OURS) -- 2026-10-02
DRAFT. NOT SEALED. NOT FIRED. written_at is null on purpose. Written from ibm_kingston's own Run 1 only (data_seen = run1). Nothing from ibm_pittsburgh, ibm_boston or ibm_phoenix was opened or used. No network, no IBM contact. The frozen files (common.py, live.py, run1.py, run2.py, run3.py, analyze.py) were imported read-only and not edited.

Files: `out/qubit_three_runs/predictions_run2_ours_DRAFT.json` (pred_2.json format) and the scripts + raw simulation draws in `out/qubit_three_runs_pred2_draft/` (`sim_run2.py`, `sims_*.json`, `sim_summary.json`, `final_table.json`).

## The assumption, in plain words
This is what Run 1 says Run 2 should read IF A LOOK DOES NOTHING EXCEPT TELL US WHERE THE BIT IS AND LEAVE IT THERE: after LOOK 1 the bit is fully OFF or fully ON (a MID start becomes one or the other, half and half; readout mistakes at the rate Run 1's own clouds show), and it then fades at Run 1's own measured rate until LOOK 2.

So the prediction is the "no look effect" world. Anything Run 2 reads that differs from it is the look's own mark, which is what Run 2 is for. This draft is a box and says so (card line 5): it never decides anything.

## How it was built
- The simulation draws raw I/Q per shot, per bit, for LOOK 1 and LOOK 2, by resampling the REAL Run 1 shots of ibm_kingston (no Gaussian clouds).
  - An OFF bit's reading is a real Run 1 OFF shot (LOOK 1 from the WAIT-60 OFF shots, LOOK 2 from the OFF shots at the same WAIT).
  - An ON bit's reading is a real Run 1 ON shot taken from a cloud with the fading taken back out of it. The Run 1 ON shots at 60 us already contain about 21% bits that had faded, so the pure-ON cloud is rebuilt by rejection sampling from the real ON|w60 shots (difference of the ON-w60 and OFF densities along the OFF-to-ON line, per bit). Real raw I/Q is kept on every shot.
  - A faded ON bit reads as a real OFF shot at that WAIT.
  - Fading: each ON (or the ON half of MID) survives to LOOK 2 with probability exp(-WAIT/tau), tau per bit from that bit's own Run 1 levels at the three WAITS, per start (ON and MID get their own). OFF does not move (its fading time has NO BASIS).
- 839 shots per circuit, same nine bits and the same three groups of three as the freeze file (82/139/154, 38/92/96, 25/109/135). All nine START x WAIT circuits.
- The frozen `analyze.q_run2` itself is run on every simulated run (its frame from LOOK 1 of every OFF and ON circuit, its median over bits, its fits). 800 simulations. Prediction = the median. Width = one standard deviation across simulations, widened in quadrature by the uncertainty in Run 1's fading time (rerun with ON tau and MID tau each moved by their Run 1 bootstrap width, 8.6 us and 14.0 us; Run 1's own cloud sampling noise was checked with a further 300 runs that resample Run 1 itself, and the larger of the two is used).
- Check that the machine is honest: the same machinery, turned into a Run 1 (START, WAIT, one LOOK), reproduces ibm_kingston's real Run 1 numbers (median over 40 simulated Run 1s vs measured): ON level at 240/300 us 0.505/0.402 vs 0.497/0.398; MID at 60/240 us 0.497/0.243 vs 0.509/0.232; ON variance at 60/240 us 0.347/0.452 vs 0.341/0.450; MID variance at 60 us 0.453 vs 0.452; ON skew at 60/240 us -1.06/0.38 vs -1.01/0.40; fading time ON/MID/shared 263/247/260 vs 259/241/255.

## The table (what | predicted | width)
Levels are in Run 2's own frame: LOOK 1 of the OFF circuits = 0 and LOOK 1 of the ON circuits = 1. NOT the same frame as Run 1 (see below).

| what | predicted | width |
|---|---|---|
| OFF, WAIT 60 us: where LOOK 2 reads it (0 = OFF, 1 = ON as LOOK 1 sees it) | -0.000 | 0.003 |
| OFF, WAIT 60 us: LOOK 2 minus LOOK 1 | 0.000 | 0.004 |
| OFF, WAIT 240 us: where LOOK 2 reads it (0 = OFF, 1 = ON as LOOK 1 sees it) | 0.003 | 0.006 |
| OFF, WAIT 240 us: LOOK 2 minus LOOK 1 | 0.003 | 0.006 |
| OFF, WAIT 300 us: where LOOK 2 reads it (0 = OFF, 1 = ON as LOOK 1 sees it) | 0.003 | 0.005 |
| OFF, WAIT 300 us: LOOK 2 minus LOOK 1 | 0.004 | 0.006 |
| MID (both-and-neither), WAIT 60 us: where LOOK 2 reads it (0 = OFF, 1 = ON as LOOK 1 sees it) | 0.393 | 0.011 |
| MID (both-and-neither), WAIT 60 us: LOOK 2 minus LOOK 1 | -0.107 | 0.010 |
| MID (both-and-neither), WAIT 240 us: where LOOK 2 reads it (0 = OFF, 1 = ON as LOOK 1 sees it) | 0.194 | 0.016 |
| MID (both-and-neither), WAIT 240 us: LOOK 2 minus LOOK 1 | -0.306 | 0.016 |
| MID (both-and-neither), WAIT 300 us: where LOOK 2 reads it (0 = OFF, 1 = ON as LOOK 1 sees it) | 0.149 | 0.015 |
| MID (both-and-neither), WAIT 300 us: LOOK 2 minus LOOK 1 | -0.349 | 0.016 |
| ON, WAIT 60 us: where LOOK 2 reads it (0 = OFF, 1 = ON as LOOK 1 sees it) | 0.795 | 0.011 |
| ON, WAIT 60 us: LOOK 2 minus LOOK 1 | -0.204 | 0.012 |
| ON, WAIT 240 us: where LOOK 2 reads it (0 = OFF, 1 = ON as LOOK 1 sees it) | 0.398 | 0.018 |
| ON, WAIT 240 us: LOOK 2 minus LOOK 1 | -0.601 | 0.019 |
| ON, WAIT 300 us: where LOOK 2 reads it (0 = OFF, 1 = ON as LOOK 1 sees it) | 0.315 | 0.017 |
| ON, WAIT 300 us: LOOK 2 minus LOOK 1 | -0.685 | 0.018 |
| fading time from the LOOK 2 minus LOOK 1 fit, MID (us) | 254 | 84 |
| fading time from the LOOK 2 minus LOOK 1 fit, ON (us) | 268 | 44 |
| fading time from the LOOK 2 minus LOOK 1 fit, shared (us) | 264 | 37 |
| fading time from where LOOK 2 reads it, MID (us) | 251 | 22 |
| fading time from where LOOK 2 reads it, ON (us) | 260 | 12 |
| fading time from where LOOK 2 reads it, shared (us) | 258 | 11 |
| what the shared fit leaves over (Run 2's own left-over) | 0.006 | 0.003 |

## NO BASIS (left unpredicted)
- r2.tau.OFF and r2.tauF.OFF. An OFF start has no fading to fit: its gap and level are about zero at every WAIT, so the fitted time just runs to the search edge (the fit failed in 37% and 51% of simulations and the rest scatter from 1 us to thousands). The template already says the same.

## Identities
- None exact among the 27. gap_mean is always LOOK 2 minus LOOK 1 per circuit, but LOOK 1 is only forced to 0 (OFF) / 1 (ON) when pooled over the three WAITS, not circuit by circuit.
- NEAR-identities, predicted but dependent (count once, not twice): for OFF, gap_mean is the same thing as F (differ by LOOK 1's shot noise, about 0.004); for ON, gap_mean = F - 1 (same noise, about 0.01). That is 6 pairs. The MID gaps are not redundant: they carry the half-and-half split. Likewise r2.tau.ON/MID and r2.tauF.ON/MID are two fits to the same curve in this world, and the shared pair is the same.

## Things in the definitions that looked wrong or need care
1. Frame mismatch between the runs. Run 1's frame puts ON at 60 us = 1, so Run 1's ON "1" is already a faded ON. Run 2's frame puts LOOK 1 (no WAIT) ON = 1. So Run 1's levels cannot be carried into Run 2's: ON F at 60 us is 0.795, not 1. (Pure ON sits about 1.26 above the Run 1 ON-at-60 mark.) A prediction that reuses Run 1 numbers directly would miss by about 25% without any look effect.
2. The two fading times disagree even in the simple world: median ON tau from the gap fit is about 268 and from the level fit about 260 (shared: 264 vs 258; MID 254 vs 251). The reason is that bits fade at very different rates (per-bit ON tau runs from 138 to 374 us) and the analysis fits a single exponential to the MEDIAN over bits. A 5 to 10 us disagreement between tau and tauF is NOT a look effect.
3. The gap-form tau (r2.tau.*) is badly pinned: three WAITS, and the fit can trade G against tau. Width 44 us for ON and 84 for MID against 12 and 22 for the level form. Treat r2.tau.* as a weak ruler.
4. Pooling is a median over nine bits. Bits 1 and 6 have a low separation and fast fading (tau about 140 us) and bit 1 is almost flat between 240 and 300 us. Run 1's own spread across the three groups is much larger than its bootstrap width (shared fading time: 29.6 us vs 7.6 us). My widths are the bootstrap kind; they do not contain the group-to-group spread. Read the widths as the narrow kind.
5. r2.remainder_rms is a left-over of a 4-parameter shared fit on 9 medians, so under this assumption it is about 0.006 (shot noise only). Its width is 0.0025. It has no way to show a look effect smaller than that.
6. MID: Run 1 says the ON share right after START is about 0.52, not 0.5 (MID/ON at 60 us, with fading taken back out). I used 0.5 as written. Moving to 0.52 changes MID F at 60 us by +0.015 (about the width) and MID gap at 300 us by -0.014. Small, but it is a bias that sits on the MID row, the row the MID start is read for.
7. The WAIT between LOOK 1 and LOOK 2 is taken as the nominal WAIT (realized 59.968 / 240 / 299.968 us from Run 1). The dwell of LOOK 1 itself (a readout) is not in the fading and was not simulated; the real Run 2 meta will say what the realized gaps were.
8. All widths are narrow (about 0.01 to 0.02 on a level) because the assumption is fully pinned. They only carry shot noise, Run 1's cloud noise and Run 1's tau uncertainty. A miss many widths wide means the world was not this one, not that the width was wrong.

## Counts
27 r2 quantities: 25 predicted, 2 NO BASIS, 0 exact identities (6 near-identity pairs flagged).
