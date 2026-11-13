src = open('/Users/heuremen/bones-forge/solar_index_referee/code/recount.py').read().split('# ---------- diff vs desk')[0]
exec(src)
# max K per day for stations, from DGD (own fixed-width read)
mx = {'fred': {}, 'col': {}, 'pl': {}}
for f in sorted(glob.glob(D + '/raw/warehouse/*_DGD.txt')) + sorted(glob.glob(D + '/raw/indices/*_DGD.txt')):
    for ln in open(f, encoding='latin-1'):
        if not re.match(r'\d{4} \d\d \d\d ', ln): continue
        n = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', ln)]
        if len(n) != 30: continue
        d = dt.date(int(n[0]), int(n[1]), int(n[2]))
        for nm, v in (('fred', n[4:12]), ('col', n[13:21]), ('pl', n[22:30])): mx[nm][d] = None if min(v) < 0 else max(v)
def run(blk, label, cat, st):
    # blk: 'mid' or 'hi'; cat: 'Active'/'Minor'/'Major'
    out = []
    for d, r in stated.items():
        tg = d + dt.timedelta(1)
        if r['d1'] != tg or r['iss'] >= dt.datetime.combine(tg, dt.time()) or tg >= SETTLED: continue
        k = mx[st].get(tg)
        if k is None: continue
        # planetary in third units: treat 4.67..5.33 as 5
        kk = round(k) if st == 'pl' else k
        o = int(kk == 4) if cat == 'Active' else int(kk == 5) if cat == 'Minor' else int(kk >= 6)
        # need Active triple: read again from the file
        p = {'Minor': r[blk + '_mi'][0], 'Major': r[blk + '_ma'][0]}.get(cat)
        out.append((p, o))
    return out
print('Exclusive-category reading (day one): stated category chance vs day greatest K in that category')
for blk, st in (('mid', 'fred'), ('mid', 'pl'), ('hi', 'col'), ('hi', 'pl')):
    for cat in ('Minor', 'Major'):
        s = run(blk, '', cat, st)
        if not s: continue
        n = len(s); mp = sum(p for p, o in s) / n; f = 100 * sum(o for p, o in s) / n
        print('  %-3s %-5s vs %-5s greatest K exactly-in-category: n %d mean stated %.1f%% observed %.1f%%' % (blk, cat, st, n, mp, f))
# stated Active (needs reading)
act = {}
for src_, tx in rsga_files():
    s = re.search(r'^SDF Number\s+\d+\s+Issued at \d{4}Z[^\n]* on (\d+) (\w{3}) (\d{4})', tx, re.M)
    if not s or '(AMD)' in tx[:600] or 'Correction' in tx[:600]: continue
    day = dt.date(int(s[3]), MO[s[2]], int(s[1])); v = re.search(r'^VI\.', tx, re.M)
    vt = tx[v.start():]; a = re.search(r'^A\.\s+Middle', vt, re.M); b = re.search(r'^B\.\s+High', vt, re.M)
    act[day] = (tri(vt[a.start():b.start()], 'Active'), tri(vt[b.start():], 'Active'))
for blk, idx, st in (('mid', 0, 'fred'), ('mid', 0, 'pl'), ('hi', 1, 'col'), ('hi', 1, 'pl')):
    s = []
    for d, r in stated.items():
        tg = d + dt.timedelta(1)
        if r['d1'] != tg or r['iss'] >= dt.datetime.combine(tg, dt.time()) or tg >= SETTLED or mx[st].get(tg) is None or act.get(d) is None: continue
        k = mx[st][tg]; kk = round(k) if st == 'pl' else k
        s.append((act[d][idx][0], int(kk == 4)))
    n = len(s); print('  %-3s Active vs %-5s greatest K == 4: n %d mean stated %.1f%% observed %.1f%%' % (blk, st, n, sum(p for p, o in s) / n, 100 * sum(o for p, o in s) / n))
# distribution of daily greatest K Fred vs planetary
for nm in ('fred', 'col', 'pl'):
    v = [round(x) for d, x in mx[nm].items() if x is not None and dt.date(2021,1,2) <= d < SETTLED]
    c = C.Counter(v); n = len(v); print(nm, 'greatest K distribution %:', {k: round(100 * c[k] / n, 1) for k in sorted(c)})
