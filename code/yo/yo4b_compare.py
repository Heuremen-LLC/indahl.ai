"""yo4b_compare.py -- PLAN_YO_V4B readings: S1 R1-R4 for v4b, S2 the seed gap v4b minus v4 (paired bootstrap over TEST4 records, 2,000
resamples, seed 51, 95 %, four outcomes with a 0.02 margin), S3 item flips between the seeds, S4 v4b minus v2 on R1."""
import sys, json, random, collections; sys.path.insert(0, '/Users/heuremen/bones-forge/yo')
import yo4_compare as Y
ev = {n: Y.load(n) for n in ('yo_v4b', 'yo_v4', 'yo_v2')}
for n in ev: print(n, {k: round(x, 3) if isinstance(x, float) else x for k, x in Y.R(ev[n]).items()})
byrec = collections.defaultdict(list)
for i, it in Y.items.items(): byrec[it['record']].append(i)
recs = sorted(byrec); rng = random.Random(51)
def d(a, b, k): return lambda Rs: (lambda ids: Y.R(ev[a], ids)[k] - Y.R(ev[b], ids)[k])([i for r in Rs for i in byrec[r]])
for a, b, k in (('yo_v4b', 'yo_v4', 'R1'), ('yo_v4b', 'yo_v4', 'R2'), ('yo_v4b', 'yo_v4', 'R4'), ('yo_v4b', 'yo_v2', 'R1')):
    f = d(a, b, k); v = f(recs); bs = sorted(f([recs[rng.randrange(len(recs))] for _ in recs]) for _ in range(2000)); lo, hi = bs[49], bs[1949]
    print(f'{k}, {a} minus {b}: {v:+.3f} [{lo:+.3f}, {hi:+.3f}] -> {Y.outcome(lo, hi)}')
def stale(n, i):
    o = ev[n][i]['out']
    try: return tuple(sorted(int(x) for x in json.loads(o[o.index('{'):o.rindex('}') + 1]).get('stale', [])))
    except Exception: return None
A = [i for i in Y.items if Y.items[i]['job'] == 'A']; C = [i for i in Y.items if Y.items[i]['job'] == 'C']
truth = {i: tuple(sorted(json.loads(Y.items[i]['answer'])['stale'])) for i in A}
diffA = [i for i in A if stale('yo_v4b', i) != stale('yo_v4', i)]
print(f'S3 Job A items whose stale list differs between the seeds: {len(diffA)} of {len(A)} (v4b exact where v4 is not: {sum(stale("yo_v4b", i) == truth[i] for i in diffA)}, v4 exact where v4b is not: {sum(stale("yo_v4", i) == truth[i] for i in diffA)})')
diffC = [i for i in C if ev['yo_v4b'][i]['pred'] != ev['yo_v4'][i]['pred']]
print(f'S3 Job C items whose verdict differs: {len(diffC)} of {len(C)} (v4b right: {sum(ev["yo_v4b"][i]["score"] == 1 for i in diffC)}, v4 right: {sum(ev["yo_v4"][i]["score"] == 1 for i in diffC)})')
