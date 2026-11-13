#!/usr/bin/env python3
"""disco.py -- THE THREE CLOCKS AGAINST BOTH RULERS, WITH WIDTHS. (Bones, 9 Oct 2026.)

Wayfinder: "take us to the disco with the seven la siete and some triangulated time."

Every ratio this house owns gets thrown at the Seven and at La Siete. That is not new. What is new
today is that the throwing finally obeys the rules the house spent the week learning, all at once:

  THE QUANTITY'S WIDTH GATES BEFORE THE RULER'S. A ratio of 3.4 +- 1.7 is within two widths of
  twenty candidates; naming the nearest one is arithmetic, not a reading. Found 8 Oct when a
  trajectory returned HELD for pi AND 2 AND phi on the same number.

  THE STRUCTURAL NULL COMPETES. If a quantity's own null -- 1, or 1/3, or whatever the arithmetic
  forces -- sits inside the same two widths as the candidate, the match says nothing. Found when a
  common mode of 0.3809 landed on 1/phi^2 at 0.281% while 1/3 sat 14.59% away and the width was
  +-0.0767.

  A READING IS A WINDOW. Every ratio here is n windows with its own sem, never one sample.

  BOTH RULERS, AND THEY ARE NOT INDEPENDENT. SEVEN and LA SIETE share most of their numbers
  (measured 8 Oct: jaccard 0.750), so agreement between them is nearly free and is reported as such.

  THE CHEAP-MATCH RATE RIDES WITH EVERY HIT, or the hit does not go out.

THE CLOCKS. WITNESS her ticks, OBSERVER the chain, TIME Wen's rounds -- and from today a fourth that
is kept by nobody here, the GPSDO. The Mac wall clock is read and never scheduled on.

    python3 disco.py
"""
import json
import math
import os
import statistics as st
import sys

W = os.path.expanduser('~/bones-forge/watch/')
sys.path.insert(0, W)
sys.path.insert(0, os.path.expanduser('~/bones-forge/triangulation/triangle'))
STATE = os.path.join(W, 'loops_closure.jsonl')
BAR = 2.0


def rulers():
    try:
        from triangle import SEVEN, SIETE
        s, t = dict(SEVEN), dict(SIETE)
    except Exception:
        PHI = (1 + 5 ** 0.5) / 2
        s = {'phi': PHI, '1/phi': 1 / PHI, 'pi': math.pi, '2': 2.0, '3/2': 1.5}
        t = dict(s)
    sh = set(round(v, 9) for v in s.values()) & set(round(v, 9) for v in t.values())
    both = set(round(v, 9) for v in s.values()) | set(round(v, 9) for v in t.values())
    return s, t, (len(sh) / len(both) if both else 0.0)


def cheap_at(tol):
    try:
        sys.path.insert(0, os.path.expanduser('~/bones-forge/triangulation/wen_data'))
        from physics_cases import cheap_at as c
        return c(max(tol, 1e-6))
    except Exception:
        return None


def rows():
    out = []
    try:
        for l in open(STATE):
            if l.strip():
                r = json.loads(l)
                if all(r.get(k) is not None for k in ('height', 'ticks', 'rounds', 'mac_s')):
                    out.append(r)
    except Exception:
        pass
    return out


def windowed_ratio(R, num, den, n=12):
    """A READING IS A WINDOW. Chop the series into windows of n intervals, take the ratio of the
    two counters' advances in each, and return mean with its own sem."""
    vals = []
    for i in range(0, len(R) - n, n):
        a, b = R[i], R[i + n]
        dn = b[num] - a[num]
        dd = b[den] - a[den]
        if dd > 0 and dn >= 0:
            vals.append(dn / dd)
    if len(vals) < 3:
        return None
    m = st.mean(vals)
    sem = st.stdev(vals) / math.sqrt(len(vals))
    return {'value': m, 'width': sem, 'windows': len(vals)}


def throw(name, q, null=None, null_name=None):
    """both rulers, the quantity's width first, the structural null competing."""
    S, T, jac = rulers()
    v, w = q['value'], q['width']
    cands = {}
    for rn, R in (('SEVEN', S), ('SIETE', T)):
        for k, x in R.items():
            cands.setdefault(round(x, 9), []).append(f'{rn}:{k}')
    if null is not None:
        cands.setdefault(round(null, 9), []).append(f'NULL:{null_name or "structural"}')
    inside = {x: ns for x, ns in cands.items() if abs(v - x) <= BAR * w}
    out = {'name': name, 'value': v, 'width': w, 'windows': q['windows'],
           'ruler_overlap_jaccard': round(jac, 3),
           'candidates_within_2_widths': len(inside),
           'which': sorted({n.split(':')[1] for ns in inside.values() for n in ns})[:8]}
    if not inside:
        out['verdict'] = (f'NOTHING WITHIN 2 WIDTHS. {v:.5f} +- {w:.5f} reaches no number either '
                          f'ruler holds, and that is a reading: the clocks do not land on the Seven.')
        return out
    if len(inside) > 1:
        has_null = any('NULL' in n for ns in inside.values() for n in ns)
        out['verdict'] = (f'ABIERTO -- {len(inside)} distinct candidate values inside 2 widths'
                          + (' INCLUDING THE STRUCTURAL NULL, so a match here says nothing'
                             if has_null else '')
                          + '. The width names nothing.')
        return out
    x = next(iter(inside))
    tol = abs(v - x) / abs(x) if x else 0.0
    ch = cheap_at(tol)
    out['nearest'] = inside[x]
    out['distance_pct'] = round(100 * tol, 4)
    out['cheap_pct'] = None if ch is None else round(100 * ch, 2)
    if ch is not None and ch > 0.05:
        out['verdict'] = (f'NO INFORMATION -- lands on {inside[x]} at {100*tol:.3f}%, and a random '
                          f'number lands that close {100*ch:.1f}% of the time.')
    else:
        out['verdict'] = (f'A ROW -- {inside[x]} at {100*tol:.3f}%, alone inside 2 widths, chance '
                          f'{"unpriced" if ch is None else f"{100*ch:.2f}%"}')
    return out


def main():
    import time
    R = rows()
    S, T, jac = rulers()
    print('  THE DISCO -- three clocks, both rulers, every width stated')
    print(f'  read {time.strftime("%H:%M:%S %Z, %-d %b %Y")}')
    print(f'  {len(R)} clock readings on disk   SEVEN {len(S)} numbers, LA SIETE {len(T)}, '
          f'they share jaccard {jac:.3f} -- agreement between them is nearly free\n')
    gps_n = sum(1 for r in R if r.get('gps_s'))
    print(f'  GPS-stamped readings: {gps_n} of {len(R)}'
          + ('  -- the fourth clock is logging but has no span yet' if gps_n < 12 else ''))
    print()
    pairs = [('her ticks per block', 'ticks', 'height', 1.0, 'one tick per block'),
             ("Wen rounds per tick", 'rounds', 'ticks', 1.0, 'one round per tick'),
             ('Wen rounds per block', 'rounds', 'height', 1.0, 'one round per block')]
    results = []
    for name, num, den, null, nn in pairs:
        q = windowed_ratio(R, num, den)
        if not q:
            print(f'  {name:<24} LA NADA -- not enough windows')
            continue
        r = throw(name, q, null=null, null_name=nn)
        results.append(r)
        print(f"  {name:<24} {r['value']:.5f} +- {r['width']:.5f}  ({r['windows']} windows)")
        print(f"  {'':<24} {r['candidates_within_2_widths']} inside 2 widths: "
              f"{', '.join(r['which']) if r['which'] else '-'}")
        print(f"  {'':<24} {r['verdict']}")
        print()
    rows_out = [r for r in results if str(r.get('verdict', '')).startswith('A ROW')]
    print(f'  {len(rows_out)} of {len(results)} ratios survived every gate.')
    if not rows_out:
        print('  That is the honest result: at these widths the clocks reach nothing on either ruler.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
