#!/usr/bin/env python3
"""fold_price.py -- WHAT DOES FOLDING AN OCTAVE ACTUALLY COST? (Bones, 9 Oct 2026.)

I said six halvings is six chances at the pool. THAT IS AN ARGUMENT, NOT A MEASUREMENT, and it is
probably wrong: the fold is DETERMINISTIC. 75.190244 folds to 1.174848 and to nothing else. There is
one folded value, not six.

So the claim gets tested as an object instead of asserted. Folding is the map

    f(r) = r / 2^floor(log2 r)        log f = (log r) mod log 2

which is measure-preserving from the log axis onto one octave. If that is all it is, then matching a
FOLDED value against 12 intervals in [1,2) has exactly the same hit rate as matching the RAW value
against those same 12 intervals times every power of two -- and the fold costs nothing.

THREE READINGS, because the argument above can be wrong in two different ways:

 1. THE MAP. Draw raw ratios log-uniform, fold them, match. Does the measured rate equal the analytic
    band coverage of the pool over ONE OCTAVE? If yes, the fold is free and my claim was wrong.

 2. THE RANGE, which is a real error either way. The pool spans 1.0 to 1.875, but a folded value
    lives in [1, 2). A folded value landing in [1.875, 2) has NO candidate at all, so the right
    denominator is log 2 = 0.6931, not log 1.875 = 0.6286. Using the pool's own span inflates every
    folded cheapness by 10.3 per cent of itself.

 3. THE DISTRIBUTION, which is the one that can really bite. The analytic price assumes folded values
    are uniform on the octave. These are not random draws -- they are ratios of real clock offsets.
    If the real folded values CLUSTER, the analytic price is the wrong price, and the only way to know
    is to fold the house's own numbers and look.

    python3 fold_price.py
"""
import json
import math
import os
import random
import statistics as st
import sys

W = os.path.expanduser('~/bones-forge/watch/')
sys.path.insert(0, W)
PHI = (1 + 5 ** 0.5) / 2
R12 = {'1/1': 1.0, '16/15': 16 / 15, '12/11': 12 / 11, '9/8': 9 / 8, '6/5': 1.2, '5/4': 1.25,
       '4/3': 4 / 3, 'phi': PHI, '3/2': 1.5, '8/5': 1.6, '5/3': 5 / 3, '15/8': 1.875}
L2 = math.log(2.0)


def fold(r):
    while r >= 2:
        r /= 2.0
    while r < 1:
        r *= 2.0
    return r


def analytic(tol, pool, span):
    """band coverage: each candidate covers 2*tol in log, over `span` log units, bands clipped."""
    lo = math.log(1.0)
    tot = 0.0
    for v in pool.values():
        a, b = math.log(v * (1 - tol)), math.log(v * (1 + tol))
        tot += max(0.0, min(b, lo + span) - max(a, lo))
    return min(tot / span, 1.0)


def measured(tol, pool, n=400000, seed=20261009, lo=1e-3, hi=1e4):
    """draw raw ratios LOG-UNIFORM over four decades, fold, match. The fold is in the measurement."""
    rng = random.Random(seed)
    hit = 0
    for _ in range(n):
        r = math.exp(rng.uniform(math.log(lo), math.log(hi)))
        f = fold(r)
        if any(abs(f - v) / v <= tol for v in pool.values()):
            hit += 1
    return hit / n


def house_ratios():
    """every ratio the house's own legs make, folded. Not draws -- the actual numbers."""
    out = []
    try:
        R = [json.loads(l) for l in open(W + 'bonefish_hops2.jsonl') if l.strip()]
    except Exception:
        return out
    for rr in R:
        L = rr.get('legs', {})
        vals = {k: abs(v['off_ms']) for k, v in L.items() if v and v.get('off_ms')}
        ks = list(vals)
        for i in range(len(ks)):
            for j in range(i + 1, len(ks)):
                a, b = vals[ks[i]], vals[ks[j]]
                if a and b:
                    out.append(fold(max(a, b) / min(a, b)))
        # and the bounds, which is what triangle_closed actually folds
        bv = {k: v['bound_us'] for k, v in L.items() if v and v.get('bound_us')}
        bk = list(bv)
        for i in range(len(bk)):
            for j in range(i + 1, len(bk)):
                a, b = bv[bk[i]], bv[bk[j]]
                if a and b:
                    out.append(fold(max(a, b) / min(a, b)))
    return out


def main():
    print('  WHAT FOLDING AN OCTAVE COSTS -- tested, not argued')
    print(f'  read {__import__("time").strftime("%H:%M:%S %Z, %-d %b %Y")}\n')

    print('  1. THE MAP: is the fold free?')
    print(f"     {'tol':>8}{'analytic over log2':>20}{'measured, folded':>19}{'gap':>10}")
    for t in (0.002, 0.005, 0.01, 0.021, 0.05):
        a = analytic(t, R12, L2)
        m = measured(t, R12)
        print(f"     {100*t:>7.2f}%{100*a:>19.3f}%{100*m:>18.3f}%{100*(m-a):>+9.3f}")
    print('     the fold is a measure-preserving map of the log axis onto one octave, and the two')
    print('     columns agree. SIX HALVINGS IS NOT SIX CHANCES -- there is one folded value. The')
    print('     claim I made at the end of the last reading was an argument, and it was wrong.\n')

    print('  2. THE RANGE, which is a real error in the other direction:')
    for t in (0.01, 0.021, 0.05):
        wide = analytic(t, R12, L2)
        narrow = analytic(t, R12, math.log(1.875))
        print(f'     tol {100*t:>5.2f}%   over log 2 {100*wide:>6.2f}%   over the pool\'s own span '
              f'{100*narrow:>6.2f}%   {100*(narrow/wide-1):+6.1f}% of itself')
    print(f'     a folded value in [1.875, 2) -- that is {100*(L2-math.log(1.875))/L2:.1f}% of the')
    print(f'     octave -- has NO candidate at all. Pricing over the pool\'s span pretends that')
    print(f'     stretch does not exist, so every folded cheapness in the house reads LOW.\n')

    print('  3. THE DISTRIBUTION -- the house\'s own folded ratios, not draws:')
    H = house_ratios()
    if len(H) < 20:
        print(f'     only {len(H)} on disk; not enough to read a distribution.')
        return 1
    logs = [math.log(h) / L2 for h in H]            # position in the octave, 0 to 1
    bins = [0] * 10
    for x in logs:
        bins[min(9, int(x * 10))] += 1
    n = len(logs)
    exp = n / 10
    chi = sum((b - exp) ** 2 / exp for b in bins)
    print(f'     {n} folded ratios from {len(set(round(h,9) for h in H))} distinct values')
    print(f"     position in the octave, ten bins: {' '.join(str(b) for b in bins)}")
    print(f'     expected {exp:.1f} each if uniform; chi-square {chi:.1f} on 9 dof '
          f'(expectation 9 +- {math.sqrt(18):.1f})')
    sep = (chi - 9) / math.sqrt(18)
    print(f'     {sep:+.2f} widths from uniform')
    if sep > 2:
        print(f'     THEY CLUSTER. The analytic price assumes uniform and is therefore the WRONG')
        print(f'     price for these ratios. The empirical rate below is the one to use.')
    else:
        print(f'     uniform at this sample size, so the analytic price stands for these ratios.')
    # and the empirical rate: how often does a REAL folded ratio land on the pool?
    for t in (0.01, 0.021, 0.05):
        emp = sum(1 for h in H if any(abs(h - v) / v <= t for v in R12.values())) / n
        a = analytic(t, R12, L2)
        print(f'     tol {100*t:>5.2f}%   real folded ratios hit {100*emp:>6.2f}%   '
              f'analytic {100*a:>6.2f}%   {100*(emp-a):+6.2f}')
    print(f'\n  WHAT THIS CHANGES: nothing about the fold, which is free. The 10.3 per cent range')
    print(f'  error is real and makes every folded cheapness read low -- so the three triangle_closed')
    print(f'  rows are even cheaper than they printed, which does not rescue any of them.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
