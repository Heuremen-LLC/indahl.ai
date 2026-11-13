"""yr_rescore_score.py -- the frozen scoring of PREREG_YO_RESCORE.md (sha256 fe751109...). Written and committed before any rescore reply exists.
Per field (DATES, LINK, REQUEST) and per seed (61, 62, 63): accuracy against the labels, the "always answer NO" baseline on the same items, exact two-sided
McNemar on the discordant pairs (b = seed right & NO wrong, c = seed wrong & NO right), Holm across all 9 seed x field tests. A seed clears a field
only if its accuracy is above always-NO AND its Holm-corrected p < 0.05. Every seed reported, raw counts and (b, c) printed. Unread replies count wrong."""
import json, os
from math import comb
H = os.path.dirname(os.path.abspath(__file__))
def binom_two(b, c):
    n = b + c
    if n == 0: return 1.0
    k = min(b, c); p = sum(comb(n, i) for i in range(k + 1)) / 2 ** n; return min(1.0, 2 * p)
rows = {s: {json.loads(l)['id']: json.loads(l) for l in open(f'{H}/eval_rescore_yo_shuf{s}.jsonl')} for s in (1, 2, 3)}
items = [json.loads(l) for l in open(H + '/data/test_items_rescore.jsonl')]
tests = []
for q in ('DATES', 'LINK', 'REQUEST'):
    its = [i for i in items if i['q'] == q]
    no_right = {i['id']: i['answer'] == 'NO' for i in its}
    for s in (1, 2, 3):
        r = rows[s]; right = {i['id']: r[i['id']]['score'] == 1.0 for i in its}
        b = sum(right[k] and not no_right[k] for k in right); c = sum((not right[k]) and no_right[k] for k in right)
        acc = sum(right.values()) / len(its); acc0 = sum(no_right.values()) / len(its); unread = sum(r[i['id']]['pred'] is None for i in its)
        tests.append(dict(q=q, seed=70 + s, n=len(its), acc=acc, acc_no=acc0, right=sum(right.values()), no_right=sum(no_right.values()), b=b, c=c, unread=unread, p=binom_two(b, c)))
order = sorted(range(len(tests)), key=lambda i: tests[i]['p']); m = len(tests); prev = 0
for rank, i in enumerate(order):
    adj = min(1.0, max(prev, (m - rank) * tests[i]['p'])); tests[i]['p_holm'] = adj; prev = adj
lines = ['YO SHUFFLED arm, scored with a copy of yr_rescore_score.py (only file names and seed numbers changed). YO rescore (PREREG_YO_RESCORE.md fe751109..., items DATA_YO_RESCORE.sha256 132a3b0f...). Every seed, every field; raw counts beside rates.']
for t in tests:
    t['clears'] = t['acc'] > t['acc_no'] and t['p_holm'] < 0.05
    lines.append(f"{t['q']:8s} seed {t['seed']}: {t['right']}/{t['n']} = {t['acc']:.3f} vs always-NO {t['no_right']}/{t['n']} = {t['acc_no']:.3f}; b {t['b']} c {t['c']}; unread {t['unread']}; McNemar p {t['p']:.4g}, Holm {t['p_holm']:.4g} -> {'CLEARS' if t['clears'] else 'does not clear'}")
dates = [t for t in tests if t['q'] == 'DATES' and t['clears']]
lines.append('DATES: ' + (f"cleared by seed(s) {', '.join(str(t['seed']) for t in dates)}" if dates else 'NO SEED CLEARS DATES -> per the rule, the public sentence is restated and the second-read plan withdrawn or rewritten'))
open(H + '/shuffled/results_shuffled.text', 'w').write('\n'.join(lines) + '\n'); json.dump(tests, open(H + '/shuffled/results_shuffled.json', 'w'), indent=1); print('\n'.join(lines))
