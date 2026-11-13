"""known_good.py -- reproduce the paper's printed Mantel statistics (2508.16895v2 Sec. IV B) from the authors' RELEASED data files only
(data/081920_355r_p0.01/*.csv, results_ibm-kingston.xlsx; read as data, none of their code run).  Mantel statistic with method='spearman'
= Spearman rank correlation of the off-diagonal upper-triangle entries of the two symmetric matrices (skbio's statistic; the
permutation p-value is not recomputed).  Usage: python -I known_good.py <data dir>"""
import sys, csv, os, numpy as np
from scipy.stats import spearmanr
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); from xlsx_read import read
def load_csv(p):
    r = list(csv.reader(open(p))); hdr = [int(float(x)) for x in r[0][1:]]
    return {int(float(row[0])): {h: (float(x) if x not in ('', 'nan') else np.nan) for h, x in zip(hdr, row[1:])} for row in r[1:]}
def tri(m, ids):
    v = []
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            x = m.get(a, {}).get(b, np.nan)
            if not np.isfinite(x): x = m.get(b, {}).get(a, np.nan)
            v.append(x)
    return np.array(v)
def matrices(D):
    M = {'Correlation': load_csv(D + '/classical-correlations.csv'), 'Fidelity': load_csv(D + '/classical_fidelity.csv'),
         'Euclidean': load_csv(D + '/results_euclidean.csv')}
    for k, n in [('Ang', 'ang'), ('AngQFT', 'ang-qft'), ('Amp', 'amp'), ('AmpQFT', 'amp-qft')]: M[k] = load_csv(D + f'/results_simulator_{n}.csv')
    rows = read(D + '/results_ibm-kingston.xlsx')['Sheet1']; h = rows[0]
    for col, k in [('ang', 'Ang+IBM'), ('amp', 'Amp+IBM'), ('amp-ddd', 'Amp+DDD+IBM'), ('amp-qft', 'AmpQFT+IBM'), ('amp-qft-ddd', 'AmpQFT+DDD+IBM')]:
        j = h.index(col); m = {}
        for r in rows[1:]: m.setdefault(int(r[1]), {})[int(r[2])] = float(r[j])
        M[k] = m
    tc = {int(float(r[0])): np.array([float(x) for x in r[1:]]) for r in list(csv.reader(open(D + '/data_tuning-curves_rescaled.csv')))[1:]}
    ids = sorted(tc); M['AngEXACT'] = {a: {b: float(np.prod(np.cos((tc[a] - tc[b]) / 2) ** 2)) for b in ids} for a in ids}   # exact |<a|b>|^2 of the released ang circuit
    return M, ids, tc
PRINTED = [('Euclidean', 'Fidelity', 0.994), ('Euclidean', 'Correlation', 0.488), ('Amp', 'AmpQFT', 0.349), ('AmpQFT', 'Ang', 0.039),
           ('Euclidean', 'AmpQFT', 0.145), ('Correlation', 'AmpQFT', 0.030), ('Euclidean', 'AmpQFT+IBM', 0.880), ('Fidelity', 'Ang+IBM', 0.702),
           ('Amp+IBM', 'Amp+DDD+IBM', 0.919), ('AmpQFT+IBM', 'AmpQFT+DDD+IBM', 0.904)]
if __name__ == '__main__':
    M, ids, tc = matrices(sys.argv[1]); V = {k: tri(m, ids) for k, m in M.items()}
    print(f'{len(ids)} neurons, {len(V["Fidelity"])} off-diagonal pairs')
    ok = 0
    for a, b, p in PRINTED:
        r = spearmanr(V[a], V[b], nan_policy='omit').statistic; hit = abs(round(abs(r), 3) - p) <= 0.001; ok += hit
        print(f'  {a:>14} vs {b:<15} printed {p:.3f}  mine |r| = {abs(r):.4f} (signed {r:+.4f})  {"MATCH" if hit else "MISS"}')
    print(f'KNOWN-GOOD {ok}/{len(PRINTED)} printed Mantel statistics reproduced to the printed digit (+-0.001)')
    print('Defined after reading their data (descriptive, not the known-good):')
    for a in ['Ang', 'Ang+IBM']: print(f'  AngEXACT vs {a:<8} spearman {spearmanr(V["AngEXACT"], V[a]).statistic:+.4f}')
    for c in ['Fidelity', 'Euclidean', 'Correlation']:
        print(f'  {c:>11}: vs AngEXACT {spearmanr(V[c], V["AngEXACT"]).statistic:+.4f}  vs Ang(sim col) {spearmanr(V[c], V["Ang"]).statistic:+.4f}  vs Ang+IBM {spearmanr(V[c], V["Ang+IBM"]).statistic:+.4f}')
    ang = np.array([M['Ang+IBM'][a][b] for i, a in enumerate(ids) for b in ids[i:]]); S = (ang - 0.5) * 2 * 2 ** 18
    print(f'  Ang+IBM column = 1/2 + S/2^19 with S integer in {np.mean(np.abs(S - np.round(S)) < 1e-6) * 100:.1f} % of {len(S)} rows; S range {S.min():.0f}..{S.max():.0f} (1000 shots): '
          f'the column is (1 + sum(-1)^(s.t) counts / 2^18)/2, i.e. counts divided by 2^18 = 262144 not by 1000 shots')
    ex = np.array([M['AngEXACT'][a][b] for i, a in enumerate(ids) for b in ids[i:]]); est = S / 1000
    d = est - ex; print(f'  their hardware swap estimate S/1000 minus exact |<a|b>|^2 over {len(d)} rows: median {np.median(d):+.4f}, 2.5-97.5 % [{np.percentile(d, 2.5):+.4f}, {np.percentile(d, 97.5):+.4f}]; '
                        f'ratio median {np.median(est / ex):.4f}; identical pairs (a=b, exact 1): median {np.median(est[ex > 0.999999]):.4f} n={int(np.sum(ex > 0.999999))}')
    sim = np.array([M['Ang'][a][b] for i, a in enumerate(ids) for b in ids[i:]])
    print(f'  their simulator Ang column vs (1+exact)/2 of the released circuit: max |diff| {np.max(np.abs(sim - (1 + ex) / 2)):.4f}, median {np.median(sim - (1 + ex) / 2):+.4f}')
    # --- circuit rebuild check: my builder (swaprun.build) vs their released qasm2 for every pair (data only, parsed by Qiskit's qasm2 reader)
    from qiskit import QuantumCircuit
    import swaprun
    rows = read(sys.argv[1] + '/circuits_ang.xlsx')['Sheet1']; eq = 0
    for r in rows[1:]:
        a, b = int(r[1]), int(r[2]); ta, tb = (tc[a], tc[b])
        theirs = QuantumCircuit.from_qasm_str(r[3]); mine = swaprun.build(ta, tb)
        if not (theirs.data and theirs.data[0].operation.name == 'rx' and abs(theirs.data[0].operation.params[0] - ta[0]) < 1e-12): ta, tb = tb, ta; mine = swaprun.build(ta, tb)   # their small_then_big order
        sig = lambda q: [(i.operation.name, tuple(q.find_bit(x).index for x in i.qubits), tuple(round(float(p), 12) for p in i.operation.params)) for i in q.data]
        eq += sig(theirs) == sig(mine)
    print(f'  CIRCUIT REBUILD: my builder equals their released qasm2 instruction-for-instruction (gates, qubits, angles to 1e-12) in {eq}/{len(rows) - 1} pairs')
    # --- their Aug 2025 hardware values (un-bugged S/1000) for the pairs this run uses
    P = swaprun.select(tc); look = {(int(r[1]), int(r[2])): (float(r[3]) - 0.5) * 2 * 2 ** 18 / 1000 for r in read(sys.argv[1] + '/results_ibm-kingston.xlsx')['Sheet1'][1:]}
    for p in P:
        if p['cls'] == 'ORTHO': continue
        v = look.get((p['A'], p['B']), look.get((p['B'], p['A'])))
        print(f"  THEIR 2025 kingston F^ (S/1000) {p['cls']:>6} {p['A']:>3}-{p['B']:<3} exact {p['F']:.4f}  theirs {v:.3f}  diff {v - p['F']:+.4f}")
