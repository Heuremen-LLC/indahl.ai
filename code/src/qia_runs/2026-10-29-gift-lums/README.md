# Your first batched job on ibm_fez, repeated on two days

For Muhammad Faryad, from Heuremen LLC. A free calibration of arXiv 2609.13669v1, "Batched pattern search for QAOA parameter optimization on cloud-accessed quantum hardware".

## The line it answers

Your paper: "The drift control of Sec. VI is a single paired repeat per instance, which cannot separate drift from shot noise; it bounds the effect at a few hundredths of a CVaR unit and no more than that."

## What we ran

Your first batched job (bps1: your parameter rows, your shots per row) for n = 8 (13 rows x 1102 shots) and n = 10 (17 rows x 2168 shots), on your chains on ibm_fez, twelve jobs per day in the order T O O T T O O T T O O T, on 24 October and again on 29 October 2026 with the same compiled circuits. T jobs use your settings (dynamical decoupling, Pauli twirling of gates and measurement), O jobs turn twirling off. IBM's calibration record was saved before every job. Before reading anything of ours, your released counts went through our code and gave your numbers, and the compiled circuits match your gate counts (252, 72, 334 and 540, 120, 548).

## What we found

Spread of the job means, against the shot noise of a job:

| | 24 October | 29 October |
|---|---|---|
| n = 8, twirling off | 0.326, beyond shot noise | 0.017, within shot noise |
| n = 8, your settings | 0.048, beyond shot noise | 0.027, within shot noise |
| n = 10, twirling off | 0.012, within shot noise | 0.012, within shot noise |
| n = 10, your settings | 0.017, within shot noise | 0.026, cannot tell (the two halves of the day disagree) |

Your single-pair shifts (+0.0426 at n = 8, -0.0499 at n = 10) are consistent with the spread on every day and size.

On 24 October the untwirled n = 8 spread was one step: one job read -2.835 and the five later untwirled jobs read -1.97 to -2.10, the first of them 25 seconds later under the same calibration record. On 29 October nothing like it appeared.

Beside these, and only as context: the mean CVaR over each arm's six jobs moved between our two days by +0.40 (n = 8, your settings), -0.90 (n = 8, twirling off), +0.07 and +0.36 (n = 10).

## What this adds to your paper

Job-to-job drift beyond shot noise came on one day and not on the next, at the same size n and the same settings. So a single paired repeat on one day bounds that day only. And the arm means moved between days by tenths of a CVaR unit, which is the scale your "Sequential arms" paragraph warns about when two arms run at different times. Interleaving the two arms job by job (T O O T, as here) keeps both effects out of the comparison for the cost of a few more jobs.

## What we cannot say

How large the drift was on your dates, or what caused the 24 October step (a coherent-error change, a control glitch and a readout-assignment change all fit). These are two days on ibm_fez.

## Files

- results_24oct.text, results_29oct.text: every reading of each day, with the shot-noise nulls
- known_good.text: your published numbers recovered from your released counts

The raw counts of all 24 jobs per day, IBM's records and our code are yours on request.

Heuremen LLC
"We found it."
