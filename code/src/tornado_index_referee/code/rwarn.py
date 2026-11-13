#!/opt/homebrew/bin/python3
"""Referee: GPRA warning measures recounted with own segment logic. Writes out/recount_warn.json"""
import sys, os, json, time, calendar, math, bisect, collections as C
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rgeo, recount as RC
RAW = RC.RAW; OUT = RC.OUT
def ep(s): return calendar.timegm(time.strptime(s[:16], '%Y-%m-%dT%H:%M'))
def load_warn(fys):
    W = []
    for fy in fys:
        d = json.load(open(RAW + 'warnings/to_fy%d.geojson' % fy))
        for f in d['features']:
            p = f['properties']; g = f['geometry']
            polys = [g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']
            rings = [np.array(r)[:, :2] for poly in polys for r in poly]
            a = np.concatenate(rings)
            pe = ep(p['utc_polygon_end']) if p.get('utc_polygon_end') else ep(p['utc_expire'])
            W.append(dict(fy=fy, iss=ep(p['utc_issue']), exp=ep(p['utc_expire']), pend=pe, rings=rings, bb=(a[:, 0].min(), a[:, 1].min(), a[:, 0].max(), a[:, 1].max()), key=(p['wfo'], p['eventid'], p['year'], p['product_id'])))
    W.sort(key=lambda w: w['iss']); return W
def process(T, W, mode='expire', wmax=None):
    """For tornadoes T, return per-tornado (t0, pew, lead, lead0) and set of verified warning indices. mode 'expire': active iss<=t<exp; 'pend': active iss<=t<min(exp, polygon_end)."""
    iss = [w['iss'] for w in W]; per = []; ver = set()
    for (t0, t1, lo0, la0, lo1, la1, m, yr) in T:
        if t1 is None or t1 <= t0: ts = np.array([float(t0)]); fr = np.array([0.0])
        else:
            k = int((t1 - t0) // 60); ts = t0 + 60.0 * np.arange(k + 1); fr = (ts - t0) / (t1 - t0)
        lon = lo0 + fr * (lo1 - lo0); lat = la0 + fr * (la1 - la0)
        lo_i = bisect.bisect_left(iss, t0 - 95 * 60); hi_i = bisect.bisect_right(iss, ts[-1])
        lead = np.full(len(ts), -1.0)    # best (largest) lead among warned
        for i in range(lo_i, hi_i):
            w = W[i]; end = w['exp'] if mode == 'expire' else min(w['exp'], w['pend'])
            act = (ts >= w['iss']) & (ts < end)
            if not act.any(): continue
            x0, y0, x1, y1 = w['bb']; bb = act & (lon >= x0) & (lon <= x1) & (lat >= y0) & (lat <= y1)
            if not bb.any(): continue
            idx = np.nonzero(bb)[0]; h = rgeo.inside_even_odd(lon[idx], lat[idx], w['rings'])
            if h.any():
                ver.add(i); hi = idx[h]; lead[hi] = np.maximum(lead[hi], (ts[hi] - w['iss']) / 60.0)
        warned = lead >= 0
        per.append((t0, float(warned.mean()), float(np.where(warned, lead, 0.0).mean()), float(lead[0] if lead[0] > 0 else 0.0) if warned[0] else 0.0))
    return per, ver
def fy_range(fy): return calendar.timegm((fy - 1, 10, 1, 0, 0, 0)), calendar.timegm((fy, 10, 1, 0, 0, 0))
def summarize(per, W, ver, fys):
    out = {}
    for lab, fl in [('FY%d' % f, [f]) for f in fys] + [('pooled', list(fys))]:
        pd = C.defaultdict(lambda: [0.0, 0.0, 0.0, 0]); n = 0
        for (t0, pew, lead, l0) in per:
            for f in fl:
                a, b = fy_range(f)
                if a <= t0 < b: x = pd[RC.dstr(t0, 12)]; x[0] += pew; x[1] += lead; x[2] += l0; x[3] += 1; n += 1
        ks = sorted(pd); N = np.array([pd[k][3] for k in ks], float)
        arr = lambda i: np.array([pd[k][i] for k in ks], float)
        wi = [i for i, w in enumerate(W) if w['fy'] in fl]
        fd = C.defaultdict(lambda: [0, 0])
        for i in wi: x = fd[RC.dstr(W[i]['iss'], 12)]; x[0] += (i not in ver); x[1] += 1
        kf = sorted(fd); fa = np.array([fd[k][0] for k in kf], float); fn = np.array([fd[k][1] for k in kf], float)
        r = lambda num, den, s: RC.boot_days(num, den, s)
        pod = arr(0).sum() / N.sum(); ld = arr(1).sum() / N.sum(); l0 = arr(2).sum() / N.sum(); far = fa.sum() / fn.sum()
        cp = r(arr(0), N, 11); cl = r(arr(1), N, 12); cf = r(fa, fn, 14)
        out[lab] = dict(tornadoes=n, warnings=len(wi), verified=sum(1 for i in wi if i in ver), unverified=int(fa.sum()), tornado_days=len(ks), warning_days=len(kf),
                        pod=dict(v=pod, lo=cp[0], hi=cp[1], out=('CONSISTENT' if cp[0] >= .72 else 'BELOW' if cp[1] < .72 else 'CANNOT_TELL')),
                        lead=dict(v=ld, lo=cl[0], hi=cl[1], out=('CONSISTENT' if cl[0] >= 13 else 'BELOW' if cl[1] < 13 else 'CANNOT_TELL')),
                        far=dict(v=far, lo=cf[0], hi=cf[1], out=('CONSISTENT' if cf[1] <= .71 else 'ABOVE' if cf[0] > .71 else 'CANNOT_TELL')), initial_lead=l0)
    return out
if __name__ == '__main__':
    T, _ = RC.load_db(); P, _ = RC.load_prelim()
    closed = list(range(2008, 2026)); W = load_warn(range(2008, 2028))
    cl = [t for t in T if t[0] < calendar.timegm((2026, 1, 1, 0, 0, 0))]
    res = {}
    for mode in ('expire', 'pend'):
        t0 = time.time(); per, ver = process(cl, W, mode); res[mode] = summarize([p for p in per], W, ver, closed); print(mode, time.time() - t0, file=sys.stderr)
        res[mode + '_dup_warnings_count'] = len(W) - len(set(w['key'] + (w['iss'], w['exp']) for w in W))
    # FY2026 (database Oct-Dec 2025, preliminary after), expire mode
    per, ver = process(cl + P, W, 'expire'); res['fy2026_prelim'] = summarize(per, W, ver, [2026])['FY2026']
    # warnings: tornadoes missing from FY2008 start (tornadoes in 2007 needed): handled since T includes 2006+.
    json.dump(res, open(OUT + 'recount_warn.json', 'w'), indent=1, default=float)
    for k in ('expire', 'pend'):
        for lab in ['pooled', 'FY2008', 'FY2013', 'FY2025']:
            v = res[k][lab]; print(k, lab, v['tornadoes'], v['warnings'], v['verified'], 'POD %.4f [%.4f,%.4f]' % (v['pod']['v'], v['pod']['lo'], v['pod']['hi']), 'lead %.2f [%.2f,%.2f]' % (v['lead']['v'], v['lead']['lo'], v['lead']['hi']), 'FAR %.4f [%.4f,%.4f]' % (v['far']['v'], v['far']['lo'], v['far']['hi']), 'init %.2f' % v['initial_lead'])
