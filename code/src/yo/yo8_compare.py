"""yo8_compare.py -- PLAN_YO_V8 readings. R8 on TEST8C: share of border verdicts exact (reply label equals the code's answer).
R6a, R6b, R6c on TEST6 and R1 to R4 on TEST4 as PLAN_YO_V7 (yo7s_compare.R6, yo4_compare.R, unchanged). Each seed (v8 = 56, v8b = 57,
v8c = 58) minus YO v7 seed 51, paired bootstrap over records, 2,000 resamples, seed 41, 95 %, four outcomes, margin 0.02.
Rule: a seed passes if R8 ABOVE, R6a not ABOVE, R6b false not ABOVE, R6b found not BELOW, R6c not BELOW, R1 to R4 not BELOW.
YO v8 seed 56 replaces YO v7 only if all three pass. Also reported, outside the rule: R8 for YO v4 and the nulls, R8 by kind.
Written after the replies were read in full (structure plus 10 per kind) and before any score was read."""
import json, random, collections, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import yo4_compare as C4, yo7s_compare as C7
T8 = {json.loads(l)['id']: json.loads(l) for l in open(H + '/data8/test8c_items.jsonl')}
def load8(n): return {json.loads(l)['id']: json.loads(l) for l in open(H + f'/eval6_test8c_{n}.jsonl')}
def ans(i):
    a = T8[i]['answer']
    try: a = json.loads(a)
    except Exception: pass
    return (a.get('verdict') if isinstance(a, dict) else a).strip()
def exact(ev, i): return 1 if i in ev and str(ev[i]['out']).strip() == ans(i) else 0
def R8(ev, ids=None, kind=None):
    ids = [i for i in (ids or list(T8)) if kind is None or T8[i]['kind'] == kind]
    return sum(exact(ev, i) for i in ids) / max(1, len(ids))
SEEDS = ('yo_v8', 'yo_v8b', 'yo_v8c'); BASE = 'yo_v7'
if __name__ == '__main__':
    S8 = {n: load8(n) for n in ('yo_v7', 'yo_v4', 'consistent', 'binary', 'oracle') + SEEDS}
    for n, ev in S8.items():
        agree = sum((exact(ev, i) == 1) == (ev[i]['score'] == 1.0) for i in ev)
        print('TEST8C', n, 'n', len(ev), 'R8', round(R8(ev), 3), 'by kind', {k: round(R8(ev, kind=k), 3) for k in ('margin-in', 'margin-out', 'ref-past', 'ref-short')}, 'scorer agrees on', agree)
    S4 = {n: C4.load(n) for n in (BASE,) + SEEDS}
    S6 = {n: C7.load6('test6', n) for n in (BASE,) + SEEDS}
    for n in S4: print('TEST4', n, {k: round(x, 3) if isinstance(x, float) else x for k, x in C4.R(S4[n]).items()})
    for n in S6: print('TEST6', n, {k: round(x, 3) if isinstance(x, float) else x for k, x in C7.R6(S6[n]).items()})
    by4 = collections.defaultdict(list); [by4[it['record']].append(i) for i, it in C4.items.items()]
    by6 = collections.defaultdict(list); [by6[it['record']].append(i) for i, it in C7.T6.items()]
    by8 = collections.defaultdict(list); [by8[it['record']].append(i) for i, it in T8.items()]
    r4, r6, r8 = sorted(by4), sorted(by6), sorted(by8); passes = {}
    for s in SEEDS:
        res = {}; rng = random.Random(41)
        v, lo, hi = C7.boot(lambda Rs: (lambda ids: R8(S8[s], ids) - R8(S8[BASE], ids))([i for r in Rs for i in by8[r]]), r8, rng)
        res['R8'] = C4.outcome(lo, hi); print(f'R8, {s} minus {BASE}: {v:+.3f} [{lo:+.3f}, {hi:+.3f}] -> {res["R8"]}')
        for k in ('R1', 'R2', 'R3', 'R4'):
            v, lo, hi = C7.boot(lambda Rs: (lambda ids: C4.R(S4[s], ids)[k] - C4.R(S4[BASE], ids)[k])([i for r in Rs for i in by4[r]]), r4, rng)
            res[k] = C4.outcome(lo, hi); print(f'{k}, {s} minus {BASE}: {v:+.3f} [{lo:+.3f}, {hi:+.3f}] -> {res[k]}')
        for k in ('R6a', 'R6b_false', 'R6b_found', 'R6c'):
            v, lo, hi = C7.boot(lambda Rs: (lambda ids: C7.R6(S6[s], ids)[k] - C7.R6(S6[BASE], ids)[k])([i for r in Rs for i in by6[r]]), r6, rng)
            res[k] = C4.outcome(lo, hi); print(f'{k}, {s} minus {BASE}: {v:+.3f} [{lo:+.3f}, {hi:+.3f}] -> {res[k]}')
        passes[s] = (res['R8'] == 'ABOVE' and res['R6a'] != 'ABOVE' and res['R6b_false'] != 'ABOVE' and res['R6b_found'] != 'BELOW'
                     and res['R6c'] != 'BELOW' and all(res[k] != 'BELOW' for k in ('R1', 'R2', 'R3', 'R4')))
        print(f'{s} passes the plan rule: {passes[s]}')
    print('PLAN RULE (V8):', 'YO v8 (seed 56) replaces YO v7 as the model at work' if all(passes.values()) else 'YO v7 stays the model at work; every v8 seed is reported as tried')
