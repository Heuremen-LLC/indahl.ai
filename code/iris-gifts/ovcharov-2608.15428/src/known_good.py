#!/usr/bin/env python3
"""known_good.py: rebuild Ovcharov's Table 4 row for Llama 3.1 8B (and two other rows) from his released predictions, our own code.
Blind accuracy over parsed answers, answer-position shares, habit = sum_j q_j * g_j (the model's own position shares against the gold-position
shares of the set), excess = blind - habit, Wilson 95% interval. Reads theirs/ as data only."""
import json, sys, os, collections, math
T = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'theirs')
gold = {}
for l in open(T + '/data/ua_judge_exam_gated.jsonl'):
    r = json.loads(l); gold[r['id']] = r.get('answer', r.get('gold', r.get('key')))
rows = collections.defaultdict(list); keys = None
for l in open(T + '/predictions/scenario_a.jsonl'):
    r = json.loads(l); keys = keys or list(r); rows[r['model']].append(r)
print('fields:', keys); print('models:', sorted((m, len(v)) for m, v in rows.items()))
def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)); return (c - h) / d, (c + h) / d
g = collections.Counter(r['gold'] for v in list(rows.values())[:1] for r in v); gn = sum(g.values()); gs = [g[j] / gn for j in range(4)]
print('gold-position shares of the set:', [round(x, 3) for x in gs], 'n', gn)
for m in sorted(rows):
    v = rows[m]; parsed = [r for r in v if r.get('pred') is not None and r['pred'] in (0, 1, 2, 3)]
    k = sum(r['pred'] == r['gold'] for r in parsed); n = len(parsed); q = collections.Counter(r['pred'] for r in parsed); qs = [q[j] / n for j in range(4)]
    habit = sum(a * b for a, b in zip(qs, gs)); lo, hi = wilson(k, n)
    print('%-16s n %5d of %5d  A %.2f B %.2f C %.2f D %.2f  blind %.3f [%.3f, %.3f]  habit %.3f  excess %+.3f' % (m, n, len(v), *qs, k / n, lo, hi, habit, k / n - habit))

# 30 Oct addendum, before any run: the printed Table 4 digits, compared in code. Two habit rules side by side: set = gold shares of all
# 8,128 accepted items (the paper's words); parsed = gold shares of the items that model's reply was parsed on (rebuilds Llama's 0.287).
PRINTED = {  # model: (A, B, C, D, blind, habit, excess) as printed in Table 4, and the blind interval from Table 3
 'gpt-5.6-sol': (.24, .27, .27, .22, .515, .250, .265), 'sonnet-4.6': (.08, .20, .30, .42, .320, .238, .081),
 'deepseek-r1': (.12, .24, .29, .35, .257, .242, .015), 'qwen3-32b': (.14, .27, .30, .30, .244, .244, .000),
 'ministral-8b': (.02, .25, .45, .29, .239, .238, .001), 'llama-3.3-70b': (.08, .28, .31, .33, .237, .240, -.003),
 'nova-micro': (.09, .31, .22, .39, .233, .240, -.007), 'nova-pro': (.17, .28, .27, .28, .232, .246, -.014),
 'gemma-3-12b': (.08, .28, .40, .23, .230, .242, -.012), 'nova-2-lite': (.03, .30, .29, .39, .225, .237, -.012),
 'pixtral-large': (.10, .46, .25, .20, .239, .244, -.005), 'llama-3.1-8b': (.92, .00, .07, .01, .292, .287, .005),
 'haiku-4.5': (.16, .44, .22, .19, .204, .247, -.043)}
print('\nprinted Table 4 against our rebuild, both habit rules (a cell is off when its rounding differs from the printed digit)')
full = {'set': 0, 'parsed': 0}
for m in sorted(rows):
    v = rows[m]; parsed = [r for r in v if r.get('pred') in (0, 1, 2, 3)]; n = len(parsed)
    q = collections.Counter(r['pred'] for r in parsed); qs = [q[j] / n for j in range(4)]; blind = sum(r['pred'] == r['gold'] for r in parsed) / n
    gp = collections.Counter(r['gold'] for r in parsed); gps = [gp[j] / n for j in range(4)]
    out = []
    for rule, G in (('set', gs), ('parsed', gps)):
        h = sum(a * b for a, b in zip(qs, G)); ours = [round(x, 2) for x in qs] + [round(blind, 3), round(h, 3), round(blind - h, 3)]
        off = [i for i, (a, b) in enumerate(zip(ours, PRINTED[m])) if abs(a - b) > 1e-9]
        if not off: full[rule] += 1
        out.append('%s habit %.4f %s' % (rule, h, 'all 7 cells match' if not off else 'off in ' + ','.join('ABCD'[i] if i < 4 else ['blind', 'habit', 'excess'][i - 4] for i in off)))
    print('%-15s n %5d  %s  |  %s%s' % (m, n, *out, '   (partial file: %d rows released)' % len(v) if m == 'pixtral-large' else ''))
print('rows matching all 7 printed cells: set rule %d of 13, parsed rule %d of 13' % (full['set'], full['parsed']))
