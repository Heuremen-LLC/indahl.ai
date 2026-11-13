# Which index does "middle latitudes" track? python3 -I
src = open('/Users/heuremen/bones-forge/solar_index_referee/code/recount.py').read().split('# ---------- diff vs desk')[0]
exec(src)
# planetary estimated K (SWPC DGD third block) and GFZ Kp
kpd = {}
for f in sorted(glob.glob(D + '/raw/warehouse/*_DGD.txt')) + sorted(glob.glob(D + '/raw/indices/*_DGD.txt')):
    for ln in open(f, encoding='latin-1'):
        if not re.match(r'\d{4} \d\d \d\d ', ln): continue
        n = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', ln)]
        if len(n) == 30:
            v = n[22:30]; kpd[dt.date(int(n[0]), int(n[1]), int(n[2]))] = None if min(v) < 0 else max(v)
gfz = {}
for ln in open(D + '/raw/gfz/Kp_ap_Ap_SN_F107_since_1932.txt'):
    if ln.startswith('#'): continue
    t = ln.split()
    if int(t[0]) >= 2021:
        v = [float(x) for x in t[7:15]]; gfz[dt.date(int(t[0]), int(t[1]), int(t[2]))] = None if min(v) < 0 else max(v)
def series(ev, L, fn):
    out = []
    for d, r in stated.items():
        if r['d1'] != d + dt.timedelta(1): continue
        tg = d + dt.timedelta(L)
        if r['iss'] >= dt.datetime.combine(tg, dt.time()) or tg >= SETTLED: continue
        p = pstated(r, ev, L - 1); o = fn(tg)
        if p is None or o is None: continue
        out.append((p / 100, o))
    return out
def brier(s):
    n = len(s); f = sum(o for p, o in s) / n; bs = sum((p - o)**2 for p, o in s) / n
    return n, sum(p for p, o in s) / n, f, bs, 1 - bs / (f * (1 - f))
def th(src, t, eps=0.0):
    return lambda d: (None if src.get(d) is None else int(src[d] >= t - eps))
rd = {}
print('reading                                   n   mean_stated  observed   Brier   BSS')
for ev, t in (('MID5', 5), ('MID6', 6)):
    for lab, fn in (('Fredericksburg K>=%d' % t, th(kf, t)), ('DGD est. planetary K>=%d (integer-or-third)' % t, th(kpd, t)), ('DGD est. planetary K>=%d- (%.3f)' % (t, t - 1/3), th(kpd, t, 0.34)),
                    ('GFZ Kp>=%d' % t, th(gfz, t)), ('GFZ Kp>=%d- (%.3f)' % (t, t - 1/3), th(gfz, t, 0.34)), ('College K>=%d' % t, th(kc, t))):
        s = series(ev, 1, fn); n, mp, f, bs, bss = brier(s); print('%-6s %-44s %4d  %.4f  %.4f  %.5f  %+.4f' % (ev, lab, n, mp, f, bs, bss))
        rd[(ev, lab)] = dict(n=n, mean_stated=mp, observed=f, brier=bs, bss=bss)
print()
print('HI5/HI6 against College K and planetary')
for ev, t in (('HI5', 5), ('HI6', 6)):
    for lab, fn in (('College K>=%d' % t, th(kc, t)), ('Fredericksburg K>=%d' % t, th(kf, t)), ('DGD planetary K>=%d- ' % t, th(kpd, t, 0.34)), ('GFZ Kp>=%d-' % t, th(gfz, t, 0.34))):
        s = series(ev, 1, fn); n, mp, f, bs, bss = brier(s); print('%-6s %-44s %4d  %.4f  %.4f  %.5f  %+.4f' % (ev, lab, n, mp, f, bs, bss))
# correlation of daily stated MID5 with each
import numpy as np
for ev in ('MID5','HI5'):
    xs = []; 
    for d, r in stated.items():
        tg = d + dt.timedelta(1)
        if r['d1'] != tg or tg >= SETTLED: continue
        p = pstated(r, ev, 0)
        if None in (p, kf.get(tg), kc.get(tg), gfz.get(tg), kpd.get(tg)): continue
        xs.append((p, kf[tg], kc[tg], gfz[tg], kpd[tg]))
    a = np.array(xs); print(ev, 'n', len(a), 'corr(stated p, daily max K): Fred %.3f College %.3f GFZ Kp %.3f DGD planetary %.3f' % tuple(np.corrcoef(a.T)[0, 1:]))
# 2026 DGD quarter file planetary check: what does 2026 planetary K look like
print('DGD planetary decimals present?', sum(1 for v in kpd.values() if v is not None and v != int(v)), 'of', len(kpd))
