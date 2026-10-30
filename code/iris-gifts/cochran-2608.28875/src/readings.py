#!/usr/bin/env python3
"""C1-C3 (PLAN 559d0b5, committed before this ran). Our code; their release files read as data only. WER in points."""
import csv, os, math, collections, numpy as np
T = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'theirs', 'release')
R = list(csv.DictReader(open(T + '/rerun_cells_release.csv'))); M = {}
for r in csv.DictReader(open(T + '/per_side_outcomes.csv')): M[(r['side_id'], r['model'], r['arm'])] = float(r['wer']) * 100
def sign_p(k, n):   # exact two-sided sign test
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(min(k, n - k) + 1)) / 2 ** n)
cell = collections.defaultdict(list)
for r in R: cell[(r['side_id'], r['model'], r['arm'])].append(float(r['wer']) * 100)
med = {k: float(np.median(v)) for k, v in cell.items()}
print('C1 first-part position: arm-centred residual WER (rep minus its side-model-arm median over five reps), position 0 against position 2. arm_pos records each side\'s first audio part only (score_rerun.py), so this reads first-part position, not order across a whole side')
for m in sorted({r['model'] for r in R}):
    res = collections.defaultdict(list)
    for r in R:
        if r['model'] == m: res[r['arm_pos']].append(float(r['wer']) * 100 - med[(r['side_id'], m, r['arm'])])
    for p in ('0', '1', '2'): print('  %-18s position %s: n %2d  median residual %+.2f  above zero %d, below %d, zero %d' % (m, p, len(res[p]), np.median(res[p]), sum(x > 0 for x in res[p]), sum(x < 0 for x in res[p]), sum(x == 0 for x in res[p])))
    # paired within (side, rep): the cell that ran last minus the cell that ran first, in residuals, so arm and side are held by the medians
    tri = collections.defaultdict(dict)
    for r in R:
        if r['model'] == m: tri[(r['side_id'], r['rep'])][r['arm_pos']] = float(r['wer']) * 100 - med[(r['side_id'], m, r['arm'])]
    d = [v['2'] - v['0'] for v in tri.values()]; k = sum(x > 0 for x in d); nz = sum(x != 0 for x in d)
    print('  %-18s last minus first, paired within side and rep: n %d  median %+.2f  last higher %d of %d nonzero, exact sign p %.3f' % (m, len(d), np.median(d), k, nz, sign_p(k, nz)))
print('\nC2 sign repeat: sign of full minus none, main run against each rerun rep (rep k full minus rep k none). The main run and the reruns also differ in arm order (fixed against counterbalanced) and date (seven days), so a sign change is not read as draw alone')
for m in sorted({r['model'] for r in R}):
    for s in sorted({r['side_id'] for r in R}):
        main = M[(s, m, 'full')] - M[(s, m, 'none')]
        by = {(r['arm'], r['rep']): float(r['wer']) * 100 for r in R if r['side_id'] == s and r['model'] == m}
        reps = [by[('full', str(k))] - by[('none', str(k))] for k in range(1, 6)]
        agree = sum(np.sign(x) == np.sign(main) for x in reps)
        print('  %-18s %s  main %+7.2f  reruns %s  same sign %d of 5' % (m, s, main, ' '.join('%+7.2f' % x for x in reps), agree))
print('\nC3 the rerun delta IQR (gpt-4o-transcribe, 20 side x rep pairs, full minus none). The paper\'s other IQRs use the linear rule; this one uses index quartiles. Two rules, not an error')
d = sorted(float(np.round(x, 6)) for x in [float(a) for a in []] ) or None
pairs = []
by = {(r['side_id'], r['arm'], r['rep']): float(r['wer']) * 100 for r in R if r['model'] == 'gpt-4o-transcribe'}
for s in sorted({r['side_id'] for r in R}):
    for k in range(1, 6): pairs.append(by[(s, 'full', str(k))] - by[(s, 'none', str(k))])
x = sorted(pairs); n = len(x)
print('  n %d  median %+.2f  range [%+.2f, %+.2f]' % (n, np.median(x), x[0], x[-1]))
print('  index quartiles sorted[n//4], sorted[3n//4]: [%+.2f, %+.2f]' % (x[n // 4], x[3 * n // 4]))
print('  linear interpolation (numpy default):      [%+.2f, %+.2f]' % tuple(np.percentile(x, [25, 75])))
# C1 bound (same run): distribution-free 95% interval for the median of the 20 paired last-minus-first residual differences, from binomial
# order statistics (the largest k, narrowest interval, with coverage of at least 95%), so a CONSISTENT reads as a bound.
def median_ci(d):
    x = sorted(d); n = len(x); best = None
    for k in range(n // 2):
        cov = sum(math.comb(n, i) for i in range(k + 1, n - k)) / 2 ** n   # P(x_(k+1) <= median < x_(n-k))
        if cov >= 0.95: best = (x[k], x[n - k - 1], cov)
    return best
print('\nC1 bound: 95% order-statistic interval for the median last-minus-first difference (WER points)')
for m in sorted({r['model'] for r in R}):
    tri = collections.defaultdict(dict)
    for r in R:
        if r['model'] == m: tri[(r['side_id'], r['rep'])][r['arm_pos']] = float(r['wer']) * 100 - med[(r['side_id'], m, r['arm'])]
    lo, hi, cov = median_ci([v['2'] - v['0'] for v in tri.values()]); print('  %-18s [%+.2f, %+.2f] (coverage %.3f)' % (m, lo, hi, cov))
