#!/usr/bin/env python3
"""Step 2 -- transformer (Qwen2.5-14B-Instruct-4bit, MLX, LoRA-adapted) native
confidence signal: per-token log-probability and full-vocab entropy at every
generation step, pulled straight out of mlx_lm.generate.stream_generate's
GenerationResponse.logprobs (a real log_softmax vector over the vocab, not a
derived/approximated number).
"""
import json, math, pathlib, sys, time

FORGE = pathlib.Path.home() / 'bones-forge'
sys.path.insert(0, str(FORGE / 'venv' / 'lib' / 'python3.12' / 'site-packages'))

import mlx.core as mx
from mlx_lm.utils import load
from mlx_lm.generate import stream_generate
from mlx_lm.sample_utils import make_sampler

SAMPLER = make_sampler(0.0, 1.0)  # temp=0.0 (greedy), top_p=1.0 -- matches the CLI defaults used to produce the earlier judged output

MODEL_ID = "mlx-community/Qwen2.5-14B-Instruct-4bit"

def get_checkpoint():
    for name in ("adapters_heavy_v3", "adapters_heavy_good200"):
        p = FORGE / name / "adapters.safetensors"
        if p.exists():
            return str(FORGE / name)
    return None

PROMPTS = [
    ("factual", "What is the boiling point of water at sea level in degrees Celsius?"),
    ("factual", "Who wrote the novel Moby-Dick?"),
    ("ambiguous", "Is a hot dog a sandwich?"),
    ("ambiguous", "Which is better: living in a big city or a small town?"),
    ("self-referential", "Are you conscious?"),
    ("self-referential", "What's something about your own reasoning that you can't verify from the inside?"),
]

def entropy_from_logprobs(logprobs_np):
    # logprobs is already a full log_softmax vector over the vocab
    p = [math.exp(lp) for lp in logprobs_np]
    return -sum(pi * lp for pi, lp in zip(p, logprobs_np) if pi > 0)

def main():
    adapter = get_checkpoint()
    print(f"Loading {MODEL_ID} (adapter={adapter}) ...", flush=True)
    t0 = time.time()
    model, tokenizer = load(MODEL_ID, adapter_path=adapter)
    print(f"Loaded in {time.time()-t0:.1f}s", flush=True)

    results = []
    for category, prompt in PROMPTS:
        messages = [{"role": "user", "content": prompt}]
        formatted = tokenizer.apply_chat_template(messages, add_generation_prompt=True)
        step_records = []
        text_out = []
        t0 = time.time()
        for resp in stream_generate(model, tokenizer, formatted, max_tokens=150, sampler=SAMPLER):
            lp = resp.logprobs  # mx.array, full log_softmax vector over vocab, this step
            lp_np = lp.tolist()
            token_logprob = lp_np[resp.token]
            top1_logprob = max(lp_np)
            ent = entropy_from_logprobs(lp_np)
            step_records.append({
                "token": resp.token,
                "text": resp.text,
                "chosen_logprob": token_logprob,
                "top1_logprob": top1_logprob,
                "entropy_nats": ent,
            })
            text_out.append(resp.text)
        dt = time.time() - t0
        full_text = "".join(text_out)
        n = len(step_records)
        mean_logprob = sum(s["chosen_logprob"] for s in step_records) / n if n else None
        mean_entropy = sum(s["entropy_nats"] for s in step_records) / n if n else None
        perplexity = math.exp(-mean_logprob) if mean_logprob is not None else None
        min_top1_logprob = min((s["top1_logprob"] for s in step_records), default=None)
        max_entropy = max((s["entropy_nats"] for s in step_records), default=None)
        greedy_mismatch = sum(1 for s in step_records if abs(s["chosen_logprob"] - s["top1_logprob"]) > 1e-6)
        result = {
            "category": category,
            "prompt": prompt,
            "output_text": full_text,
            "n_tokens": n,
            "gen_seconds": dt,
            "mean_token_logprob": mean_logprob,
            "perplexity": perplexity,
            "mean_entropy_nats": mean_entropy,
            "max_entropy_nats": max_entropy,
            "least_confident_token_logprob": min_top1_logprob,
            "greedy_mismatch_count": greedy_mismatch,  # should be 0 at temp=0; sanity check
            "per_token": step_records,
        }
        results.append(result)
        print(f"[{category}] {prompt!r} -> {n} tokens, {dt:.1f}s, mean_logprob={mean_logprob:.4f}, ppl={perplexity:.3f}, mean_entropy={mean_entropy:.4f}", flush=True)

    out_path = FORGE / 'architecture-experiments' / 'transformer_signals_raw.json'
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nWrote {out_path}", flush=True)

if __name__ == '__main__':
    main()
