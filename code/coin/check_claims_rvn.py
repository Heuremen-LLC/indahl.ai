#!/usr/bin/env python3
"""Ravencoin: whitepaper statements read against the chain's own block record. Stdlib only. Writes claims_rvn.json.
Rules written before the outcomes were set. Outcomes: ABOVE / BELOW / CONSISTENT / CANNOT_TELL, delivered relative to stated.
RV1 block time: CONSISTENT if |mean gap - 60| <= 2 standard errors of the mean, else ABOVE or BELOW.
RV2 algorithm: the script recomputes no KawPow or x16r hashes, so the hash function is CANNOT_TELL. The nonce width in the header is reported.
RV3 and RV5: the whitepaper states no threshold for dominance or fairness, so figures are reported and the outcome is CANNOT_TELL.
RV4 and RV6: CONSISTENT if no block in the range has a paid coinbase output other than one miner payout, else BELOW (extra allocation found)."""
import json, glob, re, binascii, collections as C, statistics as S, math
rows = {}
for f in glob.glob("data/rvn_w*.jsonl") + glob.glob("data/rvn_live.jsonl") + ["data/rvn_part0_seed.jsonl", "data/rvn_genesis.jsonl"]:
    for l in open(f):
        r = json.loads(l)
        if "hash" in r: rows[r["height"]] = r
H = sorted(rows); rec = [h for h in H if h > 4000000][-3000:]; gen = [h for h in H if h <= 1000]
paid = lambda r: [(o["a"][0] if o["a"] else None, float(o["v"])) for o in r["coinbase_vout"] if float(o["v"]) > 0]
out = []
def add(i, quote, outcome, figures, rng): out.append({"id": i, "quote": quote, "outcome": outcome, "figures": figures, "heights": rng})
gaps = [rows[h]["time"] - rows[h-1]["time"] for h in rec if h-1 in rows]
m = S.mean(gaps); se = S.stdev(gaps) / math.sqrt(len(gaps))
o = "CONSISTENT" if abs(m-60) <= 2*se else ("ABOVE" if m > 60 else "BELOW")
add("RV1", "a block reward time of one minute", o, {"n_gaps": len(gaps), "mean_s": round(m, 2), "se_s": round(se, 2), "median_s": S.median(gaps),
    "share_under_5s": round(sum(g < 5 for g in gaps)/len(gaps), 4), "share_over_180s": round(sum(g > 180 for g in gaps)/len(gaps), 4)}, [rec[0], rec[-1]])
ne = C.Counter("32-bit" if isinstance(rows[h]["nonce"], int) and rows[h]["nonce"] < 2**32 else "other" for h in gen)
nr = C.Counter("hex string, up to 64 bits" if isinstance(rows[h]["nonce"], str) and len(rows[h]["nonce"]) <= 16 and int(rows[h]["nonce"], 16) >= 0 else "other" for h in rec)
add("RV2", "using the x16r algorithm", "CANNOT_TELL", {"early_nonce_form": dict(ne), "recent_nonce_form": dict(nr), "hash_recomputed": False}, [gen[0], rec[-1]])
tags = C.Counter(); addr = C.Counter()
for h in rec:
    b = binascii.unhexlify(rows[h]["coinbase_hex"]) if rows[h].get("coinbase_hex") else b""
    t = re.findall(rb"/[A-Za-z0-9._-]{3,24}/", b); tags[t[-1].decode() if t else "no tag"] += 1
    p = paid(rows[h]); addr[p[0][0] if p else "none"] += 1
n = len(rec); top = addr.most_common(5)
cum = 0; k50 = None
for i, (a, c) in enumerate(addr.most_common(), 1):
    cum += c
    if cum/n > .5: k50 = i; break
add("RV3", "intended to prevent immediate dominance by mining pools, and future dominance by ASIC mining equipment", "CANNOT_TELL",
    {"blocks": n, "top_payout_addresses_share": [[a[:8], round(c/n, 4)] for a, c in top], "addresses_to_pass_half": k50,
     "tag_share": [[t, round(c/n, 4)] for t, c in tags.most_common(6)], "note": "no threshold is stated; ASIC hardware is not visible in block records"}, [rec[0], rec[-1]])
ext = [h for h in gen if len(paid(rows[h])) != 1 or round(paid(rows[h])[0][1]) != 5000]
cov = [gen[0], gen[-1]]; complete = (len(gen) == 1000 and gen[0] == 1)
add("RV4", "Launch the token with no pre-mine", "CONSISTENT" if (complete and not ext) else ("BELOW" if ext else "CANNOT_TELL"),
    {"blocks_read": len(gen), "range": cov, "complete_from_block_1": complete, "blocks_not_one_5000_payout": len(ext), "genesis_block_zero_read": 0 in rows}, cov)
ea = C.Counter(paid(rows[h])[0][0] for h in gen if paid(rows[h]))
add("RV5", "a fair launch to widely distribute the tokens", "CANNOT_TELL",
    {"blocks": len(gen), "distinct_first_payout_addresses": len(ea), "top_share": [[a[:8], round(c/len(gen), 4)] for a, c in ea.most_common(3)], "note": "no threshold is stated"}, cov)
bad = [h for h in rec + gen if len(paid(rows[h])) != 1]
add("RV6", "There is no private, public, founder, or developer allocation set aside", "CONSISTENT" if not bad else "BELOW",
    {"blocks_read": len(rec)+len(gen), "blocks_with_other_than_one_paid_output": len(bad), "first_few": bad[:5]}, [gen[0], rec[-1]])
json.dump({"chain": "Ravencoin", "source": "explorer.rvn.zelcore.io public Insight API", "statements": out}, open("claims_rvn.json", "w"), indent=1)
for s in out: print(s["id"], s["outcome"], json.dumps(s["figures"])[:230])
