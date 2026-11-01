"""yo5_counts.py -- defined after the data (1 Nov 2026, after yo5_compare.py was read): item and qubit counts behind the YO v5 readings, per model.
TEST4 Job A: false flags (flagged, not stale) and misses (stale, not flagged); TEST4 Job C: wrong verdicts, forced verdicts on CANNOT_TELL items;
TEST5: missed stale qubits in the older same-date items, false flags in the younger; item flips against YO v4 (exact in one, not the other)."""
import json, os
H = os.path.dirname(os.path.abspath(__file__))
T4 = {json.loads(l)['id']: json.loads(l) for l in open(H + '/data4/test_items.jsonl')}; T5 = {json.loads(l)['id']: json.loads(l) for l in open(H + '/data5/test_items.jsonl')}
def ev(f): return {json.loads(l)['id']: json.loads(l) for l in open(H + '/' + f)}
def flags(r):
    try: o = r['out']; return set(int(x) for x in json.loads(o[o.index('{'):o.rindex('}') + 1]).get('stale', []))
    except Exception: return set()
def shown(it): return set(int(l[1:l.index(':')]) for l in it['prompt'].splitlines() if l.startswith('q') and ':' in l)
def counts(e4, e5):
    ff = ms = 0
    for i, it in T4.items():
        if it['job'] != 'A': continue
        t = set(json.loads(it['answer'])['stale']); f = flags(e4[i]) & shown(it); ff += len(f - t); ms += len(t - f)
    cw = sum(1 for i, it in T4.items() if it['job'] == 'C' and e4[i]['pred'] != it['answer'])
    fv = sum(1 for i, it in T4.items() if it['job'] == 'C' and it['answer'] == 'CANNOT_TELL' and e4[i]['pred'] != 'CANNOT_TELL')
    m5 = sum(len(shown(it) - flags(e5[i])) for i, it in T5.items() if '|sdold' in i); f5 = sum(len(flags(e5[i]) & shown(it)) for i, it in T5.items() if '|sdyoung' in i)
    return dict(test4_false_flags=ff, test4_missed=ms, test4_C_wrong=cw, test4_forced=fv, test5_missed=m5, test5_false_flags=f5)
E = {m: (ev(f'eval4_yo_{m}.jsonl'), ev(f'eval5_test5_yo_{m}.jsonl')) for m in ('v4', 'v5', 'v5b')}
for m, (a, b) in E.items(): print(m, counts(a, b))
for m in ('v5', 'v5b'):
    for name, T, k in (('TEST4 Job A', T4, 0), ('TEST4 Job C', T4, 0), ('TEST5', T5, 1)):
        job = 'C' if 'Job C' in name else 'A'; ids = [i for i, it in T.items() if it['job'] == job]
        up = sum(1 for i in ids if E[m][k][i]['score'] == 1.0 and E['v4'][k][i]['score'] < 1.0); dn = sum(1 for i in ids if E[m][k][i]['score'] < 1.0 and E['v4'][k][i]['score'] == 1.0)
        print(f'{m} vs v4, {name}: right where v4 was not {up}, wrong where v4 was right {dn}, of {len(ids)}')
