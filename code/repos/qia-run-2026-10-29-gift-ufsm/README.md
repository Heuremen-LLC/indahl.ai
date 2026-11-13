# Your Fig 8 on ibm_kingston, with and without dynamical decoupling

For Victor P. Brasil, Diego S. Starke and Jonas Maziero, from Heuremen LLC. A free calibration of arXiv 2502.01824v3, "Digital quantum simulation of bosonic systems and quantum complementarity".

## What we ran

Your Fig 8(a) and 8(b) circuits, rebuilt from your published construction and checked in a noiseless simulator, on ibm_kingston on 24 October 2026, on the qubit pair 81 and 82. Before reading anything of ours, your released Fig 8 counts went through our code and gave your numbers: deficit (a) 1.245 pp, (b) 4.673 pp, extra deficit from the measure-and-reset blocker 3.428 pp. We ran two copies with dynamical decoupling off, then one job with XY4 on and one with it off, the same transpiled circuits in all four jobs.

## What we found

| Setting | deficit (a) | deficit (b) | extra deficit (b) - (a) | against your 3.428 pp |
|---|---|---|---|---|
| DD off (three jobs) | 2.09 to 2.29 pp | 51.8 to 52.0 pp | +49.7 pp | far above |
| DD on, XY4 | 2.63 pp | 6.60 pp | +3.97 +- 0.23 pp | consistent |

With XY4 the run gives your extra deficit back (3.97 against 3.43 pp). With dynamical decoupling off, mode A idling through mode B's mid-circuit measure and reset loses the correlation the interferometer needs. The (b) outcomes spread over 000, 001, 100 and 101 at about a quarter each, while with XY4 they return to your 001 and 100 pattern (0.452 and 0.483). Your notebook's sampler option cell for Fig 8 is commented out, so the setting your run used is not on record. Your Fig 8 is consistent with a run that had dynamical decoupling on.

With XY4 on, the measure and reset still costs 3.06 +- 0.24 pp beyond the extra readout it adds, which answers the question your figure raises: the blocker costs more than its readout.

## What we cannot say

Which part of the idle the echo protects, and whether your undated Fig 8 run used it. This is one pair on one day.

## Files

- results_dd_off.text, results_dd_on_off.text: every reading of both runs

The raw counts of all four jobs, IBM's records and our code are yours on request.

Heuremen LLC
"We found it."
