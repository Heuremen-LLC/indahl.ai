#!/usr/bin/env python3
"""train_sft.py -- Wen-data v0: a LoRA adapter taught the house rule (never label on one ruler; hold when rulers split or
the chip moves; commit when they agree) from gen_train.py's cases. Loss on the answer only.
Run: venv/Scripts/python train_sft.py train.jsonl --out wen_v0 [--model Qwen/Qwen3-1.7B]"""
import argparse, json
import torch
from datasets import Dataset
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import SFTConfig, SFTTrainer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('data'); ap.add_argument('--model', default='Qwen/Qwen3-1.7B'); ap.add_argument('--out', default='wen_v0')
    ap.add_argument('--n', type=int, default=0); ap.add_argument('--epochs', type=float, default=1); ap.add_argument('--lr', type=float, default=2e-4); ap.add_argument('--threads', type=int, default=10)
    a = ap.parse_args(); torch.set_num_threads(a.threads)
    rows = [json.loads(l) for l in open(a.data, encoding='utf-8')]
    rows = rows[:a.n] if a.n else rows
    ds = Dataset.from_list([{'messages': r['messages']} for r in rows])
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.float32)
    print('threads', torch.get_num_threads(), flush=True)
    cfg = SFTConfig(output_dir=a.out, num_train_epochs=a.epochs, per_device_train_batch_size=4, gradient_accumulation_steps=2,
                    learning_rate=a.lr, logging_steps=1, save_strategy='no', report_to=[], max_length=320, dataloader_num_workers=0, disable_tqdm=True,
                    assistant_only_loss=False, completion_only_loss=None, use_cpu=not torch.cuda.is_available())
    lora = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, target_modules=['q_proj', 'k_proj', 'v_proj', 'o_proj'], task_type='CAUSAL_LM')
    tr = SFTTrainer(model=model, args=cfg, train_dataset=ds, processing_class=tok, peft_config=lora)
    tr.train(); tr.save_model(a.out)
    print('trained on', len(rows), 'cases; adapter in', a.out)


if __name__ == '__main__':
    main()
