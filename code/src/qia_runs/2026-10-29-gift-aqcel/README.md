# Aqcel on ibm_fez, 24 October 2026

For Toshiaki Kaji, Koji Terashi and Ryu Sawada, from Heuremen LLC. A free calibration of arXiv 2509.04761v4, "Improving initial-state-dependent quantum circuit optimization by introducing state labels", the one-step QPS example.

## What we ran

Your example circuit rebuilt from your published construction, compiled three ways (Qiskit-only, Aqcel-v1, Aqcel-v2), plus a control: the Aqcel-v2 circuit with its CZ gates removed. One job on ibm_fez on 24 October 2026, four copies of each arm, no twirling and no dynamical decoupling, IBM's record unchanged across the job. Readout corrected the same way for every arm.

## What we found

| Arm | CZ (our compile) | fidelity [95 percent] | printed |
|---|---|---|---|
| Qiskit-only | 199 | 0.498 [0.491, 0.506] | 0.46 (246 CZ) |
| Aqcel-v1 | 49 | 0.989 [0.985, 0.992] | 0.99 (48 CZ) |
| Aqcel-v2 | 31 | 0.987 [0.983, 0.990] | 0.99 (36 CZ) |
| Aqcel-v2 with its CZs removed | 0 | 0.314 [0.271, 0.343] | |

Both Aqcel circuits reproduce your 0.99 on fez, and Aqcel-v2 beats its own CZ-removed control by 0.67 [0.64, 0.72], so the fidelity comes from the circuit, not from the support. The gap over Qiskit-only is 0.489 [0.481, 0.497] with our compile (199 CZ) against your printed 0.53 (246 CZ). v1 and v2 differ by 0.002 [-0.003, +0.007], as your text says for this circuit size.

## Three notes from your released outputs (no hardware)

- Table 2's "(0.96)" at threshold 0.05 is the approximation error of the threshold itself: the noiseless fidelity of that v2 circuit is 0.962 (your tutorial prints 0.960 and 0.963), so it is not a hardware loss.
- The readout correction carries about 0.02 of the 0.99: raw Aqcel-v2 reads 0.966 and corrected 0.987.
- With exact control reads our v1 keeps 33 and 18 CX against your 41 and 23, while v2 reproduces yours exactly (25 and 11). The printed v2-over-v1 ratios (61 and 48 percent) may include the noisy control reads in v1. We did not test that.

## What we cannot say

How your own compile date and layout compare with ours. This is one job on one day.

## Files

- results.text: every reading of the job
- desk_notes.text: the three notes from your released outputs, with their numbers
- posthoc.text: the v1 minus v2 reading

The raw counts, IBM's record and our code are yours on request.

Heuremen LLC
"We found it."
