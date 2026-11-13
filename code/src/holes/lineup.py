#!/usr/bin/env python3
"""THE BIG-SMALL HOLE LINEUP. Pre-registered in gridsong/biblioteca.md (2026-09-26 ~21:30Z). Run with qvenv python.

Sources: NIST beacon holes, IBM no-calibration gaps, IBM onsets (starts only), LIGO/Virgo/KAGRA data-off per detector.
Metrics: M0 co-absence seconds, M5/M60 hole-start coincidences. Null: 1000 circular shifts by whole weeks inside blocks.
"""
import json, os
from datetime import datetime, timedelta, timezone, date
from itertools import combinations
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WEEK = 7 * 86400.0
NSHIFT = 1000
MIN_COMMON = 28 * 86400.0
rng = np.random.default_rng(20260926)


def ts(s):
    s = s.replace("Z", "+00:00")
    d = datetime.fromisoformat(s)
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.timestamp()


def merge(iv):
    """merge overlapping/touching intervals; zero-length kept."""
    iv = sorted(iv)
    out = []
    for a, b in iv:
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return np.array(out, dtype=float).reshape(-1, 2)


def clip(iv, blocks):
    out = []
    for s, e in blocks:
        a = np.maximum(iv[:, 0], s)
        b = np.minimum(iv[:, 1], e)
        m = b >= a
        m &= (iv[:, 0] < e) & (iv[:, 1] >= s)
        out.append(np.stack([a[m], b[m]], 1))
    return merge(np.concatenate(out).tolist()) if out else np.zeros((0, 2))


def intersect(A, B):
    out, i, j = [], 0, 0
    while i < len(A) and j < len(B):
        a, b = max(A[i, 0], B[j, 0]), min(A[i, 1], B[j, 1])
        if b > a:
            out.append((a, b))
        if A[i, 1] < B[j, 1]:
            i += 1
        else:
            j += 1
    return np.array(out, dtype=float).reshape(-1, 2)


def subtract(A, M):
    """A minus M (both sorted disjoint)."""
    out = []
    for a, b in A:
        cur = a
        for m0, m1 in M[(M[:, 1] > a) & (M[:, 0] < b)]:
            if m0 > cur:
                out.append((cur, m0))
            cur = max(cur, m1)
        if cur < b:
            out.append((cur, b))
    return np.array(out, dtype=float).reshape(-1, 2)


def overlap_len(A, B):
    """|A ∩ B| for sorted disjoint interval arrays, vectorized."""
    if len(A) == 0 or len(B) == 0:
        return 0.0
    pts = np.unique(np.concatenate([A.ravel(), B.ravel()]))
    mid = (pts[:-1] + pts[1:]) / 2
    w = np.diff(pts)
    ia = np.searchsorted(A[:, 0], mid, "right") - 1
    ib = np.searchsorted(B[:, 0], mid, "right") - 1
    inA = (ia >= 0) & (A[np.clip(ia, 0, None), 1] > mid)
    inB = (ib >= 0) & (B[np.clip(ib, 0, None), 1] > mid)
    return float(w[inA & inB].sum())


def in_set(t, C):
    i = np.searchsorted(C[:, 0], t, "right") - 1
    return (i >= 0) & (C[np.clip(i, 0, None), 1] >= t)


def coinc(F, S, W):
    """number of F starts with an S start within +/-W."""
    if len(F) == 0 or len(S) == 0:
        return 0
    S = np.sort(S)
    i = np.searchsorted(S, F)
    d1 = np.abs(F - S[np.clip(i, 0, len(S) - 1)])
    d0 = np.abs(F - S[np.clip(i - 1, 0, len(S) - 1)])
    return int((np.minimum(d0, d1) <= W).sum())


def shift_iv(iv, blocks, offs):
    """circular rotation inside each block; disjoint intervals stay disjoint, so only a sort is needed."""
    out = []
    for (s, e), o in zip(blocks, offs):
        L = e - s
        x = iv[(iv[:, 1] > s) & (iv[:, 0] < e)] if len(iv) else iv
        if not len(x):
            continue
        a = np.maximum(x[:, 0], s); b = np.minimum(x[:, 1], e)
        a2 = s + ((a - s + o) % L); b2 = a2 + (b - a)
        w = b2 > e
        out.append(np.stack([a2, np.minimum(b2, e)], 1))
        if w.any():
            out.append(np.stack([np.full(w.sum(), s), s + (b2[w] - e)], 1))
    if not out:
        return np.zeros((0, 2))
    r = np.concatenate(out)
    return r[np.argsort(r[:, 0], kind="stable")]


def shift_pts(p, blocks, offs):
    out = []
    for (s, e), o in zip(blocks, offs):
        x = p[(p >= s) & (p < e)]
        out.append(s + ((x - s + o) % (e - s)))
    return np.sort(np.concatenate(out)) if out else np.zeros(0)


# ---------------- load sources ----------------
def load():
    nist, ibm_nocal, ibm_on = [], [], set()
    for line in open(os.path.join(HERE, "outside_holes.jsonl")):
        d = json.loads(line)
        if d["provider"] == "nist-beacon":
            nist.append((ts(d["at"]), ts(d["ended"]) if d["ended"] else ts(d["at"])))
        elif d["provider"] == "ibm-calibration":
            a = ts(d["at"])
            if d["kind"] == "no-calibration":
                ibm_nocal.append((a, ts(d["ended"]) if d["ended"] else ts("2026-09-25T23:59:59Z")))
            elif d["kind"] in ("gate-nonoperational", "qubit-extreme"):
                ibm_on.add(a)
    lig = {}
    for line in open(os.path.join(HERE, "ligo_holes.jsonl")):
        d = json.loads(line)
        lig.setdefault(d["device"], []).append((ts(d["at"]), ts(d["ended"])))
    cov = json.load(open(os.path.join(HERE, "ligo_coverage.json")))
    S = {}
    S["NIST"] = dict(holes=merge(nist), blocks=[(ts("2018-07-23T19:26:00Z"), ts("2026-09-26T18:23:00Z"))], starts_only=False)
    S["IBM"] = dict(holes=merge(ibm_nocal), blocks=[(ts("2024-05-16T03:40:36Z"), ts("2026-09-25T23:59:59Z"))], starts_only=False)
    S["IBMon"] = dict(holes=None, pts=np.array(sorted(ibm_on)), blocks=S["IBM"]["blocks"], starts_only=True)
    for det in ("H1", "L1", "V1", "K1"):
        S[det] = dict(holes=merge(lig[det]), blocks=[(ts(r["at"]), ts(r["ended"])) for r in cov[det]], starts_only=False)
    for k, v in S.items():
        if v["holes"] is not None:
            v["pts"] = v["holes"][:, 0].copy()
    return S


def truncate_weeks(blocks):
    return [(s, s + np.floor((e - s) / WEEK) * WEEK) for s, e in blocks]


def us_holidays(y0=2018, y1=2026):
    def nth(y, m, wd, n):
        d = date(y, m, 1)
        d += timedelta((wd - d.weekday()) % 7)
        return d + timedelta(weeks=n - 1)

    def last(y, m, wd):
        d = date(y, m + 1, 1) - timedelta(1) if m < 12 else date(y, 12, 31)
        return d - timedelta((d.weekday() - wd) % 7)
    out = set()
    for y in range(y0, y1 + 2):
        fixed = [date(y, 1, 1), date(y, 7, 4), date(y, 11, 11), date(y, 12, 25)] + ([date(y, 6, 19)] if y >= 2021 else [])
        for d in fixed:
            out.add(d)
            if d.weekday() == 5:
                out.add(d - timedelta(1))
            if d.weekday() == 6:
                out.add(d + timedelta(1))
        out |= {nth(y, 1, 0, 3), nth(y, 2, 0, 3), last(y, 5, 0), nth(y, 9, 0, 1), nth(y, 10, 0, 2), nth(y, 11, 3, 4)}
    return sorted(out)


def day_windows(days, before=1, after=1):
    iv = []
    for d in days:
        t = datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp()
        iv.append((t - before * 86400, t + (after + 1) * 86400))
    return merge(iv)


def dst_days(y0=2018, y1=2026):
    out = []
    for y in range(y0, y1 + 1):
        d = date(y, 3, 1); d += timedelta((6 - d.weekday()) % 7); out.append(d + timedelta(7))   # US 2nd Sun Mar
        d = date(y, 11, 1); d += timedelta((6 - d.weekday()) % 7); out.append(d)                 # US 1st Sun Nov
        for m in (3, 10):
            d = date(y, m, 31); out.append(d - timedelta((d.weekday() - 6) % 7))                 # EU last Sun
    return out


EVENTS = {
    "Hurricane Barry": ("2019-07-12", "2019-07-15"), "COVID lab shutdowns": ("2020-03-16", "2020-03-28"),
    "Hurricane Idalia": ("2023-08-29", "2023-09-01"), "Jan 2024 US winter storm": ("2024-01-13", "2024-01-17"),
    "Hurricane Beryl": ("2024-07-07", "2024-07-10"), "CrowdStrike outage": ("2024-07-19", "2024-07-21"),
    "Hurricane Francine": ("2024-09-10", "2024-09-14"), "Hurricane Helene": ("2024-09-25", "2024-09-29"),
    "Hurricane Milton": ("2024-10-08", "2024-10-12"),
}


def run_pair(S, X, Y, holiday_mask=None):
    """X = shifted, Y = fixed."""
    bx = truncate_weeks(S[X]["blocks"])
    C = intersect(merge(bx), merge(S[Y]["blocks"]))
    if holiday_mask is not None:
        C = subtract(C, holiday_mask)
    common = float((C[:, 1] - C[:, 0]).sum()) if len(C) else 0.0
    if common < MIN_COMMON:
        return None
    both_iv = not S[X]["starts_only"] and not S[Y]["starts_only"]
    Yh = intersect(S[Y]["holes"], C) if both_iv else None
    Yp = S[Y]["pts"][in_set(S[Y]["pts"], C)]
    weeks = [int(round((e - s) / WEEK)) for s, e in bx]

    def metrics(offs):
        m = {}
        if both_iv:
            m["M0"] = overlap_len(shift_iv(S[X]["holes"], bx, offs) if any(offs) else clip(S[X]["holes"], bx), Yh)
        Xp = shift_pts(S[X]["pts"], bx, offs)
        Xp = Xp[in_set(Xp, C)]
        m["M5"] = coinc(Yp, Xp, 300)
        m["M60"] = coinc(Yp, Xp, 3600)
        return m
    obs = metrics([0.0] * len(bx))
    nulls = {k: [] for k in obs}
    for _ in range(NSHIFT):
        offs = [float(rng.integers(1, w)) * WEEK for w in weeks]
        for k, v in metrics(offs).items():
            nulls[k].append(v)
    res = {}
    for k in obs:
        n = np.array(nulls[k], float)
        ge = int((n >= obs[k]).sum())
        res[k] = dict(observed=obs[k], null_mean=float(n.mean()), null_sd=float(n.std()),
                      null_p95=float(np.percentile(n, 95)), p=ge / NSHIFT, p_conservative=(1 + ge) / (NSHIFT + 1))
    distinct = int(np.prod([w - 1 for w in weeks])) if len(weeks) < 4 else ">1e6"
    info = dict(shifted=X, fixed=Y, common_days=common / 86400, n_fixed_starts=int(len(Yp)),
                distinct_offsets=distinct, fixed_hole_frac=(float((Yh[:, 1] - Yh[:, 0]).sum()) / common if both_iv else None))
    return info, res, (C, Yh, Yp, bx)


def shifted_of(a, b):
    rank = {"NIST": 0, "IBM": 1, "IBMon": 1, "H1": 2, "L1": 3, "V1": 4, "K1": 5}
    if rank[a] < 2 or rank[b] < 2:
        return (a, b) if rank[a] <= rank[b] else (b, a)
    return (a, b) if rank[a] > rank[b] else (b, a)   # LIGO-LIGO: later detector shifted


def cause_check(S, X, Y, C, Yh):
    """fraction of observed co-absence seconds (M0) falling in DST/holiday/event windows vs those windows' share of C."""
    if Yh is None:
        return None
    co = intersect(clip(S[X]["holes"], [(c0, c1) for c0, c1 in C]), Yh)
    tot = float((co[:, 1] - co[:, 0]).sum()) if len(co) else 0.0
    ctot = float((C[:, 1] - C[:, 0]).sum())
    out = {"co_absence_s": tot}
    wins = {"DST+/-1d": day_windows(dst_days()), "US holidays+/-1d": day_windows(us_holidays())}
    for name, (a, b) in EVENTS.items():
        wins[name] = np.array([[ts(a + "T00:00:00Z"), ts(b + "T00:00:00Z")]])
    for name, w in wins.items():
        share_c = overlap_len(C, w) / ctot
        share_co = overlap_len(co, w) / tot if tot else 0.0
        if share_c > 0:
            out[name] = dict(share_of_coabsence=round(share_co, 4), share_of_coverage=round(share_c, 4))
    return out


def main():
    S = load()
    srcs = ["NIST", "IBM", "H1", "L1", "V1", "K1"]
    pairs = [shifted_of(a, b) for a, b in combinations(srcs, 2)] + [shifted_of("IBMon", d) for d in ("NIST", "H1", "L1", "V1", "K1")]
    hol = day_windows(us_holidays())
    out = {"preregistered": "gridsong/biblioteca.md 2026-09-26 ~21:30Z", "n_shifts": NSHIFT, "seed": 20260926,
           "primary": [], "holiday_excluded": [], "dropped": []}
    keep = {}
    for label, mask in (("primary", None), ("holiday_excluded", hol)):
        for X, Y in pairs:
            r = run_pair(S, X, Y, mask)
            if r is None:
                if label == "primary":
                    out["dropped"].append(f"{Y}~{X} (<28 d common coverage)")
                continue
            info, res, extra = r
            out[label].append(dict(pair=f"{Y}~{X}", **info, metrics=res))
            if label == "primary":
                keep[(X, Y)] = extra
            print(label, f"{Y}~{X}", {k: (round(v['observed'], 1), round(v['null_mean'], 1), v['p']) for k, v in res.items()})
    for label in ("primary", "holiday_excluded"):
        n = sum(len(e["metrics"]) for e in out[label])
        out[label + "_n_tests"] = n
        for e in out[label]:
            for k, v in e["metrics"].items():
                v["p_bonf"] = min(1.0, v["p"] * n)
                v["p_bonf_conservative"] = min(1.0, v["p_conservative"] * n)
                v["survives"] = v["p_bonf"] < 0.05
    out["survivors_primary"] = [f"{e['pair']} {k}" for e in out["primary"] for k, v in e["metrics"].items() if v["survives"]]
    out["survivors_holiday_excluded"] = [f"{e['pair']} {k}" for e in out["holiday_excluded"] for k, v in e["metrics"].items() if v["survives"]]
    out["cause_check"] = {}
    for e in out["primary"]:
        X, Y = e["shifted"], e["fixed"]
        C, Yh, _, _ = keep[(X, Y)]
        out["cause_check"][e["pair"]] = cause_check(S, X, Y, C, Yh)
    json.dump(out, open(os.path.join(HERE, "lineup_results.json"), "w"), indent=1, default=str)
    print("survivors primary:", out["survivors_primary"])
    print("survivors holiday-excluded:", out["survivors_holiday_excluded"])
    plot(S)


L_merge = merge


def plot(S):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    rows = ["NIST", "IBM", "IBMon", "H1", "L1", "V1", "K1"]
    ap = os.path.join(HERE, "anomaly_jobs.json")
    if os.path.exists(ap):   # written-off anomalies (our IBM jobs, 9/24) as an event row
        aj = json.load(open(ap))
        S = dict(S, ANOM=dict(holes=L_merge([(ts(j["running"]), ts(j["finished"])) for j in aj]),
                              blocks=[(ts(min(j["running"] for j in aj)), ts(max(j["finished"] for j in aj)))], starts_only=False))
        rows = ["ANOM"] + rows
    col = {"ANOM": "#b8860b", "NIST": "#7a3b8f", "IBM": "#1f5fa8", "IBMon": "#1f5fa8", "H1": "#b5561b", "L1": "#b5561b", "V1": "#2f7d4a", "K1": "#777777"}
    fig, axes = plt.subplots(2, 1, figsize=(13, 6.5), facecolor="white")
    spans = [(ts("2018-07-01T00:00:00Z"), ts("2026-10-01T00:00:00Z")), (ts("2024-05-10T00:00:00Z"), ts("2025-02-01T00:00:00Z"))]
    titles = ["Outside-recorded holes, 2018-2026 (light band = coverage; dark = hole; NIST/IBM/anomaly holes widened to be visible)",
              "Zoom: the only span all five sources overlap (LIGO O4b x IBM x NIST)"]
    ep = lambda t: mdates.date2num(datetime.fromtimestamp(t, timezone.utc))
    for ax, (t0, t1), title in zip(axes, spans, titles):
        minw = (t1 - t0) / 1500
        for i, r in enumerate(rows):
            y = len(rows) - 1 - i
            for s, e in S[r]["blocks"]:
                ax.broken_barh([(ep(s), ep(e) - ep(s))], (y - 0.35, 0.7), color=col[r], alpha=0.12, lw=0)
            if S[r]["holes"] is not None:
                h = S[r]["holes"]
                h = h[(h[:, 1] > t0) & (h[:, 0] < t1)]
                # sparse sources get a visible minimum width; LIGO (25-50% hole duty) is drawn at true width
                mw = (minw * (6 if r == "ANOM" else 1) if r in ("ANOM", "NIST", "IBM") else 0) / 86400
                bars = [(ep(a), max(ep(b) - ep(a), mw)) for a, b in h]
                ax.broken_barh(bars, (y - 0.35, 0.7), color=col[r], lw=0)
            else:
                p = S[r]["pts"]
                p = p[(p > t0) & (p < t1)]
                ax.vlines([ep(x) for x in p], y - 0.35, y + 0.35, color=col[r], lw=0.4)
        ax.set_yticks(range(len(rows)))
        ax.set_yticklabels(["our anomalies" if r == "ANOM" else "IBM onsets" if r == "IBMon" else ("IBM no-cal" if r == "IBM" else r) for r in rows][::-1])
        ax.set_xlim(ep(t0), ep(t1))
        ax.xaxis_date()
        ax.set_title(title, fontsize=10, loc="left")
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "lineup.png"), dpi=130)


if __name__ == "__main__":
    main()
