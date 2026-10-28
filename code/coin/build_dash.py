#!/usr/bin/env python3
"""Bake dashboard/data.json from the collected Ravencoin pulls. Read-only, no prices."""
import json, glob, re, binascii, collections as C, statistics as S, time
rows = {}
for f in glob.glob("data/rvn_w*.jsonl") + glob.glob("data/rvn_part0_seed.jsonl") + glob.glob("data/rvn_genesis.jsonl") + glob.glob("data/rvn_live.jsonl"):
    for l in open(f):
        r = json.loads(l)
        if "hash" in r: rows[r["height"]] = r
B = [rows[h] for h in sorted(rows)]
RB = [r for r in B if r["height"] > 4000000][-3000:]
gaps = [b["time"]-a["time"] for a, b in zip(RB, RB[1:]) if b["height"] == a["height"]+1]
tags = C.Counter(); addr = C.Counter()
for r in RB:
    h = binascii.unhexlify(r["coinbase_hex"]) if r.get("coinbase_hex") else b""
    m = re.findall(rb"/[A-Za-z0-9._-]{3,24}/", h); tags[m[-1].decode() if m else "no tag"] += 1
    paid = [o for o in r["coinbase_vout"] if o["a"] and float(o["v"]) > 0]
    addr[paid[0]["a"][0] if paid else "none"] += 1
n = len(RB)
hist = [0]*13
for g in gaps: hist[min(12, max(0, g)//30)] += 1
qs = S.quantiles(gaps, n=20) if len(gaps) > 20 else []
out = {"gap_q": {"p10": qs[1], "p25": qs[4], "p50": qs[9], "p75": qs[14], "p90": qs[17]} if qs else {}, "gap_under5": round(sum(g < 5 for g in gaps)/len(gaps), 3) if gaps else None, "gap_over180": round(sum(g > 180 for g in gaps)/len(gaps), 3) if gaps else None, "gaps_n": len(gaps), "read_rows": len(rows), "target_rows": 4000, "chain": "Ravencoin", "read": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), "blocks": n,
       "tip": RB[-1]["height"] if RB else None, "hashes": [r["hash"] for r in B[-400:]], "latest_hash": B[-1]["hash"] if B else "",
       "gap_mean": round(S.mean(gaps), 2) if gaps else None, "gap_median": S.median(gaps) if gaps else None,
       "hist": hist, "hist_bin": 30, "stated_gap": 60,
       "tags": [[k, v] for k, v in tags.most_common(8)],
       "top_addr": [[a[:6]+"…"+a[-4:], round(c/n, 3)] for a, c in addr.most_common(6)] if n else []}
import os
def delivered(c):
    f = c["figures"]; i = c["id"]
    if i == "RV1": return f"Mean {f['mean_s']} s over {f['n_gaps']:,} gaps, median {f['median_s']} s. {f['share_under_5s']*100:.1f}% under 5 s, {f['share_over_180s']*100:.1f}% over 180 s."
    if i == "RV2": return "Blocks 1 to 1,000 carry a 32-bit nonce. Recent blocks carry a hex nonce of up to 64 bits. The hash function is not recomputed here."
    if i == "RV3": return f"Over the last {f['blocks']:,} blocks the first payout address takes {f['top_payout_addresses_share'][0][1]*100:.1f}% and {f['addresses_to_pass_half']} addresses pass half. No threshold is stated."
    if i == "RV4": return f"Blocks {f['range'][0]} to {f['range'][1]:,}: {f['blocks_not_one_5000_payout']} blocks pay anything other than one 5,000 payout."
    if i == "RV5": return f"{f['distinct_first_payout_addresses']} different first payout addresses in {f['blocks']:,} blocks, the largest takes {f['top_share'][0][1]*100:.1f}%. No threshold is stated."
    if i == "RV6": return f"{f['blocks_with_other_than_one_paid_output']} of {f['blocks_read']:,} blocks read have a second paid coinbase output."
    return ""
out["claims"] = [dict(s, delivered=delivered(s)) for s in json.load(open("claims_rvn.json"))["statements"]] if os.path.exists("claims_rvn.json") else []
json.dump(out, open("dashboard/data.json", "w")); print(n, "blocks baked")
