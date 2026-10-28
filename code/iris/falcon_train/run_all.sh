#!/bin/zsh
# After the download: train both adapters, then answer both evaluation sets with the base model, the trained model and the mixed-label model. One worker. Runs once.
cd "${0:A:h}"; PY=/private/tmp/claude-501/-Users-heuremen/80087010-0cb3-4ae5-9e13-362e6d5086ad/scratchpad/trainenv/bin/python
while [ ! -f models/Falcon3-3B-Instruct/model-00001-of-00002.safetensors ] || pgrep -f "snapshot_download" >/dev/null; do sleep 5; done
./train.sh > train_all.log 2>&1
$PY publish_train_status.py
$PY eval_mlx.py falcon3_base > eval_base.log 2>&1
$PY eval_mlx.py falcon3_trained adapters_true > eval_true.log 2>&1
$PY eval_mlx.py falcon3_mixed adapters_mixed > eval_mixed.log 2>&1
echo "FALCON ALL DONE $(date +%H:%M)"
