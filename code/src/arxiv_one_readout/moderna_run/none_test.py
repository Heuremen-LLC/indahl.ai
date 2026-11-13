"""none_test.py -- the baseline the papers never ran (zero IBM seconds). For random mRNA sequences sized like the papers' hardware
instances (26, 40, 50, 80 quartet variables), with the exact optimum from HiGHS: does a plain classical method find it?
  RANDOM   uniform random bitstrings, as many as the paper's hardware sampled for that size (shots x max iterations x trials)
  LOCAL    the same budget of random starts, each followed by single-bit-flip descent (a classical stand-in for 'post-processing')
Reported: share of sequences where the best found equals the exact optimum."""
import sys, numpy as np
sys.path.insert(0, '.'); import mrna_qubo as M
# the 2024 paper's hardware budgets (Table / Sec. hardware): shots x max iterations x trials
BUDGET = {26: 2 ** 8 * 104 * 8, 40: 2 ** 13 * 320 * 8, 50: 2 ** 13 * 600 * 5, 80: 20}
rng = np.random.default_rng(2024)
def find(nvar, tries=4000):
    for _ in range(tries):
        L = int(rng.integers(20, 64)); s = M.random_seq(L, rng); Q, h, J = M.build(s)
        if len(Q) == nvar: return s, h, J
    return None
for nvar in (26, 40, 50, 80):
    hits = {'RANDOM': 0, 'LOCAL': 0}; n_ok = 0; starts_cap = 20000
    for k in range(12):
        f = find(nvar)
        if f is None: continue
        s, h, J = f; Eopt, xopt, st = M.exact(h, J)
        if st != 0: continue
        n_ok += 1; B = BUDGET[nvar]
        nr = min(B, 200000); X = rng.integers(0, 2, (nr, nvar)); er = M.energies(X, h, J).min()
        hits['RANDOM'] += er <= Eopt + 1e-9
        ns = min(B, starts_cap); best = np.inf
        for _ in range(ns):
            x = M.local_search(h, J, rng.integers(0, 2, nvar) * (rng.random(nvar) < 0.2), rng); best = min(best, M.energy(x, h, J))
            if best <= Eopt + 1e-9: break
        hits['LOCAL'] += best <= Eopt + 1e-9
    print(f'{nvar} variables: {n_ok} sequences with an exact optimum | RANDOM sampling found it in {hits["RANDOM"]} | LOCAL search (<= {min(BUDGET[nvar], starts_cap)} starts) in {hits["LOCAL"]}', flush=True)
