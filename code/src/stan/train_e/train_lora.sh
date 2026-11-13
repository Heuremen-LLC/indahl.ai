#!/bin/zsh
# train_lora.sh MODEL LR ITERS ADAPTER_DIR [DATA_DIR, default data] -- one LoRA run on data/ (built by build_set.py). Exit code is the chain's event.
# 13 Nov: rows over 4096 tokens dropped first (filter_len.py), batch 1 + grad checkpoint (48 GB Mac; v1 at batch 2/3072 peaked 56 GB and
# went NaN because truncation removed whole targets). Any NaN loss in the log fails the stage, so nothing downstream evaluates a broken adapter.
set -eu
cd /Users/heuremen/bones-forge/stan/train_e
V=/Users/heuremen/bones-forge/venv/bin/python
$V filter_len.py "$1" 4096
LOG="$4.train.log"; mkdir -p "$4"
$V -m mlx_lm lora --model "$1" --train --data "${5:-data}" --adapter-path "$4" --iters "$3" \
  --batch-size 1 --learning-rate "$2" --num-layers 16 --max-seq-length 4096 --grad-checkpoint --mask-prompt --seed 20261112 --steps-per-eval 100 2>&1 | tee "$LOG"
if grep -qi "loss nan" "$LOG"; then echo "NaN loss in $LOG: stage failed"; exit 7; fi
grep -q "Saved final weights" "$LOG" || { echo "no final weights line: stage failed"; exit 8; }
