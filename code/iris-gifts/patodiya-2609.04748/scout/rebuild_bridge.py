# usage: python3 -I rebuild_bridge.py out.json   (needs numpy, scipy)
# Rebuilds Table 7 (GSM8K single-turn bridge) and the pooled problem-level analysis from the four logged passes per item.
# Gold answers are read from the authors' summary.json. The answer extractor is our own, written from the repository README and the
# docstring of the re-extraction script (patterns in priority order, no last-number fallback, numeric comparison).
import sys, os, json, math, re
from decimal import Decimal, InvalidOperation
import numpy as np
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cdlib as C

PATS = [re.compile(r"####\s*\$?(-?[\d,]+(?:\.\d+)?)"),
        re.compile(r"\\boxed\{\s*\$?(-?[\d,]+(?:\.\d+)?)\s*\}"),
        re.compile(r"\\boxed\{\\text\{\s*\$?(-?[\d,]+(?:\.\d+)?)[^}]*\}\}"),
        re.compile(r"(?:final answer|answer)\s*(?:is|:)\s*\$?(-?[\d,]+(?:\.\d+)?)", re.I),
        re.compile(r"\\boxed\{\s*\\?\$\s*(-?[\d,]+(?:\.\d+)?)"),
        re.compile(r"\\boxed\{\s*\$?(-?[\d,]+(?:\.\d+)?)\s*\\text"),
        re.compile(r"\*\*\s*\$?(-?[\d,]+(?:\.\d+)?)\s*\*\*\s*[\.\)]?\s*$", re.M)]
def extract(t):
    for p in PATS:
        m = p.findall(t)
        if m: return m[-1].replace(",", "").rstrip(".").strip()
    return None
def num(s):
    try: return Decimal(s.replace(",", "").rstrip(".").strip())
    except Exception: return None
def old_extract(t):
    m = re.findall(r"####\s*([\-\d,\.]+)", t)
    return m[-1].replace(",", "").rstrip(".") if m else None

BR = [("Qwen2.5-7B", "F16", "bridge-qwen7b-f16", 200, (3.5, [1.7, 7.0], 0, 183, 183, 1.000)),
      ("Qwen2.5-7B", "Q8_0", "bridge-qwen7b-q80", 200, (44.5, [37.8, 51.4], 4, 184, 182, 0.625)),
      ("Qwen2.5-7B", "Q4_K_M", "bridge-lcpp-qwen7b-q4km", 200, (41.5, [34.9, 48.4], 4, 180, 180, 1.000)),
      ("Qwen2.5-14B", "Q4_K_M", "bridge-qwen14b-q4km", 200, (48.0, [41.2, 54.9], 1, 185, 186, 1.000)),
      ("Qwen2.5-7B", "Q4_K_M", "bridge-qwen7b-q4km-n500", 500, (45.4, [41.1, 49.8], 12, 453, 459, 0.146)),
      ("Qwen2.5-7B", "Q3_K_M", "bridge-qwen7b-q3km", 200, (48.0, [41.2, 54.9], 3, 178, 179, 1.000))]
def mcn(b, c):
    n = b + c
    return 1.0 if n == 0 else float(min(1.0, 2 * stats.binom.cdf(min(b, c), n, 0.5)))
out = {"table7": {}}; obs = []; pooled = ["bridge-qwen7b-f16", "bridge-qwen7b-q80", "bridge-qwen7b-q3km", "bridge-qwen14b-q4km", "bridge-qwen7b-q4km-n500"]
print("model, weights | n | det recompute | det cache hit | path divergence % [Wilson] | flips | correct recompute / cache hit | McNemar p")
for model, w, name, n_exp, pr in BR:
    recs = C.load_file(f"results/{name}/cache_on/raw_requests.jsonl.gz")
    passes = {}
    dup = 0
    for r in recs:
        k = (r["item"], r["phase"])
        if k in passes: dup += 1
        passes[k] = r                                  # a restarted run supersedes earlier records of the same item and pass
    summ = json.load(open(os.path.join(C.REPO, f"results/{name}/cache_on/summary.json")))
    gold = {s["item_idx"]: s["gold"] for s in summ}
    old = json.load(open(os.path.join(C.REPO, f"results/{name}/cache_on/summary_collection_time.json")))
    items = sorted({i for i, _ in passes})
    rows = []
    for i in items:
        t = {p: passes[(i, p)]["text"] for p in ("cold", "cold2", "warm", "warm2")}
        a = {p: extract(t[p]) for p in t}
        g = gold[i]
        rows.append(dict(i=i, cold_det=t["cold"] == t["cold2"], warm_det=t["warm"] == t["warm2"], same=t["cold"] == t["warm"],
                         cc=num(a["cold"]) is not None and num(a["cold"]) == num(g), wc=num(a["warm"]) is not None and num(a["warm"]) == num(g),
                         ids_same=passes[(i, "cold")]["ids"] == passes[(i, "warm")]["ids"], cold_unparsed=a["cold"] is None,
                         old_cold_ok=old_extract(t["cold"]) is not None and old_extract(t["cold"]) == g))
    n = len(rows)
    det = [r for r in rows if r["cold_det"] and r["warm_det"]]
    attrib = [r for r in det if not r["same"]]
    flips = [r for r in attrib if r["cc"] != r["wc"]]
    b = sum(1 for r in det if r["wc"] and not r["cc"]); c = sum(1 for r in det if r["cc"] and not r["wc"])
    k = len(attrib); wl = C.wilson(k, n)
    d = dict(n=n, det_cold=sum(r["cold_det"] for r in rows), det_warm=sum(r["warm_det"] for r in rows), path_div=100 * k / n, wilson=[100 * wl[0], 100 * wl[1]],
             flips=len(flips), correct_cold=sum(r["cc"] for r in rows), correct_warm=sum(r["wc"] for r in rows), mcnemar=mcn(c, b),
             favor_cached=b, favor_recompute=c, token_level_path_divergence=sum(1 for r in det if not r["ids_same"]),
             duplicate_records_superseded=dup, raw_records=len(recs),
             unparsed_cold=sum(r["cold_unparsed"] for r in rows),
             recompute_wrong_by_old_scorer_right_by_new=100 * sum(1 for r in rows if (not r["old_cold_ok"]) and r["cc"]) / n)
    out["table7"][name] = d
    print(f"{model} {w} | {n} | {d['det_cold']}/{n} | {d['det_warm']}/{n} | {d['path_div']:.1f} [{d['wilson'][0]:.1f}, {d['wilson'][1]:.1f}] | {d['flips']} | {d['correct_cold']} / {d['correct_warm']} | {d['mcnemar']:.3f}"
          f"   printed: {pr}  (raw records {len(recs)}, superseded {dup}, token-level div {d['token_level_path_divergence']}, formatting-only {d['recompute_wrong_by_old_scorer_right_by_new']:.1f}%, accuracy {100*d['correct_cold']/n:.1f}/{100*d['correct_warm']/n:.1f}%)")
    if name in pooled:
        for r in rows:
            obs.append((r["i"], name, bool(r["cc"]), bool(r["wc"]), (r["cold_det"] and r["warm_det"]) and (r["cc"] != r["wc"]) and not r["same"]))
# pooled, clustered by problem
probs = sorted({o[0] for o in obs}); by_p = {p: [o for o in obs if o[0] == p] for p in probs}; n_obs = len(obs)
net = (sum(o[3] for o in obs) - sum(o[2] for o in obs)) / n_obs
fav_c = sum(1 for o in obs if o[4] and o[3]); fav_r = sum(1 for o in obs if o[4] and o[2])
per_p_flips = [sum(o[4] for o in by_p[p]) for p in probs]
net_by_p = [sum((o[3] - o[2]) for o in by_p[p] if o[4]) for p in probs]
pos = sum(1 for v in net_by_p if v > 0); neg = sum(1 for v in net_by_p if v < 0)
strata = {}
for p in probs: strata.setdefault(tuple(sorted(o[1] for o in by_p[p])), []).append(p)
dp = {p: sum(o[3] - o[2] for o in by_p[p]) for p in probs}
rng = np.random.default_rng(C.SEED); reps = np.zeros(C.NBOOT)
for s, pl in strata.items():
    arr = np.array([dp[p] for p in pl], float); draw = rng.integers(0, len(arr), size=(C.NBOOT, len(arr))); reps += arr[draw].sum(axis=1)
reps /= n_obs; ci = np.quantile(reps, [0.025, 0.975])
out["pooled"] = dict(observations=n_obs, unique_problems=len(probs), flips=fav_c + fav_r, favor_cached=fav_c, favor_recompute=fav_r,
                     problems_with_flip=sum(1 for v in per_p_flips if v), max_flips_one_problem=max(per_p_flips),
                     mcnemar_p=mcn(fav_r, fav_c), sign_test_p=mcn(neg, pos), net_pp=100 * net, net_ci=[100 * ci[0], 100 * ci[1]])
print("pooled: observations %d over %d unique problems; flips %d (%d favor cache hit, %d favor recompute) on %d problems; pooled McNemar p %.2f; problem-clustered sign test p %.2f; net %+.2f points [%+.2f, %+.2f]" %
      (n_obs, len(probs), fav_c + fav_r, fav_c, fav_r, out["pooled"]["problems_with_flip"], out["pooled"]["mcnemar_p"], out["pooled"]["sign_test_p"], 100 * net, 100 * ci[0], 100 * ci[1]))
print("   printed: 1300 observations over 500 unique problems; 20 flips, 13 favor cache hit and 7 recompute, on 20 different problems; p 0.26 and 0.26; +0.46 [-0.15, +1.15]")
json.dump(out, open(sys.argv[1], "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
