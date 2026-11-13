# QIA-2026-001: IBM

Heuremen LLC · Quantum Idle Audit · 22 October 2026

The case statement (`QIA-2026-001.pdf`) lists 19 places where the IBM Heron processors ibm_fez, ibm_kingston, ibm_marrakesh and ibm_phoenix delivered something different from IBM's own stated calibration figures, measured by the same definition, in the same job, against IBM's calibration record saved when each job ran.

## Contents

- `QIA-2026-001.pdf`: the case statement.
- `ibm_calibration_records/`: IBM's published calibration records (backend properties) as saved at the moment each job was fired, named by run folder.
- `inputs/fleet_records.jsonl`: IBM's daily calibration medians for six processors, read 6 Oct 2026 (items 13 and 14).
- `scripts/`: the scripts that compute every line item; `outputs/`: their printed results.

## Raw shot data

The jobs, raw results, plans and analysis scripts behind every measurement are published at https://heuremen.org/experiments/ and in the data release doi:10.5281/zenodo.23169755. Scripts here read those files by their original paths (`bones-forge/arxiv_one_readout/...`); point the paths at a copy of that release to rerun.

## Method

Same quantity, same definition, same job, against IBM's calibration record saved when the job ran. Medians over qubits, 95 % bootstrap intervals (2000 resamples). A deviation is listed only when IBM's figure falls outside our interval or bound.

Heuremen LLC
“We found it.”
