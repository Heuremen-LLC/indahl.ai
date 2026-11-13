"""yr_compare.py -- PLAN_YO_READ readings. RD, RL, RQ = share right on TEST per question, per arm. Each seed minus REGEX, paired bootstrap
over TEST papers, 2,000 resamples, seed 41, 95 %, margin 0.02, four outcomes; false YES / false NO per arm; flips against REGEX. The rule.
Written after the replies were read in full (every reply parsed, 10 per question read) and before any score was read."""
import json, random, collections
def load(n): return {json.loads(l)['id']: json.loads(l) for l in open(f'eval_{n}.jsonl')}
items = {json.loads(l)['id']: json.loads(l) for l in open('data/test_items.jsonl')}
A = {n: load(n) for n in ('regex', 'majority', 'base', 'yo_read1', 'yo_read2', 'yo_read3', 'truth')}
Q = ('DATES', 'LINK', 'REQUEST'); papers = sorted({i['paper'] for i in items.values()})
def acc(ev, q, ps):
    ids = [f'{p}|{q}' for p in ps]; return sum(ev[i]['score'] for i in ids) / len(ids)
def outcome(lo, hi, m=0.02): return 'ABOVE' if lo > 0 else 'BELOW' if hi < 0 else 'CONSISTENT' if (lo >= -m and hi <= m) else 'CANNOT_TELL'
for n, ev in A.items():
    fy = {q: sum(ev[f'{p}|{q}']['pred'] == 'YES' and items[f'{p}|{q}']['answer'] == 'NO' for p in papers) for q in Q}
    fn = {q: sum(ev[f'{p}|{q}']['pred'] != 'YES' and items[f'{p}|{q}']['answer'] == 'YES' for p in papers) for q in Q}
    print(n, {q: round(acc(ev, q, papers), 3) for q in Q}, 'false YES', fy, 'false NO or unread', fn)
print('TEST papers', len(papers), 'truth YES counts', {q: sum(items[f'{p}|{q}']['answer'] == 'YES' for p in papers) for q in Q})
passes = {}
for s in ('yo_read1', 'yo_read2', 'yo_read3'):
    rng = random.Random(41); res = {}
    for q in Q:
        f = lambda ps: acc(A[s], q, ps) - acc(A['regex'], q, ps)
        v = f(papers); bs = sorted(f([papers[rng.randrange(len(papers))] for _ in papers]) for _ in range(2000)); lo, hi = bs[49], bs[1949]
        up = sum(A[s][f'{p}|{q}']['score'] > A['regex'][f'{p}|{q}']['score'] for p in papers); dn = sum(A[s][f'{p}|{q}']['score'] < A['regex'][f'{p}|{q}']['score'] for p in papers)
        res[q] = outcome(lo, hi); print(f'{q}, {s} minus regex: {v:+.3f} [{lo:+.3f}, {hi:+.3f}] -> {res[q]} | flips right-only {up}, regex-only {dn}')
    passes[s] = (res['DATES'] == 'ABOVE' or res['LINK'] == 'ABOVE') and all(res[q] != 'BELOW' for q in Q)
    print(f'{s} passes the plan rule: {passes[s]}')
print('PLAN RULE (YO READ):', 'YO Read (seed 61) goes to work as a second reading before QIA notices' if all(passes.values()) else 'YO Read is reported as tried')
