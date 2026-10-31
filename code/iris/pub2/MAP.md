# A Pinned Model Is Not a Stable Tool: where each section's files are

Release for the preprint "A Pinned Model Is Not a Stable Tool: Recounting Published LLM Evaluations From Their Own Files" (K. Indahl,
Heuremen LLC). Third-party files are not redistributed. Each recount fetches them from the authors' own repositories.

Two places hold the files:
- iris/runs/ in this repository (https://github.com/Heuremen-LLC/indahl.ai/tree/main/iris/runs): recounts.zip, study-<arXiv id>.zip,
  frontier.zip, matrix-round-1.zip, matrix-round-2.zip and model-<name>.zip.
- code/iris/pub2/ (this folder): the two-machine bench, its comparison, the checks on our own record, and the referee reports.

| Paper section or table | Files |
|---|---|
| Table "Every recounted paper", and Sections 3 to 5 for each recounted paper | iris/runs/recounts.zip, or iris/runs/study-<arXiv id>.zip for one paper: PLAN.md (committed before the reading), recount.py, outputs, RESULT.md |
| Sections 3 and 5, frontier judge readings computed from released judge files (answer position across vendors, the copy floor, persona abstention) | iris/runs/frontier.zip: PLAN.md, frontier.py, frontier_out.json, RESULT.md |
| Section 6, Table "Our setup, first five models" | iris/runs/matrix-round-1.zip and matrix-round-2.zip (every reply), model-<name>.zip (one model's replies) |
| Section 6, Table "Byte-identical replies out of 170" and the item-by-item flips | faultsbench2_mac_cross/ (the Mac: PLAN.md, run.py, items, score.py, out/), faultsbench2_armature/ (the RTX 3080 machine: the same), seats_compare/ (compare.py, item_flips.py, results.txt, item_flips.txt, setups_20261030.json) |
| Section 7, the same checks on our own record | WITHDRAWALS.md, S1_seat_floor/ and X1_cross_model/ (plans, results and their JSON outputs) |
| Referees | REFEREE_EXT.md (findings about other papers), REFEREE_SEATS.md (the two-machine finding), referee/ (the referees' own check scripts, run against the unzipped recounts) |

The scripts behind S1_seat_floor and X1_cross_model call an internal scanner module that is not released. Their plans, samples and outputs
are here. The record of how the 39 candidate repositories were narrowed to the eleven papers is not in this folder. The paper states the
counts and that the record does not say why 18 of the 39 were not taken forward.

Heuremen LLC
