"""callib.py: analysis for the hourly calibration (PLAN.md). Pure numpy, no IBM access, so synth.py can drive it.
Readout: P(1|0) from C0 and P(0|1) from C1 per qubit, exact (Clopper-Pearson) 99.9% interval, against IBM's prob_meas1_prep0 / prob_meas0_prep1.
T1: P1(d) at the delay grid (d = 0 is C1), model P1 = B + A exp(-d/T1) with B fixed at the measured P(1|0); weighted least squares on a log grid of
T1; 99.99% profile interval (delta chi2 <= 15.14). Against IBM's T1. Four outcomes from IBM's point of view: ABOVE (IBM's figure above our interval),
BELOW, CONSISTENT, CANNOT_TELL."""
import numpy as np
Z = 3.2905                      # two-sided 99.9%
DCHI = 15.137                  # chi2(1 dof) 99.99%: the 99.9% cut gave 3x its nominal false rate in synth (/q 16), so T1 uses 99.99%
DELAYS_US = [0, 15, 40, 80, 160, 320]
GRID = np.logspace(0, 3.5, 700)  # 1 us .. 3162 us
def wilson(k, n, z=Z):
    """Clopper-Pearson exact 99.9% interval (kept under the old name): never under-covers at small counts (/q 16, chosen before any data)."""
    from scipy.stats import beta
    k = np.asarray(k, float); n = float(n); a = 0.001
    lo = np.where(k > 0, beta.ppf(a / 2, k, n - k + 1), 0.0); hi = np.where(k < n, beta.ppf(1 - a / 2, k + 1, n - k), 1.0)
    return k / n, lo, hi
def side(stated, lo, hi):
    if stated is None or not np.isfinite(stated): return 'CANNOT_TELL'
    return 'ABOVE' if stated > hi else ('BELOW' if stated < lo else 'CONSISTENT')
def side_counts(stated, lo, hi, n_ibm=4096):
    """Note 1: IBM's readout figure is k/4096; give it its own exact 99.9% interval and call only on non-overlap."""
    if stated is None or not np.isfinite(stated): return 'CANNOT_TELL'
    k = stated * n_ibm
    if abs(k - round(k)) > 1e-6: return side(stated, lo, hi)
    _, ilo, ihi = wilson(np.array([round(k)]), n_ibm); ilo, ihi = float(ilo[0]), float(ihi[0])
    return 'ABOVE' if ilo > hi else ('BELOW' if ihi < lo else 'CONSISTENT')
MARGIN = 1.25
def side_margin(stated, lo, hi, m=MARGIN):
    """Note 1: IBM's T1 has no published fit uncertainty; call only beyond a 25% margin past our interval."""
    if stated is None or not np.isfinite(stated): return 'CANNOT_TELL'
    if lo <= stated <= hi: return 'CONSISTENT'
    return 'ABOVE' if stated > hi * m else ('BELOW' if stated < lo / m else 'CANNOT_TELL')
def t1_fit(p1, n, B):
    """p1: (Q, D) measured P(1) at DELAYS_US; n: shots per delay (D,); B: (Q,) floor. Two passes: weights from the data, then from the fitted
    model (Pearson), so a noisy low point does not get an inflated weight. Returns best, lo, hi, edge (Q,)."""
    d = np.asarray(DELAYS_US, float); p1 = np.asarray(p1, float); n = np.asarray(n, float); B = np.asarray(B, float)
    E = np.exp(-d[None, :] / GRID[:, None]); y = p1 - B[:, None]
    def prof(w):
        num = np.einsum('qd,gd,qd->qg', w, E, y); den = np.einsum('qd,gd->qg', w, E * E); A = np.clip(num / den, 0, None)
        r = y[:, None, :] - A[:, :, None] * E[None, :, :]; return np.einsum('qd,qgd->qg', w, r * r), A
    pc = np.clip(p1, 1e-3, 1 - 1e-3); chi, A = prof(n / (pc * (1 - pc)))
    i = chi.argmin(1); m = np.clip(B[:, None] + A[np.arange(len(i)), i][:, None] * E[i], 1e-3, 1 - 1e-3)
    chi, A = prof(n / (m * (1 - m)))
    i = chi.argmin(1); best = GRID[i]; ok = chi <= chi.min(1, keepdims=True) + DCHI
    lo = np.array([GRID[np.where(row)[0].min()] for row in ok]); hi = np.array([GRID[np.where(row)[0].max()] for row in ok])
    edge = (lo <= GRID[0] * 1.001) | (hi >= GRID[-1] * 0.999) | (best < 5.0)
    return best, lo, hi, edge
def ibm_readout_shots(stated):
    """Note 3 (30 Oct 2026): the shot count behind IBM's readout figures, read from the record itself. Every multiple of 1/1024 is also a multiple
    of 1/4096, so a record whose readout figures are ALL multiples of 1/1024 is a count from about 1,024 shots (ibm_fez, ibm_marrakesh: 312 of 312);
    otherwise 4,096 (ibm_aachen: 89 of 312 are multiples of 1/1024, about the quarter chance gives)."""
    v = [x for s in stated.values() for x in (s.get('p10'), s.get('p01')) if x is not None and np.isfinite(x)]
    return 1024 if v and all(abs(x * 1024 - round(x * 1024)) < 1e-6 for x in v) else 4096
def analyse(c0_ones, c1_zeros, t1_ones, shots_ro, shots_t1, stated, n_ibm=None):
    """c0_ones (Q,), c1_zeros (Q,), t1_ones (Q, D-1) ones at the nonzero delays; stated: dict q-index -> {'p10','p01','t1'} (IBM, may be None).
    Returns per-qubit rows and the run's known-good."""
    Q = len(c0_ones); p10, l10, h10 = wilson(c0_ones, shots_ro); p01, l01, h01 = wilson(c1_zeros, shots_ro)
    n_ibm = n_ibm or ibm_readout_shots(stated)
    p1 = np.column_stack([1 - p01] + [np.asarray(t1_ones)[:, j] / shots_t1 for j in range(np.asarray(t1_ones).shape[1])])
    n = np.array([shots_ro] + [shots_t1] * (p1.shape[1] - 1)); best, lo, hi, edge = t1_fit(p1, n, p10)
    rows = []
    for q in range(Q):
        s = stated[q]
        rows.append(dict(p10=round(float(p10[q]), 4), p10_ci=[round(float(l10[q]), 4), round(float(h10[q]), 4)], ibm_p10=s.get('p10'), p10_outcome=side_counts(s.get('p10'), l10[q], h10[q], n_ibm),
                         p01=round(float(p01[q]), 4), p01_ci=[round(float(l01[q]), 4), round(float(h01[q]), 4)], ibm_p01=s.get('p01'), p01_outcome=side_counts(s.get('p01'), l01[q], h01[q], n_ibm),
                         t1=round(float(best[q]), 1), t1_ci=[round(float(lo[q]), 1), round(float(hi[q]), 1)], ibm_t1=s.get('t1'),
                         t1_outcome='CANNOT_TELL' if edge[q] else side_margin(s.get('t1'), lo[q], hi[q])))
    ro_ratio = [((r['p10'] + r['p01']) / 2) / ((r['ibm_p10'] + r['ibm_p01']) / 2) for r in rows if r['ibm_p10'] and r['ibm_p01']]
    t1_ratio = [r['t1'] / r['ibm_t1'] for r in rows if r['ibm_t1'] and r['t1_outcome'] != 'CANNOT_TELL']
    mro = float(np.median(ro_ratio)) if ro_ratio else float('nan'); mt1 = float(np.median(t1_ratio)) if t1_ratio else float('nan')
    kg = bool(0.5 <= mro <= 2.0 and 0.5 <= mt1 <= 2.0)
    if not kg:
        for r in rows: r['p10_outcome'] = r['p01_outcome'] = r['t1_outcome'] = 'CANNOT_TELL'
    return rows, dict(ibm_readout_shots=n_ibm, known_good='passed' if kg else 'failed', median_readout_measured_over_stated=round(mro, 3), median_t1_measured_over_stated=round(mt1, 3))
