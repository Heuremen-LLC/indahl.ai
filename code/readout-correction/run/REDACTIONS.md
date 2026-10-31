# Redactions in this public copy

The files listed here differ from the files whose hashes were fixed and timestamped before any job (PLAN_KEYSTONE.sha256.text, CODE_KEYSTONE.sha256.text, PREREG_HASHES.text and its OpenTimestamps proof). Only these strings were replaced: local absolute paths (to relative paths or <local>), the name of our IBM Quantum instance (to <our IBM instance>), and the names of two internal folders and our internal catch log. No number, rule, reading or line of logic was changed. The originals are kept and can be shown on request.

| file | replacements | sha256 of this public copy |
|---|---|---|
| LIT_PASS.md.text | 1 | f0e2e9986926b2af6736881a5e89ef6c106667c8177c3bb46cefa6862e9c4b33 |
| PLAN_KEYSTONE.md.text | 4 | 57b3de3d7d5307000877b584cdfba2822b0a83c8758bb715a815b3eea0b671c0 |
| code/committed_kicks.py | 3 | a297b0dfd88d22d3c2e3e9256b4649b9c6bee7cb9dd8268c34126f052c3f6cc3 |
| code/fire_keystone.py | 3 | a66bc5de5f3c2d4b0ed7966a0a7dd1b3de621b908435ec74a66f87434b31ffcd |
| code/free/f1_pooters_offline.py | 3 | 875f436b2283765c1521190c57e1e13f49aa631800c043f124f4ad1867eb3c98 |
| code/free/f2_pauli_by_pauli.py | 3 | edfa9ee67024a72728dfaf8bfef0eac257422625bbdb64923fdf6a766368fd08 |
| code/keystone.py | 2 | 79dd58f6416298b4aaf54437e51b4745d1346222e0431bae6c9a0b9d0fc339cd |
| code/sim_check.py | 3 | f0c432502b211448d5a2a68600c084cc10d455c4f63475b8540f7dd247f12b82 |
| code/unwrap_kicks.py | 2 | 5026761bab509100f04ae1ef045e27f28fba3912cab838594377df0c2b2bc8fb |

## Second pass, 31 Oct 2026
Further strings replaced in code/pooters.py: names of other runs in our queue and an internal record path (no number, rule or logic changed). sha256 of this public copy now: 8cf8c43357d08079a3db4898566964e78bfa5f71e94d9aa3c1d3e365c3de12db
