# Darkwave daily table: tested without IBM

Tested 2 November 2026 (UTC). Nothing was submitted to IBM, deployed, pushed, committed or sent. Run the tests again with `../qvenv/bin/python -I tests/test_pipeline.py` and `python3 -I tests/test_rider.py`. The outputs are in `tests/last_result.txt` and `tests/last_result_rider.txt`. Both end in ALL PASSED.

## What the daily table is

`daily_table.py CHIP` runs one job of the kit's 8 measure circuits on the study's readout pack E (39 qubits) and untouched qubits S (117 qubits) for that chip. The pack comes from `committed_kicks_<chip>.json` in the Darkwave clock folder, which is the same file the 2 November hardware check read. The circuits are built with `darkwave_kit.build` and read with `darkwave_kit.analyse`, both unchanged. Dynamical decoupling and twirling are off, the shots are 4,000, the layout is trivial and the transpiler seed is 31, as in the hardware check.

Without `--fire` it builds and transpiles everything, runs the kit's own checks (layout unmoved, idle and readout arms equal in time on every target), reads the remaining instance seconds and prints one line ending in `remaining N`. With `--fire` it refuses below 600 remaining seconds, saves the job record and the circuits before the job, submits one job, saves the raw arrays, the job record with its usage, the table in the kit's own format (`darkwave_kit.save_table`) and the published JSON.

## Tests on the fake backends

FakeKingston and FakeMarrakesh supply the target (156 qubits, gate durations, dt). The Aer simulator (matrix product state) stands in for the chip. A turn is planted on every target after each readout step, the way `darkwave_kit.py selftest` plants it. Each target gets a random planted turn between -20 and +20 degrees per readout, and six targets get zero.

| Reading | ibm_kingston | ibm_marrakesh |
|---|---|---|
| Study pack in the fake chip's range | 39 readout, 117 targets | 39 readout, 117 targets |
| Dry run submits nothing and passes | yes | yes |
| Refuses at 599 s and when the seconds cannot be read | yes | yes |
| Fires at exactly 600 s: one job, 8 circuits, 4,000 shots | yes | yes |
| Record and circuits on disk before the job | yes | yes |
| Largest error against the planted turn over 117 targets | 0.784 deg | 0.862 deg |
| Raw arrays give the kit table again through `DK.analyse` | all 117 equal | all 117 equal |
| Published JSON `kicks`, `targets`, `readout`, `job_id`, `measured_utc` equal the kit table | yes | yes |
| `.kit.json` download is the kit file byte for byte, sha256 in the published JSON matches | yes | yes |
| `darkwave_kit.py apply --table` accepts the downloaded table and adds 468 rz (4 readouts times 117 targets) | yes | yes |
| Same, on the value that `push_tables.py` would put in KV | yes | yes |

The calibration record in force is read from the QIA mirror's file names (stamp in local time with offset, converted to UTC). The test checks the conversion against the stamp inside the record, read with `qia_check.load`, for the newest five real files. It also checks that every stamp in the run-check manifest's last 20 entries is a stamp in the mirror. The run-check manifest was built at 01:47 UTC and lags the mirror by one record, which does not matter here because `daily_table.py` reads the mirror.

The published JSON carries the record in force at the start of the run, any record stamped during the run, and the newest stamp the mirror held when the table was written. IBM can recalibrate after the newest record the mirror holds. Then the record in force is not in the mirror yet, and the field shows the newest one we have.

## Tests of the route, the push and the page script

`worker_tables.patch` adds two routes after `/darkwave/clock.json`. They serve `/darkwave/tables.js` from the site files and `/darkwave/tables/latest.json`, `/darkwave/tables/<chip>/index.json`, `/darkwave/tables/<chip>/<date>.json` and `/darkwave/tables/<chip>/<date>.kit.json` from KV keys `dwt/...`. The patch applies cleanly to the current `worker.js` (checked with `patch --dry-run`, nothing changed). The route lines were run in node against a stand-in KV holding the dry-run bulk file. Reads of latest, a dated table, the kit file (served with the file name `kick_table_<chip>_<date>.json` as an attachment), the index and a missing day all answer as designed. Five malformed paths and another host are not routed.

`push_tables.py --dry-run` lists seven files for two chips and sends nothing. The real push is one `wrangler kv bulk put`, the way `qia_runcheck/push_index.py` does it.

`tables.js` sets all page text with `textContent`. A table URL outside `/darkwave/tables/` becomes `#`. A hostile job id stays plain text. An empty `latest.json` shows "No table yet." for both chips.

`tick_bus_table.patch` adds one rider line after the clock's. `table_daily.py` was tested with a stub fire script in a temporary folder. It is off without both gates, waits for the clock's marker on that chip until 18:00 UTC, fires once per chip per day, refuses below 600 seconds and pushes once only when `PUSH_ON` exists.

## Dry runs against the real service (read only)

On 2 November 02:10 UTC both chips printed `checks PASS` with durations of 1106 and 2741 dt (ibm_kingston) and 1360 and 3373 dt (ibm_marrakesh) for N = 1 and N = 4, and `remaining 1793`. Nothing was submitted.

## Not applied

The two patches, the `kit.html` fragment (`fragment_tables.html`), the `tables.js` copy into the site tree with its entry in `ledger/copies.json`, the gate files `TABLE_ON` and `PUSH_ON`, and the first fire are all left for the main session.

## 6 Nov 2026: floor lowered to 60 s
FLOOR 600 -> 60 in table_daily.py and daily_table.py (a table costs ~12 s; 600 held back the 4 and 5 Nov tables). Tests moved to the 59/60 boundary; both suites ALL PASSED after the change, and on the old code before it.
