src = open('/Users/heuremen/bones-forge/solar_index_referee/code/recount.py').read().split('# ---------- diff vs desk')[0]
exec(src)
import numpy as np
R = json.load(open(OUT + '/recount.json'))
# bin boot/wilson width ratio (n>=30)
rat = []
for k, c in R.items():
    for b in c['bins']:
        if b.get('n', 0) >= 30 and 'blo' in b: rat.append((b['bhi'] - b['blo']) / (b['hi'] - b['lo']))
print('block-bootstrap width / Wilson width over %d bins n>=30: median %.2f, min %.2f, max %.2f; share wider than Wilson %.2f' % (len(rat), np.median(rat), min(rat), max(rat), np.mean([r > 1 for r in rat])))
# lag-1 and lag-1..27 autocorr of residual (o - p) for M1, MID5_1, HI5_1
rows = json.load(open(OUT + '/rows.json'))
for ev in ('M', 'X', 'MID5', 'HI5'):
    s = sorted([(x['target'], x['o'] - x['p'] / 100) for x in rows if x['ev'] == ev and x['lead'] == 1 and x['status'] == 'scored'])
    ds = {dt.date.fromisoformat(t): v for t, v in s}
    days = sorted(ds); v = np.array([ds[d] for d in days]); v = v - v.mean()
    def ac(l):
        pairs = [(ds[d] - 0, ds[d + dt.timedelta(l)]) for d in days if d + dt.timedelta(l) in ds]
        a = np.array(pairs); a = a - np.array([np.mean([ds[d] for d in days])]*1)
        return np.corrcoef(a[:, 0], a[:, 1])[0, 1]
    ac1, ac2, ac7, ac27 = ac(1), ac(2), ac(7), ac(27)
    # Bartlett-ish effective n using sum of autocorr to lag 27
    rho = [ac(l) for l in range(1, 28)]; neff = len(days) / (1 + 2 * sum((1 - l / 28) * r for l, r in enumerate(rho, 1)))
    print(ev, 'n', len(days), 'residual autocorr lag1 %.2f lag2 %.2f lag7 %.2f lag27 %.2f ; effective n (Bartlett lags<=27) %.0f' % (ac1, ac2, ac7, ac27, neff))
# X <= M always? stated side
viol = sum(1 for r in stated.values() for i in range(3) if r['X'][i] > r['M'][i]); print('stated X > stated M (of %d triples): %d' % (3 * len(stated), viol))
# stated minor vs major ordering
print('stated mid Minor < Major in', sum(1 for r in stated.values() for i in range(3) if r['mid_mi'][i] < r['mid_ma'][i]), 'of', 3 * len(stated), '; hi:', sum(1 for r in stated.values() for i in range(3) if r['hi_mi'][i] < r['hi_ma'][i]))
# Active+Minor+Major > 100 for both blocks
over = C.Counter()
for r_ in stated.values(): pass
for src_, tx in rsga_files():
    v = re.search(r'^VI\.\s+Geomagnetic Activity Probabilities', tx, re.M)
    if not v or '(AMD)' in tx[:600]: continue
    vt = tx[v.start():]; a = re.search(r'^A\.\s+Middle', vt, re.M); b = re.search(r'^B\.\s+High', vt, re.M)
    for nm, blk in (('mid', vt[a.start():b.start()]), ('hi', vt[b.start():])):
        ac_, mi, ma = tri(blk, 'Active'), tri(blk, 'Minor storm'), tri(blk, 'Major-severe storm')
        if ac_ and mi and ma:
            over[nm + '_files'] += 1
            for i in range(3):
                if ac_[i] + mi[i] + ma[i] > 100: over[nm + '_over100'] += 1
print('Active+Minor+Major>100 (triples):', dict(over))
# missing-K selection: Fred K missing days vs planetary
kpd = {}
for f in sorted(glob.glob(D + '/raw/warehouse/*_DGD.txt')) + sorted(glob.glob(D + '/raw/indices/*_DGD.txt')):
    for ln in open(f, encoding='latin-1'):
        if re.match(r'\d{4} \d\d \d\d ', ln):
            n = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', ln)]
            if len(n) == 30: v = n[22:30]; kpd[dt.date(int(n[0]), int(n[1]), int(n[2]))] = None if min(v) < 0 else max(v)
miss = [d for d in kf if kf[d] is None]; allk = [d for d in kf if dt.date(2021,1,2) <= d < SETTLED]
print('Fred days with a missing K:', len(miss), 'College missing:', sum(1 for d in kc if kc[d] is None))
hi_pl = lambda d: kpd.get(d) is not None and kpd[d] >= 4.6
print('planetary est K>=5- on Fred-missing days: %d of %d (%.1f%%) ; overall frame %.1f%%' % (sum(hi_pl(d) for d in miss), len(miss), 100*sum(hi_pl(d) for d in miss)/len(miss), 100*sum(hi_pl(d) for d in allk)/len(allk)))
# if the K is missing for only some values (partial days): does max of the observed K>=5 on those days?
