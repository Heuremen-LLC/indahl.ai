"""eval_score.py (13 Nov 2026): a confidence score per chunk, so the flag cutoff can be read as a curve instead of one yes/no.
The models answer {"errors": []} (clean) or {"errors": [{...}]} (flag). After the shared prefix {"errors": [ the next token is either the
close of an empty list or the opening of an entry. Score = P(entry) / (P(entry) + P(close)) at that position, from one forward pass, with
the chat template and prompt exactly as eval_mlx.py uses them. No sampling, no generation.
Usage: venv/bin/python eval_score.py MODEL [ADAPTER|-] SET_FILE OUT_NAME   -> results/<OUT_NAME>_scores.json"""
import json, sys, os
import mlx.core as mx
from mlx_lm import load
model_id, adapter, setf, name = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
H = os.path.dirname(os.path.abspath(__file__))
model, tok = load(model_id, adapter_path=None if adapter == '-' else adapter)

def split_point(prompt):
    """Token ids for prompt + '{"errors": [', and the first token of each continuation (close vs entry)."""
    a = tok.encode(prompt + '{"errors": []}', add_special_tokens=False)
    b = tok.encode(prompt + '{"errors": [{"code": "F1"}]}', add_special_tokens=False)
    i = 0
    while i < min(len(a), len(b)) and a[i] == b[i]: i += 1
    return a[:i], a[i], b[i]

items = []
for l in open(setf):
    x = json.loads(l); msgs = [x['messages'][0]]
    prompt = tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False)
    pre, t_close, t_entry = split_point(prompt)
    logits = model(mx.array(pre)[None])[0, -1].astype(mx.float32)
    lp = logits - mx.logsumexp(logits)
    pc, pe = float(mx.exp(lp[t_close])), float(mx.exp(lp[t_entry]))
    items.append({'arxiv': x['arxiv'], 'chunk': x['chunk'], 'label': x['label'], 'p_close': pc, 'p_entry': pe,
                  'mass_on_two': round(pc + pe, 4), 'score': pe / (pc + pe) if pc + pe > 0 else None})
os.makedirs(os.path.join(H, 'results'), exist_ok=True)
json.dump({'model': model_id, 'adapter': adapter, 'set': os.path.basename(setf), 'items': items},
          open(os.path.join(H, 'results', name + '_scores.json'), 'w'), indent=1)
low = sum(1 for i in items if i['mass_on_two'] < 0.9)
print(json.dumps({'name': name, 'items': len(items), 'items_with_under_0.9_mass_on_the_two_tokens': low}))
