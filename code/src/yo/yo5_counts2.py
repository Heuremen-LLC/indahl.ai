"""yo5_counts2.py -- defined after the data (1 Nov 2026, after the outside referee of the YO v5 post): counts the referee raised, recounted
here with our own code before any of them is printed. Item-level same-date counts, false flags by item and by kind on YO v4's test items,
the FUTURE set described, and how many of TEST4's audit items are young same-date sets."""
import json, os, collections, datetime as dt
H = os.path.dirname(os.path.abspath(__file__))
T4 = {json.loads(l)['id']: json.loads(l) for l in open(H + '/data4/test_items.jsonl')}; T5 = {json.loads(l)['id']: json.loads(l) for l in open(H + '/data5/test_items.jsonl')}
FU = [json.loads(l) for l in open(H + '/data5/future_items.jsonl')]
def ev(f): return {json.loads(l)['id']: json.loads(l) for l in open(H + '/' + f)}
def flags(r):
    try: o = r['out']; return set(int(x) for x in json.loads(o[o.index('{'):o.rindex('}') + 1]).get('stale', []))
    except Exception: return set()
def lines(it):
    out = {}
    for l in it['prompt'].splitlines():
        if l.startswith('q') and ':' in l: out[int(l[1:l.index(':')])] = l
    return out
def stamp(it):
    import re; return dt.datetime.strptime(re.search(r'stamp (\d{4}-\d\d-\d\d \d\d:\d\d) UTC', it['prompt']).group(1), '%Y-%m-%d %H:%M')
def older_date(l):
    import re; ds = re.findall(r'T[12]=[^ ]+ \((\d{4}-\d\d-\d\d \d\d:\d\d)\)', l); return min(dt.datetime.strptime(d, '%Y-%m-%d %H:%M') for d in ds)
L = ['DEFINED AFTER THE DATA (1 Nov 2026, after the outside referee of the YO v5 post).']
E5 = {m: ev(f'eval5_test5_yo_{m}.jsonl') for m in ('v4', 'v5', 'v5b')}; E4 = {m: ev(f'eval4_yo_{m}.jsonl') for m in ('v4', 'v4b', 'v4c', 'v5', 'v5b')}
old = [i for i in T5 if '|sdold' in i]
L.append('TEST5 stale qubits found in older same-date items, out of %d: ' % sum(len(lines(T5[i])) for i in old) + ', '.join(f'{m} {sum(len(set(lines(T5[i])) & flags(E5[m][i])) for i in old)}' for m in E5))
L.append('TEST5 older same-date items with every stale qubit found, out of %d: ' % len(old) + ', '.join(f'{m} {sum(1 for i in old if set(lines(T5[i])) <= flags(E5[m][i]))}' for m in E5))
young4 = []
for i, it in T4.items():
    if it['job'] != 'A': continue
    S = stamp(it); od = collections.Counter(older_date(l) for l in lines(it).values())
    d, n = od.most_common(1)[0]
    if n >= 7 and (S - d).total_seconds() < 86400: young4.append(i)
L.append(f'TEST4 audit items with 7 or 8 of their 8 qubits sharing one older date younger than 24 h: {len(young4)} of {sum(1 for it in T4.values() if it["job"] == "A")}')
for m in E4:
    ff_items = [i for i, it in T4.items() if it['job'] == 'A' and (flags(E4[m][i]) & set(lines(it))) - set(json.loads(it['answer'])['stale'])]
    ff_q = sum(len((flags(E4[m][i]) & set(lines(T4[i]))) - set(json.loads(T4[i]['answer'])['stale'])) for i in ff_items)
    yi = [i for i in ff_items if i in young4]; yq = sum(len((flags(E4[m][i]) & set(lines(T4[i]))) - set(json.loads(T4[i]['answer'])['stale'])) for i in yi)
    L.append(f'{m}: false flags on TEST4 {ff_q} in {len(ff_items)} items; of those, in young same-date items {yq} qubits in {len(yi)} items')
st = [stamp(it) for it in FU]; ws = [len(json.loads(it['answer'])['stale']) for it in FU]; zs = [len(json.loads(it['answer'])['zero']) for it in FU]
L.append(f'FUTURE: {len(FU)} records stamped {min(st):%H:%M} to {max(st):%H:%M} UTC on {min(st):%d %b}; with stale qubits {sum(1 for w in ws if w)} ({sum(ws)} in all, {sum(1 for w in ws if w == 8)} with all 8), with a zero value {sum(1 for z in zs if z)}, with nothing to flag {sum(1 for w, z in zip(ws, zs) if not w and not z)}')
open(H + '/yo5_counts2.text', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
