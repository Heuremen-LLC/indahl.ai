"""pds.py -- OUR rebuild (Wayfinder and Bones, 24 Oct 2026) of the N=3 label-variance readout of arXiv 2608.04486v3 Sec. XI E.
Written from the paper's construction and the released generator's stated recipe (read as text, never run):
sd-IBM Fock basis at N bosons, modes (s, d-2..d+2), ordering ns = N..0 then d occupations in reverse-lexicographic order;
M = 0 block; first-order critical H = sum_mu P2mu^dag P2mu, P2mu^dag = beta0 s^dag d_mu^dag + sqrt(7/2) (d^dag d^dag)^(2)_mu,
beta0 = sqrt(2) (Leviatan PRL 98 242502 Eq. 7); C2[SU(3)] = 2 Q.Q + (3/4) L.L, Q_q = s^dag dt_q + d_q^dag s - (sqrt7/2)(d^dag dt)^(2)_q.
Degenerate eigenspaces re-diagonalised by L.L, then C2, then n_d (released recipe). Dense encoding: the d-dim block padded to 2^nq.
CG coefficients from sympy (independent of the authors' Racah code)."""
import math, itertools
import numpy as np
from sympy.physics.quantum.cg import CG
from sympy import S
DM = [-2, -1, 0, 1, 2]
def cg(j1, m1, j2, m2, J, M):
    if m1 + m2 != M or abs(m1) > j1 or abs(m2) > j2 or abs(M) > J or not abs(j1 - j2) <= J <= j1 + j2: return 0.0
    return float(CG(S(j1), S(m1), S(j2), S(m2), S(J), S(M)).doit())
def comps(n, k):
    if k == 1: yield (n,); return
    for a in range(n, -1, -1):
        for r in comps(n - a, k - 1): yield (a,) + r
def basis(N):
    st = [(ns,) + c for ns in range(N, -1, -1) for c in comps(N - ns, 5)]
    return st, {s: i for i, s in enumerate(st)}
def mi(m): return 0 if m == 's' else m + 3
def hop(st, ix, i, j):
    A = np.zeros((len(st), len(st)))
    for c, s in enumerate(st):
        if s[j] == 0: continue
        if i == j: A[c, c] += s[j]; continue
        l = list(s); a = math.sqrt(l[j]); l[j] -= 1; a *= math.sqrt(l[i] + 1); l[i] += 1; A[ix[tuple(l)], c] += a
    return A
def dd(st, ix, k, q):
    A = 0
    for m1 in DM:
        m2 = q - m1
        if -2 <= m2 <= 2:
            c = cg(2, m1, 2, m2, k, q)
            if c: A = A + c * (-1) ** m2 * hop(st, ix, mi(m1), mi(-m2))
    return A
def ops(N):
    st, ix = basis(N)
    L = {q: math.sqrt(10) * dd(st, ix, 1, q) for q in (-1, 0, 1)}
    L2 = sum((-1) ** q * L[q] @ L[-q] for q in (-1, 0, 1))
    Q = {q: (-1) ** q * hop(st, ix, 0, mi(-q)) + hop(st, ix, mi(q), 0) - math.sqrt(7) / 2 * dd(st, ix, 2, q) for q in range(-2, 3)}
    C2 = 2 * sum((-1) ** q * Q[q] @ Q[-q] for q in range(-2, 3)) + 0.75 * L2
    nd = sum(hop(st, ix, mi(m), mi(m)) for m in DM)
    return st, ix, L2, C2, nd
def H_first(N, beta0=math.sqrt(2)):
    st, ix = basis(N); st2, _ = basis(N - 2); H = np.zeros((len(st), len(st)))
    def add2(s, i, j):
        l = list(s); a = math.sqrt(l[j] + 1); l[j] += 1; a *= math.sqrt(l[i] + 1); l[i] += 1; return ix[tuple(l)], a
    for mu in range(-2, 3):
        P = np.zeros((len(st), len(st2)))
        for c, s in enumerate(st2):
            r, a = add2(s, 0, mi(mu)); P[r, c] += beta0 * a
            for m1 in DM:
                m2 = mu - m1
                if -2 <= m2 <= 2:
                    g = cg(2, m1, 2, m2, 2, mu)
                    if g: r, a = add2(s, mi(m1), mi(m2)); P[r, c] += math.sqrt(3.5) * g * a
        H += P @ P.T
    return H
def block(N=3):
    """returns nq, C2 embedded (2^nq square), eigenvectors V (d x d), label variances lv, energies e"""
    st, ix, L2, C2, nd = ops(N)
    M = np.array([sum(m * n for m, n in zip(DM, s[1:])) for s in st]); m0 = np.where(M == 0)[0]; b = np.ix_(m0, m0)
    H = H_first(N)[b]; C = C2[b]; L = L2[b]; n = nd[b]; H = (H + H.T) / 2; C = (C + C.T) / 2
    e, V = np.linalg.eigh(H); i = 0
    while i < len(e):
        j = i
        while j + 1 < len(e) and e[j + 1] - e[i] < 1e-7: j += 1
        if j > i:
            sub = V[:, i:j + 1]
            for op in (L, C, n): _, u = np.linalg.eigh(sub.T @ op @ sub); sub = sub @ u
            V[:, i:j + 1] = sub
        i = j + 1
    d = len(e); lv = np.array([V[:, k] @ C @ C @ V[:, k] - (V[:, k] @ C @ V[:, k]) ** 2 for k in range(d)])
    nq = int(np.ceil(np.log2(d))); Ce = np.zeros((2 ** nq, 2 ** nq)); Ce[:d, :d] = C
    return nq, Ce, V, lv, e, [st[k] for k in m0]
def exemplars(N=3):
    nq, Ce, V, lv, e, b = block(N); d = V.shape[0]
    solv = [k for k in range(d) if lv[k] < 1e-6][:3]; mixed = [k for k in range(d) if lv[k] >= 1e-6][:2]
    out = {}
    for k in solv + mixed:
        w = np.zeros(2 ** nq); w[:d] = V[:, k]; w /= np.linalg.norm(w)
        out[k] = dict(w=w, kind='solvable' if lv[k] < 1e-6 else 'mixed', lv=float(lv[k]), C2=float(w @ Ce @ w), C2sq=float(w @ Ce @ Ce @ w))
    return nq, Ce, out
