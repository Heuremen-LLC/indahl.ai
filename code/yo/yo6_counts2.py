"""yo6_counts2.py -- defined after the data (1 Nov 2026, after the outside referee of the YO v6 post): recounts the referee's numbers with our
own code before any is printed. (1) flagged qubit numbers that are not among the qubits shown in the item, per model and set; (2) the share of
flags that are right (R3) counting every flagged number, each seed minus YO v4, paired bootstrap over TEST4 records (2,000, seed 41, 95 %);
(3) TEST6 record counts and overlap with TEST4 and TEST5 records."""
import json, os, sys, random, collections
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import yo4_compare as C4, yo6_compare as C6
M = ('yo_v4', 'yo_v6', 'yo_v6b'); S4 = {n: C4.load(n) for n in M}; S6 = {n: C6.load6('test6', n) for n in M}
items = C4.items; A = [i for i in items if items[i]['job'] == 'A']
def flags4(ev, i):
    try: o = ev[i]['out']; return set(int(x) for x in json.loads(o[o.index('{'):o.rindex('}') + 1]).get('stale', []))
    except Exception: return set()
def shown4(i): return set(int(l[1:l.index(':')]) for l in items[i]['prompt'].splitlines() if l.startswith('q') and ':' in l)
truth4 = lambda i: set(json.loads(items[i]['answer'])['stale'])
for n in M:
    off4 = [(i, sorted(flags4(S4[n], i) - shown4(i))) for i in A if flags4(S4[n], i) - shown4(i)]
    off6 = [(i, sorted(C6.flagged(S6[n], i) - C6.shown(i))) for i in C6.T6 if C6.flagged(S6[n], i) - C6.shown(i)]
    allf = sum(len(flags4(S4[n], i)) for i in A); right = sum(len(flags4(S4[n], i) & truth4(i)) for i in A)
    wrong_items = sum(1 for i in A if flags4(S4[n], i) - truth4(i))
    print(n, f'off-record flagged numbers: TEST4 {sum(len(x[1]) for x in off4)} (in {len(off4)} items), TEST6 {sum(len(x[1]) for x in off6)} (in {len(off6)} items);',
          f'every flag counted on TEST4: {right} of {allf} truly stale, {allf - right} not stale (in {wrong_items} items)')
    for i, x in off4[:6]: print('   TEST4', i.split('|')[1] if '|' in i else i, 'flagged', x, 'shown', sorted(shown4(i))[:12])
def r3all(ev, ids):
    f = sum(len(flags4(ev, i)) for i in ids if items[i]['job'] == 'A'); r = sum(len(flags4(ev, i) & truth4(i)) for i in ids if items[i]['job'] == 'A')
    return r / max(1, f)
by = collections.defaultdict(list)
for i, it in items.items(): by[it['record']].append(i)
recs = sorted(by); rng = random.Random(41)
for s in ('yo_v6', 'yo_v6b'):
    f = lambda Rs: (lambda ids: r3all(S4[s], ids) - r3all(S4['yo_v4'], ids))([i for r in Rs for i in by[r]])
    v = f(recs); bs = sorted(f([recs[rng.randrange(len(recs))] for _ in recs]) for _ in range(2000))
    print(f'R3 counting every flagged number, {s} minus yo_v4: {v:+.5f} [{bs[49]:+.5f}, {bs[1949]:+.5f}] -> {C4.outcome(bs[49], bs[1949])}')
r6 = set(it['record'] for it in C6.T6.values()); r4 = set(it['record'] for it in items.values())
T5 = [json.loads(l) for l in open(H + '/data5/test_items.jsonl')]; r5 = set(it['record'] for it in T5)
print(f'TEST6 records {len(r6)}, TEST4 records {len(r4)}, overlap {len(r6 & r4)}; TEST5 records {len(r5)}, overlap with TEST6 {len(r6 & r5)}; TEST6 items {len(C6.T6)}')
