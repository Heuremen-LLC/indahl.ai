"""yf_combine.py -- final verdict per field for PLAN_YO_FRESH Addendum 3: a verdict reads as shown only if it holds on BOTH the primary (88) and the
sensitivity (84) sets. If they split, the field prints "depends on 4 labels" and nothing stronger. Reads results_fresh_{primary,sensitivity}.json."""
import json, os
H = os.path.dirname(os.path.abspath(__file__)); F = ('DATES', 'LINK', 'REQUEST')
def verdicts(SET):
    d = json.load(open(f'{H}/results_fresh_{SET}.json')); out = {}
    for q in F:
        A = [t for t in d['A'] if t['q'] == q]; A2 = [t for t in d['A2'] if t['q'] == q]; B = [t for t in d['B'] if t['q'] == q]
        rep = sum(x['win'] and y['win'] for x, y in zip(A, A2)) >= 2; bp = sum(t['win'] for t in B) == 3
        out[q] = ('REPLICATES' if rep else 'not shown on these papers', 'needs the real labels' if (bp and rep) else 'not shown to need the real labels')
    return out
P, S = verdicts('primary'), verdicts('sensitivity'); L = ['FRESH TEST final reading (Addendum 3): agreement with the List reader F4 notes as parsed, on unseen papers. UNDERPOWERED.']
for q in F:
    for k, name in ((0, 'replication'), (1, 'labels')):
        a, b = P[q][k], S[q][k]
        L.append(f'{q} {name}: ' + (a if a == b else f'depends on 4 labels (primary: {a}; sensitivity: {b})'))
open(H + '/results_fresh_final.text', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
