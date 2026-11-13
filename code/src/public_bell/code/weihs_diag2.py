"""Diagnostic: is the 'other side next/previous setting' effect just coincidence partners?
Remove every detection that has a far-side detection within +-50 ns of the coincidence peak, then redo."""
import numpy as np, weihs_tables as w, bellsort as bs, glob, re, os, json
names = ['longdist%d' % k for k in [0,1,2,3,4,5,10,11,12,13,20,22,23,30,31,32,33,34,35,36,37]]
T = {}
for n in names:
    tA, a, x = w.load('Alice', 'longdist', n); tB, b, y = w.load('Bob', 'longdist', n)
    peak, _, _ = w.find_peak(tA, tB)
    def near(t1, t2, off):
        j = np.searchsorted(t2, t1 + off)
        d1 = np.abs(t2[np.clip(j, 0, t2.size - 1)] - t1 - off); d0 = np.abs(t2[np.clip(j - 1, 0, t2.size - 1)] - t1 - off)
        return np.minimum(d0, d1) < 50e-9
    keepA = ~near(tA, tB, peak); keepB = ~near(tB, tA, -peak)
    for side, t, s, xx, to, so, off, keep, keepo in (('A', tA, a, x, tB, b, peak, keepA, keepB), ('B', tB, b, y, tA, a, -peak, keepB, keepA)):
        t0 = t[0]; i = np.where(keep)[0]; i = i[(i > 0) & (i < t.size - 1)]
        blk = ((t[i] - t0) / 1.0).astype(int)
        tt = t[i] + off
        # other side, restricted to its own non-partner detections
        to2, so2 = to[keepo], so[keepo]
        j = np.searchsorted(to2, tt); ok = (j >= 1) & (j < to2.size)
        ii, jn, jp, bb = i[ok], j[ok], j[ok] - 1, blk[ok]
        gn = w.gbin(to2[jn] - tt[ok]); gp = w.gbin(tt[ok] - to2[jp])
        for tag, k, g in (('later', so2[jn], gn), ('earlier', so2[jp], gp)):
            name = f'{tag}|{side}out~other_set_nonpartners'
            s_ = (bb * 14 + s[ii] * 7 + g)
            key = (n, name)
            T.setdefault(name, []).append((s_, k, xx[ii]))
res = {}
for name, parts in T.items():
    off = 0; S_all = []; K_all = []; E_all = []
    for s_, k, e in parts:
        S_all.append(s_ + off); off += s_.max() + 1; K_all.append(k); E_all.append(e)
    s_ = np.concatenate(S_all); k = np.concatenate(K_all); e = np.concatenate(E_all)
    Tb = np.bincount((s_ * 2 + k) * 2 + e, minlength=off * 4).reshape(off, 2, 2)
    r, _ = bs.test_table(Tb, R=2000)
    rs = bs.rate_split(Tb, 1)
    print(name, 'N', r['N'], 'G %.1f df %d p_an %.3g p_shuf %.4f z %+.2f  adj diff %+.2e' % (r['G'], r['df'], r['p_analytic'], r['p_shuffle'], r['z_vs_shuffle'], rs['adj_diff']))
    res[name] = dict(r, adj_diff=rs['adj_diff'])
json.dump(res, open('../results/weihs_nonpartner_diag.json', 'w'), indent=1, default=float)
