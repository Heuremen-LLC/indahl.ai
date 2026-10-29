#!/usr/bin/env python3
"""rvn_history.py: extends the Ravencoin block + coinbase record backwards from a public Insight explorer. Read-only, six workers, resumable.
Same fields as rvn_collect.py. usage: rvn_history.py FROM_HEIGHT TO_HEIGHT   (inclusive range, scanned newest first). Appends to data/rvn_hist.jsonl."""
import os, sys, json, glob, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); B = 'https://explorer.rvn.zelcore.io/api'
lo, hi = int(sys.argv[1]), int(sys.argv[2])
def get(p):
    for a in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(B + p, headers={'User-Agent': 'heuremen-coin-index/0.1'}), timeout=30) as r: return json.loads(r.read())
        except Exception: time.sleep(2 * (a + 1))
have = set()
for f in glob.glob('data/rvn_*.jsonl'):
    for l in open(f):
        try: r = json.loads(l)
        except Exception: continue
        if 'hash' in r: have.add(r['height'])
todo = [h for h in range(hi, lo - 1, -1) if h not in have]; print('to read', len(todo), flush=True)
out = open('data/rvn_hist.jsonl', 'a')
def one(h):
    time.sleep(0.2); bh = (get(f'/block-index/{h}') or {}).get('blockHash'); b = get(f'/block/{bh}') if bh else None
    if not b: return None
    tx = get(f"/tx/{b['tx'][0]}") or {}
    return {'height': b['height'], 'hash': b['hash'], 'prev': b.get('previousblockhash'), 'time': b['time'], 'bits': b.get('bits'), 'nonce': b.get('nonce'), 'size': b.get('size'), 'ntx': len(b['tx']),
            'coinbase_vout': [{'v': o.get('value'), 'a': (o.get('scriptPubKey') or {}).get('addresses')} for o in tx.get('vout', [])], 'coinbase_hex': (tx.get('vin') or [{}])[0].get('coinbase'), '_read': time.time()}
n = miss = 0
with ThreadPoolExecutor(6) as ex:
    for r in ex.map(one, todo):
        if r is None: miss += 1; continue
        out.write(json.dumps(r) + '\n'); n += 1
        if n % 500 == 0: out.flush(); print(n, 'blocks', flush=True)
out.close(); print('done', n, 'missed', miss)
