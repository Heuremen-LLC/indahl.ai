# Your ibm_kingston gap, with the calibration held fixed

For Neilson Carlos Leite Ramalho, Higor Amario de Souza, Anthony Accioly, Valter Vieira de Camargo and Marcos Lordello Chaim, from Heuremen LLC. A free calibration of arXiv 2609.33255v1, "N×M-Version Programming for Quantum Software: High-Level Components across Frameworks and Engines".

## The line it answers

Your paper: "Repeating the batches showed that the ibm_kingston result did not hold." Then: "three later batches, each on a new calibration and a different set of qubits, removed the gap", and the results "do not establish stability across calibrations".

In your released files, your seven kingston batches ran on three qubit sets, each under its own calibration record. Set A (138, 151, 152, 153) is batch 0, set B (140 to 143) is batches 1 to 3, set C (82, 83, 96, 103) is batches 4 to 6. The Qiskit lead over PennyLane is there on A and B and gone on C. So "a new calibration removed the gap" and "a different set of qubits removed the gap" cannot be told apart from those batches.

## What we ran

On ibm_kingston on 24 October 2026: your exact submitted circuits (60 of them, rebuilt from your manifests and checked equal to them), the Qiskit, PennyLane and Cirq controls on cases 10, 11, 0111 and 0110, on all three sets, in one job. One job means one calibration for every comparison. A second job ran the same circuits in reverse order. 2048 shots per circuit. Before reading anything of ours, your released counts went through our code and gave all 16 cells of your Table II and your 0.16 gap (we get +0.159).

## What we found

Qiskit minus PennyLane, averaged over your two four-qubit cases, 99% intervals:

| Set | Your batches | Qiskit minus PennyLane |
|---|---|---|
| A | 0 | +0.068 [+0.047, +0.087] |
| B | 1 to 3 | +0.043 [+0.024, +0.063] |
| C | 4 to 6 | -0.035 [-0.055, -0.015], PennyLane ahead |

The two jobs agree on every set. With the calibration held fixed, sets A and B carry the Qiskit lead and set C does not: A minus C is +0.102 [+0.074, +0.131]. The qubit set, with the placement your circuits carry for it, reproduces the split in your batches on a single calibration. A change of calibration is not needed to explain it.

Beside this, from a short benchmark we ran on your 12 qubits before and after the jobs: our two readings disagree on which set has the best two-qubit gates (best first: before the jobs C, A, B; after them A, B, C). The gap pattern (A, then B, then C) follows neither, so "the best-calibrated set shows no gap" is not supported on this day. On set B, IBM's record stated two couplers at 5.8e-3 and 6.6e-3, and we measured 1.7e-3 to 2.1e-3.

## What this adds to your paper

The gap that "did not hold" is a property of where the circuits ran, not only of when. Comparing builders on one qubit set at a time, or interleaving the sets inside one job as here, keeps the qubit set out of the builder comparison.

## What we cannot say

- Which part of "set" does it: the physical qubits, or the builder-specific routing your circuits carry for each set. Your logical circuits re-transpiled onto all three sets with one routing seed would separate the two.
- How large the effect was on your dates.

## Files

- results_usp.text: every reading, with a legend
- known_good.text: your Table II recovered from your released counts

The raw counts of both jobs, IBM's records and our code are yours on request.

Heuremen LLC
"We found it."
