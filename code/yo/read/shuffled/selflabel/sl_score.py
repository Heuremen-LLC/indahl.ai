"""sl_score.py -- SELF-LABEL arm scoring, per PLAN_YO_SHUFFLED Addendum 2 (written before any self-label reply exists).
Pairs: YO Read seed 61/62/63 (eval_rescore_yo_read1-3.jsonl, the rescored outputs) vs SELF-LABEL seed 74/75/76 (eval_rescore_yo_self1-3.jsonl), per field,
same 148 papers. Exact two-sided McNemar on discordant pairs (b = YO Read right & self-label wrong, c = self-label right & YO Read wrong), Holm across these 9.
YO Read beats a self-label seed on a field only if its accuracy is higher AND Holm p < 0.05 (PREREG_YO_RESCORE.md line 15).
PASS on a field: YO Read beats all three. Otherwise that field FAILS: "the gain is NOT SHOWN to need the real labels". Unread replies count wrong."""
import json, os
from math import comb
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(H + '/../..')
def binom_two(b, c):
    n = b + c
    if n == 0: return 1.0
    k = min(b, c); return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)
ld = lambda p: {json.loads(l)['id']: json.loads(l) for l in open(p)}
yo = {s: ld(f'{R}/eval_rescore_yo_read{s}.jsonl') for s in (1, 2, 3)}
sl = {s: ld(f'{R}/eval_rescore_yo_self{s}.jsonl') for s in (1, 2, 3)}
items = [json.loads(l) for l in open(R + '/data/test_items_rescore.jsonl')]
tests = []
for q in ('DATES', 'LINK', 'REQUEST'):
    its = [i for i in items if i['q'] == q]
    for s in (1, 2, 3):
        a = {i['id']: yo[s][i['id']]['score'] == 1.0 for i in its}; z = {i['id']: sl[s][i['id']]['score'] == 1.0 for i in its}
        b = sum(a[k] and not z[k] for k in a); c = sum(z[k] and not a[k] for k in a)
        tests.append(dict(q=q, yo_seed=60 + s, self_seed=73 + s, n=len(its), yo_right=sum(a.values()), self_right=sum(z.values()), b=b, c=c,
                          unread_self=sum(sl[s][i['id']]['pred'] is None for i in its), p=binom_two(b, c)))
order = sorted(range(len(tests)), key=lambda i: tests[i]['p']); m = len(tests); prev = 0
for rank, i in enumerate(order):
    adj = min(1.0, max(prev, (m - rank) * tests[i]['p'])); tests[i]['p_holm'] = adj; prev = adj
L = ['SELF-LABEL arm (PLAN_YO_SHUFFLED Addendum 2). YO Read seed vs self-label seed, per field, 148 papers, exact McNemar, Holm across 9.']
for t in tests:
    t['beats'] = t['yo_right'] > t['self_right'] and t['p_holm'] < 0.05
    L.append(f"{t['q']:8s} YO {t['yo_seed']} {t['yo_right']}/{t['n']} vs self {t['self_seed']} {t['self_right']}/{t['n']}; b {t['b']} c {t['c']}; self unread {t['unread_self']}; p {t['p']:.4g}, Holm {t['p_holm']:.4g} -> {'YO READ BEATS IT' if t['beats'] else 'not beaten'}")
for q in ('DATES', 'LINK', 'REQUEST'):
    k = sum(t['beats'] for t in tests if t['q'] == q)
    L.append(f"{q}: YO Read beats {k} of 3 self-label seeds -> {'PASS' if k == 3 else 'FAIL (the gain is NOT SHOWN to need the real labels on ' + q + ')'}")
open(H + '/results_selflabel.text', 'w').write('\n'.join(L) + '\n'); json.dump(tests, open(H + '/results_selflabel.json', 'w'), indent=1); print('\n'.join(L))
