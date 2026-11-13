#!/usr/bin/env python3
"""train_dpo.py -- the first hat: a LoRA adapter trained on the kept pairs from build_pairs.py (6 October 2026).

Holds out one moment in five (fixed seed) so the score is read on moments it never trained on.
CPU-safe defaults for the 1.7B prototype; the same script runs on the 3080 for the 4B (add --bf16 when on GPU).
Run: venv/Scripts/python train_dpo.py pairs.jsonl --model Qwen/Qwen3-1.7B --out hat_v1"""
import argparse, json, random
import torch
from datasets import Dataset
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import DPOConfig, DPOTrainer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pairs'); ap.add_argument('--model', default='Qwen/Qwen3-1.7B'); ap.add_argument('--out', default='hat_v1')
    ap.add_argument('--epochs', type=float, default=2); ap.add_argument('--beta', type=float, default=0.1)
    ap.add_argument('--lr', type=float, default=5e-5); ap.add_argument('--threads', type=int, default=8); ap.add_argument('--bf16', action='store_true')
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    rows = [json.loads(l) for l in open(a.pairs, encoding='utf-8')]
    rows = [r for r in rows if r.get('kept')]
    random.Random(1031).shuffle(rows)
    k = max(1, len(rows) // 5)
    held, train = rows[:k], rows[k:]
    json.dump([dict(conv=r['conv'], at=r['at']) for r in held], open(a.out + '_heldout.json', 'w'), indent=1)
    data = Dataset.from_list([dict(prompt=r['prompt'], chosen=[{'role': 'assistant', 'content': r['chosen']}],
                                   rejected=[{'role': 'assistant', 'content': r['rejected']}]) for r in train])
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, torch_dtype=torch.bfloat16 if a.bf16 else torch.float32)
    cfg = DPOConfig(output_dir=a.out, num_train_epochs=a.epochs, per_device_train_batch_size=1, gradient_accumulation_steps=4,
                    learning_rate=a.lr, beta=a.beta, logging_steps=1, save_strategy='no', report_to=[], bf16=a.bf16,
                    max_length=1536, use_cpu=not torch.cuda.is_available())
    lora = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, target_modules=['q_proj', 'k_proj', 'v_proj', 'o_proj'], task_type='CAUSAL_LM')
    tr = DPOTrainer(model=model, args=cfg, train_dataset=data, processing_class=tok, peft_config=lora)
    tr.train()
    tr.save_model(a.out)
    print(f'trained on {len(train)} pairs, held out {len(held)}; adapter in {a.out}/')


if __name__ == '__main__':
    main()
