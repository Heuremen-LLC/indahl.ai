"""Distribution of outcome fields in frontier directories, by model. usage: python3 -I survey_outcomes.py <hf_root>"""
import sys, os, json, collections
root = sys.argv[1]
for d in ["trajectories","data/trajectories"]:
    print("===", d)
    cnt = collections.Counter()
    for f in sorted(os.listdir(os.path.join(root,d))):
        if not f.endswith(".json"): continue
        j = json.load(open(os.path.join(root,d,f)))
        o = j["outcome"]; v = o.get("verification")
        key = (j["model"], repr(o.get("success")), repr(v.get("method") if isinstance(v,dict) else v), repr(v.get("result") if isinstance(v,dict) else None), "gt" if j.get("ground_truth") else "nogt")
        cnt[key] += 1
    for k in sorted(cnt): print(k, cnt[k])
