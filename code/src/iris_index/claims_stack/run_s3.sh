#!/bin/zsh
# Round S3 (ROUND_S3.md): Granite 4.1 3B, the card's stated results rerun. One GPU job at a time (queued). Resumable.
cd "${0:A:h}"; PY=/private/tmp/claude-501/-Users-heuremen/80087010-0cb3-4ae5-9e13-362e6d5086ad/scratchpad/trainenv/bin/python
M=ibm-granite/granite-4.1-3b; COMMON="--batch-size 4 --seed 20281028"; mkdir -p s3
run() { d=$1; shift; [ -f s3/$d/done ] && return; echo "== $d $(date +%H:%M:%S)"; $PY -m mlx_lm evaluate --model $M ${=COMMON} --output-dir s3/$d "$@" > s3/$d.log 2>&1 && touch s3/$d/done || echo "RUN FAILED $d"; }
run gsm8k_plain --tasks gsm8k --num-shots 8 --no-apply-chat-template --max-tokens 512
run gsm8k_cot_chat --tasks gsm8k_cot --num-shots 8 --apply-chat-template --fewshot-as-multiturn --max-tokens 512
run bbh_cot_chat --tasks bbh_cot_fewshot --num-shots 3 --apply-chat-template --fewshot-as-multiturn --max-tokens 512
run mmlu --tasks mmlu --num-shots 5 --no-apply-chat-template
echo "S3 DONE $(date +%H:%M)"
