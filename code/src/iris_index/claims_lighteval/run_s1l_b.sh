#!/bin/zsh
# Round S1L, Addendum 4: the six task lines after IFEval, at the card's max length 2048. Tasks with no generation size (BBH) use lighteval's
# vllm budget rule through the marked patch (LIGHTEVAL_VLLM_BUDGET=1, patched/base_model_addendum4.diff). One call per task, own done flags.
cd "${0:A:h}"; LE=$PWD/venv/bin/lighteval; mkdir -p out
export HF_DATASETS_TRUST_REMOTE_CODE=1 TOKENIZERS_PARALLELISM=false PYTORCH_ENABLE_MPS_FALLBACK=1 PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.3 PYTORCH_MPS_LOW_WATERMARK_RATIO=0.2 LIGHTEVAL_VLLM_BUDGET=1
tail -n +2 patched/smollm2_instruct.txt | while IFS= read -r TASK || [ -n "$TASK" ]; do [ -z "$TASK" ] && continue; TN=${TASK//|/_}
  if [ ! -f out/claims_b_$TN.done ]; then echo "== claims $TASK $(date +%H:%M:%S)"
    (cd patched && $LE accelerate --model_args "pretrained=HuggingFaceTB/SmolLM2-1.7B-Instruct,revision=31b70e2e869a7173562077fd711b654946d38674,dtype=bfloat16,max_length=2048" \
      --custom_tasks tasks.py --tasks "$TASK" --use_chat_template --output_dir ../out/claims_$TN --save_details --override_batch_size 4) > out/claims_$TN.log 2>&1 && touch out/claims_b_$TN.done || echo "CLAIMS $TASK FAILED"; fi
done
echo "S1L B DONE $(date +%H:%M)"
