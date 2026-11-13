#!/bin/zsh
# After Thunderdome round 13 ends (event wait): Falcon round 2 evaluation on sets C and D, then the SAD S1 generation runs. One GPU job at a time.
cd "${0:A:h}"; PY=/private/tmp/claude-501/-Users-heuremen/80087010-0cb3-4ae5-9e13-362e6d5086ad/scratchpad/trainenv/bin/python
for p in $(pgrep -f 'thunder_chain[.]sh'); do caffeinate -w $p; done
cd falcon_train; export SETS=tC,tD
$PY eval_mlx.py falcon3_base > eval2_base.log 2>&1
$PY eval_mlx.py falcon3_trained adapters_true > eval2_true.log 2>&1
$PY eval_mlx.py falcon3_mixed adapters_mixed > eval2_mixed.log 2>&1
echo "FALCON ROUND 2 REPLIES DONE $(date +%H:%M)"
cd ../claims_stack; ./run_s1b.sh now
echo "S1B DONE $(date +%H:%M)"
