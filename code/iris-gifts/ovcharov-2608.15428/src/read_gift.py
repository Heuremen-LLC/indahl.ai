#!/usr/bin/env python3
"""read_gift.py: readings R1-R6 of PLAN.md for the 2608.15428 gift. Written before any reply existed (30 Oct 2026).
  --sample MACHINE MODEL ARM REP : print 10 replies (seed 7) with the parser's letter, for the read in full. No rates.
  --rates                        : R1-R6. Refuses an arm whose read-in-full note runs/READ_<machine>_<model>_<arm>_r<rep>.md is missing.
Outcomes are bucketed letter A-D, no letter (reply with none), error (call failed); never folded."""
import json, os, sys, glob, random, math, collections, numpy as np
G = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); R = G + '/runs'; T = G + '/theirs'
THEIR = {'llama3.1:8b': 'llama-3.1-8b', 'ministral-3:8b': 'ministral-8b'}
def load(machine, model, arm, rep):
    p = '%s/%s/%s_%s_r%d.jsonl' % (R, machine, model.replace(':', '-'), arm, rep); out = {}
    if not os.path.exists(p): return None
    for l in open(p, encoding='utf-8'):
        d = json.loads(l); out[d['id']] = d   # the last row per id stands (an error row followed by a reply)
    return out
def cls(d): return 'error' if d.get('err') else ('none' if d.get('pred') is None else 'ABCD'[d['pred']])
if sys.argv[1] == '--sample':
    m, model, arm, rep = sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]); D = load(m, model, arm, rep)
    ids = sorted(D); random.Random(7).shuffle(ids)
    for i in ids[:10]:
        d = D[i]; print('== %s  parsed %s  gold %s  done %s  tokens %s\n%s\n' % (i, cls(d), 'ABCD'[d['gold']], d.get('done_reason'), d.get('eval_count'), (d.get('raw') or d.get('err') or '(reply text not released; parsed letter and reason only)')[:1500]))
    sys.exit()
def wil(k, n, z=1.96):
    if n == 0: return (float('nan'),) * 2
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)); return (c - h) / d, (c + h) / d
def readok(m, model, arm, rep): return os.path.exists('%s/READ_%s_%s_%s_r%d.md' % (R, m, model.replace(':', '-'), arm, rep))
his = collections.defaultdict(dict)
for l in open(T + '/predictions/scenario_a.jsonl'):
    d = json.loads(l)
    if d['model'] in THEIR.values() and d['mode'] == 'blind': his[(d['model'], 'B')][d['id']] = d
for l in open(T + '/predictions/small_models.jsonl'):
    d = json.loads(l)
    if d['model'] in THEIR.values() and d['mode'] == 'full': his[(d['model'], 'F')][d['id']] = d
hcls = lambda d: 'none' if d['pred'] is None else 'ABCD'[d['pred']]
def flips(A, B):
    ids = sorted(set(A) & set(B)); c = collections.Counter((cls(A[i]), cls(B[i])) for i in ids); ch = sum(v for (a, b), v in c.items() if a != b)
    return ch, len(ids), c
def habit_excess(D, ids, seed=20261030, Bn=2000):
    a = np.array([(D[i]['pred'], D[i]['gold']) for i in ids if not D[i].get('err') and D[i].get('pred') is not None])
    if len(a) == 0: return None
    p, g = a[:, 0], a[:, 1]
    def st(p, g): acc = (p == g).mean(-1); h = sum((p == j).mean(-1) * (g == j).mean(-1) for j in range(4)); return acc, h, acc - h
    acc, h, ex = st(p, g); i = np.random.default_rng(seed).integers(0, len(a), size=(Bn, len(a))); lo, hi = np.percentile(st(p[i], g[i])[2], [2.5, 97.5])
    return dict(n=len(a), acc=acc, h=h, ex=ex, lo=lo, hi=hi, shares=[(p == j).mean() for j in range(4)])
for model in THEIR:
    for arm in ('B', 'F'):
        print('\n######## %s arm %s' % (model, arm)); runs = {}
        for m in ('armature', 'mac'):
            for rep in (1, 2):
                D = load(m, model, arm, rep)
                if D is None: continue
                if not readok(m, model, arm, rep): print('  %s r%d: %d rows, held: no read-in-full note yet' % (m, rep, len(D))); continue
                runs[(m, rep)] = D
        for m in ('armature', 'mac'):   # R1 repeat floor
            if (m, 1) in runs and (m, 2) in runs:
                ch, n, c = flips(runs[(m, 1)], runs[(m, 2)]); print('  R1 %s: %d of %d items change class between repeats  %s' % (m, ch, n, dict((k, v) for k, v in c.items() if k[0] != k[1])))
        if ('armature', 1) in runs and ('mac', 1) in runs:   # R2 machine floor
            ch, n, c = flips(runs[('armature', 1)], runs[('mac', 1)]); print('  R2 armature r1 vs mac r1: %d of %d items change class  %s' % (ch, n, dict((k, v) for k, v in c.items() if k[0] != k[1])))
        H = his[(THEIR[model], arm)]
        for (m, rep), D in sorted(runs.items()):
            ids = sorted(D); oc = collections.Counter(cls(D[i]) for i in ids); n = len(ids)
            print('  %s r%d: n %d | A %d B %d C %d D %d | no letter %d | error %d' % (m, rep, n, oc['A'], oc['B'], oc['C'], oc['D'], oc['none'], oc['error']))
            nl = oc['none'] + oc['error']; print('    R4 no letter or error %d of %d = %.3f [%.3f, %.3f]' % (nl, n, nl / n, *wil(nl, n)))
            import re as _re   # Addendum 3: no-letter replies by reason, his parser unchanged
            why = collections.Counter('error' if D[i].get('err') else (D[i].get('nonletter') or 'refusal or other text') for i in ids if cls(D[i]) in ('none', 'error'))   # 30 Oct fix: a Cyrillic letter followed by option text counts as a letter (read in full, F arm)
            print('    R4 by reason: %s' % dict(why))
            for grp in (('accepted', 'rejected') if arm == 'F' else ('accepted',)):
                gi = [i for i in ids if D[i]['grp'] == grp]; he = habit_excess(D, gi)
                if he: print('    R3 %s: parsed %d | shares %s | accuracy %.3f [%.3f, %.3f] | habit %.4f | excess %+.4f [%+.4f, %+.4f]' % (grp, he['n'], ' '.join('%.2f' % s for s in he['shares']), he['acc'], *wil(round(he['acc'] * he['n']), he['n']), he['h'], he['ex'], he['lo'], he['hi']))
            hi_ = [i for i in ids if i in H]; c6 = collections.Counter((hcls(H[i]), cls(D[i])) for i in hi_)
            same = sum(v for (a, b), v in c6.items() if a == b); print('    R6 his Bedrock letter vs ours on %d shared items: same %d, changed %d  %s' % (len(hi_), same, len(hi_) - same, dict(sorted(((k, v) for k, v in c6.items() if k[0] != k[1]), key=lambda x: -x[1])[:8])))
