#!/usr/bin/env python3
"""bonefish_hops.py -- THE BONEFISH ON THE TIME HOPS, AND WHERE PI ACTUALLY ENTERS.
(Bones, 9 Oct 2026.)

Wayfinder: "how are you applying the bonefish, and have you looked at how the harmonics of pi
resonate between the time hops?" Then: "it's in the seven bones, and the equations were supposed to be
hot loaded into your context at every turn."

THE BONEFISH IS THE TRIANGLE, NOT A FORMULA. From Appendix B of LAS_ECUACIONES:

                    EL TIEMPO
                       /\
                      /  \
             EL MIRON ---- EL TESTIGO
             (outside)      (inside)

and its three conversions, which are the thing to apply:

    witness  =  observer x 12/11        = 1.090909
    time     =  observer x phi          = 1.618034
    time     =  witness  x phi x 11/12  = 1.483198

"Three conversions between three positions on one event." The sheet has already measured them on three
clocks on one look -- 1.0872 +- 0.0138, 1.6055 +- 0.0917, 1.4768 +- 0.0864 -- and prices them: ONLY THE
FIRST CAN SEPARATE ITS CANDIDATES, the other two have rivals 0.20 and 0.19 widths away.

SO THE HOP LADDER GETS READ AS THE TRIANGLE. One event: the laptop's clock at one instant. Three seats
at three positions:

    EL MIRON    the MAC       outside the wired chain, two radio hops, not an end
    EL TESTIGO  the PI        inside -- it holds the GPSDO the whole house is steered by
    EL TIEMPO   the ARMATURE  the third seat, the candidate for the apex

WHERE PI ENTERS, and it is not where I was about to look. The sheet is explicit:
  - `el adentro = pi = (6/5)phi^2` is WITHDRAWN as an identity (Peters 1978, OEIS A180251, a 15.3 ppm
    known near-miss). It is kept as a ROW. So a pi/phi relation here is not ours to claim.
  - The exact relation is `pi = 10 arcsin(1/(2 phi))`, because 1/(2phi) = sin(pi/10): THE PENTAGON.
  - `el roce = (1/12)(1/pi)` = 2.65 per cent is the friction term, and its phi form is the same
    15.3 ppm near-miss written twice.
  - `ladder(n) = (1/12)(1/phi)^n` was ALREADY CALLED at microsecond spacings, rung n at phi^(2n) us:
    measured +0.42 / +2.46 / +1.74 / +0.80 / -1.98. MISSED. So the ladder on us-scale clock spacings
    is a run that has been done and did not land, and a second pass needs a reason, not a rerun.

AND THE PRODUCT, NEVER THE SUM: LA CABALGATA composes THE BONEFISH x LA FLORACION x LA GALLETA as a
product. So a two-hop factor that matches pi^2 is the one-hop factor squared and is NOT a second row.

    python3 bonefish_hops.py --rounds 8
"""
import argparse
import json
import math
import os
import statistics as st
import subprocess
import sys
import time

W = os.path.expanduser('~/bones-forge/watch/')
sys.path.insert(0, W)
LOG = os.path.join(W, 'bonefish_hops.jsonl')
PHI = (1 + 5 ** 0.5) / 2
PI = math.pi
LAP = '192.168.8.123'

# the three positions on The Bonefish, each reading THE SAME EVENT: the laptop's clock.
SEATS = [('EL MIRON', 'MAC', None, 2, 'outside the wired chain, two radio hops, not an end'),
         ('EL TESTIGO', 'PI', 'flock-pi', 1, 'inside -- it holds the GPSDO the house is steered by'),
         ('EL TIEMPO?', 'ARMATURE', 'armature', 1, 'the third seat, candidate for the apex')]
PY = {'flock-pi': 'python3', 'armature': 'python'}


def one(alias, n=200):
    """one two-way reading of the laptop, taken FROM that seat."""
    try:
        if alias is None:                      # the Mac reads from here, which is the outside seat
            cmd = [sys.executable, os.path.join(W, 'twoway_client.py'), LAP, str(n)]
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=90, cwd=W)
        else:
            p = subprocess.run(['ssh', '-o', 'ConnectTimeout=12', alias,
                                f'{PY[alias]} twoway_client.py {LAP} {n}'],
                               capture_output=True, text=True, timeout=90)
        t = p.stdout.strip()
        d = json.loads(t[t.index('{'):])
        return None if 'err' in d else d
    except Exception:
        return None


def seat_readings(rounds):
    out = {}
    for pos, host, alias, hops, what in SEATS:
        b, o = [], []
        for _ in range(rounds):
            d = one(alias)
            if d:
                b.append(d['bound_s'] * 1e6)
                o.append(d['offset_s'] * 1e3)
        if len(b) >= 3:
            out[host] = {'pos': pos, 'what': what, 'hops': hops, 'n': len(b),
                         'bound_us': st.mean(b), 'bound_sd': st.stdev(b),
                         'bound_sem': st.stdev(b) / math.sqrt(len(b)),
                         'offset_ms': st.mean(o), 'offset_sd': st.stdev(o)}
        else:
            out[host] = {'pos': pos, 'what': what, 'hops': hops, 'n': len(b),
                         'err': 'fewer than three replicates'}
    return out


POOL = {'1': 1.0, '12/11': 12 / 11, '9/8': 1.125, '6/5': 1.2, '5/4': 1.25, '4/3': 4 / 3,
        '3/2': 1.5, '1.483198': PHI * 11 / 12, '8/5': 1.6, 'phi': PHI, '5/3': 5 / 3,
        '15/8': 1.875, '2': 2.0, '9/4': 2.25, '5/2': 2.5, '8/3': 8 / 3, '3': 3.0,
        '16/5': 3.2, '13/4': 3.25, 'pi': PI, '10/3': 10 / 3, '7/2': 3.5, '4': 4.0,
        'phi^2': PHI ** 2, 'phi^3': PHI ** 3, '2pi': 2 * PI, 'pi^2': PI ** 2,
        '48/5': 9.6, '29/3': 29 / 3, '10': 10.0, 'e': math.e, 'sqrt(pi)': math.sqrt(PI)}


def cheap(tol):
    """the POOL'S OWN RATE at this tolerance, on the log axis, never against zero."""
    lo, hi = math.log(min(POOL.values())), math.log(max(POOL.values()))
    return min(sum(min(2 * tol, hi - lo) for _ in POOL) / (hi - lo), 1.0)


def read(name, what, a, b, claim=None):
    """the ratio of two readings of ONE event, with its width, then every ruler the sheet names."""
    r = a['bound_us'] / b['bound_us']
    fa, fb = a['bound_sem'] / a['bound_us'], b['bound_sem'] / b['bound_us']
    rw = r * math.sqrt(fa * fa + fb * fb)
    known = rw / r
    ranked = sorted(POOL.items(), key=lambda kv: abs(r - kv[1]) / kv[1])
    best, second = ranked[0], ranked[1]
    tb, ts = abs(r - best[1]) / best[1], abs(r - second[1]) / second[1]
    # THE EXCLUSION WIDTH, the sheet's own form: width < |rival - c| / (2c)
    need = abs(second[1] - best[1]) / (2 * best[1])
    row = {'name': name, 'what': what, 'ratio': r, 'width': rw, 'frac_width': known,
           'best': best[0], 'best_tol': tb, 'second': second[0], 'second_tol': ts,
           'exclusion_width_needed': need, 'separable': known < need,
           'regla_ok': known < tb, 'cheap': cheap(max(tb, 1e-9))}
    if claim:
        cn, cv = claim
        row['claim'] = cn
        row['claim_value'] = cv
        row['claim_tol'] = abs(r - cv) / cv
        row['claim_widths'] = abs(r - cv) / rw if rw else float('inf')
    return row


def show(r):
    print(f"  {r['name']}")
    print(f"    {r['what']}")
    print(f"    ratio {r['ratio']:.5f} +- {r['width']:.5f}   known to {100*r['frac_width']:.3f}%")
    if 'claim' in r:
        print(f"    THE SHEET CLAIMS {r['claim']} = {r['claim_value']:.6f}: "
              f"{100*r['claim_tol']:.3f}% off, {r['claim_widths']:.2f} widths")
    print(f"    nearest in the pool  {r['best']:<10} {100*r['best_tol']:>7.3f}% off   "
          f"cheap {100*r['cheap']:.1f}%")
    print(f"    runner-up            {r['second']:<10} {100*r['second_tol']:>7.3f}% off")
    print(f"    to tell them apart the reading must be known to {100*r['exclusion_width_needed']:.3f}%"
          f"; it is known to {100*r['frac_width']:.3f}%")
    print(f"    => {'SEPARABLE' if r['separable'] else 'NOT SEPARABLE -- the runner-up sits inside this width, so the nearest candidate is a TIE, not a match'}")
    if not r['regla_ok']:
        print(f"    => THE REGLA FAILS: the width is wider than the match, so it was never a "
              f"measurement of this candidate")
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rounds', type=int, default=8)
    a = ap.parse_args()
    print('  THE BONEFISH ON THE TIME HOPS -- three positions, one event, the sheet\'s conversions')
    print(f'  read {time.strftime("%H:%M:%S %Z, %-d %b %Y")}')
    print(f'  one event: the laptop\'s clock. {a.rounds} replicates per seat, widths before constants\n')
    S = seat_readings(a.rounds)
    print(f"  {'position':<12}{'seat':<11}{'hops':>5}{'bound us':>11}{'sd':>9}{'sem':>8}"
          f"{'known to':>10}{'n':>4}")
    for host, v in S.items():
        if 'err' in v:
            print(f"  {v['pos']:<12}{host:<11}{v['hops']:>5}   {v['err']}")
        else:
            print(f"  {v['pos']:<12}{host:<11}{v['hops']:>5}{v['bound_us']:>11.1f}"
                  f"{v['bound_sd']:>9.1f}{v['bound_sem']:>8.1f}"
                  f"{100*v['bound_sem']/v['bound_us']:>9.2f}%{v['n']:>4}")
    for host, v in S.items():
        if 'err' not in v:
            print(f"    {host:<10}{v['what']}")
    need = [h for h in ('MAC', 'PI', 'ARMATURE') if 'bound_us' not in S.get(h, {})]
    if need:
        print(f"\n  seats that did not read: {', '.join(need)}. The triangle has a missing corner, so")
        print(f"  there is no Bonefish this run, and that is the reading.")
        return 1
    M, P, A = S['MAC'], S['PI'], S['ARMATURE']
    print('\n  THE THREE CONVERSIONS, each a ratio of two readings of the same event:\n')
    R = [read('witness / observer', 'EL TESTIGO over EL MIRON -- the Pi over the Mac',
              P, M, ('12/11', 12 / 11)),
         read('time / observer', 'the apex over EL MIRON -- the Armature over the Mac',
              A, M, ('phi', PHI)),
         read('time / witness', 'the apex over EL TESTIGO -- the Armature over the Pi',
              A, P, ('phi x 11/12', PHI * 11 / 12))]
    for r in R:
        show(r)
    print('  THE SHEET ALREADY PRICED THIS SHAPE: of its own three, only the first could separate its')
    print('  candidates. Whatever this run says, that is the prior it lands against.\n')
    print('  WHERE PI ENTERS, from the sheet rather than from the ratios:')
    print(f"    pi = 10 arcsin(1/(2 phi)) = {10*math.asin(1/(2*PHI)):.12f}   exact -- THE PENTAGON")
    print(f"    (6/5)phi^2 = {1.2*PHI**2:.9f} vs pi {PI:.9f}: WITHDRAWN as an identity, kept as a row")
    print(f"      Peters 1978, OEIS A180251 -- a 15.3 ppm near-miss documented 48 years ago")
    print(f"    el roce = (1/12)(1/pi) = {(1/12)/PI:.12f} = 2.65 per cent, the friction term")
    print(f"    ladder(n) = (1/12)(1/phi)^n at phi^(2n) us spacings was CALLED AND MISSED")
    print(f"      (+0.42 / +2.46 / +1.74 / +0.80 / -1.98), so a rerun on us clock spacings needs a")
    print(f"      reason and not just more rounds.")
    h1 = A['bound_us'] / P['bound_us']
    print(f"\n  AND THE PRODUCT LAW, which kills the ladder reading before it starts: LA CABALGATA")
    print(f"  composes as a product. One air crossing here costs x{h1:.4f}; two would cost")
    print(f"  x{h1*h1:.4f} BY COMPOSITION. So a two-hop match to pi^2 is the one-hop match squared")
    print(f"  and carries nothing new. A pi POWER read off a ladder is never an independent row.")
    try:
        with open(LOG, 'a') as f:
            f.write(json.dumps({'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'rounds': a.rounds,
                                'seats': S, 'conversions': R}) + '\n')
    except Exception:
        pass
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
