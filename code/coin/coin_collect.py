#!/usr/bin/env python3
"""Read-only COIN collector: block records from Blockchair's public API, no keys, no prices.
usage: coin_collect.py OUTDIR PAGES chain [chain ...]   (100 blocks per page, newest first)"""
import sys, json, time, urllib.request, os
out, pages, chains = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
os.makedirs(out, exist_ok=True)
KEEP = ("id","hash","time","merkle_root","version","size","nonce","bits","difficulty","coinbase_data_hex","guessed_miner","transaction_count","version_hex","witness_count","reward","cdd_total")
def get(u):
    for a in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent":"heuremen-coin-index/0.1"}), timeout=30) as r:
                return json.loads(r.read())
        except Exception as e:
            err = repr(e)[:100]; time.sleep(5*(a+1))
    return {"error": err}
for c in chains:
    n = 0; path = f"{out}/{c}.jsonl"
    with open(path, "a") as f:
        for p in range(pages):
            j = get(f"https://api.blockchair.com/{c}/blocks?limit=100&offset={p*100}")
            d = j.get("data")
            if not d:
                f.write(json.dumps({"_status": j.get("error") or j.get("context",{}).get("error") or "empty", "page": p, "_read": time.time()}) + "\n"); break
            for b in d:
                f.write(json.dumps({k: b[k] for k in KEEP if k in b}) + "\n"); n += 1
            time.sleep(2)
    print(c, n, flush=True)
