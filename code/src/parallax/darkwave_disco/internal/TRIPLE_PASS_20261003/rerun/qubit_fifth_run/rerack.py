"""rerack.py -- THE JUMP RUN RE-RACKED UNDER THE CRAZY HAT (Bones, by hand, 2026-10-02). No cut, no two-way sort, no verdict word. Errors are rows.
The things I filed as "ordinary" are the objects here:
  A. THE LOOK'S OWN LENGTH, read from INSIDE four ways (each from its own circuits), bit by bit, against the maker's OUTSIDE number.
  B. THE HALF I THREW AWAY: every dot's part OFF the OFF-to-ON line (across), and the spread and lopsidedness along it.
  C. THE BITS I CALLED CAN'T READ: their raw rows.
  D. THE ARROW over the order of the shots: A(k) = <x^2 x'> - <x x'^2>, x' = the shot k later (raw continuous dots, never cut).
  E. EVERY BIT'S CLOCK ACROSS THE EIGHT READS, sorted in THREES, no cut."""
import json, os, sys, warnings
import numpy as np
from scipy.optimize import curve_fit
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, 'data', 'fire', 'ibm_pittsburgh'); WS = [60, 240, 300]
med = lambda v: float(np.nanmedian(v)); q13 = lambda v: (float(np.nanpercentile(v, 25)), float(np.nanpercentile(v, 75)))


def fitGT(ws, Y):
    G = np.full(Y.shape[1], np.nan); T = G.copy()
    for b in range(Y.shape[1]):
        try:
            p, _ = curve_fit(lambda w, g, t: g * np.exp(-w / t), ws, Y[:, b], p0=[max(Y[0, b], .1) * 1.2, 250.], maxfev=2000)
            if 5 < p[1] < 5000: G[b], T[b] = p
        except Exception: pass
    return G, T


def arrow(x, k):
    x = x - x.mean(0); return (x[:-k] ** 2 * x[k:]).mean(0) - (x[:-k] * x[k:] ** 2).mean(0)


R = []
for k in range(1, 9):
    m = json.load(open(os.path.join(D, f'run{10 + k}_meta.json'))); z = np.load(os.path.join(D, f'run{10 + k}_results.npz'))
    wr = {c['pre_waits_us'][1]: c['pre_waits_realized_us'][1] for c in m['ledger']['circuits']}; L = lambda key, i: np.asarray(z[f'{key}__L{i}']).astype(complex)
    off1 = np.concatenate([L('OFF|w0', 1), L('OFF|w300', 1)]); on1 = np.concatenate([L(f'ON|w{w}', 1) for w in [0] + WS]); mid1 = np.concatenate([L(f'MID|w{w}', 1) for w in [0] + WS])
    m0 = off1.mean(0); d = on1.mean(0) - m0; u = lambda x: (x - m0) * np.conj(d) / np.abs(d) ** 2; al = lambda x: np.real(u(x)); ac = lambda x: np.imag(u(x))
    r = {'time': m['start_time'][11:19], 'sep': np.abs(d) / np.sqrt((np.abs(off1 - m0) ** 2).mean(0) / 2), 'rawsep': np.abs(d)}
    ws = [wr[w] for w in WS]; l1m = al(mid1).mean(0); r['l1mid'] = l1m
    for s, lev in (('ON', 1.0), ('MID', l1m)):
        G, T = fitGT(ws, np.array([al(L(f'{s}|w{w}', 2)).mean(0) for w in WS])); none = (al(L(f'{s}|w0', 2)) - al(L(f'{s}|w0', 1))).mean(0)
        r[f'tau_{s}'] = T; r[f'L_none_{s}'] = -T * np.log(1 + none / lev); r[f'L_fit_{s}'] = -T * np.log(G / lev); r[f'none_{s}'] = none
    for s, key in (('OFF', 'OFF|w0'), ('MID', 'MID|w0'), ('ON', 'ON|w0'), ('OFF300', 'OFF|w300'), ('MID300', 'MID|w300'), ('ON300', 'ON|w300')):
        for i in (1, 2):
            a_, c_ = al(L(key, i)), ac(L(key, i)); sk = lambda v: ((v - v.mean(0)) ** 3).mean(0) / v.std(0) ** 3
            r[f'B_{s}_{i}'] = dict(along_var=a_.var(0), along_skew=sk(a_), across_mean=c_.mean(0), across_var=c_.var(0), across_skew=sk(c_), tie=((a_ - a_.mean(0)) * (c_ - c_.mean(0))).mean(0) / (a_.std(0) * c_.std(0)))
            for kk in (1, 2, 3): r[f'D_{s}_{i}_{kk}'] = arrow(a_, kk); r[f'Dx_{s}_{i}_{kk}'] = arrow(c_, kk)
    R.append(r)
n = len(R); nb = len(R[0]['sep']); S = lambda key: np.array([r[key] for r in R])
print(f'THE JUMP RUN, RE-RACKED: ibm_pittsburgh, ALL {nb} bits, {n} reads ' + ' '.join(r['time'][:5] for r in R))

print('\n== A. THE LOOK\'S OWN LENGTH, FROM INSIDE (us). Four readings, each from its own circuits; every bit that gives a number is in (count shown).')
print('   none-ON : look, look again (no wait), start ON      none-MID: the same, start MID')
print('   fit-ON  : where the ON fading curve over 60/240/300 says look 2 started from      fit-MID: the same, MID')
names = ['L_none_ON', 'L_none_MID', 'L_fit_ON', 'L_fit_MID']
print('   read      ' + ''.join(f'{x[2:]:>22}' for x in names))
for i, r in enumerate(R): print(f"   {r['time'][:5]}     " + ''.join(f"{med(r[x]):>10.2f} ({int(np.isfinite(r[x]).sum()):>3} bits)   " for x in names))
allm = {x: np.nanmedian(S(x), 0) for x in names}
print('   each bit over its 8 reads, then across bits: middle [quarter points]')
for x in names: print(f'      {x[2:]:<9} {med(allm[x]):6.2f}  [{q13(allm[x])[0]:.2f}  {q13(allm[x])[1]:.2f}]')
print('   each reading against the other two of its kind, bit by bit (middle of the differences):')
for a_, b_ in (('L_none_ON', 'L_none_MID'), ('L_none_ON', 'L_fit_ON'), ('L_none_MID', 'L_fit_MID'), ('L_fit_ON', 'L_fit_MID')):
    dd = allm[a_] - allm[b_]; print(f'      {a_[2:]:<9} minus {b_[2:]:<9} {med(dd):+6.2f}  [{q13(dd)[0]:+.2f}  {q13(dd)[1]:+.2f}]   moving together bit to bit: {np.corrcoef(allm[a_][np.isfinite(dd)], allm[b_][np.isfinite(dd)])[0, 1]:+.2f}')
tau = np.nanmedian(S('tau_ON'), 0); o = np.argsort(tau); th = np.array_split(o[np.isfinite(tau[o])], 3)
print('   by thirds of the chip sorted on the bit\'s clock (short / middle / long clocks): clock, then the four lengths')
for t in th: print(f'      clock {med(tau[t]):5.0f} us:  ' + '  '.join(f'{x[2:]} {med(allm[x][t]):5.2f}' for x in names))
print('   OUTSIDE: the maker\'s stated length of one look on this chip was NOT read (blind path). On ibm_kingston, read live 10/1: 2.18 us.')

print('\n== B. THE HALF I THREW AWAY. Units: the OFF-to-ON separation. Middle bit over all bits and reads. look 1 -> look 2.')
print('   start, wait      along: spread        lopsided        ACROSS: mean            spread          lopsided        along-across tie')
for s in ('OFF', 'MID', 'ON', 'OFF300', 'MID300', 'ON300'):
    g = lambda f, i: med(np.array([r[f'B_{s}_{i}'][f] for r in R]))
    print(f"   {s:<8}      " + '   '.join(f"{g(f, 1):+.4f} -> {g(f, 2):+.4f}" for f in ('along_var', 'along_skew', 'across_mean', 'across_var', 'across_skew', 'tie')))

print('\n== C. THE NINE BITS I CALLED CAN\'T READ (rows): OFF-to-ON separation / cloud width at each read; raw separation; clocks')
bad = np.where((S('sep').min(0) < 3) | ~np.isfinite(S('tau_ON')).all(0) | ~np.isfinite(S('tau_MID')).all(0))[0]
for b in bad: print(f"   q{b:<4} sep/width " + ' '.join(f'{x:5.1f}' for x in S('sep')[:, b]) + '  | ON clock ' + ' '.join(('  nan' if not np.isfinite(x) else f'{x:5.0f}') for x in S('tau_ON')[:, b]) + '  | MID clock ' + ' '.join(('  nan' if not np.isfinite(x) else f'{x:5.0f}') for x in S('tau_MID')[:, b]))
print(f"   (all other bits: sep/width middle {med(S('sep')):.1f})")

print('\n== D. THE ARROW over the order of the shots (x 1e4). Along the line, then across it. Middle bit; width = spread of the 8 reads\' middles / root 8.')
print('   start,wait look     k=1                 k=2                 k=3            |  ACROSS k=1')
for s in ('OFF', 'MID', 'ON', 'OFF300', 'MID300', 'ON300'):
    for i in (1, 2):
        cell = lambda key: (lambda v: f'{np.mean(v) * 1e4:+7.2f} +-{np.std(v, ddof=1) / np.sqrt(n) * 1e4:5.2f}')(np.nanmedian(S(key), 1))
        print(f"   {s:<8} look {i}   " + '   '.join(cell(f'D_{s}_{i}_{kk}') for kk in (1, 2, 3)) + '   |  ' + cell(f'Dx_{s}_{i}_1'))

print('\n== E. EVERY BIT\'S CLOCK OVER THE EIGHT READS, SORTED IN THREES (lowest 3 reads / middle 2 / highest 3 of each bit; no cut; all bits with 8 clocks)')
T = S('tau_ON'); TM = S('tau_MID'); ok = np.isfinite(T).all(0) & np.isfinite(TM).all(0); order = np.argsort(T[:, ok], 0)
lo = np.take_along_axis(T[:, ok], order[:3], 0).mean(0); mi = np.take_along_axis(T[:, ok], order[3:5], 0).mean(0); hi = np.take_along_axis(T[:, ok], order[5:], 0).mean(0)
mlo = np.take_along_axis(TM[:, ok], order[:3], 0).mean(0); mmi = np.take_along_axis(TM[:, ok], order[3:5], 0).mean(0); mhi = np.take_along_axis(TM[:, ok], order[5:], 0).mean(0)
print(f'   {int(ok.sum())} bits.  ON (the ruler that did the sorting): low/high {med(lo / hi):.3f}   low/middle {med(lo / mi):.3f}   middle/high {med(mi / hi):.3f}')
print(f'   MID on ON\'s sorting (the other ruler):                   low/high {med(mlo / mhi):.3f}   low/middle {med(mlo / mmi):.3f}   middle/high {med(mmi / mhi):.3f}')
no = S('none_ON')[:, ok]; nlo = np.take_along_axis(no, order[:3], 0).mean(0); nmi = np.take_along_axis(no, order[3:5], 0).mean(0); nhi = np.take_along_axis(no, order[5:], 0).mean(0)
print(f'   the no-time step (ON) in the same three sets of reads:   low {med(nlo):+.4f}   middle {med(nmi):+.4f}   high {med(nhi):+.4f}')
