import json, glob, os, sys
B = os.path.expanduser("~/bones-forge/rank_index/public/nj_claims")
out = {}
for kind in ("claims", "schedules"):
    items = []
    for f in sorted(glob.glob(f"{B}/parts/g*_{kind}.json")):
        try:
            d = json.load(open(f))
        except Exception as e:
            print("BAD", f, e); continue
        for it in d:
            it.setdefault("group", os.path.basename(f).split("_")[0])
            sc = it.get("saved_copy")
            it["saved_copy_exists"] = bool(sc) and os.path.exists(os.path.join(B, sc))
            items.append(it)
    json.dump(items, open(f"{B}/{kind}.json", "w"), indent=1, ensure_ascii=False)
    print(kind, len(items), "missing copies:", sum(not i["saved_copy_exists"] for i in items))
