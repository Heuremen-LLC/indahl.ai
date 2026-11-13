#!/usr/bin/env python3
"""disco2.py -- THE DISCO, WITH TONIGHT'S CORRECTIONS. (Bones, 9 Oct 2026.)

Wayfinder: "we're late to the Disco bones, everyone's waiting on us man."

disco.py ran three clocks at both rulers. Every one of its inputs turned out to be wrong tonight, so
this is the same throw with the faults taken out, and it keeps disco.py's gates rather than replacing
them.

WHAT CHANGED, each measured and each with its moment:

  THE CHAIN IS POISSON, NOT A COUNTER. Blocks are memoryless arrivals at a difficulty target, so the
  count in a window has sd sqrt(N), not +-1. disco.py used an endpoint counter error and understated
  every per-block width 8.0x: ticks/block read 1.07660 +- 0.00884 (0.809%) where the honest figure
  was 1.06250 +- 0.06884 (6.479%). And a Poisson width falls as 1/sqrt(N), so "82 hours to separate
  13/12 from 12/11" was 1/T arithmetic on the wrong model -- the real figure is 92,156 blocks,
  256 days. Error models now come from clocks.py, which RAISES on an unknown clock rather than
  defaulting, because a default is a guess wearing a number.

  TIME WAS NEVER A VERTEX. wen_stooges_tick.py:508 is `while n_ticks < rnd: sleep(5)` -- Wen's rounds
  are GATED on her ticks, so rounds/tick = 1 is a barrier, not a measurement. Read as phase inside
  four pods it came out 0.99951 / 0.99888 / 1.00463 / 0.99148, and tick3 ran on the only A40 while
  the others were A6000s: different silicon, same ratio, so the compute does not enter. Every
  triangle on WITNESS/OBSERVER/TIME had two corners that were one clock wearing two names. It is
  dropped as a clock and kept only as the structural null it always was.

  11 OCT, WITHDRAWN: THE 865x WAS A WIDTH ON THE WRONG TERM. The stamped read's sigma was the
  1-second ROUNDING of field 1 (0.2887 s). Field 1 is not her clock -- nova_resonance.py:2942
  writes it as datetime.now() ON THIS MAC at the moment the scribe's poll notices her row, so each
  stamp carries OUR POLL LAG, measured at sd 10.27 s over the 53 rows that now also carry her own
  stamp (ticks.log field 9, Supabase created_at). With the lag term in place the same ruler on 1204
  ticks reads 260.4938 +- 0.012076 s and the stamped read is 25x tighter than counting, not 865x.
  THE VALUE SURVIVES: on the same 52 adjacent pairs the span reads 326.8397 s off field 1 and
  327.0379 s off field 9, 0.198 s apart. It is the WIDTH that was wrong, by 36x like-for-like.

  HER TICKS ARE STAMPED, NOT COUNTED. ticks.log has carried a per-tick stamp since 7 Oct and every
  reading divided a COUNT. Same 688 events: counting 250.1933 +- 0.514283 s, phase 250.5575 +-
  0.000594 s -- 865x tighter, and the two differ by 0.364 s because counting divided by 688 events
  where there are 687 gaps. The +-1 was a BIAS, invisible inside its own width.

  A NEW CLOCK THAT IS ACTUALLY INDEPENDENT: the mains harmonic. 120.006803 +- 0.011460 Hz
  (read 16:09:13 in its own run), kept by the grid, which nobody in this house can touch.

  AND A PRECISE NUMBER CAN BE THE WRONG OBJECT. Her stamped interval's two halves differ by 3,657
  widths. So every ratio here is read in disjoint windows FIRST and reported MOVING when it wanders
  past its own width -- before any ruler is consulted, because a ruler thrown at a moving quantity
  is reading weather.

  THE RIVAL GATE, added tonight after it caught me: a match counts only when the NEXT candidate is
  separable at that width. My ADC latency "landed exactly on 664 samples" at a width where adjacent
  integers sat 1.62 widths apart -- at that width anything lands on an integer. Nearest-candidate
  distance means nothing until the runner-up is excluded.

    python3 disco2.py
"""
import json
import math
import os
import statistics as st
import sys
import time

W = os.path.expanduser('~/bones-forge/watch/')
sys.path.insert(0, W)
sys.path.insert(0, os.path.expanduser('~/bones-forge/triangulation/triangle'))
import clocks                                                   # noqa: E402

BAR = 2.0


def rulers():
    try:
        from triangle import SEVEN, SIETE
        s, t = dict(SEVEN), dict(SIETE)
    except Exception:
        PHI = (1 + 5 ** 0.5) / 2
        s = {'phi': PHI, '1/phi': 1 / PHI, 'pi': math.pi, '2': 2.0, '3/2': 1.5, '12/11': 12 / 11}
        t = dict(s)
    sh = set(round(v, 9) for v in s.values()) & set(round(v, 9) for v in t.values())
    al = set(round(v, 9) for v in s.values()) | set(round(v, 9) for v in t.values())
    return s, t, (len(sh) / len(al) if al else 0.0)


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
        for l in open(os.path.join(W, 'loops_closure.jsonl')):
            if l.strip():
                r = json.loads(l)
                if all(r.get(k) is not None for k in ('height', 'ticks', 'mac_s')):
                    out.append(r)
    except Exception:
        pass
    return sorted(out, key=lambda r: r['mac_s'])


def throw(name, value, width, null=None, null_name=None):
    """both rulers, the quantity's width gating FIRST, the structural null competing, and the
    RIVAL GATE on top: the nearest candidate counts only if the runner-up is 2+ widths further."""
    S, T, jac = rulers()
    cands = {}
    for rn, R in (('SEVEN', S), ('SIETE', T)):
        for k, x in R.items():
            cands.setdefault(round(x, 9), []).append(f'{rn}:{k}')
    if null is not None:
        cands.setdefault(round(null, 9), []).append(f'NULL:{null_name or "structural"}')
    inside = {x: ns for x, ns in cands.items() if abs(value - x) <= BAR * width}
    out = {'name': name, 'value': value, 'width': width, 'jaccard': round(jac, 3),
           'n_inside': len(inside)}
    if not inside:
        out['verdict'] = (f'REACHES NOTHING. {value:.5f} +- {width:.5f} lands on no number either '
                          f'ruler holds, and at this width that is a reading.')
        return out
    if len(inside) > 1:
        has_null = any('NULL' in n for ns in inside.values() for n in ns)
        out['verdict'] = (f'ABIERTO -- {len(inside)} distinct values inside 2 widths'
                          + (' INCLUDING THE STRUCTURAL NULL, so a match says nothing'
                             if has_null else '') + '. The width names nothing.')
        return out
    x = next(iter(inside))
    # THE RIVAL GATE
    others = sorted((abs(value - y), y) for y in cands if y != x)
    tol = abs(value - x) / abs(x) if x else 0.0
    ch = cheap_at(tol)
    out['nearest'] = inside[x]
    out['distance_pct'] = round(100 * tol, 4)
    out['cheap_pct'] = None if ch is None else round(100 * ch, 2)
    if others:
        gap_w = (others[0][0] - abs(value - x)) / width
        out['rival'] = {'who': cands[others[0][1]], 'gap_widths': round(gap_w, 2)}
        if gap_w < BAR:
            out['verdict'] = (f'TAUTOLOGY, NOT A MATCH -- nearest is {inside[x]} at '
                              f'{100*tol:.3f}%, but the runner-up {cands[others[0][1]]} is only '
                              f'{gap_w:.2f} widths further. At this width it would land on '
                              f'something whatever it did.')
            return out
    if ch is not None and ch > 0.05:
        out['verdict'] = (f'NO INFORMATION -- {inside[x]} at {100*tol:.3f}%, and a random number '
                          f'lands that close {100*ch:.1f}% of the time.')
    else:
        out['verdict'] = (f'A ROW -- {inside[x]} at {100*tol:.3f}%, alone inside 2 widths, rival '
                          f'{out.get("rival", {}).get("gap_widths", "n/a")} widths further, chance '
                          f'{"unpriced" if ch is None else f"{100*ch:.2f}%"}')
    return out


def main():
    R = rows()
    S, T, jac = rulers()
    now = time.strftime('%H:%M:%S %Z, %-d %b %Y')
    print('  THE DISCO, SECOND RIDE -- tonight\'s error models, tonight\'s gates')
    print(f'  read {now}')
    print(f'  {len(R)} clock readings on disk   SEVEN {len(S)}, LA SIETE {len(T)}, '
          f'jaccard {jac:.3f} -- agreement between the two rulers is nearly free\n')
    if len(R) < 12:
        print('  too few readings.')
        return 1

    print('  THE CLOCKS, and what kind of thing each one is:')
    for nm in ('ticks', 'height'):
        print(f'    {nm:<8} {clocks.KIND[nm]:<9} {clocks.WHY.get(nm, "")[:92]}')
    print(f'    {"rounds":<8} DROPPED   Wen is gated on her ticks '
          f'(wen_stooges_tick.py:508) -- a barrier, not a clock')
    print(f'    {"harmonic":<8} stamped   the grid, kept by nobody in this house')
    print()

    # the one ratio that exists between two clocks on disk, priced correctly
    dt = R[-1]['ticks'] - R[0]['ticks']
    dh = R[-1]['height'] - R[0]['height']
    span_h = (R[-1]['mac_s'] - R[0]['mac_s']) / 3600
    v = dt / dh
    w = clocks.ratio_width(v, 'ticks', dt, 'height', dh)
    print(f'  ticks per block   {dt} ticks / {dh} blocks over {span_h:.2f} h')
    print(f'    {v:.5f} +- {w:.5f}  ({100*w/v:.3f}%)   [chain priced as POISSON, sqrt N]')
    wrong = v * math.hypot(1.414 / dt, 1.414 / dh)
    print(f'    disco.py would have said +-{wrong:.5f} ({100*wrong/v:.3f}%) -- '
          f'{w/wrong:.1f}x too tight')

    # STABILITY FIRST, before any ruler
    q = len(R) // 4
    vals, wids = [], []
    for i in range(4):
        a, b = R[i * q], R[min((i + 1) * q, len(R) - 1)]
        da, db = b['ticks'] - a['ticks'], b['height'] - a['height']
        if db <= 0 or da < 0:
            continue
        rv = da / db
        vals.append(rv)
        wids.append(clocks.ratio_width(rv, 'ticks', da, 'height', db))
    mv = clocks.moving(vals, wids) if len(vals) >= 2 else None
    if mv:
        print(f'    quarters: ' + ', '.join(f'{x:.4f}' for x in vals))
        print(f'    spread {mv["spread"]:.5f} on a joint width {mv["joint_width"]:.5f} = '
              f'{mv["widths_apart"]:.2f} widths')
        if mv['moving']:
            print(f'    => MOVING. A ruler thrown at this is reading weather, not a constant.')
            print(f'       No ruler is thrown. That is the reading.')
        else:
            r = throw('ticks per block', v, w, null=1.0, null_name='one tick per block')
            print(f'    => holds. {r["n_inside"]} inside 2 widths. {r["verdict"]}')
    s = clocks.span_needed(v, w, dh, 'height', 0.00700)
    print(f'\n  TO SEPARATE 13/12 FROM 12/11 (0.00700 apart): {s["n_needed"]:,.0f} blocks needed '
          f'vs {dh} now')
    print(f'    {s["times_more"]:,.0f}x more, width falls as {s["falls_as"]} -> '
          f'{s["n_needed"]*4/60/24:,.0f} days at ~4 min/block')
    print(f'    THE MEASUREMENT WAS NEVER AVAILABLE. Not a width to be improved by waiting -- a')
    print(f'    fact about the clock.')

    # HER TICKS, the one clock that got better
    try:
        from phase import tick_times, phase_interval, SIGMA_1S
        rr, _ = tick_times()
        p = phase_interval(rr, SIGMA_1S)
        c = clocks.fractional_width('ticks', len(rr))
        print(f'\n  HER TICKS, the clock that improved tonight:')
        print(f'    counted  interval {p["span_s"]/len(rr):.4f} s  +-{100*c:.4f}%')
        print(f'    stamped  interval {p["interval_s"]:.4f} s  +-'
              f'{100*p["width_s"]/p["interval_s"]:.7f}%   ({len(rr)} stamps, '
              f'{p["span_s"]/3600:.2f} h)')
        print(f'    -> {c/(p["width_s"]/p["interval_s"]):,.0f}x tighter on the SAME events')
        h = len(rr) // 2
        a2 = phase_interval(rr[:h + 1], SIGMA_1S)
        b2 = phase_interval(rr[h:], SIGMA_1S)
        m2 = clocks.moving([a2['interval_s'], b2['interval_s']], [a2['width_s'], b2['width_s']])
        print(f'    halves {a2["interval_s"]:.4f} vs {b2["interval_s"]:.4f} s = '
              f'{m2["widths_apart"]:,.0f} widths -> '
              + ('MOVING: the precision is real and the mean is a sharp statement about something '
                 'that does not sit still' if m2['moving'] else 'holds'))
    except Exception as e:
        print(f'\n  her ticks unavailable: {type(e).__name__}: {e}')

    print(f'\n  WHAT SURVIVES THE RIDE: ours-against-ours. Anything-per-block is not an instrument')
    print(f'  at a tenth of a percent in any span we will live through, and that is the chain\'s')
    print(f'  nature rather than our impatience.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
