#!/usr/bin/env python3
"""Bitcoin headers from mempool.space, 15 per call, newest first. usage: btc_headers.py OUT.jsonl COUNT"""
import sys, json, time, urllib.request
out, count = sys.argv[1], int(sys.argv[2])
def get(u):
    for a in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent":"heuremen-coin-index/0.1"}), timeout=30) as r: return json.loads(r.read())
        except Exception: time.sleep(3*(a+1))
tip = get("https://mempool.space/api/blocks/tip/height"); n = 0; h = tip
with open(out, "w") as f:
    f.write(json.dumps({"_chain":"bitcoin","_tip":tip,"_read":time.time(),"_source":"mempool.space/api/blocks"}) + "\n")
    while n < count:
        bl = get(f"https://mempool.space/api/blocks/{h}")
        if not bl: break
        for b in bl:
            f.write(json.dumps({k: b[k] for k in ("id","height","version","previousblockhash","merkle_root","timestamp","bits","nonce","difficulty","tx_count","size","weight") if k in b} | {"extras_pool": (b.get("extras") or {}).get("pool",{}).get("name")}) + "\n"); n += 1
        h = bl[-1]["height"] - 1; time.sleep(0.4)
print("bitcoin", n, "tip", tip)
