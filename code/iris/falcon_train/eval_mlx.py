"""eval_mlx.py KEY [ADAPTER]: answers the items of faultsbench_tA and faultsbench_tB with Falcon3 3B Instruct (bf16, MLX), greedy decoding, three arms (bare, bare_copy, guard), written in the layout score.py reads: faultsbench_tX/out/<KEY>/<arm>.jsonl. Resumable. Replies counts go to the IRIS page (key train). One worker."""
import json, os, sys, subprocess, datetime
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(HERE)
KEY = sys.argv[1]; ADAPTER = sys.argv[2] if len(sys.argv) > 2 else None
model, tok = load(os.path.join(HERE, 'models', 'Falcon3-3B-Instruct'), adapter_path=os.path.join(HERE, ADAPTER) if ADAPTER else None)
samp = make_sampler(temp=0.0)
def call(user):
    p = tok.apply_chat_template([{'role': 'user', 'content': user}], add_generation_prompt=True, tokenize=False)
    return generate(model, tok, prompt=p, max_tokens=1500, sampler=samp, verbose=False)
def publish():
    subprocess.Popen([sys.executable, os.path.join(HERE, 'publish_train_status.py')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
n = 0
for S in ('tA', 'tB'):
    d = os.path.join(B, f'faultsbench_{S}'); sys.path.insert(0, d)
    import importlib; spec = importlib.util.spec_from_file_location('items_' + S, os.path.join(d, 'items.py')); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    IT = json.load(open(os.path.join(d, 'items.json'))); out = os.path.join(d, 'out', KEY); os.makedirs(out, exist_ok=True)
    for arm in ('bare', 'bare_copy', 'guard'):
        p = os.path.join(out, arm + '.jsonl'); seen = {json.loads(l)['id'] for l in open(p)} if os.path.exists(p) else set(); f = open(p, 'a')
        for it in IT:
            if it['id'] in seen: continue
            try: txt, err = call(m.prompt(it, 'guard' if arm == 'guard' else 'bare')), None
            except Exception as e: txt, err = '', str(e)[:200]
            f.write(json.dumps(dict(id=it['id'], raw=txt, done_reason='stop' if not err else None, error=err)) + '\n'); f.flush(); n += 1
            if n % 10 == 0: publish()
        f.close()
    sys.path.pop(0)
publish(); print(KEY, 'done', flush=True)
