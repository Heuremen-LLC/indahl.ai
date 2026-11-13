"""mrna_qubo.py -- the quartet QUBO of Alevras et al. (arXiv:2405.20328, Eq. 3) for mRNA secondary structure, built from the Turner 2004
stacking free energies (NNDB file nndb/turner_2004_watson_crick_stack_dg.txt, sha256 in nndb/SHA256.txt), and the classical baselines.
Variables: quartets q = (i, j) meaning pairs (i, j) and (i+1, j-1) are both formed and stacked (pairs AU UA CG GC GU UG; hairpin loop >= 3).
Energy (the paper's Eq. 3; its r, p, t values are not published, ours are disclosed):
  sum_q e_q q                  e_q = Turner 2004 stack of (i,j) followed by (i+1,j-1)
  + r sum_{q, q' stacked} q q'  r = 0 (a helix is the plain sum of its stacks)
  + p sum_q q (1 - q_next)      p = +0.45 kcal/mol (Turner terminal AU/GU penalty) when the inner pair of q is AU/UA/GU/UG and no quartet stacks on it
  + t sum_{q, q' conflicting} q q'   t = 1 + sum|e| (two quartets that reuse a base with a different partner, or cross: never optimal)
Exact optimum: HiGHS mixed-integer program (scipy.optimize.milp), products linearised (the role CPLEX plays in the paper)."""
import itertools, os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); PAIRS = {'AU', 'UA', 'CG', 'GC', 'GU', 'UG'}; WEAK = {'AU', 'UA', 'GU', 'UG'}
R_STACK, P_END = 0.0, 0.45

def turner():
    """{(x1, x2, y1, y2): dG} for 5'-x1 x2-3' / 3'-y1 y2-5', from the NNDB file (row = X = x2, column = Y = y2, table = first pair x1/y1)"""
    lines = [l.rstrip('\n') for l in open(os.path.join(HERE, 'nndb', 'turner_2004_watson_crick_stack_dg.txt'))]
    tab, k = {}, 0
    while k < len(lines):
        l = lines[k].strip()
        if not l.startswith('#') and len(l) == 2 and l.endswith('X') and k + 1 < len(lines) and lines[k + 1].strip().endswith('Y') and not lines[k + 1].strip().startswith('#'):
            x1 = l[0]; y1 = lines[k + 1].strip()[0]; rows = []; m = k + 2
            while len(rows) < 4 and m < len(lines):
                s = lines[m].split()
                if s and s[0] in 'ACGU' and len(s) == 5: rows.append(s)
                m += 1
            for s in rows:
                for col, v in zip('ACGU', s[1:]):
                    if v != '.': tab[(x1, s[0], y1, col)] = float(v)
            k = m
        else: k += 1
    return tab

def build(seq):
    T = turner(); n = len(seq); Q = []
    for i in range(n):
        for j in range(i + 6, n):
            if seq[i] + seq[j] in PAIRS and seq[i + 1] + seq[j - 1] in PAIRS:
                Q.append((i, j))
    e = np.array([T[(seq[i], seq[i + 1], seq[j], seq[j - 1])] for i, j in Q])
    idx = {q: a for a, q in enumerate(Q)}; m = len(Q); J = np.zeros((m, m)); h = e.copy(); t = 1 + np.abs(e).sum()
    def bases(q): i, j = q; return {i: j, j: i, i + 1: j - 1, j - 1: i + 1}
    for a, b in itertools.combinations(range(m), 2):
        qa, qb = Q[a], Q[b]
        stacked = (qb[0] == qa[0] + 1 and qb[1] == qa[1] - 1) or (qa[0] == qb[0] + 1 and qa[1] == qb[1] - 1)
        if stacked: J[a, b] += R_STACK; continue
        A, B = bases(qa), bases(qb); clash = any(k in B and B[k] != v for k, v in A.items())
        (i, j), (k, l) = qa, qb; cross = (i < k < j < l) or (k < i < l < j)
        if clash or cross: J[a, b] += t
    for a, (i, j) in enumerate(Q):
        if seq[i + 1] + seq[j - 1] in WEAK:
            nxt = idx.get((i + 1, j - 1)); h[a] += P_END
            if nxt is not None: J[min(a, nxt), max(a, nxt)] -= P_END
    return Q, h, J

def energy(x, h, J): x = np.asarray(x, float); return float(h @ x + x @ np.triu(J, 1) @ x)
def energies(X, h, J): X = np.asarray(X, float); return X @ h + np.einsum('si,ij,sj->s', X, np.triu(J, 1), X)

def exact(h, J):
    """minimum of the QUBO by HiGHS MILP: y_ab = x_a x_b linearised"""
    from scipy.optimize import milp, LinearConstraint, Bounds
    m = len(h); prs = [(a, b) for a in range(m) for b in range(a + 1, m) if J[a, b] != 0]
    nv = m + len(prs); c = np.concatenate([h, [J[a, b] for a, b in prs]]); rows, lo, hi = [], [], []
    for k, (a, b) in enumerate(prs):
        y = m + k
        for coeffs, l_, u_ in ((({y: 1, a: -1}), -np.inf, 0), (({y: 1, b: -1}), -np.inf, 0), (({y: 1, a: -1, b: -1}), -1, np.inf)):
            r = np.zeros(nv)
            for v, w in coeffs.items(): r[v] = w
            rows.append(r); lo.append(l_); hi.append(u_)
    cons = LinearConstraint(np.array(rows), lo, hi) if rows else ()
    res = milp(c, constraints=cons, integrality=np.ones(nv), bounds=Bounds(0, 1), options=dict(time_limit=120))
    x = np.round(res.x[:m]).astype(int); return energy(x, h, J), x, res.status

def local_search(h, J, x0, rng):
    """steepest single-bit-flip descent to a local minimum (the post-processing step's kind of classical search)"""
    x = np.array(x0, int); Jf = np.triu(J, 1); Js = Jf + Jf.T
    while True:
        delta = (1 - 2 * x) * (h + Js @ x)      # energy change of flipping each bit
        k = int(np.argmin(delta))
        if delta[k] >= -1e-12: return x
        x[k] ^= 1

def random_seq(n, rng): return ''.join(rng.choice(list('ACGU'), n))
