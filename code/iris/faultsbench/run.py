"""run.py MODEL: resumable; out/<model>/<arm>.jsonl. Our own model seat only (127.0.0.1:11500). Arms: bare, bare_copy (exact repeat = floor), guard."""
import json, sys, os, urllib.request
from items import prompt
H = 'http://127.0.0.1:11500/api/chat'; HERE = os.path.dirname(os.path.abspath(__file__)); MODEL = sys.argv[1]
OUT = os.path.join(HERE, 'out', MODEL.replace(':', '_')); os.makedirs(OUT, exist_ok=True)
IT = json.load(open(os.path.join(HERE, 'items.json')))
def call(user):
    body = {'model': MODEL, 'messages': [{'role': 'user', 'content': user}], 'stream': False, 'think': False,
            'options': {'temperature': 0, 'seed': 20261025, 'num_ctx': 4096, 'num_predict': 400}}
    for _ in (1, 2):
        try:
            r = json.loads(urllib.request.urlopen(urllib.request.Request(H, data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'}), timeout=300).read())
            return r.get('message', {}).get('content', ''), r.get('done_reason'), None
        except Exception as e:
            if 'think' in str(e) and 'think' in body: body.pop('think'); continue
            return '', None, str(e)[:200]
    return '', None, 'retry exhausted'
for arm in ('bare', 'bare_copy', 'guard'):
    p = os.path.join(OUT, arm + '.jsonl'); seen = {json.loads(l)['id'] for l in open(p)} if os.path.exists(p) else set(); f = open(p, 'a')
    for it in IT:
        if it['id'] in seen: continue
        txt, dr, err = call(prompt(it, 'guard' if arm == 'guard' else 'bare'))
        f.write(json.dumps(dict(id=it['id'], raw=txt, done_reason=dr, error=err)) + '\n'); f.flush()
    f.close(); print(MODEL, arm, 'done', flush=True)
