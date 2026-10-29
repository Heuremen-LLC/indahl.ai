# Code

Scripts behind the tables on indahl.ai. Free to read, run and cite with attribution. See LICENSE.txt in the repository root.

- `sad/` builds and checks the Stated against Delivered sources, one claims checker per source.
- `iris/` holds the Faults and Guards bench (items, runner, scorer), the Falcon training plan and scripts, and the model claims round for SmolLM2.
- `coin/` collects block records from public explorers, recomputes block hashes from header fields, and checks a chain's stated claims against its own record. It reads public data only.
- `mirror/` mirrors the calibration IBM publishes and audits each record against itself, with an independent recount script.
- `t1t2-check/` measures T1 and a Hahn echo T2 together on chosen qubits with your own IBM account and compares the ratio with 2. It prints the estimated QPU seconds first and does not submit without --yes.
- `*/history.jsonl` in each live corner's folder (and `mirror/audit_history.jsonl`, `mirror/ibm_history.jsonl`) is one row of that corner's published numbers every few hours, added only when something changed. Each commit is a point on the trend.

Each plan file is committed before the run it describes. Run any script with `python3 -I` from its own folder.
