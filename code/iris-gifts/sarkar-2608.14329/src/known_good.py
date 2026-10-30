#!/usr/bin/env python3
"""Known-good for Sarkar, arXiv 2608.14329 (our code; their run files read as JSON data, nothing of theirs run).
Rebuilds: LLM-judge accuracy on Consumer Duty original (printed 0.74) and adversarial (printed 0.27), COBS adversarial (0.92),
and the inter-judge kappa table (judge_agreement.csv: Consumer Duty adversarial 0.157 on n 23)."""
import json, os, glob, collections
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'theirs', 'tree_a2e47ae', 'runs')
CD, CO = 'PRINCIPLE_CONSUMER_DUTY_FAIR_VALUE', 'PRINCIPLE_FAIR_CLEAR_NOT_MISLEADING'
def run(method, split, judge2=False):
    fs = [f for f in glob.glob(R + '/*_%s_%s%s.json' % (method, split, '_judge2' if judge2 else '')) ]
    assert len(fs) == 1, fs
    return json.load(open(fs[0]))
def expected(sid): return sid.rsplit('_', 1)[1]          # ids end in _comply or _escalate
def own(sid): return CD if 'CONSUMER_DUTY' in sid else CO
def verdicts(d):
    """per scenario: {principle: 'escalate'|'comply'}; scenarios without assessments returned separately with their keys"""
    out, fail = {}, {}
    for s in d['per_scenario']:
        if 'assessments' not in s: fail[s['id']] = sorted(k for k in s if k != 'id'); continue
        out[s['id']] = {a['principle_id']: ('escalate' if a['escalation_required'] else 'comply') for a in s['assessments']}
    return out, fail
def acc(d, p):
    v, fail = verdicts(d); ids = [i for i in v if own(i) == p]
    ok = sum(v[i][p] == expected(i) for i in ids); nf = sum(1 for i in fail if own(i) == p)
    return ok, len(ids), nf, fail
def kappa(a, b):
    n = len(a); po = sum(x == y for x, y in zip(a, b)) / n; cats = set(a) | set(b)
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats); return (po - pe) / (1 - pe) if pe < 1 else float('nan'), po, n
print('LLM-judge (gpt-oss:120b), each scenario scored on its own principle:')
for split, p, printed in (('original', CD, '0.74'), ('adversarial', CD, '0.27'), ('original', CO, '0.96'), ('adversarial', CO, '0.92')):
    ok, n, nf, fail = acc(run('llm-judge', split), p)
    print('  %-11s %-36s %2d of %2d = %.4f (printed %s) | scenarios with no assessment on this principle: %d' % (split, p, ok, n, ok / n, printed, nf))
_, fail = verdicts(run('llm-judge', 'adversarial')); print('  adversarial scenarios with no assessment:', {k: v for k, v in fail.items()})
print('\nInter-judge kappa, their pooling (every scenario both judges assessed, scored against one principle):')
for split in ('original', 'paraphrase', 'adversarial', 'boundary'):
    v1, _ = verdicts(run('llm-judge', split)); v2, _ = verdicts(run('llm-judge', split, judge2=True))
    for p in (CO, CD):
        ids = sorted(i for i in v1 if i in v2 and p in v1[i] and p in v2[i])
        k, po, n = kappa([v1[i][p] for i in ids], [v2[i][p] for i in ids])
        print('  %-11s %-36s n %3d kappa %.3f raw agreement %.3f' % (split, p, n, k, po))
