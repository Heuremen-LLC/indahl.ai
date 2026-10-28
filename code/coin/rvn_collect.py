#!/usr/bin/env python3
"""Ravencoin block + coinbase record from a public Insight explorer. Read-only. usage: rvn_collect.py OUT.jsonl COUNT"""
import sys, json, time, urllib.request
B = "https://explorer.rvn.zelcore.io/api"
out, count = sys.argv[1], int(sys.argv[2]); skip = int(sys.argv[3]) if len(sys.argv) > 3 else 0
def get(p):
    for a in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(B+p, headers={"User-Agent":"heuremen-coin-index/0.1"}), timeout=30) as r: return json.loads(r.read())
        except Exception: time.sleep(2*(a+1))
st = get("/status"); tip = st["info"]["blocks"]
with open(out, "w") as f:
    f.write(json.dumps({"_chain":"ravencoin","_tip":tip,"_source":B,"_read":time.time(),"_reward_field":st["info"].get("reward")}) + "\n")
    h = tip - 1 - skip
    for n in range(count):
        bh = (get(f"/block-index/{h}") or {}).get("blockHash")
        b = get(f"/block/{bh}") if bh else None
        if not b: f.write(json.dumps({"height": h, "_status": "NOTHING_RETURNED"}) + "\n"); h -= 1; continue
        tx = get(f"/tx/{b['tx'][0]}") or {}
        vout = tx.get("vout", [])
        f.write(json.dumps({"height": b["height"], "hash": b["hash"], "prev": b.get("previousblockhash"), "time": b["time"], "bits": b.get("bits"),
            "nonce": b.get("nonce"), "size": b.get("size"), "ntx": len(b["tx"]),
            "coinbase_vout": [{"v": o.get("value"), "a": (o.get("scriptPubKey") or {}).get("addresses")} for o in vout],
            "coinbase_hex": (tx.get("vin") or [{}])[0].get("coinbase"), "_read": time.time()}) + "\n")
        f.flush(); h -= 1; time.sleep(0.2)
print("done", count)
