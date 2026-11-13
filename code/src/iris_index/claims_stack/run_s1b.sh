#!/bin/zsh
# Round S1, generation tasks (ROUND_S1.md addenda 1 and 2). Starts when the Falcon pipeline ends (event wait). One GPU job at a time.
cd "${0:A:h}"; PY=/private/tmp/claude-501/-Users-heuremen/80087010-0cb3-4ae5-9e13-362e6d5086ad/scratchpad/trainenv/bin/python
M=HuggingFaceTB/SmolLM2-1.7B-Instruct; COMMON="--batch-size 4 --seed 20281028"
mark() { echo "{\"status\": \"$1\", \"known_good\": \"$KG\"}" > state_s1.json; $PY publish_model_live.py; }
KG=$($PY score_s1.py knowngood 2>&1 | tail -1)
[ "$1" != "now" ] && caffeinate -w ${1:?pid to wait for, or now}
mkdir -p kg s1
if [ ! -f kg/gsm8k/done ]; then
  $PY -m mlx_lm evaluate --model Qwen/Qwen1.5-1.8B --tasks gsm8k --num-shots 5 --no-apply-chat-template ${=COMMON} --output-dir kg/gsm8k > kg/gsm8k.log 2>&1 && touch kg/gsm8k/done
fi
GK=$($PY score_s1.py genknowngood 2>&1 | tail -1); KG="$KG; generation: $GK"
case "$GK" in passed*) touch gen_ok; mark "Generation check passed. Running GSM8K, BBH and IFEval." ;; *) mark "Generation check did not pass. Generation rows stay held."; exit 0;; esac
run() { d=$1; shift; [ -f s1/$d/done ] && return; $PY -m mlx_lm evaluate --model $M ${=COMMON} --output-dir s1/$d "$@" > s1/$d.log 2>&1 && touch s1/$d/done; $PY score_s1.py read > score_s1.log 2>&1; mark "Running. $d finished." ; }
run gsm8k_plain --tasks gsm8k --num-shots 5 --no-apply-chat-template
run gsm8k_chat --tasks gsm8k --num-shots 5 --apply-chat-template
run gsm8k_chatmt --tasks gsm8k --num-shots 5 --apply-chat-template --fewshot-as-multiturn
run ifeval_chat --tasks ifeval --num-shots 0 --apply-chat-template
run bbh_plain --tasks bbh_fewshot --num-shots 3 --no-apply-chat-template --max-tokens 256
run bbh_chat --tasks bbh_fewshot --num-shots 3 --apply-chat-template --max-tokens 256
mark "All runs finished. Outcomes are recounted by hand before they are final."
echo "S1B DONE $(date +%H:%M)"
