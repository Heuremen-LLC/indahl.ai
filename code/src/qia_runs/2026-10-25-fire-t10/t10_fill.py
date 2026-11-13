"""t10_fill.py -- analysis. raw[arm][copy][delay_index] = counts dict over 4 bits (clbit i = chosen qubit i). Fit per qubit/arm/copy:
P1(t) = 0.5 + A exp(-t/T) (weighted, binomial widths; T in us, bounds 1-5000). Readings:
  THEIRS  dT = T(t10) - T(cpmg) per qubit (copy a), four outcomes vs 0; beside their +32.0 us (344.6 - 312.6).
  LAYOUT  chi2 of dT across the four qubits (dof 3): ABOVE if p < 0.05 (the T10 margin depends on the qubit), else CONSISTENT (a bound).
  RANK    on how many of the four qubits T10 > CPMG > free holds with both gaps resolved (descriptive).
  DRIFT   T(t10) job B - copy a, per qubit, four outcomes.
  KNOWN-GOOD copies a and b of T10 on every qubit agree within 2.58 sd (identical circuits, one job)."""
import numpy as np
from scipy.optimize import curve_fit
from scipy import stats
from t10 import DELAYS_US
t = np.array(DELAYS_US, float)
def p1(c, i):
    n = sum(c.values()); k = sum(v for b, v in c.items() if b[::-1][i] == '1'); return k / n, n
def fitT(ps, ns):
    ps = np.array(ps); s = np.sqrt(np.clip(ps * (1 - ps), 1e-4, None) / np.array(ns))
    f = lambda x, A, T: 0.5 + A * np.exp(-x / T)
    try:
        (A, T), cov = curve_fit(f, t, ps, p0=[0.45, 200], sigma=s, absolute_sigma=True, bounds=([0, 1], [0.6, 5000]), maxfev=20000)
        return float(T), float(np.sqrt(cov[1, 1]))
    except Exception: return float('nan'), float('nan')
def cmp(a, b):
    d = a[0] - b[0]; s = float(np.hypot(a[1], b[1])); return dict(diff=d, sd=s, z=d / s if s else None, outcome='CANNOT_TELL' if not np.isfinite(s) else 'ABOVE' if d - 1.96 * s > 0 else 'BELOW' if d + 1.96 * s < 0 else 'CONSISTENT')
def analyse(raw, nq=4):
    T = {}
    for arm, copies in raw.items():
        for cp, cs in copies.items():
            for i in range(nq):
                ps, ns = zip(*[p1(c, i) for c in cs]); T[(arm, cp, i)] = fitT(ps, ns)
    out = {'T': {f'{a}|{c}|q{i}': v for (a, c, i), v in T.items()}}
    kg = [cmp(T[('t10', 'a', i)], T[('t10', 'b', i)]) for i in range(nq)]
    out['KNOWN_GOOD'] = dict(rule='T10 copies a and b agree within 2.58 sd on every qubit', copies=kg, passed=bool(all(k['z'] is not None and abs(k['z']) < 2.58 for k in kg)))
    dT = [cmp(T[('t10', 'a', i)], T[('cpmg', 'a', i)]) for i in range(nq)]; out['THEIRS'] = dict(per_qubit=dT, their_dT=32.0)
    d = np.array([x['diff'] for x in dT]); s = np.array([x['sd'] for x in dT]); w = 1 / s ** 2; m = (w * d).sum() / w.sum(); c2 = float((w * (d - m) ** 2).sum()); pv = float(stats.chi2.sf(c2, nq - 1))
    out['LAYOUT'] = dict(dT=[float(x) for x in d], weighted_mean=float(m), chi2=c2, p=pv, outcome='ABOVE (T10 margin depends on the qubit)' if pv < 0.05 else 'CONSISTENT (a bound)')
    se = float(np.sqrt(1 / w.sum())); out['POOLED'] = dict(dT=float(m), se=se, outcome='ABOVE' if m - 1.96 * se > 0 else 'BELOW' if m + 1.96 * se < 0 else 'CONSISTENT', their_dT=32.0, vs_theirs=cmp((float(m), se), (32.0, 0.0))['outcome'], note='read only if LAYOUT is CONSISTENT')
    out['RANK'] = sum(1 for i in range(nq) if cmp(T[('t10', 'a', i)], T[('cpmg', 'a', i)])['outcome'] == 'ABOVE' and cmp(T[('cpmg', 'a', i)], T[('free', 'a', i)])['outcome'] == 'ABOVE')
    if 'jobB' in raw.get('t10', {}): out['DRIFT'] = [cmp(T[('t10', 'jobB', i)], T[('t10', 'a', i)]) for i in range(nq)]
    if not out['KNOWN_GOOD']['passed']: out['VERDICT'] = 'NOT DECIDED: known-good failed'
    return out
