import torch
import numpy as np
import torch.nn.functional as F
import time, json, pathlib, sys

FORGE = pathlib.Path.home() / 'bones-forge' / 'architecture-experiments'
sys.path.insert(0, str(FORGE))
from shared_prompts import PROMPTS

MODEL_DIR = str(FORGE / "llada-8b-instruct")

def add_gumbel_noise(logits, temperature):
    if temperature == 0:
        return logits
    logits = logits.to(torch.float32)
    noise = torch.rand_like(logits, dtype=torch.float32)
    gumbel_noise = (- torch.log(noise)) ** temperature
    return logits.exp() / gumbel_noise

def get_num_transfer_tokens(mask_index, steps):
    mask_num = mask_index.sum(dim=1, keepdim=True)
    base = mask_num // steps
    remainder = mask_num % steps
    num_transfer_tokens = torch.zeros(mask_num.size(0), steps, device=mask_index.device, dtype=torch.int64) + base
    for i in range(mask_num.size(0)):
        num_transfer_tokens[i, :remainder[i]] += 1
    return num_transfer_tokens

@torch.no_grad()
def generate_tracked(model, prompt, attention_mask=None, steps=64, gen_length=64, block_length=32,
                      temperature=0., remasking='low_confidence', mask_id=126336):
    x = torch.full((prompt.shape[0], prompt.shape[1] + gen_length), mask_id, dtype=torch.long).to(model.device)
    x[:, :prompt.shape[1]] = prompt.clone()
    if attention_mask is not None:
        attention_mask = torch.cat([attention_mask, torch.ones((prompt.shape[0], gen_length), dtype=attention_mask.dtype, device=model.device)], dim=-1)
    prompt_index = (x != mask_id)
    assert gen_length % block_length == 0
    num_blocks = gen_length // block_length
    assert steps % num_blocks == 0
    steps_per_block = steps // num_blocks

    step_log = []
    global_step = 0

    for num_block in range(num_blocks):
        block_mask_index = (x[:, prompt.shape[1] + num_block * block_length: prompt.shape[1] + (num_block + 1) * block_length:] == mask_id)
        num_transfer_tokens = get_num_transfer_tokens(block_mask_index, steps_per_block)
        for i in range(steps_per_block):
            mask_index = (x == mask_id)
            logits = model(x, attention_mask=attention_mask).logits

            logits_with_noise = add_gumbel_noise(logits, temperature=temperature)
            x0 = torch.argmax(logits_with_noise, dim=-1)

            if remasking == 'low_confidence':
                p = F.softmax(logits.to(torch.float32), dim=-1)
                x0_p = torch.squeeze(torch.gather(p, dim=-1, index=torch.unsqueeze(x0, -1)), -1)
            else:
                raise NotImplementedError(remasking)

            x0_p[:, prompt.shape[1] + (num_block + 1) * block_length:] = -np.inf
            x0 = torch.where(mask_index, x0, x)
            confidence = torch.where(mask_index, x0_p, torch.tensor(-np.inf, device=x0_p.device, dtype=x0_p.dtype))

            transfer_index = torch.zeros_like(x0, dtype=torch.bool, device=x0.device)
            for j in range(confidence.shape[0]):
                _, select_index = torch.topk(confidence[j], k=num_transfer_tokens[j, i])
                transfer_index[j, select_index] = True

            transferred_confidences = x0_p[transfer_index].tolist()
            x[transfer_index] = x0[transfer_index]

            remaining_masked = int((x == mask_id).sum().item())
            step_log.append({
                "global_step": global_step,
                "block": num_block,
                "step_in_block": i,
                "n_tokens_committed_this_step": int(transfer_index.sum().item()),
                "mean_confidence_this_step": float(np.mean(transferred_confidences)) if transferred_confidences else None,
                "min_confidence_this_step": float(np.min(transferred_confidences)) if transferred_confidences else None,
                "masked_remaining_after_step": remaining_masked,
            })
            global_step += 1

    return x, step_log

def main():
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    print(f'Using device: {device}', flush=True)
    tokenizer = __import__('transformers').AutoTokenizer.from_pretrained(MODEL_DIR, trust_remote_code=True)
    t0 = time.time()
    model = __import__('transformers').AutoModel.from_pretrained(MODEL_DIR, trust_remote_code=True, torch_dtype=torch.bfloat16)
    model = model.to(device).eval()
    load_time = time.time() - t0
    print(f'Model loaded in {load_time:.1f}s', flush=True)
    if tokenizer.padding_side != 'left':
        tokenizer.padding_side = 'left'

    gen_length = 64
    results = []
    run_t0 = time.time()
    partial_path = FORGE / 'llada_signals_raw_batch2.partial.jsonl'
    done_prompts = {}
    if partial_path.exists():
        with open(partial_path) as pf:
            for line in pf:
                line = line.strip()
                if line:
                    r = json.loads(line)
                    done_prompts[r['prompt']] = r
        print(f'Resuming: {len(done_prompts)} prompts already completed in {partial_path}', flush=True)
    partial_f = open(partial_path, 'a')
    for category, prompt_text_raw in PROMPTS:
        if prompt_text_raw in done_prompts:
            results.append(done_prompts[prompt_text_raw])
            print(f"[{category}] {prompt_text_raw!r} -> SKIPPED (already done)", flush=True)
            continue
        message = [{'role': 'user', 'content': prompt_text_raw}]
        prompt_text = tokenizer.apply_chat_template(message, add_generation_prompt=True, tokenize=False)
        encoded = tokenizer(prompt_text, add_special_tokens=False, return_tensors='pt')
        input_ids = encoded['input_ids'].to(device)
        attention_mask = encoded['attention_mask'].to(device)

        t0 = time.time()
        out, step_log = generate_tracked(model, input_ids, attention_mask, steps=64, gen_length=gen_length,
                                          block_length=32, temperature=0., remasking='low_confidence')
        dt = time.time() - t0
        output_text = tokenizer.batch_decode(out[:, input_ids.shape[1]:], skip_special_tokens=True)[0]

        confidences = [s["mean_confidence_this_step"] for s in step_log if s["mean_confidence_this_step"] is not None]
        n_steps = len(step_log)
        q = max(1, n_steps // 4)
        early_conf = float(np.mean(confidences[:q])) if confidences[:q] else None
        late_conf = float(np.mean(confidences[-q:])) if confidences[-q:] else None
        masked_before_final_step = step_log[-1]["masked_remaining_after_step"] + step_log[-1]["n_tokens_committed_this_step"]
        unresolved_fraction_entering_final_step = masked_before_final_step / gen_length

        result = {
            "category": category,
            "prompt": prompt_text_raw,
            "output_text": output_text,
            "gen_seconds": dt,
            "n_steps": n_steps,
            "mean_confidence_overall": float(np.mean(confidences)) if confidences else None,
            "min_confidence_overall": float(np.min(confidences)) if confidences else None,
            "early_quarter_mean_confidence": early_conf,
            "late_quarter_mean_confidence": late_conf,
            "confidence_delta_late_minus_early": (late_conf - early_conf) if (early_conf is not None and late_conf is not None) else None,
            "unresolved_fraction_entering_final_step": unresolved_fraction_entering_final_step,
            "final_step_mean_confidence": step_log[-1]["mean_confidence_this_step"],
            "final_step_min_confidence": step_log[-1]["min_confidence_this_step"],
            "step_log": step_log,
        }
        results.append(result)
        partial_f.write(json.dumps(result) + "\n")
        partial_f.flush()
        print(f"[{category}] {prompt_text_raw!r} -> {dt:.1f}s, mean_conf={result['mean_confidence_overall']:.4f}, "
              f"early={early_conf:.4f}, late={late_conf:.4f}, unresolved_entering_final_step={unresolved_fraction_entering_final_step:.3f}",
              flush=True)

    partial_f.close()
    total_run_time = time.time() - run_t0
    out_path = FORGE / 'llada_signals_raw_batch2.json'
    out_path.write_text(json.dumps({"load_seconds": load_time, "total_gen_seconds": total_run_time, "results": results}, indent=2))
    print(f"\nWrote {out_path}  (load={load_time:.1f}s, total_gen={total_run_time:.1f}s)", flush=True)

if __name__ == '__main__':
    main()
