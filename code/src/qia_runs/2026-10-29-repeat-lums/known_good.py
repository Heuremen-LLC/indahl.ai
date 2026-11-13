"""known_good.py -- KNOWN-GOOD: the author's published drift-control numbers recomputed from HIS released counts through OUR committed
lums.py (CVaR and shift), all four sizes. Pass rule: every stored per-row CVaR (first job and repeat) and every stored shift reproduced
to 1e-9. Context (not a pass rule): our CM/RS/TOT statistics on his own two-job pair (J = 2) against our parametric null."""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lums
rng = np.random.default_rng(20261024); ok = True
for n in (6, 8, 10, 12):
    d = lums.theirs(n); cv = lums.Cvar(lums.energies(d)); L = {j['tag']: j for j in d['ledger']['log']}
    a, b = L['bps1'], L['drift_repeat']; Pa = lums.counts_to_P(a['counts'], n); Pb = lums.counts_to_P(b['counts'], n)
    ca, cb = cv(Pa / Pa.sum(1, keepdims=True)), cv(Pb / Pb.sum(1, keepdims=True))
    e1 = np.abs(ca - np.array(d['drift']['first'])).max(); e2 = np.abs(cb - np.array(d['drift']['repeat'])).max(); sh = float((cb - ca).mean())
    p = e1 < 1e-9 and e2 < 1e-9 and abs(sh - d['drift']['shift']) < 1e-9; ok &= p
    N = np.stack([Pa, Pb]).astype(int); o, nul, _ = lums.read_arm(N, a['shots'], cv, rng, B=300)
    cm = lums.outcome_var(o, nul, 'CM', 99); tot = lums.outcome_var(o, nul, 'TOT', 99)
    print(f'n={n:2d} rows {a["rows"]:2d} shots {a["shots"]}: max|CVaR ours-stored| first {e1:.1e} repeat {e2:.1e}; shift ours {sh:+.5f} stored {d["drift"]["shift"]:+.5f} -> {"PASS" if p else "FAIL"}'
          f' | context on his pair: CM obs {o["CM"]:.2e} null median {cm[1]:.2e} 99% [{cm[2]:.2e},{cm[3]:.2e}] -> {cm[0]}; TOT -> {tot[0]}')
print('KNOWN-GOOD', 'PASS' if ok else 'FAIL')
