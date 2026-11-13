# Your Var C2 readout on ibm_kingston, without error mitigation

For Dhritimalya Roy, from Heuremen LLC. A free calibration of arXiv 2608.04486v3, "State-resolved quantum-information fingerprints of partial dynamical symmetry in the interacting boson model".

## The line it answers

Your paper: on ibm_kingston at resilience level 2 (TREX and zero-noise extrapolation), the mixed state gives Var C2 = 236 ± 78 and the solvable state 36 ± 136, and "the direct mixed−solvable difference is resolved only at ∼1.3σ". You also write that a device evaluation is still "illustrative" rather than "compelling".

## What we ran

On ibm_kingston on 24 October 2026, one EstimatorV2 job of 88 seconds: the same two states on your physical qubits (solvable on 73, 79, 72, 74; mixed |0000> on 148, 60, 47, 21), the same operators C2 and C2², 4,000 shots per basis as yours, but at resilience level 0: no TREX, no extrapolation. The states and operators come from our own rebuild of your model, which gives your exact values (240 and 0). Before reading anything of ours, your released job results went through our code and gave your printed 236 ± 78, 36 ± 136 and 1.28 sigma.

## What we found

| | Ours, resilience 0 | Yours, resilience 2 | Exact |
|---|---|---|---|
| Var C2, mixed | 243.8 ± 19.3 | 236 ± 78 | 240 |
| Var C2, solvable | 123.9 ± 35.1 | 36 ± 136 | 0 |
| Mixed minus solvable | 120.0 ± 40.1 | 200 (1.28 sigma) | 240 |

Without mitigation the hardware separates the two states: the difference is 120, 95% interval 41 to 199, about 3 sigma, in one 88-second job. The estimator does not return the correlation between the two moments, so we also took both extremes. The worst case gives 12 to 228, still above zero.

The price is bias. The solvable arm reads 124, not 0. That arm carries all the two-qubit gates (16 in our compile, 15 in yours), and the mixed arm |0000> carries none, so gate noise lands on the solvable state only and pulls its variance up from zero. That is the gap between our 120 and the exact 240. Your extrapolation removes most of that bias (36 is close to 0) but widens the solvable error bar to 136, which is what holds your difference at 1.3 sigma.

## What this adds to your paper

The separation your paper calls illustrative is there on kingston at resilience 0, at about 3 sigma, with a bias that pointed the conservative way on this run: gate noise pulled the solvable state toward the mixed one, so our 120 understates the separation. Running both levels side by side, as a pair, gives a resolved difference from one and a debiased point estimate from the other. Giving the mixed state a circuit with the same number of two-qubit gates as the solvable one would put the gate noise on both arms equally.

## What we cannot say

- What makes the noise. We name no mechanism.
- How large the effect was on 7 October, your run date. This is one job on 24 October.

## Files

- results_res0.json: every moment and its standard error, the difference and both correlation bounds
- known_good.text: your printed numbers recovered from your released job results

IBM's record for the job and our code are yours on request.

Heuremen LLC
"We found it."
