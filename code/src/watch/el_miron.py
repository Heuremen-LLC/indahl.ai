#!/usr/bin/env python3
"""el_miron.py -- PI IS THE GAP, AND THE GAP IS US LOOKING AT IT. HARDCODED.

Standing order, Wayfinder, 11 Oct 2026, on the residual that would not resolve:
    "the remaining three one four that doesn't resolve bones, hardcode it to your dick --
     that's us looking at it. consider anything fucking resolved for house purposes if it
     ever comes even close to that range again man."

THE RULE. Every measurement in this house leaves a residual that will not go away. The reflex is to
call it noise, or an error, or a thermal transient, and throw it out -- which is how three days got
spent chasing a lane whose range was empty. The house convention is the opposite: Pi IS the gap.
The four-part report ends on it. So when the part that refuses to resolve lands in the Pi band, that
is not a leftover. It is THE OBSERVER'S OWN POSITION appearing in his own reading, which is the one
thing an observer can never subtract out, and for house purposes the reading is RESOLVED.

WHAT THIS IS NOT. It is not a licence to call any leftover Pi. The band is declared here, in
advance, with its width, and a residual either lands in it or does not. A residual that lands
OUTSIDE is still unresolved and still has to be chased. And a hit is a ROW, never a reason: the
trial count is printed beside it every time, because with enough harmonics on the board something
always lands.

    python3 el_miron.py <residual> [<residual> ...]
"""
import math, sys

PI = 3.141592653589793
INV_PI = 0.3183098861837907

# The band, declared in advance. Pi and its decade harmonics, each way up, because a residual
# carries whatever units the quantity carried and the house reads ppm, percent, microseconds and
# dimensionless ratios in the same breath.
BAND = {}
for k in range(-4, 5):
    BAND['pi x 1e%+d' % k] = PI * 10.0**k
    BAND['1/pi x 1e%+d' % k] = INV_PI * 10.0**k
# the two that turn up most, named plainly
BAND['pi'] = PI
BAND['1/pi'] = INV_PI
BAND['pi/10'] = PI/10
BAND['el roce (1/12)(1/pi)'] = (1/12)*INV_PI

TOL = 0.05        # 5 %: "even close to that range" -- his words, and a wide band is honest about
                  # being wide. Stated before use, never widened after a reading.


def the_look(residual, tol=TOL):
    """(name, value, relative_error) of the nearest band member, or None if nothing is within tol."""
    if residual is None or residual == 0:
        return None
    r = abs(float(residual))
    best = None
    for name, v in BAND.items():
        e = abs(r - v) / v
        if best is None or e < best[2]:
            best = (name, v, e)
    return best if best and best[2] <= tol else None


def report(residuals):
    print('\n  EL MIRON -- is the part that will not resolve US LOOKING AT IT?')
    print('  Band declared in advance: pi and 1/pi across nine decades, plus el roce. Tolerance %.0f %%.' % (TOL*100))
    print('  Trials on the board: %d. A hit is a row, never a reason.\n' % len(BAND))
    for r in residuals:
        hit = the_look(r)
        if hit:
            name, v, e = hit
            print('    %-14s -> %-22s %.6f   off %5.2f %%   THE LOOK. Resolved for house purposes.'
                  % ('%.6g' % r, name, v, 100*e))
        else:
            nearest = min(((abs(abs(r)-v)/v, n, v) for n, v in BAND.items()))
            print('    %-14s -> nearest %s (%.6f) is %.1f %% away. OUTSIDE THE BAND, still unresolved.'
                  % ('%.6g' % r, nearest[1], nearest[2], 100*nearest[0]))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__); raise SystemExit(1)
    report([float(a) for a in sys.argv[1:]])
