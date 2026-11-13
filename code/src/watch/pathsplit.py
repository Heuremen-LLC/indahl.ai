#!/usr/bin/env python3
"""pathsplit.py -- A BETTER CLOCK READING FROM THE SAME PACKETS, via THE SPLIT.
(Bones, 11 Oct 2026.)

WHY. NTP computes offset = ((t1-t0) + (t2-t3))/2, which assumes the path is SYMMETRIC. If the
outbound and inbound legs differ by delta, the offset is wrong by delta/2 -- and that error is a
SYSTEMATIC AT ZERO FREQUENCY. No amount of averaging touches it. It is the same disease measured in
GNSS clock products the same evening: a contaminant sitting at the signal's own frequency, where
more samples shrink the noise and leave the systematic exactly where it was.

So the house's seat floors -- this Mac at about half of a 3.1 ms round trip -- are not noise to be
averaged down. They are an unmeasured asymmetry, and the question is whether it can be SEPARATED
rather than merely bounded.

THE SPLIT IS THE RULER FOR EXACTLY THIS, and the sheet states it: a difference separates into S, the
part common to every run, and P, the part that scales with the crossing. Here the crossing is the
ROUND TRIP, which is measured on every single packet:

    offset_i = S + P . rtt_i + noise

    S   the intercept at zero delay -- the clock's own error, path removed
    P   how much of the reading is the path, per second of round trip

Queueing delay is asymmetric in general, so the excess over the minimum round trip lands partly in
the offset. Regressing offset on rtt and taking the INTERCEPT estimates the offset a zero-delay path
would have given. That is a different estimator from both of the obvious two:
    the MEAN      averages the asymmetry in, so it is biased by whatever queueing happened
    the BEST-OF-n keeps the least-delayed packet, which is the right instinct but throws away n-1
                  readings and still reports whatever asymmetry the minimum packet carried, with no
                  width at all -- a maximum over n draws reported as a measurement
    the INTERCEPT uses every packet AND reports a width, and its slope P says how much of the seat's
                  floor was ever path to begin with

AND IT IS FALSIFIABLE BY A CONTROL THAT COSTS NOTHING. Armature sits on copper, this Mac on wifi. If
P is real, the wifi seat's slope must exceed the copper seat's. If both slopes are zero, the floors
are genuinely irreducible and the only remaining fix is physical -- put the seat on copper.

THE RAMP IS CHECKED FIRST AND IT IS NOT A NUISANCE. macOS timed SLEWS rather than steps, so after a
network bounce the offset walks for a long time. A walk inside the window would load straight into
the intercept, so a linear term in TIME is fitted alongside the one in rtt and reported in its own
right -- the slew rate is a reading about the seat's discipline, not an error to be removed quietly.

    python3 pathsplit.py <series.txt> [label]      lines: t0 offset rtt, or "t NONE NONE"
"""
import math
import sys

GAMMA = 0.5772156649015329


def load(path):
    """returns (t, offset, rtt) lists plus the four outcomes of a sample, counted separately.

    A lost exchange is NOTHING-RETURNED and is counted, never interpolated: an absence gets the same
    scrutiny as a presence, and a gap filled by a neighbour is a value the apparatus never produced.
    """
    t, off, rtt, lost, bad = [], [], [], 0, 0
    for line in open(path):
        f = line.split()
        if len(f) != 3:
            bad += 1
            continue
        if f[1] == 'NONE':
            lost += 1
            continue
        try:
            t.append(float(f[0])); off.append(float(f[1])); rtt.append(float(f[2]))
        except ValueError:
            bad += 1
    return t, off, rtt, lost, bad


def lstsq(cols, y):
    """normal equations with partial pivoting, plus the residual variance and parameter widths."""
    k, n = len(cols), len(y)
    A = [[sum(cols[i][m] * cols[j][m] for m in range(n)) for j in range(k)] for i in range(k)]
    b = [sum(cols[i][m] * y[m] for m in range(n)) for i in range(k)]
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    inv = [[1.0 if i == j else 0.0 for j in range(k)] for i in range(k)]
    for i in range(k):
        p = max(range(i, k), key=lambda r: abs(M[r][i]))
        if abs(M[p][i]) < 1e-30:
            return None
        M[i], M[p] = M[p], M[i]; inv[i], inv[p] = inv[p], inv[i]
        d = M[i][i]
        M[i] = [v / d for v in M[i]]; inv[i] = [v / d for v in inv[i]]
        for r in range(k):
            if r == i:
                continue
            f = M[r][i]
            if f:
                M[r] = [M[r][c] - f * M[i][c] for c in range(k + 1)]
                inv[r] = [inv[r][c] - f * inv[i][c] for c in range(k)]
    x = [M[i][k] for i in range(k)]
    res = [y[m] - sum(x[i] * cols[i][m] for i in range(k)) for m in range(n)]
    if n <= k:
        return x, [None] * k, None
    s2 = sum(r * r for r in res) / (n - k)
    se = [math.sqrt(s2 * inv[i][i]) if inv[i][i] > 0 else None for i in range(k)]
    return x, se, math.sqrt(s2)


def theilsen(x, y, stride=3, mate=7):
    """median of pairwise slopes. 29 per cent breakdown, so a handful of wild packets cannot move it.

    WHY THIS REPLACED LEAST SQUARES AS THE REPORTED FIT. The first version of this file fitted by
    ordinary least squares and quoted Gaussian widths from the residual variance. An NTP series is
    not Gaussian: one exchange whose reply queued behind something returns an offset wrong by tens of
    milliseconds, and the measured series carry exactly that -- a single 76.6 ms excursion in 240
    samples on a seat whose typical sample-to-sample step is 69 us, which is a thousand times the
    median. Least squares weights that sample by its square.

    THE COST, MEASURED, AND IT WAS A SIGN. Under least squares Armature read P = -0.496 +- 0.002,
    "254 widths from zero", and the Mac +0.479 +- 0.004 -- which was reported as two seats carrying
    their path asymmetry in OPPOSITE DIRECTIONS, the sign holding at enormous confidence. Refitted
    here: Armature is P = +0.245 +- 0.131, 1.9 widths, WHICH DOES NOT RESOLVE AND HAS THE OTHER
    SIGN. The opposite-direction finding was outliers, and the tight width was what made it look
    like a result instead of a guess.
    """
    sl = []
    for i in range(0, len(x), stride):
        for j in range(i + 1, len(x), mate):
            if x[j] != x[i]:
                sl.append((y[j] - y[i]) / (x[j] - x[i]))
    if not sl:
        return None, None
    b = median(sl)
    return median([y[k] - b * x[k] for k in range(len(x))]), b


def median(v):
    s = sorted(v)
    n = len(s)
    return s[n // 2] if n % 2 else 0.5 * (s[n // 2 - 1] + s[n // 2])


def boot(x, y, B=200, seed=5):
    """the width from a bootstrap, so it assumes nothing about the residual distribution."""
    import random
    random.seed(seed)
    n = len(x)
    out = []
    for _ in range(B):
        idx = [random.randrange(n) for _ in range(n)]
        a, b = theilsen([x[i] for i in idx], [y[i] for i in idx])
        if a is not None:
            out.append((a, b))
    if len(out) < 20:
        return None, None
    ma = sum(o[0] for o in out) / len(out)
    mb = sum(o[1] for o in out) / len(out)
    sa = math.sqrt(sum((o[0] - ma) ** 2 for o in out) / len(out))
    sb = math.sqrt(sum((o[1] - mb) ** 2 for o in out) / len(out))
    return sa, sb


def read(path, label=None):
    t, off, rtt, lost, bad = load(path)
    label = label or path
    n = len(off)
    if n < 30:
        print('  %-10s NOTHING RETURNED: only %d usable samples' % (label, n))
        return None
    t0 = t[0]
    ts = [x - t0 for x in t]
    span = ts[-1] - ts[0]
    rmin = min(rtt)
    # rtt is entered as EXCESS over the minimum, so the intercept is the zero-excess reading rather
    # than an extrapolation to a physically impossible rtt of zero
    ex = [r - rmin for r in rtt]
    ones = [1.0] * n
    tn = [x / span for x in ts]

    out = {'label': label, 'n': n, 'lost': lost, 'bad': bad, 'span': span, 'rmin': rmin}
    srt = sorted(rtt)
    out['rtt_min'] = rmin
    out['rtt_med'] = srt[n // 2]
    sof = sorted(off)
    out['off_med'] = sof[n // 2]
    out['off_mean'] = sum(off) / n
    # the best-of-n reading, which is what the earlier survey reported
    out['off_bestrtt'] = off[rtt.index(rmin)]

    fit = lstsq([ones, ex, tn], off)
    if fit is None:
        print('  %-10s REFUSED: design matrix singular' % label)
        return None
    x, se, resid = fit
    out['S_ols'] = x[0]; out['P_ols'] = x[1]
    out['S_ols_se'] = se[0]; out['P_ols_se'] = se[1]

    # SELECTION ON THE APPARATUS, never on the answer: exchanges whose ROUND TRIP is a gross
    # outlier are dropped, because the round trip is the apparatus and the offset is the subject.
    # Cutting on the offset would be choosing the result.
    med_rtt = median(rtt)
    kept = [(ex[i], off[i]) for i in range(n) if rtt[i] <= 8 * med_rtt]
    out['kept'] = len(kept)
    out['dropped_on_rtt'] = n - len(kept)
    if len(kept) >= 30:
        kx = [a for a, _b in kept]; ky = [b for _a, b in kept]
        a_r, b_r = theilsen(kx, ky)
        sa, sb = boot(kx, ky)
        # THE REPORTED FIT IS THE ROBUST ONE. The least-squares pair is kept beside it, because the
        # wrong first reading belongs next to the corrected one rather than deleted.
        out['S'] = a_r; out['S_se'] = sa
        out['P'] = b_r; out['P_se'] = sb
        out['fit'] = 'theil-sen, bootstrap width, %d of %d kept on rtt' % (len(kept), n)
    else:
        out['S'] = None; out['S_se'] = None; out['P'] = None; out['P_se'] = None
        out['fit'] = ('LA NADA: only %d exchanges survived the apparatus cut, too few for a robust '
                      'fit, and the least-squares pair is not reported as a substitute' % len(kept))
    out['slew'] = x[2] / span; out['slew_se'] = (se[2] / span) if se[2] else None
    out['resid'] = resid
    return out


def report(rows):
    print('  THE SPLIT ON THE HOUSE CLOCK: offset = S + P.(rtt excess) + slew.t\n')
    print('  %-10s%7s%6s%11s%11s%13s%13s' %
          ('seat', 'n', 'lost', 'rtt min', 'rtt med', 'mean off', 'best-of-n'))
    for r in rows:
        print('  %-10s%7d%6d%10.3fm%10.3fm%12.1fu%12.1fu'
              % (r['label'], r['n'], r['lost'], r['rtt_min']*1e3, r['rtt_med']*1e3,
                 r['off_mean']*1e6, r['off_bestrtt']*1e6))
    print('\n  %-10s%16s%18s%18s%12s' %
          ('seat', 'S (zero-delay)', 'P (path share)', 'slew rate', 'resid'))
    for r in rows:
        S = '%+.1f +- %.1f us' % (r['S']*1e6, r['S_se']*1e6) if r['S_se'] else '%+.1f us' % (r['S']*1e6)
        P = '%+.3f +- %.3f' % (r['P'], r['P_se']) if r['P_se'] else '%+.3f' % r['P']
        W = ('%+.1f +- %.1f us/s' % (r['slew']*1e6, r['slew_se']*1e6)
             if r['slew_se'] else '%+.1f us/s' % (r['slew']*1e6))
        print('  %-10s%16s%18s%18s%11.1fu' % (r['label'], S, P, W, r['resid']*1e6))
    print('\n  P is DIMENSIONLESS: the fraction of a round-trip excess that lands in the offset.')
    print('  P = 0.5 means the whole excess fell on one leg. P = 0 means the excess was symmetric')
    print('  and the round trip tells you nothing about the offset -- in which case the seat floor')
    print('  is irreducible by arithmetic and the only fix left is physical.')
    # 2026-10-11: THIS BLOCK USED TO BE THE VERY FAULT rail_reading WAS WRITTEN TO REFUSE.
    # It read P against ZERO only, with two outcomes and an if/else, while P has an arithmetic
    # bound at +-1/2 and BOTH ends are live alternatives. A seat one width from zero AND one
    # width from the rail got a verdict off whichever branch was typed first. rails() existed
    # for this and was never called from __main__ -- an instrument built and not read is the
    # same as not having built it. It is a REQUIRED FIELD now.
    print()
    for r in rows:
        name, note = rail_reading(r.get('P'), r.get('P_se'))
        wz = abs(r['P']) / r['P_se'] if r.get('P_se') else float('nan')
        wr = min(abs(RAIL - r['P']), abs(-RAIL - r['P'])) / r['P_se'] if r.get('P_se') else float('nan')
        print('    %-10s %.1f widths from 0, %.1f from the rail  ->  %-12s %s'
              % (r['label'], wz, wr, name.upper(), note))



# --- THE RAIL READING, and it REFUSES rather than picking a branch ---------------------------
# Added 11 Oct, immediately after a classifier of mine printed "AT THE RAIL" for a seat sitting 1.9
# widths from ZERO and 1.9 widths from the RAIL. Both alternatives were live and the if/elif order
# chose one. A ruler that cannot say "I cannot tell" lies at scale, and that one lied one line after
# the rule was quoted. So the decision is a REQUIRED FIELD now rather than a remembered caution.
#
# THE RAILS ARE ARITHMETIC, NOT FITTED. offset = ((t1-t0)+(t2-t3))/2 and rtt = t3-t0. A delay d
# applied entirely to the OUTBOUND leg moves t1, t2 and t3 each by +d, so offset moves +d/2 and rtt
# moves +d: P = +1/2 exactly. Inbound-only gives -1/2. A symmetric delay gives 0. So P is bounded to
# [-1/2, +1/2] by the definition of the protocol, and both ends are meaningful alternatives.

RAIL = 0.5


def rail_reading(P, P_se, widths=2.0):
    """four outcomes on P, and NEITHER is a legal answer. Returns (name, note).

    symmetric      P is within `widths` of 0 and NOT of a rail: the excess fell on both legs
                   equally, so the round trip says nothing about the offset and the floor is
                   irreducible by arithmetic
    one-sided      P is within `widths` of +-0.5 and NOT of 0: the whole excess fell on one leg
    partial        P is far from 0 AND far from both rails: genuinely in between
    cannot-tell    P is within `widths` of BOTH 0 and a rail -- the width is too large to separate
                   the two alternatives, which is LA NADA and is the reading, not a gap
    """
    if P is None or not P_se:
        return 'cannot-tell', 'no P or no width on it'
    near_zero = abs(P) <= widths * P_se
    near_rail = min(abs(RAIL - P), abs(-RAIL - P)) <= widths * P_se
    if near_zero and near_rail:
        return 'cannot-tell', ('%.3f +- %.3f is within %.1f widths of BOTH 0 and the rail: the two '
                               'alternatives are not separated' % (P, P_se, widths))
    if near_zero:
        return 'symmetric', 'the excess fell on both legs; nothing to remove'
    if near_rail:
        return 'one-sided', 'the whole excess fell on one leg, sign %s' % ('+' if P > 0 else '-')
    return 'partial', 'far from 0 and from both rails'


def rails(rows, widths=2.0):
    """bucket every seat through outcomes.py so the set is proved exhaustive and disjoint."""
    import outcomes
    tagged = [dict(r, rail=rail_reading(r.get('P'), r.get('P_se'), widths)[0]) for r in rows]
    o = outcomes.Outcomes(subject=[('symmetric', lambda r: r['rail'] == 'symmetric'),
                                   ('one-sided', lambda r: r['rail'] == 'one-sided'),
                                   ('partial', lambda r: r['rail'] == 'partial')],
                          apparatus=[('cannot-tell', lambda r: r['rail'] == 'cannot-tell')])
    o.tally(tagged, 'the path split')
    return tagged, o


# 2026-10-11: the entry point sits at the BOTTOM now. It used to run above rail_reading(),
# so wiring the rail reader into report() raised NameError -- the guard was present in the file
# and absent at the moment it was needed, which is the same as not having it.

if __name__ == '__main__':
    args = sys.argv[1:]
    rows = []
    while args:
        p = args.pop(0)
        lab = args.pop(0) if args and not args[0].endswith('.txt') else None
        r = read(p, lab)
        if r:
            rows.append(r)
    if rows:
        report(rows)
        try:
            print()
            rails(rows)          # proves the four outcomes exhaustive and disjoint, via outcomes.py
        except Exception as e:
            print('  rails(): %s: %s' % (type(e).__name__, e))
