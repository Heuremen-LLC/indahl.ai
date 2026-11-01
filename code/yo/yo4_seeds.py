"""yo4_seeds.py -- the three YO v4 seeds (44 at work, 45, 46) and YO v2 on TEST4, every count the seed post prints (our recount of the
referee's added readings; planned readings first, the rest defined after the data)."""
import sys, json, re, random, collections; sys.path.insert(0, '/Users/heuremen/bones-forge/yo')
import yo4_compare as Y
N = {'yo_v4': 'seed 44', 'yo_v4b': 'seed 45', 'yo_v4c': 'seed 46', 'yo_v2': 'YO v2'}
ev = {n: Y.load(n) for n in N}
A = [i for i in Y.items if Y.items[i]['job'] == 'A']; C = [i for i in Y.items if Y.items[i]['job'] == 'C']
T = {i: json.loads(Y.items[i]['answer']) for i in A}
def fl(n, i):
    o = ev[n][i]['out']
    try: p = json.loads(o[o.index('{'):o.rindex('}') + 1]); return set(int(x) for x in p.get('stale', [])), set(str(x) for x in p.get('zero', []))
    except Exception: return set(), set()
def gaps(i):
    it = Y.items[i]; S = Y.P(re.search(r'stamp (\d{4}-\d\d-\d\d \d\d:\d\d) UTC', it['prompt']).group(1)); out = {}
    for line in it['prompt'].splitlines():
        m = re.match(r'q(\d+): (.*)', line)
        if m: out[int(m.group(1))] = max((S - Y.P(d)).total_seconds() / 3600 for d in re.findall(r'T[12]=[^ ]+ \((\d{4}-\d\d-\d\d \d\d:\d\d)\)', m.group(2)))
    return out
G = {i: gaps(i) for i in A}
gen = [i for i in A if Y.GEN(i)]; all8 = [i for i in A if len(T[i]['stale']) == 8]; ct = [i for i in C if Y.items[i]['answer'] == 'CANNOT_TELL']
for n, lab in N.items():
    w = [x for i in A if Y.WIN(i) for x in Y.qubits(i, ev[n]) if x[0] and x[1]]
    flagged = sum(len(fl(n, i)[0]) for i in A); true_fl = sum(len(fl(n, i)[0] & set(T[i]['stale'])) for i in A); false_items = sum(1 for i in A if fl(n, i)[0] - set(T[i]['stale']))
    allstale = sum(len(T[i]['stale']) for i in A); exact = sum(fl(n, i)[0] == set(T[i]['stale']) for i in A)
    mix = sum(len(fl(n, i)[0] & set(T[i]['stale'])) for i in gen); mixt = sum(len(T[i]['stale']) for i in gen)
    zt = sum(len(T[i]['zero']) for i in A); zf = sum(len(fl(n, i)[1] & set(T[i]['zero'])) for i in A); zx = sum(len(fl(n, i)[1] - set(T[i]['zero'])) for i in A)
    forced = collections.Counter(ev[n][i]['pred'] for i in ct if ev[n][i]['pred'] != 'CANNOT_TELL'); ctw = sum(1 for i in C if ev[n][i]['pred'] == 'CANNOT_TELL' and Y.items[i]['answer'] != 'CANNOT_TELL')
    def band(lo, hi): q = [(i, k) for i in A for k, g in G[i].items() if lo <= g < hi]; return sum(k in fl(n, i)[0] for i, k in q), len(q)
    byb = collections.defaultdict(lambda: [0, 0])
    for i in A:
        if not Y.WIN(i): continue
        for s, b, f in Y.qubits(i, ev[n]):
            if s and b: byb[Y.items[i]['record'].split('|')[0]][0] += f; byb[Y.items[i]['record'].split('|')[0]][1] += 1
    print(f'{lab}: R1 {sum(x[2] for x in w)} of {len(w)} | R2 {Y.R(ev[n])["R2"]:.3f} | flagged {flagged}, truly stale {true_fl}, false {flagged - true_fl} in {false_items} items | stale found over all items {true_fl} of {allstale} | stale list exact {exact} of {len(A)} | all-8-stale exact {sum(fl(n, i)[0] == set(T[i]["stale"]) for i in all8)} of {len(all8)} | everyday mix {mix} of {mixt} | zeros {zf} of {zt}, false {zx} | Job C {sum(ev[n][i]["score"] for i in C):.0f} of 400 | forced {sum(forced.values())} of {len(ct)} {dict(forced)} | CANNOT_TELL on verdict items {ctw} | 23-24 h flagged {band(23, 24)[0]} of {band(23, 24)[1]} | 24-25 h {band(24, 25)[0]} of {band(24, 25)[1]} | boston {byb["ibm_boston"][0]}/{byb["ibm_boston"][1]} kingston {byb["ibm_kingston"][0]}/{byb["ibm_kingston"][1]}')
byrec = collections.defaultdict(list)
for i, it in Y.items.items(): byrec[it['record']].append(i)
recs = sorted(byrec); rng = random.Random(53)
def boot(f):
    v = f(recs); bs = sorted(f([recs[rng.randrange(len(recs))] for _ in recs]) for _ in range(2000)); return v, bs[49], bs[1949]
for n in ('yo_v4', 'yo_v4b', 'yo_v4c'):
    v, lo, hi = boot(lambda Rs, n=n: (lambda ids: Y.R(ev[n], ids)['R4'] - Y.R(ev['yo_v2'], ids)['R4'])([i for r in Rs for i in byrec[r]]))
    print(f'DEFINED AFTER THE DATA: verdicts, {N[n]} minus YO v2: {v:+.4f} [{lo:+.3f}, {hi:+.3f}] -> {Y.outcome(lo, hi)}')
for n in ('yo_v4b', 'yo_v4c'):
    v, lo, hi = boot(lambda Rs, n=n: (lambda ids: Y.R(ev[n], ids)['R3'] - Y.R(ev['yo_v4'], ids)['R3'])([i for r in Rs for i in byrec[r]]))
    print(f'DEFINED AFTER THE DATA: share of flags truly stale, {N[n]} minus seed 44: {v:+.4f} [{lo:+.3f}, {hi:+.3f}] -> {Y.outcome(lo, hi)}')
