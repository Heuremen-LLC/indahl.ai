"""Run the stratified G test + exact shuffle null on every table in one or more npz files.
Writes a JSON list of result rows. Pools across files (sum of G; replicate G's summed for the pooled null)."""
import sys, json, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import bellsort as bs
from scipy.stats import chi2

def effect(name, T, slot_ns=None):
    K, E = T.shape[1], T.shape[2]
    if K == 2 and E == 2:
        r = bs.rate_split(T, 1)
        return dict(effect=f"outcome-1 rate {r['base_rate']:.5g}; key1-key0 adj diff {r['adj_diff']:+.3g} (relative {r['adj_diff']/r['base_rate']:+.3%})")
    if K == 2 and slot_ns is not None and E == len(slot_ns):
        d = bs.mean_split(T, slot_ns)
        return dict(effect=f"mean time shift key1-key0 {d:+.4g} ns")
    return dict(effect='')

def run(files, dataset, R=2000, slot_ns=None, out=None):
    rows = []; pooled = {}
    rng = np.random.default_rng(20260929)
    for fn in files:
        z = np.load(fn)
        tag = os.path.basename(fn).replace('.npz', '')
        for k in z.files:
            if k == 'ntrials':
                continue
            T = z[k]
            name = k.replace('__', '|').replace('_BY_', '~')
            res, Gp = bs.test_table(T, R=R, rng=rng)
            res.update(dataset=dataset, part=tag, sort=name)
            res.update(effect(name, T, slot_ns))
            rows.append(res)
            P = pooled.setdefault(name, dict(G=0.0, df=0, Gp=np.zeros(R), N=0))
            P['G'] += res['G']; P['df'] += int(res['df']); P['Gp'] += Gp; P['N'] += res['N']
    if len(files) > 1:
        for name, P in pooled.items():
            rows.append(dict(dataset=dataset, part='POOLED', sort=name, G=P['G'], df=P['df'], N=P['N'],
                             p_analytic=float(chi2.sf(P['G'], P['df'])),
                             p_shuffle=float((1 + np.sum(P['Gp'] >= P['G'])) / (1 + R)),
                             z_vs_shuffle=float((P['G'] - P['Gp'].mean()) / P['Gp'].std()), R=R, effect=''))
    for r in rows:
        for k, v in list(r.items()):
            if isinstance(v, (np.integer,)): r[k] = int(v)
            if isinstance(v, (np.floating,)): r[k] = float(v)
    if out:
        json.dump(rows, open(out, 'w'), indent=1)
    return rows

def show(rows, filt=None):
    for r in rows:
        if filt and filt not in r['sort'] and filt not in r['part']:
            continue
        print(f"{r['part'][:28]:28s} {r['sort']:28s} N={r['N']:>11d} G={r['G']:9.2f} df={r['df']:3d} p_an={r['p_analytic']:.3g} p_shuf={r['p_shuffle']:.4f} z={r['z_vs_shuffle']:+6.2f} {r.get('effect','')}")
