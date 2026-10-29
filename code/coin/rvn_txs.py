#!/usr/bin/env python3
"""rvn_txs.py: reads the non-coinbase transactions of every collected Ravencoin block from a public Insight explorer (read-only), appending compact rows to data/tx_rows.jsonl.
Row: height, time, txid, in_addrs (distinct), n_in, n_out, total_out, outs [address, value] kept only when the transaction has 20 or more outputs. Resumable: data/tx_done.json lists scanned heights."""
import os, sys, json, glob, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); B = 'https://explorer.rvn.zelcore.io/api'; LIM = int(sys.argv[1]) if len(sys.argv) > 1 else 10**9
def get(p):
    for a in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(B + p, headers={'User-Agent': 'heuremen-coin-index/0.1'}), timeout=30) as r: return json.loads(r.read())
        except Exception: time.sleep(2 * (a + 1))
rows = {}
for f in glob.glob('data/rvn_*.jsonl'):
    for l in open(f):
        r = json.loads(l)
        if 'hash' in r and r['height'] > 4000000 and r.get('ntx', 1) > 1: rows[r['height']] = r
done = set(json.load(open('data/tx_done.json'))) if os.path.exists('data/tx_done.json') else set()
todo = [h for h in sorted(rows, reverse=True) if h not in done][:LIM]; print('blocks to scan', len(todo), flush=True)
out = open('data/tx_rows.jsonl', 'a'); ok = []
def one(h):
    b = get(f"/block/{rows[h]['hash']}")
    if not b: return h, None
    res = []
    for tid in b['tx'][1:]:
        t = get(f'/tx/{tid}')
        if not t: return h, None
        vin = [v.get('addr') for v in t.get('vin', []) if v.get('addr')]; vo = t.get('vout', [])
        outs = [[(o.get('scriptPubKey') or {}).get('addresses', [None])[0], float(o.get('value', 0))] for o in vo]
        row = dict(height=h, time=t.get('time'), txid=tid, in_addrs=sorted(set(vin)), n_in=len(t.get('vin', [])), n_out=len(vo), total_out=round(sum(x[1] for x in outs), 8))
        if len(vo) >= 20: row['outs'] = outs
        res.append(row)
    return h, res
n = 0
with ThreadPoolExecutor(6) as ex:
    for h, res in ex.map(one, todo):
        if res is None: continue
        for r in res: out.write(json.dumps(r) + '\n')
        done.add(h); n += 1
        if n % 100 == 0: out.flush(); json.dump(sorted(done), open('data/tx_done.json', 'w')); print(n, 'blocks', flush=True)
out.close(); json.dump(sorted(done), open('data/tx_done.json', 'w')); print('done', n)
