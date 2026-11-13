#!/bin/bash
# 29 Oct, his word "fire away": one job per flagged processor, sequential. Key and instance from local files, never printed.
cd ~/bones-forge/t1t2_check
export IBM_QUANTUM_TOKEN="$(cat ~/bones-forge/.ibm_quantum_key_3)" IBM_QUANTUM_INSTANCE="$(cat ~/bones-forge/.ibm_quantum_instance_crn)"
for b in ibm_boston ibm_kingston ibm_fez; do
  ~/bones-forge/qvenv/bin/python -I run_check.py --backend $b --flagged --yes --out runs/results_$b.json 2>&1 | grep -v WARNING | sed "s/$IBM_QUANTUM_TOKEN/<KEY>/g" > runs/log_$b.txt
done
echo done > runs/DONE
