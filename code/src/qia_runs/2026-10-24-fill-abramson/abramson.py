"""abramson.py -- the readings for the ABBA run (A1 B1 B2 A2) of Abramson's raw-IQ experiment, on ibm_kingston.
Estimator: onset.py (own code; known-good = his published Kingston numbers, known_good.py). Units: the TEN qubits.
Per qubit i and job j: onset_ij = a * present (per cycle, from the 2-state HMM on the qubit's 30-cycle symbol records).
  R1  B-A   = median_i [ ((on_B1+on_B2) - (on_A1+on_A2)) / 2 / cz_i ]    in % onset per CZ per cycle (his published 0.09 %/CZ). ABBA cancels LINEAR drift.
  R2  DRIFT = median_i [ (on_A2 - on_A1) / cz_i ]                         same units; positive = onset rose over the run.
Shot-noise null (both readings, same draws): pool the four jobs' symbol records for the qubit, shuffle whole shot-records, split into four equal
groups, refit, recompute R1 and R2 (B perms). h = t(B-1,.975) * sd(null draws).
RESOLVABILITY SCALE S = 0.09 % per CZ (his published per-CZ figure), fixed before any data of ours: a bound narrower than S can exclude his effect.
Outcomes (four): ABOVE  s - guard > h   BELOW  s + guard < -h   CONSISTENT  inside, and h + guard <= S   CANNOT_TELL  inside, h + guard > S, or fewer than 8 of 10
qubits 'present' in any job (censored near the floor).  guard: R1 only = (|R2| + h2)/2 (upper bound on the bias any single step between jobs can put on B-A under ABBA); R2 guard 0."""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from onset import fit_cloud, classify, fit_hmm, onset as onset_of
from scipy import stats
S_SCALE = 0.09        # % per CZ
LABELS = ('A1', 'B1', 'B2', 'A2'); NQ = 10; CYC = 30
def to_symbols(R0, R1, arm):
    pts = np.asarray(arm).reshape(len(arm), CYC, NQ); out = []
    for i in range(NQ): out.append(classify(pts[:, :, i], fit_cloud(R0[:, i]), fit_cloud(R1[:, i])))
    return out                                    # list over qubits of (shots, CYC) int8
def job_fit(sym_q): f = fit_hmm(sym_q); return onset_of(f), f['present']
def stats_from(on, cz):
    """on: array (4 jobs, 10 qubits) in LABELS order. returns R1, R2 in % per CZ."""
    on = np.asarray(on) * 100.0; cz = np.asarray(cz, float)
    r1 = np.median(((on[1] + on[2]) - (on[0] + on[3])) / 2 / cz); r2 = np.median((on[3] - on[0]) / cz)
    return float(r1), float(r2)
def perm_draw(sym, cz, rng):
    on = np.zeros((4, NQ))
    for i in range(NQ):
        pool = np.concatenate([sym[j][i] for j in range(4)]); pool = pool[rng.permutation(len(pool))]; m = len(pool) // 4
        for j in range(4): on[j, i] = job_fit(pool[j * m:(j + 1) * m])[0]
    return stats_from(on, cz)
def _perm_worker(args): sym, cz, seed = args; return perm_draw(sym, cz, np.random.default_rng(seed))
def outcome(s, h, guard=0.0, censored=False):
    if censored: return 'CANNOT_TELL'
    if s - guard > h: return 'ABOVE'
    if s + guard < -h: return 'BELOW'
    return 'CONSISTENT' if h + guard <= S_SCALE else 'CANNOT_TELL'
def readings(sym, cz, B=40, seed=0, pool=None):
    """sym: dict label -> list over qubits of (shots, 30) symbol arrays. cz: CZs per cycle per qubit (arm B)."""
    syml = [sym[l] for l in LABELS]
    fits = [[job_fit(syml[j][i]) for i in range(NQ)] for j in range(4)]
    on = np.array([[f[0] for f in row] for row in fits]); npres = [sum(f[1] for f in row) for row in fits]
    r1, r2 = stats_from(on, cz)
    args = [(syml, cz, seed * 100003 + k) for k in range(B)]
    draws = np.array(pool.map(_perm_worker, args) if pool else [_perm_worker(a) for a in args])
    t = stats.t.ppf(0.975, B - 1); h1, h2 = t * draws[:, 0].std(ddof=1), t * draws[:, 1].std(ddof=1)
    cens = min(npres) < 8; guard = (abs(r2) + h2) / 2        # upper bound on the bias one step can put on B-A: (|R2| + its shot half-width)/2 (synth defect found 24 Oct: |R2|/2 alone ignored R2's own noise)
    return dict(R1=r1, R2=r2, h1=float(h1), h2=float(h2), guard=float(guard), present=npres, onset_pct=(on * 100).round(4).tolist(),
                R1_outcome=outcome(r1, h1, guard, cens), R2_outcome=outcome(r2, h2, 0.0, cens),
                R1_raw_outcome=outcome(r1, h1, 0.0, cens))
