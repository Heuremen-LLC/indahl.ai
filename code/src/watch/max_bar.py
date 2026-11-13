#!/usr/bin/env python3
"""max_bar.py -- THE BAR FOR A MAXIMUM OVER n DRAWS, EXACT, AS AN OBJECT THE WHOLE HOUSE CAN REACH.

LAS FALLAS 3: "a maximum over n draws reported as a measurement." It is in family I, the largest
family, and it keeps coming back because the fix is remembered rather than structural: every scorer
that reports its BEST cell, BEST lag, BEST band or BEST send is reporting a maximum, and a fixed bar
on a maximum GETS EASIER EVERY TIME THE RECORD GROWS. A guard is a filter, not a teacher, so the bar
lives here as a function with a self-test instead of as a comment in each scorer.

    from max_bar import bar, bar_sd_units, retired_asymptotic, reached_at_n

THE NULL IS EXACT AND CLOSED-FORM, no resampling (las guardas 7):

    P(max of n standard normals >= x) = alpha   <=>   Phi(x)^n = 1 - alpha
                                                <=>   x = Phi^-1((1 - alpha)^(1/n))

WHAT THIS REPLACES, and it was wrong in a direction nobody would guess. The house used
`sqrt(2 ln n)`, which is the leading term of the EXPECTED maximum -- and a bar is a QUANTILE of the
maximum, not its mean. Measured here over 200,000 simulated records per n:

    n      sqrt(2 ln n)   P(max >= it)        exact 5 % bar   P(max >= it)
    256       3.3302        0.1054               3.5396          0.0492
    1024      3.7233        0.0954               3.8902          0.0497

So the retired bar was a TEN PER CENT bar being read as a five per cent one at n=256, and it gets
WORSE as n falls -- 15 % at n=8, 22 % at n=2 -- which is the opposite of the intuition that an
asymptotic form errs safely for small n. At the same time it sat ABOVE the true expected maximum
(2.83 at n=256). The wrong object in both directions at once, which is why neither sign of the error
was visible from looking at it.

AND A FIXED BAR HAS AN EXPIRY DATE, which `reached_at_n` prints: the number of draws at which noise
alone clears it routinely. Quote that beside any fixed bar still in service.

    python3 max_bar.py --selftest [trials]      simulate and check the stated alpha is delivered
    python3 max_bar.py --table                  the bar at the n this house actually works in
"""
import math
import sys
from statistics import NormalDist

ALPHA = 0.05


def bar(n, alpha=ALPHA):
    """The one-sided bar, in standard deviations above the mean, for the maximum of n draws."""
    if n is None or n < 2: return 0.0
    return NormalDist().inv_cdf((1.0 - alpha) ** (1.0 / n))


def bar_sd_units(values, alpha=ALPHA):
    """The bar in the units of a real record: mean + sd * bar(n). Takes the per-draw values, so the
    none is built from the draws themselves and never from a number typed in afterwards.
    Returns (bar, mean, sd, n, excess_widths_of_the_observed_max)."""
    v = [x for x in values if x is not None and x == x]
    n = len(v)
    if n < 2: return (None, None, None, n, None)
    m = sum(v) / n
    sd = (sum((x - m) ** 2 for x in v) / (n - 1)) ** 0.5 or 1e-12
    b = m + sd * bar(n, alpha)
    return (b, m, sd, n, (max(v) - b) / sd)


def retired_asymptotic(n):
    """sqrt(2 ln n). Kept so any switch to the exact bar can be printed with both numbers and can
    never be an invisible change. Never use it for a decision."""
    return (2 * math.log(n)) ** 0.5 if n and n > 1 else 0.0


def reached_at_n(z, mean=0.0, sd=1.0, alpha=ALPHA):
    """How many draws it takes before noise alone clears a FIXED bar z at this alpha. The expiry
    date of every fixed bar. Returns inf when the bar is unreachable in any finite record."""
    t = (z - mean) / sd
    p = 1.0 - NormalDist().cdf(t)          # per-draw tail
    if p <= 0: return float('inf')
    return math.log(1.0 - alpha) / math.log(1.0 - p)


def _selftest(trials=200000):
    import numpy as np
    rng = np.random.default_rng(20261011)
    print('EXACT BAR vs SIMULATION, alpha = %.3f, %d records per n' % (ALPHA, trials))
    print('   %6s  %10s  %12s   %10s  %12s   %8s' %
          ('n', 'exact bar', 'P(max>=bar)', 'retired', 'P(max>=it)', 'E[max]'))
    bad = []
    for n in (2, 3, 8, 16, 64, 256, 1024, 4096):
        t = trials if n <= 1024 else max(4000, trials // 16)
        mx = rng.standard_normal((t, n)).max(axis=1)
        b, r = bar(n), retired_asymptotic(n)
        pb, pr = float((mx >= b).mean()), float((mx >= r).mean())
        print('   %6d  %10.4f  %12.4f   %10.4f  %12.4f   %8.4f' % (n, b, pb, r, pr, mx.mean()))
        if abs(pb - ALPHA) > 4 * (ALPHA * (1 - ALPHA) / t) ** 0.5 + 0.002:
            bad.append((n, pb))
    print('\n   stated alpha delivered at every n: %s' % ('YES' if not bad else 'NO -- %s' % bad))
    print('   the retired bar delivers 9 %% at n=4096 rising to 22 %% at n=2, where 5 %% was being read.\n   Two to four times as easy as advertised, and WORST at small n -- the opposite of the\n   intuition that an asymptotic form is only wrong for small n in the safe direction.')
    return 0 if not bad else 1


def _table():
    print('THE BAR AT THE n THIS HOUSE WORKS IN (sd above the per-draw mean, alpha = %.2f)' % ALPHA)
    print('   %8s  %10s  %10s  %12s' % ('n draws', 'exact', 'retired', 'retired is a'))
    for n in (3, 10, 31, 100, 316, 1000, 3162, 10000, 100000):
        # what the retired bar's alpha actually is at this n, in closed form, no simulation
        pr = 1.0 - NormalDist().cdf(retired_asymptotic(n))
        print('   %8d  %10.4f  %10.4f  %11.1f %%' % (n, bar(n), retired_asymptotic(n),
                                                     100 * (1 - (1 - pr) ** n)))
    print('\n   a fixed bar\'s expiry date, reached_at_n(z) with per-draw mean 0, sd 1:')
    for z in (2.0, 3.0, 4.0, 5.0, 6.0):
        print('      z = %.1f  ->  %s draws' % (z, format(reached_at_n(z), ',.0f')))
    return 0


if __name__ == '__main__':
    a = sys.argv[1:]
    if '--selftest' in a:
        i = a.index('--selftest')
        raise SystemExit(_selftest(int(a[i + 1]) if len(a) > i + 1 else 200000))
    if '--table' in a:
        raise SystemExit(_table())
    print(__doc__)
