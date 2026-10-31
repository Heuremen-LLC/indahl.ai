# A Readout's Kick Is a Turn: data, code and preregistration

## The experiment

A mid-circuit readout of a 39-qubit pack shifts the phase of nearby untouched qubits. A per-qubit virtual-Z correction from a table measured minutes earlier gives most of it back on both chips. A table measured ten days earlier did so on ibm_kingston and over-corrected on ibm_marrakesh. On 31 October 2026, on ibm_kingston and ibm_marrakesh, six arms were run on 117 untouched qubits, 48 Bell pairs and a three-qubit clock: idle, idle plus echo, readout, readout plus the 21 October correction table, readout plus a table measured minutes earlier, readout plus echo.

Spectator kick, readout minus equal idle, degrees per readout: kingston -2.4240 [-3.9835, -1.9317] BELOW, marrakesh -1.6830 [-2.3377, -1.0173] BELOW.
Share given back, against 0.5, old table then fresh table:
- Kingston spectators +0.9221 [+0.8734, +0.9479] ABOVE and +0.9281 [+0.8738, +0.9538] ABOVE. Pair phase +0.9266 [+0.8362, +0.9627] and +0.9619 [+0.9175, +0.9749], both ABOVE. Clock +0.7591 [+0.7344, +0.7840] and +1.0007 [+0.9965, +1.0047], both ABOVE.
- Marrakesh spectators +0.2426 [-0.1420, +0.4365] BELOW and +0.7952 [+0.6656, +0.8764] ABOVE. Pair phase +0.3958 [+0.1553, +0.6416] CONSISTENT and +0.9167 [+0.8310, +0.9605] ABOVE. Clock -0.5118 [-1.1330, -0.0918] BELOW and +0.7703 [+0.6458, +0.8819] CANNOT_TELL (the two copies disagree).

Source: run/results/results_keystone_ibm_kingston.text and run/results/results_keystone_ibm_marrakesh.text.

## Folder map

- [run](run/): the 31 October run with plan, code, data (raw .npz arrays, .qpy circuits, correction tables), records and results.
- [earlier_runs](earlier_runs/): the 24 October runs and the two probe runs, each with its own plan, code, raw data and REDACTIONS.md.
- [for-page-wootters-field](for-page-wootters-field/), [for-santos-uzdin](for-santos-uzdin/), [for-chu-et-al](for-chu-et-al/), [for-kumar](for-kumar/), [for-krinner-et-al](for-krinner-et-al/): one README per research group, with links into run and earlier_runs and no copies.

## Verify the preregistration

- run/PLAN_KEYSTONE.sha256.text holds the sha256 of the plan.
- run/CODE_KEYSTONE.sha256.text holds the sha256 of the code and the two committed kick tables.
- run/PREREG_HASHES.text collects both with the repository commit 0663d84d2ef75f7e816746ee1086f384fad79455 of 2026-10-31T19:07:04Z. The first job was created at 19:07:40Z (run/records).
- run/PREREG_HASHES.text.ots is its OpenTimestamps proof. Check it with the ots client.
- A few public files differ from the hashed originals by redactions of local paths, our IBM instance name and internal labels. [run/REDACTIONS.md](run/REDACTIONS.md) lists them with the hash of each public copy. The originals are kept and can be shown on request.

## The 21 October table

The correction table used in the old-table arm comes from the public control run at https://github.com/Heuremen-LLC/heuremen.org, path experiments/2026-10-21-control-run.

## License

See [LICENSE.txt](../../LICENSE.txt): free to download, read and cite with attribution to Heuremen LLC, all other rights reserved, no text and data mining or AI training.

Heuremen LLC
