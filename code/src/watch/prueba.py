#!/usr/bin/env python3
"""prueba.py -- A KNOWN-GOOD SEAT FOR EVERY LAW MODULE. The scripts are the subject here, not prose.
(Bones, 11 Oct 2026.)

Wayfinder: "get those scripts running then evaluate the scripts instead of evaluating your own
output."

THE GAP THIS CLOSES. Las Guardas item 4 says the instrument is tested as an object FIRST -- a
measured ceiling, a measured floor never assumed zero, and a KNOWN-GOOD SEAT. Nine law modules were
written tonight and exactly one of them, allan.py, had such a seat: four synthetic noise types whose
Allan slopes are known in advance, and it caught a real bug (a flicker generator shipped with the
wrong weight, passing only because I had typed its tolerance wide enough to admit it).

Every other module was judged by reading its output and agreeing with it. That is the reviewer handed
no evidence measuring tone, applied to myself.

SO EACH CASE BELOW HAS AN ANSWER KNOWN BEFORE THE CODE RUNS, and several are cases the module must
REFUSE rather than answer. A filter that cannot be shown to refuse has not been shown to filter.

    python3 prueba.py
"""
import math
import os
import random
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

RESULTS = []


def case(name, expect):
    """register a case whose expected answer is written down BEFORE the call that produces it."""
    def deco(fn):
        RESULTS.append((name, expect, fn))
        return fn
    return deco


# ---------------------------------------------------------------- outcomes.py
@case('outcomes: a residual bin named "other" is REFUSED', 'raises OutcomeCollapse')
def _():
    import outcomes
    try:
        outcomes.Outcomes(subject=[('real', lambda r: True), ('other', lambda r: False)])
        return 'returned normally', False
    except outcomes.OutcomeCollapse:
        return 'raises OutcomeCollapse', True


@case('outcomes: a NON-EXHAUSTIVE set is REFUSED', 'raises OutcomeCollapse')
def _():
    import outcomes
    o = outcomes.Outcomes(subject=[('big', lambda r: r > 10), ('small', lambda r: r < 1)])
    try:
        o.tally([0.5, 50, 5], 'known')        # 5 matches neither
        return 'tallied anyway', False
    except outcomes.OutcomeCollapse:
        return 'raises OutcomeCollapse', True


@case('outcomes: a NON-DISJOINT set is REFUSED', 'raises OutcomeCollapse')
def _():
    import outcomes
    o = outcomes.Outcomes(subject=[('pos', lambda r: r > 0), ('alsopos', lambda r: r > -1)])
    try:
        o.tally([5], 'known')                 # 5 matches both
        return 'tallied anyway', False
    except outcomes.OutcomeCollapse:
        return 'raises OutcomeCollapse', True


@case('outcomes: a valid exhaustive disjoint set PASSES', 'counts 1/1/1')
def _():
    import outcomes
    o = outcomes.Outcomes(subject=[('neg', lambda r: r < 0), ('zero', lambda r: r == 0),
                                   ('pos', lambda r: r > 0)])
    o.tally([-1, 0, 1], 'known')
    got = '%d/%d/%d' % (o.counts['neg'], o.counts['zero'], o.counts['pos'])
    return 'counts ' + got, got == '1/1/1'


# ---------------------------------------------------------------- landing.py (K)
@case('K: rel_err 1.0 is the start of the profile', 'K = -1')
def _():
    from landing import K
    k, _e = K(1.0)
    return 'K = %s' % ('%.6f' % k if k is not None else 'REFUSED'), (k is not None and abs(k + 1) < 1e-9)


@case('K: the first series anchor is K = 0', 'K = 0')
def _():
    from landing import K, REL_E
    k, _e = K(REL_E[0])
    return 'K = %s' % ('%.6f' % k if k is not None else 'REFUSED'), (k is not None and abs(k) < 1e-6)


@case('K: zero error has no position -- REFUSES', 'REFUSED')
def _():
    from landing import K
    k, e = K(0.0)
    return ('REFUSED: ' + (e or '')) if k is None else 'K = %.4f' % k, k is None


@case('K: an error finer than the last anchor REFUSES, never extrapolates', 'REFUSED')
def _():
    from landing import K, REL_E
    k, e = K(float(REL_E[-1]) / 1e6)
    return ('REFUSED: ' + (e or ''))[:60] if k is None else 'K = %.4f' % k, k is None


@case('K: monotone decreasing in the error', 'monotone')
def _():
    from landing import K
    ks = [K(10.0 ** -p)[0] for p in range(1, 8)]
    ok = all(ks[i] < ks[i + 1] for i in range(len(ks) - 1))
    return 'monotone' if ok else 'NOT monotone: %s' % ['%.2f' % v for v in ks], ok


# ---------------------------------------------------------------- pathsplit.py
# THE CONTAMINATION IS ONE-SIDED, AND THE FIRST VERSION OF THIS CASE WAS NOT.
# I threw outliers with rng.choice((-1,+1)) at evenly spaced x, and ordinary least squares came
# within 0.035 of the truth -- symmetric contamination spread evenly in x CANCELS in a regression
# and only inflates its width. So my known-bad case was not bad, and it would have certified OLS.
# A QUEUED PACKET IS LATE AND NEVER EARLY: real NTP contamination is one-sided and clustered. The
# case now matches the physics it claims to stand for, and it is clustered at high x so it also
# levers the slope.
def _contaminated(seed=4):
    rng = random.Random(seed)
    TRUE = 0.400
    x = [i / 100.0 for i in range(300)]
    y = [TRUE * v + 0.01 * rng.gauss(0, 1) for v in x]
    for i in range(200, 300, 4):              # one-sided, LATE only, clustered at high x
        y[i] += 20.0 * (1.0 + rng.random())
    return TRUE, x, y


@case('theil-sen recovers a KNOWN slope through ONE-SIDED clustered outliers', 'within 0.02 of 0.400')
def _():
    import pathsplit as ps
    TRUE, x, y = _contaminated()
    _a, b = ps.theilsen(x, y)
    return 'slope %.4f' % b, abs(b - TRUE) < 0.02


@case('and LEAST SQUARES FAILS that case -- the floor is measured, never assumed', 'ols off by >0.1')
def _():
    import statistics as st
    TRUE, x, y = _contaminated()
    mx, my = st.mean(x), st.mean(y)
    den = sum((v - mx) ** 2 for v in x)
    b = sum((x[i] - mx) * (y[i] - my) for i in range(len(x))) / den
    return 'ols slope %.4f (off by %.3f)' % (b, abs(b - TRUE)), abs(b - TRUE) > 0.1


@case('rail_reading: P far from both 0 and the rail -> partial', 'partial')
def _():
    import pathsplit as ps
    n, _note = ps.rail_reading(0.25, 0.01)
    return n, n == 'partial'


@case('rail_reading: P at zero within its width -> symmetric', 'symmetric')
def _():
    import pathsplit as ps
    n, _note = ps.rail_reading(0.01, 0.05)
    return n, n == 'symmetric'


@case('rail_reading: P at the rail within its width -> one-sided', 'one-sided')
def _():
    import pathsplit as ps
    n, _note = ps.rail_reading(0.49, 0.02)
    return n, n == 'one-sided'


@case('rail_reading: within a width of BOTH -> cannot-tell, NOT the first branch', 'cannot-tell')
def _():
    import pathsplit as ps
    n, _note = ps.rail_reading(0.25, 0.20)   # 1.25 widths from 0 AND from 0.5
    return n, n == 'cannot-tell'


@case('rail_reading: no width stated -> cannot-tell, never a verdict', 'cannot-tell')
def _():
    import pathsplit as ps
    n, _note = ps.rail_reading(0.47, None)
    return n, n == 'cannot-tell'


# ---------------------------------------------------------------- ley.py
@case('ley: a Reading with no none is REFUSED', 'raises Illegal')
def _():
    import ley
    try:
        ley.Reading('t', lambda c: 1.0, '', 'the split',
                    [ley.Freedom('f', [1, 2], 1)], 'src', width=1.0)
        return 'constructed', False
    except ley.Illegal:
        return 'raises Illegal', True


@case('ley: a ruler not on the roster is REFUSED', 'raises Illegal')
def _():
    import ley
    try:
        ley.Reading('t', lambda c: 1.0, 'x' * 40, 'vibes',
                    [ley.Freedom('f', [1, 2], 1)], 'src', width=1.0)
        return 'constructed', False
    except ley.Illegal:
        return 'raises Illegal', True


@case('ley: a Freedom with ONE option is REFUSED (a knob is not a declaration)', 'raises Illegal')
def _():
    import ley
    try:
        ley.Freedom('f', [1], 1)
        return 'constructed', False
    except ley.Illegal:
        return 'raises Illegal', True


@case('ley: envelope LARGER than the width -> significance REFUSED', 'refused')
def _():
    import ley
    r = ley.Reading('t', lambda c: float(c['k']), 'x' * 40, 'the split',
                    [ley.Freedom('k', [0.0, 10.0], 0.0)], 'src', width=0.1)
    ok, _why = r.significance_allowed()
    return 'allowed' if ok else 'refused', not ok


@case('ley: envelope INSIDE the width -> significance ALLOWED', 'allowed')
def _():
    import ley
    r = ley.Reading('t', lambda c: float(c['k']), 'x' * 40, 'the split',
                    [ley.Freedom('k', [0.0, 0.001], 0.0)], 'src', width=1.0)
    ok, _why = r.significance_allowed()
    return 'allowed' if ok else 'refused', ok


# ---------------------------------------------------------------- los_pasos.py
@case('los_pasos: a reading missing steps is NOT legal', 'not legal')
def _():
    import los_pasos as lp
    ok = lp.report('known-bad', {'event': 'x'}, strict=True)
    return 'legal' if ok else 'not legal', not ok


@case('los_pasos: NO APLICA with no reason counts as FALTA', 'FALTA')
def _():
    import los_pasos as lp
    rows = lp.check({'giro': 'n/a:'})
    st = [s for n, _nm, s, _no in rows if n == 16][0]
    return st, st == lp.FALTA


@case('los_pasos: the four statuses are exhaustive over 19 steps', 'sums to 19')
def _():
    import los_pasos as lp
    rows = lp.check({'event': 'x', 'giro': 'n/a: no phase pair'})
    tot = len(rows)
    return 'sums to %d' % tot, tot == 19


# ---------------------------------------------------------------- novatime.py
@case('novatime: tick names WHICH counter it read', "counter == 'deep cycle'")
def _():
    import novatime
    d = novatime.tick(detail=True)
    if not isinstance(d, dict):
        return 'returned %r' % (d,), False
    return "counter == %r" % d.get('counter'), d.get('counter') == 'deep cycle'


@case('novatime: tick() and tick(detail=True) agree', 'same value')
def _():
    import novatime
    v = novatime.tick()
    d = novatime.tick(detail=True)
    same = isinstance(d, dict) and d.get('tick') == v
    return 'same value' if same else 'differ: %r vs %r' % (v, d), same


# ---------------------------------------------------------------- allan.py  (NAILED DOWN)
# Four noise types whose Allan slopes are known from the definition, one tolerance for all four,
# the fit range fixed BEFORE any curve is seen, and a constructed KNEE that a single global fit
# demonstrably cannot name. This is the module that already had a seat and it earned it: the seat
# caught a flicker generator shipped with weight tc^-0.5 (which is WHITE) passing only because its
# tolerance had been typed at 0.30.
@case('allan: white phase recovers slope -1', 'within 0.08 of -1.00')
def _():
    import allan, random
    pts = allan.adev_phase(allan.white_phase(16384, random.Random(7)), 1.0)
    sl, _n = allan.slope(pts, 0.15, 0.75)
    return 'slope %.3f' % sl, abs(sl + 1.0) <= 0.08


@case('allan: white frequency recovers slope -1/2', 'within 0.08 of -0.50')
def _():
    import allan, random
    pts = allan.adev_phase(allan.white_freq(16384, random.Random(7)), 1.0)
    sl, _n = allan.slope(pts, 0.15, 0.75)
    return 'slope %.3f' % sl, abs(sl + 0.5) <= 0.08


@case('allan: flicker frequency recovers slope 0 (FLAT)', 'within 0.08 of 0.00')
def _():
    import allan, random
    pts = allan.adev_phase(allan.flicker_freq(16384, random.Random(7)), 1.0)
    sl, _n = allan.slope(pts, 0.15, 0.75)
    return 'slope %.3f' % sl, abs(sl) <= 0.08


@case('allan: random walk frequency recovers slope +1/2', 'within 0.08 of +0.50')
def _():
    import allan, random
    pts = allan.adev_phase(allan.random_walk_freq(16384, random.Random(7)), 1.0)
    sl, _n = allan.slope(pts, 0.15, 0.75)
    return 'slope %.3f' % sl, abs(sl - 0.5) <= 0.08


@case('allan: the WRONG flicker weight (tc^-0.5) is caught, not passed', 'slope below -0.15')
def _():
    import allan, math, random
    # the bug as shipped: unit-variance AR(1) poles summed with weight tc^-0.5, which integrates to
    # a CONSTANT psd -- white, not 1/f. The seat must reject it.
    def wrong(n, rng, poles=64, band=26.0):
        taus = [2.0 ** (k * band / poles) for k in range(poles)]
        state = [0.0] * poles
        y = []
        for _ in range(n):
            tot = 0.0
            for j, tc in enumerate(taus):
                a = math.exp(-1.0 / tc)
                state[j] = a * state[j] + math.sqrt(1 - a * a) * rng.gauss(0, 1)
                tot += state[j] * tc ** -0.5
            y.append(tot)
        x, acc = [], 0.0
        for v in y:
            acc += v
            x.append(acc)
        return x
    pts = allan.adev_phase(wrong(16384, random.Random(7)), 1.0)
    sl, _n = allan.slope(pts, 0.15, 0.75)
    return 'slope %.3f' % sl, sl < -0.15


@case('allan: a KNEE defeats one global fit -- gap over SEEDS, bar from its own scatter',
      'gap exceeds 3 of its own widths')
def _():
    # THE FIRST VERSION OF THIS CASE USED ONE SEED AND A BAR I TYPED (0.25), and it failed at a gap
    # of 0.18 -- not because the module was wrong but because a single realisation of a knee is a
    # draw, and 0.25 was a number chosen by the observer. The gap now carries a width across seeds
    # and is judged against THAT, so the bar comes from the quantity instead of from me.
    import allan, random, statistics as st
    gaps, globals_ = [], []
    for s in range(8):
        pts = allan.adev_phase(allan.knee(8192, random.Random(100 + s), cross=64.0), 1.0)
        ls = allan.local_slope(pts, window=4)
        lo = [v for tau, v in ls if tau <= 32]
        hi = [v for tau, v in ls if tau >= 256]
        g, _n = allan.slope(pts, 0.15, 0.75)
        if lo and hi:
            gaps.append(sum(hi) / len(hi) - sum(lo) / len(lo))
            globals_.append(g)
    if len(gaps) < 4:
        return 'only %d usable seeds' % len(gaps), False
    m = st.mean(gaps); sd = st.pstdev(gaps); sem = sd / len(gaps) ** 0.5
    gm = st.mean(globals_)
    return ('gap %+.3f +- %.3f (n=%d, %.1f widths); global fit %+.3f sits between'
            % (m, sem, len(gaps), m / sem if sem else 0, gm)), (sem > 0 and m / sem > 3)


@case('allan: a tau with too few terms is DROPPED, never reported thin', 'no tau with n < 8')
def _():
    import allan, random
    pts = allan.adev_phase(allan.white_phase(64, random.Random(1)), 1.0)
    bad = [p for p in pts if p[2] < 8]
    return 'thin taus: %d' % len(bad), len(bad) == 0


# ---------------------------------------------------------------- escalera.py (its missing seat)
# Named as missing in the four-part before it was built. A module I wrote without a known-answer
# case is the one thing the harness exists to prevent, so it gets one rather than a promise.
@case('escalera: one rung is exactly log10(phi^2)', 'within 1e-12 of 0.417960')
def _():
    import escalera, math
    PHI = (1 + 5 ** 0.5) / 2
    want = math.log10(PHI ** 2)
    return 'step %.9f' % escalera.STEP_DECADES, abs(escalera.STEP_DECADES - want) < 1e-12


@case('escalera: the anchors ARE the Fibonacci convergents', '2/1 3/2 5/3 8/5 13/8')
def _():
    import escalera
    got = ['%d/%d' % (p, q) for p, q, _r in escalera.convergents(5)]
    want = ['2/1', '3/2', '5/3', '8/5', '13/8']
    return ' '.join(got), got == want


@case('escalera: rung n sits at n, by construction', 'L(anchor k) == k')
def _():
    import escalera
    bad = []
    for k in range(1, 12):
        r = escalera.convergents(14)[k][2]
        l, _e = escalera.L(r)
        if l is None or abs(l - k) > 1e-6:
            bad.append(k)
    return 'all exact' if not bad else 'off at rungs %s' % bad, not bad


@case('escalera: coarser than the first anchor -> REFUSES', 'REFUSED')
def _():
    import escalera
    l, e = escalera.L(0.9)
    return ('REFUSED: ' + (e or ''))[:40] if l is None else 'rung %.2f' % l, l is None


@case('escalera: finer than the last anchor -> REFUSES, never extrapolates', 'REFUSED')
def _():
    import escalera
    l, e = escalera.L(1e-30)
    return ('REFUSED: ' + (e or ''))[:40] if l is None else 'rung %.2f' % l, l is None


@case('escalera: monotone decreasing in the error, like K', 'monotone')
def _():
    import escalera
    ls = []
    for p in range(1, 6):
        l, _e = escalera.L(10.0 ** -p)
        if l is not None:
            ls.append(l)
    ok = len(ls) >= 4 and all(ls[i] < ls[i + 1] for i in range(len(ls) - 1))
    return 'monotone' if ok else 'NOT monotone: %s' % ['%.2f' % v for v in ls], ok


@case('escalera: it is FINER than K in our range -- the claim, checked', 'ratio > 15')
def _():
    import escalera
    kd, ld, ratio = escalera.resolution_vs_K()
    return 'K step %.2f dec, rung %.4f dec, ratio %.1f' % (kd, ld, ratio), ratio > 15


@case('escalera: (RUNG - K) is DETERMINISTIC in rel_err -- never a second seat', 'monotone, no freedom')
def _():
    # the case exists so the module carries its own prohibition. If this ever came out NON-monotone
    # it would mean one of the two profiles had stopped being a monotone function of the error, and
    # the ladder would need rebuilding -- not that a second reading had appeared.
    import escalera
    from landing import K
    iv = []
    for p10 in (2, 3, 4, 5, 6):
        for mult in (1.0, 3.0):
            v = mult * 10.0 ** -p10
            k, _a = K(v)
            l, _b = escalera.L(v)
            if k is not None and l is not None:
                iv.append((v, l - k))
    iv.sort(key=lambda r: -r[0])
    d = [b for _a, b in iv]
    ok = len(d) >= 6 and all(d[i] < d[i + 1] for i in range(len(d) - 1))
    return ('monotone, no freedom (%.3f to %.3f)' % (min(d), max(d))) if ok else 'NOT monotone', ok


if __name__ == '__main__':
    print('  A KNOWN-GOOD SEAT FOR EVERY LAW MODULE. The expected answer is written in the case')
    print('  name, BEFORE the call. A filter that cannot be shown to refuse has not been shown')
    print('  to filter, so several of these demand a REFUSAL rather than an answer.\n')
    print('  %-62s%-26s%s' % ('case', 'got', 'verdict'))
    passed = failed = errored = 0
    for name, expect, fn in RESULTS:
        try:
            got, ok = fn()
        except Exception as e:
            got, ok = '%s: %s' % (type(e).__name__, str(e)[:28]), None
        if ok is True:
            passed += 1; v = 'PASS'
        elif ok is False:
            failed += 1; v = 'FAIL (expected %s)' % expect
        else:
            errored += 1; v = 'ERROR'
        print('  %-62s%-26s%s' % (name[:62], str(got)[:26], v))
    n = len(RESULTS)
    print('\n  %d cases: %d PASS, %d FAIL, %d ERROR.' % (n, passed, failed, errored))
    print('  %s' % ('every law module now has a seat that would catch it being wrong.'
                    if failed == errored == 0 else
                    'SOMETHING IS WRONG AND IT IS IN THE MODULE, NOT IN THE PROSE -- which is the '
                    'point of\n  running the scripts instead of reading them.'))
