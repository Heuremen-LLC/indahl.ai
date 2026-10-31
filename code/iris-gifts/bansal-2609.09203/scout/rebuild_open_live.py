"""Open-weight (4 x 30), live-retrieval (30), task bank, Table 2 totals and Table 10 times from the released files.
usage: <python> -I rebuild_open_live.py <hf_root>"""
import sys, os, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from common import *
root = sys.argv[1]
say = print
DIRS = [("Qwen2.5-7B", "trajectories_qwen2.5-7b", "~15s A10G"), ("Mistral-7B-v0.3", "trajectories_mistral-7b-v0.3", "~15s A10G"),
        ("Phi-3.5-mini", "trajectories_phi-3.5-mini", "<1s A10G"), ("Qwen2.5-1.5B", "trajectories_opensource", "~7s V100")]
tb = json.load(open(os.path.join(root, "task_bank.json")))
tasks = tb["tasks"]
say("== TASK BANK  metadata:", tb["metadata"])
say("tasks in file:", len(tasks), "| per domain:", dict(collections.Counter(t["domain"] for t in tasks)), "| per difficulty:", dict(collections.Counter(t["difficulty"] for t in tasks)))
say("tasks with non-empty ground_truth:", sum(1 for t in tasks if t.get("ground_truth")), dict(collections.Counter(t["difficulty"] for t in tasks if t.get("ground_truth"))))
first30 = [t["task_id"] for t in tasks[:30]]
say("first 30 task ids in file order:", first30[0], "...", first30[-1], "| difficulty mix:", dict(collections.Counter(t["difficulty"] for t in tasks[:30])), "| ground-truth among them:", sum(1 for t in tasks[:30] if t.get("ground_truth")))
prompts = {t["task_id"]: t["prompt"] for t in tasks}

total = 0
for label, d, printed in DIRS:
    O = load_dir(root, d)
    total += len(O)
    say("\n== %s  (%s)  files=%d" % (label, d, len(O)))
    ids = sorted(t["task_id"] for t in O)
    say(" task ids equal first 30 of task bank:", ids == sorted(first30), "| prompt equals task_bank prompt for all:", all(t["prompt"] == prompts[t["task_id"]] for t in O))
    say(" model strings:", dict(collections.Counter(t["model"] for t in O)), "| model_version:", dict(collections.Counter(t["metadata"]["model_version"] for t in O)))
    wt = np.array([t["metadata"]["wall_time_seconds"] for t in O], float)
    say(" mean wall_time_seconds %.2f (printed %s) | min %.2f max %.2f" % (wt.mean(), printed, wt.min(), wt.max()))
    L = np.array([len(t["trajectory"][0]["raw_response"]) for t in O])
    say(" raw_response chars: mean %.0f min %d max %d | files at the 3000-char truncation: %d" % (L.mean(), L.min(), L.max(), int((L >= 3000).sum())))
    say(" success values:", dict(collections.Counter(repr(t["outcome"]["success"]) for t in O)), "| steps per file:", dict(collections.Counter(t["metadata"]["total_steps"] for t in O)))
    say(" error.occurred true:", sum(1 for t in O if t["trajectory"][0]["error"]["occurred"]), "| metadata total_failures sum:", sum(t["metadata"]["total_failures"] for t in O))
    errlike = [t["task_id"] for t in O if t["trajectory"][0]["raw_response"].lstrip().lower().startswith("error")]
    say(" responses that begin with 'Error':", len(errlike))
    if errlike:
        c = collections.Counter(next(t for t in O if t["task_id"] == i)["trajectory"][0]["raw_response"][:80] for i in errlike)
        say("   distinct first-80-char strings among them:", dict(c))
    keys = collections.Counter(k for t in O for k in t.keys())
    say(" top-level keys:", dict(keys))
say("\nopen-weight files total:", total, "(printed 120 = 30 x 4)")

Lv = load_dir(root, "trajectories_live")
say("\n== LIVE VARIANT  files=%d  (printed 60)" % len(Lv))
say(" models:", dict(collections.Counter(t["model"] for t in Lv)), "| retrieval_mode:", dict(collections.Counter(t["retrieval_mode"] for t in Lv)), "| unique task ids:", len({t["task_id"] for t in Lv}))
say(" pubmed hit counts (live_search_results.pubmed) >0:", sum(1 for t in Lv if (t["live_search_results"].get("pubmed") or 0) > 0), "| pubchem True:", sum(1 for t in Lv if t["live_search_results"].get("pubchem")))
say(" mean wall_time_seconds %.2f" % np.mean([t["metadata"]["wall_time_seconds"] for t in Lv]))
say(" responses beginning 'Error':", sum(1 for t in Lv if (t["trajectory"][-1].get("raw_response") or "").lstrip().startswith("Error")))

say("\n== TOTALS")
nf = len(os.listdir(os.path.join(root, "trajectories"))); 
say("frontier %d + open %d + live %d = %d released trajectory files; printed 558 = 372 + 120 + 6 tool-scaffolded + 60 live" % (nf, total, len(Lv), nf + total + len(Lv)))
say("tool-scaffolded Qwen2.5-7B trajectories (printed 6): any file with model qwen2.5-7b and total_steps>1 in any directory:", sum(1 for d in ["trajectories", "data/trajectories", "trajectories_qwen2.5-7b", "trajectories_live", "trajectories_opensource"] for t in load_dir(root, d) if t.get("model") == "qwen2.5-7b" and t["metadata"].get("total_steps", 1) > 1))
