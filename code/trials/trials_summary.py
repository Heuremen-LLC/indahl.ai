#!/usr/bin/env python3
"""TRIALS summary per PLAN.md + Addendum 1. Reads data/records.jsonl, writes data/summary.json."""
import json, math, collections
R = [json.loads(l) for l in open("data/records.jsonl")]
by = {r["nct"]: r for r in R}
def state(r):
    if r["has"]: return "POSTED"
    if r["submit"] and not r["post"]: return "IN_REVIEW"
    return "NO_RESULTS"
def phase1_only_drug(r):
    ph = set(r["phases"]); return r["drug"] and not r["device"] and ph and ph <= {"PHASE1", "EARLY_PHASE1"}
# known-good
assert state(by["NCT03515551"]) == "POSTED", "known-good POSTED failed"
k2 = by.get("NCT04537429")
assert k2 and state(k2) == "NO_RESULTS" and phase1_only_drug(k2), "known-good NO_RESULTS/excluded failed"
Q = [r for r in R if not phase1_only_drug(r)]
def wilson(k, n, z=1.96):
    if n == 0: return (0, 0)
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)
def outcome(lo, hi):
    if lo > 0.25: return "ABOVE"
    if hi < 0.10: return "CONSISTENT"
    return "CANNOT_TELL"
def group(rs):
    c = collections.Counter(state(r) for r in rs); scored = c["POSTED"] + c["NO_RESULTS"]
    lo, hi = wilson(c["NO_RESULTS"], scored)
    return {"n": len(rs), "posted": c["POSTED"], "no_results": c["NO_RESULTS"], "in_review": c["IN_REVIEW"],
            "share_no_results": round(c["NO_RESULTS"] / scored, 4) if scored else None,
            "lo": round(lo, 4), "hi": round(hi, 4), "outcome": outcome(lo, hi) if scored else "CANNOT_TELL"}
# lag zone: pcd 13-15 months back is outside the query end (13 months), so none here; recorded in read_at
summ = {"read": open("data/read_at.txt").read().split("\n")[0], "all": group(Q), "excluded_phase1_drug_only": len(R) - len(Q)}
summ["by_class"] = {k: group([r for r in Q if r["class"] == k]) for k in sorted({r["class"] for r in Q if r["class"]})}
summ["by_kind"] = {"drug": group([r for r in Q if r["drug"] and not r["device"]]), "device_only": group([r for r in Q if r["device"] and not r["drug"]]),
                   "both": group([r for r in Q if r["device"] and r["drug"]])}
sp = collections.defaultdict(list)
for r in Q: sp[(r["sponsor"], r["class"])].append(r)
big = {f"{k[0]}|{k[1]}": group(v) for k, v in sp.items() if len(v) >= 20 and k[1] != "INDIV"}
summ["sponsors"] = dict(sorted(big.items(), key=lambda kv: -kv[1]["n"]))
yr = collections.defaultdict(list)
for r in Q: yr[(r["pcd"] or "")[:4]].append(r)
summ["by_year"] = {y: group(v) for y, v in sorted(yr.items()) if y}
json.dump(summ, open("data/summary.json", "w"), indent=1)
print(json.dumps({k: summ[k] for k in ("read", "all", "excluded_phase1_drug_only", "by_class", "by_kind")}, indent=1))
print("sponsors >=20:", len(big), "outcomes:", collections.Counter(v["outcome"] for v in big.values()))
print("years:", {y: (v["n"], v["share_no_results"]) for y, v in summ["by_year"].items()})
