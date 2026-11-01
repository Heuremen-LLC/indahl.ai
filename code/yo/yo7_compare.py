"""yo7_compare.py -- PLAN_YO_V7 readings (PLAN_YO_V6 readings, unchanged, for v7 = seed 51 and v7b = seed 52; FUTURE7). R6a share of qubits flagged in young previous-day items (none stale); R6b in young-with-stale items,
the share of young qubits flagged (false flags) and the share of stale qubits found; R6c stale qubits found in same-date items older than 24 h;
all on TEST6. R1 to R4 on TEST4 (yo4_compare.R, unchanged). R7 on FUTURE7, reported only. Each seed (v7 = 51, v7b = 52) minus YO v4, paired
bootstrap over records (TEST6 records for R6, TEST4 records for R1 to R4), 2,000 resamples, seed 41, 95 %; four outcomes, margin 0.02; the rule."""
import json, random, collections, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import yo4_compare as C4
T6 = {json.loads(l)['id']: json.loads(l) for l in open(H + '/data6/test_items.jsonl')}
def load6(s, n): return {json.loads(l)['id']: json.loads(l) for l in open(H + f'/eval6_{s}_{n}.jsonl')}
def flagged(ev, iid):
    try: o = ev[iid]['out']; return set(int(x) for x in json.loads(o[o.index('{'):o.rindex('}') + 1]).get('stale', []))
    except Exception: return set()
def shown(iid): return set(int(l[1:l.index(':')]) for l in T6[iid]['prompt'].splitlines() if l.startswith('q') and ':' in l)
def truth(iid): return set(json.loads(T6[iid]['answer'])['stale'])
YP = lambda i: '|yprev' in i; YS = lambda i: '|ystale' in i; SO = lambda i: '|sdold' in i
def R6(ev, ids=None):
    ids = ids or list(T6); yp = [i for i in ids if YP(i)]; ys = [i for i in ids if YS(i)]; so = [i for i in ids if SO(i)]
    a_n = sum(len(shown(i)) for i in yp); a_f = sum(len(flagged(ev, i) & shown(i)) for i in yp)
    by = sum(len(shown(i) - truth(i)) for i in ys); bf = sum(len((flagged(ev, i) & shown(i)) - truth(i)) for i in ys)
    bs = sum(len(truth(i)) for i in ys); bfs = sum(len(flagged(ev, i) & truth(i)) for i in ys)
    c_n = sum(len(truth(i)) for i in so); c_f = sum(len(flagged(ev, i) & truth(i)) for i in so)
    return dict(R6a=a_f / max(1, a_n), R6a_n=a_n, R6b_false=bf / max(1, by), R6b_young_n=by, R6b_found=bfs / max(1, bs), R6b_stale_n=bs, R6c=c_f / max(1, c_n), R6c_n=c_n)
def boot(f, recs, rng):
    v = f(recs); bs = sorted(f([recs[rng.randrange(len(recs))] for _ in recs]) for _ in range(2000)); return v, bs[49], bs[1949]
if __name__ == '__main__':
    S4 = {n: C4.load(n) for n in ('yo_v4', 'yo_v7', 'yo_v7b')}
    S6 = {n: load6('test6', n) for n in ('yo_v4', 'yo_v7', 'yo_v7b', 'nothing', 'all', 'daterule')}
    for n in ('yo_v4', 'yo_v7', 'yo_v7b'): print('TEST4', n, {k: round(x, 3) if isinstance(x, float) else x for k, x in C4.R(S4[n]).items()})
    for n in S6: print('TEST6', n, {k: round(x, 3) if isinstance(x, float) else x for k, x in R6(S6[n]).items()})
    if os.path.exists(H + '/data7/future_items.jsonl'):
        for n in ('yo_v4', 'yo_v7', 'yo_v7b'):
            e = load6('future7', n); print('FUTURE7', n, 'n', len(e), 'exact', sum(r['score'] == 1.0 for r in e.values()))
    by4 = collections.defaultdict(list)
    for i, it in C4.items.items(): by4[it['record']].append(i)
    by6 = collections.defaultdict(list)
    for i, it in T6.items(): by6[it['record']].append(i)
    r4, r6 = sorted(by4), sorted(by6); passes = {}
    for s in ('yo_v7', 'yo_v7b'):
        res = {}; rng = random.Random(41)
        for k in ('R1', 'R2', 'R3', 'R4'):
            v, lo, hi = boot(lambda Rs: (lambda ids: C4.R(S4[s], ids)[k] - C4.R(S4['yo_v4'], ids)[k])([i for r in Rs for i in by4[r]]), r4, rng)
            res[k] = C4.outcome(lo, hi); print(f'{k}, {s} minus yo_v4: {v:+.3f} [{lo:+.3f}, {hi:+.3f}] -> {res[k]}')
        for k in ('R6a', 'R6b_false', 'R6b_found', 'R6c'):
            v, lo, hi = boot(lambda Rs: (lambda ids: R6(S6[s], ids)[k] - R6(S6['yo_v4'], ids)[k])([i for r in Rs for i in by6[r]]), r6, rng)
            res[k] = C4.outcome(lo, hi); print(f'{k}, {s} minus yo_v4: {v:+.3f} [{lo:+.3f}, {hi:+.3f}] -> {res[k]}')
        passes[s] = (res['R6c'] == 'ABOVE' and res['R6a'] != 'ABOVE' and res['R6b_false'] != 'ABOVE' and res['R6b_found'] != 'BELOW'
                     and all(res[k] != 'BELOW' for k in ('R1', 'R2', 'R3', 'R4')))
        print(f'{s} passes the plan rule: {passes[s]}')
    print('PLAN RULE:', 'YO v7 (seed 51) replaces YO v4 as the model at work' if all(passes.values()) else 'YO v4 stays the model at work; YO v7 and v7b are reported as tried')
