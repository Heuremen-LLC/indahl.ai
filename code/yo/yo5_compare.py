"""yo5_compare.py -- PLAN_YO_V5 readings. R1 to R4 on TEST4 (yo4_compare.R, unchanged); R5a same-date recall (older than 24 h), R5b same-date
false flags (younger than 24 h), R5c same-date Job A score, on TEST5; R6 on FUTURE (reported only). Each seed (v5 = seed 47, v5b = seed 48) minus
YO v4, paired bootstrap over records (TEST4 records for R1 to R4, TEST5 records for R5), 2,000 resamples, seed 41, 95 %; four outcomes with a 0.02
margin; the plan's rule (both seeds must pass)."""
import json, random, collections, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import yo4_compare as C4
T5 = {json.loads(l)['id']: json.loads(l) for l in open(H + '/data5/test_items.jsonl')}
def load5(s, n): return {json.loads(l)['id']: json.loads(l) for l in open(H + f'/eval5_{s}_{n}.jsonl')}
def flagged(ev, iid):
    try: o = ev[iid]['out']; return set(int(x) for x in json.loads(o[o.index('{'):o.rindex('}') + 1]).get('stale', []))
    except Exception: return set()
def shown(iid): return [int(l[1:l.index(':')]) for l in T5[iid]['prompt'].splitlines() if l.startswith('q') and ':' in l]
OLD = lambda i: '|sdold' in i; YOUNG = lambda i: '|sdyoung' in i
def R5(ev, ids=None):
    ids = ids or list(T5); o = [i for i in ids if OLD(i)]; y = [i for i in ids if YOUNG(i)]
    st = sum(len(shown(i)) for i in o); fl = sum(len(flagged(ev, i) & set(shown(i))) for i in o)
    ny = sum(len(shown(i)) for i in y); fy = sum(len(flagged(ev, i) & set(shown(i))) for i in y)
    return dict(R5a=fl / max(1, st), R5a_n=st, R5b=fy / max(1, ny), R5b_n=ny, R5c=sum(ev[i]['score'] for i in ids) / max(1, len(ids)))
def bands(ev):
    out = {}
    for lo, hi in ((24, 28), (28, 36), (36, 48), (48, 1e9)):
        o = [i for i in T5 if OLD(i) and lo <= T5[i]['age_h'] < hi]; st = sum(len(shown(i)) for i in o)
        out[f'{lo}-{hi if hi < 1e9 else "up"} h'] = (round(sum(len(flagged(ev, i) & set(shown(i))) for i in o) / max(1, st), 3), st)
    return out
def boot(f, recs, rng):
    v = f(recs); bs = sorted(f([recs[rng.randrange(len(recs))] for _ in recs]) for _ in range(2000)); return v, bs[49], bs[1949]
if __name__ == '__main__':
    S4 = {n: C4.load(n) for n in ('yo_v4', 'yo_v5', 'yo_v5b')}
    S5 = {n: load5('test5', n) for n in ('yo_v4', 'yo_v5', 'yo_v5b', 'nothing', 'all', 'daterule')}
    for n in ('yo_v4', 'yo_v5', 'yo_v5b'): print('TEST4', n, {k: round(x, 3) if isinstance(x, float) else x for k, x in C4.R(S4[n]).items()})
    for n in S5: print('TEST5', n, {k: round(x, 3) if isinstance(x, float) else x for k, x in R5(S5[n]).items()})
    for n in ('yo_v4', 'yo_v5', 'yo_v5b'): print('TEST5 R5a by age band', n, bands(S5[n]))
    if os.path.exists(H + '/data5/future_items.jsonl'):
        for n in ('yo_v4', 'yo_v5', 'yo_v5b'):
            e = load5('future', n); print('FUTURE', n, 'n', len(e), 'exact', sum(r['score'] == 1.0 for r in e.values()), 'mean', round(sum(r['score'] for r in e.values()) / max(1, len(e)), 3))
    by4 = collections.defaultdict(list)
    for i, it in C4.items.items(): by4[it['record']].append(i)
    by5 = collections.defaultdict(list)
    for i, it in T5.items(): by5[it['record']].append(i)
    r4, r5 = sorted(by4), sorted(by5); passes = {}
    for s in ('yo_v5', 'yo_v5b'):
        res = {}; rng = random.Random(41)
        for k in ('R1', 'R2', 'R3', 'R4'):
            v, lo, hi = boot(lambda Rs: (lambda ids: C4.R(S4[s], ids)[k] - C4.R(S4['yo_v4'], ids)[k])([i for r in Rs for i in by4[r]]), r4, rng)
            res[k] = C4.outcome(lo, hi); print(f'{k}, {s} minus yo_v4: {v:+.3f} [{lo:+.3f}, {hi:+.3f}] -> {res[k]}')
        for k in ('R5a', 'R5b', 'R5c'):
            v, lo, hi = boot(lambda Rs: (lambda ids: R5(S5[s], ids)[k] - R5(S5['yo_v4'], ids)[k])([i for r in Rs for i in by5[r]]), r5, rng)
            res[k] = C4.outcome(lo, hi); print(f'{k}, {s} minus yo_v4: {v:+.3f} [{lo:+.3f}, {hi:+.3f}] -> {res[k]}')
        passes[s] = res['R5a'] == 'ABOVE' and res['R5b'] != 'ABOVE' and all(res[k] != 'BELOW' for k in ('R1', 'R2', 'R3', 'R4'))
        print(f'{s} passes the plan rule: {passes[s]}')
    print('PLAN RULE:', 'YO v5 (seed 47) replaces YO v4 as the model at work' if all(passes.values()) else 'YO v4 stays the model at work; YO v5 and v5b are reported as tried')
