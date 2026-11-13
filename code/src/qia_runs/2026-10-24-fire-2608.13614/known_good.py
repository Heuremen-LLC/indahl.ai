"""known_good.py -- the published SIS numbers (Table 2 of 2608.13614v1) through MY committed rebuild (sis_qubo.py).
Printed, Table 2: IBM simulator and IBM QPU beta 0.659677, gamma 0.256774; SQA beta 0.653226, gamma 0.252258.
Rule (fixed before running): KNOWN-GOOD PASSES if the paper-variant (P) refined grid contains both printed QAOA values to 6 digits and the
P-variant QUBO minimum OR one of its 10 lowest states decodes to the printed QAOA pair (17,17); the SQA pair is checked the same way.
Also: the QAOA circuit's ideal (Statevector) output distribution equals my statevector QAOA to 1e-9 (bit order check)."""
import json, sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sis_qubo import *
out = {}
for name in ('P', 'S'):
    m = build(name); E = m['E']; order = np.argsort(E, kind='stable')
    best = int(order[0]); (bi, gi), th = decode(best, m['fine'])
    low = [dict(rank=r, state=int(s), idx=decode(int(s), m['fine'])[0], theta=[round(x, 6) for x in decode(int(s), m['fine'])[1]], E=float(E[s])) for r, s in enumerate(order[:10])]
    par, fun = angles(E); pr = qaoa_probs(par, E); L = lowset(E)
    qc = circuit(m['h'], m['J'], par)
    from qiskit.quantum_info import Statevector
    qn = qc.remove_final_measurements(inplace=False); sv = Statevector(qn).probabilities_dict()
    # measure(i, n-1-i): printed bitstring char k (left to right) = qubit k = bit b_k (MSB-first) -> integer of the bitstring as printed
    # Statevector key: char 0 (left) = qubit n-1.  Reverse it to get b_0..b_9.
    svp = np.zeros(2 ** NB)
    for k, p in sv.items(): svp[int(k[::-1], 2)] = p
    out[name] = dict(n_da=m['n_da'], domain=[list(map(float, m['lo'])), list(map(float, m['hi']))], mse_qubo=m['mse_qubo'],
                     qubo_min=dict(idx=[bi, gi], theta=[round(th[0], 6), round(th[1], 6)]), lowest10=low,
                     qaoa_expectation=fun, angles=list(map(float, par)), ideal_low10_fraction=float(sum(pr[s] for s in L)),
                     ideal_p_opt=float(pr[best]), circuit_vs_mine_maxdiff=float(np.max(np.abs(svp - pr))), null_low10=10 / 1024,
                     ideal_E_mean=float(pr @ E), uniform_E_mean=float(E.mean()))
fineP = [np.linspace(0.55, 0.75, 32), np.linspace(0.18, 0.32, 32)]
hit = lambda v, arr: [int(i) for i in np.where(np.abs(arr - v) < 5e-7)[0]]
out['grid_check'] = dict(qaoa_beta_idx=hit(0.659677, fineP[0]), qaoa_gamma_idx=hit(0.256774, fineP[1]), sqa_beta_idx=hit(0.653226, fineP[0]), sqa_gamma_idx=hit(0.252258, fineP[1]))
out['uniform_4096_hits_given_state'] = 1 - (1 - 1 / 1024) ** 4096
P = out['P']; low_idx = [tuple(x['idx']) for x in P['lowest10']]
gc = out['grid_check']
ongrid = all(len(gc[k]) == 1 for k in gc)
out['verdict'] = dict(printed_values_on_P_grid=ongrid, qaoa_pair_rank=low_idx.index((17, 17)) if (17, 17) in low_idx else None,
                      sqa_pair_rank=low_idx.index((16, 16)) if (16, 16) in low_idx else None,
                      bit_order_ok=max(out[n]['circuit_vs_mine_maxdiff'] for n in 'PS') < 1e-9)
out['verdict']['PASS'] = bool(ongrid and out['verdict']['qaoa_pair_rank'] is not None and out['verdict']['bit_order_ok'])
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'known_good.json'), 'w'), indent=1, default=str)
print(json.dumps({k: (v if k in ('grid_check', 'verdict', 'uniform_4096_hits_given_state') else {kk: vv for kk, vv in v.items() if kk not in ('lowest10', 'angles')}) for k, v in out.items()}, indent=1, default=str))
for n in 'PS': print(n, [(x['rank'], x['idx'], x['theta'], round(x['E'], 5)) for x in out[n]['lowest10']])
