"""analyze_aqcel.py -- readings for the 2509.04761 re-test (fixed before any job; PLAN_AQCEL.md.text).
Input entries: list of [label, round, counts] with label in CAL0, CAL1, Q, V1, V2, CTRL; meas[arm] = 6 physical qubits (clbit order);
union = physical qubits of the calibration circuits (clbit j <-> union[j]); p = exact ideal output of the ORIGINAL circuit.
Readout: tensored per-qubit correction from pooled CAL0/CAL1 (e0 = P(1|prep0), e1 = P(0|prep1)), inverse applied per measured bit;
the quasi-distribution keeps its sum (not renormalised after clipping); negative entries count as 0 inside the fidelity sum only. Fidelity F = (sum_k sqrt(p_k q_k))^2 (paper eq. 1) on the corrected (and on the raw) distribution.
Interval: 95 % percentile bootstrap (B resamples): arm counts multinomial at the pooled shot number, calibration counts binomial per qubit.
Drift: per-copy F (4 copies); flag when the between-copy variance exceeds the single-copy shot variance by > 5.42 (chi2_3 0.999 / 3).
PRIMARY outcome (one, in this order):
  0 drift flag on V2 or CTRL                   -> CANNOT_TELL
  1 D3 = F_V2 - F_CTRL upper < 0                -> GAP   (control beats Aqcel-v2)
  2 D3 lower <= 0                               -> CANNOT_TELL (control scores as high as Aqcel-v2)
  3 F_V2 upper < 0.985                          -> GAP   (Aqcel-v2 below its printed 0.99, rounding edge 0.985)
  4 D2 = F_V2 - F_Q lower <= 0                  -> GAP   (no advantage over Qiskit-only)
  5 D2 interval overlaps [0.52, 0.54]           -> CLEAN (their printed 0.99 - 0.46 gap reproduces with the control)
    otherwise                                   -> FILL  (advantage holds beyond the control; size differs from printed: we print it)
SECONDARY (reported, four outcomes vs printed band; CANNOT_TELL if that arm's drift flag is set):
  F_V2 vs [0.985, 0.995]; F_V1 vs [0.985, 0.995]; F_Q vs [0.455, 0.465]."""
import numpy as np

CHI2_3_999_OVER_3 = 16.266 / 3


def vec(counts, nbits=6):
    v = np.zeros(2 ** nbits)
    for k, c in counts.items():
        v[int(k.replace(' ', ''), 2)] += c
    return v


def cal_errors(entries, nunion):
    """per union-qubit e0, e1 from pooled CAL0/CAL1, plus the shot numbers"""
    n0 = n1 = 0; one0 = np.zeros(nunion); zero1 = np.zeros(nunion)
    for lab, r, cnt in entries:
        if lab not in ('CAL0', 'CAL1'):
            continue
        for k, c in cnt.items():
            k = k.replace(' ', '')
            bits = np.array([int(k[-1 - j]) for j in range(nunion)])
            if lab == 'CAL0':
                one0 += c * bits; n0 += c
            else:
                zero1 += c * (1 - bits); n1 += c
    return one0 / n0, zero1 / n1, n0, n1


def correct(raw, e0, e1):
    """raw: length-64 vector (index bit i = clbit i); e0/e1: per-clbit errors (length 6)"""
    t = raw.reshape((2,) * 6)  # C order: axis a <-> bit (5 - a)
    for i in range(6):
        M = np.array([[1 - e0[i], e1[i]], [e0[i], 1 - e1[i]]])
        t = np.moveaxis(np.tensordot(np.linalg.inv(M), t, axes=([1], [5 - i])), 0, 5 - i)
    return t.reshape(-1)  # quasi-distribution, sums to the raw total; NOT clipped or renormalised (clipping biases F down)


def fid(pv, q):
    q = np.asarray(q, float); q = q / q.sum()
    return float(np.sum(np.sqrt(pv * np.clip(q, 0, None))) ** 2)


def pvec(p):
    v = np.zeros(64)
    for k, x in p.items():
        v[int(k, 2)] = x
    return v


def band(lo, hi, blo, bhi, flag=False):
    if flag or not np.isfinite(lo):
        return 'CANNOT_TELL'
    return 'ABOVE' if lo > bhi else 'BELOW' if hi < blo else 'CONSISTENT'


def analyze(entries, meas, union, p, B=2000, seed=1):
    rng = np.random.default_rng(seed)
    pv = pvec(p)
    e0u, e1u, n0, n1 = cal_errors(entries, len(union))
    pos = {q: j for j, q in enumerate(union)}
    arms = ('Q', 'V1', 'V2', 'CTRL')
    out = {}
    boots = {}
    for a in arms:
        cop = [vec(c) for lab, r, c in entries if lab == a]
        pooled = np.sum(cop, axis=0); N = pooled.sum()
        ix = [pos[q] for q in meas[a]]
        e0, e1 = e0u[ix], e1u[ix]
        F = fid(pv, correct(pooled, e0, e1)); Fraw = fid(pv, pooled / N)
        Fc = [fid(pv, correct(c, e0, e1)) for c in cop]
        # bootstrap
        fb = np.empty(B)
        f1 = np.empty(B)  # single-copy shot spread at the copy size
        n_c = cop[0].sum()
        for b in range(B):
            eb0 = rng.binomial(n0, e0) / n0; eb1 = rng.binomial(n1, e1) / n1
            fb[b] = fid(pv, correct(rng.multinomial(int(N), pooled / N).astype(float), eb0, eb1))
            f1[b] = fid(pv, correct(rng.multinomial(int(n_c), pooled / N).astype(float), e0, e1))
        boots[a] = fb
        s2 = float(np.var(Fc, ddof=1)); sig2 = float(np.var(f1, ddof=1))
        ratio = s2 / sig2 if sig2 > 0 else np.inf
        lo, hi = np.percentile(fb, [2.5, 97.5])
        out[a] = dict(F=F, lo=float(lo), hi=float(hi), F_raw=Fraw, F_copies=Fc, drift_ratio=ratio, drift=bool(ratio > CHI2_3_999_OVER_3), shots=int(N))
    d3 = boots['V2'] - boots['CTRL']; d2 = boots['V2'] - boots['Q']
    D3 = dict(v=out['V2']['F'] - out['CTRL']['F'], lo=float(np.percentile(d3, 2.5)), hi=float(np.percentile(d3, 97.5)))
    D2 = dict(v=out['V2']['F'] - out['Q']['F'], lo=float(np.percentile(d2, 2.5)), hi=float(np.percentile(d2, 97.5)))
    if out['V2']['drift'] or out['CTRL']['drift']:
        prim, why = 'CANNOT_TELL', 'drift beyond shot noise on V2 or CTRL'
    elif D3['hi'] < 0:
        prim, why = 'GAP', 'control beats Aqcel-v2'
    elif D3['lo'] <= 0:
        prim, why = 'CANNOT_TELL', 'control scores as high as Aqcel-v2'
    elif out['V2']['hi'] < 0.985:
        prim, why = 'GAP', 'Aqcel-v2 below printed 0.99 beyond the interval'
    elif D2['lo'] <= 0:
        prim, why = 'GAP', 'no advantage of Aqcel-v2 over Qiskit-only'
    elif D2['lo'] <= 0.54 and D2['hi'] >= 0.52:
        prim, why = 'CLEAN', 'printed 0.99 - 0.46 gap reproduces, control far below'
    else:
        prim, why = 'FILL', 'advantage beyond control and Qiskit-only; size differs from printed 0.53'
    sec = dict(V2_vs_099=band(out['V2']['lo'], out['V2']['hi'], 0.985, 0.995, out['V2']['drift']),
               V1_vs_099=band(out['V1']['lo'], out['V1']['hi'], 0.985, 0.995, out['V1']['drift']),
               Q_vs_046=band(out['Q']['lo'], out['Q']['hi'], 0.455, 0.465, out['Q']['drift']))
    return dict(arms=out, D3=D3, D2=D2, primary=prim, why=why, secondary=sec, cal=dict(e0=e0u.tolist(), e1=e1u.tolist(), n0=n0, n1=n1))
