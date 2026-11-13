"""run_real.py -- assemble the two copies (meta_copy*.json, raw_copy*.npz) and run analyze_geopump.run at the plan's 99 % band.
R1 reference = their tau-scan job at the same tau (tau 20: dape8d318flc739m4ing, tau 60: dap8pvopqrnc739b0oi0): every key from THEIR raw bits
through OUR estimator, with its bootstrap standard deviation as the published-side width."""
import os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import geopump as G, analyze_geopump as AN
REF = {20.0: 'theirs/tau20_dape8d318flc739m4ing.npz', 60.0: 'theirs/tau60_dap8pvopqrnc739b0oi0.npz'}

def published():
    rng = np.random.default_rng(5); out = {}
    for tau, f in REF.items():
        z = np.load(f'{HERE}/{f}'); blk = {(d, b): (float(z[f'{d}_{b}_weight']), z[f'{d}_{b}_eL'], z[f'{d}_{b}_eR']) for d in ('fwd', 'rev') for b in ('plus', 'minus')}
        dr = AN.realize(AN.family_boot('A', blk, tau, rng, 2000), {}); out[tau] = {k: (float(np.mean(dr[k])), float(np.std(dr[k]))) for k in G.KEYS}
    return out

def load():
    data = []
    for copy in (1, 2):
        meta = json.load(open(f'{HERE}/meta_copy{copy}.json')); z = np.load(f'{HERE}/raw_copy{copy}.npz'); cp = {}
        for i, m in enumerate(meta):
            tau = float(m['tau']); blk = cp.setdefault(tau, {'A': {}, 'Ap': {}, 'Bp': {}}); key = (m['d'], m['b'])
            if m['fam'] == 'A': blk['A'][key] = (m['w'], z[f'eL_{i}'], z[f'eR_{i}'])
            else:
                bins = {x: np.array(m['bins'][x]) for x in 'LR'}; blk[m['fam']].setdefault(key, (m['w'], {}))[1][m['k']] = (z[f'eL_{i}'], z[f'eR_{i}'], bins)
        for tau in cp:
            for fam in ('Ap', 'Bp'):
                for key, (w, dct) in list(cp[tau][fam].items()): cp[tau][fam][key] = (w, [dct[k] for k in sorted(dct)])
        data.append(cp)
    return data

if __name__ == '__main__':
    pub = published(); print('R1 reference (their raw bits, our estimator):', json.dumps({str(t): {k: [round(v[0], 4), round(v[1], 4)] for k, v in d.items()} for t, d in pub.items()}))
    AN.run(load(), band=99.0, B=2000, seed=11, published=pub)
