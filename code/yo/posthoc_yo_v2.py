"""posthoc_yo_v2.py -- the readings of POSTHOC_YO_V2.md (defined after the data): YO's stale recall by gap and two code baselines."""
import json, re, datetime as dt, collections, os
H = os.path.dirname(os.path.abspath(__file__)); UTC = dt.timezone.utc
items = {json.loads(l)['id']: json.loads(l) for l in open(H + '/data2/test_items.jsonl')}; Y = {json.loads(l)['id']: json.loads(l) for l in open(H + '/eval2_yo_v2.jsonl')}
def P(s): return dt.datetime.strptime(s, '%Y-%m-%d %H:%M').replace(tzinfo=UTC)
def f1(p, t):
    p, t = set(p), set(t)
    if not p and not t: return 1.0
    if not p or not t: return 0.0
    k = len(p & t); return 0.0 if k == 0 else 2 * k / (len(p) + len(t))
tp = fp = fn = 0; bins = collections.Counter(); hit = collections.Counter(); z = []; zc = []
for iid, it in items.items():
    if it['job'] != 'A': continue
    S = P(re.search(r'stamp (\d{4}-\d\d-\d\d \d\d:\d\d) UTC', it['prompt']).group(1)); truth = json.loads(it['answer'])
    try: ys = set(int(x) for x in json.loads(Y[iid]['out'][Y[iid]['out'].index('{'):Y[iid]['out'].rindex('}') + 1]).get('stale', []))
    except Exception: ys = set()
    cal2 = []
    for line in it['prompt'].splitlines():
        m = re.match(r'q(\d+): (.*)', line)
        if not m: continue
        q = int(m.group(1)); ds = [P(d) for f, d in re.findall(r'(T1|T2)=[^ ]+ \((\d{4}-\d\d-\d\d \d\d:\d\d)\)', m.group(2))]
        gap = max((S - d).total_seconds() / 3600 for d in ds); st = q in truth['stale']
        if (S.date() - min(ds).date()).days >= 2: cal2.append(q)
        if st:
            b = '24-25' if gap < 25 else '25-30' if gap < 30 else '30-48' if gap < 48 else '48+'; bins[b] += 1; hit[b] += q in ys
        tp += st and q in ys; fp += (not st) and q in ys; fn += st and q not in ys
    z.append((f1([], truth['stale']) + 1.0) / 2); zc.append((f1(cal2, truth['stale']) + 1.0) / 2)
print('stale precision %.3f recall %.3f' % (tp / (tp + fp), tp / (tp + fn)), dict(bins), dict(hit), 'zeros-only %.3f zeros+2cal %.3f' % (sum(z) / len(z), sum(zc) / len(zc)))
