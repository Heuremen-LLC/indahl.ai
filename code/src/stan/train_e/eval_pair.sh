#!/bin/zsh
# eval_pair.sh MODEL ADAPTER|- NAME -- scores on both held-out sets (test_pipeline, test_hand) with eval_mlx.py
set -eu
cd /Users/heuremen/bones-forge/stan/train_e
for SET in test_pipeline test_hand; do
  /Users/heuremen/bones-forge/venv/bin/python eval_mlx.py "$1" "$2" data/$SET.jsonl "$3_$SET"
done
