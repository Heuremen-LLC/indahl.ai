# TILE 8 SPACINGS RUN -- 2026-09-30 -- DRY, NOT ATTEMPTED

## Step 0: budget check (read-only, via QiskitRuntimeService(channel='ibm_quantum_platform').usage())

Checked with the venv the parallax scripts actually use (`~/bones-forge/venv_quantum`, qiskit-ibm-runtime 0.49.0),
same account-loading pattern as `parallax_ibm.py chip()`.

| key name | usage_remaining_seconds |
|---|---|
| ibm_quantum_key | 0 |
| ibm_quantum_key_2 | 0 |
| ibm_quantum_key_3 | 4 |
| ibm_quantum_key_4 | 14 |
| ibm_quantum_key_parallax | 4 |

Threshold for this run: at least 40 s on some key. Best available (key_4) has 14 s. **No key qualifies.**

## Result

STOPPED at Step 0 per instructions. No circuits built, no PREREG_TILE8.md written, no job submitted,
no QPU seconds spent. The tile-8 alias-pinning run (Fez +44,441.66 Hz + n*100kHz / Kingston 106.39 Hz + n*100kHz,
five shot spacings, random groups-of-three) is designed but not executed. Re-run Step 0 once a key crosses
the 40 s bar (28-day rolling windows reset per-key on their own schedules -- do not guess a refill date).
