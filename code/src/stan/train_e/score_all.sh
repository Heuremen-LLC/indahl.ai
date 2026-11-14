#!/bin/zsh
# score_all.sh (13 Nov 2026): confidence scores for base, v4, v6, v7 on both held-out sets (eval_score.py), then the cutoff curves.
set -eu
cd /Users/heuremen/bones-forge/stan/train_e
M=mlx-community/Qwen2.5-7B-Instruct-4bit
for SET in test_hand test_pipeline; do
  /Users/heuremen/bones-forge/venv/bin/python eval_score.py $M - data/$SET.jsonl base_$SET
  for V in v4 v6 v7; do [ -d adapters_$V ] && /Users/heuremen/bones-forge/venv/bin/python eval_score.py $M adapters_$V data/$SET.jsonl lora_${V}_$SET; done
done
/opt/homebrew/bin/python3 curves.py
