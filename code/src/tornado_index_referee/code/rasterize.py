"""Referee: band/sign per point-day from the IEM outlook shapefiles. variant 'c13' = CYCLE 13 (desk reading), 'a1300' = latest product with ISSUE 1300 any cycle, falling back to c13."""
import numpy as np, sys, collections as C, pickle, os
import rshp, rgeo, rgrid
LEV = ['0.02', '0.05', '0.10', '0.15', '0.30', '0.45', '0.60']
OUT = '/Users/heuremen/bones-forge/tornado_index_referee/out/cache/'
os.makedirs(OUT, exist_ok=True)
def run(ox=0.0, oy=0.0, tag='grid0'):
    X, Y, lon, lat, st = rgrid.build(ox, oy)
    res = {'c13': {}, 'a1300': {}}; odd = {'c13': C.Counter(), 'a1300': C.Counter()}; prod = {'c13': {}, 'a1300': {}}
    for y in range(2007, 2027):
        f, a, g = rshp.read(rgrid.D + 'outlooks/day1_%d.zip' % y)
        sel = {'c13': C.defaultdict(list), 'a1300': C.defaultdict(list)}
        # product choice per day
        pr13 = {}; pr1300 = {}
        for i, x in enumerate(a):
            d = x['ISSUE'][:8]
            if not d.startswith(str(y)): continue
            if x['CYCLE'] == '13': pr13.setdefault(d, set()).add(x['PRODISS'])
            if x['ISSUE'][8:] == '1300' and x['DAY'] == '1' and x['TYPE'] == 'C': pr1300.setdefault(d, set()).add(x['PRODISS'])
        pick13 = {d: max(v) for d, v in pr13.items()}
        pick1300 = {d: max(v) for d, v in pr1300.items()}
        for d in pr13: pick1300.setdefault(d, pick13[d])
        for i, x in enumerate(a):
            d = x['ISSUE'][:8]
            if not d.startswith(str(y)): continue
            if x['CATEGORY'] != 'TORNADO': continue
            th = x['THRESHOLD']
            for var, pk, ok in (('c13', pick13, x['CYCLE'] == '13'), ('a1300', pick1300, True)):
                if d in pk and x['PRODISS'] == pk[d] and (ok):
                    if var == 'a1300' and not (x['ISSUE'][8:] == '1300' or (d in pick13 and pick13[d] == pk[d] and x['CYCLE'] == '13')): continue
                    if th != 'SIGN' and th not in LEV: odd[var][th] += 1; continue
                    sel[var][d].append((th, g[i]))
        for var, pk in (('c13', pick13), ('a1300', pick1300)):
            prod[var].update(pk)
            for d in pk:
                b = np.zeros(len(X), np.int8); s = np.zeros(len(X), bool)
                for th, rings in sorted(sel[var][d], key=lambda t: (t[0] == 'SIGN', t[0])):
                    m = rgeo.inside_even_odd(lon, lat, rings)
                    if th == 'SIGN': s |= m
                    else: b[m] = np.maximum(b[m], LEV.index(th) + 1)
                res[var][d] = (b, s)
        print(y, len(pick13), len(pick1300), file=sys.stderr, flush=True)
    pickle.dump(dict(grid=(X, Y, lon, lat, st), res=res, odd={k: dict(v) for k, v in odd.items()}, prod=prod), open(OUT + tag + '.pkl', 'wb'))
if __name__ == '__main__':
    if len(sys.argv) > 1: run(float(sys.argv[1]), float(sys.argv[2]), sys.argv[3])
    else: run()
