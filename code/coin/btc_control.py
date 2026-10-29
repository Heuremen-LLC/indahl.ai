#!/usr/bin/env python3
"""btc_control.py: the control chain for the linkage test (PLAN_TRENDS.md addendum 2). For each Bitcoin pool, the addresses mempool.space publishes for it, and the batch payouts
(transactions spending from one of those addresses with 20 or more outputs) in the last 14 days. Read-only. Writes data/btc_ctl_<slug>.jsonl and data/btc_ctl_pools.json."""
import os, sys, json, time, urllib.request
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); B = 'https://mempool.space/api'; NOW = time.time(); CUT = NOW - 14 * 86400
POOLS = ['antpool', 'btccom', 'foundryusa', 'f2pool', 'viabtc', 'spiderpool', 'marapool', 'luxor', 'braiinspool']
def get(p):
    for a in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(B + p, headers={'User-Agent': 'heuremen-coin-index/0.1'}), timeout=30) as r: return json.loads(r.read())
        except Exception as e:
            time.sleep(1.5 * (a + 1))
    return None
meta = {}
for slug in POOLS:
    d = get(f'/v1/mining/pool/{slug}'); time.sleep(0.3)
    if not d: print(slug, 'NOTHING_RETURNED'); continue
    addrs = d['pool'].get('addresses', []); meta[slug] = dict(name=d['pool']['name'], n_addresses=len(addrs), read=time.time(), source=f'https://mempool.space/api/v1/mining/pool/{slug}')
    f = open(f'data/btc_ctl_{slug}.jsonl', 'w'); nb = 0; seen = set(); aset = set(addrs)
    for a in addrs[:60]:
        last = ''; pages = 0
        while pages < 6:
            txs = get(f'/address/{a}/txs/chain' + (f'/{last}' if last else '')); time.sleep(0.25); pages += 1
            if not txs: break
            for t in txs:
                bt = (t.get('status') or {}).get('block_time')
                if bt and bt < CUT: txs = []; break
                if t['txid'] in seen: continue
                spend = any(((v.get('prevout') or {}).get('scriptpubkey_address') in aset) for v in t.get('vin', []))
                if spend and len(t['vout']) >= 20:
                    seen.add(t['txid']); nb += 1
                    f.write(json.dumps(dict(pool=slug, from_addrs=sorted({(v.get('prevout') or {}).get('scriptpubkey_address') for v in t['vin'] if (v.get('prevout') or {}).get('scriptpubkey_address') in aset}), txid=t['txid'], time=bt, n_out=len(t['vout']),
                                            outs=[[o.get('scriptpubkey_address'), o['value']] for o in t['vout']])) + '\n')
            if not txs or len(txs) < 25: break
            last = txs[-1]['txid']
        f.flush()
    f.close(); meta[slug]['batches'] = nb; print(slug, len(addrs), 'addresses,', nb, 'batch payouts in 14 days', flush=True)
json.dump(meta, open('data/btc_ctl_pools.json', 'w'), indent=1); print('done')
