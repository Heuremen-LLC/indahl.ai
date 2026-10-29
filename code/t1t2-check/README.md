# T1 and T2 together: check IBM's published pair

IBM publishes T1 and T2 for each qubit in one calibration record, but the two can be measured on different days. Physics keeps T2 at or below 2 x T1.
Our audit at https://indahl.ai/qia lists qubits where the published pair breaks that. This script measures T1 and a Hahn echo T2 on the same qubit in one job and tells you whether the ratio is really above 2.

Read PLAN.md first. The rules were committed before the code.

## Run it

```
pip install -r requirements.txt
python3 run_check.py --selftest                       # no device, about a minute
python3 run_check.py --flagged                        # lists what the audit flags right now
export IBM_QUANTUM_TOKEN=...                          # your own IBM Quantum Platform API key
export IBM_QUANTUM_INSTANCE=...                       # only if your account has more than one instance (the CRN)
python3 run_check.py --backend ibm_kingston --flagged --estimate    # prints the plan and the QPU seconds, submits nothing
python3 run_check.py --backend ibm_kingston --flagged --yes         # submits one job on your account
```

You can name qubits yourself: `--backend ibm_fez --qubits 148,20`. A control qubit with a healthy published T2 / T1 is added for you and must pass first.

## What comes out

`results.json` with, for each qubit: measured T1 and T2 with 95% intervals, the ratio with its interval, the published T1, T2 and their dates, and one outcome.

- ABOVE: the whole interval of T2 / T1 is above 2.
- CONSISTENT: the whole interval is at or below 2.
- CANNOT_TELL: the interval contains 2, a fit failed, or the control failed.
- NOTHING_RETURNED: the job gave no data.

A result now does not date a past record. It says whether a joint measurement today gives a ratio above 2.

## Cost and honesty

You use your own IBM account and your own seconds. The script prints an estimate first and does not submit without --yes. Your token is read from the environment and never written or printed.
Self-test: the fitter is checked on planted worlds over 30 seeds each, and the circuits are checked noiseless. If you find a mistake, tell us at https://indahl.ai/contact and we will correct it in the open.

Heuremen LLC. Free to read, run and cite with attribution. See LICENSE.txt in the repository root. Terms: https://indahl.ai/terms
