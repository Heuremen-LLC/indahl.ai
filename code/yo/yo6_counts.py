"""yo6_counts.py -- defined after the data (1 Nov 2026, after yo6_compare.py was read): the counts behind every YO v6 reading, per model, so the
post prints numbers of qubits and items, not only shares. TEST6 (R6a, R6b, R6c), TEST4 (R1 to R4, false flags, misses, forced verdicts),
item flips against YO v4, and the FUTURE6 records described. Same parsing as yo6_compare.py and yo4_compare.py."""
import json, os, sys, collections
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import yo4_compare as C4, yo6_compare as C6
M = ('yo_v4', 'yo_v6', 'yo_v6b')
S4 = {n: C4.load(n) for n in M}; S6 = {n: C6.load6('test6', n) for n in M + ('nothing', 'all', 'daterule')}
T6 = C6.T6
def r6counts(ev):
    yp = [i for i in T6 if C6.YP(i)]; ys = [i for i in T6 if C6.YS(i)]; so = [i for i in T6 if C6.SO(i)]
    f = lambda i: C6.flagged(ev, i) & C6.shown(i)
    return dict(R6a=f'{sum(len(f(i)) for i in yp)} of {sum(len(C6.shown(i)) for i in yp)} in {len(yp)} items',
                R6a_items=sum(1 for i in yp if f(i)),
                R6b_false=f'{sum(len(f(i) - C6.truth(i)) for i in ys)} of {sum(len(C6.shown(i) - C6.truth(i)) for i in ys)}',
                R6b_false_items=sum(1 for i in ys if f(i) - C6.truth(i)),
                R6b_found=f'{sum(len(f(i) & C6.truth(i)) for i in ys)} of {sum(len(C6.truth(i)) for i in ys)} in {len(ys)} items',
                R6c=f'{sum(len(f(i) & C6.truth(i)) for i in so)} of {sum(len(C6.truth(i)) for i in so)} in {len(so)} items',
                R6c_items_all_found=f'{sum(1 for i in so if C6.truth(i) <= f(i))} of {len(so)}')
for n in S6: print('TEST6', n, r6counts(S6[n]))
items = C4.items
def flags4(ev, i):
    try: o = ev[i]['out']; return set(int(x) for x in json.loads(o[o.index('{'):o.rindex('}') + 1]).get('stale', []))
    except Exception: return set()
def shown4(i): return set(int(l[1:l.index(':')]) for l in items[i]['prompt'].splitlines() if l.startswith('q') and ':' in l)
for n in M:
    r = C4.R(S4[n]); A = [i for i in items if items[i]['job'] == 'A']; C = [i for i in items if items[i]['job'] == 'C']
    ff = sum(len((flags4(S4[n], i) & shown4(i)) - set(json.loads(items[i]['answer'])['stale'])) for i in A)
    ffi = sum(1 for i in A if (flags4(S4[n], i) & shown4(i)) - set(json.loads(items[i]['answer'])['stale']))
    ms = sum(len(set(json.loads(items[i]['answer'])['stale']) - flags4(S4[n], i)) for i in A)
    ct = [i for i in C if items[i]['answer'] == 'CANNOT_TELL']
    print('TEST4', n, f"R1 {round(r['R1'] * r['R1_n'])} of {r['R1_n']}", f"R2 {r['R2']:.3f}", f"R3 {r['R3']:.4f}",
          f"R4 {sum(S4[n][i]['score'] for i in C):.0f} of {len(C)}", f"forced {sum(S4[n][i]['pred'] != 'CANNOT_TELL' for i in ct)} of {len(ct)}",
          f"ct_wrong {r['ct_wrong']}", f"false flags {ff} (in {ffi} items)", f"missed {ms}")
for n in ('yo_v6', 'yo_v6b'):
    for name, ids, E, B in (('TEST4 audit (Job A)', [i for i in items if items[i]['job'] == 'A'], S4[n], S4['yo_v4']),
                            ('TEST4 verdicts (Job C)', [i for i in items if items[i]['job'] == 'C'], S4[n], S4['yo_v4']),
                            ('TEST6', list(T6), S6[n], S6['yo_v4'])):
        up = sum(1 for i in ids if E[i]['score'] == 1.0 and B[i]['score'] < 1.0); dn = sum(1 for i in ids if E[i]['score'] < 1.0 and B[i]['score'] == 1.0)
        print(f'{n} vs yo_v4, {name}: right where v4 was not {up}, wrong where v4 was right {dn}, of {len(ids)}')
FU = [json.loads(l) for l in open(H + '/data6/future_items.jsonl')]
kinds = collections.Counter('stale' if json.loads(it['answer']).get('stale') else 'zero' if json.loads(it['answer']).get('zero') else 'nothing' for it in FU)
print('FUTURE6 records', len(FU), dict(kinds), 'stamps', min(it.get('stamp', '') for it in FU), 'to', max(it.get('stamp', '') for it in FU))
for n in M:
    e = C6.load6('future6', n); wrong = [i for i, r in e.items() if r['score'] < 1.0]
    print('FUTURE6', n, 'exact', sum(r['score'] == 1.0 for r in e.values()), 'of', len(e), 'not exact:', wrong)
# R3 as counts (flags that are right / all flags, TEST4 audit items), same definition as yo4_compare.R
for n in M:
    A = [i for i in items if items[i]['job'] == 'A']; qa = [x for i in A for x in C4.qubits(i, S4[n])]
    print('TEST4', n, f'R3 {sum(x[0] for x in qa if x[2])} of {sum(x[2] for x in qa)} flags truly stale')
