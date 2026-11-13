import torch
import time, json, pathlib, sys
import torch.nn.functional as F
from transformers import AutoTokenizer, RwkvForCausalLM

FORGE = pathlib.Path.home() / 'bones-forge' / 'architecture-experiments'
sys.path.insert(0, str(FORGE))
from shared_prompts import PROMPTS

MODEL_DIR = str(FORGE / "rwkv-raven-1b5")

MAX_NEW_TOKENS = 150
TEMPERATURE = 1.0
TOP_P = 0.85

def top_p_sample(logits, top_p, temperature):
    logits = logits / max(temperature, 1e-6)
    probs = F.softmax(logits, dim=-1)
    sorted_probs, sorted_idx = torch.sort(probs, descending=True)
    cumulative = torch.cumsum(sorted_probs, dim=-1)
    cutoff = cumulative > top_p
    cutoff[..., 1:] = cutoff[..., :-1].clone()
    cutoff[..., 0] = False
    sorted_probs = sorted_probs.masked_fill(cutoff, 0.0)
    sorted_probs = sorted_probs / sorted_probs.sum(dim=-1, keepdim=True)
    choice = torch.multinomial(sorted_probs, 1)
    return sorted_idx.gather(-1, choice)

def state_norms(state):
    full = torch.cat([s.flatten() for s in state])
    wkv = torch.cat([s.flatten() for s in state[2:]])
    return float(full.norm().item()), float(wkv.norm().item())

@torch.no_grad()
def generate_tracked(model, tokenizer, prompt_text, device):
    inputs = tokenizer(prompt_text, return_tensors='pt').to(device)
    input_ids = inputs['input_ids']

    out = model(input_ids=input_ids, state=None, use_cache=True)
    state = out.state
    logits = out.logits[:, -1, :]

    full_norm, wkv_norm = state_norms(state)
    step_log = [{"step": 0, "token": None, "full_state_norm": full_norm, "wkv_state_norm": wkv_norm}]

    generated = []
    prev_full, prev_wkv = full_norm, wkv_norm
    eos_id = tokenizer.eos_token_id

    for step in range(1, MAX_NEW_TOKENS + 1):
        next_token = top_p_sample(logits, TOP_P, TEMPERATURE)
        tok_id = int(next_token.item())
        if eos_id is not None and tok_id == eos_id:
            break
        generated.append(tok_id)

        out = model(input_ids=next_token, state=state, use_cache=True)
        state = out.state
        logits = out.logits[:, -1, :]

        full_norm, wkv_norm = state_norms(state)
        step_log.append({
            "step": step,
            "token": tok_id,
            "full_state_norm": full_norm,
            "wkv_state_norm": wkv_norm,
            "full_state_delta": full_norm - prev_full,
            "wkv_state_delta": wkv_norm - prev_wkv,
        })
        prev_full, prev_wkv = full_norm, wkv_norm

    text = tokenizer.decode(generated, skip_special_tokens=True)
    return text, step_log

def summarize(step_log):
    import statistics as st
    wkv_norms = [s["wkv_state_norm"] for s in step_log]
    wkv_deltas = [s["wkv_state_delta"] for s in step_log if "wkv_state_delta" in s]
    full_norms = [s["full_state_norm"] for s in step_log]
    return {
        "n_steps": len(step_log),
        "wkv_state_norm_mean": st.mean(wkv_norms) if wkv_norms else None,
        "wkv_state_norm_variance": st.pvariance(wkv_norms) if len(wkv_norms) > 1 else None,
        "wkv_state_delta_mean": st.mean(wkv_deltas) if wkv_deltas else None,
        "wkv_state_delta_variance": st.pvariance(wkv_deltas) if len(wkv_deltas) > 1 else None,
        "full_state_norm_mean": st.mean(full_norms) if full_norms else None,
        "full_state_norm_variance": st.pvariance(full_norms) if len(full_norms) > 1 else None,
    }

def main():
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    print(f'Using device: {device}', flush=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    t0 = time.time()
    model = RwkvForCausalLM.from_pretrained(MODEL_DIR, torch_dtype=torch.float32).to(device).eval()
    load_time = time.time() - t0
    print(f'Model loaded in {load_time:.1f}s', flush=True)

    torch.manual_seed(20260806)

    results = []
    run_t0 = time.time()
    partial_path = FORGE / 'rwkv_signals_raw_batch2.partial.jsonl'
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
    for category, prompt_raw in PROMPTS:
        if prompt_raw in done_prompts:
            results.append(done_prompts[prompt_raw])
            print(f"[{category}] {prompt_raw!r} -> SKIPPED (already done)", flush=True)
            continue
        prompt_text = f'Bot: Hi! I am your assistant.\n\nUser: {prompt_raw}\n\nBot:'
        t0 = time.time()
        text, step_log = generate_tracked(model, tokenizer, prompt_text, device)
        dt = time.time() - t0
        summ = summarize(step_log)
        result = {
            "category": category,
            "prompt": prompt_raw,
            "output_text": text,
            "gen_seconds": dt,
            **summ,
            "step_log": step_log,
        }
        results.append(result)
        partial_f.write(json.dumps(result) + "\n")
        partial_f.flush()
        print(f"[{category}] {prompt_raw!r} -> {dt:.1f}s, {summ['n_steps']} steps, "
              f"wkv_norm_mean={summ['wkv_state_norm_mean']:.4f}, wkv_norm_var={summ['wkv_state_norm_variance']:.6f}, "
              f"wkv_delta_var={summ['wkv_state_delta_variance']:.6f}", flush=True)

    partial_f.close()
    total_run_time = time.time() - run_t0
    out_path = FORGE / 'rwkv_signals_raw_batch2.json'
    out_path.write_text(json.dumps({"load_seconds": load_time, "total_gen_seconds": total_run_time, "results": results}, indent=2))
    print(f"\nWrote {out_path}  (load={load_time:.1f}s, total_gen={total_run_time:.1f}s)", flush=True)

if __name__ == '__main__':
    main()
