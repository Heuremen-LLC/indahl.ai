"""diag_pairs_posthoc.py -- DEFINED AFTER THE DATA (post-hoc, not in the plan, not scored): per Bell-pair marginal parity <(-1)^(s_k t_k)> for each circuit,
mapped to the physical qubits of its layout, beside IBM's stated readout_error and the CZ error on that pair from the record saved before the job."""
import json, sys, os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); from swaprun import *
rec = json.load(open(f'{HERE}/job_swap.json')); raw = json.load(open(f'{HERE}/raw_swap.json')); pr = json.load(open(f'{HERE}/props_swap_before_1.json'))
ro = {i: {p['name']: p['value'] for p in q} for i, q in enumerate(pr['qubits'])}
cz = {}
for g in pr['gates']:
    if g['gate'] == 'cz': cz[tuple(sorted(g['qubits']))] = {p['name']: p['value'] for p in g['parameters']}.get('gate_error')
P = select(curves()); acc = {}
for r in raw:
    i = r['pair']; lay = rec['layouts'][i]; n = sum(r['counts'].values()); par = np.zeros(NQ)
    for k, v in r['counts'].items():
        x = int(k, 2)
        for j in range(NQ): par[j] += v * (-1) ** (((x >> j) & 1) * ((x >> (j + NQ)) & 1))
    par /= n
    for j in range(NQ): acc.setdefault((lay[j], lay[j + NQ]), []).append((P[i]['cls'], par[j], float(np.cos((P[i]['a'][j] - P[i]['b'][j]) / 2) ** 2)))
print('physical pair (q_s, q_t): n circuits, mean marginal parity minus exact per-pair cos^2, stated readout_error q_s / q_t, stated CZ gate_error')
rows = []
for (a, b), v in acc.items():
    d = np.mean([p - e for c, p, e in v if c != 'ORTHO']) if any(c != 'ORTHO' for c, _, _ in v) else np.nan
    rows.append((d, a, b, len(v), ro[a].get('readout_error'), ro[b].get('readout_error'), cz.get(tuple(sorted((a, b))))))
for d, a, b, n, ea, eb, ez in sorted(rows, key=lambda x: (np.nan_to_num(x[0], nan=9))):
    print(f'  ({a:>3},{b:>3}) n {n:>2}  parity-exact {d:+.4f}  ro {ea:.4f} / {eb:.4f}  cz {ez}')
