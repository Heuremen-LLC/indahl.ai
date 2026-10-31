"""Our own loader and comparison code for the 2609.04748 recount (Patodiya, cache-divergence-study).

Written from the paper's Section III-G and from the released code read as text.
Nothing from the authors' repository is imported or executed. Raw logs are read as data.
Run scripts that use this file with: PY -I script.py ...   (PY needs numpy and scipy)
"""
import gzip, json, os, pickle, hashlib, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, "..", "theirs", "repo_bc0551d")
CACHE = os.path.join(HERE, "cache")
os.makedirs(CACHE, exist_ok=True)

SEED = 20261007
NBOOT = 10000


def ep_num(e):
    return int(e.rsplit("_", 1)[1])


def _compact(r):
    """One raw log line to a compact record. Reads the schema fields seen in the probe:
    llama.cpp: choices[0].logprobs.content[*] = {id, token, bytes, logprob, top_logprobs[*]}
    vLLM:      choices[0].logprobs = {tokens, token_logprobs, top_logprobs, ...}
    """
    resp = r["response"]
    ch = resp["choices"][0]
    lp = ch.get("logprobs") or {}
    content = lp.get("content")
    out = {
        "ep": r.get("episode_id"), "ridx": r.get("request_idx"),
        "item": r.get("item_idx"), "phase": r.get("phase") or r.get("pass"),
        "prompt": r.get("prompt_sha256"),
        "latency": r.get("latency_s"),
        "created": resp.get("created"),
        "finish": ch.get("finish_reason"),
        "text": ch.get("text", ""),
    }
    usage = resp.get("usage") or {}
    out["ctok"] = usage.get("completion_tokens")
    out["ptok"] = usage.get("prompt_tokens")
    det = usage.get("prompt_tokens_details")
    out["cached"] = None if not det else det.get("cached_tokens")
    if "cached_tokens" in r and out["cached"] is None:
        out["cached"] = r["cached_tokens"]
    tm = resp.get("timings") or {}
    out["cache_n"] = tm.get("cache_n")
    out["prompt_n"] = tm.get("prompt_n")
    out["prompt_ms"] = tm.get("prompt_ms")
    out["pred_ms"] = tm.get("predicted_ms")
    if content:
        out["level"] = "id"
        out["ids"] = tuple(t["id"] for t in content)
        out["lps"] = np.array([t["logprob"] for t in content], dtype=np.float64)
        mg = []
        for t in content:
            tops = sorted((x["logprob"] for x in (t.get("top_logprobs") or [])), reverse=True)
            mg.append(tops[0] - tops[1] if len(tops) >= 2 else np.nan)
        out["margins"] = np.array(mg, dtype=np.float64)
    else:
        toks = lp.get("tokens")
        if toks:
            out["level"] = "str"
            out["ids"] = tuple(toks)
            out["lps"] = np.array(lp.get("token_logprobs") or [], dtype=np.float64)
            out["margins"] = np.full(len(toks), np.nan)
        else:
            out["level"] = "text"
            out["ids"] = (ch.get("text", ""),)
            out["lps"] = np.array([], dtype=np.float64)
            out["margins"] = np.array([], dtype=np.float64)
    return out


def load_file(relpath, repo=None):
    """relpath is relative to the repo root, e.g. results/lcpp-qwen7b-q4km/main/arm_on/raw_requests.jsonl.gz"""
    repo = repo or REPO
    full = os.path.join(repo, relpath)
    key = hashlib.sha1(relpath.encode()).hexdigest()[:16]
    cp = os.path.join(CACHE, key + ".pkl")
    if os.path.exists(cp) and os.path.getmtime(cp) >= os.path.getmtime(full):
        with open(cp, "rb") as fh:
            return pickle.load(fh)
    recs = []
    with gzip.open(full, "rt") as fh:
        for line in fh:
            if line.strip():
                recs.append(_compact(json.loads(line)))
    with open(cp, "wb") as fh:
        pickle.dump(recs, fh, protocol=4)
    return recs


def by_episode(recs):
    d = {}
    for r in recs:
        d.setdefault(r["ep"], []).append(r)
    for v in d.values():
        v.sort(key=lambda x: x["ridx"])
    return d


def load_pass(cell_dir):
    """cell_dir like results/lcpp-qwen7b-q4km/main/arm_on : an agentic pass keyed by episode id."""
    return by_episode(load_file(os.path.join(cell_dir, "raw_requests.jsonl.gz")))


# ---------------------------------------------------------------- divergence, the paper's Section III-G definition
def compare_episode(a, b):
    """Walk the requests of one episode in lockstep. Divergent if any prompt hash differs, any emitted
    token sequence differs, or the number of requests differs."""
    for k, (x, y) in enumerate(zip(a, b)):
        if x["prompt"] != y["prompt"]:
            return dict(div=True, req=k, tok=None, kind="prompt")
        if x["ids"] != y["ids"]:
            t = next((i for i, (p, q) in enumerate(zip(x["ids"], y["ids"])) if p != q), min(len(x["ids"]), len(y["ids"])))
            return dict(div=True, req=k, tok=t, kind="token")
    if len(a) != len(b):
        return dict(div=True, req=None, tok=None, kind="count")
    return dict(div=False, req=None, tok=None, kind=None)


def div_series(pa, pb, strict=True):
    """0/1 divergence per episode, ordered by numeric episode id."""
    if strict and set(pa) != set(pb):
        raise ValueError("episode sets differ")
    eps = sorted(set(pa) & set(pb), key=ep_num)
    res = [compare_episode(pa[e], pb[e]) for e in eps]
    return eps, np.array([1 if r["div"] else 0 for r in res]), res


# ---------------------------------------------------------------- intervals
def wilson(k, n, z=1.959964):
    if n == 0:
        return [None, None]
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [max(0.0, c - h), min(1.0, c + h)]


def pw_block_length(x):
    """Politis-White (2004) circular-bootstrap block length with the Patton-Politis-White (2009) correction,
    written after the arch package's algorithm as the paper cites it. None for a constant series."""
    x = np.asarray(x, float)
    n = len(x)
    eps = x - x.mean()
    if not np.any(eps):
        return None
    b_max = math.ceil(min(3 * math.sqrt(n), n / 3))
    kn = max(5, int(math.log10(n)))
    m_max = int(math.ceil(math.sqrt(n))) + kn
    cv = 2 * math.sqrt(math.log10(n) / n)
    acv = np.zeros(m_max + 1)
    abs_acorr = np.zeros(m_max + 1)
    opt_m = None
    for i in range(m_max + 1):
        v1 = eps[i + 1:] @ eps[i + 1:]
        v2 = eps[: -(i + 1)] @ eps[: -(i + 1)]
        cross = eps[i:] @ eps[: n - i]
        acv[i] = cross / n
        abs_acorr[i] = abs(cross) / math.sqrt(v1 * v2) if v1 > 0 and v2 > 0 else 0.0
        if i >= kn and opt_m is None and np.all(abs_acorr[i - kn: i] < cv):
            opt_m = i - kn
    m = 2 * max(opt_m, 1) if opt_m is not None else m_max
    m = min(m, m_max)
    g = 0.0
    lr = acv[0]
    for k in range(1, m + 1):
        lam = 1.0 if k / m <= 0.5 else 2 * (1 - k / m)
        g += 2 * lam * k * acv[k]
        lr += 2 * lam * acv[k]
    d_cb = 4 / 3 * lr ** 2
    if d_cb <= 0 or g == 0:
        return 1.0
    return float(min(((2 * g ** 2) / d_cb) ** (1 / 3) * n ** (1 / 3), b_max))


def block_len(n, pw):
    floor = math.ceil(n ** (1 / 3))
    return max(floor, int(math.ceil(pw))) if pw is not None else floor


def cbb_indices(n, block, n_boot, rng):
    k = math.ceil(n / block)
    starts = rng.integers(0, n, size=(n_boot, k))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]) % n
    return idx.reshape(n_boot, -1)[:, :n]


def cbb_ci(x, block, n_boot=NBOOT, seed=SEED):
    x = np.asarray(x, float)
    rng = np.random.default_rng(seed)
    idx = cbb_indices(len(x), block, n_boot, rng)
    reps = x[idx].mean(axis=1)
    lo, hi = np.quantile(reps, [0.025, 0.975])
    return [float(lo), float(hi)]


def reported_interval(x):
    """Envelope of the circular block bootstrap (block by Politis-White, floored at ceil(n^(1/3))) and Wilson."""
    x = np.asarray(x)
    n, k = len(x), int(x.sum())
    w = wilson(k, n)
    pw = pw_block_length(x)
    if pw is None:
        return dict(n=n, k=k, rate=k / n, wilson=w, block=None, cbb=None, reported=None)
    b = block_len(n, pw)
    ci = cbb_ci(x, b)
    return dict(n=n, k=k, rate=k / n, wilson=w, block=b, pw=pw, cbb=ci, reported=[min(ci[0], w[0]), max(ci[1], w[1])])


def pct(v, d=1):
    return None if v is None else round(100 * v, d)
