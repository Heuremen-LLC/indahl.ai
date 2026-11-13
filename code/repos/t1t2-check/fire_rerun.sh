#!/bin/bash
# 29 Oct, Note 4 in PLAN.md: fez q148 rerun with a grid sized to the measured T1 and interleaved circuits. Key and instrument from local files, never printed.
cd ~/bones-forge/t1t2_check
export IBM_QUANTUM_TOKEN="$(cat ~/bones-forge/.ibm_quantum_key_3)" IBM_QUANTUM_INSTANCE="$(cat ~/bones-forge/.ibm_quantum_instance_crn)"
~/bones-forge/qvenv/bin/python -u -I run_check.py --backend ibm_fez --qubits 148 --t1max 5 --t2max 5 --interleave --yes --out runs/results_ibm_fez_rerun1.json 2>&1 | grep -v WARNING | sed "s/$IBM_QUANTUM_TOKEN/<KEY>/g" > runs/log_ibm_fez_rerun1.txt
