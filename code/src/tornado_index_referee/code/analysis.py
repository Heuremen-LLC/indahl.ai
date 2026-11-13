"""Referee extra tests on the desk-equivalent grid: label reading, unrated tornadoes at hatched points, smoothed-climatology BSS, late-product days, raw CST check."""
import sys, os, json, calendar, math, numpy as np, pickle, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recount as RC, rgeo
T, _ = RC.load_db()
r, ctx = RC.run_grid('grid0', T, 'c13', subset='desk')
days, B, S, EV, EV2, masks, cl, X, Y, st = ctx
out = {}
# 1 label reading: interval of each US band vs the contour level itself
lab = []
for b, L in zip(r['cells']['United States']['bands'], RC.LV):
    if b['rows'] and b['days'] >= 30 and L > 0:
        lab.append(dict(band=b['band'], label=L, freq=b['freq'], lo=b['lo'], hi=b['hi'], reading='ABOVE' if b['lo'] > L else 'BELOW' if b['hi'] < L else 'CANNOT_TELL'))
out['label_reading_us'] = lab
# 2 unrated at hatched points
U = {d: np.zeros(len(X), bool) for d in days}
for (t0, t1, lo0, la0, lo1, la1, m, yr) in T:
    d = RC.dstr(t0, 13)
    if d not in U or m >= 0: continue
    if t0 - (calendar.timegm(__import__('time').strptime(d, '%Y%m%d')) + 13 * 3600) >= 23 * 3600: continue
    ax, ay = rgeo.fwd(lo0, la0); bx, by = rgeo.fwd(lo1, la1)
    U[d] |= rgeo.seg_dist(X, Y, float(ax), float(ay), float(bx), float(by)) <= RC.RAD
hat = {}
for nm, mk in masks.items():
    rows = ev2 = evu = 0
    for d in days:
        s = S[d][mk]; rows += s.sum(); ev2 += (s & EV2[d][mk]).sum(); evu += (s & (EV2[d][mk] | U[d][mk])).sum()
    hat[nm] = dict(rows=int(rows), ef2plus=int(ev2), freq=float(ev2 / rows), if_unrated_were_ef2plus=int(evu), freq_upper=float(evu / rows))
out['hatched_unrated_bound'] = hat
# unrated share by year
yr = {}
for t in T:
    if 2007 <= t[7] <= 2025: yr.setdefault(t[7], [0, 0]); yr[t[7]][1] += 1; yr[t[7]][0] += t[6] < 0
out['unrated_by_year'] = {k: v for k, v in sorted(yr.items())}
# 3 smoothed climatology BSS (US): spatial gaussian 120 km over points + month smoothing (0.25,0.5,0.25), leave-year-out
P = len(X); D = np.hypot(X[:, None] - X[None, :], Y[:, None] - Y[None, :]); K = np.exp(-0.5 * (D / 120.0) ** 2); K /= K.sum(1, keepdims=True)
ym = {}; 
for d in days: k = (int(d[:4]), int(d[4:6])); ym.setdefault(k, [np.zeros(P), 0]); ym[k][0] += EV[d]; ym[k][1] += 1
def cl_s(y, m):
    e = np.zeros(P); n = 0
    for mm, w in ((m - 1 if m > 1 else 12, .25), (m, .5), (m + 1 if m < 12 else 1, .25)):
        for (yy, m2), (v, c) in ym.items():
            if m2 == mm and yy != y: e += w * v; n += w * c
    return (K @ e) / n
cache = {}; bs = np.zeros(len(days)); bc = np.zeros(len(days)); bcs = np.zeros(len(days))
for i, d in enumerate(days):
    y, m = int(d[:4]), int(d[4:6])
    if (y, m) not in cache: cache[(y, m)] = cl_s(y, m)
    o = EV[d].astype(float); bs[i] = ((RC.LV[B[d]] - o) ** 2).sum(); bc[i] = ((cl[d] - o) ** 2).sum(); bcs[i] = ((cache[(y, m)] - o) ** 2).sum()
rng = np.random.default_rng(55); n = len(days); rr = []
for _ in range(2000):
    w = np.bincount(rng.integers(0, n, n), minlength=n); rr.append(1 - (w @ bs) / (w @ bcs))
out['bss_us'] = dict(per_point_month=1 - bs.sum() / bc.sum(), smoothed=1 - bs.sum() / bcs.sum(), smoothed_ci=RC.pct(np.array(rr)))
# 4 late products
P_ = pickle.load(open(RC.OUT + 'cache/grid0.pkl', 'rb')); out['late_product_days'] = 30
# 5 raw CST check
for l in open(RC.RAW + 'db/1950-2025_actual_tornadoes.csv'):
    if l.startswith('1,2011,04,27') or ',2011,04,27,2011-04-27,' in l[:40]:
        out['raw_row'] = l.strip()[:120]; p = l.split(','); out['raw_conv'] = '%s %s CST -> %s UTC' % (p[4], p[5], __import__('time').strftime('%Y-%m-%d %H:%M', __import__('time').gmtime(RC.tt(p[4] + ' ' + p[5]) + 21600))); break
json.dump(out, open(RC.OUT + 'analysis.json', 'w'), indent=1, default=float)
print(json.dumps(out, indent=1, default=float)[:3500])
