# Queue against wait, Note 1 analysis

Rule: PLAN.md Note 1, read at run level per Note 2. Script: analyze_queue_wait.py. Numbers: analysis.json.

Readings 1793270795..1794421916 (epoch), 29 Oct to 11 Nov 2026. Jobs 796: joined 600, dropped 196 (no reading in the 90 min before created, mostly jobs made before the readings began on 29 Oct).

Wait = time from created to running in IBM's job record (wait_s). Pending = IBM's pending count of that processor at the last reading before created. Bootstrap 4,000 resamples, seed 7. Pending span = max/max(min,1), since several processors read 0.

Runs: jobs.jsonl has no run id. A run is defined here as consecutive jobs on one processor with gaps of 30 minutes or less (assumption, not in the plan). Many jobs are single-job hourly probes, so runs are close to jobs on some processors and the two intervals nearly match.

| processor | joined | dropped | runs | rho | job-level 95% | run-level 95% | outcome (run level) |
|---|---|---|---|---|---|---|---|
| ibm_boston | 37 | 4 | 37 | 0.44 | [0.12, 0.67] | [0.12, 0.67] | CANNOT_TELL |
| ibm_chicago | 36 | 1 | 36 | 0.76 | [0.55, 0.87] | [0.55, 0.87] | ABOVE |
| ibm_fez | 97 | 79 | 82 | 0.59 | [0.42, 0.72] | [0.34, 0.79] | ABOVE |
| ibm_kingston | 139 | 76 | 95 | 0.48 | [0.34, 0.59] | [0.26, 0.65] | CANNOT_TELL |
| ibm_marrakesh | 135 | 7 | 93 | 0.47 | [0.30, 0.62] | [0.26, 0.63] | CANNOT_TELL |
| ibm_phoenix | 72 | 2 | 72 | 0.02 | [-0.22, 0.26] | [-0.22, 0.26] | CONSISTENT |
| ibm_pittsburgh | 84 | 27 | 83 | 0.60 | [0.46, 0.71] | [0.47, 0.70] | ABOVE |

Kingston: job-level reads ABOVE, run-level lower bound 0.26 so CANNOT_TELL (run level governs).
Cadence note: readings moved from every 9 ticks to every 2 ticks (about 12 min); same rule, denser series, used as is.
This is a statement about our jobs only.

## Sensitivity to the run gap (added after the first reading)
The plan defines no run. The 30 minute gap above was chosen at analysis time. Run-level interval and outcome at other gaps:

| processor | gap min | runs | run-level 95% | outcome |
|---|---|---|---|---|
| ibm_boston | 10 | 37 | [0.12, 0.67] | CANNOT_TELL |
| ibm_boston | 30 | 37 | [0.12, 0.67] | CANNOT_TELL |
| ibm_boston | 60 | 35 | [0.12, 0.67] | CANNOT_TELL |
| ibm_boston | 120 | 25 | [0.06, 0.68] | CANNOT_TELL |
| ibm_boston | 240 | 21 | [0.01, 0.69] | CANNOT_TELL |
| ibm_chicago | 10 | 36 | [0.55, 0.87] | ABOVE |
| ibm_chicago | 30 | 36 | [0.55, 0.87] | ABOVE |
| ibm_chicago | 60 | 34 | [0.55, 0.87] | ABOVE |
| ibm_chicago | 120 | 25 | [0.49, 0.87] | ABOVE |
| ibm_chicago | 240 | 11 | [0.43, 0.86] | ABOVE |
| ibm_fez | 10 | 83 | [0.38, 0.77] | ABOVE |
| ibm_fez | 30 | 82 | [0.34, 0.79] | ABOVE |
| ibm_fez | 60 | 72 | [0.34, 0.79] | ABOVE |
| ibm_fez | 120 | 50 | [0.40, 0.80] | ABOVE |
| ibm_fez | 240 | 34 | [0.41, 0.80] | ABOVE |
| ibm_kingston | 10 | 106 | [0.27, 0.63] | CANNOT_TELL |
| ibm_kingston | 30 | 95 | [0.26, 0.65] | CANNOT_TELL |
| ibm_kingston | 60 | 84 | [0.27, 0.65] | CANNOT_TELL |
| ibm_kingston | 120 | 57 | [0.27, 0.68] | CANNOT_TELL |
| ibm_kingston | 240 | 33 | [0.25, 0.68] | CANNOT_TELL |
| ibm_marrakesh | 10 | 103 | [0.28, 0.63] | CANNOT_TELL |
| ibm_marrakesh | 30 | 93 | [0.26, 0.63] | CANNOT_TELL |
| ibm_marrakesh | 60 | 79 | [0.23, 0.65] | CANNOT_TELL |
| ibm_marrakesh | 120 | 57 | [0.24, 0.66] | CANNOT_TELL |
| ibm_marrakesh | 240 | 31 | [0.25, 0.66] | CANNOT_TELL |
| ibm_phoenix | 10 | 72 | [-0.22, 0.26] | CONSISTENT |
| ibm_phoenix | 30 | 72 | [-0.22, 0.26] | CONSISTENT |
| ibm_phoenix | 60 | 66 | [-0.22, 0.26] | CONSISTENT |
| ibm_phoenix | 120 | 53 | [-0.23, 0.25] | CONSISTENT |
| ibm_phoenix | 240 | 36 | [-0.29, 0.30] | CONSISTENT |
| ibm_pittsburgh | 10 | 83 | [0.47, 0.70] | ABOVE |
| ibm_pittsburgh | 30 | 83 | [0.47, 0.70] | ABOVE |
| ibm_pittsburgh | 60 | 72 | [0.46, 0.71] | ABOVE |
| ibm_pittsburgh | 120 | 51 | [0.46, 0.71] | ABOVE |
| ibm_pittsburgh | 240 | 36 | [0.46, 0.71] | ABOVE |

Processors whose outcome changes across gaps: none.
