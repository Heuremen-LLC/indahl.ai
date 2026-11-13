"""sis_qubo.py -- MY OWN rebuild of the SIS DA -> quadratic surrogate -> QUBO -> Ising -> QAOA(p=4) chain of arXiv 2608.13614v1
(Ahmad, Mohammadisiahroudi, Biswas, Hoffman; UMBC).  Their code is never executed; it was read as text only.
Two variants, both fixed before any job:
  P = the PAPER's stated construction (Sec. 3, Sec. 4 common settings, Sec. 4.1): S(0)=0.99875, I(0)=0.00125 (fractions), beta=0.65,
      gamma=0.25, [0,40] with 200 observation times, I(t) observed, mu_I=0.5, C = sum_i (I_data - I~)^2, domain [0.55,0.75]x[0.18,0.32],
      Mc=8 coarse grid (64 DA solves), lambda=8 for both fits, Mf=32 refined grid on the same domain, 5 bits per parameter.
      Not stated in the paper and chosen here: nudged initial state = the true initial state; RK45 rtol 1e-8 atol 1e-10.
  S = the RELEASED SCRIPT's construction (SIS_IBM_Annealer.py, first copy, read as text): N=8000, S0=7990, I0=10, 300 times on [0,40],
      mu_I=5, coarse 8x8 on [0.35,0.95]x[0.10,0.45], local box +-(0.12,0.08) around the coarse minimum, 32x32 local DA training grid,
      lambda_weight=2.0 for both fits.
Both: QAOA depth 4, angles from noiseless statevector expectation minimisation (COBYLA, rhobeg 0.5, maxiter 300, 3 starts with
numpy default_rng(seed) seeds 0,1,2, gammas U[0,2pi), betas U[0,pi)) as the released script states; circuit = H on all, per layer
rz(2 g h_i), cx-rz(2 g J_ij)-cx for every pair, rx(2 b); measure(i, n-1-i) (MSB-first), as the released construction.
"""
import numpy as np
from itertools import product, combinations
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d
from scipy.optimize import minimize

EPS = 1e-14; MF = 32; BPP = 5; D = 2; NB = D * BPP; P_DEPTH = 4; NSTART = 3; MAXIT = 300

VARIANTS = {
    'P': dict(N=1.0, S0=0.99875, I0=0.00125, nt=200, mu=0.5, lo=(0.55, 0.18), hi=(0.75, 0.32), lam=8.0, local=None),
    'S': dict(N=8000.0, S0=7990.0, I0=10.0, nt=300, mu=5.0, lo=(0.35, 0.10), hi=(0.95, 0.45), lam=2.0, local=(0.12, 0.08)),
}
BETA, GAMMA = 0.65, 0.25

def bits_of(idx):            # MSB-first, 5 bits
    return [(idx >> k) & 1 for k in range(BPP - 1, -1, -1)]

def _solve(v, beta, gamma, t, nudge=None):
    N, mu = v['N'], v['mu']
    def f(tt, y):
        S, I = y; inf = beta * S * I / N
        dI = inf - gamma * I + (mu * (float(nudge(tt)) - I) if nudge is not None else 0.0)
        return [-inf + gamma * I, dI]
    s = solve_ivp(f, (t[0], t[-1]), [v['S0'], v['I0']], t_eval=t, rtol=1e-8, atol=1e-10, method='RK45')
    if not s.success: raise RuntimeError('ode')
    return s.y.T

def build(name):
    v = VARIANTS[name]; t = np.linspace(0.0, 40.0, v['nt'])
    Itrue = _solve(v, BETA, GAMMA, t)[:, 1]; interp = interp1d(t, Itrue, kind='linear', fill_value='extrapolate', bounds_error=False)
    cost = lambda th: float(np.sum((Itrue - _solve(v, th[0], th[1], t, interp)[:, 1]) ** 2))
    lo, hi = np.array(v['lo']), np.array(v['hi'])
    coarse = [np.linspace(lo[p], hi[p], 8) for p in range(D)]
    ct = np.array([[coarse[0][i], coarse[1][j]] for i, j in product(range(8), repeat=2)]); cc = np.array([cost(th) for th in ct])
    if v['local'] is not None:                        # released script: local box around coarse min, 32x32 DA training grid
        best = ct[int(np.argmin(cc))]; lo = np.maximum(lo, best - np.array(v['local'])); hi = np.minimum(hi, best + np.array(v['local']))
        fine = [np.linspace(lo[p], hi[p], MF) for p in range(D)]
        tt = np.array([[fine[0][i], fine[1][j]] for i, j in product(range(MF), repeat=2)]); tc = np.array([cost(th) for th in tt]); n_da = 64 + 1024
    else:
        fine = [np.linspace(lo[p], hi[p], MF) for p in range(D)]; tt, tc = ct, cc; n_da = 64
    qf = lambda th: np.array([1.0, th[0], th[1], th[0] * th[0], th[0] * th[1], th[1] * th[1]])
    X = np.vstack([qf(th) for th in tt]); cs = (tc - tc.min()) / (tc.max() - tc.min() + EPS); w = np.exp(-v['lam'] * cs)
    coef = np.linalg.lstsq(X * np.sqrt(w)[:, None], cs * np.sqrt(w), rcond=None)[0]
    idx = list(product(range(MF), repeat=D)); bits = np.array([bits_of(i) + bits_of(j) for i, j in idx])
    ints = np.array([int(''.join(map(str, b)), 2) for b in bits])
    fs = np.array([qf([fine[0][i], fine[1][j]]) @ coef for i, j in idx]); fs = fs - fs.min(); fs = np.clip(fs / (fs.max() + EPS), 0, 1)
    pairs = list(combinations(range(NB), 2))
    Phi = np.array([[1.0] + list(b.astype(float)) + [float(b[i] * b[j]) for i, j in pairs] for b in bits])
    wq = np.sqrt(np.exp(-v['lam'] * fs)); raw = np.linalg.lstsq(Phi * wq[:, None], fs * wq, rcond=None)[0]
    er = Phi @ raw; rmin, rr = er.min(), er.max() - er.min() + EPS
    E = np.zeros(2 ** NB); E[ints] = np.clip((er - rmin) / rr, 0, None)
    q = raw / rr; q[0] = (raw[0] - rmin) / rr
    mse = float(np.mean((np.clip((er - rmin) / rr, 0, None) - fs) ** 2))
    # Ising (b = (1 - Z)/2)
    lin = q[1:1 + NB]; quad = q[1 + NB:]; h = -lin / 2.0; J = {}
    for c, (i, j) in zip(quad, pairs): h[i] -= c / 4.0; h[j] -= c / 4.0; J[(i, j)] = c / 4.0
    return dict(name=name, E=E, fine=fine, h=h, J=J, mse_qubo=mse, n_da=n_da, lo=lo, hi=hi, coarse_cost=cc, true_I=Itrue)

def decode(state_int, fine):
    b = format(state_int, '0%db' % NB); i, j = int(b[:BPP], 2), int(b[BPP:], 2)
    return (i, j), (float(fine[0][i]), float(fine[1][j]))

def _mixer(psi, beta):       # exp(-i beta X) on every qubit (symmetric, so the index convention does not matter)
    c, s = np.cos(beta), -1j * np.sin(beta); psi = psi.reshape([2] * NB)
    for ax in range(NB):
        a0 = np.take(psi, 0, axis=ax); a1 = np.take(psi, 1, axis=ax)
        psi = np.stack([c * a0 + s * a1, s * a0 + c * a1], axis=ax)
    return psi.reshape(-1)

def qaoa_probs(params, E):   # index = MSB-first basis integer of bits b0..b9
    psi = np.ones(2 ** NB, complex) / np.sqrt(2 ** NB)
    for r in range(P_DEPTH): psi = _mixer(np.exp(-1j * params[r] * E) * psi, params[P_DEPTH + r])
    return np.abs(psi) ** 2

def angles(E):
    best = None
    for seed in range(NSTART):
        g = np.random.default_rng(seed); x0 = np.concatenate([g.uniform(0, 2 * np.pi, P_DEPTH), g.uniform(0, np.pi, P_DEPTH)])
        r = minimize(lambda x: float(qaoa_probs(x, E) @ E), x0, method='COBYLA', options=dict(maxiter=MAXIT, rhobeg=0.5))
        if best is None or r.fun < best.fun: best = r
    return best.x, float(best.fun)

def circuit(h, J, params):
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(NB, NB); qc.h(range(NB))
    for r in range(P_DEPTH):
        g, b = params[r], params[P_DEPTH + r]
        for i in range(NB):
            if abs(h[i]) > 1e-12: qc.rz(2 * g * h[i], i)
        for (i, j), Jij in J.items():
            if abs(Jij) > 1e-12: qc.cx(i, j); qc.rz(2 * g * Jij, j); qc.cx(i, j)
        for i in range(NB): qc.rx(2 * b, i)
    for i in range(NB): qc.measure(i, NB - 1 - i)
    return qc

def lowset(E, k=10):         # the 10 lowest-energy states of 1024 (the "lowest 1%"); null fraction = 10/1024
    return set(int(x) for x in np.argsort(E, kind='stable')[:k])
