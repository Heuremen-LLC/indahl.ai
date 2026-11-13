"""Score a model (with or without a LoRA adapter) on the held-out chunk sets. Chunk-level: FLAG if the model lists any error.
Reports flag rate on positive chunks (recall) and on negative chunks (false-flag rate), each with a Wilson 95% interval, plus parse failures.
The untrained base model is scored by the same script so the two rows are like for like.
Usage: venv/bin/python eval_mlx.py MODEL [ADAPTER|-] SET_FILE OUT_NAME"""
import json, sys, os
from math import sqrt
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler
model_id, adapter, setf, name = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
H = os.path.dirname(os.path.abspath(__file__))
def wilson(k, n, z=1.959964):
    if not n: return None
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round((c - h) / d, 3), round((c + h) / d, 3)]
model, tok = load(model_id, adapter_path=None if adapter == '-' else adapter)
samp = make_sampler(temp=0.0)
cnt = {'pos': 0, 'pos_flag': 0, 'neg': 0, 'neg_flag': 0, 'parse_fail': 0}; per = []
for l in open(setf):
    x = json.loads(l); msgs = [x['messages'][0]]
    prompt = tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False)
    out = generate(model, tok, prompt=prompt, max_tokens=400, sampler=samp)
    try:
        s = out[out.index('{'):out.rindex('}') + 1]; flag = bool(json.loads(s).get('errors'))
    except Exception:
        cnt['parse_fail'] += 1; flag = None
    k = 'pos' if x['label'] else 'neg'; cnt[k] += 1; cnt[k + '_flag'] += bool(flag)
    per.append({'arxiv': x['arxiv'], 'chunk': x['chunk'], 'label': x['label'], 'flag': flag})
res = dict(cnt, recall=wilson(cnt['pos_flag'], cnt['pos']), false_flag=wilson(cnt['neg_flag'], cnt['neg']),
           model=model_id, adapter=adapter, set=os.path.basename(setf))
os.makedirs(os.path.join(H, 'results'), exist_ok=True)
json.dump({'summary': res, 'items': per}, open(os.path.join(H, 'results', name + '.json'), 'w'), indent=1)
print(json.dumps(res))
