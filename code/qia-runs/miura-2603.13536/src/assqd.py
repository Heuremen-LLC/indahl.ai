"""assqd.py -- my own re-implementation (Bones/QIA, 24 Oct 2026) of the Heisenberg model, Standard SQD, Random SQD and AS-SQD of
arXiv 2603.13536v1 (Miura, Kobe City College of Technology), written from the paper text (Sec. IV-VI, Alg. 1) and the released
main.py / build_2.py READ AS TEXT ONLY (theirs/*.txt; never executed).  Protocol constants are the paper's: K = 50, B = 20, T = 10,
h = 0.5, J = 1, periodic chain; dominant threshold tau = 1e-5 and eps = 1e-6 as main.py (the code that carries the paper's
5-seed, 50/20/10 protocol); Random SQD draws its candidates from the whole of S (main.py, paper Sec. V C), AS-SQD from the
dominant support D (Alg. 1 lines 5-9).  Bit convention: qubit q <-> bit q of the integer (theirs and Qiskit's counts order).
Everything is dense-sparse linear algebra on the full 2^n matrix (n <= 12 here), which gives the same restricted matrices as their
term-by-term construction."""
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import eigsh
from scipy.linalg import eigh

K_INIT, B_ADD, T_STEPS, TAU, EPS = 50, 20, 10, 1e-5, 1e-6
FLOOR = 1e-10            # /q 24: an energy error under 1e-10 is censored at the floor (machine-precision cells are not readings)

def heis_terms(n, seed, J=1.0, h=0.5):
    """Terms in their order: for each bond (i, i+1 mod n): XX, YY, ZZ, then h_i Z_i with h_i = h * N(0,1) from default_rng(seed),
    drawn once per i in that order (main.py make_heisenberg_model and build_2.py make_heisenberg agree on this order)."""
    rng = np.random.default_rng(seed); t = []
    for i in range(n):
        j = (i + 1) % n
        t.append((J, 'XX', (i, j))); t.append((J, 'YY', (i, j))); t.append((J, 'ZZ', (i, j)))
        t.append((float(h * rng.standard_normal()), 'Z', (i,)))
    return t

def apply_term(term, ket):
    c, ops, qs = term; bra = ket; ph = 1.0 + 0j
    for op, q in zip(ops, qs):
        bit = (ket >> q) & 1
        if op == 'X': bra ^= (1 << q)
        elif op == 'Y': bra ^= (1 << q); ph *= (1j if bit == 0 else -1j)
        elif op == 'Z': ph *= (-1.0 if bit else 1.0)
    return bra, c * ph

def full_matrix(n, terms):
    dim = 1 << n; r, cidx, v = [], [], []
    for ket in range(dim):
        for tm in terms:
            b, a = apply_term(tm, ket)
            if abs(a) > 1e-15: r.append(b); cidx.append(ket); v.append(a)
    H = coo_matrix((v, (r, cidx)), shape=(dim, dim)).tocsr(); H = (H + H.getH()) * 0.5
    assert abs(H.imag).max() < 1e-12; H = H.real.tocsr(); H.eliminate_zeros(); return H

def sparse_pauli_op(n, terms):
    from qiskit.quantum_info import SparsePauliOp
    labs, cs = [], []
    for c, ops, qs in terms:
        s = ['I'] * n
        for op, q in zip(ops, qs): s[n - 1 - q] = op
        labs.append(''.join(s)); cs.append(c)
    return SparsePauliOp(labs, coeffs=np.array(cs, dtype=complex))

class Model:
    def __init__(self, n, seed):
        self.n, self.seed = n, seed; self.terms = heis_terms(n, seed); self.H = full_matrix(n, self.terms)
        self.diag = self.H.diagonal().copy(); self.Hc = self.H.tocsc()
        vals, vecs = eigsh(self.H, k=2, which='SA'); o = np.argsort(vals)
        self.E0, self.E1 = float(vals[o[0]]), float(vals[o[1]]); self.psi0, self.psi1 = vecs[:, o[0]], vecs[:, o[1]]
        self.p0 = np.abs(self.psi0) ** 2; self.p1 = np.abs(self.psi1) ** 2

def top_k(counts, k=K_INIT):
    """top-K by count; ties broken by bitstring integer (deterministic; theirs uses Python's sort order over the dict)"""
    items = sorted(counts.items(), key=lambda x: (-x[1], x[0])); return [b for b, _ in items[:k]]

def _solve(M, S):
    S = np.asarray(sorted(S)); Hs = M.H[S][:, S].toarray(); w, v = eigh(Hs); return float(w[0]), v[:, 0], S

def run(M, counts, method, rng=None, T=T_STEPS):
    """method in standard / random / en.  Returns (E, final subspace array)."""
    S = set(top_k(counts))
    if method == 'standard': E, _, Sa = _solve(M, S); return E, Sa
    for _ in range(T):
        E, c, Sa = _solve(M, S)
        if method == 'random':
            cand = np.unique(M.Hc[:, Sa].indices); cand = np.setdiff1d(cand, Sa)
            if len(cand) == 0: break
            add = rng.choice(cand, size=min(B_ADD, len(cand)), replace=False)
        else:
            dm = np.abs(c) ** 2 > TAU; D = Sa[dm]; cD = c[dm]
            cand = np.setdiff1d(np.unique(M.Hc[:, D].indices), Sa)
            if len(cand) == 0: break
            nu = M.H[cand][:, D] @ cD
            sc = nu ** 2 / np.maximum(np.abs(E - M.diag[cand]), EPS)
            add = cand[np.argsort(sc, kind='mergesort')[-min(B_ADD, len(cand)):]]
        S.update(int(a) for a in add)
    E, _, Sa = _solve(M, S); return E, Sa

def lerr(M, E): return float(np.log10(max(abs(E - M.E0), FLOOR)))

def sample(rng, p, shots):
    d = rng.multinomial(shots, p / p.sum()); return {int(i): int(x) for i, x in enumerate(d) if x > 0}

def merge(*cs):
    out = {}
    for c in cs:
        for k, v in c.items(): out[k] = out.get(k, 0) + v
    return out

def counts_from_bitstrings(cd):
    """Qiskit counts {'0101..': n} (rightmost char = qubit 0) -> {int: n}"""
    return {int(k.replace(' ', ''), 2): int(v) for k, v in cd.items()}

def resample(rng, counts):
    ks = np.array(list(counts.keys())); vs = np.array(list(counts.values()), float)
    d = rng.multinomial(int(vs.sum()), vs / vs.sum()); return {int(k): int(x) for k, x in zip(ks, d) if x > 0}
