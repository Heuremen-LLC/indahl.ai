"""yo4_compare.py -- PLAN_YO_V4 readings on TEST4: R1 whole-window recall (qubits stale by 24 to 48 h inside the whole-window items), R2 Job A
score on the items drawn as v2 draws them, R3 stale precision over all Job A items, R4 Job C accuracy, forced-verdict rate and wrong
CANNOT_TELL answers. YO v4 minus YO v2 (R1-R4), YO v4 minus YO v3 (R1, R2); paired bootstrap over TEST4 records, 2,000 resamples, seed 41, 95 %;
four outcomes with a 0.02 margin; the plan's rule."""
import json, re, random, collections, datetime as dt, os
H = os.path.dirname(os.path.abspath(__file__)); UTC = dt.timezone.utc
items = {json.loads(l)['id']: json.loads(l) for l in open(H + '/data4/test_items.jsonl')}
def load(n): return {json.loads(l)['id']: json.loads(l) for l in open(H + f'/eval4_{n}.jsonl')}
def P(s): return dt.datetime.strptime(s, '%Y-%m-%d %H:%M').replace(tzinfo=UTC)
WIN = lambda i: '|win' in i; GEN = lambda i: items[i]['job'] == 'A' and not WIN(i)
def qubits(iid, ev):   # per qubit: (stale, in 24-48 h band, flagged)
    it = items[iid]; S = P(re.search(r'stamp (\d{4}-\d\d-\d\d \d\d:\d\d) UTC', it['prompt']).group(1)); truth = set(json.loads(it['answer'])['stale'])
    try: o = ev[iid]['out']; ys = set(int(x) for x in json.loads(o[o.index('{'):o.rindex('}') + 1]).get('stale', []))
    except Exception: ys = set()
    out = []
    for line in it['prompt'].splitlines():
        m = re.match(r'q(\d+): (.*)', line)
        if not m: continue
        q = int(m.group(1)); g = max((S - P(d)).total_seconds() / 3600 for d in re.findall(r'T[12]=[^ ]+ \((\d{4}-\d\d-\d\d \d\d:\d\d)\)', m.group(2)))
        out.append((q in truth, 24 < g < 48, q in ys))
    return out
def R(ev, ids=None):
    ids = ids or list(items); A = [i for i in ids if items[i]['job'] == 'A']; C = [i for i in ids if items[i]['job'] == 'C']
    w = [x for i in A if WIN(i) for x in qubits(i, ev) if x[0] and x[1]]; qa = [x for i in A for x in qubits(i, ev)]; g = [i for i in A if GEN(i)]
    ct = [i for i in C if items[i]['answer'] == 'CANNOT_TELL']
    return dict(R1=sum(x[2] for x in w) / max(1, len(w)), R1_n=len(w), R2=sum(ev[i]['score'] for i in g) / max(1, len(g)),
                R3=sum(x[0] for x in qa if x[2]) / max(1, sum(x[2] for x in qa)), R4=sum(ev[i]['score'] for i in C) / max(1, len(C)),
                forced=sum(ev[i]['pred'] != 'CANNOT_TELL' for i in ct) / max(1, len(ct)),
                ct_wrong=sum(1 for i in C if ev[i]['pred'] == 'CANNOT_TELL' and items[i]['answer'] != 'CANNOT_TELL'))
def outcome(lo, hi, m=0.02): return 'ABOVE' if lo > 0 else 'BELOW' if hi < 0 else 'CONSISTENT' if (lo >= -m and hi <= m) else 'CANNOT_TELL'
if __name__ == '__main__':
    ev = {n: load(n) for n in ('yo_v4', 'yo_v3', 'yo_v2', 'nothing', 'daterule', 'all')}
    for n in ev: print(n, {k: round(x, 3) if isinstance(x, float) else x for k, x in R(ev[n]).items()})
    byrec = collections.defaultdict(list)
    for i, it in items.items(): byrec[it['record']].append(i)
    recs = sorted(byrec); rng = random.Random(41); res = {}
    def d(a, b, k): return lambda Rs: (lambda ids: R(ev[a], ids)[k] - R(ev[b], ids)[k])([i for r in Rs for i in byrec[r]])
    for a, b, k in (('yo_v4', 'yo_v2', 'R1'), ('yo_v4', 'yo_v2', 'R2'), ('yo_v4', 'yo_v2', 'R3'), ('yo_v4', 'yo_v2', 'R4'), ('yo_v4', 'yo_v3', 'R1'), ('yo_v4', 'yo_v3', 'R2')):
        f = d(a, b, k); v = f(recs); bs = sorted(f([recs[rng.randrange(len(recs))] for _ in recs]) for _ in range(2000)); lo, hi = bs[49], bs[1949]
        res[(a, b, k)] = outcome(lo, hi); print(f'{k}, {a} minus {b}: {v:+.3f} [{lo:+.3f}, {hi:+.3f}] -> {res[(a, b, k)]}')
    ok = res[('yo_v4', 'yo_v2', 'R1')] == 'ABOVE' and all(res[('yo_v4', 'yo_v2', k)] != 'BELOW' for k in ('R2', 'R3', 'R4'))
    print('PLAN RULE:', 'YO v4 replaces YO v2 as the model at work' if ok else 'YO v4 does not replace YO v2; YO v2 stays the model at work')
