"""run.py BUILD PORT MODEL: resumable; out/<build>/<model>/<arm>.jsonl. Our models only, on a server drive.sh starts for one build. Arms: bare, bare_copy (exact repeat = floor), guard.
Differs from faultsbench2_mac_cross/run.py only in the server address and the output folder, and it does not publish a status page."""
import json, sys, os, urllib.request, subprocess
from items import prompt
BUILD, PORT, MODEL = sys.argv[1], sys.argv[2], sys.argv[3]; H = f'http://127.0.0.1:{PORT}/api/chat'; HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out', BUILD, MODEL.replace(':', '_')); os.makedirs(OUT, exist_ok=True)
IT = json.load(open(os.path.join(HERE, 'items.json')))
def call(user):
    body = {'model': MODEL, 'messages': [{'role': 'user', 'content': user}], 'stream': False, 'think': False,
            'options': {'temperature': 0, 'seed': 20261025, 'num_ctx': 8192, 'num_predict': 1500}}
    for _ in (1, 2):
        try:
            r = json.loads(urllib.request.urlopen(urllib.request.Request(H, data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'}), timeout=900).read())
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
    f.close(); print(BUILD, MODEL, arm, 'done', flush=True)
