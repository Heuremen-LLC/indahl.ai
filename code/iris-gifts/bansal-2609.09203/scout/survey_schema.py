"""Inventory of every released trajectory directory: file counts, key sets, models, task ids.
usage: python3 -I survey_schema.py <hf_root>"""
import sys, os, json, collections
root = sys.argv[1]
dirs = ["trajectories","data/trajectories","trajectories_live","trajectories_opensource","trajectories_qwen2.5-7b","trajectories_mistral-7b-v0.3","trajectories_phi-3.5-mini"]
for d in dirs:
    fs = sorted(f for f in os.listdir(os.path.join(root,d)) if f.endswith(".json"))
    top = collections.Counter(); step = collections.Counter(); outk = collections.Counter(); metak = collections.Counter()
    models = collections.Counter(); doms = collections.Counter(); diffs = collections.Counter(); ver = collections.Counter()
    succ = collections.Counter(); bad = 0
    for f in fs:
        try:
            j = json.load(open(os.path.join(root,d,f)))
        except Exception as e:
            bad += 1; continue
        top.update(j.keys()); outk.update(j.get("outcome",{}).keys()); metak.update(j.get("metadata",{}).keys())
        for s in j.get("trajectory",[]): step.update(s.keys())
        models[j.get("model")] += 1; doms[j.get("domain")] += 1; diffs[j.get("difficulty")] += 1
        ver[j.get("metadata",{}).get("model_version")] += 1
        succ[repr(j.get("outcome",{}).get("success","<absent>"))] += 1
    print("=== %s: %d files (unparseable %d)" % (d, len(fs), bad))
    print(" top keys:", dict(top)); print(" step keys:", dict(step)); print(" outcome keys:", dict(outk)); print(" meta keys:", dict(metak))
    print(" models:", dict(models)); print(" domains:", dict(doms)); print(" difficulty:", dict(diffs)); print(" model_version:", dict(ver)); print(" success values:", dict(succ))
