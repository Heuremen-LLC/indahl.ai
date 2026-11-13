#!/usr/bin/env python3
"""rhythms.py -- let the holes show their own rhythms (read-only, no targeted numbers).

Run:  ~/bones-forge/qvenv/bin/python rhythms.py      (needs numpy, scipy, matplotlib, astropy)

Sources (each over its OWN coverage):
  NIST                beacon holes (gaps, cert changes, skipped index, chain restart)
  IBM_fez/marrakesh/kingston  calibration holes (starts = every condition start; 0/1 = no-calibration intervals)
  H1, L1, V1, K1      GWOSC data-off segments
  ABSENCE             our rejected Braket tasks (20 tasks in ~10 s: no spectrum possible at >= 2 min)

Part A  global spectra: Lomb-Scargle on (a) hole-start counts and (b) 0/1 in-hole series.
        short band: 1-min bins, periods 2 min .. 1 d.   long band: 30-min bins, periods 1 d .. min(2 y, span/2).
        IBM is snapshot-limited (one calibration record/day), so IBM starts at >= 2 d only.
        FAP_boot = permutation bootstrap of the band max: long band 300 draws empirical; short band (4M freqs,
        ~30 s/draw) 30 draws + Gumbel fit to the draw maxima, extrapolated to the tail.
        FAP_local = peak vs its own local continuum (running median, +/-0.125 dex), exponential tail x independent freqs.
        A peak counts as significant only if BOTH < 0.01 (bootstrap alone passes every red-noise shoulder).
Part B  cross-source shared periods (+/-2% or peak width), known-rhythm labels, pairwise coherence (segment-averaged, common coverage).
Part C  short-lived bursts: sliding windows at 5 scales. starts -> Rayleigh/Schuster periodogram on exact times;
        0/1 -> Lomb-Scargle on binned occupancy. Burst = analytic FAP < 1e-3 AND power >= 3x the source's median
        at that frequency across all its windows. Adjacent flagged windows with period within 10% merge.
Part D  superposed-epoch: B's in-hole series +/-6 h around every A hole start, vs calendar-preserving shuffles
        (each epoch moved by a random whole number of weeks, +/-8), 200 shuffles.
Part E  cross-source burst overlaps: bursts in different sources overlapping in time, periods within 10%.
Part F  DARKWAVE lag asymmetry, pre-registered in biblioteca 2026-09-26 ~23:40Z (before computing).
Every hole is kept at full weight; "known" is a label carried beside a period, never a filter.
"""
import json, os, sys, time
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
from datetime import datetime, timezone
import numpy as np
from multiprocessing import get_context

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(HERE, "rhythms_results.json")
OUT_PNG = os.path.join(HERE, "rhythms.png")
DAY, HOUR, MIN, WEEK, YEAR = 86400.0, 3600.0, 60.0, 7 * 86400.0, 365.25 * 86400.0
IBM_END = "2026-09-25T23:59:59Z"
NPROC = 14


def ts(s):
    s = s.replace("Z", "+00:00")
    d = datetime.fromisoformat(s)
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.timestamp()


def iso(t):
    return datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def fmt_p(p):
    if p < 2 * MIN: return f"{p:.0f} s"
    if p < 2 * HOUR: return f"{p/MIN:.2f} min"
    if p < 2 * DAY: return f"{p/HOUR:.3f} h"
    return f"{p/DAY:.3f} d"


# ---------------- known human / instrument rhythms ----------------
def known_table():
    K = []
    for k in range(1, 25): K.append((f"day/{k}" if k > 1 else "1 day", DAY / k))
    for k in range(1, 31): K.append((f"hour/{k}" if k > 1 else "1 hour", HOUR / k))
    for n in range(2, 11): K.append((f"{n} min (60-s pulse grid)", n * MIN))
    for k in range(1, 8): K.append((f"week/{k}" if k > 1 else "7 days (weekly maintenance)", WEEK / k))
    K += [("2 weeks", 2 * WEEK), ("4 weeks", 4 * WEEK), ("sidereal day", 86164.09), ("sidereal day/2", 43082.05),
          ("M2 lunar tide 12.42 h", 12.4206 * HOUR), ("O1 lunar tide 25.82 h", 25.8193 * HOUR),
          ("lunar month", 29.5306 * DAY), ("Mf fortnightly tide", 13.661 * DAY), ("month", YEAR / 12),
          ("quarter", YEAR / 4), ("half year", YEAR / 2), ("year", YEAR), ("4 months", YEAR / 3)]
    return K


KNOWN = known_table()


def label_known(P, w=0.0):
    tol = max(0.02 * P, w)
    hits = [n for n, q in KNOWN if abs(P - q) <= tol]
    return ", ".join(dict.fromkeys(hits)) if hits else ""


# ---------------- load ----------------
def merge_iv(iv):
    iv = sorted(iv)
    out = []
    for a, b in iv:
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def load_sources():
    S = {}
    nist, ibm = [], {}
    for line in open(os.path.join(HERE, "outside_holes.jsonl")):
        d = json.loads(line)
        a = ts(d["at"])
        if d["provider"] == "nist-beacon":
            b = ts(d["ended"]) if d["ended"] else a
            nist.append((a, max(b, a)))
        elif d["provider"] == "ibm-calibration":
            bk = d["device"].split("/")[0]
            r = ibm.setdefault(bk, dict(starts=[], nocal=[]))
            r["starts"].append(a)
            if d["kind"] == "no-calibration":
                r["nocal"].append((a, ts(d["ended"]) if d["ended"] else ts(IBM_END)))
    S["NIST"] = dict(group="NIST", blocks=[(ts("2018-07-23T19:26:00Z"), ts("2026-09-26T18:23:00Z"))],
                     starts=np.array(sorted(a for a, b in nist)), holes=merge_iv(nist), res_floor=2 * MIN, min_period=2 * MIN)
    for bk in sorted(ibm):
        st = np.array(sorted(ibm[bk]["starts"]))
        S["IBM_" + bk.replace("ibm_", "")] = dict(group="IBM", blocks=[(st.min(), ts(IBM_END))], starts=st,
                                                  holes=merge_iv(ibm[bk]["nocal"]), res_floor=2 * DAY, min_period=2 * DAY)
    lig = {}
    for line in open(os.path.join(HERE, "ligo_holes.jsonl")):
        d = json.loads(line)
        lig.setdefault(d["device"], []).append((ts(d["at"]), ts(d["ended"])))
    cov = json.load(open(os.path.join(HERE, "ligo_coverage.json")))
    grp = dict(H1="LIGO", L1="LIGO", V1="Virgo", K1="KAGRA")
    for det in ("H1", "L1", "V1", "K1"):
        S[det] = dict(group=grp[det], blocks=[(ts(r["at"]), ts(r["ended"])) for r in cov[det]],
                      starts=np.array(sorted(a for a, b in lig[det])), holes=merge_iv(lig[det]), res_floor=20.0, min_period=2 * MIN)
    ab = [ts(json.loads(l)["at"]) for l in open(os.path.join(HERE, "..", "standoff", "absence_ledger.jsonl")) if l.strip()]
    absence = dict(n=len(ab), first=iso(min(ab)), last=iso(max(ab)), span_s=max(ab) - min(ab),
                   median_spacing_s=float(np.median(np.diff(sorted(ab)))) if len(ab) > 1 else None,
                   note="coverage shorter than the 2-min shortest period: no spectrum, no bursts, no epochs")
    return S, absence


# ---------------- minute grids ----------------
def build_grid(src):
    """1-min grid aligned so m0 is a multiple of 30 (30-min aggregation lines up across sources)."""
    lo = min(a for a, b in src["blocks"]); hi = max(b for a, b in src["blocks"])
    m0 = int(np.floor(lo / MIN)) // 30 * 30
    n = int(np.ceil(hi / MIN)) - m0 + 1
    n = (n + 29) // 30 * 30
    cov = np.zeros(n, bool)
    for a, b in src["blocks"]:
        cov[int(np.floor(a / MIN)) - m0: int(np.ceil(b / MIN)) - m0] = True
    d = np.zeros(n + 1, np.int32)
    for a, b in src["holes"]:
        i = int(np.floor(a / MIN)) - m0; j = max(int(np.ceil(b / MIN)) - m0, i + 1)
        i, j = max(i, 0), min(j, n)
        if j > i: d[i] += 1; d[j] -= 1
    occ = (np.cumsum(d[:n]) > 0).astype(np.float32)
    cnt = np.zeros(n, np.float32)
    idx = np.floor(src["starts"] / MIN).astype(np.int64) - m0
    idx = idx[(idx >= 0) & (idx < n)]
    np.add.at(cnt, idx, 1)
    occ[~cov] = 0
    src.update(m0=m0, cov=cov, occ=occ, cnt=cnt, span=hi - lo)


def series_at(src, res):
    """(t_centers, starts, occ, covfrac, absolute bin index) at res seconds (60 or multiple of 60)."""
    k = int(res // MIN)
    cov, occ, cnt = src["cov"], src["occ"], src["cnt"]
    n = len(cov) // k * k
    if src["m0"] % k:  # align start to absolute multiple of k minutes
        off = (-src["m0"]) % k
    else:
        off = 0
    n = (len(cov) - off) // k * k
    c = cov[off:off + n].reshape(-1, k).mean(1)
    s = cnt[off:off + n].reshape(-1, k).sum(1)
    o = occ[off:off + n].reshape(-1, k).sum(1) / np.maximum(c * k, 1)
    b0 = (src["m0"] + off) // k
    idx = b0 + np.arange(len(c))
    t = (idx + 0.5) * res
    return t, s, o, c, idx


# ---------------- Part A: global Lomb-Scargle ----------------
_NB = float(os.environ.get("RHY_BOOT", "1"))
BANDS = [("short", 60.0, 2 * MIN, DAY, 2, max(3, int(30 * _NB))), ("long", 1800.0, DAY, 2 * YEAR, 10, max(3, int(300 * _NB)))]
_G = {}


def _ls(t, y, f):
    from astropy.timeseries import LombScargle
    return LombScargle(t, y).power(f, method="fast")


def _boot(args):
    key, seed = args
    t, y, f = _G[key]
    r = np.random.default_rng(seed)
    return float(_ls(t, r.permutation(y), f).max())


def continuum(f, p):
    lf = np.log10(f)
    w = 0.025
    edges = np.arange(lf.min(), lf.max() + w, w)
    b = np.clip(np.digitize(lf, edges) - 1, 0, len(edges) - 1)
    order = np.argsort(b, kind="stable")
    bs = b[order]
    cuts = np.searchsorted(bs, np.arange(len(edges) + 1))
    med = np.full(len(edges), np.nan)
    ps = p[order]
    # running median over +/-5 bins (+/-0.125 dex)
    for i in range(len(edges)):
        lo, hi = cuts[max(i - 5, 0)], cuts[min(i + 6, len(edges))]
        if hi > lo: med[i] = np.median(ps[lo:hi])
    return med[b]


def global_spectra(S):
    from scipy.signal import find_peaks
    jobs, specs = [], {}
    for name, src in S.items():
        for band, res, pmin, pmax, osamp, nboot in BANDS:
            lo = max(pmin, src["min_period"]); hi = min(pmax, src["span"] / 2)
            if hi <= lo * 1.05: continue
            t, s, o, c, _ = series_at(src, res)
            m = c >= 0.5
            for kind, y in (("starts", s[m]), ("inhole", o[m])):
                if np.var(y) == 0 or np.count_nonzero(y) < 3: continue
                tt = t[m]
                T = tt[-1] - tt[0]
                f = np.arange(1 / hi, 1 / lo, 1 / (T * osamp))
                key = (name, band, kind)
                specs[key] = dict(t=tt, y=y.astype(np.float64), f=f, T=T, osamp=osamp, nboot=nboot)
    print(f"[A] {len(specs)} spectra", flush=True)
    for key, d in specs.items():
        t0 = time.time()
        d["p"] = _ls(d["t"], d["y"], d["f"])
        print(f"   {key} N={len(d['t'])} Nf={len(d['f'])} {time.time()-t0:.1f}s", flush=True)
    # bootstrap in parallel (fork shares arrays)
    for key, d in specs.items():
        _G[key] = (d["t"], d["y"], d["f"])
        jobs += [(key, hash((key, i)) & 0xFFFFFFFF) for i in range(d["nboot"])]
    t0 = time.time()
    with get_context("fork").Pool(NPROC) as pool:
        res = pool.map(_boot, jobs, chunksize=1)
    print(f"[A] bootstrap {len(jobs)} runs {time.time()-t0:.0f}s", flush=True)
    boots = {}
    for (key, _), v in zip(jobs, res):
        boots.setdefault(key, []).append(v)
    out = {}
    for key, d in specs.items():
        f, p = d["f"], d["p"]
        bm = np.sort(np.array(boots[key]))
        cont = continuum(f, p)
        neff = len(f) / d["osamp"]
        pk, _ = find_peaks(p, distance=max(1, d["osamp"]))
        peaks = []
        for i in pk:
            if len(bm) >= 100:
                fb = (np.sum(bm >= p[i]) + 1) / (len(bm) + 1)
            else:  # few draws (short band, 4M freqs): Gumbel fit to the bootstrap maxima, extrapolated
                beta = np.std(bm) * np.sqrt(6) / np.pi; mu = np.mean(bm) - 0.5772 * beta
                fb = float(-np.expm1(-np.exp(-(p[i] - mu) / max(beta, 1e-12))))
            if fb >= 0.01: continue
            r = p[i] / cont[i]
            p1 = np.exp(-r * np.log(2))
            fl = float(-np.expm1(neff * np.log1p(-min(p1, 1 - 1e-16)))) if p1 > 0 else 0.0
            if fl >= 0.01: continue
            P = 1 / f[i]
            w = P * P / d["T"] / 2  # half-width in period
            peaks.append(dict(period_s=float(P), period=fmt_p(P), power=float(p[i]), local_ratio=float(r),
                              fap_boot=float(fb), fap_local=fl, halfwidth_s=float(w), known=label_known(P, w)))
        peaks.sort(key=lambda x: -x["local_ratio"])
        out[key] = dict(n_bins=int(len(d["t"])), n_freq=int(len(f)), span_days=d["T"] / DAY, n_boot=int(len(bm)),
                        fap_boot_method="empirical" if len(bm) >= 100 else "Gumbel fit to bootstrap maxima",
                        boot_max_q99=float(np.quantile(bm, 0.99)), n_significant=len(peaks), peaks=peaks[:40],
                        _curve=(f, p))
    return out


# ---------------- Part B: shared periods + coherence ----------------
def shared_periods(A, S):
    allp = []
    for (src, band, kind), d in A.items():
        for pk in d["peaks"]:
            allp.append(dict(pk, source=src, band=band, series=kind, group=S[src]["group"]))
    allp.sort(key=lambda x: x["period_s"])
    clusters = []
    for p in allp:
        if clusters:
            c = clusters[-1]
            ctr = np.exp(np.mean(np.log([q["period_s"] for q in c])))
            if abs(p["period_s"] - ctr) <= max(0.02 * ctr, p["halfwidth_s"] + max(q["halfwidth_s"] for q in c)):
                c.append(p); continue
        clusters.append([p])
    shared = []
    for c in clusters:
        srcs = sorted({q["source"] for q in c})
        if len(srcs) < 2: continue
        grps = sorted({q["group"] for q in c})
        P = float(np.exp(np.mean(np.log([q["period_s"] for q in c]))))
        w = max(q["halfwidth_s"] for q in c)
        best = {}
        for q in c:
            if q["source"] not in best or q["local_ratio"] > best[q["source"]]["local_ratio"]:
                best[q["source"]] = q
        shared.append(dict(period_s=P, period=fmt_p(P), sources=srcs, groups=grps, n_groups=len(grps),
                           known=label_known(P, w),
                           members=[dict(source=s, series=best[s]["series"], period=best[s]["period"],
                                         local_ratio=round(best[s]["local_ratio"], 1), power=round(best[s]["power"], 4))
                                    for s in srcs],
                           strength=float(sum(np.log10(best[s]["local_ratio"]) for s in srcs))))
    shared.sort(key=lambda x: (-x["n_groups"], -x["strength"]))
    return shared


def coherence(S, a, b, P, kind):
    res = 60.0 if P < DAY else 1800.0
    ta, sa, oa, ca, ia = series_at(S[a], res)
    tb, sb, ob, cb, ib = series_at(S[b], res)
    lo, hi = max(ia[0], ib[0]), min(ia[-1], ib[-1])
    if hi <= lo: return None
    xa = (sa if kind == "starts" else oa)[lo - ia[0]:hi - ia[0] + 1]
    xb = (sb if kind == "starts" else ob)[lo - ib[0]:hi - ib[0] + 1]
    ma = ca[lo - ia[0]:hi - ia[0] + 1] >= 0.5
    mb = cb[lo - ib[0]:hi - ib[0] + 1] >= 0.5
    m = ma & mb
    for nper in (8, 4, 2):
        L = max(int(round(nper * P / res)), 16)
        K = len(m) // L
        if K < 4: continue
        M = m[:K * L].reshape(K, L)
        keep = M.mean(1) >= 0.8
        if keep.sum() < 4: continue
        X = xa[:K * L].reshape(K, L)[keep].astype(float); Y = xb[:K * L].reshape(K, L)[keep].astype(float); M = M[keep]
        X = np.where(M, X - (X * M).sum(1, keepdims=True) / M.sum(1, keepdims=True), 0)
        Y = np.where(M, Y - (Y * M).sum(1, keepdims=True) / M.sum(1, keepdims=True), 0)
        e = np.exp(-2j * np.pi * np.arange(L) * res / P)
        FX, FY = X @ e, Y @ e
        den = (np.abs(FX) ** 2).sum() * (np.abs(FY) ** 2).sum()
        if den == 0: return dict(segments=int(keep.sum()), coherence=None, note="one series flat in overlap")
        C = float(np.abs((FX * FY.conj()).sum()) ** 2 / den)
        k = int(keep.sum())
        phase = float(np.degrees(np.angle((FX * FY.conj()).sum())))
        return dict(segments=k, seg_periods=nper, coherence=round(C, 4), p_value=float((1 - C) ** (k - 1)),
                    phase_deg=round(phase, 1), lag_s=round(phase / 360 * P, 1))
    return None


# ---------------- Part C: sliding-window bursts ----------------
SCALES = [  # name, window, step, occ res, pmin, pmax
    ("S0", HOUR, 15 * MIN, None, 20.0, 15 * MIN),
    ("S1", 6 * HOUR, 90 * MIN, 60.0, 2 * MIN, 90 * MIN),
    ("S2", 3 * DAY, 18 * HOUR, 600.0, 90 * MIN, 18 * HOUR),
    ("S3", 30 * DAY, 7.5 * DAY, 3600.0, 18 * HOUR, 7.5 * DAY),
    ("S4", 180 * DAY, 45 * DAY, 6 * HOUR, 7.5 * DAY, 45 * DAY),
]


def rayleigh_windows(name, src, sc):
    scn, W, step, _, pmin, pmax = sc
    lo_p = max(pmin, src["res_floor"])
    if lo_p >= pmax: return []
    st = np.unique(src["starts"])
    f = np.arange(1 / pmax, 1 / lo_p, 1 / (3 * W))
    rows = []
    for a, b in src["blocks"]:
        for w0 in np.arange(a, b - W + 1, step):
            i, j = np.searchsorted(st, [w0, w0 + W])
            n = j - i
            if n < 5: continue
            tt = st[i:j] - w0
            Z = np.abs(np.exp(2j * np.pi * np.outer(tt, f)).sum(0)) ** 2 / n
            rows.append((w0, n, Z))
    return rows, f, W


def ls_windows(name, src, sc):
    from astropy.timeseries import LombScargle
    scn, W, step, res, pmin, pmax = sc
    if res is None: return [], None, W
    lo_p = max(pmin, 2 * res, src["res_floor"] if src["group"] == "IBM" else 0)
    if lo_p >= pmax: return [], None, W
    t, s, o, c, idx = series_at(src, res)
    f = np.arange(1 / pmax, 1 / lo_p, 1 / (3 * W))
    nb = int(W // res); stp = max(1, int(step // res))
    rows = []
    for i in range(0, len(t) - nb + 1, stp):
        cc = c[i:i + nb]
        if cc.mean() < 0.8: continue
        m = cc >= 0.5
        y = o[i:i + nb][m]; sN = s[i:i + nb].sum()
        if sN < 3 or np.var(y) == 0: continue
        tt = t[i:i + nb][m]
        ls = LombScargle(tt, y)
        p = ls.power(f, method="fast" if len(tt) > 200 else "cython")
        rows.append((t[i] - res / 2, int(sN), p, ls))
    return rows, f, W


def bursts_for(args):
    name, sci, kind = args
    src = _G["S"][name]; sc = SCALES[sci]
    if kind == "starts":
        r = rayleigh_windows(name, src, sc)
        if not r or not r[0]: return []
        rows, f, W = r
    else:
        rows, f, W = ls_windows(name, src, sc)
        if not rows: return []
    Pm = np.array([r[2] for r in rows])
    bg = np.median(Pm, axis=0)
    bg = np.where(bg > 0, bg, np.nanmean(Pm))
    neff = len(f) / 3
    flagged = []
    for k, r in enumerate(rows):
        p = r[2]; j = int(np.argmax(p / bg)); strength = float(p[j] / bg[j])
        if kind == "starts":
            fap = float(-np.expm1(neff * np.log1p(-np.exp(-p[j])))) if p[j] < 700 else 0.0
        else:
            fap = float(r[3].false_alarm_probability(p[j], minimum_frequency=f[0], maximum_frequency=f[-1]))
        if fap < 1e-3 and strength >= 3:
            flagged.append(dict(w0=float(r[0]), w1=float(r[0] + W), period_s=float(1 / f[j]), strength=strength,
                                fap=fap, n_starts=int(r[1])))
    # merge
    out = []
    for fl in sorted(flagged, key=lambda x: x["w0"]):
        if out and fl["w0"] <= out[-1]["w1"] and abs(fl["period_s"] - out[-1]["period_s"]) <= 0.1 * out[-1]["period_s"]:
            o = out[-1]; o["w1"] = max(o["w1"], fl["w1"]); o["n_windows"] += 1
            if fl["strength"] > o["strength"]: o["strength"], o["period_s"] = fl["strength"], fl["period_s"]
            o["fap"] = min(o["fap"], fl["fap"]); o["n_starts_peak"] = max(o["n_starts_peak"], fl["n_starts"])
        else:
            out.append(dict(w0=fl["w0"], w1=fl["w1"], period_s=fl["period_s"], strength=fl["strength"], fap=fl["fap"],
                            n_windows=1, n_starts_peak=fl["n_starts"]))
    res = []
    for o in out:
        res.append(dict(source=name, scale=sc[0], series=kind, start=iso(o["w0"]), end=iso(o["w1"]), t0=o["w0"], t1=o["w1"],
                        period_s=o["period_s"], period=fmt_p(o["period_s"]), strength=round(o["strength"], 2),
                        fap=o["fap"], n_windows=o["n_windows"], n_starts_peak=o["n_starts_peak"],
                        known=label_known(o["period_s"]), windows_scanned=len(rows)))
    return res


# ---------------- Part D: superposed epochs ----------------
def epoch_pair(S, a, b, nshuf=200, half=360):
    A, B = S[a], S[b]
    lo = max(A["m0"], B["m0"]); hi = min(A["m0"] + len(A["cov"]), B["m0"] + len(B["cov"]))
    if hi - lo < 2 * half + 1: return None
    ep = np.unique(np.floor(A["starts"] / MIN).astype(np.int64))
    ep = ep[(ep >= lo + half) & (ep < hi - half)]
    covB = B["cov"].astype(np.int32); cs = np.concatenate([[0], np.cumsum(covB)])
    occB = B["occ"]
    lags = np.arange(-half, half + 1)

    def valid(e):
        i = e - B["m0"]
        ok = (i - half >= 0) & (i + half + 1 <= len(covB))
        ii = np.clip(i, half, len(covB) - half - 1)
        full = (cs[ii + half + 1] - cs[ii - half]) == 2 * half + 1
        return ok & full

    ep = ep[valid(ep)]
    if len(ep) < 10: return None

    def curve(e):
        i = e - B["m0"]
        return occB[i[:, None] + lags[None, :]].mean(0)

    obs = curve(ep)
    r = np.random.default_rng(len(ep) * 7919 + len(a) + 31 * len(b))
    sh = []
    for _ in range(nshuf):
        k = r.integers(1, 9, len(ep)) * r.choice([-1, 1], len(ep))
        e2 = ep + k * int(WEEK / MIN)
        e2 = e2[valid(e2)]
        if len(e2) < 10: continue
        sh.append(curve(e2))
    sh = np.array(sh)
    mu, sd = sh.mean(0), sh.std(0)
    sd = np.where(sd > 0, sd, np.nan)
    z = (obs - mu) / sd
    zs = (sh - mu) / sd
    jmax = int(np.nanargmax(z)) if np.isfinite(z).any() else half
    zmax = float(np.nanmax(z)) if np.isfinite(z).any() else 0.0
    gp = float((np.sum(np.nanmax(zs, 1) >= zmax) + 1) / (len(sh) + 1))
    # lag-localized structure: remove each curve's own +/-6 h mean (a plateau = slow co-variation, not a lag)
    od = obs - obs.mean(); shd = sh - sh.mean(1, keepdims=True)
    mud, sdd = shd.mean(0), shd.std(0)
    sdd = np.where(sdd > 0, sdd, np.nan)
    zd = (od - mud) / sdd; zsd = (shd - mud) / sdd
    jd = int(np.nanargmax(np.abs(zd))) if np.isfinite(zd).any() else half
    zdm = float(np.abs(zd[jd])) if np.isfinite(zd).any() else 0.0
    gpd = float((np.sum(np.nanmax(np.abs(zsd), 1) >= zdm) + 1) / (len(sh) + 1))
    return dict(A=a, B=b, n_epochs=int(len(ep)), n_shuffles=int(len(sh)),
                plateau_excess=float(obs.mean() - mu.mean()),
                lag_structure=dict(peak_lag_min=int(lags[jd]), dev_from_plateau=float(od[jd] - mud[jd]), abs_z=zdm, global_p=gpd),
                peak_lag_min=int(lags[jmax]),
                B_inhole_at_peak=float(obs[jmax]), baseline_at_peak=float(mu[jmax]), excess=float(obs[jmax] - mu[jmax]),
                z=zmax, global_p=gp, excess_at_lag0=float(obs[half] - mu[half]), z_at_lag0=float(z[half]) if np.isfinite(z[half]) else None,
                _obs=obs, _mu=mu)



# ---------------- Part F: darkwave lag asymmetry (PRE-REGISTERED in biblioteca 2026-09-26 ~23:40Z) ----------------
ASYM_W = (5, 60, 360)


def _asym(eb, ea):
    den = np.abs(eb) + np.abs(ea)
    return np.where(den > 0, (eb - ea) / np.where(den > 0, den, 1), 0.0)


def asym_pair(S, a, b, nshuf=10000, half=360, chunk=250):
    A, B = S[a], S[b]
    lo = max(A["m0"], B["m0"]); hi = min(A["m0"] + len(A["cov"]), B["m0"] + len(B["cov"]))
    if hi - lo < 2 * half + 1: return None
    n = len(B["cov"])
    cs = np.concatenate([[0.0], np.cumsum(B["occ"], dtype=np.float64)])
    cc = np.concatenate([[0], np.cumsum(B["cov"].astype(np.int64))])
    ep = np.unique(np.floor(A["starts"] / MIN).astype(np.int64)) - B["m0"]

    def ok_fwd(i):
        good = (i - half >= 0) & (i + half + 1 <= n)
        ii = np.clip(i, half, n - half - 1)
        return good & ((cc[ii + half + 1] - cc[ii - half]) == 2 * half + 1)

    ep = ep[ok_fwd(ep)]
    if len(ep) < 10: return None
    E = len(ep)
    W = np.array(ASYM_W)

    def sums_fwd(i):  # i: (..., E) -> before/after means per W: (..., 3)
        bef = np.stack([(cs[i] - cs[i - w]) / w for w in W], -1)
        aft = np.stack([(cs[i + w + 1] - cs[i + 1]) / w for w in W], -1)
        return bef, aft

    ob, oa = sums_fwd(ep)
    ob, oa = ob.mean(0), oa.mean(0)
    rng = np.random.default_rng(E * 104729 + len(a) * 13 + len(b))
    wk = int(WEEK / MIN)
    # null 1: calendar-preserving epoch shuffles
    n1b, n1a = [], []
    for c0 in range(0, nshuf, chunk):
        c = min(chunk, nshuf - c0)
        k = rng.integers(1, 9, (c, E)) * rng.choice([-1, 1], (c, E))
        i2 = ep[None, :] + k * wk
        v = ok_fwd(i2)
        i2 = np.where(v, i2, ep[None, :])
        bb, aa = sums_fwd(i2)
        vs = v.sum(1)[:, None]
        n1b.append((bb * v[..., None]).sum(1) / np.maximum(vs, 1)); n1a.append((aa * v[..., None]).sum(1) / np.maximum(vs, 1))
    n1b, n1a = np.concatenate(n1b), np.concatenate(n1a)
    base_b, base_a = n1b.mean(0), n1a.mean(0)
    eb, ea = ob - base_b, oa - base_a
    asym = _asym(eb, ea)
    null1 = _asym(n1b - base_b, n1a - base_a)
    # null 2: time-reversed B, random circular shift, A's real epochs.  B'(i) = B[n-1-((i-s) mod n)]
    def rev_sum(i, s, l0, l1):  # sum of B' over lags l0..l1 around i  (contiguous in B if no wrap)
        p = (i + l1 - s) % n; q = (i + l0 - s) % n
        lo_ = n - 1 - p; hi_ = n - 1 - q
        good = (hi_ - lo_) == (l1 - l0)
        return cs[np.clip(hi_ + 1, 0, n)] - cs[np.clip(lo_, 0, n)], good, lo_, hi_
    n2b, n2a = [], []
    for c0 in range(0, nshuf, chunk):
        c = min(chunk, nshuf - c0)
        s = rng.integers(0, n, (c, 1))
        i = ep[None, :]
        _, g, lo_, hi_ = rev_sum(i, s, -half, half)
        g = g & ((cc[np.clip(hi_ + 1, 0, n)] - cc[np.clip(lo_, 0, n)]) == 2 * half + 1)
        vs = g.sum(1)
        bb = np.stack([rev_sum(i, s, -w, -1)[0] / w for w in W], -1)
        aa = np.stack([rev_sum(i, s, 1, w)[0] / w for w in W], -1)
        n2b.append((bb * g[..., None]).sum(1) / np.maximum(vs, 1)[:, None])
        n2a.append((aa * g[..., None]).sum(1) / np.maximum(vs, 1)[:, None])
    n2b, n2a = np.concatenate(n2b), np.concatenate(n2a)
    null2 = _asym(n2b - base_b, n2a - base_a)
    # POST-HOC (not pre-registered): unnormalized difference. The registered ratio has a null that piles up near +/-1
    # whenever both excesses are near zero, so it cannot reach extreme p even for the A=B sanity case.
    dif = eb - ea
    d1 = (n1b - base_b) - (n1a - base_a); d2 = (n2b - base_b) - (n2a - base_a)
    pd1 = (np.sum(np.abs(d1) >= np.abs(dif)[None, :], 0) + 1) / (nshuf + 1)
    pd2 = (np.sum(np.abs(d2) >= np.abs(dif)[None, :], 0) + 1) / (nshuf + 1)
    p1 = (np.sum(np.abs(null1) >= np.abs(asym)[None, :], 0) + 1) / (nshuf + 1)
    p2 = (np.sum(np.abs(null2) >= np.abs(asym)[None, :], 0) + 1) / (nshuf + 1)
    rows = []
    for j, w in enumerate(W):
        rows.append(dict(A=a, B=b, window_min=int(w), n_epochs=int(E), B_before=float(ob[j]), B_after=float(oa[j]),
                         base_before=float(base_b[j]), base_after=float(base_a[j]), excess_before=float(eb[j]),
                         excess_after=float(ea[j]), asym=float(asym[j]), p_shuffle=float(p1[j]), p_reversed=float(p2[j]),
                         p=float(max(p1[j], p2[j])),
                         posthoc_diff=float(dif[j]), posthoc_p_shuffle=float(pd1[j]), posthoc_p_reversed=float(pd2[j]),
                         posthoc_p=float(max(pd1[j], pd2[j]))))
    return rows


def darkwave(S):
    rows = []
    for a in S:
        for b in S:
            r = asym_pair(S, a, b)
            if r: rows += r
    ntest = len(rows)
    alpha = 0.05 / ntest
    for r in rows: r["passes_bonferroni"] = r["p"] < alpha
    pairs = {}
    for r in rows:
        if r["A"] != r["B"] and r["passes_bonferroni"] and r["asym"] > 0:
            pairs.setdefault((r["A"], r["B"]), []).append(r["window_min"])
    dw = [dict(A=k[0], B=k[1], windows=v) for k, v in pairs.items() if len(v) >= 2]
    openeyes = sorted([r for r in rows if r["A"] != r["B"] and r["p"] < 0.01], key=lambda x: x["p"])
    for r in rows: r["posthoc_passes_bonferroni"] = r["posthoc_p"] < alpha
    ph = {}
    for r in rows:
        if r["A"] != r["B"] and r["posthoc_passes_bonferroni"] and r["posthoc_diff"] > 0:
            ph.setdefault((r["A"], r["B"]), []).append(r["window_min"])
    return dict(rule="biblioteca 2026-09-26 ~23:40Z DARKWAVE LAG-ASYMMETRY TEST (pre-registered)",
                posthoc_note="unnormalized excess_before - excess_after, same two nulls, same Bonferroni. NOT pre-registered.",
                posthoc_before_pairs=[dict(A=k[0], B=k[1], windows=v) for k, v in ph.items() if len(v) >= 2],
                posthoc_passing=[r for r in rows if r["posthoc_passes_bonferroni"]],
                n_tests=ntest, alpha_bonferroni=alpha, darkwave_pairs=dw,
                passing=[r for r in rows if r["passes_bonferroni"]], open_eyes=openeyes,
                self_reference=[r for r in rows if r["A"] == r["B"]], all=rows)


# ---------------- plot ----------------
def plot(A, S, shared, absence):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    names = list(S.keys())
    fig, axs = plt.subplots(len(names) + 1, 1, figsize=(13, 2.0 * (len(names) + 1)), sharex=True)
    fig.patch.set_facecolor("#fcfcfb")
    col = dict(starts="#2a78d6", inhole="#eb6834")
    for ax, name in zip(axs, names):
        ax.set_facecolor("#fcfcfb")
        for (src, band, kind), d in A.items():
            if src != name: continue
            f, p = d["_curve"]
            P = 1 / f
            # max-decimate onto log bins for plotting
            lb = np.linspace(np.log10(P.min()), np.log10(P.max()), 3000)
            b = np.clip(np.digitize(np.log10(P), lb), 0, len(lb))
            mx = np.full(len(lb) + 1, np.nan)
            np.fmax.at(mx, b, p)
            ok = np.isfinite(mx[1:])
            ax.plot(10 ** lb[ok] / DAY, mx[1:][ok], lw=0.8, color=col[kind],
                    label=("hole starts" if kind == "starts" else "0/1 in hole") if band == "long" or name == "NIST" else None)
        for sh in shared:
            if name in sh["sources"]:
                ax.axvline(sh["period_s"] / DAY, color="#8a8984" if sh["known"] else "#4a3aa7",
                           lw=1.0, ls=":" if sh["known"] else "--", alpha=0.9)
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_ylabel("LS power", fontsize=8, color="#52514e")
        ax.text(0.005, 0.85, f"{name}  ({S[name]['group']}, {S[name]['span']/DAY:.0f} d span)", transform=ax.transAxes,
                fontsize=9, color="#0b0b0b")
        ax.tick_params(labelsize=7, colors="#52514e")
        for s in ("top", "right"): ax.spines[s].set_visible(False)
    axs[0].legend(fontsize=7, loc="upper right", frameon=False)
    ax = axs[-1]; ax.axis("off")
    ax.text(0.005, 0.5, f"ABSENCE (our rejected tasks): {absence['n']} tasks in {absence['span_s']:.1f} s on {absence['first'][:10]} "
            f"-- shorter than the 2-min shortest period, no spectrum.\nPurple dashed = shared period, not a known rhythm.  "
            f"Gray dotted = shared, matches a known human/instrument rhythm.", fontsize=8, color="#52514e", transform=ax.transAxes)
    ticks = [2 * MIN, 10 * MIN, HOUR, 6 * HOUR, DAY, WEEK, 30 * DAY, YEAR]
    tl = ["2m", "10m", "1h", "6h", "1d", "7d", "30d", "1y"]
    axs[-2].set_xticks([x / DAY for x in ticks]); axs[-2].set_xticklabels(tl)
    axs[-2].set_xlabel("period", fontsize=8, color="#52514e")
    fig.suptitle("Holes, their own rhythms: Lomb-Scargle per source (blue = hole starts, orange = 0/1 in hole)", fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=110, facecolor=fig.get_facecolor())


def main():
    t00 = time.time()
    S, absence = load_sources()
    for s in S.values(): build_grid(s)
    _G["S"] = S
    print({k: (len(v["starts"]), round(v["span"] / DAY)) for k, v in S.items()}, flush=True)
    if os.environ.get("RHY_ONLY_F"):  # Part F needs none of C/E/D; skip the 14-worker pool (Mac RAM law 9/26)
        t0 = time.time()
        DW = darkwave(S)
        print(f"[F] {DW['n_tests']} asymmetry tests, {len(DW['passing'])} pass Bonferroni, darkwave pairs {DW['darkwave_pairs']} {time.time()-t0:.0f}s", flush=True)
        json.dump(DW, open(os.path.join(HERE, "rhythms_darkwave_only.json"), "w"), indent=1, default=float); return

    # C: bursts (parallel)
    jobs = [(n, i, k) for n in S for i in range(len(SCALES)) for k in ("starts", "inhole")]
    t0 = time.time()
    with get_context("fork").Pool(NPROC) as pool:
        br = pool.map(bursts_for, jobs, chunksize=1)
    bursts = [b for r in br for b in r]
    print(f"[C] {len(bursts)} bursts {time.time()-t0:.0f}s", flush=True)

    # E: cross-source burst overlaps
    overl = []
    bs = sorted(bursts, key=lambda x: x["t0"])
    for i, x in enumerate(bs):
        for y in bs[i + 1:]:
            if y["t0"] >= x["t1"]: break
            if y["source"] == x["source"]: continue
            if abs(x["period_s"] - y["period_s"]) <= 0.1 * max(x["period_s"], y["period_s"]):
                ov0, ov1 = max(x["t0"], y["t0"]), min(x["t1"], y["t1"])
                overl.append(dict(a=f"{x['source']}/{x['series']}/{x['scale']}", b=f"{y['source']}/{y['series']}/{y['scale']}",
                                  overlap_start=iso(ov0), overlap_end=iso(ov1), period_a=x["period"], period_b=y["period"],
                                  strength_a=x["strength"], strength_b=y["strength"],
                                  same_group=S[x["source"]]["group"] == S[y["source"]]["group"],
                                  known=label_known((x["period_s"] + y["period_s"]) / 2)))
    print(f"[E] {len(overl)} overlaps", flush=True)

    # D: superposed epochs
    ep = []
    for a in S:
        for b in S:
            if a == b: continue
            r = epoch_pair(S, a, b)
            if r: ep.append(r)
    print(f"[D] {len(ep)} pairs", flush=True)
    t0 = time.time()
    DW = darkwave(S)
    print(f"[F] {DW['n_tests']} asymmetry tests, {len(DW['passing'])} pass Bonferroni, darkwave pairs {DW['darkwave_pairs']} {time.time()-t0:.0f}s", flush=True)
    if os.environ.get("RHY_ONLY_F"):
        json.dump(DW, open(os.path.join(HERE, "rhythms_darkwave_only.json"), "w"), indent=1, default=float); return

    # A + B
    A = global_spectra(S)
    shared = shared_periods(A, S)
    for sh in shared[:12]:
        sh["coherence"] = []
        srcs = sh["sources"]
        for i in range(len(srcs)):
            for j in range(i + 1, len(srcs)):
                for kind in ("starts", "inhole"):
                    c = coherence(S, srcs[i], srcs[j], sh["period_s"], kind)
                    if c: sh["coherence"].append(dict(pair=[srcs[i], srcs[j]], series=kind, **c))

    plot(A, S, shared, absence)
    out = dict(
        generated=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        method=__doc__,
        coverage={k: dict(group=v["group"], blocks=[[iso(a), iso(b)] for a, b in v["blocks"]], n_starts=int(len(v["starts"])),
                          n_holes_merged=len(v["holes"]), min_period=fmt_p(v["min_period"])) for k, v in S.items()},
        absence=absence,
        spectra={f"{k[0]}|{k[1]}|{k[2]}": {kk: vv for kk, vv in d.items() if not kk.startswith("_")} for k, d in A.items()},
        top3={n: sorted([dict(pk, series=k[2], band=k[1]) for k, d in A.items() if k[0] == n for pk in d["peaks"]],
                        key=lambda x: -x["local_ratio"])[:3] for n in S},
        shared=shared,
        bursts=sorted([{k: v for k, v in b.items() if k not in ("t0", "t1")} for b in bursts], key=lambda x: -x["strength"]),
        burst_overlaps=overl,
        darkwave_asymmetry=DW,
        epochs=sorted([{k: v for k, v in e.items() if not k.startswith("_")} for e in ep], key=lambda x: x["global_p"]),
        runtime_s=round(time.time() - t00),
    )
    json.dump(out, open(OUT_JSON, "w"), indent=1, default=float)
    print(f"done {time.time()-t00:.0f}s -> {OUT_JSON}, {OUT_PNG}")


if __name__ == "__main__":
    main()
