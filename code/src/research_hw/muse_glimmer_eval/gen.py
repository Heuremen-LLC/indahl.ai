"""gen.py MODEL_KIND OUT_JSONL DEADLINE_EPOCH [subset_only]
Greedy, max 300 tokens, eval only on heldout_sft.jsonl (meta stripped from the prompt). Subset rows first, then the rest until the deadline.
MODEL_KIND: muse (mlx-vlm, mlx-community/Muse-Glimmer-30B-4bit, reasoning_strength low) | hermes (mlx-lm, mlx-community/Hermes-3-Llama-3.1-8B-4bit)."""
import json, sys, time, os
kind, out, deadline = sys.argv[1], sys.argv[2], float(sys.argv[3])
subset_only = len(sys.argv) > 4
SRC = '/Users/heuremen/bones-forge/sage_library/sage_v/gap_corpus/heldout_sft.jsonl'
R = [json.loads(l) for l in open(SRC)]
sub = json.load(open(os.path.dirname(os.path.abspath(__file__)) + '/subset160.json'))['indices']
order = list(sub) + ([] if subset_only else [i for i in range(len(R)) if i not in set(sub)])
done = set()
if os.path.exists(out):
    for l in open(out): done.add(json.loads(l)['idx'])
import mlx.core as mx
t0 = time.time()
if kind == 'muse':
    from mlx_vlm import load, stream_generate
    model, proc = load('mlx-community/Muse-Glimmer-30B-4bit')
    tok = proc.tokenizer if hasattr(proc, 'tokenizer') else proc
    def prompt_of(sys_, user):
        s = tok.apply_chat_template([{'role': 'system', 'content': sys_}, {'role': 'user', 'content': user}],
                                    add_generation_prompt=True, tokenize=False, reasoning_strength='low')
        return s[len(tok.bos_token):] if s.startswith(tok.bos_token) else s   # mlx-vlm tokenizes muse_glimmer with add_special_tokens=True (adds BOS itself)
    def run(p):
        ids, last = [], None
        for r in stream_generate(model, proc, p, max_tokens=300, temperature=0.0):
            if r.token is not None: ids.append(int(r.token))
            last = r
        return ids, last
else:
    sys.path.insert(0, '/Users/heuremen/bones-forge/sage_library/sage_v'); import chatfmt
    from mlx_lm import load, stream_generate
    from mlx_lm.sample_utils import make_sampler
    model, tok = load('mlx-community/Hermes-3-Llama-3.1-8B-4bit')
    samp = make_sampler(temp=0.0)
    def prompt_of(sys_, user):
        return tok.apply_chat_template(chatfmt.msgs(tok, sys_, user), add_generation_prompt=True, tokenize=False)
    def run(p):
        ids, last = [], None
        for r in stream_generate(model, tok, p, max_tokens=300, sampler=samp):
            ids.append(int(r.token)); last = r
        return ids, last
print(f'loaded {kind} in {time.time()-t0:.1f}s peak {mx.get_peak_memory()/1e9:.2f} GB', flush=True)
f = open(out, 'a')
for n, i in enumerate(order):
    if i in done: continue
    if time.time() > deadline: print(f'deadline reached after {n} rows', flush=True); break
    m = R[i]['messages']
    p = prompt_of(m[0]['content'], m[1]['content'])
    t1 = time.time(); ids, last = run(p); dt = time.time() - t1
    raw = tok.decode(ids, skip_special_tokens=False)
    f.write(json.dumps({'idx': i, 'row_id': R[i]['meta']['row_id'], 'desk': R[i]['meta']['desk'], 'in_subset': i in set(sub),
                        'gold': json.loads(m[2]['content']), 'raw': raw, 'gen_tokens': len(ids),
                        'prompt_tokens': getattr(last, 'prompt_tokens', None), 'prompt_tps': getattr(last, 'prompt_tps', None),
                        'gen_tps': getattr(last, 'generation_tps', None), 'finish_reason': getattr(last, 'finish_reason', None),
                        'seconds': round(dt, 2), 'peak_gb': round(mx.get_peak_memory() / 1e9, 3)}) + '\n'); f.flush()
    if n % 20 == 0: print(f'{n} rows, {time.time()-t0:.0f}s, last {dt:.1f}s {len(ids)} tok', flush=True)
print(f'done {kind}: peak {mx.get_peak_memory()/1e9:.2f} GB total {time.time()-t0:.0f}s', flush=True)
