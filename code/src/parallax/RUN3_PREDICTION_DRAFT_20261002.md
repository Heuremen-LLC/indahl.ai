# RUN 3 PREDICTION, DRAFT (ibm_kingston, OURS) -- 2026-10-02
DRAFT. NOT SEALED. NOT FIRED. written_at is null on purpose. Written from ibm_kingston's own Runs 1 and 2 only (data_seen = runs1+2). Nothing from ibm_pittsburgh, ibm_boston or ibm_phoenix was opened or used (ibm_phoenix data not used; no file under data/fire/ibm_pittsburgh/ was listed or read). No network, no IBM contact, single process. The frozen files (common.py, live.py, run1.py, run2.py, run3.py, analyze.py) were imported read-only and not edited.

Files: `out/qubit_three_runs/predictions_run3_ours_DRAFT.json` (pred_3.json format, r3.* entries only) and, in `out/qubit_three_runs_pred3_draft/`: `sim_run3.py` (the machine), `run_ensembles.py` (calibration plus the 2 x 500 simulations), `sims_run3.json` (every draw), `final_table.json`, `param_info.json`, `validate_run2.txt`, `validate_run2_calibrated.txt`.

## The assumption, in plain words
Each LOOK tells us where the bit is and leaves it there, AND takes the same bite Run 2 measured (the extra drop seen after a LOOK, with whatever dependence on the WAIT Run 2's three WAITS show, fitted per START from Run 2's own data, with its width). Between looks the bit fades at the rate Runs 1 and 2 measured. A second LOOK takes the same bite as the first.

## How it was built
- Raw I/Q is resampled from the real ibm_kingston shots, per bit, never cut to 0/1. LOOK 1 of every START is drawn from Run 2's real LOOK 1 shots (no WAIT before them, so they are clean OFF / ON clouds; 2,517 shots per bit). A MID START becomes ON or OFF at LOOK 1 in the share Run 2's MID LOOK 1 shows (0.50 on average, per bit 0.49 to 0.52).
- A bit found ON survives each WAIT with probability exp(-WAIT/tau) times (1 - bite for that WAIT). tau is per bit and per START from Run 1's own levels at its three WAITS (zero earlier looks, plain fading). A bit found OFF stays OFF. After each WAIT the reading is a real ON-cloud shot if the bit is still ON, otherwise a real OFF-cloud shot taken from Run 2's OFF circuits at that WAIT (one earlier look).
- The bite is fitted per START and per WAIT so that the simulation of Run 2 gives back Run 2's real LOOK 2 levels (calibrated by simulating Run 2 itself four times over; the residual after calibration is below 0.001 in every cell). OFF has no bite (OFF does not move).
- Same nine bits and groups as the freeze (82/139/154, 38/92/96, 25/109/135), 839 shots per circuit, all 18 circuits (3 STARTS x 6 layouts), and the frozen `analyze.q_run3` is run on each simulated run. Its frame, its three-cornered-hat solve, its fits and its median over the nine bits are the real ones.
- 500 simulations with the best-fit parameters (prediction = the median; shot noise only), and 500 more where every simulation first redraws Runs 1 and 2 by bootstrap (shots resampled) and refits the bite, the fading times, the MID share and the clouds (shot noise plus fit uncertainty). Width = sqrt(sd_A^2 + max(sd_B^2 - sd_A^2, 0)) = the sd of the first set widened in quadrature by what the refits add.

## The fitted bite, per START
Bite = the fraction of the bits that would still be ON that is lost right after a LOOK (so the reading after a LOOK is plain fading times (1 - bite)). Width = bootstrap sd of Runs 1 and 2.

| START | WAIT after the LOOK | bite | width |
|---|---|---|---|
| ON | 60 us | 0.063 | 0.015 |
| ON | 240 us | 0.050 | 0.039 |
| ON | 300 us | 0.047 | 0.057 |
| MID (both-and-neither) | 60 us | 0.053 | 0.025 |
| MID (both-and-neither) | 240 us | 0.063 | 0.075 |
| MID (both-and-neither) | 300 us | 0.012 | 0.101 |
| OFF | all | 0 (does not move) | n/a |

In plain levels (Run 2's frame): ON reads 0.742 / 0.373 / 0.298 at 60 / 240 / 300 us, where a LOOK-does-nothing world gave 0.795 / 0.398 / 0.315 (drop 0.053 / 0.025 / 0.017). MID reads 0.366 / 0.179 / 0.147 against 0.393 / 0.194 / 0.149 (drop 0.027 / 0.015 / 0.002). As a share of what is still ON, ON's bite is about the same at the three WAITS (0.06 / 0.05 / 0.05, inside the widths); the width grows with the WAIT because less is left to bite. MID's bite at 300 us is not separable from zero.
The bite and the fading time trade against each other inside one WAIT, but a chain of two WAITS only uses their product at each step, so Run 3's numbers are pinned by Run 2's LOOK 2 levels rather than by the split.

## The table (what | predicted | width)
Levels are in Run 3's own frame (LOOK 1 of every OFF circuit = 0, of every ON circuit = 1). Variances are of the projected readings. "twin a/b" = layout (a,b) minus layout (b,a): (a us then b us) minus (b us then a us). Pooling is the median over the nine bits, as the frozen analysis does.

| what | predicted | width |
|---|---|---|
| OFF: own-error share of LOOK 1 from the three-cornered-hat solve (hat1), pooled over the six layouts | 0.030 | 0.0015 |
| OFF: own-error share of LOOK 2 from the three-cornered-hat solve (hat2), pooled over the six layouts | 0.036 | 0.0022 |
| OFF: own-error share of LOOK 3 from the three-cornered-hat solve (hat3), pooled over the six layouts | 0.036 | 0.0022 |
| MID (both-and-neither): own-error share of LOOK 1 from the three-cornered-hat solve (hat1), pooled over the six layouts | 0.199 | 0.0053 |
| MID (both-and-neither): own-error share of LOOK 2 from the three-cornered-hat solve (hat2), pooled over the six layouts | 0.065 | 0.0032 |
| MID (both-and-neither): own-error share of LOOK 3 from the three-cornered-hat solve (hat3), pooled over the six layouts | 0.112 | 0.0035 |
| ON: own-error share of LOOK 1 from the three-cornered-hat solve (hat1), pooled over the six layouts | 0.135 | 0.0058 |
| ON: own-error share of LOOK 2 from the three-cornered-hat solve (hat2), pooled over the six layouts | 0.147 | 0.0039 |
| ON: own-error share of LOOK 3 from the three-cornered-hat solve (hat3), pooled over the six layouts | 0.091 | 0.005 |
| all starts: own-error share of LOOK 1 (hat1) | 0.122 | 0.0028 |
| all starts: own-error share of LOOK 2 (hat2) | 0.083 | 0.0024 |
| all starts: own-error share of LOOK 3 (hat3) | 0.080 | 0.0027 |
| fading time from the LOOK 1 -> LOOK 2 gap fit, shared (us) | 164 | 19 |
| fading time from where LOOK 3 reads it, MID (us) [not a clean fading time, see below] | 746 | 4.6e+02 |
| fading time from where LOOK 3 reads it, ON (us) [not a clean fading time, see below] | 637 | 1.1e+02 |
| fading time from where LOOK 3 reads it, shared (us) [not a clean fading time, see below] | 655 | 96 |
| what the covariance left-over comes to (r3.remainder_rms) | 0.056 | 0.0015 |
| twin 60/240 us, OFF: where LOOK 2 reads it, (60,240) minus (240,60) | 0.001 | 0.0057 |
| twin 60/240 us, OFF: where LOOK 3 reads it, (60,240) minus (240,60) | -0.001 | 0.0058 |
| twin 60/240 us, OFF: LOOK 3 minus LOOK 1, (60,240) minus (240,60) | -0.001 | 0.0069 |
| twin 60/240 us, OFF: spread of (LOOK 1 minus LOOK 3), (60,240) minus (240,60) | 0.001 | 0.003 |
| twin 60/240 us, MID (both-and-neither): where LOOK 2 reads it, (60,240) minus (240,60) | 0.193 | 0.019 |
| twin 60/240 us, MID (both-and-neither): where LOOK 3 reads it, (60,240) minus (240,60) | -0.002 | 0.0084 |
| twin 60/240 us, MID (both-and-neither): LOOK 3 minus LOOK 1, (60,240) minus (240,60) | -0.003 | 0.012 |
| twin 60/240 us, MID (both-and-neither): spread of (LOOK 1 minus LOOK 3), (60,240) minus (240,60) | -0.0002 | 0.0063 |
| twin 60/240 us, ON: where LOOK 2 reads it, (60,240) minus (240,60) | 0.368 | 0.021 |
| twin 60/240 us, ON: where LOOK 3 reads it, (60,240) minus (240,60) | -0.002 | 0.0097 |
| twin 60/240 us, ON: LOOK 3 minus LOOK 1, (60,240) minus (240,60) | -0.002 | 0.01 |
| twin 60/240 us, ON: spread of (LOOK 1 minus LOOK 3), (60,240) minus (240,60) | -0.0002 | 0.0069 |
| twin 60/300 us, OFF: where LOOK 2 reads it, (60,300) minus (300,60) | -0.002 | 0.0054 |
| twin 60/300 us, OFF: where LOOK 3 reads it, (60,300) minus (300,60) | 0.002 | 0.0052 |
| twin 60/300 us, OFF: LOOK 3 minus LOOK 1, (60,300) minus (300,60) | 0.002 | 0.0063 |
| twin 60/300 us, OFF: spread of (LOOK 1 minus LOOK 3), (60,300) minus (300,60) | 0.0008 | 0.0032 |
| twin 60/300 us, MID (both-and-neither): where LOOK 2 reads it, (60,300) minus (300,60) | 0.221 | 0.019 |
| twin 60/300 us, MID (both-and-neither): where LOOK 3 reads it, (60,300) minus (300,60) | 0.0007 | 0.0076 |
| twin 60/300 us, MID (both-and-neither): LOOK 3 minus LOOK 1, (60,300) minus (300,60) | -0.0001 | 0.011 |
| twin 60/300 us, MID (both-and-neither): spread of (LOOK 1 minus LOOK 3), (60,300) minus (300,60) | -0.0006 | 0.0063 |
| twin 60/300 us, ON: where LOOK 2 reads it, (60,300) minus (300,60) | 0.444 | 0.022 |
| twin 60/300 us, ON: where LOOK 3 reads it, (60,300) minus (300,60) | 0.002 | 0.0095 |
| twin 60/300 us, ON: LOOK 3 minus LOOK 1, (60,300) minus (300,60) | 0.001 | 0.01 |
| twin 60/300 us, ON: spread of (LOOK 1 minus LOOK 3), (60,300) minus (300,60) | -0.001 | 0.007 |
| twin 240/300 us, OFF: where LOOK 2 reads it, (240,300) minus (300,240) | -0.004 | 0.0058 |
| twin 240/300 us, OFF: where LOOK 3 reads it, (240,300) minus (300,240) | 0.004 | 0.0057 |
| twin 240/300 us, OFF: LOOK 3 minus LOOK 1, (240,300) minus (300,240) | 0.003 | 0.0069 |
| twin 240/300 us, OFF: spread of (LOOK 1 minus LOOK 3), (240,300) minus (300,240) | 0.0002 | 0.003 |
| twin 240/300 us, MID (both-and-neither): where LOOK 2 reads it, (240,300) minus (300,240) | 0.026 | 0.015 |
| twin 240/300 us, MID (both-and-neither): where LOOK 3 reads it, (240,300) minus (300,240) | 0.004 | 0.0073 |
| twin 240/300 us, MID (both-and-neither): LOOK 3 minus LOOK 1, (240,300) minus (300,240) | 0.004 | 0.012 |
| twin 240/300 us, MID (both-and-neither): spread of (LOOK 1 minus LOOK 3), (240,300) minus (300,240) | -0.0001 | 0.0063 |
| twin 240/300 us, ON: where LOOK 2 reads it, (240,300) minus (300,240) | 0.069 | 0.019 |
| twin 240/300 us, ON: where LOOK 3 reads it, (240,300) minus (300,240) | 0.003 | 0.0079 |
| twin 240/300 us, ON: LOOK 3 minus LOOK 1, (240,300) minus (300,240) | 0.003 | 0.0093 |
| twin 240/300 us, ON: spread of (LOOK 1 minus LOOK 3), (240,300) minus (300,240) | -0.0007 | 0.0064 |

## NO BASIS (left unpredicted, null in the JSON)
- r3.tauF.OFF: an OFF START does not fade, so there is nothing to fit (22% of the best-fit simulations and 34% of the bootstrap ones failed; the rest run from 1 us to thousands).
- r3.tau23.shared: the LOOK 2 -> LOOK 3 gap time. The assumption does not pin it: median about 800 us, spread above 2,000 us, 12% of bootstrap runs failed to fit.

## Identities and forced-by-construction
- Exact identities among the 55 r3 quantities in pred_3.json: none (so none withheld for that reason). The closure ruler (g12 + g23 = g13) is an exact identity but is not in pred_3.json.
- ZERO BY THE ASSUMPTION'S OWN SYMMETRY (27 predicted: L3mean, g13, V13 for each of three twins and three STARTS): each step only depends on the WAIT just elapsed, so a bit that is ON at LOOK 3 survived (a) and (b) in either order. The assumption therefore forces the twin to read 0 at LOOK 3; the numbers carry the sampling width only (the tiny non-zero medians are Monte Carlo noise, or the OFF cloud's small WAIT dependence, about 0.004). These are the turning-back-time rows: the box says 0 and nothing in it can move that. Not an identity of the analysis.
- NEAR-IDENTITY pairs (9): twin g13 = twin L3mean minus the same twin's LOOK 1 difference (LOOK 1 sampling noise only). Count once.
- REPLAY OF RUN 2 (9, the twin L2mean rows): LOOK 2 of Run 3 is in the very condition Run 2's LOOK 2 was (one earlier look, one WAIT) and the bite is calibrated to it, so these are Run 2's own level differences again, not a new number (ON 60/240: 0.368 vs Run 2's 0.742 - 0.373 = 0.369).
- COPIED CLOUD (3): OFF hat1 equals Run 2's OFF LOOK 1 spread (0.0302) by construction; OFF hat2/hat3 are the OFF cloud spread at LOOK 2/3 carried over.
- r3.tauF.ON/MID/shared are one curve fitted three ways, not three independent numbers.

## Things that looked wrong or need care
1. NOISE BETWEEN LOOKS IS NOT MODELLED. In the real Run 2 the reading noise of LOOK 2 is correlated with LOOK 1's (OFF 0.14 at 60 us, ON 0.11, then 0.03 to 0.05 at longer WAITS; the simulation has about 0). Replaying Run 2 with this machine, the spread of (LOOK 2 minus LOOK 1) comes out high in places: ON 60 us 0.277 vs real 0.249 (3.2 sd), MID 60 us 0.193 vs 0.175 (2.3 sd), MID 300 us 0.302 vs 0.282 (2.4 sd), OFF 60 us 0.063 vs 0.057 (1.8 sd). The levels, gaps and fading times replay fine (tauF shared 260 vs real 262). So the hat, V13 and remainder_rms predictions are probably biased high by up to about 10% at short WAITS, and the covariance remainder (r3.remainder_rms, 0.056) is a structure in this world (bits switching state), not noise. The widths do not contain that bias.
2. In this world the three-cornered hat does not return "each look's own error". hat1 0.122, hat2 0.083, hat3 0.080 for all STARTS pooled, because the bit switching state between looks is itself spread that the solve splits unevenly (LOOK 1 is the only one with no WAIT before it). For OFF it is just the cloud noise (0.030 / 0.036 / 0.036).
3. r3.tauF is not the fading time. LOOK 3 in the frozen fit is averaged over the other WAIT (for WAIT 60 the other is 240 or 300, for WAIT 300 it is 60 or 240), which flattens the curve: the assumption itself gives about 650 us (255 us is what Runs 1 and 2 measured). MID is very wide (746 +- 460; the bootstrap median is 633) and ON 637 +- 110. Read the shape, not the number.
4. The bite at 240 and 300 us is not pinned (ON 0.050 +- 0.039 and 0.047 +- 0.057; MID 0.063 +- 0.075 and 0.012 +- 0.101). It is the widths of the LOOK 2 / LOOK 3 levels there that carry it.
5. The OFF cloud at LOOK 3 is Run 2's LOOK 2 OFF cloud (one earlier look); no cloud with two earlier looks exists yet. The ON cloud at every LOOK is Run 2's LOOK 1 cloud.
6. WAITS are Run 2's realized values (59.968 / 240 / 299.968 us). Run 3's realized waits are not in the freeze; the differences are microseconds-scale.
7. MID's ON share comes from Run 2's LOOK 1 (0.501), not the 0.52 hinted at in the Run 2 draft (Run 1 had suggested 0.52). Moving it by 0.02 would shift MID levels by about 0.01.
8. Widths are the narrow kind: shot noise plus fit refits. They do not hold the group-to-group spread (Run 1's shared fading time spread across groups was about 4x its bootstrap width). A miss many widths wide means the world was not this one, not that the width was wrong.
9. r3.twin.*.L3mean/g13/V13 predicted values are medians of 500 simulations of a quantity whose expected value is 0 in this world; the median's own Monte Carlo error is about 0.0004.

## Counts
55 r3 quantities in pred_3.json: 53 predicted, 2 NO BASIS, 0 exact identities withheld. Flagged as forced or near-forced (39 distinct rows, the 9 near-identity g13/L3mean pairs sit inside the 27 symmetric zeros): 27 symmetric zeros, 9 replays of Run 2, 3 copied OFF clouds.
