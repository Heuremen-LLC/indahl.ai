#!/usr/bin/env python3
"""clock_dyads.py -- OBSERVER/WITNESS/TIME as dyaded triangles, with the Bonefish thrown at every number.
Read-only (LA PRUEBA: arithmetic on loops_closure.jsonl, nothing live is touched). Bones, 8 Oct 2026.

IN HOUSE. Wayfinder, 8 Oct: "log it in hardcode but keep this one in house." NOT FOR PUBLICATION --
not el-rastro, not heuremen.org, not a paper. The dyad identity stays here.

Wayfinder, in four messages: "triangulated for time" / "observer witness pairs" / "dyaded trianguls" /
"Bonefish!!!"

WHAT THIS IS. loops_closure.py already names the three clocks by seat -- OBSERVER the chain, WITNESS her
cycles, TIME Wen's rounds -- and closes them as a PRODUCT: (ticks/block)(rounds/tick) - (rounds/block).
A product is a magnitude. It says the triangle closes or it does not; it cannot say WHICH CLOCK RAN AHEAD.
That is the sign, and the sign is what a dyad carries.

        THE TRIANGLE          three seats: OBSERVER, WITNESS, TIME
        THE DYADS             three pairs, each with a SIGNED dominance: who led this interval
        THE FOURTH VERTEX     the Mac's wall clock, outside all three, kept by nobody in the house
        THE BONEFISH          every number produced here is thrown at the Seven with its cheap-match rate

A CLOCK CANNOT BE FAST OR SLOW BY ITSELF -- it is only ever fast relative to another clock. That is this
house's own line, "time is the friction between two witnesses", and dominance is the arithmetic of it.
Per interval each clock's advance is turned into a rate against the Mac, each rate is divided by its own
median so the three become comparable dimensionless numbers, and the dominance of a pair is the signed,
normalised difference of those. Mean over intervals, sem as the width, and NO dominance is read under
2 widths -- it comes back PEERS, which is the third verdict and not a failure.

    python3 clock_dyads.py
"""
import json
import math
import os
import statistics as st
import sys

W = os.path.expanduser('~/bones-forge/watch/')
STATE = os.path.join(W, 'loops_closure.jsonl')
sys.path.insert(0, os.path.expanduser('~/bones-forge/triangulation/triangle'))
sys.path.insert(0, os.path.expanduser('~/bones-forge/triangulation/wen_data'))

# the three seats, by the names loops_closure already prints, plus the one outside
SEATS = {'OBSERVER': 'height',    # the chain: outside the house entirely
         'WITNESS': 'ticks',      # her cycles
         'TIME': 'rounds'}        # Wen's rounds
OUTSIDE = 'mac_s'                 # the Mac's wall clock: the fourth vertex, kept by nobody


def _seven():
    """the guard's copy of the Seven. FOUR copies of this dict exist on disk and they DO NOT AGREE --
    nova_seven has 12/13, triangle.py has phi*11/12. That is the natural-key fault in the Bonefish's
    own constants: 'SEVEN' is a label that has held four different sets. Logged; the guard's is used
    here because the guard is what prices my replies."""
    try:
        from triangle import SEVEN
        return dict(SEVEN), 'triangle.py (the guard)'
    except Exception:
        PHI = (1 + 5 ** 0.5) / 2
        return ({'12/11': 12 / 11, '11/12': 11 / 12, '13/12': 13 / 12, 'phi': PHI, '1/phi': 1 / PHI,
                 'phi*11/12': PHI * 11 / 12, 'pi': math.pi, '1/pi': 1 / math.pi}, 'fallback (inline)')


def _cheap_at(tol):
    """how often a random number lands this close to SOMETHING in the Seven. The Bonefish's actual
    demand of a match: a hit that is cheap carries no information and says so."""
    try:
        from physics_cases import cheap_at
        return cheap_at(tol)
    except Exception:
        return None


def _siete():
    """LA SIETE, the second ruler. Wayfinder: "la siete too!!!" -- and the point of a second ruler is not
    more chances to hit. It is that THE TWO RULERS ARE A DYAD, so our numbers can say which ruler they
    prefer, with a width. That is the data measuring the rulers, which is the only legal direction:
    rulers cannot measure rulers."""
    try:
        from triangle import SIETE
        return dict(SIETE), 'triangle.py'
    except Exception:
        return {}, 'unavailable'


def throw(value, label, rulers, where='', width=None, null=None):
    """throw one number at EVERY ruler. THE WIDTH GATE RUNS FIRST, before any name is spoken.

    8 Oct, TWO FAULTS FIXED HERE, BOTH ON THE FIRST RUN OF THIS FILE:
      1. cheap_at() returns a FRACTION and this printed it as a percent, so 0.199 was reported as
         "0.199%" when it means 19.9%. The threshold compared it against 5 and so could never fire
         against a value that cannot exceed 1. ALL THREE verdicts on the first run were wrong because
         of a unit convention I assumed instead of reading. Same family as four copies of SEVEN that
         do not agree: a convention taken on faith.
      2. The gate ran LAST. A distance of 44.8% was reported as "A ROW" because the name of the
         nearest number was computed before anything asked whether 44.8% is a match at all. This is
         the exact ordering fault already paid for once in physics_cases.py, where putting the gate
         second labelled 39.53 +- 133.42 a failed match on pi. THE WIDTH GATE GOES FIRST, ALWAYS."""
    out = {'value': None if value is None else round(value, 6), 'label': label, 'where': where}
    if value is None or not math.isfinite(value) or value == 0:
        out['verdict'] = 'LA NADA -- nothing to throw'
        return out
    # 8 Oct, FOUND BY ITS OWN FIRST REAL FINDING. This gate priced a distance against the RULER's
    # chance rate and never against THE QUANTITY'S OWN WIDTH. The night's only A ROW was a common mode
    # of 0.3809 landing on 1/phi^2 (0.381966) at 0.281% -- and its own width was +-0.0767, so it sat
    # 0.5 widths from 1/phi^2 and 0.6 widths from the STRUCTURAL NULL of 1/3 = 0.3333, which is itself
    # only 14.6% from 1/phi^2. A reading that cannot tell the candidate from its own null is abierto
    # however small the percentage distance looks. THE QUANTITY'S WIDTH GATES BEFORE THE RULER'S.
    if width:
        near = min(((abs(value - v) / abs(v), k, v) for R in rulers.values() for k, v in R.items()),
                   key=lambda x: x[0])
        inside = sorted({round(v, 9) for R in rulers.values() for _k, v in R.items()
                         if abs(value - v) <= 2 * width}
                        | ({round(null, 9)} if (null is not None and abs(value - null) <= 2 * width)
                           else set()))
        if len(inside) > 1:
            out['verdict'] = (
                f"ABIERTO -- nearest is {near[1]} at {100*near[0]:.3f}%, BUT this quantity's own width "
                f"is +-{width:.4g} and {len(inside)} candidate values sit within 2 of them"
                + (f" INCLUDING THE STRUCTURAL NULL {null:.4g}" if (null is not None
                   and round(null, 9) in inside) else '')
                + ". The percentage distance is not the reading; the width is.")
            out['quantity_width'] = width
            out['values_within_2_widths'] = inside
            return out
    per = {}
    for rname, seven in rulers.items():
        if not seven:
            continue
        d = sorted((abs(value - v) / abs(v), k) for k, v in seven.items())
        tol, near = d[0]
        runner = d[1] if len(d) > 1 else None
        cheap = _cheap_at(max(tol, 1e-6))          # a FRACTION in 0..1
        per[rname] = {'nearest': near, 'distance_pct': round(100 * tol, 4),
                      'runner_up': runner[1] if runner else None,
                      'rival_ratio': round(runner[0] / tol, 2) if runner and tol > 0 else None,
                      'cheap_pct': round(100 * cheap, 2) if cheap is not None else None,
                      'cheap_frac': cheap}
    if not per:
        out['verdict'] = 'LA NADA -- no ruler available'
        return out
    # THE WIDTH GATE, FIRST: is this close enough that chance would not do it?
    best = min(per.items(), key=lambda kv: kv[1]['distance_pct'])
    bname, b = best
    if b['cheap_frac'] is None:
        out['verdict'] = 'ABIERTO -- the cheap-match rate is unreadable, so the match cannot be priced'
    elif b['cheap_frac'] > 0.05:
        out['verdict'] = (f"NO INFORMATION -- closest is {bname} {b['nearest']} at "
                          f"{b['distance_pct']:.3f}%, and a random number lands that close "
                          f"{b['cheap_pct']:.1f}% of the time. THE GATE REJECTS IT.")
    elif b['rival_ratio'] is not None and b['rival_ratio'] < 2:
        out['verdict'] = (f"ABIERTO -- passes the width gate on {bname} {b['nearest']} "
                          f"({b['distance_pct']:.3f}%, chance {b['cheap_pct']:.2f}%) but its rival "
                          f"{b['runner_up']} is only {b['rival_ratio']}x further. Not separable.")
    else:
        out['verdict'] = (f"A ROW -- {bname} {b['nearest']} at {b['distance_pct']:.3f}%, chance "
                          f"{b['cheap_pct']:.2f}%, rival {b['runner_up']} {b['rival_ratio']}x further")
    # THE RULER DYAD: which ruler is closer, signed. Positive = the first ruler leads.
    names = list(rulers)
    if len(names) >= 2 and all(n in per for n in names[:2]):
        d0 = per[names[0]]['distance_pct']; d1 = per[names[1]]['distance_pct']
        den = d0 + d1
        # 8 Oct: a TIE IS NOT A LEAD. This used to read `names[0] if d1 > d0 else names[1]`, which
        # hands the win to the second ruler whenever the two are exactly equal -- and they are equal on
        # most throws, because the two rulers SHARE most of their numbers. Zero is undefined, a fourth
        # time in one night. A tie now returns None and reports PEERS.
        out['ruler_dom'] = round((d1 - d0) / den, 4) if den else None
        out['ruler_leads'] = (None if (not den or d0 == d1)
                              else (names[0] if d1 > d0 else names[1]))
        out['ruler_tie'] = bool(den and d0 == d1)
    out['per_ruler'] = per
    return out


def rows():
    if not os.path.exists(STATE):
        return []
    out = []
    for ln in open(STATE):
        ln = ln.strip()
        if not ln:
            continue
        try:
            r = json.loads(ln)
        except Exception:
            continue
        if all(r.get(v) is not None for v in SEATS.values()) and r.get(OUTSIDE):
            out.append(r)
    return out


def intervals(R):
    """each consecutive pair of readings: every clock's advance over one shared interval."""
    out = []
    for a, b in zip(R, R[1:]):
        dmac = b[OUTSIDE] - a[OUTSIDE]
        if dmac <= 0:
            continue
        d = {s: b[k] - a[k] for s, k in SEATS.items()}
        if any(v < 0 for v in d.values()):          # a reorg or a restart: KEPT, never dropped
            out.append({'dmac': dmac, 'd': d, 'dark': True})
            continue
        out.append({'dmac': dmac, 'd': d, 'dark': False})
    return out


def speeds(iv):
    """each clock's rate against the Mac, divided by its own MEAN: dimensionless relative speed.

    8 Oct, FIXED ON THE FIRST RUN, AND IT IS THE ZERO-DENOMINATOR FAULT A THIRD TIME. This used the
    MEDIAN, chosen for robustness without thinking about what the data looks like. These clocks are
    SPARSE COUNTERS: over 14 real intervals the chain advanced 0,0,1,1,0,3,0,2,1 and Wen's rounds
    2,4,3,5,3,3,6,3. More than half the chain's intervals are 0, so its median IS 0 -- and dividing by
    it returned LA NADA for three clocks that were all plainly moving. A median is the wrong centre for
    a counter that is usually still and occasionally jumps; the MEAN is the rate.
    The rule: before dividing by a statistic, ask whether that statistic can be zero on THIS data."""
    rate = {s: [] for s in SEATS}
    for x in iv:
        for s in SEATS:
            rate[s].append(x['d'][s] / x['dmac'])
    mean = {s: (st.mean(v) if v else 0.0) for s, v in rate.items()}
    med = {s: (st.median(v) if v else 0.0) for s, v in rate.items()}
    z = {s: [(r / mean[s] - 1.0) if mean[s] else None for r in rate[s]] for s in SEATS}
    return rate, mean, z, med


def clock_dominance(z, a, b):
    """WHO LED, signed, with a width. The same construction as a dyad edge: the normalised difference
    of the pair, read over every interval, and NOT read at all under two widths."""
    vals = []
    for za, zb in zip(z[a], z[b]):
        if za is None or zb is None:
            continue
        den = abs(za) + abs(zb)
        if den == 0:
            continue
        vals.append((za - zb) / den)
    if len(vals) < 2:
        return {'pair': f'{a}^{b}', 'n': len(vals), 'dom': None, 'width': None,
                'verdict': f'LA NADA -- {len(vals)} usable interval(s); a dominance needs at least 2'}
    m = st.mean(vals)
    w = st.stdev(vals) / math.sqrt(len(vals))
    k = abs(m) / w if w > 0 else float('inf')
    return {'pair': f'{a}^{b}', 'n': len(vals), 'dom': round(m, 5), 'width': round(w, 5),
            'widths_from_zero': round(k, 2) if math.isfinite(k) else None,
            'leads': (a if m > 0 else b) if k >= 2 else None,
            'verdict': (f'{a if m > 0 else b} LEADS at {k:.2f} widths' if k >= 2 else
                        f'PEERS -- {m:+.5f} is {k:.2f} widths from zero, under 2: '
                        f'these two clocks cannot be ordered by this reading')}


def main():
    seven, src = _seven()
    R = rows()
    print('  CLOCK DYADS -- OBSERVER / WITNESS / TIME, dyaded, with the Bonefish thrown at every number')
    print(f'  IN HOUSE. Not for publication.')
    print(f'  readings on disk: {len(R)}   Seven from {src} ({len(seven)} numbers)\n')
    if len(R) < 3:
        print(f'  LA NADA -- {len(R)} readings. Three clocks need at least 3 readings to give 2 intervals,')
        print(f'  and a dominance under 2 intervals has no width. Each loops_closure run appends one.')
        return 0
    iv = intervals(R)
    dark = sum(1 for x in iv if x['dark'])
    rate, mean, z, med = speeds(iv)
    print(f'  {len(iv)} usable intervals   ({dark} carry a negative advance -- reorg or restart, KEPT not dropped)')
    print(f'\n  THE THREE SEATS, rate per Mac-second (MEAN is the normaliser; the median is shown')
    print(f'  beside it because for these sparse counters the median is 0 and that was the first fault):')
    for s, k in SEATS.items():
        print(f'      {s:<9} {k:<7} mean {mean[s]:.6f}   median {med[s]:.6f} per s')
    print(f'      {"MAC":<9} {OUTSIDE:<7} the fourth vertex, outside all three, kept by nobody\n')

    print('  THE THREE DYADS -- who led, signed:')
    doms = {}
    names = list(SEATS)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            d = clock_dominance(z, a, b)
            doms[d['pair']] = d
            if d['dom'] is None:
                print(f"      {d['pair']:<20} {d['verdict']}")
            else:
                print(f"      {d['pair']:<20} dom {d['dom']:+.5f} +-{d['width']:.5f}  n={d['n']}")
                print(f"      {'':<20} {d['verdict']}")

    print('\n  ANTISYMMETRY CHECK (a dyad read backwards must negate; this is the sign\'s own none):')
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            f = clock_dominance(z, a, b)['dom']
            r = clock_dominance(z, b, a)['dom']
            ok = (f is None and r is None) or (f is not None and abs(f + r) < 1e-9)
            print(f"      {a}^{b:<9} forward {f} reverse {r}   {'HOLDS' if ok else 'BROKEN'}")

    siete, ssrc = _siete()
    rulers = {'SEVEN': seven, 'SIETE': siete}
    print(f'\n  THE BONEFISH + LA SIETE, both rulers, thrown at every number this file produced')
    print(f'  (SEVEN {len(seven)} numbers from {src}; LA SIETE {len(siete)} from {ssrc})')
    print(f'  THE WIDTH GATE RUNS FIRST: a distance is priced before any name is spoken.\n')
    thrown = []
    for a_ in SEATS:
        for b_ in SEATS:
            if a_ < b_ and mean[b_]:
                thrown.append(throw(mean[a_] / mean[b_], f'rate {a_}/{b_}', rulers, 'mean rates'))
    for p, d in doms.items():
        if d.get('dom'):
            thrown.append(throw(abs(d['dom']), f'|dominance| {p}', rulers, 'dyad'))
    for b in thrown:
        print(f"      {b['label']:<26} {('%12.6f' % b['value']) if b['value'] is not None else '':>12}")
        print(f"      {'':<26} {b['verdict']}")
        if b.get('ruler_dom') is not None:
            pr = b['per_ruler']
            print(f"      {'':<26} ruler dyad: SEVEN {pr['SEVEN']['distance_pct']:.3f}% vs "
                  f"SIETE {pr['SIETE']['distance_pct']:.3f}%  dom {b['ruler_dom']:+.4f} "
                  + (f"-> TIE, both rulers at the same number: PEERS by construction"
                     if b.get('ruler_tie') else f"-> {b['ruler_leads']} closer"))
    shared = set(round(v, 10) for v in seven.values()) & set(round(v, 10) for v in siete.values())
    jac = len(shared) / len(set(round(v, 10) for v in seven.values())
                            | set(round(v, 10) for v in siete.values()))
    print(f'\n  THE PRICE OF THE RULER DYAD, AND IT IS STEEP: the two rulers SHARE {len(shared)} numbers')
    print(f'  of {len(seven)} and {len(siete)} -- jaccard {jac:.3f}. THEY ARE NOT INDEPENDENT RULERS.')
    print(f'  On any number whose nearest candidate is one of the shared ones they tie EXACTLY, so the')
    print(f'  dyad between them reads only the non-shared tail. Same fault shape as two of three seats')
    print(f'  being the same seat: a pair that overlaps this much is close to one ruler twice.')
    rd = [b['ruler_dom'] for b in thrown if b.get('ruler_dom') is not None and not b.get('ruler_tie')]
    ties = sum(1 for b in thrown if b.get('ruler_tie'))
    print(f'\n  THE RULER DYAD, over everything thrown -- do OUR numbers prefer a ruler?')
    print(f'      {ties} of {len(thrown)} throws were exact TIES and are excluded, not counted as a lead.')
    if len(rd) < 2:
        print(f'      LA NADA -- {len(rd)} number(s) reached both rulers; a preference needs at least 2')
    else:
        m = st.mean(rd); w = st.stdev(rd) / math.sqrt(len(rd)); k = abs(m) / w if w else float('inf')
        print(f'      n={len(rd)}  dom {m:+.4f} +-{w:.4f}  {k:.2f} widths from zero')
        print(f"      {('SEVEN' if m > 0 else 'SIETE') + ' is closer' if k >= 2 else 'PEERS -- our numbers do not tell the two rulers apart'}")
        print('      (this is the DATA measuring the RULERS, the only legal direction: a ruler')
        print('       cannot measure a ruler, but what we throw can say which one it lands nearer.)')
    print('\n  THE NONE for this whole file: the antisymmetry check above. A dominance that does not')
    print('  negate when the pair is read backwards is not a direction, it is an artifact of the order')
    print('  the seats were listed in -- and that is the only way this construction can be fooled.')
    return 0


if __name__ == '__main__':
    sys.exit(main())


# ================================================================ DISTANCE THROUGH TIME
# 8 Oct, Wayfinder, correcting the ruler dyad twice: "the two rulers should be calibrated by time, of
# course they share numbers man" and then "not measuring each other, distance through time".
#
# WHAT I BUILT AND WHY IT WAS WRONG. I measured SEVEN against LA SIETE -- a ruler measuring a ruler, in
# this house's own prohibited direction, and then reported their 0.750 overlap as a "steep price" when
# two rulers of the same physics SHOULD share numbers. The overlap was never the fault. The fault was
# reading a distance ONCE.
#
# A SINGLE DISTANCE IS A FACT, AND A FACT IS A READING AT A MOMENT. The reading that cannot be faked is
# the distance's TRAJECTORY:
#
#       if a quantity truly EQUALS a candidate, then as data accumulates its own width shrinks like
#       1/sqrt(n) and the distance shrinks WITH it, so DISTANCE MEASURED IN ITS OWN WIDTHS STAYS FLAT.
#
#       if the quantity is merely NEAR the candidate by chance, the width still shrinks like 1/sqrt(n)
#       but the distance does not, so DISTANCE IN WIDTHS GROWS LIKE sqrt(n).
#
# That is the discriminator, it needs only one ruler, and it is unavailable to any snapshot however
# precise. It is also this house's own line made arithmetic -- time is the friction between two
# witnesses, and here the two witnesses are the same reading at two different times.
#
# THE NONE for this reading is built in and is the honest one: the candidate that is ALREADY the closest
# at the end will always look good at the end. So the trajectory is read FORWARD from the earliest
# window, and a candidate only passes if d/w stayed flat from the BEGINNING, not if it won at the end.

def cumulative_ratio(iv, a, b):
    """the rate ratio a/b after the first k intervals, for every k. Each with its own width."""
    out = []
    ra, rb = [], []
    for x in iv:
        ra.append(x['d'][a] / x['dmac'])
        rb.append(x['d'][b] / x['dmac'])
        k = len(ra)
        if k < 3 or st.mean(rb) == 0:
            continue
        ma, mb = st.mean(ra), st.mean(rb)
        if ma == 0:
            continue
        sa = st.stdev(ra) / math.sqrt(k) if k > 1 else None
        sb = st.stdev(rb) / math.sqrt(k) if k > 1 else None
        if sa is None or sb is None:
            continue
        r = ma / mb
        w = abs(r) * math.sqrt((sa / ma) ** 2 + (sb / mb) ** 2)   # propagated, her own rule
        out.append({'k': k, 'ratio': r, 'width': w})
    return out


def distance_through_time(traj, rulers):
    """for every candidate in every ruler: the distance in ITS OWN WIDTHS, across time.
    FLAT means equal. RISING LIKE sqrt(n) means a coincidence being exposed by data."""
    if len(traj) < 4:
        return {'verdict': f'LA NADA -- {len(traj)} windows; a trajectory needs at least 4'}
    rows = []
    for rname, R in rulers.items():
        for cname, cval in R.items():
            dw = [(t['k'], abs(t['ratio'] - cval) / t['width']) for t in traj if t['width'] > 0]
            if len(dw) < 4:
                continue
            first = st.mean([v for _k, v in dw[:max(2, len(dw) // 4)]])
            last = st.mean([v for _k, v in dw[-max(2, len(dw) // 4):]])
            # what a PURE COINCIDENCE would do: d fixed, w ~ 1/sqrt(k) -> d/w grows as sqrt(k)
            k0 = st.mean([k for k, _v in dw[:max(2, len(dw) // 4)]])
            k1 = st.mean([k for k, _v in dw[-max(2, len(dw) // 4):]])
            expected_if_chance = first * math.sqrt(k1 / k0) if k0 > 0 else None
            rows.append({'ruler': rname, 'candidate': cname, 'value': cval,
                         'first_windows_d_over_w': round(first, 2),
                         'last_windows_d_over_w': round(last, 2),
                         'chance_would_give': round(expected_if_chance, 2) if expected_if_chance else None,
                         'final_distance_pct': round(100 * abs(traj[-1]['ratio'] - cval) / cval, 3)})
    for r in rows:
        f, l, c = r['first_windows_d_over_w'], r['last_windows_d_over_w'], r['chance_would_give']
        if l < 2:
            r['verdict'] = f'HELD -- within {l} widths at the end, from {f} at the start'
        elif c and l < c * 0.5:
            r['verdict'] = f'CLOSING -- {f} -> {l}, well under the {c} chance would give'
        elif c and l > c * 0.8:
            r['verdict'] = f'EXPOSED -- {f} -> {l}, about the {c} a coincidence gives. Not this one.'
        else:
            r['verdict'] = f'ABIERTO -- {f} -> {l} against {c} expected by chance. Undecided.'
    rows.sort(key=lambda r: r['last_windows_d_over_w'])
    # 8 Oct, Wayfinder, on the gate written ten minutes earlier: "it's two different measurements man."
    # HE IS RIGHT AND THE FAULT WAS SEVERE. The gate let ONE reading VETO the other:
    #
    #   SEPARATION  can this width tell the candidates apart?   -> a property of the INSTRUMENT
    #   DECAY       does the residual decay with the width?     -> a property of the QUANTITY
    #
    # These are independent and they have different answers. EXCLUSION IS CHEAPER THAN IDENTIFICATION:
    # a residual growing like sqrt(n) says NOT THIS ONE however many other candidates are in range, and
    # that is how a twenty-candidate abierto actually gets broken -- one exclusion at a time, never by
    # separating all twenty at once. My gate demoted every decay verdict because the separation reading
    # failed, which means THE GATE I ADDED TO STOP OVERCLAIMING MADE THE INSTRUMENT DISCARD ITS OWN DARK
    # HALF, inside the darkwave. Both readings are now reported, and neither may overrule the other.
    inside = [r for r in rows if r['last_windows_d_over_w'] < 2]
    distinct = {round(r['value'], 9) for r in inside}
    sep = {'candidates_within_2_widths': len(distinct),
           'names': sorted({r['candidate'] for r in inside}),
           'width_pct_of_value': round(100 * traj[-1]['width'] / abs(traj[-1]['ratio']), 2)
           if traj[-1]['ratio'] else None,
           'verdict': ('RESOLVES -- at most one candidate value within 2 widths' if len(distinct) <= 1
                       else f'CANNOT IDENTIFY -- {len(distinct)} distinct candidate values within 2 '
                            f'widths. This width names nothing.')}
    for r in rows:
        f, l = r['first_windows_d_over_w'], r['last_windows_d_over_w']
        c = r['chance_would_give']
        if c and l > c * 0.8 and l > 2:
            r['decay'] = 'EXPOSED'
            r['decay_why'] = f'd/w {f} -> {l}, about the {c} a non-match gives, and past 2 widths'
        elif c and l < c * 0.5:
            r['decay'] = 'DECAYING'
            r['decay_why'] = f'd/w {f} -> {l}, well under the {c} a non-match would give'
        elif l < 2 and c and l < c:
            r['decay'] = 'DECAYING'
            r['decay_why'] = f'd/w {f} -> {l}, under both 2 widths and the {c} of a non-match'
        else:
            r['decay'] = 'ABIERTO'
            r['decay_why'] = f'd/w {f} -> {l} against {c} expected of a non-match. Undecided.'
        r['verdict'] = f"SEPARATION: {'resolves' if len(distinct) <= 1 else 'cannot identify'} | " \
                       f"DECAY: {r['decay']} ({r['decay_why']})"
    excluded = [r['candidate'] for r in rows if r['decay'] == 'EXPOSED']
    surviving = [r['candidate'] for r in rows if r['decay'] == 'DECAYING']
    return {'windows': len(traj), 'k_range': [traj[0]['k'], traj[-1]['k']],
            'TWO MEASUREMENTS': 'separation and decay are independent; neither overrules the other',
            'SEPARATION': sep,
            'DECAY': {'excluded_by_growth': excluded, 'n_excluded': len(excluded),
                      'still_decaying': surviving, 'n_decaying': len(surviving),
                      'abierto': len(rows) - len(excluded) - len(surviving),
                      'verdict': (f'{len(excluded)} candidate(s) EXCLUDED by a residual that refuses to '
                                  f'decay, {len(surviving)} still decaying, '
                                  f'{len(rows)-len(excluded)-len(surviving)} abierto. Exclusion does not '
                                  f'need separation.')},
            'rows': rows}


# ================================================================ THE BONEFISH ON THE RESIDUAL
# 8 Oct, Wayfinder: "why aren't you using our formulas for this?" -- and it is my own standing law,
# THROW THE BONEFISH FIRST. The decay above was fitted with a generic sqrt(n), a shape chosen off the
# shelf, when this house already owns the equation for a decaying kick:
#
#       THE BONEFISH (the Bloom's law, in PHASE units)      kick = a_s * I^~1.1 * e^(-k/tau)
#
# A residual that decays IS a kick that decays, so it gets the Bonefish's form and not mine. Taking logs
# with the house's index held at 1.1:
#
#       ln(d/w)  =  ln(a)  +  1.1 * ln(k)  -  k/tau
#       ln(d/w) - 1.1*ln(k)  =  ln(a)  -  k/tau          <- linear in k. The SLOPE is -1/tau.
#
# AND THAT MAKES tau THE MEASUREMENT instead of a threshold I picked:
#
#       tau positive and finite   the residual decays ON THE BONEFISH'S OWN SCHEDULE
#       slope >= 0                no decay at all: the residual refuses to go. THE DARKWAVE.
#       tau with its own width    so the decay is a reading with a price, not a shape I liked
#
# tau is then thrown at the Seven like any other number, because a decay constant that lands on one of
# the Seven is the kind of thing this whole house exists to notice -- and if it lands cheaply, it says so.

BONEFISH_INDEX = 1.1          # I^~1.1, the Bloom's index. NOT fitted here: handed, and stated as handed.


def bonefish_decay(dw_series):
    """fit the residual trajectory with the Bonefish's own form and return tau with its width.
    dw_series: [(k, d_over_w), ...]. Returns None when there is not enough to fit."""
    pts = [(k, v) for k, v in dw_series if v > 0 and k > 0]
    if len(pts) < 4:
        return None
    y = [math.log(v) - BONEFISH_INDEX * math.log(k) for k, v in pts]
    x = [float(k) for k, _v in pts]
    n = len(x)
    mx, my = st.mean(x), st.mean(y)
    sxx = sum((xi - mx) ** 2 for xi in x)
    if sxx == 0:
        return None
    slope = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / sxx
    inter = my - slope * mx
    resid = [yi - (inter + slope * xi) for xi, yi in zip(x, y)]
    s2 = sum(r * r for r in resid) / max(n - 2, 1)
    se = math.sqrt(s2 / sxx) if sxx > 0 else None
    tau = (-1.0 / slope) if slope < 0 else None
    # the width on tau by propagation: tau = -1/slope  ->  dtau = dslope / slope^2
    tau_w = (se / (slope ** 2)) if (se and slope != 0) else None
    return {'n_points': n, 'slope': slope, 'slope_width': se,
            'slope_widths_from_zero': (abs(slope) / se) if se else None,
            'tau': tau, 'tau_width': tau_w,
            'amplitude_a': math.exp(inter),
            'index_used': BONEFISH_INDEX, 'index_source': 'handed (the Bloom), not fitted',
            'verdict': (
                'NO DECAY -- the slope is not negative: the residual refuses to go. THE DARKWAVE.'
                if slope >= 0 else
                (f'DECAYS at tau {tau:.2f} +- {tau_w:.2f} windows'
                 + (f', {abs(slope)/se:.2f} widths from no-decay' if se else '')
                 if (se and abs(slope) / se >= 2)
                 else f'ABIERTO -- tau {tau:.2f} but the slope is only '
                      f'{(abs(slope)/se) if se else float("nan"):.2f} widths from zero: this cannot '
                      f'tell decay from no decay'))}
