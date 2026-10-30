# Your ten-graph ZNE batch on ibm_fez: the between-job term, measured

For Vicenzo Scavino Alfaro, from Heuremen LLC. A free calibration of arXiv 2605.08251v2, "A finite-shot mean-squared-error boundary for Richardson zero-noise extrapolation".

## The line it tests

Your hardware section: the interval "reflects shot noise within each job rather than drift between jobs".

## What we ran

Your ten held-out MaxCut graphs at noise scales 1 and 3 (20 circuits), rebuilt from your published construction (seeds 606 to 1506) without running your code, matching your gate counts in 20 of 20, 4000 shots, on ibm_fez on 25 October 2026. Six jobs: a full pass P1, then the same circuits split so each job carries one noise scale (scale 1 then 3, then 3 then 1), then a full pass P2, about three minutes after P1. IBM's calibration record was saved before every job. Your runs were on ibm_marrakesh, which was in maintenance that week, so we used ibm_fez: the same coupling map and the same physical qubits 0 to 4. Before reading anything of ours, your raw counts went through our code and gave your published numbers exactly: MAE 0.06445 before ZNE, 0.02810 after, 9 of 10 graphs improved.

## What we found

| Reading | Value [95 percent] | Shot-noise null | Outcome |
|---|---|---|---|
| Unmitigated MAE, second pass minus first | -0.0159 [-0.0235, -0.0088] | [-0.0075, +0.0073] | drift present |
| ZNE gain, second pass minus first | +0.0075 [+0.0023, +0.0130] | [-0.0052, +0.0053] | the gain moved |
| Largest job-to-job change in the ZNE estimate (mean over graphs) | 0.0384 [0.0296, 0.0483] | [0.0072, 0.0196] | above shot noise |

The gain was 0.0231 in the first pass and 0.0306 in the second. ZNE improved 7 of 10 graphs in the first pass and 10 of 10 in the second, on the same circuits three minutes apart (your batch: 9 of 10). The largest job-to-job change in the ZNE estimate is 1.06 times your published gain of 0.03635. Shot noise alone gives about 0.35 times.

## What this adds to your paper

On the day we measured, drift between jobs minutes apart was the same size as the gain you report, so an interval that leaves out the between-job term can be narrower than the spread a repeat would show. A cheap fix is to interleave passes (P S S P, as here) and print the spread between passes beside the gain. Your boundary result is about the finite-shot variance inside one job. This is the term that sits outside it.

## What we cannot say

How large the between-job term was on ibm_marrakesh on your dates. This is one day on ibm_fez. We did not touch your theory.

## Files

- results_fez_25oct.text: every reading, with the shot-noise nulls
- known_good.text: your published numbers recovered from your raw counts
- RESULT.md.text: the summary we wrote when the run landed

The raw counts of all six jobs, IBM's records and our code are yours on request.

Heuremen LLC
"We found it."
