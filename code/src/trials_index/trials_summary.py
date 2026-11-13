#!/usr/bin/env python3
"""TRIALS summary per PLAN.md + Addendum 1. Reads data/records.jsonl, writes data/summary.json."""
import json, math, collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import heuremen_kit as K   # 12 Nov 2026 (Faults and Guards 2.0): the outcome comes from K.read, see PLAN_ADDENDUM_std2.md
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
    # 12 Nov 2026, PLAN_ADDENDUM_std2.md: size that matters 0.25, null 0, band [0, 0.10), edge '[)'. Returns (outcome, reason). No dead zone.
    return K.read(lo, hi, band=(0.0, 0.10), matters=0.25, edge='[)', null=0.0)
def group(rs):
    c = collections.Counter(state(r) for r in rs); scored = c["POSTED"] + c["NO_RESULTS"]
    lo, hi = wilson(c["NO_RESULTS"], scored)
    if scored: lo = 0.0 if c["NO_RESULTS"] == 0 else lo; hi = 1.0 if c["NO_RESULTS"] == scored else hi   # exact ends of the Wilson interval, so zero events reaches the null
    o, why = outcome(lo, hi) if scored else (K.CANNOT_TELL, K.NO_INTERVAL_FORMABLE)
    return {"n": len(rs), "posted": c["POSTED"], "no_results": c["NO_RESULTS"], "in_review": c["IN_REVIEW"],
            "share_no_results": round(c["NO_RESULTS"] / scored, 4) if scored else None,
            "lo": round(lo, 4), "hi": round(hi, 4), "outcome": o, "reason": why}
# 10 Nov 2026 (Addendum 5, newsletter audit): the plan's floor is now built. Records with primary completion 13 to 15 months before the read
# are the lag zone: shown apart, not scored. The old comment here said the query end left none, but the query ends about 13 months back, so
# 395 records of the 10 Nov read sat in the lag zone and were scored. Lag-zone records are those completed after the read date minus 15 months.
import datetime as _D
_read = open("data/read_at.txt").read().split("\n")[0]
_rd = _D.date.fromisoformat(_read[:10]); _m = _rd.month - 15; _y = _rd.year + (_m - 1) // 12; _m = (_m - 1) % 12 + 1
import calendar as _C
LAG_FROM = _D.date(_y, _m, min(_rd.day, _C.monthrange(_y, _m)[1])).isoformat()
def in_lag(r): return (r["pcd"] or "") > LAG_FROM
LAG = [r for r in R if not phase1_only_drug(r) and in_lag(r)]
Q = [r for r in Q if not in_lag(r)]
def cluster_interval(rs, key="sponsor", z=1.96):
    """Added 10 Nov 2026 (Addendum 5), beside the plan's Wilson interval: a sponsor-clustered interval for the share with no results, the
    ratio estimator with a cluster-robust standard error, lead sponsors as the units. Not the plan's ruler, labelled on the page with its date."""
    sc = [r for r in rs if state(r) != "IN_REVIEW"]; n = len(sc)
    if not n: return None
    k = sum(1 for r in sc if state(r) == "NO_RESULTS"); p = k / n; cl = collections.defaultdict(list)
    for r in sc: cl[r[key]].append(r)
    m = len(cl); s = sum((sum(1 for r in v if state(r) == "NO_RESULTS") - p * len(v)) ** 2 for v in cl.values())
    se = math.sqrt(m / (m - 1) * s) / n if m > 1 else float("nan")
    return {"lo": round(max(0.0, p - z * se), 4), "hi": round(min(1.0, p + z * se), 4), "sponsors": m, "defined": "2026-11-10, after the data"}
summ = {"read": _read, "all": group(Q), "excluded_phase1_drug_only": len(R) - len(Q) - len(LAG)}
summ["all"]["sponsor_clustered"] = cluster_interval(Q)
summ["all"]["req13"] = K.req13([summ["all"]], nothing_returned=0)   # 0 NOTHING_RETURNED: a read with a failed page stops the run and publishes nothing, see the addendum
summ["lag_zone"] = dict(group(LAG), completed_after=LAG_FROM, scored=False)
summ["by_class"] = {k: group([r for r in Q if r["class"] == k]) for k in sorted({r["class"] for r in Q if r["class"]})}
for _k, _g in summ["by_class"].items(): _g["sponsors"] = len({r["sponsor"] for r in Q if r["class"] == _k})
summ["by_kind"] = {"drug": group([r for r in Q if r["drug"] and not r["device"]]), "device_only": group([r for r in Q if r["device"] and not r["drug"]]),
                   "both": group([r for r in Q if r["device"] and r["drug"]])}
sp = collections.defaultdict(list)
for r in Q: sp[(r["sponsor"], r["class"])].append(r)
big = {f"{k[0]}|{k[1]}": group(v) for k, v in sp.items() if len(v) >= 20 and k[1] != "INDIV"}
summ["sponsors"] = dict(sorted(big.items(), key=lambda kv: -kv[1]["n"]))
yr = collections.defaultdict(list)
for r in Q: yr[(r["pcd"] or "")[:4]].append(r)
summ["by_year"] = {y: group(v) for y, v in sorted(yr.items()) if y}
summ["req13"] = {t: K.req13(list(summ[t].values()), nothing_returned=0) for t in ("by_class", "by_kind", "sponsors", "by_year")}   # the cells of each table, CANNOT_TELL split by reason
json.dump(summ, open("data/summary.json", "w"), indent=1)
print(json.dumps({k: summ[k] for k in ("read", "all", "excluded_phase1_drug_only", "by_class", "by_kind")}, indent=1))
print("sponsors >=20:", len(big), "outcomes:", collections.Counter(v["outcome"] for v in big.values()))
print("years:", {y: (v["n"], v["share_no_results"]) for y, v in summ["by_year"].items()})
