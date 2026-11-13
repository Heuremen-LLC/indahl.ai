# Referee recount for SOLAR. Imports nothing from solar_tick.py or heuremen_kit.py. Run: python3 -I recount.py
import re, os, io, json, glob, tarfile, math, gzip, datetime as dt, collections as C
import numpy as np
D = '/Users/heuremen/bones-forge/solar_index/data'
OUT = '/Users/heuremen/bones-forge/solar_index_referee/out'
RUN = dt.date(2026, 11, 10); SETTLED = RUN - dt.timedelta(3)   # target < 2026-11-07 scored
MO = {m: i + 1 for i, m in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split())}
BINS = [(0,2),(3,7),(8,17),(18,27),(28,42),(43,57),(58,72),(73,87),(88,100)]
EV = ['M','X','P','MID5','MID6','HI5','HI6']

# ---------- RSGA reader (own) ----------
def rsga_files():
    for f in sorted(glob.glob(D + '/raw/warehouse/*_RSGA.tar.gz')):
        with tarfile.open(f) as t:
            for m in t.getmembers():
                if m.isfile() and re.search(r'\d{8}\w*RSGA\.txt$', m.name):
                    yield 'tar:' + os.path.basename(f) + ':' + m.name, t.extractfile(m).read().decode('latin-1')
    for f in sorted(glob.glob(D + '/raw/warehouse/2026_RSGA/*')):
        yield 'file:' + os.path.basename(f), open(f, encoding='latin-1').read()
def tri(block, label):
    m = re.search(r'^' + label + r'\s+(\d+)/(\d+)/(\d+)\s*$', block, re.M | re.I)
    return tuple(map(int, m.groups())) if m else None
stated = {}; rej = []; allparsed = []
for src, tx in rsga_files():
    m = re.search(r'^:Issued:\s+(\d{4}) (\w{3}) +(\d+) (\d\d)(\d\d) UTC', tx, re.M)
    s = re.search(r'^SDF Number\s+(\d+)\s+Issued at (\d\d)(\d\d)Z on (\d+) (\w{3}) (\d{4})(.*)$', tx, re.M)
    if not m or not s: rej.append((src, 'no issued/SDF line')); continue
    if re.search(r'correction|amd|amended', s.group(7), re.I) or re.search(r'^\s*\(AMD\)|CORRECTION|AMENDED', tx[:600], re.M | re.I):
        rej.append((src, 'correction/amendment: ' + s.group(0)[:70])); continue
    iss = dt.datetime(int(m[1]), MO[m[2]], int(m[3]), int(m[4]), int(m[5]))
    day = dt.date(int(s[6]), MO[s[5]], int(s[4]))
    h = re.search(r'^III\.\s+Event probabilities\s+(\d+) (\w{3})-(\d+) (\w{3})', tx, re.M | re.I)
    if not h: rej.append((src, 'no III header')); continue
    y = day.year + (1 if MO[h[2]] < day.month - 0 and day.month == 12 else 0)
    d1 = dt.date(y, MO[h[2]], int(h[1]))
    i3 = h.start(); i4 = tx.find('\nIV.', i3); p3 = tx[i3:i4]
    v = re.search(r'^VI\.\s+Geomagnetic Activity Probabilities', tx, re.M)
    if not v: rej.append((src, 'no VI')); continue
    vt = tx[v.start():]; a = re.search(r'^A\.\s+Middle', vt, re.M); b = re.search(r'^B\.\s+High', vt, re.M)
    A, B = vt[a.start():b.start()], vt[b.start():]
    rec = dict(src=src, iss=iss, day=day, d1=d1, M=tri(p3,'Class M'), X=tri(p3,'Class X'), P=tri(p3,'Proton'),
               mid_mi=tri(A,'Minor storm'), mid_ma=tri(A,'Major-severe storm'), hi_mi=tri(B,'Minor storm'), hi_ma=tri(B,'Major-severe storm'))
    allparsed.append(rec)
    if day < dt.date(2021,1,1): continue
    if day not in stated or rec['iss'] < stated[day]['iss']: stated[day] = rec
dups = C.Counter(r['day'] for r in allparsed if r['day'] >= dt.date(2021,1,1))
dup_days = {str(k): v for k, v in dups.items() if v > 1}
# own snapshot (issue 2026-11-09 copy)
# ---------- events reader (own) ----------
flare = C.defaultdict(lambda: [0, 0]); evdays = set(); xra_lines = 0
LINE = re.compile(r'^(\d+)\s+\+?\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+XRA\s+(\S+)\s+(\S+)', re.M)
def hm(s):
    s = s.lstrip('B').lstrip('U').lstrip('D')
    return int(s) if re.fullmatch(r'\d{4}', s) else None
def events_files():
    for f in sorted(glob.glob(D + '/raw/warehouse/*_events.tar.gz')):
        with tarfile.open(f) as t:
            for m in t.getmembers():
                mm = re.search(r'(\d{8})events\.txt$', m.name)
                if m.isfile() and mm: yield mm[1], t.extractfile(m).read().decode('latin-1')
    for f in sorted(glob.glob(D + '/raw/warehouse/2026_events/*')):
        yield os.path.basename(f)[:8], open(f, encoding='latin-1').read()
BAD = []
for ds, tx in events_files():
    d0 = dt.date(int(ds[:4]), int(ds[4:6]), int(ds[6:])); evdays.add(d0)
    for ln in tx.splitlines():
        if ' XRA ' not in ln: continue
        xra_lines += 1
        t = ln.split()
        # find 'XRA' token; class is token 2 after it (XRA 1-8A M1.0 ...). begin/max are tokens before obs,Q
        k = t.index('XRA')
        cls = t[k + 2] if len(t) > k + 2 else ''
        mm = re.fullmatch(r'([A-Z])(\d+(?:\.\d+)?)', cls)
        if not mm or t[k+1] != '1-8A': BAD.append((ds, ln)); continue
        # tokens before: id, optional '+', begin, max, end, obs, Q
        pre = t[:k]; pre = [x for x in pre if x != '+']
        # pre = [id, begin, max, end, obs, Q]  (id may merge with + never)
        b, m_ = hm(pre[1]), hm(pre[2])
        day = d0
        if m_ is not None and b is not None and m_ < b: day = d0 + dt.timedelta(1)
        if mm[1] in 'MX': flare[day][0] += 1
        if mm[1] == 'X': flare[day][1] += 1
# ---------- DGD ----------
kf, kc = {}, {}; FIX = []
for f in sorted(glob.glob(D + '/raw/warehouse/*_DGD.txt')) + sorted(glob.glob(D + '/raw/indices/*_DGD.txt')):
    for ln in open(f, encoding='latin-1'):
        if not re.match(r'\d{4} \d\d \d\d ', ln): continue
        # fixed-width read: date(10) then A(5) then 8 x 3 chars ... use regex of ints
        n = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', ln)]
        if len(n) != 30: FIX.append(ln); continue
        d = dt.date(int(n[0]), int(n[1]), int(n[2]))
        a, b = [int(x) for x in n[4:12]], [int(x) for x in n[13:21]]
        # fixed-width cross-check (cols: A 10-14, K 3 chars each from 15; college A 39-43, K from 44)
        fa = [int(ln[17+2*i:19+2*i]) for i in range(8)]; fb = [int(ln[40+2*i:42+2*i]) for i in range(8)]
        if fa != a or fb != b: FIX.append('MISMATCH ' + ln)
        kf[d] = None if min(a) < 0 else max(a); kc[d] = None if min(b) < 0 else max(b)
# ---------- DSD ----------
dsd = {}
for f in sorted(glob.glob(D + '/raw/warehouse/*_DSD.txt')):
    for ln in open(f, encoding='latin-1'):
        if re.match(r'\d{4} \d\d \d\d ', ln):
            t = ln.split()
            if len(t) == 16: dsd[dt.date(int(t[0]), int(t[1]), int(t[2]))] = (int(t[10]), int(t[11]))   # M, X
# ---------- SPE ----------
spe = set(); yr = None
for ln in open(D + '/raw/SPE.txt', encoding='latin-1'):
    m = re.match(r'\s+(\d{4})\s*$', ln)
    if m: yr = int(m[1]); continue
    m = re.match(r'(\w{3}) (\d\d)/\d{4}', ln)
    if m and yr and m[1] in MO: spe.add(dt.date(yr, MO[m[1]], int(m[2])))
SPE_LAST = dt.date(2025, 11, 13)

def pstated(r, ev, i):
    if ev in 'MXP' and len(ev) == 1: t = r[ev]; return None if t is None else t[i]
    pre = 'mid' if ev.startswith('MID') else 'hi'
    mi, ma = r[pre + '_mi'], r[pre + '_ma']
    if mi is None or ma is None: return None
    return min(100, mi[i] + ma[i]) if ev.endswith('5') else ma[i]
def obs(ev, d):
    if d >= SETTLED: return None, 'not yet settled'
    if ev in ('M', 'X'):
        if d not in evdays: return None, 'no events file'
        return int(flare[d][0 if ev == 'M' else 1] > 0), None
    if ev == 'P':
        if d > SPE_LAST: return None, 'after the proton list last changed'
        return int(d in spe), None
    src = kf if ev.startswith('MID') else kc
    if src.get(d) is None: return None, 'no K for the day'
    return int(src[d] >= (5 if ev.endswith('5') else 6)), None

rows = []
d = dt.date(2021, 1, 1)
while d <= RUN:
    r = stated.get(d)
    for L in (1, 2, 3):
        tg = d + dt.timedelta(L)
        for ev in EV:
            row = dict(ev=ev, lead=L, issue=str(d), target=str(tg))
            if r is None: row['status'] = 'no RSGA on file'
            elif r['d1'] != d + dt.timedelta(1): row['status'] = 'dates do not match the issue day'
            elif r['iss'] >= dt.datetime.combine(tg, dt.time()): row['status'] = 'issued late'
            else:
                p = pstated(r, ev, L - 1)
                if p is None: row['status'] = 'section did not parse'
                else:
                    row['p'] = p; o, w = obs(ev, tg)
                    if o is None: row['status'] = w
                    else: row['status'] = 'scored'; row['o'] = o
            rows.append(row)
    d += dt.timedelta(1)
json.dump(rows, open(OUT + '/rows.json', 'w'))
# ---------- diff vs desk ----------
desk = json.load(open(D + '/solar.json'))['rows']
dk = {(x['ev'], x['lead'], x['issue']): x for x in desk}; mk = {(x['ev'], x['lead'], x['issue']): x for x in rows}
diffs = []
for k in set(dk) | set(mk):
    a, b = dk.get(k), mk.get(k)
    if a is None or b is None: diffs.append((k, 'one side only')); continue
    if a['status'] != b['status'] or a.get('p') != b.get('p') or a.get('o') != b.get('o'):
        diffs.append((k, dict(desk=dict(s=a['status'], p=a.get('p'), o=a.get('o')), ref=dict(s=b['status'], p=b.get('p'), o=b.get('o')))))
json.dump(dict(n_desk=len(dk), n_ref=len(mk), n_diff=len(diffs), diffs=[(list(k), v) for k, v in sorted(diffs)[:400]]), open(OUT + '/diff_vs_desk.json', 'w'), indent=1)
print('rows', len(dk), len(mk), 'diffs', len(diffs)); print(C.Counter(x['status'] for x in rows))
print('rejected', rej); print('dup days', dup_days); print('DGD odd lines', len(FIX), FIX[:3]); print('bad XRA lines', len(BAD), BAD[:5]); print('xra lines', xra_lines, 'ev days', len(evdays), 'stated days', len(stated))
for k, v in sorted(diffs)[:15]: print(k, v)

# ---------- rulers ----------
def wilson(k, n, z=1.96):
    p = k / n; den = 1 + z*z/n; c = (p + z*z/(2*n)) / den; h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / den
    return max(0, c-h), min(1, c+h)
def bn(p):
    for i, (a, b) in enumerate(BINS):
        if a <= p <= b: return i
def outc(lo, hi, m, n):
    if n < 30: return 'CANNOT_TELL'
    return 'ABOVE' if lo > m else 'BELOW' if hi < m else 'CONSISTENT'
def boot(ser, reps=2000, seed=27, block=27):
    n = len(ser); rng = np.random.default_rng(seed)
    p = np.array([s[0] for s in ser]) / 100.0; o = np.array([s[1] for s in ser], float); b = np.array([bn(s[0]) for s in ser])
    nb = -(-n // block); st = rng.integers(0, n - block + 1, size=(reps, nb))
    idx = (st[:, :, None] + np.arange(block)[None, None, :]).reshape(reps, -1)[:, :n]
    P, O, B = p[idx], o[idx], b[idx]
    f = O.mean(1); bs = ((P - O)**2).mean(1); bc = f*(1-f)
    with np.errstate(all='ignore'): bss = np.where(bc > 0, 1 - bs/bc, np.nan)
    bss = bss[~np.isnan(bss)]
    bl = []
    for i in range(9):
        m = (B == i); c = m.sum(1); e = (O*m).sum(1); ok = c > 0
        fr = e[ok]/c[ok]; bl.append((float(np.percentile(fr, 2.5)), float(np.percentile(fr, 97.5))) if ok.sum() >= 100 else None)
    return (float(np.percentile(bss, 2.5)), float(np.percentile(bss, 97.5))), bl
cells = {}
for ev in EV:
    for L in (1, 2, 3):
        ser = sorted([(x['p'], x['o'], x['target']) for x in rows if x['ev'] == ev and x['lead'] == L and x['status'] == 'scored'], key=lambda z: z[2])
        n = len(ser); bins = []
        for i, (a, b) in enumerate(BINS):
            s = [z for z in ser if bn(z[0]) == i]; m = len(s); k = sum(z[1] for z in s)
            if m == 0: bins.append(dict(bin=i, n=0)); continue
            mp = sum(z[0] for z in s) / m / 100; lo, hi = wilson(k, m)
            bins.append(dict(bin='%d to %d' % (a, b), n=m, events=k, mean=mp, obs=k/m, lo=lo, hi=hi, outcome=outc(lo, hi, mp, m)))
        f = sum(z[1] for z in ser) / n; bs = sum((z[0]/100 - z[1])**2 for z in ser) / n; bss = 1 - bs/(f*(1-f))
        (bl, bh), bb = boot(ser)
        for i, b in enumerate(bins):
            if b.get('n') and bb[i]:
                b['blo'], b['bhi'] = bb[i]; b['boot_outcome'] = outc(bb[i][0], bb[i][1], b['mean'], b['n'])
        cells[(ev, L)] = dict(n=n, events=sum(z[1] for z in ser), f=f, bs=bs, bclim=f*(1-f), bss=bss, bss_lo=bl, bss_hi=bh, bins=bins)
json.dump({'%s_%d' % k: v for k, v in cells.items()}, open(OUT + '/recount.json', 'w'), indent=1)
# compare with desk summary
S = json.load(open('/Users/heuremen/bones-forge/solar_index/summary_solar.json'))
nd = 0; flips = []; bootdiff = []
for c in S['cells']:
    k = (c['event'], c['lead']); mine = cells[k]
    sk = c['skill']
    for f_, a_, b_ in (('n', sk['n'], mine['n']), ('events', sk['events'], mine['events'])):
        if a_ != b_: print('SKILL DIFF', k, f_, a_, b_); nd += 1
    if abs(sk['brier'] - mine['bs']) > 6e-6 or abs(sk['bss'] - mine['bss']) > 6e-5: print('BSS DIFF', k, sk['brier'], mine['bs'], sk['bss'], mine['bss']); nd += 1
    for bd, bm in zip(c['bins'], mine['bins']):
        if bd['n'] == 0 and not bm.get('n'): continue
        if bd['n'] == 0 or not bm.get('n'): print('BIN n mismatch', k, bd['bin'], bd['n'], bm.get('n')); nd += 1; continue
        keys = [bd['n'] == bm['n'], bd['events'] == bm['events'], abs(bd['mean_stated'] - round(bm['mean'], 4)) < 1e-9, abs(bd['observed'] - round(bm['obs'], 4)) < 1e-9,
                abs(bd['lo'] - round(bm['lo'], 4)) < 1e-9, abs(bd['hi'] - round(bm['hi'], 4)) < 1e-9, (bd.get('outcome_before_hold') or bd['outcome']) == bm['outcome']]
        if not all(keys): print('BIN DIFF', k, bd, bm); nd += 1
        if bm.get('boot_outcome') and bm['boot_outcome'] != bm['outcome']: flips.append((k, bd['bin'], bm['n'], bm['outcome'], bm['boot_outcome'], bd.get('boot_lo'), bd.get('boot_hi'), bm['blo'], bm['bhi']))
        if bd.get('boot_lo') is not None and bm.get('blo') is not None and (abs(bd['boot_lo'] - bm['blo']) > 0.03 or abs(bd['boot_hi'] - bm['bhi']) > 0.03): bootdiff.append((k, bd['bin'], bd['boot_lo'], bd['boot_hi'], round(bm['blo'], 4), round(bm['bhi'], 4)))
    if abs(sk['lo'] - mine['bss_lo']) > 0.03 or abs(sk['hi'] - mine['bss_hi']) > 0.03: print('BSS BOOT far', k, sk['lo'], sk['hi'], mine['bss_lo'], mine['bss_hi'])
print('cell/bin cell differences vs desk:', nd)
print('own-boot flips (outcome vs Wilson outcome):'); [print(' ', f) for f in flips]
print('bin boot ends >0.03 from desk:', len(bootdiff)); [print(' ', b) for b in bootdiff[:10]]
json.dump(dict(flips=flips, bootdiff=bootdiff), open(OUT + '/boot_flips.json', 'w'), indent=1)
