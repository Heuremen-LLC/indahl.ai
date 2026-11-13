#!/usr/bin/env python3
"""paired.py: the plan's Reading section, run on both evaluation sets. Writes paired_results.json.
Per family, bare arm: paired fault difference per item (trained minus base, trained minus mixed), bootstrap 2,000, seed 7, 95% interval.
Fewer faults = AHEAD (interval below zero), more faults = BEHIND (interval above zero), CONSISTENT otherwise.
CANNOT_TELL where either arm's family gate failed or fewer than 10 items were readable in both arms.
A gain is reported only where trained is AHEAD of base in both sets and AHEAD of mixed in both sets."""
import sys, os, json, random
B = os.path.dirname(os.path.abspath(__file__)); IB = os.path.join(B, '..')
res = {}
for s in ('tA', 'tB'):
    d = os.path.join(IB, 'faultsbench_' + s); sys.path.insert(0, d); sys.modules.pop('score', None)
    import score as S; sys.path.pop(0)
    M = {m: S.score(m) for m in ('falcon3_base', 'falcon3_trained', 'falcon3_mixed')}
    L = {m: (S.load(m, 'bare'), S.load_dr(m, 'bare')) for m in M}
    def cl(m, k): return S.cls(S.IT[k], L[m][0].get(k), 'bare', L[m][1].get(k))
    for fam in ('P1', 'P2', 'P3', 'P4'):
        ks = [k for k, i in S.IT.items() if i['fam'] == fam and i.get('kind') not in ('control', 'gw')]
        for ref in ('falcon3_base', 'falcon3_mixed'):
            gates = all(M[m]['model_gate'] == 'pass' and not str(M[m]['fam'][fam]['outcome']).startswith('CANNOT_TELL (family') for m in ('falcon3_trained', ref))
            pairs = [(cl(ref, k) == 'FAULT', cl('falcon3_trained', k) == 'FAULT') for k in ks if cl(ref, k) in ('FAULT', 'OK') and cl('falcon3_trained', k) in ('FAULT', 'OK')]
            rec = dict(set=s, family=fam, vs=ref, n_pairs=len(pairs), gate_ok=gates)
            if pairs:
                R = random.Random(7); ds = []
                for _ in range(2000):
                    x = [pairs[R.randrange(len(pairs))] for _ in pairs]; ds.append(sum(t - r for r, t in x) / len(x))
                ds.sort(); dd = sum(t - r for r, t in pairs) / len(pairs); lo, hi = ds[49], ds[1949]
                rec.update(diff=round(dd, 3), lo=round(lo, 3), hi=round(hi, 3), ref_fault=round(sum(r for r, t in pairs) / len(pairs), 3), trained_fault=round(sum(t for r, t in pairs) / len(pairs), 3))
                rec['outcome'] = 'CANNOT_TELL' if (not gates or len(pairs) < 10) else ('AHEAD' if hi < 0 else ('BEHIND' if lo > 0 else 'CONSISTENT'))
            else: rec['outcome'] = 'CANNOT_TELL'
            res[f'{s}|{fam}|{ref}'] = rec
out = []
for fam in ('P1', 'P2', 'P3', 'P4'):
    for ref in ('falcon3_base', 'falcon3_mixed'):
        a, b = res[f'tA|{fam}|{ref}'], res[f'tB|{fam}|{ref}']
        out.append(dict(family=fam, vs=ref, A=a, B=b, gain='GAIN' if a['outcome'] == b['outcome'] == 'AHEAD' else ('CANNOT_TELL' if 'CANNOT_TELL' in (a['outcome'], b['outcome']) else 'NO GAIN')))
json.dump(out, open(os.path.join(B, 'paired_results.json'), 'w'), indent=1)
for r in out:
    f = lambda x: f"{x['outcome']} n={x['n_pairs']} ref {x.get('ref_fault')} trained {x.get('trained_fault')} diff {x.get('diff')} [{x.get('lo')}, {x.get('hi')}]"
    print(r['family'], 'vs', r['vs'].replace('falcon3_', ''), '|', r['gain'], '\n   A', f(r['A']), '\n   B', f(r['B']))
