"""yo4_after_referee.py -- YO v4 readings added after the referee (1 Nov 2026), all defined after the data. Our own recount, not the referee's code."""
import sys, json, re, collections; sys.path.insert(0, '/Users/heuremen/bones-forge/yo')
import yo4_compare as Y
ev = {n: Y.load(n) for n in ('yo_v4', 'yo_v3', 'yo_v2')}
A = [i for i in Y.items if Y.items[i]['job'] == 'A']; C = [i for i in Y.items if Y.items[i]['job'] == 'C']
def flags(n, i):
    o = ev[n][i]['out']
    try: p = json.loads(o[o.index('{'):o.rindex('}') + 1]); return set(int(x) for x in p.get('stale', [])), set(str(x) for x in p.get('zero', []))
    except Exception: return set(), set()
truth = {i: json.loads(Y.items[i]['answer']) for i in A}
print('TEST4 distinct records:', len(set(Y.items[i]['record'] for i in Y.items)), '| whole-window items', sum('|win' in i for i in A))
all8 = [i for i in A if len(truth[i]['stale']) == 8]
print('items with all 8 qubits stale:', len(all8))
for n in ev:
    ex = sum(flags(n, i)[0] == set(truth[i]['stale']) for i in all8); none = sum(not flags(n, i)[0] for i in all8)
    print(f'  {n}: stale list exactly right on {ex} of {len(all8)}, flags nothing on {none}')
gen = [i for i in A if Y.GEN(i)]; st = sum(len(truth[i]['stale']) for i in gen)
for n in ev:
    hit = sum(len(flags(n, i)[0] & set(truth[i]['stale'])) for i in gen); print(f'general items (the live mix), stale qubits found by {n}: {hit} of {st}')
byb = collections.defaultdict(lambda: [0, 0])
for i in A:
    if not Y.WIN(i): continue
    b = Y.items[i]['record'].split('|')[0]
    for s, band, f in Y.qubits(i, ev['yo_v4']):
        if s and band: byb[b][0] += f; byb[b][1] += 1
print('v4 whole-window recall by backend:', {b: f'{h}/{t}' for b, (h, t) in sorted(byb.items())})
for n in ev:
    tp = fp = tot = 0
    for i in A:
        t = set(truth[i]['zero']); y = flags(n, i)[1]; tot += len(t); tp += len(t & y); fp += len(y - t)
    print(f'zero values, {n}: found {tp} of {tot}, false {fp}')
for n in ev: print(f'Job C {n}: {sum(ev[n][i]["score"] for i in C):.0f} of 400')
b = sum(ev['yo_v4'][i]['score'] > ev['yo_v2'][i]['score'] for i in C); c = sum(ev['yo_v4'][i]['score'] < ev['yo_v2'][i]['score'] for i in C)
print(f'Job C flips: v4 right and v2 wrong {b}, v2 right and v4 wrong {c}')
