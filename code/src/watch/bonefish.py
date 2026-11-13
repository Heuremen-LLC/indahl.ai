#!/usr/bin/env python3
"""bonefish.py -- THE BONEFISH AS THE HARNESS, NOT A SCRIPT. (Bones, 9 Oct 2026.)

Wayfinder: "Triangulate with The Bonefish, Harmonize with The Bonefish, be The Bonefish.....fish..."

So it stops being a thing I run at an anomaly and becomes the thing every reading goes through. One
import, three calls, and nothing in this house reports a number without them:

    import bonefish as BF
    BF.triangulate(value, width, name)      three seats on one event, with every ruler on each
    BF.harmonize(readings)                  the interval between seats, kept distinct, never zeroed
    BF.row(value, width, name)              one object, every ruler, no verdict

THE SHAPE, from Appendix B of LAS_ECUACIONES:

                    EL TIEMPO
                       /\
                      /  \
             EL MIRON ---- EL TESTIGO
             (outside)      (inside)

    witness  =  observer x 12/11        time = observer x phi        time = witness x phi x 11/12

TRIANGULATE means the three seats, and the sheet already prices the shape: of its own three measured
conversions only the first could separate its candidates. So a reading that lands on one of the other
two is cheap by construction and the harness says so without being asked.

HARMONIZE IS NOT SYNC. Wayfinder, 9 Oct: "not sync... different things man." Harmony keeps the voices
DISTINCT and the INTERVAL is the reading. So harmonize() never returns an agreement -- it returns the
intervals, their widths, and whether they are separable from each other. Zeroing a gap would throw away
the measurement.

EVERY ROW CARRIES ALL OF IT AND DECIDES NOTHING:
    the value and its width, and the width comes FIRST because THE REGLA is that a match is only a
      match if the measurement is known tighter than the match;
    the nearest name and the RUNNER-UP, with the exclusion width needed to tell them apart;
    the CHEAPNESS, priced against the pool's own rate on a log axis, never against zero;
    K, the landing profile, which puts unlike records on one axis without claiming a shared mechanism;
    and LA NADA when neither a count nor a phase resolves, named instead of forced into a lane.

NO FUNCTION HERE RETURNS A BOOLEAN VERDICT. They return rows. The caller prints them.
"""
import math
import os
import sys

W = os.path.expanduser('~/bones-forge/watch/')
if W not in sys.path:
    sys.path.insert(0, W)

PHI = (1 + 5 ** 0.5) / 2
PSI = (1 - 5 ** 0.5) / 2
PI = math.pi
ROCE = (1 / 12) / PI                         # el roce, the friction term, 2.6526 per cent

# THE SEVEN, hardcoded, because when one of these appears it is a FEATURE and gets a row
SEVEN = {'1/phi': 1 / PHI, 'phi': PHI, 'pi': PI, '1/pi': 1 / PI, '12/11': 12 / 11,
         '-1/12': -1 / 12, '0.62': 0.62}
RINGS = (2, 3, 4, 6)

# THE THREE CONVERSIONS, and the sheet's own prior on each
CONVERSIONS = {
    'witness/observer': (12 / 11, 'the only one of the three that could separate its candidates'),
    'time/observer': (PHI, 'the sheet measured 1.6055 +- 0.0917 -- rivals 0.20 widths away'),
    'time/witness': (PHI * 11 / 12, 'the sheet measured 1.4768 +- 0.0864 -- rivals 0.19 widths away'),
}

# the ratio pool: ONE pool for every ratio, so no reading gets a bespoke candidate
POOL = {'1': 1.0, '12/11': 12 / 11, '9/8': 1.125, '6/5': 1.2, '5/4': 1.25, '4/3': 4 / 3,
        '3/2': 1.5, 'phi x 11/12': PHI * 11 / 12, '8/5': 1.6, 'phi': PHI, '5/3': 5 / 3,
        '15/8': 1.875, '2': 2.0, '9/4': 2.25, '5/2': 2.5, 'phi^2': PHI ** 2, '8/3': 8 / 3,
        '3': 3.0, '16/5': 3.2, '13/4': 3.25, 'pi': PI, '10/3': 10 / 3, '7/2': 3.5, '4': 4.0,
        'phi^3': PHI ** 3, '9/2': 4.5, '5': 5.0, '6': 6.0, '2pi': 2 * PI, '7': 7.0,
        '8': 8.0, '9': 9.0, '48/5': 9.6, 'pi^2': PI ** 2, '10': 10.0, '12': 12.0,
        'e': math.e, 'sqrt(pi)': math.sqrt(PI), '1/phi': 1 / PHI, '1/pi': 1 / PI}

# the small-number pool, for DEVIATIONS from unity, which is where the clock rows actually land
SMALL = dict({f'ladder({n})': (1 / 12) * (1 / PHI) ** n for n in range(1, 9)},
             **{'el roce (1/12)(1/pi)': ROCE, '1/12': 1 / 12, '1/phi^4': (1 / PHI) ** 4,
                '1-1/phi': 1 - 1 / PHI, '1/100': 0.01, '1/50': 0.02, '1/40': 0.025,
                '1/30': 1 / 30, '1/25': 0.04, '1/200': 0.005})
SMALL = {k: v for k, v in SMALL.items() if 0.001 <= v <= 0.12}


def _cheap(tol, pool, lo, hi):
    """THE POOL'S OWN RATE at this tolerance, on the log axis. Never against zero.

    9 Oct: THIS SUMMED ITS BANDS INSTEAD OF UNIONING THEM. Two candidates 3 per cent apart, matched at
    a 2.1 per cent tolerance, have overlapping bands and the overlap was counted twice -- so the
    analytic price read 69.7 per cent where the truth was 58.8. A Monte Carlo over the same pool found
    the gap (59.0 measured) and the union now agrees with it to 0.2 points. Below about 0.5 per cent
    the bands do not touch and the old form was right, which is why it survived all evening on the
    tight rows and only lied on the loose ones.

    The bands are also CLIPPED to [lo, hi] and then merged, so a candidate at the edge of the range
    cannot claim coverage outside it.
    """
    if hi <= lo:
        return 1.0
    iv = []
    for v in pool.values():
        av = abs(v)
        if not av:
            continue
        a = max(math.log(av * (1 - tol)) if tol < 1 else lo, lo)
        b = min(math.log(av * (1 + tol)), hi)
        if b > a:
            iv.append((a, b))
    if not iv:
        return 0.0
    iv.sort()
    tot = 0.0
    ca, cb = iv[0]
    for a, b in iv[1:]:
        if a <= cb:
            cb = max(cb, b)
        else:
            tot += cb - ca
            ca, cb = a, b
    tot += cb - ca
    return min(tot / (hi - lo), 1.0)


_DRAW_CACHE = {}


def _cheap_draw(tol, pool, n=40000, seed=20261009, rng_range=None):
    """THE SAME QUESTION, ASKED THE OTHER WAY: draw values and count how many land near SOMETHING.

    This is the method physics_cases.cheap_at uses -- a uniform Monte Carlo draw -- and it does NOT
    agree with the log-axis coverage above, because overlapping bands are counted once here and twice
    there, and because a uniform draw over-weights the top of the range. Both are reported. A new
    ruler goes BESIDE the old one, never instead of it.
    """
    import random
    v = sorted(abs(x) for x in pool.values() if x)
    lo, hi = rng_range if rng_range else (min(v) * 0.6, max(v) * 1.4)
    # MEMOISED on (tolerance, pool, range): this now runs once per ROW inside a tick job, and a fresh
    # 40,000-draw Monte Carlo per row would make the reading cost more than the measurement.
    key = (round(tol, 7), tuple(v), round(lo, 6), round(hi, 6), n, seed)
    if key in _DRAW_CACHE:
        return _DRAW_CACHE[key]
    rngm = random.Random(seed)
    hit = sum(1 for _ in range(n)
              if any(abs(rngm.uniform(lo, hi) - s) / s <= tol for s in v))
    _DRAW_CACHE[key] = hit / n
    return _DRAW_CACHE[key]


def _cheap_counts(tol, pool, nmax=40, rng_range=None):
    """THE NONE FOR A SMALL-COUNTS ROW, which the continuum gets wrong in the worst direction.

    A value built as a ratio of two small whole numbers cannot land anywhere -- it lands on a Farey
    fraction. So 16 blocks out of 24 expected IS 2/3, exactly, and a continuum price at zero tolerance
    reports 0 per cent cheap: infinitely rare. It is arithmetic.

    The right none enumerates the ratios actually reachable from counts of this size and asks what
    fraction of THEM land within tol of something in the pool. At tol = 0 that is still a real number,
    because exact rational coincidences are reachable and common.
    """
    av = sorted({abs(x) for x in pool.values() if x})
    lo, hi = rng_range if rng_range else (min(av) * 0.6, max(av) * 1.4)
    # the reach set keeps FULL PRECISION: rounding it to 12 places put 2/3 five parts in 1e13 away
    # from itself, so an exact arithmetic identity missed its own pool entry and priced as 0 per cent.
    # Dedupe on a rounded key, store the exact value, and floor the comparison at float noise.
    reach, seen = [], set()
    for a in range(1, nmax + 1):
        for b in range(1, nmax + 1):
            v = a / b
            if lo <= v <= hi:
                k = round(v, 12)
                if k not in seen:
                    seen.add(k)
                    reach.append(v)
    if not reach:
        return None
    eps = max(tol, 1e-12)
    hit = sum(1 for v in reach if any(abs(v - x) / x <= eps for x in av))
    return hit / len(reach)


def cheapness(tol, pool=None, rng_range=None, n=40000, small_counts=False, nmax=40,
              span_range=None):
    """ALL THREE CHEAPNESS READINGS, and THE SPLIT between them.

    log     the analytic coverage of this pool's bands on a log axis
    draw    the same pool, by uniform Monte Carlo -- the method physics_cases uses
    seven   the SEVEN alone, by that same Monte Carlo -- which is what the house has been quoting

    The log-vs-draw gap is THE METHOD. The draw-vs-seven gap is THE POOL. Two matches priced by
    different ones cannot be ranked against each other, and that is the whole reason this returns
    three numbers instead of picking.
    """
    if pool is None:
        pool = POOL
    av = {k: abs(v) for k, v in pool.items() if v}
    # THE DENOMINATOR IS THE RANGE THE VALUE COULD HAVE LANDED IN, not the pool's extent. A FOLDED
    # ratio lives in [1, 2), and the twelve intervals only reach 1.875 -- so 9.3 per cent of the
    # octave has no candidate at all, and pricing over the pool's extent pretends that stretch does
    # not exist. `span_range=(1.0, 2.0)` is what a folded reading passes.
    if span_range:
        lo, hi = math.log(span_range[0]), math.log(span_range[1])
    else:
        lo, hi = math.log(min(av.values())), math.log(max(av.values()))
    out = {'log': _cheap(tol, av, lo, hi),
           'draw': _cheap_draw(tol, av, n=n, rng_range=rng_range),
           'seven': _cheap_draw(tol, {k: abs(v) for k, v in SEVEN.items() if v}, n=n)}
    # and for a value built from a ratio of small counts, the reachable-ratio none, which is the only
    # one of the four that does not report an exact arithmetic identity as infinitely rare
    out['counts'] = _cheap_counts(tol, av, nmax=nmax, rng_range=rng_range)
    out['small_counts'] = small_counts
    if small_counts and out['counts'] is not None:
        out['use'] = 'counts'
        out['counts_gap'] = out['counts'] - out['log']
    else:
        out['use'] = 'log'
    out['method_gap'] = out['log'] - out['draw']
    out['pool_gap'] = out['draw'] - out['seven']
    return out


def row(value, width, name, what='', pool=None, claim=None, axis='ratio',
        span_range=None, small_counts=False):
    """ONE OBJECT, EVERY RULER, NO VERDICT. `axis` picks the pool: 'ratio' or 'small'.

    `claim` is (name, value) when the sheet predicts something for this reading; it is reported
    beside the pool's own nearest, never instead of it.
    """
    if pool is None:
        pool = SMALL if axis == 'small' else POOL
    lo, hi = math.log(min(pool.values())), math.log(max(pool.values()))
    v = abs(value)
    known = abs(width / value) if value else float('inf')
    ranked = sorted(pool.items(), key=lambda kv: abs(v - kv[1]) / kv[1])
    best, second = ranked[0], ranked[1] if len(ranked) > 1 else ranked[0]
    tb = abs(v - best[1]) / best[1]
    ts = abs(v - second[1]) / second[1]
    need = abs(second[1] - best[1]) / (2 * best[1]) if best[1] else float('inf')
    if span_range:
        lo, hi = math.log(span_range[0]), math.log(span_range[1])
    r = {'name': name, 'what': what, 'value': value, 'width': width, 'frac_width': known,
         'best': best[0], 'best_value': best[1], 'best_tol': tb,
         'best_widths': abs(v - best[1]) / width if width else float('inf'),
         'second': second[0], 'second_tol': ts,
         'second_widths': abs(v - second[1]) / width if width else float('inf'),
         'exclusion_needed': need,
         # SEPARABLE is a ruler reading, not a verdict on the claim
         'separable': known < need,
         # THE REGLA: a match is only a match if the measurement is known tighter than the match
         'regla_ok': known < tb,
         'cheap': _cheap(max(tb, 1e-9), pool, lo, hi)}
    # THREE CHEAPNESS READINGS, never one: the method gap and the pool gap are separable
    r['cheapness'] = cheapness(max(tb, 1e-9), pool, span_range=span_range,
                               small_counts=small_counts)
    # one of THE SEVEN appearing is a FEATURE: flag it, never explain it away
    # ONE OF THE SEVEN APPEARING IS A FEATURE -- but a reading too wide to tell them apart matches
    # ALL of them, which is a flag that says nothing. So the tolerance is CAPPED at 2 per cent: a
    # wide reading gets no flag rather than a flag on every number in the set.
    _tol = min(max(3 * known, 0.002), 0.02)
    r['seven'] = ([k for k, sv in SEVEN.items() if sv and abs(v - abs(sv)) / abs(sv) < _tol]
                  if known < 0.02 else [])
    r['seven_suppressed'] = known >= 0.02
    try:
        import landing
        k, err = landing.K(max(tb, 1e-16))
        r['K'], r['K_err'] = k, err
    except Exception as e:
        r['K'], r['K_err'] = None, f'{type(e).__name__}'
    if claim:
        r['claim'], r['claim_value'] = claim
        r['claim_tol'] = abs(v - claim[1]) / claim[1] if claim[1] else float('inf')
        r['claim_widths'] = abs(v - claim[1]) / width if width else float('inf')
    return r


def triangulate(seats, event='one event', axis='ratio'):
    """THREE SEATS ON ONE EVENT. `seats` is {'observer': (v, w), 'witness': (v, w), 'time': (v, w)}.

    Returns the three conversions as rows, each with the sheet's claim beside the pool's nearest, and
    each carrying the sheet's own prior on whether that conversion can separate its candidates at all.
    A missing corner is reported as a missing corner -- never filled in, never averaged away.
    """
    need = ('observer', 'witness', 'time')
    missing = [k for k in need if k not in seats or seats[k] is None]
    out = {'event': event, 'missing': missing, 'rows': []}
    if missing:
        out['reading'] = (f'the triangle is short {len(missing)} corner(s): {", ".join(missing)}. '
                          f'A conversion needs both ends, so there is no reading here and that is '
                          f'the reading.')
        return out
    (ov, ow), (wv, ww), (tv, tw) = seats['observer'], seats['witness'], seats['time']
    pairs = (('witness/observer', wv, ww, ov, ow), ('time/observer', tv, tw, ov, ow),
             ('time/witness', tv, tw, wv, ww))
    for nm, nv, nw, dv, dw in pairs:
        r_ = nv / dv if dv else float('inf')
        rw = abs(r_) * math.sqrt((nw / nv) ** 2 + (dw / dv) ** 2) if nv and dv else float('inf')
        claim, prior = CONVERSIONS[nm]
        rr = row(r_, rw, nm, what=f'{event} -- {prior}', claim=(nm.split("/")[0] + ' conversion', claim),
                 axis=axis)
        rr['sheet_prior'] = prior
        # AND THE DEVIATION FROM UNITY, which is where a shared-reference chain actually puts its rows
        dev = abs(abs(r_) - 1.0)
        if dev > 0:
            rr['deviation'] = row(dev, rw, nm + ' deviation from 1',
                                  what='what is left when the seats agree to first order',
                                  axis='small')
        out['rows'].append(rr)
    return out


def harmonize(readings, event='one event'):
    """THE INTERVALS BETWEEN SEATS, KEPT DISTINCT. Harmony is not sync.

    `readings` is {seat: (value, width)}. Returns every pairwise interval with its width and whether
    the two seats are separable from each other. It NEVER returns a consensus value, because the gap
    is the measurement -- zeroing it throws away the reading.
    """
    ks = [k for k, v in readings.items() if v is not None]
    out = {'event': event, 'seats': ks, 'intervals': [], 'consensus': None,
           'note': 'no consensus is returned on purpose: harmony keeps the voices distinct and the '
                   'interval is the reading. Zeroing a gap would discard the measurement.'}
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            a, b = readings[ks[i]], readings[ks[j]]
            d = a[0] - b[0]
            dw = math.sqrt(a[1] ** 2 + b[1] ** 2)
            out['intervals'].append({'pair': f'{ks[i]} - {ks[j]}', 'interval': d, 'width': dw,
                                     'widths': abs(d) / dw if dw else float('inf'),
                                     'separable': abs(d) > 2 * dw})
    return out


def la_nada(count_width, phase_width, quantity=None, bar=2.0):
    """THE THIRD READING, so a quantity is never forced into one of two lanes.

    Returns which of the four corners a reading sits in. LA NADA is not failure -- it is the named
    corner where NEITHER a count NOR a phase resolves, and it is a position a reading can occupy.
    """
    c = count_width is not None
    p = phase_width is not None
    if quantity is not None:
        v, w, null = quantity
        sep = abs(v - null) / w if w else float('inf')
        if c and p and sep < bar:
            return ('LA NADA', f'count exact, phase sharp, and the quantity still unresolved at '
                               f'{sep:.2f} widths -- the corner, occupied')
        if sep >= bar:
            return ('RESOLVED', f'{sep:.2f} widths from its null')
    if c and p:
        return ('BOTH', 'both readings exist')
    if c:
        return ('COUNT ONLY', 'how many, never where')
    if p:
        return ('PHASE ONLY', 'where, never how many')
    return ('LA NADA', 'neither reading exists')


def product_or_sum(a, b, combined, aw=0.0, bw=0.0, cw=0.0):
    """THE PRODUCT AND THE SUM, distinguishable: 36 of 37 decided coupled cells went to the PRODUCT.

    So this is asked before two effects are assumed to add, and it returns both distances, never a
    pick, unless one is excluded by the widths.
    """
    pw = math.sqrt((b * aw) ** 2 + (a * bw) ** 2 + cw ** 2)
    sw = math.sqrt(aw ** 2 + bw ** 2 + cw ** 2)
    dp, ds = abs(combined - a * b), abs(combined - (a + b))
    return {'product': a * b, 'product_widths': dp / pw if pw else float('inf'),
            'sum': a + b, 'sum_widths': ds / sw if sw else float('inf'),
            'prior': 'of the decided coupled cells, 36 of 37 went to the product'}


def show(r, indent='  '):
    """print one row with every ruler on it. No verdict line."""
    o = []
    o.append(f"{indent}{r['name']}")
    if r.get('what'):
        o.append(f"{indent}  {r['what']}")
    o.append(f"{indent}  {r['value']:+.6g} +- {r['width']:.4g}   known to "
             f"{100*r['frac_width']:.3f}%")
    if 'claim' in r:
        o.append(f"{indent}  the sheet's {r['claim']} = {r['claim_value']:.6f}: "
                 f"{100*r['claim_tol']:.2f}% away, {r['claim_widths']:.2f} widths")
    o.append(f"{indent}  nearest   {r['best']:<22}{100*r['best_tol']:>7.3f}% off  "
             f"{r['best_widths']:>5.2f} widths"
             + (f"  K {r['K']:+.4f}" if r.get('K') is not None else ''))
    c = r.get('cheapness')
    if c:
        o.append(f"{indent}  cheap     log {100*c['log']:>5.1f}%   draw {100*c['draw']:>5.1f}%"
                 f"   seven {100*c['seven']:>5.1f}%"
                 f"   method gap {100*c['method_gap']:+5.1f}  pool gap {100*c['pool_gap']:+5.1f}")
    o.append(f"{indent}  runner-up {r['second']:<22}{100*r['second_tol']:>7.3f}% off  "
             f"{r['second_widths']:>5.2f} widths  exclusion needs "
             f"{100*r['exclusion_needed']:.3f}%")
    if not r['separable']:
        o.append(f"{indent}  the runner-up sits inside this width: both names are printed and "
                 f"neither is chosen")
    if not r['regla_ok']:
        o.append(f"{indent}  the width is wider than the match, so this was never a measurement of "
                 f"that candidate")
    if r.get('seven'):
        o.append(f"{indent}  ONE OF THE SEVEN IS HERE: {', '.join(r['seven'])} -- a row and a flag, "
                 f"never explained away")
    if r.get('deviation'):
        o.append(f"{indent}  and its deviation from 1:")
        o.append(show(r['deviation'], indent + '    '))
    return '\n'.join(o)


if __name__ == '__main__':
    import json
    print(__doc__)
    print('  SELF-CHECK, on the LAST REAL READING in bonefish_hops2.jsonl -- no invented values,')
    print('  because a module whose demo prints made-up numbers teaches the wrong widths.\n')
    try:
        R = [json.loads(l) for l in open(W + 'bonefish_hops2.jsonl') if l.strip()][-1]
    except Exception as e:
        print(f'  no reading on disk ({type(e).__name__}): run bonefish_hops2.py first.')
        raise SystemExit(1)
    L, S = R['legs'], R.get('split')
    if not S:
        print('  the last reading has no split: the observer corner was never converted.')
        raise SystemExit(1)
    seats = {'observer': (S['converted_ms'], S['P_width']),
             'witness': (L['PI->LAPTOP']['off_ms'], L['PI->LAPTOP']['off_sem']),
             'time': (L['ARMATURE->LAPTOP']['off_ms'], L['ARMATURE->LAPTOP']['off_sem'])}
    print(f"  read {R['at'][11:19]}, {R['rounds']} replicates per leg")
    for k, (v, w) in seats.items():
        print(f"    {k:<10}{v:+12.4f} +- {w:.4f} ms")
    print()
    t = triangulate(seats, event="the laptop's clock, three seats on the Pi's reference")
    for r in t['rows']:
        print(show(r))
        print()
    h = harmonize({'MAC': seats['observer'], 'PI': seats['witness'], 'ARM': seats['time']},
                  event="the laptop's clock")
    print('  HARMONIZED -- the intervals, kept distinct:')
    for i in h['intervals']:
        print(f"    {i['pair']:<12}{i['interval']:+10.4f} +- {i['width']:.4f}   "
              f"{i['widths']:>6.2f} widths   {'separable' if i['separable'] else 'not separable'}")
    print(f"    {h['note']}")
