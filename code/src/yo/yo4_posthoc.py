"""yo4_posthoc.py -- defined after the data: share of qubits flagged stale by gap band (hours since the older T1/T2 date) on all TEST4 Job A items."""
import sys, json, re, collections; sys.path.insert(0, '/Users/heuremen/bones-forge/yo')
import yo4_compare as Y
ev = {n: Y.load(n) for n in ('yo_v4', 'yo_v2', 'yo_v3', 'daterule')}
A = [i for i in Y.items if Y.items[i]['job'] == 'A']
def gapq(iid):
    it = Y.items[iid]; S = Y.P(re.search(r'stamp (\d{4}-\d\d-\d\d \d\d:\d\d) UTC', it['prompt']).group(1)); out = []
    for line in it['prompt'].splitlines():
        m = re.match(r'q(\d+): (.*)', line)
        if m: out.append((int(m.group(1)), max((S - Y.P(d)).total_seconds() / 3600 for d in re.findall(r'T[12]=[^ ]+ \((\d{4}-\d\d-\d\d \d\d:\d\d)\)', m.group(2)))))
    return out
def flags(n, iid):
    o = ev[n][iid]['out']
    try: return set(int(x) for x in json.loads(o[o.index('{'):o.rindex('}') + 1]).get('stale', []))
    except Exception: return set()
bins = [(0, 20), (20, 23), (23, 24), (24, 25), (25, 30), (30, 36), (36, 42), (42, 48), (48, 1e9)]
print('DEFINED AFTER THE DATA. Share of qubits flagged stale, by gap (hours since the older T1/T2 date); stale means gap > 24 h. All Job A items of TEST4.')
print('gap band      n   ' + '  '.join(f'{n:>9s}' for n in ev))
for lo, hi in bins:
    qs = [(i, q) for i in A for q, g in gapq(i) if lo <= g < hi]
    row = '  '.join(f'{sum(q in flags(n, i) for i, q in qs) / max(1, len(qs)):9.3f}' for n in ev)
    print(f'{lo:>3.0f}-{hi if hi < 1e8 else 999:>4.0f} h {len(qs):5d}   {row}')
for n in ('yo_v4', 'yo_v2'):
    fl = collections.Counter()
    for i in A:
        for q, g in gapq(i):
            if q in flags(n, i): fl['under 24 h, flagged' if g <= 24 else 'over 24 h, flagged'] += 1
    print(n, dict(fl))
