"""precision.py -- how well does IBM's published per-qubit T2 predict the qubit, against our own measurements at known time gaps?
(23 Oct 2026, after the marrakesh fresh-record run; idea: Wayfinder, triangulate the noise; method: the three-cornered hat of clock
metrology, three readings of one quantity whose pairwise disagreements separate each reading's own noise. Zero QPU seconds.)
Per chip and fit (FIXED 1/2, FREE asymptote), per qubit, on log T2, robust spread (1.4826 x MAD) of differences:
  OUR NOISE  : copy vs copy inside one job, halved (two copies pooled per run)
  OURS vs OURS: pooled run a vs pooled run b, minus both runs' noise -> how far the qubit itself wanders over the time between runs
  IBM vs OURS : IBM's stated T2 in the record saved at submission vs our pooled run, minus our noise -> IBM's snapshot error plus the
                qubit's wander over the record's age
Reading (defined here, before the referee): if IBM vs OURS does not grow with the record's age while OURS vs OURS grows with the gap,
the IBM-vs-qubit gap is set by the published value's own imprecision, not by its age."""
import json, sys, itertools, datetime as dt, numpy as np
sys.path.insert(0, '.'); import hahn as R
from hahn_pool import fit
CH = {'ibm_fez': ['fez_run1', 'fez_run2', 'fez_clock1', 'fez_clock2'], 'ibm_kingston': ['kingston_run1', 'kingston_run2', 'kingston_fresh'],
      'ibm_marrakesh': ['marrakesh_run1', 'marrakesh_run2', 'marrakesh_fresh']}
def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00'))
def rv(x): x = np.asarray(x); return (1.4826 * np.median(np.abs(x - np.median(x)))) ** 2
def load(tag):
    rec = json.load(open(f'job_hahn_ibm_{tag}.json')); z = np.load(f'raw_hahn_ibm_{tag}.npz'); props = json.load(open(f'props_hahn_ibm_{tag}.json'))
    sub = ts(rec['submitted_utc']); st, age = {}, {}
    for q, ps in enumerate(props['qubits']):
        for x in ps:
            if x['name'] == 'T2' and x['value'] > 0: st[q] = x['value']; age[q] = (sub - ts(x['date'])).total_seconds() / 3600
    p = {}
    for i, m in enumerate(rec['meta']):
        S = rec['sets'][m['set']]; b = z[f'c_{i}'][:, :len(S)]
        for j, q in enumerate(S): p.setdefault(q, {}).setdefault(m['copy'], {})[m['tau_us']] = float(b[:, j].mean())
    out = {}
    for free in (False, True):
        for key in ('pool', 0, 1):
            dd = {}
            for q, cp in p.items():
                cs = sorted(cp)
                y = [np.mean([cp[c][t] for c in cs]) for t in R.TAUS] if key == 'pool' else [cp[cs[key]][t] for t in R.TAUS]
                T2, A, _ = fit(R.TAUS, y, free)
                if A > 0.2 and np.isfinite(T2) and T2 > 0: dd[q] = np.log(T2)
            out[(key, free)] = dd
    return out, {q: np.log(v) for q, v in st.items()}, float(np.median(list(age.values()))), sub
for chip, tags in CH.items():
    L = {t: load(t) for t in tags}
    for free in (False, True):
        D = {t: L[t][0][('pool', free)] for t in tags}
        noise = {t: rv([L[t][0][(0, free)][q] - L[t][0][(1, free)][q] for q in L[t][0][(0, free)] if q in L[t][0][(1, free)]]) / 2 for t in tags}
        print(f'== {chip} {"FREE " if free else "FIXED"} | our noise per run ' + ', '.join(f'{np.sqrt(noise[t]):.3f}' for t in tags))
        for a, b in itertools.combinations(tags, 2):
            qs = [q for q in D[a] if q in D[b]]; gap = abs((L[b][3] - L[a][3]).total_seconds()) / 3600
            print(f'   OURS vs OURS {a:15} {b:15} {gap:6.2f} h apart: {np.sqrt(max(rv([D[a][q] - D[b][q] for q in qs]) - noise[a] - noise[b], 0)):.3f}  (n {len(qs)})')
        for t in tags:
            st = L[t][1]; qs = [q for q in D[t] if q in st]
            print(f'   IBM  vs OURS {t:15} record {L[t][2]:5.1f} h old: {np.sqrt(max(rv([st[q] - D[t][q] for q in qs]) - noise[t], 0)):.3f}  (n {len(qs)})')
