#!/usr/bin/env python3
"""triangle_closed.py -- THE TRIANGLE, MEASURED FROM THE BEST SEATS, WITH ITS OWN NONE.
(Bones, 9 Oct 2026.)

Wayfinder: "do it right bones, and do it the properly computed and harmonized triangulated now."

WHAT WAS WRONG WITH EVERY TRIANGLE READING TONIGHT. All of them used the MAC as the measuring end,
and the Mac is the worst seat in the house. Measured hop ladder, same echo, same code:

    mac      -> laptop     two radio hops    bound 2492.4 us
    armature -> laptop      one radio hop    bound  769.5 us
    pi       -> armature    no radio hops    bound   80.2 us
    software floor, loopback                 bound   17-23 us

So the Mac was adding a factor of 31 to every leg it touched, and the triangles built from those
legs inherited it. The Pi and Armature are both on gigabit ethernet; the laptop is the only one of
the three without a port, which is also where the GPSDO's USB sits.

HOW THIS MEASURES INSTEAD. Each leg is read from the END THAT IS BETTER CONNECTED, and the Mac is
not an end at all:
    PI -> ARMATURE     wired to wired, the best path in the house
    PI -> LAPTOP       wired to wifi, one hop, read from the wired side
    ARMATURE -> LAPTOP wired to wifi, one hop, read from the wired side

AND THE NONE IS EXACT, WHICH IS THE WHOLE POINT OF A TRIANGLE. Clock offsets are antisymmetric and
additive, so going round the loop must return to where it started:

    off(PI,ARM) + off(ARM,LAP) + off(LAP,PI) = 0     identically

Nothing is assumed, nothing is shuffled, no synthetic family is needed. The CLOSURE RESIDUAL is the
error of the three measurements combined, and it cannot be argued with -- if the residual exceeds
what the three bounds allow, at least one leg is wrong. A triangle that closes is three readings
that agree; a triangle that does not is a fault with nowhere to hide.

THE CLOSURE IS ALSO NOT A WIDTH. It is a single exact identity, so it says SOMETHING IS WRONG without
saying which leg -- the third reading being that all three are consistent, which no pair can show.

    python3 triangle_closed.py
"""
import json
import math
import os
import statistics as st
import subprocess
import sys
import time

W = os.path.expanduser('~/bones-forge/watch/')
LOG = os.path.join(W, 'triangle_closed.jsonl')
# host: (ssh alias, its LAN address, how it is attached)
SEAT = {
    'PI':       ('flock-pi', '192.168.8.145', 'gigabit ethernet'),
    'ARMATURE': ('armature', '192.168.8.158', 'gigabit ethernet'),
    'LAPTOP':   ('laptop',   '192.168.8.123', 'wifi -- and it carries the GPSDO'),
}
# which end reads which leg: always the better-connected one, and never the Mac
LEGS = [('PI', 'ARMATURE'), ('PI', 'LAPTOP'), ('ARMATURE', 'LAPTOP')]
PY = {'flock-pi': 'python3', 'armature': 'python', 'laptop': 'python3'}


def read_leg(frm, to, n=400):
    """two-way from `frm` to `to`, run ON frm so the Mac is not in the path."""
    alias = SEAT[frm][0]
    ip = SEAT[to][1]
    try:
        p = subprocess.run(['ssh', '-o', 'ConnectTimeout=15', alias,
                            f'{PY[alias]} twoway_client.py {ip} {n}'],
                           capture_output=True, text=True, timeout=120)
        t = p.stdout.strip()
        d = json.loads(t[t.index('{'):])
        if 'err' in d:
            return None, d['err']
        return d, None
    except Exception as e:
        return None, f'{type(e).__name__}: {e}'


def main():
    now = time.strftime('%H:%M:%S %Z, %-d %b %Y')
    print('  THE TRIANGLE, READ FROM THE WIRED SEATS -- the Mac is not an end')
    print(f'  read {now}\n')
    for k, (a, ip, how) in SEAT.items():
        print(f'    {k:<10}{ip:<16}{how}')
    print()
    print(f"  {'leg':<22}{'read from':<12}{'offset ms':>12}{'bound us':>11}{'min RTT us':>12}{'n':>6}")
    O = {}
    B = {}
    for frm, to in LEGS:
        d, err = read_leg(frm, to)
        if d is None:
            print(f'  {frm+" -> "+to:<22}{frm:<12}FAILED: {err}')
            continue
        O[(frm, to)] = d['offset_s']
        B[(frm, to)] = d['bound_s']
        print(f"  {frm+' -> '+to:<22}{frm:<12}{d['offset_s']*1e3:>12.4f}"
              f"{d['bound_s']*1e6:>11.1f}{d['min_rtt_s']*1e6:>12.1f}{d['n']:>6}")
    if len(O) < 3:
        print('\n  fewer than three legs: no closure, and therefore no none. That is the reading.')
        return 1
    # THE CLOSURE. off(a,b) is how far b is ahead of a, so going round must return to zero.
    pa = O[('PI', 'ARMATURE')]
    pl = O[('PI', 'LAPTOP')]
    al = O[('ARMATURE', 'LAPTOP')]
    # off(PI,LAP) should equal off(PI,ARM) + off(ARM,LAP)
    resid = pl - (pa + al)
    allow = math.sqrt(sum(b * b for b in B.values()))
    print(f'\n  THE CLOSURE, which is exact by construction and needs no shuffle:')
    print(f'    off(PI,LAPTOP) should equal off(PI,ARMATURE) + off(ARMATURE,LAPTOP)')
    print(f'    {pl*1e3:+.4f}  vs  {pa*1e3:+.4f} + {al*1e3:+.4f} = {(pa+al)*1e3:+.4f} ms')
    print(f'    RESIDUAL {resid*1e6:+.1f} us')
    print(f'    the three bounds allow {allow*1e6:.1f} us in quadrature')
    print(f'    => {abs(resid)/allow:.2f} of what the bounds permit: '
          + ('THE TRIANGLE CLOSES. Three independent readings agree, and that is a statement no '
             'pair of them could make.' if abs(resid) <= allow else
             'IT DOES NOT CLOSE. At least one leg is wrong by more than its own bound, and the '
             'closure says so without saying which.'))
    # and now the harmonized form: the three legs as intervals, the Mac still absent
    print(f'\n  HARMONIZED -- the three legs as ratios, folded into one octave:')
    vals = {f'{a}/{b}': abs(v) for (a, b), v in O.items() if v}
    ks = list(vals)
    PHI = (1 + 5 ** 0.5) / 2
    # the pool this reading actually matches against: twelve folded intervals
    R = {'1/1': 1.0, '16/15': 16 / 15, '12/11': 12 / 11, '9/8': 9 / 8, '6/5': 1.2, '5/4': 1.25,
         '4/3': 4 / 3, 'phi': PHI, '3/2': 1.5, '8/5': 1.6, '5/3': 5 / 3, '15/8': 1.875}
    # 9 Oct: THE POOL AND THE PRICE DID NOT MATCH. The nearest was taken from these twelve folded
    # intervals and the cheapness came from physics_cases.cheap_at, which draws against THE SEVEN --
    # so a match on 16/15 was priced as though 16/15 had never been a candidate. The price now comes
    # from THIS pool, by The Bonefish, with the runner-up and the exclusion width beside it, and the
    # Seven's own figure is kept in its own column so the two are comparable instead of conflated.
    sys.path.insert(0, os.path.expanduser('~/bones-forge/watch'))
    import bonefish as BF
    # AND A WIDTH, which this reading never had: each leg's bound is its width, so a folded ratio of
    # two legs carries one. A match with no width was never a measurement of its candidate.
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            ka, kb = ks[i], ks[j]
            a, b = vals[ka], vals[kb]
            aw = B.get(tuple(ka.split('/')), 0.0) or 0.0
            bw = B.get(tuple(kb.split('/')), 0.0) or 0.0
            hi, lo = (a, b) if a >= b else (b, a)
            hw, lw = (aw, bw) if a >= b else (bw, aw)
            r = hi / lo
            rw = r * math.sqrt((hw / hi) ** 2 + (lw / lo) ** 2) if hi and lo else float('inf')
            oc = 0
            f, fw = r, rw
            while f >= 2:
                f /= 2
                fw /= 2
                oc += 1
            row = BF.row(f, fw, f'{ka} / {kb}', pool=R)
            print(f'    {ka} / {kb:<22}{r:>12.6f}  folded {f:.6f} +- {fw:.6f} ({oc} oct)')
            c = row['cheapness']
            print(f'       nearest {row["best"]:<8}{100*row["best_tol"]:>7.2f}% off  '
                  f'{row["best_widths"]:>6.2f} widths   runner-up {row["second"]:<8}'
                  f'{100*row["second_tol"]:>7.2f}% off')
            print(f'       cheap on THIS pool: log {100*c["log"]:.1f}%  draw {100*c["draw"]:.1f}%'
                  f'   vs the Seven alone {100*c["seven"]:.1f}%  (pool gap {100*c["pool_gap"]:+.1f})')
            print(f'       exclusion needs {100*row["exclusion_needed"]:.2f}%, known to '
                  f'{100*row["frac_width"]:.2f}%'
                  + ('' if row['separable'] else '  -- the runner-up is inside this width, so both '
                                                 'names stand and neither is chosen'))
    print(f'\n  and no cheapness column decides anything on its own now: each one names the pool it')
    print(f'  was computed on, because the pool gap above is the larger of the two effects.')
    try:
        with open(LOG, 'a') as f2:
            f2.write(json.dumps({'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
                                 'legs': {f'{a}->{b}': {'offset_s': v, 'bound_s': B[(a, b)]}
                                          for (a, b), v in O.items()},
                                 'closure_resid_s': resid, 'allowed_s': allow}) + '\n')
    except Exception:
        pass
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
