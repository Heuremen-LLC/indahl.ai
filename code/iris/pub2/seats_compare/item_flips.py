"""item_flips.py (defined after the data, 30 Oct 2026, from the /tp wipe of the two-machine reading): item-level scored-class flips on the gated
families' scored items read in all four runs (Mac bare/copy, CUDA bare/copy), against each machine's own repeat floor; direction of the flips;
items readable on one machine only. Output: item_flips.txt."""
import json, os, sys, collections
from math import comb
IB = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(IB, 'faultsbench2')); import score as S
P = [('phi4-mini', 'faultsbench2/out/phi4-mini', 'faultsbench2_armature/out/phi4-mini_latest')] + [(m, f'faultsbench2_mac_cross/out/{m}', f'faultsbench2_armature/out/{m}') for m in ('llama3.2_3b', 'qwen2.5_1.5b', 'granite4.1_3b', 'ministral-3_3b')]
G = {'phi4-mini': ['P1', 'P2', 'P4'], 'llama3.2_3b': ['P1', 'P2', 'P4'], 'qwen2.5_1.5b': ['P2', 'P4'], 'granite4.1_3b': ['P1', 'P2', 'P4'], 'ministral-3_3b': ['P1', 'P2', 'P4']}   # families whose gates passed on both machines (seats_compare/results.txt)
def rows(d, arm): return {r['id']: r for r in map(json.loads, open(os.path.join(IB, d, arm + '.jsonl')))}
def cl(R, k): return S.cls(S.IT[k], R[k]['raw'], 'bare', R[k].get('done_reason'))
L = []; T = collections.Counter(); up = dn = 0
for m, dm, da in P:
    Mb, Mc, Ab, Ac = rows(dm, 'bare'), rows(dm, 'bare_copy'), rows(da, 'bare'), rows(da, 'bare_copy'); c = collections.Counter()
    for k in [k for k in S.IT if S.IT[k]['fam'] in G[m] and S.IT[k].get('kind') not in ('control', 'gw')]:
        v = {n: cl(R, k) for n, R in (('Mb', Mb), ('Mc', Mc), ('Ab', Ab), ('Ac', Ac))}
        c['seen'] += 1
        for n_, x in v.items():
            if x not in ('FAULT', 'OK'): c['unread_' + n_] += 1
        if any(x not in ('FAULT', 'OK') for x in v.values()): c['dropped'] += 1
        if all(x in ('FAULT', 'OK') for x in v.values()):
            c['n'] += 1; c['mac_rep'] += v['Mb'] != v['Mc']; c['cuda_rep'] += v['Ab'] != v['Ac']; c['across'] += v['Mb'] != v['Ab']; c['across_copy'] += v['Mc'] != v['Ac']
            up += (v['Ab'] == 'FAULT' and v['Mb'] == 'OK'); dn += (v['Ab'] == 'OK' and v['Mb'] == 'FAULT')
    T.update(c); L.append(f"{m}: items {c['n']}; flips Mac repeat {c['mac_rep']}, CUDA repeat {c['cuda_rep']}, across bare {c['across']}, across copy {c['across_copy']}; dropped {c['dropped']} of {c['seen']} (unread Mac bare {c['unread_Mb']}, Mac copy {c['unread_Mc']}, CUDA bare {c['unread_Ab']}, CUDA copy {c['unread_Ac']})")
n = up + dn; p = min(1.0, 2 * sum(comb(n, i) for i in range(max(up, dn), n + 1)) / 2 ** n)
L.append(f"TOTAL items {T['n']}; flips Mac repeat {T['mac_rep']}, CUDA repeat {T['cuda_rep']}, across bare {T['across']}, across copy {T['across_copy']}; dropped {T['dropped']} of {T['seen']} (unread Mac bare {T['unread_Mb']}, Mac copy {T['unread_Mc']}, CUDA bare {T['unread_Ab']}, CUDA copy {T['unread_Ac']}); direction across bare: to fault on CUDA {up}, to OK on CUDA {dn}, exact two-sided p {p:.3f}")
open(os.path.join(IB, 'seats_compare', 'item_flips.txt'), 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
