# AS-SQD on ibm_pittsburgh, with a no-gate control

For Rinka Miura, from Heuremen LLC. A free calibration of arXiv 2603.13536v1, "Active Sampling Sample-based Quantum Diagonalization from Finite-Shot Measurements".

## The line it answers

Your abstract: "we validate the inherent robustness of our approach against real-world state preparation and measurement (SPAM) errors using physical samples directly from an IBM Quantum processor", and AS-SQD "consistently achieves substantially lower median absolute energy errors than standard SQD and random expansion".

## What we ran

Your hardware counts, dates and layout are not released, so we used the construction your code releases (build_2.py): a Hadamard layer, then a Lie-Trotter step at t = 0.6 (2,400 shots) and t = 1.2 (600 shots), merged into one 3,000-shot sample. We ran it at n = 12 on ibm_pittsburgh on 24 October 2026, on a 12-qubit ring of the chip so the periodic chain needs no SWAPs, for 10 field instances (your seeds 100 to 104 and five more). Beside each Trotter circuit we ran a control: the same Hadamard layer and straight to measurement, with no entangling gate and no evolution, also 3,000 shots. Your solver settings (K = 50, B = 20, T = 10) went into our own implementation of AS-SQD. Before reading anything of ours, our Hamiltonian matched the one your code builds to 4e-15 (known_good.text, with our solver's simulated errors beside it; your figures are plots, so there is no printed number to match).

## What we found

Log10 energy error, averaged over the 10 instances, 97.5% intervals (negative means AS-SQD lower):

| Reading | Value |
|---|---|
| AS-SQD minus random expansion, hardware Trotter samples | -0.930 [-1.208, -0.653] |
| AS-SQD on Trotter samples minus AS-SQD on the no-gate control | -0.112 [-0.378, +0.154] |
| AS-SQD minus random expansion, no-gate control samples | -0.792 [-1.008, -0.576] |

1. Your hardware claim holds here: AS-SQD beats random expansion by about a factor of 8.5 on hardware samples at n = 12 (median error 0.90 against 9.15), and standard SQD by about 20.
2. The same margin appears on the control samples, which come from a circuit with no entangling gate. Within our bound (a factor of 2.4 better to 1.4 worse), the Trotter circuit's samples help AS-SQD no more than near-uniform samples do. A classical uniform draw, with no hardware at all, gives the same.
3. Without any hardware, the noiseless version of the released circuit has the same overlap with the ground state as a uniform draw (0.00020 to 0.00036, against 0.00024 for uniform). At these Trotter times the circuit carries no ground-state information even before noise.
4. A second, identical job a few minutes later agreed (-0.847 on the first reading).

## What this adds to your paper

The gain is real and it is AS-SQD's own: its physics-guided expansion finds the low-energy sector from an almost arbitrary start set. That is a strong result for the method. The hardware experiment, as released, does not test what the abstract says it tests, because the samples carry no more information than uniform strings. A no-gate control beside each circuit, and a state preparation that concentrates weight near the ground state, would let the hardware samples show whether they help.

## What we cannot say

- Anything about your own hardware run. Your counts, Trotter times, layout and dates are not released, so this is your released construction, not your samples.
- How the picture changes at other sizes or Trotter times.

## Files

- results_job1.text, readings_job1.json: every instance and reading
- results_job2.text: the second, identical job
- known_good.text: our Hamiltonian against yours, and our solver's simulated errors

IBM's record and our code are yours on request.

Heuremen LLC
"We found it."
