#!/usr/bin/env python3
"""allan.py -- THE OVERLAPPING ALLAN DEVIATION, VALIDATED BEFORE IT IS POINTED AT ANYTHING.
(Bones, 11 Oct 2026.)

WHY THIS EXISTS. We published a proposal resting on a sqrt(N) averaging gain, which assumes WHITE
noise. Clock residuals are generally not white -- that is the reason the field characterises clocks
with Allan deviation rather than a standard error. Under flicker frequency noise the deviation is
FLAT and more data buys nothing; under random walk it RISES and more data makes it worse. So the
proposal is unpriced until the noise TYPE of the real data is measured, and this is the instrument
that measures it.

AND IT IS VALIDATED FIRST, ON CASES WITH KNOWN ANSWERS. Four instruments failed earlier in this work
because none of them was checked against something it had to get right. An Allan deviation is easy to
get subtly wrong -- overlapping versus non-overlapping estimators, the factor of 2 tau^2, how gaps
are handled -- and the four canonical noise types have KNOWN SLOPES on a log-log plot:

    white phase        sigma_y(tau) ~ tau^-1        slope -1
    white frequency                 ~ tau^-1/2      slope -1/2
    flicker frequency               ~ tau^0         slope  0     FLAT
    random walk frequency           ~ tau^+1/2      slope +1/2

So synthetic series are generated with each type and the implementation must recover each slope. A
known-good seat costs nothing here, and without it a slope read off real data is unfalsifiable.

THE ESTIMATOR, written from the definition rather than quoted. From phase (time-error) samples x_i
spaced tau0 apart, with tau = m.tau0, the OVERLAPPING Allan variance is

    sigma_y^2(tau) = 1 / (2 (N - 2m) tau^2) . sum_{i=1}^{N-2m} (x_{i+2m} - 2 x_{i+m} + x_i)^2

The second difference is what makes it blind to a constant offset AND to a constant rate, which is
the whole point: a clock's own fixed offset and fixed drift are not instability.

    python3 allan.py            validate against the four known noise types
"""
import math
import random


def adev_phase(x, tau0=1.0, taus=None):
    """overlapping Allan deviation from PHASE samples. Returns [(tau, sigma_y, n_terms), ...].

    Phase, not frequency, because clock products are published as time offsets. A tau is reported
    only when enough second differences exist to mean anything -- below that it is dropped rather
    than reported with a width it has not earned.
    """
    N = len(x)
    if taus is None:
        taus = []
        m = 1
        while 2 * m < N // 3:
            taus.append(m)
            m = max(m + 1, int(m * 1.6))
    out = []
    for m in taus:
        n = N - 2 * m
        if n < 8:                      # fewer than this and the estimate is noise about noise
            continue
        tau = m * tau0
        s = 0.0
        for i in range(n):
            d = x[i + 2 * m] - 2.0 * x[i + m] + x[i]
            s += d * d
        var = s / (2.0 * n * tau * tau)
        out.append((tau, math.sqrt(var), n))
    return out


def slope(points, lo_frac=0.0, hi_frac=1.0):
    """least squares slope of log(sigma) against log(tau), over a fraction of the tau range.

    The fit range is an argument and is always reported with the answer, because a slope read over
    a range chosen after seeing the curve is a slope chosen rather than measured.
    """
    p = [(t, s) for t, s, _n in points if s > 0]
    if len(p) < 3:
        return None, 0
    a = int(len(p) * lo_frac)
    b = max(a + 3, int(len(p) * hi_frac))
    p = p[a:b]
    xs = [math.log10(t) for t, _ in p]
    ys = [math.log10(s) for _, s in p]
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    den = sum((v - mx) ** 2 for v in xs)
    if den == 0:
        return None, n
    return sum((xs[i] - mx) * (ys[i] - my) for i in range(n)) / den, n


# --- the known-good seats: four noise types whose slopes are not in question --------------------
def white_phase(n, rng):
    return [rng.gauss(0, 1) for _ in range(n)]


def white_freq(n, rng):
    """phase is the integral of white frequency noise."""
    x, acc = [], 0.0
    for _ in range(n):
        acc += rng.gauss(0, 1)
        x.append(acc)
    return x


def random_walk_freq(n, rng):
    """phase is the double integral: frequency itself random-walks."""
    x, v, acc = [], 0.0, 0.0
    for _ in range(n):
        v += rng.gauss(0, 1)
        acc += v
        x.append(acc)
    return x


def flicker_freq(n, rng, poles=64, band=26.0):
    """1/f frequency noise by superposition of relaxations -- AND THE FIRST VERSION WAS WRONG.

    It summed unit-variance first-order filters with weight 1/sqrt(tc) and the recovered slope came
    out at -0.27 instead of 0. That survived its first test only because I had set the tolerance to
    0.30, which is a bar chosen to admit the result rather than to judge it. Widening the pole band
    from 12 to 32 octaves and the series from 4k to 32k samples moved it not at all (-0.27 to -0.31),
    while the three exact cases stayed tight -- so it was neither bandwidth nor the estimator.

    THE WEIGHT WAS WRONG BY A POWER OF tc, and the derivation says which. A unit-variance AR(1) with
    time constant tc has PSD proportional to tc / (1 + (w.tc)^2). Summing over geometrically spaced
    tc -- equal intervals in log tc -- with weight w = tc^p:
        p = 0     integrand tc/(1+(w.tc)^2) d(log tc)  ->  proportional to 1/w   == 1/f, FLICKER
        p = -0.5  integrand  1/(1+(w.tc)^2) d(log tc)  ->  constant              == WHITE
    I had shipped p = -0.5 and called it flicker. Scanned: p = -0.50 gives -0.256, p = -0.25 gives
    -0.144, and p = 0.00 gives +0.015. So the weight is 1, and the tolerance below is now 0.08 for
    all four cases instead of 0.30 for this one.
    """
    taus = [2.0 ** (k * band / poles) for k in range(poles)]
    state = [0.0] * poles
    y = []
    for _ in range(n):
        tot = 0.0
        for j, tc in enumerate(taus):
            a = math.exp(-1.0 / tc)
            state[j] = a * state[j] + math.sqrt(1 - a * a) * rng.gauss(0, 1)
            tot += state[j]            # weight 1: p = 0, which is the 1/f case
        y.append(tot)
    x, acc = [], 0.0
    for v in y:                        # integrate frequency to phase
        acc += v
        x.append(acc)
    return x


if __name__ == '__main__':
    N = 16384
    print('  VALIDATING THE ESTIMATOR ON FOUR CASES WITH KNOWN ANSWERS, %d samples each.\n' % N)
    print('  %-26s%12s%12s%10s%10s   %s'
          % ('noise type', 'expected', 'measured', 'error', 'n taus', 'verdict'))
    # ONE TOLERANCE FOR ALL FOUR. The first version gave flicker 0.30 and it passed at -0.27 --
    # a bar set wide enough to admit the answer is not a test. With the weight corrected, every case
    # is held to the same 0.08.
    cases = [('white phase', white_phase, -1.0, 0.08),
             ('white frequency', white_freq, -0.5, 0.08),
             ('flicker frequency', flicker_freq, 0.0, 0.08),
             ('random walk frequency', random_walk_freq, +0.5, 0.08)]
    passed = 0
    for name, gen, want, tol in cases:
        rng = random.Random(7)
        x = gen(N, rng)
        pts = adev_phase(x, tau0=1.0)
        # the fit range is FIXED IN ADVANCE at the middle of the tau decade span, not chosen after
        # looking at the curve, and it is the same range for every case
        sl, nt = slope(pts, 0.15, 0.75)
        ok = sl is not None and abs(sl - want) <= tol
        passed += ok
        print('  %-26s%12.2f%12s%10s%10d   %s'
              % (name, want, ('%.2f' % sl) if sl is not None else '-',
                 ('%+.2f' % (sl - want)) if sl is not None else '-', nt,
                 'PASS' if ok else 'FAIL (tolerance %.2f)' % tol))
    print('\n  %d of %d known cases recovered. %s' % (passed, len(cases),
          'The estimator may be pointed at real data.' if passed == len(cases)
          else 'IT MAY NOT BE USED until every known case is recovered -- a slope from an '
               'unvalidated estimator is unfalsifiable.'))
    print('\n  the fit range was fixed at 0.15-0.75 of the tau span BEFORE any curve was seen, and')
    print('  is the same for all four, as is the 0.08 tolerance. A range chosen after looking is a')
    print('  slope chosen rather than measured, and a tolerance widened to admit a case is not a')
    print('  test -- the first version of this file gave flicker 0.30 and passed it at -0.27.')


# --- THE THREE POSITIONS ON THE ESTIMATOR ITSELF -----------------------------------------------
# Added 11 Oct 2026, after a wipe. The validation above reported four slopes from ONE realisation
# each (random.Random(7)) with NO WIDTH, judged against a tolerance I had typed. And it folded the
# whole tau span into a SINGLE slope -- which is fatal rather than imprecise for real clock data,
# because real curves have KNEES: white at short tau, flicker at long, drift at longest. A slope
# averaged across regimes names none of them, and the question that matters is the slope at ONE
# particular tau.
#   OBSERVER   the ADEV at a given tau, from one realisation
#   WITNESS    its scatter across INDEPENDENT realisations -- the width it never had
#   TIME       how the slope MOVES across tau -- the trajectory, not the snapshot

def local_slope(points, window=4):
    """the slope as a function of tau, from a sliding log-log fit. Knees survive this; a single
    global fit erases them."""
    p = [(t, s) for t, s, _n in points if s > 0]
    out = []
    for i in range(len(p) - window + 1):
        seg = p[i:i + window]
        xs = [math.log10(t) for t, _ in seg]
        ys = [math.log10(s) for _, s in seg]
        n = len(xs)
        mx, my = sum(xs) / n, sum(ys) / n
        den = sum((v - mx) ** 2 for v in xs)
        if den == 0:
            continue
        sl = sum((xs[j] - mx) * (ys[j] - my) for j in range(n)) / den
        mid = seg[window // 2][0]
        out.append((mid, sl))
    return out


def with_width(gen, N, seeds=24, tau0=1.0):
    """ADEV at each tau WITH the scatter across independent realisations as its width.

    This is the width the first validation never had. The spread across seeds is the estimator's own
    noise, so an error is judged in units of it rather than against a bar I chose.
    """
    runs = []
    for s in range(seeds):
        runs.append(adev_phase(gen(N, random.Random(1000 + s)), tau0))
    m = min(len(r) for r in runs)
    out = []
    for i in range(m):
        tau = runs[0][i][0]
        vals = [r[i][1] for r in runs]
        mean = sum(vals) / len(vals)
        var = sum((v - mean) ** 2 for v in vals) / max(1, len(vals) - 1)
        out.append((tau, mean, math.sqrt(var), len(vals)))
    return out


def slope_with_width(gen, N, seeds=24, lo=0.15, hi=0.75):
    """the fitted slope and ITS scatter across realisations."""
    sls = []
    for s in range(seeds):
        pts = adev_phase(gen(N, random.Random(2000 + s)), 1.0)
        sl, _ = slope(pts, lo, hi)
        if sl is not None:
            sls.append(sl)
    if len(sls) < 3:
        return None, None, len(sls)
    mean = sum(sls) / len(sls)
    var = sum((v - mean) ** 2 for v in sls) / (len(sls) - 1)
    return mean, math.sqrt(var), len(sls)


def knee(n, rng, cross=64.0):
    """A KNOWN KNEE, so the knee reader has something it must find.

    White frequency plus flicker frequency, scaled so white dominates below `cross` and flicker
    above it. The local slope must therefore run near -0.5 at short tau and near 0 at long tau, with
    the handover near `cross`. A knee found in real data means nothing if the reader cannot find a
    constructed one.
    """
    a = white_freq(n, rng)
    b = flicker_freq(n, rng)
    # flicker's phase wanders far more; scale it so the two contribute equally at tau = cross
    pa = adev_phase(a, 1.0, taus=[int(cross)])
    pb = adev_phase(b, 1.0, taus=[int(cross)])
    k = (pa[0][1] / pb[0][1]) if (pa and pb and pb[0][1] > 0) else 1.0
    return [a[i] + k * b[i] for i in range(n)]
