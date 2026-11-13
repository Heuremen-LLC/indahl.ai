#!/usr/bin/env python3
"""recount_pick.py: pick recount candidates from list.json using the cache only (no network).
Run: python3 -I recount_pick.py   -> prints ranked candidates as JSON lines for RECOUNT_CANDIDATES.md"""
import json, os, re, glob, html
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
lst = json.load(open(os.path.join(OUT, "list.json")))["studies"]
info = {}
def strip(s): return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()
for p in glob.glob(os.path.join(HERE, "cache", "*.json")):
    try: d = json.load(open(p))
    except Exception: continue
    if isinstance(d, dict) and "hits" in d:
        for h in d["hits"].get("hits", []):
            if h.get("doi"):
                info["https://doi.org/" + h["doi"]] = (strip(h["metadata"].get("description", "")), [(f.get("key"), f.get("size", 0)) for f in h.get("files", [])])
    elif isinstance(d, dict) and d.get("files") is not None and d.get("doi"):
        info["https://doi.org/" + d["doi"]] = (strip(d.get("description", "")), [(f.get("name"), f.get("size", 0)) for f in d["files"]])
    elif isinstance(d, dict) and "_embedded" in d and "stash:datasets" in d["_embedded"]:
        for it in d["_embedded"]["stash:datasets"]:
            info.setdefault("https://doi.org/" + it.get("identifier", "").replace("doi:", ""), (strip(it.get("abstract", "")), None))
FIG0 = re.compile(r"((?:\bT1\b|\bT2\*?\b|\bT_?[12]\b|coherence time|relaxation time|dephasing time|fidelity|error rate|count rate|counts per second|Q factor|quality factor|loss tangent|\bTLS\b)[^.;]{0,60}?\d+(?:\.\d+)?\s?(?:±|\+/-|\(|%|µs|us|μs|ms|ns|s\b|kHz|MHz|Hz|cps|×|x10|e-)[^.;]{0,30})", re.I)
FIG = re.compile(r"((?:\bT1\b|\bT2\*?\b|\bT_?[12]\b|coherence|relaxation|dephasing|fidelit|error rate|error per|count rate|counts|Q factor|quality factor|loss tangent|visibility|heralding|key rate|bit rate|entropy|linewidth|lifetime|g\(2\)|g2)[^.;\n]{0,80}?\d+(?:\.\d+)?\s?(?:±|\+/-|\(|%|µs|us\b|μs|ms\b|ns\b|s\b|kHz|MHz|Hz|cps|Mbit|kbit|bits|dB|×|x10|e-)[^.;]{0,30})", re.I)
res = []
for r in lst:
    desc, files = info.get(r["link"], ("", None))
    m = FIG.search(desc)
    if not m: continue
    score = 1
    fn = " ".join(f[0].lower() for f in (files or []) if f[0])
    if re.search(r"t1|t2|ramsey|rabi|decay|echo|rb|benchmark|count|spectr|sweep", fn): score += 2
    if re.search(r"\.(h5|hdf5|npz|npy|csv|mat|dat|txt|json)", fn): score += 1
    total = sum(f[1] or 0 for f in (files or []))
    if 0 < total < 50e6: score += 1
    res.append((score, r["study"], r["link"], r["platform"], m.group(1).strip(), [f[0] for f in (files or [])][:6], total))
res.sort(key=lambda x: -x[0])
for x in res[:60]:
    print(json.dumps(x))
