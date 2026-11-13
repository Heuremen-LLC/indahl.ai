# FF-ZNE on ibm_fez: is the layout score a straight-line carrier?

For Debarthi Pal and Yogesh Simmhan, from Heuremen LLC. A free calibration of arXiv 2603.13949, "Folding-Free Zero-Noise Extrapolation by Layout-induced Noise".

## The line it answers

Your paper: under a depolarizing noise model "the resulting extrapolation admits a fixed linear form", and "linear extrapolation remains effective" under twirled noise. FF-ZNE then extrapolates the delivered value along the layout error score to a score of zero.

## What we ran

On ibm_fez on 25 October 2026: the 50-qubit QIC circuit (r = 1, ideal <Z> = 1) from your released notebook zne_vqe_50qubits_reps_123_HW.ipynb, with your options (resilience 0, TREX, gate twirling, DD XY4, 10,000 shots) and your cost function, scored on the record saved before the job. Your selection rule picked three layouts on fez: best (score 0.205), the equidistant middle (0.373) and worst (0.541). We added two more from the same scored list, at 0.262 and 0.381, so five layouts in one job. Every layout compiles to 49 CZ. The best layout ran twice in the same job and the two agreed (0.8665 and 0.8660, standard error 0.0012 each), which is our check that the setup reads the same thing twice.

## What we found

Delivered <Z> by layout, with your score:

| Layout | Score | <Z> |
|---|---|---|
| Best | 0.205 | 0.866 |
| Added | 0.262 | 0.849 |
| Middle | 0.373 | 0.811 |
| Added | 0.381 | 0.840 |
| Worst | 0.541 | 0.776 |

1. The score is not a straight-line carrier of the delivered value on fez. A weighted line through the five layouts misses by chi-squared 152 on 3 degrees of freedom.
2. Two layouts with almost the same score (0.373 and 0.381) delivered 0.811 and 0.840. That is 0.031 away from what the line predicts, 12 standard errors. Which qubits carry the circuit moves the result at a fixed score.
3. FF-ZNE with your three layouts gives 0.922 (standard error 0.002), 7.8% from ideal, from 0.866 raw on the best layout. Your notebook's torino run of the same circuit: 0.933 raw, 0.967 with FF-ZNE. Different chips, so this is context, not a contradiction.
4. Looked at after the data: two other choices of three from the same five layouts give 0.896 and 0.916, against 0.922 from yours. The choice of layouts moves the mitigated answer by up to 0.026, about a third of what is left after extrapolation.
5. Drift was small beside these: the best layout about one minute later, in a second job, read 0.858 against 0.866.

## What this adds to your paper

Your linear form holds when the layouts differ only in how much noise they carry. On fez on this day they also differed in which qubits carry the noise, and the score did not capture that. Running four or five layouts instead of three, and testing the line before extrapolating, would flag a day like this one. The spread over triples gives the mitigated value an honest width.

## What we cannot say

- Which term in the score misranks the layouts (two-qubit gate, readout or idle error). Five points cannot separate them.
- Anything about torino, which we did not run.
- More than one session on one chip. The layouts also differ a little in depth (158 to 166).

## Files

- results_ffzne.json: every reading, with standard errors, fits and outcomes
- layouts.json: the five layouts and their scores
- raw_expectation_values.json: the delivered <Z> per layout

IBM's record and our code are yours on request.

Heuremen LLC
"We found it."
