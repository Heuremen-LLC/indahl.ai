"""Shared statistics for the later-sort analysis.

A 'sort' = a contingency table T[s, k, e]:
  s = stratum (records we condition on, e.g. current-trial settings)
  k = sort key (the LATER record, or the EARLIER record for the mirror)
  e = the earlier record being sorted (outcome, click, time-slot ...)
Statistic: stratified likelihood-ratio G = 2 sum O ln(O/Exp), Exp from margins
within each stratum. Null: shuffle the key across trials inside each stratum.
Because G only depends on the counts, a shuffle is equivalent to drawing the
table from the (multivariate) hypergeometric law with the observed margins,
which we sample exactly via chains of univariate hypergeometric draws.
"""
import numpy as np
from scipy.stats import chi2

def G_of(T):
    """T: (..., S, K, E) counts -> G summed over strata (vectorized over leading dims)."""
    T = np.asarray(T, dtype=float)
    Ns = T.sum(axis=(-1, -2), keepdims=True)
    rk = T.sum(axis=-1, keepdims=True)
    ce = T.sum(axis=-2, keepdims=True)
    with np.errstate(divide='ignore', invalid='ignore'):
        Exp = rk * ce / Ns
        term = np.where(T > 0, T * np.log(T / Exp), 0.0)
    return 2.0 * term.sum(axis=(-1, -2, -3))

def dof(T):
    T = np.asarray(T)
    d = 0
    for s in range(T.shape[0]):
        k = (T[s].sum(1) > 0).sum(); e = (T[s].sum(0) > 0).sum()
        d += max(k - 1, 0) * max(e - 1, 0)
    return d

def perm_tables(T, R, rng):
    """Sample R tables with the same per-stratum margins (exact shuffle null)."""
    T = np.asarray(T, dtype=np.int64)
    S, K, E = T.shape
    out = np.zeros((R, S, K, E), dtype=np.int64)
    for s in range(S):
        rk = T[s].sum(1)                  # key margins
        ce = T[s].sum(0)                  # outcome margins
        remaining_k = np.tile(rk, (R, 1)) # (R,K)
        for e in range(E - 1):
            n = np.full(R, ce[e], dtype=np.int64)
            left_total = remaining_k.sum(1)
            for k in range(K - 1):
                good = remaining_k[:, k]
                bad = left_total - good
                draw = np.where(n > 0, rng.hypergeometric(np.maximum(good,0), np.maximum(bad,0), np.minimum(n, good+bad)) if True else 0, 0)
                out[:, s, k, e] = draw
                n = n - draw
                left_total = bad
            out[:, s, K - 1, e] = n
            remaining_k = remaining_k - out[:, s, :, e]
        out[:, s, :, E - 1] = remaining_k
    return out

def test_table(T, R=2000, rng=None):
    rng = rng or np.random.default_rng(12345)
    T = np.asarray(T, dtype=np.int64)
    Gobs = float(G_of(T))
    df = dof(T)
    p_an = float(chi2.sf(Gobs, df)) if df > 0 else np.nan
    Gp = G_of(perm_tables(T, R, rng)) if R > 0 else np.array([np.nan])
    p_perm = (1 + np.sum(Gp >= Gobs)) / (1 + R)
    z = (Gobs - Gp.mean()) / Gp.std() if R > 1 and Gp.std() > 0 else np.nan
    return dict(G=Gobs, df=df, p_analytic=p_an, p_shuffle=float(p_perm), z_vs_shuffle=float(z),
                shuffle_mean=float(Gp.mean()), shuffle_sd=float(Gp.std()), R=R, N=int(T.sum())), Gp

def rate_split(T, e_index=1):
    """Plain-words effect: per key value, pooled over strata, fraction of trials with outcome e_index,
    and the stratum-adjusted difference (Mantel-Haenszel-style weighted mean of within-stratum differences
    between key 1 and key 0). Only for K==2."""
    T = np.asarray(T, dtype=float)
    S, K, E = T.shape
    if K != 2:
        return None
    num = 0.0; den = 0.0
    for s in range(S):
        n0 = T[s, 0].sum(); n1 = T[s, 1].sum()
        if n0 == 0 or n1 == 0:
            continue
        p0 = T[s, 0, e_index] / n0; p1 = T[s, 1, e_index] / n1
        w = n0 * n1 / (n0 + n1)
        num += w * (p1 - p0); den += w
    base = T[:, :, e_index].sum() / T.sum()
    return dict(adj_diff=num / den if den else np.nan, base_rate=base)

def mean_split(T, values):
    """For K==2 and E categories with numeric 'values', stratum-adjusted difference of means key1-key0."""
    T = np.asarray(T, dtype=float); v = np.asarray(values, dtype=float)
    S, K, E = T.shape
    num = 0.0; den = 0.0
    for s in range(S):
        n0 = T[s, 0].sum(); n1 = T[s, 1].sum()
        if n0 == 0 or n1 == 0:
            continue
        m0 = (T[s, 0] * v).sum() / n0; m1 = (T[s, 1] * v).sum() / n1
        w = n0 * n1 / (n0 + n1)
        num += w * (m1 - m0); den += w
    return num / den if den else np.nan
