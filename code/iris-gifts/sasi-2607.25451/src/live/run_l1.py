#!/usr/bin/env python3
"""L1 live reference arm (PLAN 0721111). His three sampled sequence files through the same public Pythia weights, FP32 on the Mac CPU,
with his generate call (first 32 ids as prompt, greedy, 32 new tokens, one beam, all-ones attention mask, pad id 0, batch 32).
Writes runs/l1_<model>_r<rep>.json with per-sequence outcomes (exact match, correct prefix length) and the aggregates.
Usage: run_l1.py <rep>"""
import os, sys, json, time, platform
import numpy as np, torch, transformers
from transformers import AutoModelForCausalLM
torch.set_num_threads(4)
H = os.path.dirname(os.path.abspath(__file__)); REP = int(sys.argv[1]); M = json.load(open(os.path.join(H, 'l1_models.json')))
S = os.path.join(H, '..', '..', 'theirs', 'hf', 'sampled_data'); os.makedirs(os.path.join(H, 'runs'), exist_ok=True)
for tag in ('pythia-160m-deduped', 'pythia-410m-deduped', 'pythia-1b-deduped'):
    repo = 'EleutherAI/' + tag; t0 = time.time()
    p = M[repo].get('path')
    model = AutoModelForCausalLM.from_pretrained(p if p and os.path.isdir(p) else repo, revision=None if p and os.path.isdir(p) else M[repo]['revision'], dtype=torch.float32).eval()
    seqs = np.load(os.path.join(S, 'sampled_%s_n500_s0.npy' % tag), allow_pickle=False)
    rows = []
    with torch.no_grad():
        for i in range(0, len(seqs), 32):
            b = torch.from_numpy(seqs[i:i + 32]); pr, tr = b[:, :32], b[:, 32:]
            out = model.generate(pr, attention_mask=torch.ones_like(pr), max_new_tokens=32, do_sample=False, num_beams=1, pad_token_id=0)
            g = out[:, 32:64]; m = (g == tr)
            fw = (~m).float().argmax(dim=1); al = m.all(dim=1); pl = torch.where(al, torch.full_like(fw, 32), fw)
            for j in range(len(b)): rows.append({'i': i + j, 'exact': bool(al[j]), 'prefix': int(pl[j]), 'tok_acc': float(m[j].float().mean())})
    n = len(rows)
    res = {'model': repo, 'revision': M[repo]['revision'], 'dtype': 'float32', 'device': 'cpu', 'rep': REP, 'n': n,
           'exact_match': sum(r['exact'] for r in rows) / n, 'mean_prefix': float(np.mean([r['prefix'] for r in rows])),
           'token_acc': float(np.mean([r['tok_acc'] for r in rows])), 'seconds': round(time.time() - t0, 1),
           'torch': torch.__version__, 'transformers': transformers.__version__, 'python': platform.python_version(), 'machine': platform.platform(),
           'at_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'rows': rows}
    json.dump(res, open(os.path.join(H, 'runs', 'l1_%s_r%d.json' % (tag, REP)), 'w'))
    print(tag, 'rep', REP, 'exact', res['exact_match'], 'prefix', round(res['mean_prefix'], 2), res['seconds'], 's', flush=True)
    del model
