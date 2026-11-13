# Your noise model and ibm_fez: the calibration-data term, measured

For Stefan Raimund Maschek, Jürgen Schwitalla, Maja Franz and Wolfgang Mauerer, from Heuremen LLC. A free calibration of arXiv 2506.03636, "Make Some Noise! Measuring Noise Model Quality in Real-World Quantum Software". No new hardware time was used for it. It comes from runs we had already made.

## The number you left open

Your Section IV: "The half-value interval of the gain ratio is ≈ 220 2-qubit gates throughout all simulated results. On real hardware this interval is smaller with ≈ 180 2-qubit gates". And: "Systematic uncertainties due to the inaccuracy in the calibration data have not yet been considered and are subject to future studies."

## What we measured on ibm_fez

Randomized benchmarking on every qubit and every CZ edge of ibm_fez, two jobs on 23 October 2026 (21:04 and 21:28 UTC), both under IBM's record stamped 16:07:42 EDT that day. Delivered error over the error IBM's record states, median over the chip with a 95 percent interval over qubits or edges:

| | job dbdsnpom94ac738qs3sg | job dbdt36ngdj9s73fkr4mg |
|---|---|---|
| CZ layer, 172 of 176 edges | 1.244 [1.191, 1.303] | 1.269 [1.206, 1.338] |
| single-qubit pulse, 156 qubits | 1.450 [1.367, 1.534] | 1.417 [1.336, 1.528] |

The same kind of run on seven IBM processors on 23 and 24 October read delivered above stated in 28 of 28 readings (CZ 1.18 to 1.62).

## What it does to your half-value

If the two-qubit error carries the decay of the gain ratio, the half-value scales as 220 divided by the factor: 220 / 1.244 = 177 and 220 / 1.269 = 173 gates, and 164 to 185 across the intervals. Your hardware value of about 180 sits inside that range. If single-qubit, readout or relaxation terms carry part of the decay, the shift from the two-qubit factor alone is smaller and the single-qubit factor (about 1.4) adds to it.

## What we cannot say

Your runs predate June 2025 and ours are from October 2026, so this is the size of the correction on the dates we measured, not a reading of your dates. We did not rebuild your noise model or your circuits.

## Files

- README.md (this file)
- fez_23oct_job1.text, fez_23oct_job2.text: the printed readings for the two fez jobs

Heuremen LLC
"We found it."
