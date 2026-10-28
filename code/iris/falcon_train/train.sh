#!/bin/zsh
# One worker, our Mac only. Trains the true-label adapter and the mixed-label adapter back to back. Event-driven: runs once, logs, exits.
cd "${0:A:h}"; PY=/private/tmp/claude-501/-Users-heuremen/80087010-0cb3-4ae5-9e13-362e6d5086ad/scratchpad/trainenv/bin/python
for k in true mixed; do
  echo "== train $k $(date +%H:%M:%S)"; $PY -m mlx_lm lora -c train_config.yaml --data data_$k --adapter-path adapters_$k > train_$k.log 2>&1; echo "exit $? $(date +%H:%M:%S)"
done
echo "TRAIN DONE $(date +%H:%M:%S)"
