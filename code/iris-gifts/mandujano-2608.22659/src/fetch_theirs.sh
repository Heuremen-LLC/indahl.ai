#!/bin/sh
# Downloads the files this recount reads into ../theirs (beside src) at pinned commits, then checks them against THEIRS_HASHES.txt.
set -e
cd "$(dirname "$0")/.."; mkdir -p theirs/upstream theirs/upstream_code; cd theirs
H=https://raw.githubusercontent.com/JFMandujanoR/Statistical-Methods-for-Multi-Model-LLM-Evaluation/a353e2cbbce2c5ae10c8ea5d18fb5c0b0bed4f5b
T=https://raw.githubusercontent.com/TIGER-AI-Lab/MMLU-Pro/f418b116db00b065c2aea046518d8fcf74d39872
curl -sL -o paper.pdf https://arxiv.org/pdf/2608.22659v2
curl -sL -o mmlu_pro_real_data.csv $H/mmlu_pro_real_data.csv
for m in Mistral-7B-Instruct-v0.1 Mistral-7B-Instruct-v0.2 Mistral-7B-v0.1 Qwen1.5-7B-Chat Yi-6B Yi-6b-Chat; do
  curl -sL -o upstream/$m.zip "$T/eval_results/model_outputs_${m}_5shots.zip"; done
for f in evaluate_from_local.py compute_accuracy.py; do curl -sL -o upstream_code/$f $T/$f; done
grep -E '^[0-9a-f]{64} ' ../THEIRS_HASHES.txt | shasum -a 256 -c -
