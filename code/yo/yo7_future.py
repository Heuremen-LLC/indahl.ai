"""yo7_future.py -- PLAN_YO_V7.md FUTURE7: every IBM record the QIA mirror saved with a stamp later than the plan's commit time (e313664), one
item each, built as the live reader builds it (yo2_data.item_a, k = 0). Writes data7/future_items.jsonl once, so every model scores the same items."""
import json, gzip, glob, os, sys, subprocess, datetime as dt, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(HERE); sys.path.insert(0, HERE)
import yo2_data as D
OUT = HERE + '/data7/future_items.jsonl'
if os.path.exists(OUT): print('future items already built:', sum(1 for _ in open(OUT))); sys.exit(0)
T0 = dt.datetime.fromisoformat(subprocess.run(['git', '-C', HERE, 'log', '-1', '--format=%cI', 'e313664'], capture_output=True, text=True).stdout.strip())
seen = {}
for p in sorted(glob.glob(os.path.join(B, 'qia_mirror', 'records', '*', '*.json.gz'))):
    try: d = json.load(gzip.open(p))
    except Exception: continue
    S = D.when(d['last_update_date'])
    if S <= T0: continue
    Q = {}
    for i, qs in enumerate(d['qubits']):
        e = {x['name']: (x.get('value'), x.get('date')) for x in qs if x.get('name') in D.FIELDS}
        if all(f in e and e[f][0] is not None and e[f][1] for f in ('T1', 'T2')): Q[i] = e
    if len(Q) >= 8: seen[(d['backend_name'], S)] = Q
items = [D.item_a(b, S, Q, 0) for (b, S), Q in sorted(seen.items(), key=lambda kv: (kv[0][1], kv[0][0]))]
with open(OUT, 'w') as fh:
    for it in items: fh.write(json.dumps(it) + '\n')
open(HERE + '/DATA_YO_V7_FUTURE.sha256', 'w').write(hashlib.sha256(open(OUT, 'rb').read()).hexdigest() + '  data7/future_items.jsonl\n')
print('FUTURE7: records stamped after', T0.isoformat(), ':', len(items))
