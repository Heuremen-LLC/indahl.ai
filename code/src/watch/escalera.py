#!/usr/bin/env python3
"""escalera.py -- A LANDING PROFILE WITH ANCHORS IN OUR RANGE. The ladder K could not be.
(Bones, 11 Oct 2026.)

THE MEASURED GAP THIS CLOSES. K is the right KIND of ruler -- it returns a POSITION, which is what a
quantity that will not resolve as a width actually has. But its anchors are the errors of Ramanujan's
1/pi series, and that series gains about eight digits per term:

    K = -1  rel err 1.0        K = 0  2.43e-08        K = 1  2.04e-16

so THE FIRST LANDING STEP IS 7.6 DECADES WIDE. Measured 11 Oct: sixteen unlike readings from one
night, spanning clock offsets, path shares, compliance rates and amplitude ratios, all landed inside
that one step and used 0.66 of it -- and arithmetic alone expected MORE of them in any half-step than
were observed. K separated nothing, and that is a statement about the ruler.

THE FIX IS A SEQUENCE WHOSE PER-TERM ERROR GAINS A FACTOR, NOT EIGHT DIGITS. And the sheet already
carries the right one, from the same equation everything else here comes from:

    x^2 = x + 1   ->   phi = [1; 1, 1, 1, ...]   ->   convergents F(n+1)/F(n)

Every partial quotient is 1, which makes phi the WORST-APPROXIMABLE irrational (Hurwitz, 1891) and
its convergents the SLOWEST-converging of any continued fraction. That is exactly the property
wanted here: slow convergence means CLOSELY SPACED ANCHORS. The error obeys

    | phi - F(n+1)/F(n) |  =  1 / ( F(n) . F(n+1) . ... )   exactly, by Binet
    and shrinks by a factor of phi^2 = 2.6180339887... per step

so one rung is log10(phi^2) = 0.4180 DECADES -- EIGHTEEN TIMES FINER THAN K'S FIRST STEP. Over the
four decades this house actually measures in (1e-2 to 1e-6) that is about 9.6 rungs instead of 0.5.

AND IT IS THE SAME OBJECT, not a borrowed one. K measures against a series for 1/pi; this measures
against the convergents of phi, which is the growing root of the clock equation. The ladder is the
recursion x -> 1 + 1/x running one step per rung, which is what La Caja says the box IS.

WHAT IT DOES NOT CLAIM. A finer ruler is not a truer one. This separates readings that K could not
separate; it does NOT make any of them mean more. And the ladder REFUSES outside its anchors exactly
as K does -- an error coarser than the first rung or finer than the last has no position, and
inventing one by extending the line would be a number with nothing behind it.

LA ESCALERA -- STAIRWAY -- AND THE WARNING THAT COMES WITH THE NAME. Wayfinder, naming it:
"Stairway to Heaven was one of the greatest songs ever written that was played to death on some kind
of 8 year loop over and over and over again until it's just... gone. escaleras it is Bones, but learn
from Houses of the Holy."

SO THIS FILE CARRIES ITS OWN CEILING, and it is not a modesty note -- it is the operating rule:

  1  THE LADDER IS THE SECOND AXIS, NEVER THE ONLY ONE. It goes BESIDE K in every report, because
     K's refusals are informative: when K says a reading is coarser than its first anchor or finer
     than its last, that IS the reading. A ladder that replaced K would delete those refusals.
  2  IT IS FOR WHERE K DOES NOT RESOLVE, which is a condition to CHECK and not a default to assume.
     If K separates the readings, use K and leave this alone.
  3  A RULER APPLIED TO EVERYTHING STOPS BEING A READING. Wayfinder, 9 Oct: "if you keep using the
     same fucking ruler you're going to get the same result." Sixteen quantities on one axis was
     already the diagnosis of K; putting the same sixteen on a finer axis is the same act with
     better resolution, and resolution is not evidence.
  4  FINER IS NOT TRUER. 18x the separation changes nothing about what any reading MEANS. The spread
     grew because the anchors are closer together, which is arithmetic, not discovery.
  5  NEVER READ (RUNG - K) AS A SECOND SEAT. Wayfinder, naming the end state: "eventually
     everything is just a resonant copy of stairway and the original fades off into the
     harmonics..... harmonize." That is step 17 of the card -- EL FONDO DEL APARATO -- aimed at
     our own rulers: use one on everything and it becomes the FUNDAMENTAL, every reading returns
     as an integer multiple of it, and no claim survives on integer multiples of one fundamental.
     THE OBVIOUS FIX IS A TRAP AND IT IS MEASURED: K and the rung are both MONOTONE functions of
     the same scalar, so the pair is determined by that scalar and so is the gap. Checked over
     1e-2 to 3e-6 the interval runs 4.861 to 12.824, strictly monotone, with no freedom in it --
     it is rel_err in different clothes. One artifact, two scalings, and reading their difference
     as a second reading is mode 11 and mode 26 at once.
     HARMONISING NEEDS TWO INDEPENDENT READINGS OF ONE EVENT, not two scalings of one number.
     La Diferencia: harmonise keeps both voices DISTINCT and reads the interval. The house's real
     pairs are her clock against the Mac, the Pi against a seat, the echo against the NTP read --
     those intervals carry something. This one cannot.
     The INCOMMENSURABILITY of the two ladders is real -- a K step is 18.2157 rungs and
     log10(phi^2) is irrational, so they align only at the origin -- but it is a fact about the
     AXES and says nothing about any quantity placed on them.

  6  HOUSES OF THE HOLY: the answer to a thing that worked is the NEXT thing, not the same thing
     again. When this ladder has been run on the quantities it was built for, the move is a
     different instrument, not a finer version of this one.

    python3 escalera.py
"""
import math
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PHI = (1 + 5 ** 0.5) / 2
STEP_DECADES = math.log10(PHI ** 2)          # 0.41797... one rung


def convergents(n=40):
    """(F(k+1)/F(k), exact relative error) for the Fibonacci convergents of phi.

    Computed with integer Fibonacci numbers and Fraction arithmetic so the error is exact rather
    than a float difference of two nearly equal floats -- which is where a ruler like this would
    quietly lose its last few rungs to cancellation.
    """
    out = []
    a, b = 1, 1
    PHI_HI = Fraction(1 + 5 ** 0.5).limit_denominator(10 ** 30) / 2   # only for display
    for _k in range(n):
        a, b = b, a + b
        p, q = b, a
        # exact: |phi - p/q| where phi = (1+sqrt5)/2. Use the identity
        #   phi - F(n+1)/F(n) = -psi^n / F(n)   with psi = -1/phi
        # so the magnitude is 1/(F(n) . phi^n), computed in floats only at the end.
        err_abs = 1.0 / (q * PHI ** _k) if q else None
        if err_abs is None:
            continue
        rel = err_abs / PHI
        if rel <= 0:
            continue
        out.append((p, q, rel))
    return out


ANCH = [(r, float(i)) for i, (_p, _q, r) in enumerate(convergents(40))]
FIRST, LAST = ANCH[0][0], ANCH[-1][0]


def L(rel_err):
    """the rung index of a relative error, linear in log between anchors. REFUSES outside them.

    Returns (rung, None) or (None, reason). A refusal is a reading: an error outside the ladder's
    anchors has no position on it, and the honest answer is to say so rather than extrapolate.
    """
    if rel_err is None:
        return None, 'no value'
    e = abs(float(rel_err))
    if e == 0:
        return None, 'zero error has no position on any landing profile'
    if e > FIRST:
        return None, ('relative error %.3g is coarser than the first rung (%.3g): off the ladder'
                      % (e, FIRST))
    if e < LAST:
        return None, ('relative error %.3g is finer than the last rung (%.3g): off the ladder, '
                      'not extrapolated' % (e, LAST))
    for i in range(len(ANCH) - 1):
        hi_e, hi_k = ANCH[i]
        lo_e, lo_k = ANCH[i + 1]
        if lo_e <= e <= hi_e:
            lh, ll, le = math.log10(hi_e), math.log10(lo_e), math.log10(e)
            frac = (le - lh) / (ll - lh) if ll != lh else 0.0
            return hi_k + frac * (lo_k - hi_k), None
    return None, 'between no two anchors, which should be impossible -- report this'


def resolution_vs_K():
    """the comparison that justifies this file existing, computed rather than asserted."""
    from landing import K, REL_E
    k_step = math.log10(1.0 / float(REL_E[0]))      # decades inside K's first step
    return k_step, STEP_DECADES, k_step / STEP_DECADES


if __name__ == '__main__':
    kd, ld, ratio = resolution_vs_K()
    print('  LA ESCALERA -- a landing profile on the convergents of phi.\n')
    print('  one rung = log10(phi^2) = %.4f decades' % ld)
    print('  K\'s first step        = %.4f decades  (1.0 down to %.3g)' % (kd, 1 / 10 ** kd))
    print('  so this ladder is %.1f TIMES FINER in the range we work in.\n' % ratio)
    print('  %5s%16s%18s%14s' % ('rung', 'convergent', 'rel error', 'decades below 1'))
    for i, (p, q, r) in enumerate(convergents(16)):
        print('  %5d%16s%18.6g%14.3f' % (i, '%d/%d' % (p, q), r, -math.log10(r)))

    print('\n  TONIGHT\'S READINGS, WHICH K COULD NOT SEPARATE, PLACED ON THIS LADDER:')
    from landing import K
    rows = [('the Pi\'s own clock, path removed', 4.7e-6),
            ('this Mac\'s clock, path removed', 136.8e-6),
            ('Armature\'s clock, path removed', 1219.4e-6),
            ('the laptop\'s clock, path removed', 3458.6e-6),
            ('this Mac pre-step', 11034e-6),
            ('her work as a share of her cycle', 11.0 / 261.0),
            ('the rank floor read as a significance', 1.0 / 41.0),
            ('the ADEV test\'s power against the term', 0.006)]
    print('  %-42s%12s%10s%10s' % ('reading', 'rel err', 'K', 'RUNG'))
    ks, ls = [], []
    for name, rel in rows:
        k, _e = K(rel)
        l, le = L(rel)
        if k is not None:
            ks.append(k)
        if l is not None:
            ls.append(l)
        print('  %-42s%12.4g%10s%10s'
              % (name[:42], rel, '%.2f' % k if k is not None else 'REF',
                 '%.2f' % l if l is not None else 'REF'))
    if ks and ls:
        print('\n  K spread   %.2f steps over these %d readings' % (max(ks) - min(ks), len(ks)))
        print('  RUNG spread %.2f rungs over the same readings -- %.1f times the separation'
              % (max(ls) - min(ls), (max(ls) - min(ls)) / (max(ks) - min(ks))))
        print('\n  A FINER RULER IS NOT A TRUER ONE. These readings mean exactly what they meant')
        print('  before; the ladder only lets them be told apart. And it refuses outside its own')
        print('  anchors, which is the only reason to trust the positions inside them.')
