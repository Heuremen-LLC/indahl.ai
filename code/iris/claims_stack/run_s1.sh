#!/bin/zsh
# Round S1 (ROUND_S1.md): SmolLM2-1.7B-Instruct, original weights in bf16, lm-evaluation-harness through mlx-lm. Starts when the Falcon pipeline ends (event wait, no timer). Updates the MODEL live block after each task.
cd "${0:A:h}"; PY=/private/tmp/claude-501/-Users-heuremen/80087010-0cb3-4ae5-9e13-362e6d5086ad/scratchpad/trainenv/bin/python
M=HuggingFaceTB/SmolLM2-1.7B-Instruct; COMMON="--batch-size 8 --seed 20281028"
mark() { echo "{\"status\": \"$1\", \"known_good\": \"$2\"}" > state_s1.json; $PY publish_model_live.py; }
[ "$1" != "now" ] && caffeinate -w ${1:?pid of a process to wait for, or now}
KG=$($PY score_s1.py knowngood 2>&1 | tail -1); mark "Known-good check read. Running the claims." "$KG"
for spec in "hellaswag 0 no" "arc_easy 0 no" "arc_challenge 0 no" "piqa 0 no" "gsm8k 5 no" "bbh_fewshot 3 no" "ifeval 0 yes"; do
  set -- ${=spec}; t=$1; sh=$2; ct=$3; flag="--no-apply-chat-template"; [ "$ct" = yes ] && flag="--apply-chat-template"
  [ -f s1/$t/done ] && continue
  $PY -m mlx_lm evaluate --model $M --tasks $t --num-shots $sh $flag ${=COMMON} --output-dir s1/$t > s1/$t.log 2>&1 && touch s1/$t/done
  $PY score_s1.py read > score_s1.log 2>&1; mark "Running. $t finished." "$KG"
done
n=$(ls s1/*/done 2>/dev/null | wc -l); if [ "$n" = 7 ]; then mark "All runs finished. Outcomes are recounted by hand before they are final." "$KG"; else mark "Stopped with $n of 7 tasks finished. See the logs." "$KG"; fi
echo "S1 DONE $(date +%H:%M)"
