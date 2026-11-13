import json, math, sys, collections as C
import numpy as np
D = '/Users/heuremen/bones-forge/steo_index/'
mine = json.load(open('../out/rows.json'))
desk = json.load(open(D+'data/steo.json'))['rows']
pdfl = json.load(open('../out/pdf_levels_ref.json'))
LEADS = (('all', 1, 999), ('1-2', 1, 2), ('3-6', 3, 6), ('7-12', 7, 12), ('13+', 13, 999))
def outc(lo, up, y):
    if lo is None or up is None or lo > up: return 'CT'
    if y is None: return 'NR'
    return 'A' if y > up else ('B' if y < lo else 'C')
def prep(rows, mode):
    out = []
    for r in rows:
        lo, up = r.get('lo', r.get('lower')), r.get('up', r.get('upper'))
        ym = r.get('ym', r.get('month')); lvl = r.get('level')
        if mode == 'primary': ok = lvl is not None and abs(lvl-0.95) < 1e-9
        else:
            ok = (lvl is not None and abs(lvl-0.95) < 1e-9) or (lvl is None and (pdfl.get('%s/%s' % (r['issue'], r['series'])) or {}).get('pagehit'))
        o = outc(lo, up, r['spot']) if ok else 'CT'
        out.append(dict(series=r['series'], ym=ym, lead=r['lead'], o=o, issue=r['issue']))
    return out
def draws(W, reps, seed, block):
    rng = np.random.default_rng(seed); M = np.zeros((reps, W))
    if W < block: return M
    nb = math.ceil(W/block); st = rng.integers(0, W-block+1, size=(reps, nb))
    for j in range(block):
        np.add.at(M, (np.repeat(np.arange(reps), nb), (st+j).ravel()), 1)
    return M
def cells(rows, block=12, reps=2000, seed=20261110):
    res = {}
    for s in ('WTI', 'HH'):
        sc = [r for r in rows if r['series'] == s and r['o'] in 'ABC']
        months = sorted({r['ym'] for r in sc}); idx = {m: i for i, m in enumerate(months)}
        M = draws(len(months), reps, seed, block)
        for nm, a, b in LEADS:
            rs = [r for r in sc if a <= r['lead'] <= b]
            n = len(rs); k = sum(r['o'] == 'C' for r in rs); mo = len({r['ym'] for r in rs})
            num = np.zeros(len(months)); den = np.zeros(len(months))
            for r in rs: den[idx[r['ym']]] += 1; num[idx[r['ym']]] += r['o'] == 'C'
            lo = hi = None
            if n:
                A = M @ num; B = M @ den; ok = B > 0
                if ok.sum() >= 100: q = A[ok]/B[ok]; lo, hi = float(np.percentile(q, 2.5)), float(np.percentile(q, 97.5))
            if n < 30 or mo < 24 or lo is None: oc = 'CANNOT_TELL'
            elif hi < .95: oc = 'BELOW'
            elif lo > .95: oc = 'ABOVE'
            elif hi-lo <= .15: oc = 'CONSISTENT'
            else: oc = 'CANNOT_TELL'
            cnt = C.Counter(r['o'] for r in rows if r['series'] == s and a <= r['lead'] <= b)
            res[(s, nm)] = dict(n=n, k=k, above=sum(r['o'] == 'A' for r in rs), below=sum(r['o'] == 'B' for r in rs), months=mo, share=k/n if n else None, lo=lo, hi=hi, outcome=oc, ct=cnt['CT'], nr=cnt['NR'])
    return res
def show(title, res):
    print('==', title)
    for (s, nm), v in res.items():
        print('%-3s %-5s n=%4d in=%4d ab=%3d be=%3d mo=%3d sh=%s [%s, %s] %s ct=%d nr=%d' % (s, nm, v['n'], v['k'], v['above'], v['below'], v['months'],
              None if v['share'] is None else round(v['share'], 4), None if v['lo'] is None else round(v['lo'], 4), None if v['hi'] is None else round(v['hi'], 4), v['outcome'], v['ct'], v['nr']))
if __name__ == '__main__':
    S = json.load(open(D+'summary_steo.json'))
    for key, mode in (('cells', 'primary'), ('cells_addendum1', 'add1')):
        res = cells(prep(desk, mode)); show('AS DESK (artifact rows kept), '+mode, res)
        for c in S[key]:
            v = res[(c['series'], {'all leads': 'all', '1 to 2 months': '1-2', '3 to 6 months': '3-6', '7 to 12 months': '7-12', '13 months or more': '13+'}[c['cell']])]
            d = max(abs((v['lo'] or 0)-(c['lo'] or 0)), abs((v['hi'] or 0)-(c['hi'] or 0)))
            flag = '' if (v['n'], v['k'], v['outcome']) == (c['scored'], c['inside'], c['outcome']) and d < 1e-3 else '  <-- DIFF desk n=%d k=%d [%s,%s] %s' % (c['scored'], c['inside'], c['lo'], c['hi'], c['outcome'])
            if flag: print(c['series'], c['cell'], flag)
        show('CORRECTED (artifact rows removed), '+mode, cells(prep(mine, mode)))
