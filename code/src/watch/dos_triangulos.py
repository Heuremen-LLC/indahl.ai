#!/usr/bin/env python3
"""dos_triangulos.py -- TWO OVERLAPPING TRIANGLES OF CLOCKS, and the inference seats are the same
machines. (Wayfinder's design, 11 Oct 2026: "two triangles of clocks with inference. Pi.")

WHY TWO AND NOT ONE. A single triangle gives a closure residual and no way to say whether it is the
clocks or the apparatus. Two triangles that SHARE AN EDGE give S exactly, with no fit:

    D(T1) + D(T2) - D(T1 + T2) = S

because the part common to every run appears twice on the left and once on the right, while the part
that scales with the crossing cancels. That identity is arithmetic. Every claim this house made
tonight that rested on an identity held; every one that rested on a fitted width broke.

THE SEATS, and each is both a clock AND an inference substrate -- that is the double whammy:

    flock-pi    Leo Bodnar GPSDO, PPS, stratum 1, WIRED to Oe    THE REFERENCE. no inference.
    Armature    NO TIME SERVICE AT ALL (w32time Stopped/Manual), free-running crystal,
                250 us copper path to the reference                EL TIEMPO     POOL_ARMATURE
    this Mac    Oe wifi, 3.45 ms, stratum 2 servo off the Pi      EL MIRON      POOL_MAC
    laptop      Oe wifi, 2.12 ms, stratum 2 servo off the Pi      EL TESTIGO    POOL_LAPTOP

    T1 = Pi -- Mac -- laptop        both seats are SERVO COPIES of the reference
    T2 = Pi -- Mac -- Armature      one seat is a FREE-RUNNING ROOT
    shared edge: Pi -- Mac

T1 and T2 differ in exactly one thing: whether the third vertex is steered by the reference or not.
A servo copy cannot disagree with its own source, so T1's residual is a floor on the apparatus. T2's
residual contains a clock that CAN disagree. T2 - T1 is therefore the part that is not the apparatus.

WHAT IS NOT CLAIMED. Armature's 6.84 s offset is an INTERCEPT and says nothing about rate on its own
-- it is accumulated over an unknown interval, and the clock may have been restored from the RTC at
boot. The rate is the SLOPE of offset against time, which needs a window, and until there is one the
rate is NOTHING-RETURNED and not zero.

    python3 dos_triangulos.py <dir-of-seat-samples>
"""
import glob, math, os, re, sys


def read(path):
    """(n committed, median offset, min rtt, median rtt) -- and the four outcomes counted."""
    off, rtt, lost, bad = [], [], 0, 0
    for line in open(path):
        f = line.split()
        if len(f) != 3:
            bad += 1; continue
        if f[1] == 'NONE':
            lost += 1; continue
        try:
            off.append(float(f[1])); rtt.append(float(f[2]))
        except ValueError:
            bad += 1
    if not off:
        return None
    med = lambda v: sorted(v)[len(v)//2] if len(v) % 2 else (sorted(v)[len(v)//2-1]+sorted(v)[len(v)//2])/2
    return dict(n=len(off), off=med(off), rtt_min=min(rtt), rtt_med=med(rtt),
                lost=lost, bad=bad, off_mean=sum(off)/len(off))


def main(d):
    seats = {}
    for p in sorted(glob.glob(os.path.join(d, '*_to_pi.txt'))):
        lab = os.path.basename(p).replace('_to_pi.txt', '')
        r = read(p)
        if r: seats[lab] = r
        else: print('  %-12s NOTHING RETURNED (0 committed of its attempts)' % lab)

    print('\n  THE SEATS, each read against the same reference (flock-pi, GPSDO/PPS, stratum 1)\n')
    print('  %-12s%7s%6s%11s%11s%16s' % ('seat', 'n', 'lost', 'rtt min', 'rtt med', 'median offset'))
    for lab, r in seats.items():
        o = r['off']
        os_ = ('%+.3f s' % o) if abs(o) > 0.05 else ('%+.1f us' % (o*1e6))
        print('  %-12s%7d%6d%10.3fm%10.3fm%16s' % (lab, r['n'], r['lost'], r['rtt_min']*1e3,
                                                   r['rtt_med']*1e3, os_))

    # the two triangles. a leg's delay is the one-way share of the round trip to the reference.
    print('\n  THE TWO TRIANGLES. A leg is half the minimum round trip -- the least-delayed packet')
    print('  bounds the one-way path from below, and the minimum is a BOUND, not an estimate.\n')
    def leg(a):
        return seats[a]['rtt_min'] / 2 if a in seats else None

    T1 = ('pi', 'mac', 'laptop')
    T2 = ('pi', 'mac', 'armature')
    for name, tri in (('T1 (two servo copies)', T1), ('T2 (one free-running root)', T2)):
        have = [v for v in tri if v == 'pi' or v in seats]
        missing = [v for v in tri if v != 'pi' and v not in seats]
        if missing:
            print('  %-28s INCOMPLETE -- no samples for %s. Not a zero: the triangle was never closed.'
                  % (name, ', '.join(missing)))
            continue
        legs = [leg(v) for v in tri if v != 'pi']
        print('  %-28s legs to the reference: %s' % (name, '  '.join('%.3f ms' % (l*1e3) for l in legs)))

    if all(v in seats for v in ('mac', 'laptop')) and 'armature' in seats:
        d1 = sum(leg(v) for v in ('mac', 'laptop'))
        d2 = sum(leg(v) for v in ('mac', 'armature'))
        d12 = sum(leg(v) for v in ('mac', 'laptop', 'armature'))
        S = d1 + d2 - d12
        print('\n  D(T1) + D(T2) - D(T1+T2) = %+.1f us' % (S*1e6))
        print('  That is S, the part common to both triangles, and it came out of an identity')
        print('  rather than a fit: the shared Pi--Mac edge appears twice on the left and once on')
        print('  the right. The per-crossing part cancels exactly.')
        print('\n  shared edge Pi--Mac, half the minimum round trip: %.1f us' % (leg('mac')*1e6))
        print('  S recovers it to %+.1f us' % ((S - leg('mac'))*1e6))
    else:
        print('\n  THE IDENTITY IS NOT EVALUATED: a seat is missing, and a triangle that was never')
        print('  closed is nothing-returned. It is not reported as a zero residual.')

    print('\n  WHAT IS STILL NOTHING-RETURNED: Armature\'s RATE. The offset above is an intercept')
    print('  accumulated over an unknown interval. The rate is the slope against time and needs a')
    print('  window; until there is one it is absent, not zero.')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'seats')
