"""Rebuild the frontier-model numbers (Tables 2-6, 9, H.2, H.3, H.4, Appendix E) from the 372 released trajectory files.
usage: <python> -I rebuild_frontier.py <hf_root>   (hf_root = .../theirs/hf_at_b112204c)
Reads JSON as data only. Nothing from the authors is executed or imported."""
import sys, os, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from common import *

root = sys.argv[1]
T = load_dir(root, "trajectories")
R = {}                                    # results kept for out/rebuild_frontier.json
def say(*a):
    print(*a)

say("== FILE COUNTS")
say("trajectories:", len(T), "| per model:", dict(collections.Counter(t["model"] for t in T)))
say("per domain:", dict(collections.Counter(t["domain"] for t in T)), "| per difficulty:", dict(collections.Counter(t["difficulty"] for t in T)))
say("unique task ids:", len({t["task_id"] for t in T}), "| per domain per model:", dict(collections.Counter((t["domain"], t["model"]) for t in T)))
for m in MODELS:
    say(" ", m, "difficulty", dict(collections.Counter(t["difficulty"] for t in T if t["model"] == m)))

# ---- integrity: metadata vs counts rebuilt from steps
D = [derived(t) for t in T]
mm = collections.Counter()
for t, d in zip(T, D):
    me = t["metadata"]
    mm["steps"] += me["total_steps"] != d["n_steps"]
    mm["failures"] += me["total_failures"] != d["n_err"]
    mm["tool_calls"] += me["total_tool_calls"] != d["n_tool"]
    mm["revisions"] += me["total_revisions"] != d["n_rev"]
say("\n== INTEGRITY: trajectories whose metadata count differs from the count rebuilt from step records:", dict(mm))
tc_gap = collections.Counter()
for t, d in zip(T, D):
    if t["metadata"]["total_tool_calls"] != d["n_tool"]:
        tc_gap[(t["model"], t["metadata"]["total_tool_calls"] - d["n_tool"])] += 1
say("tool-call gap detail (model, metadata minus step count):", dict(tc_gap))

# ---- per-trajectory arrays
def arr(model, key):
    return np.array([t["metadata"][key] for t in T if t["model"] == model], float)
M = {"steps": "total_steps", "tools": "total_tool_calls", "errors": "total_failures", "revisions": "total_revisions", "wall": "wall_time_seconds"}
has_claim = {m: np.array([t["outcome"]["final_claim"] is not None for t in T if t["model"] == m], float) for m in MODELS}

say("\n== TABLE 2 (frontier rows)")
allT = lambda k: np.array([t["metadata"][k] for t in T], float)
say("conclusion rate (final_claim not null): %.4f  (%d of %d)" % (np.mean([t["outcome"]["final_claim"] is not None for t in T]), sum(t["outcome"]["final_claim"] is not None for t in T), len(T)))
say("final_claim empty string count:", sum(1 for t in T if t["outcome"]["final_claim"] == ""))
say("mean steps %.3f | median steps %.1f | mean tool calls %.3f | mean errors %.3f | mean revisions %.4f | mean wall %.2f" % (
    allT("total_steps").mean(), np.median(allT("total_steps")), allT("total_tool_calls").mean(), allT("total_failures").mean(), allT("total_revisions").mean(), allT("wall_time_seconds").mean()))
say("share with >=1 error: %.4f (%d)  | share with >=1 revision: %.4f (%d)" % ((allT("total_failures") > 0).mean(), (allT("total_failures") > 0).sum(), (allT("total_revisions") > 0).mean(), (allT("total_revisions") > 0).sum()))
say("max_steps_reached count:", sum(1 for t in T if t["metadata"]["max_steps_reached"]))
tot_chars = sum(d["resp_chars"] for d in D)
say("total response chars %d -> chars/4 = %.0f tokens (printed ~701K)" % (tot_chars, tot_chars / 4))
say("mean response chars per trajectory: overall %.0f" % np.mean([d["resp_chars"] for d in D]))
for m in MODELS:
    say("  %s mean response chars %.0f" % (m, np.mean([d["resp_chars"] for t, d in zip(T, D) if t["model"] == m])))

say("\n== TABLE 3 (mean +/- SD with ddof=1, Kruskal-Wallis H and p, Cliff's delta)")
for name, key in M.items():
    g = [arr(m, key) for m in MODELS]
    row = " | ".join("%s %.2f+/-%.2f" % (m, *mean_sd(x)) for m, x in zip(MODELS, g))
    H, p = kruskal3(g)
    say("%-9s %s | H=%.3f p=%.3g" % (name, row, H, p))
    R[name] = dict(means={m: mean_sd(x) for m, x in zip(MODELS, g)}, H=H, p=p)
H, p = kruskal3([has_claim[m] for m in MODELS])
say("conclusion %s | H=%.3f p=%.4f" % (" | ".join("%s %.4f" % (m, has_claim[m].mean()) for m in MODELS), H, p))
for name, key in [("steps", "total_steps"), ("tools", "total_tool_calls"), ("errors", "total_failures"), ("revisions", "total_revisions")]:
    c, g_, p_ = arr("claude-opus-4.6", key), arr("gemini-3.1-pro", key), arr("gpt-5.4", key)
    say("Cliff delta %-9s claude-gemini %.3f | claude-gpt %.3f | gemini-gpt %.3f" % (name, cliffs_delta(c, g_), cliffs_delta(c, p_), cliffs_delta(g_, p_)))
say("errors ratio Claude/GPT: %.1f" % (arr("claude-opus-4.6", "total_failures").mean() / arr("gpt-5.4", "total_failures").mean()))

say("\n== TABLE 4 / APPENDIX E failure taxonomy (counting rule read from the released script, re-implemented here)")
def taxonomy(t):
    ev = []
    for s in step_list(t):
        raw = (s.get("raw_response") or "").lower()
        e = s.get("error") or {}
        if e.get("occurred"):
            typ = (e.get("type") or "")
            msg = (e.get("message") or "").lower()
            if "hallucin" in raw: ev.append("hallucination")
            elif "tool" in typ or "api" in typ: ev.append("tool_misuse")
            elif "timeout" in msg: ev.append("timeout")
            elif "not found" in msg or "404" in msg: ev.append("resource_not_found")
            elif "rate" in msg or "429" in msg: ev.append("rate_limit")
            else: ev.append("other_error")
        if s.get("revision_trigger") and "error" in str(s.get("revision_trigger")).lower():
            ev.append("reasoning_error")
    return ev
tax = {m: collections.Counter() for m in MODELS}
for t in T: tax[t["model"]].update(taxonomy(t))
for m in ["claude-opus-4.6", "gemini-3.1-pro", "gpt-5.4"]:
    tot = sum(tax[m].values())
    say("%-16s total %d | tool_misuse %d (%.1f%%) | reasoning %d (%.1f%%) | other %s" % (m, tot, tax[m]["tool_misuse"], 100 * tax[m]["tool_misuse"] / tot, tax[m]["reasoning_error"], 100 * tax[m]["reasoning_error"] / tot, {k: v for k, v in tax[m].items() if k not in ("tool_misuse", "reasoning_error")}))
gt = sum(sum(c.values()) for c in tax.values()); tm = sum(c["tool_misuse"] for c in tax.values()); re_ = sum(c["reasoning_error"] for c in tax.values())
say("all: total %d | tool_misuse %d (%.1f%%) | reasoning %d (%.1f%%)" % (gt, tm, 100 * tm / gt, re_, 100 * re_ / gt))
say("error.type values among error steps:", {m: dict(collections.Counter((s["error"].get("type")) for t in T if t["model"] == m for s in step_list(t) if s["error"].get("occurred"))) for m in MODELS})
say("revision_trigger values:", dict(collections.Counter(s.get("revision_trigger") for t in T for s in step_list(t) if s.get("revision_trigger"))))
say("steps with error.occurred and total reasoning-count tie: reasoning_error counts equal total_revisions by model:", {m: (tax[m]["reasoning_error"], int(arr(m, "total_revisions").sum())) for m in MODELS})
say("note: Claude 2.5 x 124 = %.0f step-errors printed as 310, 152 keyword events printed. Rebuilt: %d error steps + %d revision events" % (2.5 * 124, int(arr("claude-opus-4.6", "total_failures").sum()), tax["claude-opus-4.6"]["reasoning_error"]))

say("\n== TABLE 5 matched-task within-domain (n=31 per model per domain)")
for dom in DOMAINS:
    for key, nm in [("total_steps", "steps"), ("total_failures", "errors")]:
        g = [np.array([t["metadata"][key] for t in T if t["model"] == m and t["domain"] == dom], float) for m in ["claude-opus-4.6", "gemini-3.1-pro", "gpt-5.4"]]
        H, p = kruskal3(g)
        say("%-17s %-6s " % (dom, nm) + " | ".join("%.2f+/-%.2f" % mean_sd(x) for x in g) + " | n=%s H=%.2f p=%.2g" % ([len(x) for x in g], H, p))

say("\n== TABLE 6 per difficulty per model (mean steps, mean errors)")
for diff in ["easy", "medium", "hard"]:
    n = sum(1 for t in T if t["difficulty"] == diff)
    say(diff, "n=%d" % n)
    for m in ["claude-opus-4.6", "gemini-3.1-pro", "gpt-5.4"]:
        sel = [t for t in T if t["model"] == m and t["difficulty"] == diff]
        say("   %-16s steps %.2f errors %.2f (n=%d)" % (m, np.mean([t["metadata"]["total_steps"] for t in sel]), np.mean([t["metadata"]["total_failures"] for t in sel]), len(sel)))

say("\n== TABLE 9 tool invocations by action.tool string (steps with a non-empty tool)")
cnt = {m: collections.Counter() for m in MODELS}
lat = collections.defaultdict(list)
for t in T:
    for s in step_list(t):
        tl = (s.get("action") or {}).get("tool")
        if tl:
            cnt[t["model"]][tl] += 1
            w = s.get("wall_time", 0) or 0
            if w > 0: lat[tl].append(w)
for m in ["claude-opus-4.6", "gemini-3.1-pro", "gpt-5.4"]:
    say(" ", m, dict(cnt[m]), "total", sum(cnt[m].values()))
tot_all = sum(sum(c.values()) for c in cnt.values())
printed4 = {m: sum(cnt[m][k] for k in ("python_exec", "web_search", "pubmed_search", "api_call")) for m in cnt}
say("total of all tool strings:", tot_all, "| total of the four named tools:", sum(printed4.values()), "(printed 1,116) | python_exec", sum(c["python_exec"] for c in cnt.values()), "share of 1116 = %.4f" % (sum(c["python_exec"] for c in cnt.values()) / 1116))
say("metadata total_tool_calls per model:", {m: int(arr(m, "total_tool_calls").sum()) for m in MODELS})
say("GPT share of its four-tool total: web %.3f pubmed %.3f api %.3f ; Claude python share %.3f" % (cnt["gpt-5.4"]["web_search"] / 301, cnt["gpt-5.4"]["pubmed_search"] / 301, cnt["gpt-5.4"]["api_call"] / 301, cnt["claude-opus-4.6"]["python_exec"] / 350))
say("latency (mean of step wall_time>0 by tool):", {k: (round(float(np.mean(v)), 2), len(v)) for k, v in lat.items() if k in ("python_exec", "web_search", "pubmed_search", "api_call")})

say("\n== H.2 error localization")
failed = [t for t in T if t["metadata"]["total_failures"] > 0]
first = []
for t in failed:
    st = step_list(t)
    for i, s in enumerate(st):
        if (s.get("error") or {}).get("occurred"):
            first.append((i, len(st))); break
say("trajectories with >=1 error:", len(failed), "| with an error-flagged step found:", len(first))
s0 = sum(1 for i, n in first if i == 0)
say("first error at step 0: %d of %d = %.4f | at last step: %d" % (s0, len(first), s0 / len(first), sum(1 for i, n in first if i == n - 1)))
say("1/mean(total steps) over those trajectories = %.3f (printed ~7%%)" % (1 / np.mean([n for i, n in first])))
say("mean relative first-error position i/n = %.3f" % np.mean([i / n for i, n in first]))

say("\n== H.3 claim verification: what the released outcome.success supports")
for m in MODELS:
    v = [t["outcome"]["success"] for t in T if t["model"] == m]
    k = sum(1 for x in v if x is True); n = sum(1 for x in v if x is not None)
    lo, hi = wilson(k, n)
    say("  %-16s null %d | evaluable n=%d | true %d | rate %.3f | Wilson [%.3f, %.3f]" % (m, sum(1 for x in v if x is None), n, k, k / n, lo, hi))
vv = [t["outcome"]["success"] for t in T]
say("  all: evaluable %d, true %d, rate %.4f ; verification.method values: %s" % (sum(x is not None for x in vv), sum(x is True for x in vv), sum(x is True for x in vv) / sum(x is not None for x in vv), dict(collections.Counter(t["outcome"]["verification"]["method"] for t in T))))
say("  evaluable with null/empty ground_truth field:", sum(1 for t in T if t["outcome"]["success"] is not None and not t.get("ground_truth")))
say("  ground-truth tasks (non-empty ground_truth):", len({t["task_id"] for t in T if t.get("ground_truth")}), "difficulty of those:", dict(collections.Counter(t["difficulty"] for t in T if t.get("ground_truth"))))

say("\n== H.3 printed judged rates: Wilson interval recomputed from the printed rate and n (arithmetic check only, no per-item file)")
for m, rate, n, printed in [("GPT-5.4", 0.886, 123, (81.8, 93.1)), ("Claude Opus 4.6", 0.839, 118, (76.2, 89.4)), ("Gemini 3.1 Pro", 0.893, 122, (82.6, 93.7))]:
    k = round(rate * n); lo, hi = wilson(k, n)
    say("  %-16s k=%d n=%d rate %.4f -> Wilson [%.1f, %.1f] printed [%.1f, %.1f]" % (m, k, n, k / n, 100 * lo, 100 * hi, *printed))
ks = [109, 99, 109]; ns = [123, 118, 122]
say("  pooled %d/%d = %.4f (printed 87.3%%)" % (sum(ks), sum(ns), sum(ks) / sum(ns)))
g = [np.array([1] * k + [0] * (n - k), float) for k, n in zip(ks, ns)]
H, p = kruskal3(g)
say("  Kruskal-Wallis on the 0/1 vectors implied by the printed counts: H=%.3f p=%.3f (printed p=0.38)" % (H, p))
say("  9 unjudged: 372-363 = %d ; 9/372 = %.1f%% (printed 3.6%%)" % (372 - 363, 100 * 9 / 372))

say("\n== H.4 process quality (two definitions)")
steps_all = np.array([t["metadata"]["total_steps"] for t in T], float); tools_all = np.array([t["metadata"]["total_tool_calls"] for t in T], float)
fail_all = np.array([t["metadata"]["total_failures"] for t in T], float); hc = np.array([t["outcome"]["final_claim"] is not None for t in T], float)
uniq = np.array([len(set(d["tools"])) for d in D], float)
mod = np.array([t["model"] for t in T])
def report(label, q):
    g = [q[mod == m] for m in ["gpt-5.4", "gemini-3.1-pro", "claude-opus-4.6"]]
    H, p = kruskal3(g)
    say("  %-58s " % label + " | ".join("%.3f+/-%.3f" % mean_sd(x) for x in g) + " | H=%.1f" % H)
eff_data = 1 - np.clip(steps_all / steps_all.max(), 0, 1)
eff_30 = 1 - np.clip(steps_all / 30, 0, 1)
low_err = 1 - np.clip(fail_all / max(fail_all.max(), 1), 0, 1)
report("released-script rule: tool CALLS / max, steps / data max", (eff_data + np.clip(tools_all / tools_all.max(), 0, 1) + low_err + hc) / 4)
report("printed text rule: unique tools / max, steps / data max", (eff_data + uniq / uniq.max() + low_err + hc) / 4)
report("printed text rule: unique tools / max, steps / 30", (eff_30 + uniq / uniq.max() + low_err + hc) / 4)
say("  printed: GPT-5.4 0.747+/-0.008 | Gemini 0.747+/-0.011 | Claude 0.724+/-0.067 | H=149.9")
say("  max steps in data %.0f, max tool calls %.0f, max failures %.0f, max unique tools %.0f" % (steps_all.max(), tools_all.max(), fail_all.max(), uniq.max()))
