"""yo3_compare.py -- PLAN_YO_V3 readings on TEST3: R1 Job A score, R2 qubit stale recall/precision and recall in the 24-48 h band, R3 Job C
accuracy and forced-verdict rate; YO v3 minus YO v2 (R1, R3, band recall) and YO v3 minus the date rule (R1), paired bootstrap over TEST3
records, 2,000 resamples, seed 31, 95 %; four outcomes with a 0.02 margin; the plan's REFINES rule."""
import json, re, random, collections, datetime as dt, sys, os
H = os.path.dirname(os.path.abspath(__file__)); UTC = dt.timezone.utc
items = {json.loads(l)['id']: json.loads(l) for l in open(H + '/data3/test_items.jsonl')}
def load(n): return {json.loads(l)['id']: json.loads(l) for l in open(H + f'/eval3_{n}.jsonl')}
def P(s): return dt.datetime.strptime(s, '%Y-%m-%d %H:%M').replace(tzinfo=UTC)
def qubits(iid, ev):   # per stale qubit: (record, in 24-48 h band, flagged); and flags on non-stale qubits
    it = items[iid]; S = P(re.search(r'stamp (\d{4}-\d\d-\d\d \d\d:\d\d) UTC', it['prompt']).group(1)); truth = set(json.loads(it['answer'])['stale'])
    try: ys = set(int(x) for x in json.loads(ev[iid]['out'][ev[iid]['out'].index('{'):ev[iid]['out'].rindex('}') + 1]).get('stale', []))
    except Exception: ys = set()
    out = []
    for line in it['prompt'].splitlines():
        m = re.match(r'q(\d+): (.*)', line)
        if not m: continue
        q = int(m.group(1)); g = max((S - P(d)).total_seconds() / 3600 for d in re.findall(r'T[12]=[^ ]+ \((\d{4}-\d\d-\d\d \d\d:\d\d)\)', m.group(2)))
        out.append((q in truth, 24 < g < 48, q in ys))
    return out
def readings(ev):
    A = [i for i in items if items[i]['job'] == 'A']; C = [i for i in items if items[i]['job'] == 'C']
    qs = [x for i in A for x in qubits(i, ev)]; st = [x for x in qs if x[0]]; band = [x for x in st if x[1]]
    ct = [i for i in C if items[i]['answer'] == 'CANNOT_TELL']
    return dict(A=sum(ev[i]['score'] for i in A) / len(A), recall=sum(x[2] for x in st) / len(st), precision=sum(x[0] for x in qs if x[2]) / max(1, sum(x[2] for x in qs)),
                band_recall=sum(x[2] for x in band) / len(band), band_n=len(band), C=sum(ev[i]['score'] for i in C) / len(C), forced=sum(ev[i]['pred'] != 'CANNOT_TELL' for i in ct) / len(ct))
def outcome(lo, hi, m=0.02): return 'ABOVE' if lo > 0 else 'BELOW' if hi < 0 else 'CONSISTENT' if (lo >= -m and hi <= m) else 'CANNOT_TELL'
def boot(f, recs, rng):
    v = f(recs); bs = sorted(f([recs[rng.randrange(len(recs))] for _ in recs]) for _ in range(2000)); return v, bs[49], bs[1949]
if __name__ == '__main__':
    v3, v2, dr = load('yo_v3'), load('yo_v2'), load('daterule')
    for n, ev in (('YO v3', v3), ('YO v2', v2)): print(n, {k: round(x, 3) if isinstance(x, float) else x for k, x in readings(ev).items()})
    byrec = collections.defaultdict(list)
    for i, it in items.items(): byrec[it['record']].append(i)
    recs = sorted(byrec); rng = random.Random(31); res = {}
    def dA(a, b): return lambda R: (lambda ids: sum(a[i]['score'] - b[i]['score'] for i in ids) / max(1, len(ids)))([i for r in R for i in byrec[r] if items[i]['job'] == 'A'])
    def dC(R): ids = [i for r in R for i in byrec[r] if items[i]['job'] == 'C']; return sum(v3[i]['score'] - v2[i]['score'] for i in ids) / max(1, len(ids))
    def dband(R):
        h3 = h2 = n = 0
        for r in R:
            for i in byrec[r]:
                if items[i]['job'] != 'A': continue
                for (s, b, f3), (_, _, f2) in zip(qubits(i, v3), qubits(i, v2)):
                    if s and b: n += 1; h3 += f3; h2 += f2
        return (h3 - h2) / max(1, n)
    for name, f in (('band recall, v3 minus v2', dband), ('Job A score, v3 minus v2', dA(v3, v2)), ('Job C accuracy, v3 minus v2', dC), ('Job A score, v3 minus date rule', dA(v3, dr))):
        v, lo, hi = boot(f, recs, rng); res[name] = outcome(lo, hi); print(f'{name}: {v:+.3f} [{lo:+.3f}, {hi:+.3f}] -> {res[name]}')
    ref = res['band recall, v3 minus v2'] == 'ABOVE' and res['Job A score, v3 minus v2'] != 'BELOW' and res['Job C accuracy, v3 minus v2'] != 'BELOW'
    print('PLAN RULE:', 'v3 REFINES YO' if ref else 'v3 does not refine YO; YO v2 stays the working model')
