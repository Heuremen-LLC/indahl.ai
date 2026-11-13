# robustness: blocks of 12 CALENDAR months (list-index blocks in the plan jump over gaps in the month list)
import sys, math, numpy as np, json
sys.path.insert(0, '.')
import boot as B
def run(rows, block=12, reps=2000, seed=20261110):
    out = {}
    for s in ('WTI', 'HH'):
        sc = [r for r in rows if r['series'] == s and r['o'] in 'ABC']
        ci = lambda ym: int(ym[:4])*12+int(ym[5:7])
        lo_m, hi_m = min(ci(r['ym']) for r in sc), max(ci(r['ym']) for r in sc); W = hi_m-lo_m+1
        rng = np.random.default_rng(seed); nb = math.ceil(W/block)
        st = rng.integers(0, W-block+1, size=(reps, nb)); M = np.zeros((reps, W))
        for j in range(block): np.add.at(M, (np.repeat(np.arange(reps), nb), (st+j).ravel()), 1)
        for nm, a, b in B.LEADS:
            rs = [r for r in sc if a <= r['lead'] <= b]
            num = np.zeros(W); den = np.zeros(W)
            for r in rs: den[ci(r['ym'])-lo_m] += 1; num[ci(r['ym'])-lo_m] += r['o'] == 'C'
            A = M@num; Bd = M@den; ok = Bd > 0; q = A[ok]/Bd[ok]
            lo, hi = np.percentile(q, 2.5), np.percentile(q, 97.5)
            n = len(rs); mo = len({r['ym'] for r in rs})
            oc = 'CANNOT_TELL' if n < 30 or mo < 24 else ('BELOW' if hi < .95 else ('ABOVE' if lo > .95 else ('CONSISTENT' if hi-lo <= .15 else 'CANNOT_TELL')))
            out[(s, nm)] = (round(lo, 3), round(hi, 3), oc)
    return out
for mode in ('primary', 'add1'):
    print(mode, 'span WTI months in list vs calendar:')
    rows = B.prep(B.mine, mode)
    for s in ('WTI', 'HH'):
        sc = [r for r in rows if r['series'] == s and r['o'] in 'ABC']
        ms = sorted({r['ym'] for r in sc}); print(' ', s, len(ms), 'scored months over', int(ms[-1][:4])*12+int(ms[-1][5:7])-int(ms[0][:4])*12-int(ms[0][5:7])+1, 'calendar months')
    for blk in (6, 12, 24):
        r = run(rows, blk); print('  calendar block', blk, {str(k): v for k, v in r.items() if k[1] == 'all'})
    r12 = run(rows, 12); r_ = B.cells(rows)
    print('  all cells calendar-12 vs list-12 outcome changes:', [(k, r_[k]['outcome'], v[2]) for k, v in r12.items() if r_[k]['outcome'] != v[2]])
