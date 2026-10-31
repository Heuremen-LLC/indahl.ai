"""Shared loaders and statistics for the 2609.09203 recount. Pure numpy. Data is only read as JSON text.
Imported by the rebuild scripts, which are run as: <python> -I <script> <hf_root> (script dir is on sys.path under -I only for the script file's own directory)."""
import os, json, math
import numpy as np

MODELS = ["gpt-5.4", "claude-opus-4.6", "gemini-3.1-pro"]          # paper column order for Table 3
DOMAINS = ["drug_discovery", "genomics", "literature", "materials_science"]

def load_dir(root, sub):
    out = []
    d = os.path.join(root, sub)
    for f in sorted(os.listdir(d)):
        if f.endswith(".json"):
            out.append(json.load(open(os.path.join(d, f))))
    return out

def step_list(t):
    return t.get("trajectory") or []

def derived(t):
    """Per-trajectory quantities rebuilt from the step records (not from metadata)."""
    steps = step_list(t)
    err_steps = [s for s in steps if (s.get("error") or {}).get("occurred")]
    tool_steps = [s for s in steps if (s.get("action") or {}).get("type") == "tool_call"]
    rev_steps = [s for s in steps if s.get("revision_trigger")]
    tools = [(s.get("action") or {}).get("tool") for s in steps if (s.get("action") or {}).get("tool")]
    return dict(n_steps=len(steps), n_err=len(err_steps), n_tool=len(tool_steps), n_rev=len(rev_steps),
                tools=tools, resp_chars=sum(len(s.get("raw_response") or "") for s in steps),
                obs_chars=sum(len(str(s.get("observation") or "")) for s in steps),
                phases=[s.get("phase", "unknown") for s in steps])

def rankdata(x):
    x = np.asarray(x, float)
    order = np.argsort(x, kind="mergesort")
    xs = x[order]
    ranks = np.empty(len(x), float)
    i = 0
    n = len(x)
    while i < n:
        j = i
        while j + 1 < n and xs[j + 1] == xs[i]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return ranks

def kruskal3(groups):
    """Kruskal-Wallis H with tie correction. p from chi-square, df = k-1; closed form for k=3 (df=2): exp(-H/2)."""
    allv = np.concatenate([np.asarray(g, float) for g in groups])
    N = len(allv)
    r = rankdata(allv)
    pos = 0
    s = 0.0
    for g in groups:
        n = len(g)
        s += r[pos:pos + n].sum() ** 2 / n
        pos += n
    H = 12.0 / (N * (N + 1)) * s - 3 * (N + 1)
    _, cnt = np.unique(allv, return_counts=True)
    C = 1.0 - (cnt ** 3 - cnt).sum() / (N ** 3 - N)
    if C == 0:
        return float("nan"), float("nan")
    H /= C
    k = len(groups)
    assert k == 3, "closed-form p only for 3 groups"
    return H, math.exp(-H / 2.0)

def cliffs_delta(x, y):
    x = np.asarray(x, float)[:, None]
    y = np.asarray(y, float)[None, :]
    return float(((x > y).sum() - (x < y).sum()) / (x.size * y.size))

def wilson(k, n, z=1.96):
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h, c + h

def mean_sd(v):
    v = np.asarray(v, float)
    return float(v.mean()), float(v.std(ddof=1))
