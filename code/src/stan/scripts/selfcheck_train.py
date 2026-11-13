"""selfcheck_train.py (12 Nov, Sage: run STAN on its own training rows). Feeds the first 40 training rows (seeded order, seed 7) to STAN v1 exactly as
infer_mlx.py feeds gold items (apply_chat_template, enable_thinking=False), parses the status and compares it with the row's own label.
Also renders one training row the way mlx_lm lora saw it, to check the chat template matches. Writes results/selfcheck_train.json."""
import json, os, random, collections as C
from common import *
os.environ['HF_HUB_OFFLINE'] = '1'
rows = [json.loads(l) for l in open(S + '/data/silver_v1/train.jsonl')]; random.Random(7).shuffle(rows); rows = rows[:40]
lk = gpu_lock()
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler
ad = open(S + '/runs/stan_v1/CHECKPOINT.txt').read().strip()
model, tok = load('Qwen/Qwen3-1.7B', adapter_path=ad if os.path.isdir(ad) else S + '/runs/stan_v1/ckpt250')
res = []; cm = C.Counter()
for r in rows:
    u = [m for m in r['messages'] if m['role'] != 'assistant']; gold = json.loads([m for m in r['messages'] if m['role'] == 'assistant'][-1]['content'])['status']
    p = tok.apply_chat_template(u, add_generation_prompt=True, tokenize=False, enable_thinking=False)
    out = generate(model, tok, p, max_tokens=120, sampler=make_sampler(temp=0.0))
    try: got = json.loads(out[out.index('{'):out.rindex('}') + 1])['status']
    except Exception: got = 'UNPARSED'
    cm[(gold, got)] += 1; res.append({'gold': gold, 'got': got, 'out': out[:200]})
train_view = tok.apply_chat_template(rows[0]['messages'], tokenize=False)
infer_view = tok.apply_chat_template([m for m in rows[0]['messages'] if m['role'] != 'assistant'], add_generation_prompt=True, tokenize=False, enable_thinking=False)
json.dump({'confusion': {'%s->%s' % k: v for k, v in cm.items()}, 'rows': res, 'train_view_tail': train_view[-300:], 'infer_view_tail': infer_view[-200:]}, open(S + '/results/selfcheck_train.json', 'w'), indent=1)
print(dict(cm)); print('TRAIN VIEW TAIL:', repr(train_view[-260:])); print('INFER VIEW TAIL:', repr(infer_view[-160:]))
