#!/bin/zsh
# Round S2 (ROUND_S2.md): Phi-4-mini-instruct, the vendor card's stated results rerun. One GPU job at a time (queued). Resumable: a run with a done flag is skipped.
cd "${0:A:h}"; PY=/private/tmp/claude-501/-Users-heuremen/80087010-0cb3-4ae5-9e13-362e6d5086ad/scratchpad/trainenv/bin/python
M=microsoft/Phi-4-mini-instruct; COMMON="--batch-size 4 --seed 20281028"; mkdir -p s2
run() { d=$1; shift; [ -f s2/$d/done ] && return; echo "== $d $(date +%H:%M:%S)"; $PY -m mlx_lm evaluate --model $M ${=COMMON} --output-dir s2/$d "$@" > s2/$d.log 2>&1 && touch s2/$d/done || echo "RUN FAILED $d"; }
run arc_challenge --tasks arc_challenge --num-shots 10 --no-apply-chat-template
run boolq --tasks boolq --num-shots 2 --no-apply-chat-template
run hellaswag --tasks hellaswag --num-shots 5 --no-apply-chat-template
run openbookqa --tasks openbookqa --num-shots 10 --no-apply-chat-template
run piqa --tasks piqa --num-shots 5 --no-apply-chat-template
run social_iqa --tasks social_iqa --num-shots 5 --no-apply-chat-template
run winogrande --tasks winogrande --num-shots 5 --no-apply-chat-template
run gsm8k_cot_plain --tasks gsm8k_cot --num-shots 8 --no-apply-chat-template --max-tokens 512
run gsm8k_cot_chat --tasks gsm8k_cot --num-shots 8 --apply-chat-template --fewshot-as-multiturn --max-tokens 512
run mmlu --tasks mmlu --num-shots 5 --no-apply-chat-template
echo "S2 DONE $(date +%H:%M)"
