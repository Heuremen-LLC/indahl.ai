"""onset.py -- our own persistent-state estimator for raw-IQ readout records (kerneled IQ, shots x (cycles*qubits) complex).
Built from the paper's description (a hidden state entered with probability a per cycle, left with probability b, lifetime tau=-T/ln(1-b),
reads 1 with probability u1 inside it; reference R0/R1 clouds define the symbols; EM fit per qubit per arm) and its method note. Own code; his
code is never run. Symbols: 0 / 1 by the likelier reference cloud, 2 = outside both (Mahalanobis > 4 from both)."""
import numpy as np
TRIM, OUTSIDE, MAX_EXIT, MIN_DBIC, MIN_CONTRAST = 3.0, 4.0, 0.5, 10.0, 0.25
def xy(z): z = np.asarray(z); return np.stack([z.real, z.imag], -1).astype(float)
class Cloud:
    def __init__(s, mean, cov): s.mean, s.cov, s.inv, s.logdet = mean, cov, np.linalg.inv(cov), np.log(np.linalg.det(cov))
    def d2(s, x): d = x - s.mean; return np.einsum('...i,ij,...j->...', d, s.inv, d)
    def logpdf(s, x): return -0.5 * s.d2(x) - np.log(2 * np.pi) - 0.5 * s.logdet
def fit_cloud(z):
    x = xy(np.ravel(z)); r2 = TRIM ** 2
    keep = (2 - (r2 + 2) * np.exp(-r2 / 2)) / (2 * (1 - np.exp(-r2 / 2)))     # variance kept by a cut at TRIM in 2-D
    m = np.median(x, 0); sd = 1.4826 * np.median(np.abs(x - m), 0); c = Cloud(m, np.diag(sd ** 2))
    for _ in range(50):
        core = x[c.d2(x) < r2]; n = Cloud(core.mean(0), np.cov(core.T) / keep)
        if np.allclose(n.mean, c.mean) and np.allclose(n.cov, c.cov): break
        c = n
    return c
def classify(z, c0, c1):
    x = xy(z); s = (c1.logpdf(x) > c0.logpdf(x)).astype(np.int8)
    s[(c0.d2(x) > OUTSIDE ** 2) & (c1.d2(x) > OUTSIDE ** 2)] = 2
    return s
def loglik_rates(counts):
    r = counts / counts.sum(-1, keepdims=True); return float((counts * np.log(np.where(r > 0, r, 1))).sum())
def fit_hmm(seq, K=3, iters=2000, tol=1e-7):
    pat, w = np.unique(np.asarray(seq, np.int8), axis=0, return_counts=True); w = w.astype(float); S, T = pat.shape
    oh = np.eye(K)[pat].reshape(S * T, K)
    rates = (w @ oh.reshape(S, T * K)).reshape(T, K).sum(0) / (w.sum() * T)
    e = np.array([0.9 * rates + 0.1 / K, [0.2] + [0.8 / (K - 1)] * (K - 1)]); p, a, b = 0.02, 0.01, 0.2; last = -np.inf
    for it in range(iters):
        A = np.array([[1 - a, a], [b, 1 - b]]); B = e[:, pat].transpose(1, 2, 0)
        al = np.empty((S, T, 2)); c = np.empty((S, T)); x = np.array([1 - p, p]) * B[:, 0]; c[:, 0] = x.sum(1); al[:, 0] = x / c[:, :1]
        for t in range(1, T): x = (al[:, t - 1] @ A) * B[:, t]; c[:, t] = x.sum(1); al[:, t] = x / c[:, t:t + 1]
        be = np.ones((S, T, 2))
        for t in range(T - 2, -1, -1): be[:, t] = ((B[:, t + 1] * be[:, t + 1]) @ A.T) / c[:, t + 1:t + 2]
        g = al * be; g /= g.sum(2, keepdims=True); nxt = B[:, 1:] * be[:, 1:] / c[:, 1:, None]
        ll = float(w @ np.log(c).sum(1)); p = float(w @ g[:, 0, 1] / w.sum()); stay = w @ g[:, :-1].sum(1)
        a = a * float(w @ (al[:, :-1, 0] * nxt[:, :, 1]).sum(1)) / stay[0]; b = b * float(w @ (al[:, :-1, 1] * nxt[:, :, 0]).sum(1)) / stay[1]
        e = (g * w[:, None, None]).reshape(S * T, 2).T @ oh; e = np.clip(e / e.sum(1, keepdims=True), 1e-12, 1); e /= e.sum(1, keepdims=True)
        p, a = (float(np.clip(v, 1e-9, 1 - 1e-9)) for v in (p, a)); b = float(np.clip(b, 1e-9, MAX_EXIT))
        if ll - last < tol: break
        last = ll
    cnt = (w @ oh.reshape(S, T * K)).reshape(T, K); llr_one = ll - loglik_rates(cnt.sum(0))
    dbic = 2 * llr_one - (K + 2) * np.log(w.sum() * T)
    return dict(pi=p, a=a, b=b, e_N=e[0], e_P=e[1], dbic=float(dbic), present=bool(dbic > MIN_DBIC and e[1, 0] <= 1 - MIN_CONTRAST))
def lifetime_us(b, period_us): return -period_us / np.log1p(-b)
def arm_fits(R0, R1, arm, n=10):
    """per qubit: HMM fit of one job's arm. arm: shots x (cycles*n) complex; bit order cycle-major (cycle, qubit)."""
    pts = np.asarray(arm).reshape(len(arm), -1, n); out = []
    for i in range(n):
        c0, c1 = fit_cloud(R0[:, i]), fit_cloud(R1[:, i]); out.append(fit_hmm(classify(pts[:, :, i], c0, c1)))
    return out
def onset(f): return f['a'] * f['present']
