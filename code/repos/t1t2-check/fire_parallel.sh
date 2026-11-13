#!/bin/bash
# 29 Oct, Note 2 in PLAN.md: kingston and fez submitted in parallel with the already queued boston job. Key and instance from local files, never printed.
cd ~/bones-forge/t1t2_check
export IBM_QUANTUM_TOKEN="$(cat ~/bones-forge/.ibm_quantum_key_3)" IBM_QUANTUM_INSTANCE="$(cat ~/bones-forge/.ibm_quantum_instance_crn)"
b=$1
~/bones-forge/qvenv/bin/python -u -I run_check.py --backend $b --flagged --yes --out runs/results_$b.json 2>&1 | grep -v WARNING | sed "s/$IBM_QUANTUM_TOKEN/<KEY>/g" > runs/log_$b.txt
