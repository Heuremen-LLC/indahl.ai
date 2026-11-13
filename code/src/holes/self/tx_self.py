"""SELF TEST 1: does the copper read differently while OUR OWN FSK rides it? Strata = date x hour (time of day and era held fixed).
Effect = mean over strata of (mean dB while riding - mean dB while not), per band, for 'grid before' (g) and 'echo' (e).
Null = 2000 copies where each day's riding/not sequence is circularly shifted by a random offset (keeps the runs, breaks the timing)."""
import csv, math, random, collections
R = [r for r in csv.DictReader(open('copper_self.csv')) if r['g200'] not in ('', 'nan') and r['plc_off'] == '0']
bands = ['g200', 'g212', 'g300', 'e200', 'e212', 'e300']
byday = collections.defaultdict(list)
for r in R: byday[r['ts'][:10]].append(r)
def effect(txlab):
    out = {b: [] for b in bands}
    for d, rows in byday.items():
        lab = txlab[d]; st = collections.defaultdict(lambda: ([], []))
        for r, t in zip(rows, lab): st[r['ts'][11:13]][t].append(r)
        for h, (off, on) in st.items():
            if len(on) < 5 or len(off) < 5: continue
            for b in bands:
                a = [float(x[b]) for x in on if x[b] not in ('', 'nan')]; c = [float(x[b]) for x in off if x[b] not in ('', 'nan')]
                if len(a) >= 5 and len(c) >= 5: out[b].append(sum(a) / len(a) - sum(c) / len(c))
    return {b: (sum(v) / len(v) if v else float('nan'), len(v)) for b, v in out.items()}
real = {d: [int(r['tx_any']) for r in rows] for d, rows in byday.items()}
obs = effect(real); rng = random.Random(212); null = {b: [] for b in bands}
for i in range(2000):
    sh = {}
    for d, lab in real.items():
        k = rng.randrange(len(lab)) if len(lab) > 1 else 0; sh[d] = lab[k:] + lab[:k]
    e = effect(sh)
    for b in bands: null[b].append(e[b][0])
for b in bands:
    m, n = obs[b]; nv = [x for x in null[b] if not math.isnan(x)]; mu = sum(nv) / len(nv); sd = (sum((x - mu) ** 2 for x in nv) / len(nv)) ** .5
    p = (1 + sum(abs(x - mu) >= abs(m - mu) for x in nv)) / (1 + len(nv))
    print(f'{b}: riding minus not = {m:+.2f} dB over {n} day-hours | null {mu:+.2f} +/- {sd:.2f} | z {(m-mu)/sd:+.1f} p {p:.4f}')
