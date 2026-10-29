#!/usr/bin/env python3
"""coin_tick.py: one COIN round, run by Nova's tick bus as a rider. Reads the Ravencoin blocks that arrived since the last round
(public Insight explorer, read-only, at most 60 per round), appends them to data/rvn_live.jsonl, rescores the whole-window statements,
rebuilds the page data and publishes it to the page's KV key."""
import os, sys, json, time, subprocess, urllib.request
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door')
B = 'https://explorer.rvn.zelcore.io/api'
def get(p):
    for a in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(B + p, headers={'User-Agent': 'heuremen-coin-index/0.1'}), timeout=30) as r: return json.loads(r.read())
        except Exception: time.sleep(2 * (a + 1))
st = get('/status')
if not st: print('coin: explorer unreachable'); sys.exit(0)
tip = st['info']['blocks']; have = 0
for fn in os.listdir('data'):
    if fn.startswith('rvn_') and fn.endswith('.jsonl'):
        for l in open('data/' + fn):
            try: have = max(have, json.loads(l).get('height', 0))
            except Exception: pass
start = max(have + 1, tip - 59); n = 0
if start > have + 1 and have: print('coin: heights', have + 1, 'to', start - 1, 'were not read this round (60 per round cap):', start - have - 1, 'unread')   # 29 Oct (audit): the gap is printed, not silent
with open('data/rvn_live.jsonl', 'a') as f:
    for h in range(start, tip):
        bh = (get(f'/block-index/{h}') or {}).get('blockHash'); b = get(f'/block/{bh}') if bh else None
        if not b: f.write(json.dumps({'height': h, '_status': 'NOTHING_RETURNED', '_read': time.time()}) + '\n'); continue
        tx = get(f"/tx/{b['tx'][0]}")
        if not tx: f.write(json.dumps({'height': h, '_status': 'NOTHING_RETURNED', 'why': 'coinbase read failed', '_read': time.time()}) + '\n'); continue   # 29 Oct (audit): a failed read is not a block signed by no one
        f.write(json.dumps({'height': b['height'], 'hash': b['hash'], 'prev': b.get('previousblockhash'), 'time': b['time'], 'bits': b.get('bits'), 'nonce': b.get('nonce'), 'size': b.get('size'), 'ntx': len(b['tx']),
            'coinbase_vout': [{'v': o.get('value'), 'a': (o.get('scriptPubKey') or {}).get('addresses')} for o in tx.get('vout', [])], 'coinbase_hex': (tx.get('vin') or [{}])[0].get('coinbase'), '_read': time.time()}) + '\n'); f.flush(); n += 1; time.sleep(0.2)
subprocess.run([sys.executable, 'check_claims_rvn.py'], capture_output=True); subprocess.run([sys.executable, 'build_dash.py'], capture_output=True)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
p = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'coin_live', '--path', os.path.join(H, 'dashboard', 'data.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
print('coin:', n, 'new blocks,', 'coin_live published' if p.returncode == 0 else 'publish FAILED')
