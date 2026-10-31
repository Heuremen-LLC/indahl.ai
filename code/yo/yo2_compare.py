"""yo2_compare.py YO_FILE NULL_FILE... -- PLAN_YO_V2 rule: YO minus each null, per job, paired bootstrap over TEST records
(items of one record move together), 2,000 resamples, seed 31, 95 %. ABOVE / BELOW / CONSISTENT (inside [-0.02, +0.02]) / CANNOT_TELL."""
import json, sys, random, collections
def load(f): return {r['id']: r for r in map(json.loads, open(f))}
Y = load(sys.argv[1])
for nf in sys.argv[2:]:
    N = load(nf)
    for j in 'AC':
        ids = [i for i in Y if Y[i]['job'] == j and i in N and N[i]['job'] == j and (N[i]['pred'] is not None or j == 'A')]
        if not ids or (j == 'C' and all(N[i]['out'] == '' for i in ids)) or (j == 'A' and all(N[i]['out'] == '' for i in ids)): continue
        by = collections.defaultdict(list)
        for i in ids: by[Y[i]['record']].append(Y[i]['score'] - N[i]['score'])
        recs = sorted(by); pt = sum(sum(by[r]) for r in recs) / sum(len(by[r]) for r in recs); rng = random.Random(31); bs = []
        for _ in range(2000):
            s = [recs[rng.randrange(len(recs))] for _ in recs]; bs.append(sum(sum(by[r]) for r in s) / sum(len(by[r]) for r in s))
        bs.sort(); lo, hi = bs[49], bs[1949]
        oc = 'ABOVE' if lo > 0 else 'BELOW' if hi < 0 else 'CONSISTENT' if (lo >= -0.02 and hi <= 0.02) else 'CANNOT_TELL'
        print(f'{sys.argv[1]} minus {nf} job {j}: {pt:+.3f} [{lo:+.3f}, {hi:+.3f}] over {len(ids)} items in {len(recs)} records -> {oc}')
