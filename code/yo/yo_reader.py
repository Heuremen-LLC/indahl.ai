"""yo_reader.py -- tick-bus rider: YO reads IBM's calibration records live (31 Oct 2026, his "time to put Yo to work").
For every new record the QIA mirror saves (qia_mirror/changes.jsonl), YO gets the Job A prompt of PLAN_YO_V2 for that record (8 qubits,
seeded by processor and stamp) and flags stale and zero entries; the code computes the true answer from the same record. Both are kept in
yo/live_reads.jsonl and the latest are published to the QIA page (KV key yo_live -> indahl.ai/qia/yo.json).
Gate: runs only while yo/LIVE_READER_ON exists, written after YO's TEST reading beat both Job A baselines under the plan's rule.
One GPU job per machine: skips the pass while another model job runs. At most 6 records per pass."""
import os, sys, json, gzip, time, subprocess, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(HERE); sys.path.insert(0, HERE)
W = os.path.join(B, 'cloudflare-workers', 'heuremen-door'); NS = 'ecb59d96b07c43bdac14271687eae5af'
GATE = os.path.join(HERE, 'LIVE_READER_ON'); ST = os.path.join(HERE, '.reader_state.json'); OUT = os.path.join(HERE, 'live_reads.jsonl')
if not os.path.exists(GATE): print('yo reader: gate closed (no LIVE_READER_ON)'); sys.exit(0)
busy = subprocess.run("pgrep -f 'mlx_lm|yo[0-9]_eval|yo[0-9]_run|lighteval|lm_eval|falcon_train/train'", shell=True, capture_output=True, text=True).stdout.split()
if busy: print('yo reader: another model job holds the GPU, skipped'); sys.exit(0)
st = json.load(open(ST)) if os.path.exists(ST) else {'at': 0}
open(os.path.join(HERE, '.reader_ran'), 'w').write(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))   # heartbeat for the watch: the reader ran (gate open, GPU free)
_rs = [r for r in map(json.loads, open(os.path.join(B, 'qia_mirror', 'changes.jsonl'))) if r.get('at', 0) > st['at'] and r.get('file')]
new = _rs[:6] if os.path.exists(ST) else _rs[-6:]   # first run starts at the newest records, then reads forward in order, 6 per run
WAITING = len(_rs) - len(new) if os.path.exists(ST) else 0
def publish():
    rows = [json.loads(l) for l in open(OUT)] if os.path.exists(OUT) else []
    d = dict(updated=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), n=len(rows), mean=round(sum(r['score'] for r in rows) / len(rows), 3) if rows else None,
             exact=sum(r['score'] == 1.0 for r in rows), latest=rows[-12:][::-1], adapter=open(GATE).read().strip(), waiting=WAITING)
    f = os.path.join(HERE, 'yo_live.json'); json.dump(d, open(f, 'w'))
    env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
    r = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'yo_live', '--path', f, '--namespace-id', NS, '--remote'], cwd=W, env=env, capture_output=True, text=True)
    print('yo reader: published' if r.returncode == 0 else 'yo reader: publish FAILED')
if not new: print('yo reader: no new record'); publish() if not os.path.exists(os.path.join(HERE, 'yo_live.json')) else None; sys.exit(0)
from yo2_data import item_a, when, FIELDS, render
def _f1(p, t):   # the Job A scorer of yo2_eval.py, unchanged (that file runs as a script, so it is copied, not imported)
    p, t = set(p), set(t)
    if not p and not t: return 1.0
    if not p or not t: return 0.0
    tp = len(p & t); return 0.0 if tp == 0 else 2 * tp / (len(p) + len(t))
def score(it, out):
    t = json.loads(it['answer'])
    try: p = json.loads(out[out.index('{'):out.rindex('}') + 1])
    except Exception: return 0.0, 'unparsed'
    try: return (_f1([int(x) for x in p.get('stale', [])], t['stale']) + _f1([str(x) for x in p.get('zero', [])], t['zero'])) / 2, 'json'
    except Exception: return 0.0, 'unparsed'
from mlx_lm import load, generate
ADP = open(GATE).read().split()[0]   # 1 Nov: the gate file names the adapter at work (adapters/v4 since the v4 post)
model, tok = load('Qwen/Qwen3-1.7B', adapter_path=os.path.join(HERE, ADP))
for r in new:
    p = os.path.join(B, 'qia_mirror', 'records', r['backend'], r['file'])
    if not os.path.exists(p): continue
    d = json.load(gzip.open(p)); S = when(d['last_update_date']); Q = {}
    for i, qs in enumerate(d['qubits']):
        e = {x['name']: (x.get('value'), x.get('date')) for x in qs if x.get('name') in FIELDS}
        if all(f in e and e[f][0] is not None and e[f][1] for f in ('T1', 'T2')): Q[i] = e
    if len(Q) < 8: continue
    it = item_a(r['backend'], S, Q, 0)
    out = generate(model, tok, prompt=render(it['prompt']), max_tokens=200, verbose=False); s, how = score(it, out)
    try: yo = json.loads(out[out.index('{'):out.rindex('}') + 1])
    except Exception: yo = None
    row = dict(backend=r['backend'], stamp=str(S)[:16] + ' UTC', read=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), yo=yo, code=json.loads(it['answer']), score=round(s, 3), parsed=how, model=ADP.split('/')[-1])
    with open(OUT, 'a') as f: f.write(json.dumps(row) + '\n')
    st['at'] = max(st['at'], r['at']); json.dump(st, open(ST, 'w'))
    print('yo reader:', r['backend'], row['stamp'], 'score', row['score'])
publish()
