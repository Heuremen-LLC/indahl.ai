"""lums.py -- shared code for the free calibration run on arXiv 2609.13669v1 (LUMS, single author, ibm_fez). 24 Oct 2026.
Problem, energies and CVaR are rebuilt from the author's released JSON (theirs/), never by running his notebooks.
Energies: C(x) = lam x'Sx - r'x + mu (sum x - B)^2, normalised e = (C - E_offset)/E_scale (his stored offset/scale);
bit k of the integer index = asset k (his convention). CVaR_alpha (alpha 0.5) = mean energy of the lowest alpha of the mass.
Statistics for a set of jobs of one arm (J jobs x R rows of CVaR):
  CM  = variance over jobs of the job's mean deviation d_j = mean_r (c[j,r] - m_r)       (common-mode: every row moves together)
  RS  = sum of squared residuals c[j,r] - m_r - d_j                                     (row-specific)
  TOT = sum of squared deviations c[j,r] - m_r                                          (both)
Null: parametric bootstrap, every (j,r) re-drawn as multinomial(shots, pooled distribution of row r over the arm's jobs)."""
import json, os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ALPHA = 0.5
CHAINS = {8: [124, 123, 136, 143, 144, 145, 146, 147], 10: [107, 106, 105, 117, 125, 124, 123, 122, 121, 120]}

def theirs(n):
    return json.load(open(f'{HERE}/theirs/qaoa_jobs_{n}assets_ibm_fez.json'))

def energies(d):
    n = d['provenance']['n_assets']; pr = d['problem']; S = np.array(pr['covariance']); r = np.array(pr['expected_returns'])
    lam, mu, B = d['provenance']['lam'], d['provenance']['mu'], d['provenance']['budget']
    X = np.array([[(i >> k) & 1 for k in range(n)] for i in range(2 ** n)])
    C = lam * np.einsum('ij,jk,ik->i', X, S, X) - X @ r + mu * (X.sum(1) - B) ** 2
    return (C - pr['E_offset']) / pr['E_scale']

class Cvar:
    def __init__(self, e):
        self.o = np.argsort(e, kind='mergesort'); self.es = e[self.o]
    def __call__(self, P):                      # P (..., S) probabilities (rows sum to 1)
        Ps = np.take(P, self.o, axis=-1); prev = np.cumsum(Ps, axis=-1) - Ps
        w = np.minimum(Ps, np.clip(ALPHA - prev, 0, None))
        return (w @ self.es) / w.sum(axis=-1)

def counts_to_P(counts, n):
    P = np.zeros((len(counts), 2 ** n))
    for i, c in enumerate(counts):
        for k, v in c.items(): P[i, int(k)] = v
    return P

def stats(C):                                   # C (J, R)
    m = C.mean(0); dev = C - m; d = dev.mean(1); res = dev - d[:, None]
    return dict(CM=float(np.var(d, ddof=1)), RS=float((res ** 2).sum()), TOT=float((dev ** 2).sum()), dSD=float(np.std(d, ddof=1)))

def null_stats(N, shots, cv, rng, B=300):
    """N (J, R, S) integer counts of one arm. Returns list of null stats dicts."""
    J, R, S = N.shape; pooled = N.sum(0) / N.sum(0).sum(-1, keepdims=True); out = []
    for _ in range(B):
        D = rng.multinomial(shots, np.broadcast_to(pooled, (J, R, S)))
        out.append(stats(cv(D / shots)))
    return out

def outcome_var(obs, nul, key, band):
    v = np.array([x[key] for x in nul]); hi = np.percentile(v, 100 - (100 - band) / 2); lo = np.percentile(v, (100 - band) / 2)
    o = 'ABOVE' if obs[key] > hi else 'BELOW' if obs[key] < lo else 'CONSISTENT'
    return o, float(np.median(v)), float(lo), float(hi)

def excess_sd(obs, nul, key='CM'):
    """common-mode job SD beyond shot noise: point and a generous upper bound (obs minus the null 1st percentile)."""
    v = np.array([x[key] for x in nul])
    return float(np.sqrt(max(0.0, obs[key] - np.median(v)))), float(np.sqrt(max(0.0, obs[key] - np.percentile(v, 1))))

def diff_outcome(oT, nT, oO, nO, key, band, rng):
    obs = oT[key] - oO[key]; a = np.array([x[key] for x in nT]); b = np.array([x[key] for x in nO])
    dn = rng.choice(a, 2000) - rng.choice(b, 2000); hi = np.percentile(dn, 100 - (100 - band) / 2); lo = np.percentile(dn, (100 - band) / 2)
    return ('ABOVE' if obs > hi else 'BELOW' if obs < lo else 'CONSISTENT'), float(obs), float(lo), float(hi)

def read_arm(N, shots, cv, rng, B=300):
    C = cv(N / shots); o = stats(C); return o, null_stats(N, shots, cv, rng, B), C

ORDER = ['T', 'O', 'O', 'T', 'T', 'O', 'O', 'T', 'T', 'O', 'O', 'T']          # ABBA over arms; T = his settings (DD + gate and measure twirling), O = DD only
BAND = 99

def analyse(N, arms, shots, cv, rng, B=200, Bh=100):
    """N (J, R, S) counts for one size over all jobs in ORDER; arms list of 'T'/'O'.
    R1  drift      : CM of the O arm (no twirl) against the shot-noise parametric null.
    R1b T arm      : CM of the T arm against its shot-noise null (drift and/or job-level twirl instance variance).
    R2  twirl job  : var(d_T) - var(d_O), d = job mean deviation from its own arm's row means, exact permutation test over all
                     6/6 relabelings of the 12 jobs (calibrated under any drift, which is common to both arms).
    R2b twirl rows : mean row-specific residual sum, T minus O, same permutation test.
    ABOVE on R1/R1b becomes CANNOT_TELL if either half of the run (jobs 1-6, 7-12) has its statistic below its own null median."""
    from itertools import combinations
    iT = [i for i, a in enumerate(arms) if a == 'T']; iO = [i for i, a in enumerate(arms) if a == 'O']
    oT, nT, CT = read_arm(N[iT], shots, cv, rng, B); oO, nO, CO = read_arm(N[iO], shots, cv, rng, B)
    out = {}
    for name, (o, n_, idx) in {'R1_drift_O_CM': (oO, nO, iO), 'R1b_T_CM': (oT, nT, iT)}.items():
        oc, med, lo, hi = outcome_var(o, n_, 'CM', BAND); pt, ub = excess_sd(o, n_, 'CM')
        if oc == 'ABOVE':
            h = len(arms) // 2
            for part in ([i for i in idx if i < h], [i for i in idx if i >= h]):
                ho, hn, _ = read_arm(N[part], shots, cv, rng, Bh)
                if ho['CM'] < np.median([x['CM'] for x in hn]): oc = 'CANNOT_TELL'
        out[name] = dict(outcome=oc, obs=o['CM'], null_med=med, null_hi=hi, dSD=o['dSD'], excess_sd=pt, excess_sd_ub=ub)
    def jobvals(Cm):
        dev = Cm - Cm.mean(0); d = dev.mean(1); res = dev - d[:, None]; return d, (res ** 2).sum(1)
    dT, rT = jobvals(CT); dO, rO = jobvals(CO); D = np.concatenate([dT, dO]); Rr = np.concatenate([rT, rO]); J = len(D); k = len(dT)
    s_obs = (np.var(dT, ddof=1) - np.var(dO, ddof=1), rT.mean() - rO.mean()); perm = []
    for c in combinations(range(J), k):
        m = np.zeros(J, bool); m[list(c)] = True
        perm.append((np.var(D[m], ddof=1) - np.var(D[~m], ddof=1), Rr[m].mean() - Rr[~m].mean()))
    perm = np.array(perm)
    for j, name in enumerate(('R2_twirl_job_var_T_minus_O', 'R2b_twirl_rows_T_minus_O')):
        lo, hi = np.percentile(perm[:, j], [(100 - BAND) / 2, 100 - (100 - BAND) / 2])
        oc = 'ABOVE' if s_obs[j] > hi else 'BELOW' if s_obs[j] < lo else 'CONSISTENT'
        out[name] = dict(outcome=oc, obs=float(s_obs[j]), perm_lo=float(lo), perm_hi=float(hi), p_upper=float((perm[:, j] >= s_obs[j]).mean()))
    out['mean_CVaR_T'] = float(CT.mean()); out['mean_CVaR_O'] = float(CO.mean()); out['dSD_T'] = float(np.std(dT, ddof=1)); out['dSD_O'] = float(np.std(dO, ddof=1))
    return out
