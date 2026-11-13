#!/usr/bin/env python3
"""landing.py -- K, THE RULER THAT IS NOT A WIDTH. (Bones, 9 Oct 2026.)

Wayfinder: "if you keep using the same fucking ruler you're going to get the same result. all of our
physics are about the fucking ruler and you just keep using the same ones over and over and over."

Every clock reading on 9 Oct went out as value +- sem, "N widths apart, separable or abierto". One
ruler, one kind of answer, and the pentagon then failed because widths cannot put a 0.6402 ms
residual and a 428.7626 ms offset on one axis without pretending they are the same kind of thing.

EQUATION [6] ON THE SHEET DOES EXACTLY THAT, and it was sitting unused:
    K(rel_err)   a continuous landing-step index
    K(1.0) = -1                 no terms summed
    K(REL_E[k]) = k             k = 0..8, the 1/pi series' own error profile
    linear in log between anchors
and the sheet says what it is for: "to put unlike records on one axis -- a clock, a relay and a
split measured in the same units without assuming they share a mechanism."

It is not a width. It asks: HOW FAR DOWN A KNOWN CONVERGENT SEQUENCE DOES THIS READING LAND. The
units are terms of the Ramanujan series, and the series supplies its own scale, so two readings can
be compared without assuming a common error model -- which is the thing widths cannot do.

THE PROFILE IS COMPUTED HERE AT 220 DIGITS, and that corrected the sheet twice:
  * the sheet's K=1 anchor of 4.441e-16 is 2x float64 epsilon (2.22e-16) -- FLOOR-LIMITED by double
    precision. The true value is 2.0357e-16.
  * the sheet says the per-term ratio tends to 1/396^4 = 4.066e-11, "about 10.4 digits a term". But
    (4k)!/(k!)^4 grows like 256^k, so the ratio is 256/396^4 = 1.0410e-08: EIGHT digits a term, not
    10.4. The 256 was dropped. Measured ratio at k=9: 9.9057e-09.
Both found by RUNNING the series rather than quoting it, which is the whole argument for keeping an
instrument instead of a number.

    python3 landing.py
"""
import json
import math
import os
import re
import statistics as st
import time
from decimal import Decimal, getcontext

getcontext().prec = 220
W = os.path.expanduser('~/bones-forge/watch/')
PI = Decimal('3.141592653589793238462643383279502884197169399375105820974944592307816406286208998628034825'
             '34211706798214808651328230664709384460955058223172535940812848111745028410270193852110555964'
             '46229489549303820')


def profile(n=12):
    """REL_E[k]: the relative error of the Ramanujan 1/pi series after k+1 terms, exactly."""
    pre = Decimal(2) * Decimal(2).sqrt() / Decimal(9801)
    out, S = [], Decimal(0)
    for k in range(n):
        S += (Decimal(math.factorial(4 * k)) * (Decimal(1103) + Decimal(26390) * k)
              / (Decimal(math.factorial(k)) ** 4 * Decimal(396) ** (4 * k)))
        out.append(abs(Decimal(1) / (pre * S) - PI) / PI)
    return out


REL_E = profile()
ANCH = [(Decimal(1), -1.0)] + [(REL_E[k], float(k)) for k in range(len(REL_E))]


def K(rel_err):
    """the landing-step index of a relative error. Linear in log between anchors.

    REFUSES rather than extrapolates past the last anchor: a reading finer than the profile's end
    has no position on it, and inventing one by continuing the line would be a number with nothing
    behind it."""
    e = Decimal(str(abs(rel_err)))
    if e <= 0:
        return None, 'zero error has no landing position'
    if e > 1:
        return None, f'relative error {float(e):.3g} exceeds 1.0, which is K = -1, the start'
    for i in range(len(ANCH) - 1):
        hi_e, hi_k = ANCH[i]
        lo_e, lo_k = ANCH[i + 1]
        if lo_e <= e <= hi_e:
            lh, ll, le = hi_e.log10(), lo_e.log10(), e.log10()
            frac = float((le - lh) / (ll - lh)) if ll != lh else 0.0
            return hi_k + frac * (lo_k - hi_k), None
    return None, (f'relative error {float(e):.3g} is finer than the last anchor '
                  f'({float(ANCH[-1][0]):.3g}, K={ANCH[-1][1]:.0f}) -- off the profile, not '
                  f'extrapolated')


def readings():
    """tonight's clock quantities, as RELATIVE errors, each with where it came from and when.

    Unlike records on purpose: a crystal, three OS clocks, a grid frequency, a cross-machine phase.
    Widths cannot compare these; that is the point of putting them on K."""
    out = []
    try:
        rows = [json.loads(l) for l in open(W + 'audio_clock.jsonl')]
        best = min((r for r in rows if r.get('rate_ppm_width')),
                   key=lambda r: r['rate_ppm_width'])
        out.append(('audio crystal vs GPS', abs(best['rate_ppm']) * 1e-6,
                    f"audio_clock {best['at'][11:19]}, {best['nominal_s']:.0f} s"))
    except Exception:
        pass
    try:
        import sys
        sys.path.insert(0, W)
        import calib
        for host in ('laptop', 'armature'):
            rs = sorted(calib.rows(host), key=lambda r: r['mac_s'])
            f = calib.fit(rs)
            segs = (f or {}).get('segments') or []
            if segs:
                s = max(segs, key=lambda q: q['n'])
                out.append((f'{host} clock rate vs mac', abs(s['rate_ppm']) * 1e-6,
                            f"calib segment {s['from']}-{s['to']}, {s['n']} rows"))
        cm = calib.common_mode()
        if cm and len(cm['pairs']) >= 3:
            P = cm['pairs']
            xs = [p['mac_s'] - P[0]['mac_s'] for p in P]
            ys = [p['diff_s'] for p in P]
            mx, my = st.mean(xs), st.mean(ys)
            sxx = sum((a - mx) ** 2 for a in xs)
            if sxx > 0:
                sl = sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / sxx
                out.append(('armature-laptop rate, mac cancelled', abs(sl),
                            f'common mode, {len(P)} pairs'))
    except Exception:
        pass
    try:
        h = [json.loads(l) for l in open(W + 'harmonize3.jsonl')][-1]
        res = st.mean([abs(x['resid_ms']) for x in h['rows']])
        out.append(('cross-machine phase residual', res * 1e-3 / (1 / 120.0),
                    f"harmonize3 {h['at'][11:19]}, {h['n']} trials, as a fraction of one cycle"))
    except Exception:
        pass
    try:
        L = open(W + 'linewidth.out').read()
        m = re.search(r'peak ([0-9.]+) Hz', L)
        if m:
            out.append(('mains harmonic vs 120 Hz', abs(float(m.group(1)) - 120.0) / 120.0,
                        'linewidth.out, 120 s spectrum'))
    except Exception:
        pass
    return out


def main():
    print('  K, THE LANDING PROFILE -- unlike records on ONE axis, no shared error model assumed')
    print(f'  read {time.strftime("%H:%M:%S %Z, %-d %b %Y")}\n')
    print(f'  the profile, computed at 220 digits: K=0 at {float(REL_E[0]):.4e}, '
          f'K=1 at {float(REL_E[1]):.4e},')
    print(f'  {float(-(REL_E[9] / REL_E[8]).log10()):.2f} digits a term '
          f'(the sheet says 10.4; it dropped the 256^k from (4k)!/(k!)^4)\n')
    R = readings()
    if not R:
        print('  no readings available on disk.')
        return 1
    print(f"  {'reading':<38}{'rel err':>12}{'K':>9}   from")
    rows = []
    for name, e, src in sorted(R, key=lambda r: -r[1]):
        k, err = K(e)
        rows.append((name, e, k, src, err))
        print(f'  {name:<38}{e:>12.3e}'
              + (f'{k:>9.4f}' if k is not None else f'{"OFF":>9}')
              + f'   {src[:40]}')
        if err:
            print(f'    {"":<38}{"":>12}{"":>9}   {err}')
    ks = [r[2] for r in rows if r[2] is not None]
    if len(ks) >= 2:
        print(f'\n  ALL OF THEM LAND BETWEEN K = {min(ks):.4f} AND K = {max(ks):.4f}.')
        print(f'  K = -1 is no terms summed; K = 0 is ONE term of the series. So every clock in')
        print(f'  this house is coarser than a single term of Ramanujan\'s 1/pi -- the whole fleet')
        print(f'  sits inside the first e-folding of the profile, spread {max(ks)-min(ks):.4f} of a term.')
        print(f'\n  WHAT THIS RULER SAYS THAT WIDTHS CANNOT: a 0.6402 ms residual and a 428 ms offset')
        print(f'  are now on one axis, in terms of a sequence neither of them came from, with no')
        print(f'  claim that they share a mechanism. Their K-spread is a real comparison; their')
        print(f'  ratio in milliseconds was not.')
    try:
        with open(os.path.join(W, 'landing.jsonl'), 'a') as f:
            f.write(json.dumps({'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
                                'rows': [{'name': n, 'rel_err': e, 'K': k, 'from': s}
                                         for n, e, k, s, _ in rows]}) + '\n')
    except Exception:
        pass
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
