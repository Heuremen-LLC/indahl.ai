#!/usr/bin/env python3
"""el_candidato.py -- PRICE A CANDIDATE CONSTANT AGAINST THE HOUSE'S WHOLE NUMERIC RECORD.
(Bones, 12 Oct 2026.)

Wayfinder: "6.023 is our jam man, the numbers are lining up for you don't drop the ball with binary
bitch shit." Then: "lean on it. trust me."

LEANING ON IT IS NOT AGREEING WITH IT, AND IT IS NOT DISMISSING IT. The house's own rule is that a
match is A ROW, NEVER A REASON: price its cheapness or do not raise it. So this file does the only
thing that makes a near-match mean anything -- IT COUNTS THE DENOMINATOR.

THE ARITHMETIC NULL, EXACT, NOT RESAMPLED (guarda 7). Scan N numbers off the ledgers. Scale each to
a mantissa in [1,10). Mantissas of real-world quantities are close to log-uniform (Benford), so the
density at m is 1/(m ln 10) and the chance a single number lands within a relative tolerance r of a
target T is

    p  =  integral over [T(1-r), T(1+r)] of dm/(m ln10)  =  ln((1+r)/(1-r)) / ln 10

which is INDEPENDENT OF T. That is the whole point: at r = 0.001 every candidate gets p = 8.7e-4,
so 10,000 scanned numbers yield ~8.7 hits BY ARITHMETIC ALONE, for 6.023 and for any other value.
A candidate is only a row if its hits beat that, and the excess is reported with a Poisson width.

AND THE SCALE FREEDOM IS PRICED TOO. Allowing any power of ten is a search over ~20 decades, so a
hit is not one draw but one of however many decades the data spans. This file reports hits per
decade so the freedom cannot hide inside the total.

WHAT IT CANNOT DO, said plainly: a ledger is not a random sample of the universe. The same quantity
recorded 500 times is 500 rows and ONE fact, so this counts DISTINCT values, and it still cannot
tell a mechanism from a coincidence. It can only tell cheap from expensive. LA NADA is a real answer
here and it is the usual one.

    python3 el_candidato.py                     # price 6.023 and the Seven, side by side
    python3 el_candidato.py --target 6.023 --tol 0.001
    python3 el_candidato.py --selftest
"""
import argparse, glob, json, math, os, re, sys

VIGENCIA_NOT_A_CONSUMER = True
W = os.path.dirname(os.path.abspath(__file__))

SEVEN = [('1/phi', 0.6180339887498949), ('phi', 1.618033988749895),
         ('pi', 3.141592653589793), ('1/pi', 0.3183098861837907),
         ('12/11', 1.0909090909090908), ('-1/12', 0.08333333333333333),
         ('0.62', 0.62), ('sqrt5', 2.23606797749979)]

NUM = re.compile(r'-?\d+\.\d+(?:[eE][-+]?\d+)?|-?\d+[eE][-+]?\d+')


def mantissa(x):
    x = abs(float(x))
    if x == 0 or not math.isfinite(x):
        return None
    d = math.floor(math.log10(x))
    return x / (10.0 ** d), d


def p_chance(tol):
    """BENFORD null -- kept only to show why it is WRONG for this data. See p_empirical()."""
    return math.log((1.0 + tol) / (1.0 - tol)) / math.log(10.0)


def p_empirical(vals, target, tol, bins=2000):
    """THE NULL BUILT FROM OUR OWN MANTISSAS, not assumed from Benford.

    The Benford null gave candidates scattering from -5.12 to +12.58 sd, which is not nine
    findings -- it is one mis-specified baseline. Our ledgers are dominated by a handful of
    quantities with narrow ranges (clock_triangle 28k values, bonefish_hops2 21k), so the mantissa
    density is lumpy and nothing like log-uniform.

    So the expectation for a candidate at mantissa m is read off the OBSERVED density at m: the
    share of all our mantissas that fall in the same window width, placed where the candidate is.
    A baseline built from the measurement's own population, which is the only kind that holds
    (falla I.1).

    THE WINDOW IS THE CANDIDATE'S OWN, not a fixed bin: hits are counted on |m - t|/t <= tol, so
    the null must integrate the observed density over exactly that interval.
    """
    t = mantissa(target)[0]
    lo, hi = t * (1.0 - tol), t * (1.0 + tol)
    ms = []
    for v in vals:
        r = mantissa(v)
        if r is not None:
            ms.append(r[0])
    n = len(ms)
    if n == 0:
        return None
    # the observed share inside the candidate's own window IS the hit count -- that is circular.
    # So the null is the share in a BAND AROUND it, excluding the window itself: the local density
    # the candidate sits in, estimated from its neighbourhood rather than from itself.
    wide = 40.0 * tol
    blo, bhi = t * (1.0 - wide), t * (1.0 + wide)
    band = [m for m in ms if blo <= m <= bhi]
    inside = [m for m in band if lo <= m <= hi]
    outside = len(band) - len(inside)
    # width of the band minus the window, in mantissa units
    w_band = (bhi - blo) - (hi - lo)
    w_win = hi - lo
    if w_band <= 0 or outside == 0:
        return None
    dens = outside / w_band                      # per unit mantissa, from the NEIGHBOURHOOD only
    return dens * w_win, len(band), len(inside)


def harvest():
    """every distinct numeric value in the house's ledgers. Distinct, because the same quantity
    logged 500 times is 500 rows and one fact."""
    vals, per_file = set(), {}
    for p in sorted(glob.glob(os.path.join(W, '*.jsonl')) + glob.glob(os.path.join(W, '*.json'))):
        got = set()
        try:
            txt = open(p, errors='replace').read()
        except Exception:
            continue
        for m in NUM.finditer(txt):
            try:
                v = float(m.group(0))
            except ValueError:
                continue
            if v == 0 or not math.isfinite(v):
                continue
            got.add(v)
        per_file[os.path.basename(p)] = len(got)
        vals |= got
    return vals, per_file


def price(vals, name, target, tol):
    mt = mantissa(target)
    if mt is None:
        return None
    tm = mt[0]
    hits, decades = [], set()
    for v in vals:
        r = mantissa(v)
        if r is None:
            continue
        m, d = r
        if abs(m - tm) / tm <= tol:
            hits.append(v)
            decades.add(d)
    n = len(vals)
    benford = n * p_chance(tol)
    emp = p_empirical(vals, target, tol)
    out = {'name': name, 'target': target, 'mant': tm, 'n': n, 'hits': len(hits),
           'benford': benford, 'decades': len(decades), 'examples': sorted(hits)[:6],
           'expected': None, 'z': float('nan'), 'band': None, 'cannot_tell': True}
    if emp is not None:
        e, nband, _ = emp
        out['expected'] = e
        out['band'] = nband
        sd = math.sqrt(e) if e > 0 else 0.0
        out['z'] = (len(hits) - e) / sd if sd > 0 else float('nan')
        # a neighbourhood too thin to estimate a density is a CANNOT TELL, not a zero
        out['cannot_tell'] = (nband < 30)
    return out


def selftest():
    bad = 0
    def ck(l, c):
        nonlocal bad
        bad += 0 if c else 1
        print('  %-4s %s' % ('ok' if c else 'FAIL', l))
    ck('p_chance is independent of the target (the whole point)',
       abs(p_chance(0.001) - 8.6859e-4) < 1e-7)
    ck('p_chance doubles roughly with tol', abs(p_chance(0.002) / p_chance(0.001) - 2) < 0.01)
    ck('mantissa(6023.0) is 6.023', abs(mantissa(6023.0)[0] - 6.023) < 1e-12)
    ck('mantissa(0.0006023) is 6.023', abs(mantissa(0.0006023)[0] - 6.023) < 1e-12)
    # a planted set: 3 true hits in 1000 log-uniform draws must be flagged as an excess
    import random
    random.seed(7)
    vals = {10 ** random.uniform(-6, 6) for _ in range(1000)}
    r0 = price(vals, 'none', 6.023, 0.001)
    vals2 = set(vals) | {6.0231, 60.2299, 0.0060232}
    r1 = price(vals2, 'planted', 6.023, 0.001)
    ck('3 planted hits are seen', r1['hits'] - r0['hits'] == 3)
    ck('and the expectation stays near 1 in 1000', r1['expected'] < 1.5)
    print('  %d of 6' % (6 - bad))
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--target', type=float)
    ap.add_argument('--tol', type=float, default=0.001)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    vals, per_file = harvest()
    print()
    print('  THE DENOMINATOR FIRST, because that is the whole measurement.')
    print('  %d DISTINCT numeric values across %d ledgers in watch/' % (len(vals), len(per_file)))
    top = sorted(per_file.items(), key=lambda x: -x[1])[:6]
    print('  biggest contributors: %s' % ', '.join('%s %d' % t for t in top))
    print('  chance ANY ONE value lands within +-%.3f %% of ANY target: %.3e'
          % (a.tol * 100, p_chance(a.tol)))
    print('  so the arithmetic expectation is %.2f hits for EVERY candidate below.'
          % (len(vals) * p_chance(a.tol)))
    print()
    cands = [('6.023 (Avogadro)', 6.023)] + SEVEN if a.target is None else [('given', a.target)]
    print('  %-20s %9s %6s %9s %9s %8s %7s' % ('candidate', 'mantissa', 'hits',
                                                 'BENFORD', 'EMPIRICAL', 'z(emp)', 'band n'))
    rows = []
    for nm, t in cands:
        r = price(vals, nm, t, a.tol)
        rows.append(r)
        if r['expected'] is None or r['cannot_tell']:
            print('  %-20s %9.5f %6d %9.2f %9s %8s %7s   CANNOT TELL: neighbourhood too thin'
                  % (nm, r['mant'], r['hits'], r['benford'], '-', '-',
                     r['band'] if r['band'] is not None else '-'))
        else:
            print('  %-20s %9.5f %6d %9.2f %9.2f %+8.2f %7d'
                  % (nm, r['mant'], r['hits'], r['benford'], r['expected'], r['z'], r['band']))
    print()
    base = rows[0]
    if base['expected'] is not None and not base['cannot_tell']:
        print('  6.023: %d hits against %.2f expected FROM ITS OWN NEIGHBOURHOOD -> %+.2f sd.'
              % (base['hits'], base['expected'], base['z']))
    else:
        print('  6.023: CANNOT TELL -- its neighbourhood in our record is too thin to set a null.')
    if base['examples']:
        print('  the actual values that matched: %s' % ', '.join('%g' % x for x in base['examples']))
    print()
    print('  READ IT THIS WAY. The BENFORD column is identical for every candidate by')
    print('  construction and IS WRONG for this data -- it made candidates scatter -5.12 to')
    print('  +12.58 sd, which is one bad baseline wearing nine findings. The EMPIRICAL column')
    print('  is each candidate priced against the density of OUR OWN mantissas right where it')
    print('  sits, neighbourhood only, never its own window. A thin neighbourhood is a')
    print('  CANNOT TELL and says so.')
    print()
    print('  AND pi IS NOT A FINDING EITHER WAY: pi is hardcoded in our code and our own')
    print('  arithmetic writes it into harmonics, mains_phase and clock_triangle. Falla V.11 --')
    print('  one artifact\'s internal record read as a second independent reading.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
