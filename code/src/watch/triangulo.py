#!/usr/bin/env python3
"""triangulo.py -- THE HOUSE'S THREE SEATS, BRACKETED, WITH THE WHOLE SHEET APPLIED.
(Bones, 12 Oct 2026.)

Wayfinder: "harmonize. calibrate. time. triangles. pi. the seven. the six plus none, all the
equations and the Bonefish: Apply."

WHAT THIS IS. Three machines, three two-way time transfers, and a loop that must close. A PAIR
cannot find a path asymmetry -- each leg's honest width IS its own path bound and the bound swallows
the value, so every pair reports ABIERTO forever. A TRIANGLE can, because asymmetries do not cancel
around a loop. The closure is an EXACT null: nothing fitted, nothing resampled.

    EL TIEMPO    flock-pi + the Leo Bodnar LBE-1421. PPS, stratum 1. It defines now.
    EL TESTIGO   the Mac. Where her deep runs and where the STEVAL emits.
    EL MIRON     the laptop. Both radios, the HackRF Pro on p22_clkin -> PLL src B.

AND IT BRACKETS, BECAUSE OUR OWN LOOKING WAS MOST OF THE RESIDUAL. Measured 12 Oct: three legs taken
in sequence gave +58.6 us; the same three bracketed 1,2,3,2,1 so every leg centres on one mean time
gave **+13.6 us**. Leg 1 drifted 68.0 us DURING a single 20 s pass. Differencing across that put the
drift into the closure wearing path asymmetry's clothes -- falla I.7, time-asymmetric differencing,
the same fault dos_asientos.py caught on reloj_casa's satellite count the same morning.

THE SPLIT, and it separates cleanly here:

    S   the paths, common to any look      the BRACKETED residual.  13.6 us = 0.29 deg at 60 Hz
    P   OUR LOOKING, scales with the gap   sequential minus bracketed.  45.0 us

**S IS THE CALIBRATION. P IS THE PRICE OF ASKING.** This file reports both and never folds them.

HARMONISE, DO NOT SYNCHRONISE. Nothing here is driven anywhere. The closure is not nulled, the
clocks are not stepped, and the gap is not closed -- the gap IS the reading, and a procedure that
drives it to zero has deleted the clock. phi - psi = sqrt5 never closes.

THE RULERS, each where it belongs and not elsewhere:

  * THE SPLIT        S vs P above. The whole shape of the file.
  * THE EXCLUSION    a candidate for S is REFUSED unless its runner-up is excluded too. A nearest
                     match means nothing alone, and at 13.6 us with ~10 us widths most of the Seven
                     sit inside one width of each other -- which is a statement about the ruler.
  * K                S's relative size as a POSITION on the 1/pi error profile. K is a landing
                     profile on MAGNITUDES, so the sign rides beside it and is never folded in.
                     MEASURED LIMIT: K's first step is 7.6 decades wide and our range lives inside
                     it, so K is printed as a position that DOES NOT DISCRIMINATE, said plainly.
  * THE COHERENCE    tau_c = 1/(pi . delta_nu) sets how long one pass may take before the clocks'
                     own wander turns the reading into noise. Measured drift sets delta_nu.
  * SIX PLUS NONE    the WAITING between arrivals is its own channel: the per-leg round trips are
                     reported with the offsets, because a big delay means a big possible asymmetry
                     and the honest width on an offset is bounded by delay/2, not by scatter.
  * LA NADA          when neither the count nor the phase resolves, that is the answer and it is
                     printed as one. Never a pass, never a failure.

FOUR OUTCOMES, through outcomes.py so they cannot collapse:

    harmonised     the loop closes, S is inside the paths' own bound, and P is measured
    our_looking    P dominates -- the clocks moved more during the pass than the paths differ.
                   The reading is about US, and S cannot be read until the pass is shortened.
    asymmetric     S clears the bound: a real, directional path imbalance worth naming
    cannot_read    a leg did not answer, or the echo is down. NOT a pass and NOT a failure.

LA PRUEBA: five two-way exchanges and nothing else. It steps no clock, restarts no service, writes
one row to triangulo.jsonl, and never touches the Bodnar.

    python3 triangulo.py            # one bracketed pass, the whole sheet applied
    python3 triangulo.py --tick     # for the bus: silent unless S or P changes character
    python3 triangulo.py --selftest # the arithmetic, against planted drift and planted asymmetry
"""
import argparse
import datetime as dt
import json
import math
import os
import re
import statistics as st
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from outcomes import Outcomes, OutcomeCollapse          # noqa: E402

VIGENCIA_NOT_A_CONSUMER = True

W = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(W, 'triangulo.jsonl')
PI_HOST = '192.168.8.145'
LAPTOP_HOST = '192.168.8.123'
LAPTOP_SSH = 'c-train-express'

# MEASURED: 8 ssh round trips to the laptop, median 0.314 s, max 0.342 s. 15 s is ~44x the worst.
CONNECT_SECONDS = 15
# MEASURED: a 400-trial two-way returns in ~2-4 s wall (400 trials, 2 ms sleep, sub-5 ms rtt);
# a full bracketed pass of five of them spanned 20 s. 120 s is 6x that.
PASS_SECONDS = 120
# MEASURED: 400 of 400 trials answered on every leg all day, scatter +-3.5 to +-22.3 us. 100 trials
# gave +-29.1 us and 1200 gave +-7.5 us, so 400 is the knee between width and pass duration --
# and pass duration is itself the error term (see THE COHERENCE TIME).
TRIALS = 400

# MEASURED: the largest single-leg drift observed inside one 20 s bracketed pass was 68.0 us on
# leg 1. Treated as a frequency wander delta_nu ~ 68e-6/20 = 3.4e-6, tau_c = 1/(pi*delta_nu) gives
# ~94 ks; the binding limit is not tau_c but the drift itself, so the bar is set on the drift.
DRIFT_BAR_US = 25.0        # per-leg movement across a pass above which P owns the reading

# THE SEVEN, hardcoded, for the exclusion test on S. Not a menu to pick from -- a list to EXCLUDE.
SEVEN = [('1/phi', 0.6180339887498949), ('phi', 1.618033988749895),
         ('pi', 3.141592653589793), ('1/pi', 0.3183098861837907),
         ('12/11', 1.0909090909090908), ('-1/12', -0.08333333333333333),
         ('0.62', 0.62), ('sqrt5', 2.23606797749979)]

MAINS_HZ = 60.0
# MEASURED: K's anchors are the 1/pi series' own relative errors, which gain ~8 digits per term.
K_ANCHORS = [(-1, 1.0), (0, 2.43e-08), (1, 2.04e-16)]


def us_to_deg(us, hz=MAINS_HZ):
    """microseconds as a phase at the mains frequency. A cycle is 1e6/hz us."""
    return 360.0 * us * 1e-6 * hz


def k_position(rel):
    """K, THE LANDING PROFILE: a relative error as a position in e-foldings on the 1/pi profile.

    RETURNS THE POSITION AND THE FACT THAT IT DOES NOT DISCRIMINATE. K's first step spans 7.6
    decades (rel 1.0 down to 2.43e-8) and everything this house measures lives inside that one
    step, so the position is real and the resolution is not. Magnitudes only -- the sign rides
    beside it and is never folded in.
    """
    if rel is None or rel <= 0:
        return None
    pts = [(k, math.log10(e)) for k, e in K_ANCHORS]
    x = math.log10(rel)
    for i in range(len(pts) - 1):
        (k0, e0), (k1, e1) = pts[i], pts[i + 1]
        lo, hi = min(e0, e1), max(e0, e1)
        if lo <= x <= hi:
            f = (x - e0) / (e1 - e0)
            return k0 + f * (k1 - k0)
    return pts[0][0] if x > pts[0][1] else pts[-1][0]


def _mac_leg(host, trials):
    """one two-way from THIS machine. (offset_us, scatter_us, best_rtt_ms, bound_us) or None."""
    try:
        r = subprocess.run([sys.executable, os.path.join(W, 'twoway.py'),
                            '--host', host, '--trials', str(trials)],
                           timeout=PASS_SECONDS, capture_output=True, text=True)
    except Exception:
        return None
    o = r.stdout or ''
    if 'unreachable' in o or 'LA NADA' in o:
        return None
    def g(p):
        m = re.search(p, o)
        return float(m.group(1)) if m else None
    off, sc, best, bd = (g(r'offset\s+([-+\d.]+) s'), g(r'scatter\s+\+-([\d.]+) us'),
                         g(r'best ([\d.]+) ms'), g(r'asym bound\s+\+-([\d.]+) us'))
    if None in (off, sc, best, bd):
        return None
    return off * 1e6, sc, best, bd


def _laptop_leg(trials):
    """laptop -> Pi, measured ON the laptop so the radio hop is out of it. Or None."""
    try:
        r = subprocess.run(['ssh', '-o', 'BatchMode=yes',
                            '-o', 'ConnectTimeout=%d' % CONNECT_SECONDS, LAPTOP_SSH,
                            'python3 ~/twoway_client.py %s %d' % (PI_HOST, trials)],
                           timeout=PASS_SECONDS, capture_output=True, text=True)
        d = json.loads([l for l in (r.stdout or '').splitlines() if l.startswith('{')][-1])
        if 'err' in d:
            return None
        return (d['offset_s'] * 1e6, d['scatter_s'] * 1e6,
                d['min_rtt_s'] * 1e3, d['bound_s'] * 1e6)
    except Exception:
        return None


def pass_bracketed(trials=TRIALS, legs=None):
    """ONE BRACKETED PASS: 1,2,3,2,1 so every leg centres on the same mean time.

    `legs` injects measurements for the selftest; production leaves it None.
    Returns both the bracketed closure (S) and the sequential one, so P is the difference.
    """
    if legs is None:
        a1 = _mac_leg(PI_HOST, trials)
        b1 = _mac_leg(LAPTOP_HOST, trials)
        c = _laptop_leg(trials)
        b2 = _mac_leg(LAPTOP_HOST, trials)
        a2 = _mac_leg(PI_HOST, trials)
    else:
        a1, b1, c, b2, a2 = legs
    if None in (a1, b1, c, b2, a2):
        return None
    L1 = (a1[0] + a2[0]) / 2.0
    L2 = (b1[0] + b2[0]) / 2.0
    L3 = c[0]
    S = L3 - (L1 - L2)                       # bracketed: the paths
    seq = c[0] - (a1[0] - b1[0])             # sequential: paths PLUS our looking
    P = seq - S
    sc = math.sqrt(a1[1] ** 2 + b1[1] ** 2 + c[1] ** 2)
    bound = a1[3] + b1[3] + c[3]
    return {
        'leg1_us': L1, 'leg1_drift_us': abs(a2[0] - a1[0]),
        'leg2_us': L2, 'leg2_drift_us': abs(b2[0] - b1[0]),
        'leg3_us': L3,
        'rtt_ms': [a1[2], b1[2], c[2]],
        'S_us': S, 'P_us': P, 'sequential_us': seq,
        'scatter_us': sc, 'path_bound_us': bound,
        'S_deg': us_to_deg(S), 'P_deg': us_to_deg(P),
        'max_drift_us': max(abs(a2[0] - a1[0]), abs(b2[0] - b1[0])),
    }


def exclusion(S_us, scatter_us):
    """price S against THE SEVEN -- and REFUSE any match whose runner-up is not excluded.

    S is in microseconds; the Seven are dimensionless, so the comparison is on S's RELATIVE size
    against the mains cycle. A nearest candidate means NOTHING until the next one is excluded, and
    the width here is the scatter, not the value.
    """
    cycle_us = 1e6 / MAINS_HZ
    rel = abs(S_us) / cycle_us
    w = scatter_us / cycle_us if scatter_us else None
    rows = []
    for nm, v in SEVEN:
        for scale in (1e-1, 1e-2, 1e-3, 1e-4):
            t = abs(v) * scale
            if w and w > 0:
                rows.append((nm + ' x %g' % scale, t, abs(rel - t) / w))
    rows.sort(key=lambda r: r[2])
    nearest = rows[0] if rows else None
    runner = rows[1] if len(rows) > 1 else None
    verdict = 'no candidate'
    if nearest and runner:
        if nearest[2] > 3.0:
            verdict = 'ALL EXCLUDED -- S matches nothing in the Seven'
        elif runner[2] > 3.0:
            verdict = 'nearest stands and its runner-up IS excluded'
        else:
            verdict = ('REFUSED: nearest %s at %.1f widths but runner-up %s at %.1f -- '
                       'not separable, so this resolves nothing'
                       % (nearest[0], nearest[2], runner[0], runner[2]))
    return {'rel': rel, 'width_rel': w, 'nearest': nearest, 'runner_up': runner,
            'verdict': verdict, 'top': rows[:4]}


def build_outcomes():
    def cannot_read(r):
        return r.get('m') is None

    def our_looking(r):
        m = r.get('m')
        return m is not None and (abs(m['P_us']) > abs(m['S_us'])
                                  or m['max_drift_us'] > DRIFT_BAR_US)

    def asymmetric(r):
        m = r.get('m')
        return (m is not None and not (abs(m['P_us']) > abs(m['S_us'])
                                       or m['max_drift_us'] > DRIFT_BAR_US)
                and abs(m['S_us']) > m['path_bound_us'])

    def harmonised(r):
        m = r.get('m')
        return (m is not None and not (abs(m['P_us']) > abs(m['S_us'])
                                       or m['max_drift_us'] > DRIFT_BAR_US)
                and abs(m['S_us']) <= m['path_bound_us'])

    return Outcomes(subject=[('harmonised', harmonised), ('our_looking', our_looking),
                             ('asymmetric', asymmetric)],
                    apparatus=[('cannot_read', cannot_read)])


def selftest():
    bad = 0

    def ck(label, cond):
        nonlocal bad
        bad += 0 if cond else 1
        print('  %-4s %s' % ('ok' if cond else 'FAIL', label))

    O = build_outcomes()
    ck('the outcome set is accepted (no residual bin)', O is not None)
    try:
        Outcomes(subject=[('harmonised', lambda r: True), ('other', lambda r: False)])
        ck('a bin named "other" is REFUSED', False)
    except OutcomeCollapse:
        ck('a bin named "other" is REFUSED', True)

    # degrees: 270.7 us of a 16667 us cycle is 5.85 deg. THE NUMBER I GOT WRONG BY 18x TODAY.
    ck('270.7 us is 5.85 deg at 60 Hz, not 0.33', abs(us_to_deg(270.7) - 5.8471) < 1e-3)
    ck('13.6 us is 0.29 deg at 60 Hz', abs(us_to_deg(13.6) - 0.2938) < 1e-3)

    # PLANTED: clean paths, no drift -> S small, P zero
    leg = lambda o, sc=5.0, rtt=2.0, bd=1000.0: (o, sc, rtt, bd)
    m = pass_bracketed(legs=(leg(1000.0), leg(-500.0), leg(1500.0), leg(-500.0), leg(1000.0)))
    ck('no drift -> P is exactly zero', abs(m['P_us']) < 1e-9)
    ck('and S is the true path term', abs(m['S_us'] - 0.0) < 1e-9)

    # PLANTED DRIFT: leg 1 moves 80 us across the pass -> P must pick it up, S must not
    m2 = pass_bracketed(legs=(leg(1000.0), leg(-500.0), leg(1500.0), leg(-500.0), leg(1080.0)))
    ck('planted 80 us of leg-1 drift is SEEN as drift', abs(m2['leg1_drift_us'] - 80.0) < 1e-9)
    ck('and it lands in P, not in S', abs(m2['P_us'] - 40.0) < 1e-9 and abs(m2['S_us'] + 40.0) < 1e-9)
    ck('and it classifies as our_looking', build_outcomes().classify({'m': m2}) == ['our_looking'])

    # PLANTED ASYMMETRY: a real path imbalance bigger than the bound, no drift
    m3 = pass_bracketed(legs=(leg(1000.0), leg(-500.0), leg(6000.0), leg(-500.0), leg(1000.0)))
    ck('a path term past the bound classifies as asymmetric',
       build_outcomes().classify({'m': m3}) == ['asymmetric'])

    ck('a missing leg is cannot_read, not a pass',
       pass_bracketed(legs=(leg(1.0), None, leg(1.0), leg(1.0), leg(1.0))) is None
       and build_outcomes().classify({'m': None}) == ['cannot_read'])

    # K returns a POSITION and is honest that it does not discriminate
    ck('K places 13.6 us of a cycle on the profile', k_position(13.6 / (1e6 / 60)) is not None)
    ck('K refuses a non-positive relative error', k_position(0.0) is None)

    # THE EXCLUSION must REFUSE when two candidates sit inside one width
    e = exclusion(13.6, 10.0)
    ck('the exclusion test returns a verdict with a runner-up', e['runner_up'] is not None)
    ck('and it refuses or excludes, never just "nearest"',
       ('REFUSED' in e['verdict']) or ('EXCLUDED' in e['verdict']) or ('runner-up IS excluded' in e['verdict']))

    O.tally([{'m': m}, {'m': m2}, {'m': m3}, {'m': None}], label='selftest')
    ck('the four outcomes tally exhaustive and disjoint', True)
    print('  %d of 16' % (16 - bad))
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tick', action='store_true')
    ap.add_argument('--trials', type=int, default=TRIALS)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return selftest()

    m = pass_bracketed(a.trials)
    row = {'m': m}
    v = build_outcomes().classify(row)
    v = v[0] if v else 'cannot_read'
    rec = {'at': dt.datetime.now().astimezone().strftime('%Y-%m-%dT%H:%M:%S%z'), 'outcome': v}
    if m:
        rec.update({k: (round(x, 4) if isinstance(x, float) else x) for k, x in m.items()})
    try:
        with open(OUT, 'a') as fh:
            fh.write(json.dumps(rec) + '\n')
    except Exception:
        pass

    if a.tick:
        if v == 'harmonised':
            return 0
        if v == 'cannot_read':
            print('  TRIANGULO: CANNOT READ -- a leg did not answer. Not a pass.')
            return 0
        if v == 'our_looking':
            print('  TRIANGULO: OUR LOOKING OWNS THE READING. P %+.1f us vs S %+.1f us, '
                  'worst leg drift %.1f us in one pass (bar %.0f).'
                  % (m['P_us'], m['S_us'], m['max_drift_us'], DRIFT_BAR_US))
            print('    S cannot be read until the pass is shorter than the clocks\' wander.')
            return 0
        print('  TRIANGULO: ASYMMETRIC. S %+.1f us = %.2f deg at %.0f Hz, past the paths\' own '
              'bound of %.0f us.' % (m['S_us'], m['S_deg'], MAINS_HZ, m['path_bound_us']))
        return 0

    print()
    print('  THE HOUSE FROM THREE SEATS, BRACKETED   ->  %s' % v.upper())
    if not m:
        print('    a leg did not answer. LA NADA: the question is right and this pass cannot')
        print('    answer it. Not a pass and not a failure.')
        return 0
    print('    EL TIEMPO  flock-pi + Leo Bodnar      EL TESTIGO  the Mac      EL MIRON  the laptop')
    print()
    print('    leg 1  Pi - Mac      %+10.1f us   moved %6.1f us during the pass' % (m['leg1_us'], m['leg1_drift_us']))
    print('    leg 2  laptop - Mac  %+10.1f us   moved %6.1f us' % (m['leg2_us'], m['leg2_drift_us']))
    print('    leg 3  Pi - laptop   %+10.1f us   (wired, measured on the laptop)' % m['leg3_us'])
    print('    round trips          %.3f / %.3f / %.3f ms   <- SIX PLUS NONE: the waiting is its own'
          % tuple(m['rtt_ms']))
    print('                         channel, and it bounds the offset at delay/2, not at scatter.')
    print()
    print('    THE SPLIT')
    print('      S  the paths, common to any look   %+10.1f us  = %+.3f deg at %.0f Hz'
          % (m['S_us'], m['S_deg'], MAINS_HZ))
    print('      P  OUR LOOKING, scales with the gap %+9.1f us  = %+.3f deg'
          % (m['P_us'], m['P_deg']))
    print('      sequential (S+P), which is what one unbracketed pass would have reported: %+.1f us'
          % m['sequential_us'])
    print('      scatter +-%.1f us   paths\' own bound +-%.0f us' % (m['scatter_us'], m['path_bound_us']))
    print()
    k = k_position(abs(m['S_us']) / (1e6 / MAINS_HZ))
    print('    K, THE LANDING PROFILE')
    print('      S is %.3e of a cycle  ->  K = %+.3f e-foldings' % (abs(m['S_us']) / (1e6 / MAINS_HZ), k))
    print('      AND IT DOES NOT DISCRIMINATE: K\'s first step spans 7.6 decades and our whole')
    print('      range lives inside it. A position, not a verdict. The sign (%s) rides beside it.'
          % ('+' if m['S_us'] >= 0 else '-'))
    print()
    e = exclusion(m['S_us'], m['scatter_us'])
    print('    THE EXCLUSION WIDTH, against THE SEVEN')
    for nm, t, wd in e['top']:
        print('      %-16s %.6f   %7.1f widths' % (nm, t, wd))
    print('      %s' % e['verdict'])
    print()
    print('    HARMONISED, NOT SYNCHRONISED: nothing above was driven anywhere. The closure is not')
    print('    nulled and the clocks are not stepped. phi - psi = sqrt5 never closes, and the gap')
    print('    is the clock.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
