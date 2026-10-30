#!/usr/bin/env python3
"""K, E1, E2 (PLAN ac3c2a9, committed before this ran). Selvam and Ghosh, arXiv 2607.10626. Our code; their verdict files read as data.
No passage, question or answer text is printed."""
import os, json, glob, random, collections
B = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'theirs', 'repo', 'data', 'runs')
NAME = {'azure-gpt': 'gpt', 'gpt': 'gpt', 'grok': 'grok', 'gemini': 'gemini'}
Y = collections.defaultdict(dict); AD = {}; PERT = {}; VAL = {}
for d in sorted(glob.glob(os.path.join(B, '*judge-*-on-*'))):
    for l in open(os.path.join(d, '06_judge.jsonl')):
        r = json.loads(l); cid = r['core_id']
        PERT[cid] = NAME[r['generators']['perturb']['provider']]; v_ = r.get('validation') or {}
        VAL[cid] = all(v_.get(k) is True for k in ('type_valid', 'answer_causal', 'global_context_consistent', 'no_original_answer_leakage', 'original_contradicts_perturbed'))
        for v in r.get('judge_verdicts') or []:
            if v.get('contains_factual_error') is None: continue
            g, j = NAME[v['generator_provider']], NAME[v['judge_provider']]
            Y[(cid, g)][j] = 1.0 if v['contains_factual_error'] else 0.0; AD[(cid, g)] = bool(v.get('gold_has_induced_error'))
def contrast(role, keep):
    """per answer: flag of the role's judge minus mean of the other judges' flags (role 'gen' = generator's judge, 'pert' = perturber's judge)"""
    out = []
    for (cid, g), d in Y.items():
        if not VAL.get(cid) or not keep(cid, g): continue
        m = g if role == 'gen' else PERT[cid]
        if m in d and len(d) >= 2:
            oth = [d[j] for j in d if j != m]; out.append((cid, AD[(cid, g)], d[m] - sum(oth) / len(oth)))
    return out
def summ(rows, adopted, seed=42, Bn=10000):
    x = [(c, v) for c, a, v in rows if a == adopted]; cl = collections.defaultdict(list)
    for c, v in x: cl[c].append(v)
    keys = sorted(cl); r = random.Random(seed); bs = []
    for _ in range(Bn):
        vals = [v for k in (keys[r.randrange(len(keys))] for _ in keys) for v in cl[k]]; bs.append(sum(vals) / len(vals))
    bs.sort(); return len(x), len(keys), 100 * sum(v for _, v in x) / len(x), 100 * bs[249], 100 * bs[9749]
fmt = lambda t: 'n %d answers on %d records: %+.1f pp [%+.1f, %+.1f]' % t
allk = lambda c, g: True
print('records %d, validated %d | answers with a verdict %d' % (len(PERT), sum(VAL.values()), len(Y)))
K = contrast('gen', allk)
print('K paired same-model contrast on validated records (matching judge minus the mean of the others on the same answer)')
print('  answers with the matching judge and at least one other: %d (all three judges: %d)' % (len(K), sum(1 for (cid, g), d in Y.items() if VAL.get(cid) and len(d) == 3)))
print('  recall on adopted answers (printed -0.5): ' + fmt(summ(K, True)))
print('  flagging on avoided answers (printed -4.3): ' + fmt(summ(K, False)))
print('\nE1 the perturber as judge (perturber\'s judge minus the mean of the others on the same answer)')
E1 = contrast('pert', allk)
print('  adopted answers: ' + fmt(summ(E1, True)))
print('  avoided answers: ' + fmt(summ(E1, False)))
print('  perturbers on validated records: %s' % dict(collections.Counter(PERT[c] for c in PERT if VAL[c])))
print('\nE2 answers whose generator is not the perturber')
nk = lambda c, g: g != PERT[c]
E2p, E2g = contrast('pert', nk), contrast('gen', nk)
print('  perturber\'s judge, adopted: ' + fmt(summ(E2p, True)) + ' | avoided: ' + fmt(summ(E2p, False)))
print('  generator\'s judge, adopted: ' + fmt(summ(E2g, True)) + ' | avoided: ' + fmt(summ(E2g, False)))
# E2b (PLAN Addendum 1, defined after the data)
print('\nE2b (defined after the data) answers whose generator is not the perturber: perturber\'s judge minus the third judge (neither is the generator\'s)')
E2b = []
for (cid, g), d in Y.items():
    if not VAL.get(cid) or g == PERT[cid]: continue
    p = PERT[cid]; o = [j for j in ('gpt', 'grok', 'gemini') if j not in (g, p)][0]
    if p in d and o in d: E2b.append((cid, AD[(cid, g)], d[p] - d[o]))
print('  adopted: ' + fmt(summ(E2b, True)) + ' | avoided: ' + fmt(summ(E2b, False)))
for adopted in (True, False):
    x = [v for c, a, v in E2b if a == adopted]; print('  %s: perturber flags and third does not %d, third flags and perturber does not %d' % ('adopted' if adopted else 'avoided', sum(v > 0 for v in x), sum(v < 0 for v in x)))
# E3, E4 (PLAN Addendum 2, defined after the data)
print('\nE3 (defined after the data) validating model against perturbing model, and gate failures by perturber')
VP = {}
for d in sorted(glob.glob(os.path.join(B, '*judge-*-on-*'))):
    for l in open(os.path.join(d, '06_judge.jsonl')):
        r = json.loads(l); VP[r['core_id']] = (NAME[r['generators']['perturb']['provider']], NAME[(r['generators'].get('validate') or {}).get('provider', '?')] if (r['generators'].get('validate') or {}).get('provider') in NAME else str((r['generators'].get('validate') or {}).get('provider')))
print('  records %d | validator equals perturber in %d' % (len(VP), sum(1 for p, v in VP.values() if p == v)))
print('  records failing a gate by perturber: %s of %s' % (dict(collections.Counter(PERT[c] for c in PERT if not VAL[c])), dict(collections.Counter(PERT.values()))))
print('\nE4 (defined after the data) matching-judge contrast where the generator is also the perturber, beside the other answers')
yk = lambda c, g: g == PERT[c]
E4a, E4b = contrast('gen', yk), contrast('gen', nk)
print('  generator is perturber, adopted: ' + fmt(summ(E4a, True)) + ' | avoided: ' + fmt(summ(E4a, False)))
print('  generator is not perturber, adopted: ' + fmt(summ(E4b, True)) + ' | avoided: ' + fmt(summ(E4b, False)))
