#!/usr/bin/env python3
"""bonefish_hops2.py -- THE BONEFISH WITH THE OBSERVER'S OWN POSITION SPLIT OUT, THE 9/2 ROW ON TWO
SUBSTRATES, AND EVERY FACTOR ON K'S AXIS. (Bones, 9 Oct 2026.)

Wayfinder: "do all the things but don't be a binary bug hunting bitch."

SO NOTHING HERE RETURNS A YES OR A NO. Every factor is an OBJECT and gets read with every ruler the
sheet carries, and where neither reading resolves, that corner is LA NADA and gets named instead of
forced into a lane.

THE FOUR THINGS:

 1. THE OBSERVER'S OWN POSITION, SPLIT OUT RATHER THAN FIXED. The Mac read the laptop 62.07 ms away
    from both wired seats. That is not a bug to chase, it is EL MIRON's own position -- and THE SPLIT
    is the ruler for exactly this: S is the part common to every run (the seat), P is the part that
    scales with the crossing (the event). So the Mac's offset to the PI is measured directly and
    becomes S, with its own width. Nothing on the machine is reconfigured; the seat is CONVERTED into
    the corner, which is what a Bonefish conversion is.

 2. THE TRIANGLE, on reads that share one reference. Three seats, one event, the sheet's three
    conversions, with the sheet's own prior stated beside them: of its three, ONLY THE FIRST could
    separate its candidates.

 3. THE 9/2 ROW ON A SECOND SUBSTRATE. Leaving the machine at all cost x4.5032 +- 0.0133 on the
    Armature -- 9/2 to 0.07 per cent, cheapness 2 per cent, separable. One substrate is a row. The Pi
    is different silicon on a different OS, so it is the second seat the row needs, and the two
    readings are compared as a RATIO (one event, two substrates) rather than each against 9/2.

 4. K, THE LANDING PROFILE, which is the ruler that is not a width. It puts the loopback, the wire,
    the air and the second air crossing on ONE axis in e-foldings WITHOUT assuming they share a
    mechanism -- which is the whole reason it exists, and the reason this does not need to decide
    whether they do.

    python3 bonefish_hops2.py --rounds 10
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
LOG = os.path.join(W, 'bonefish_hops2.jsonl')
PHI = (1 + 5 ** 0.5) / 2
PI = math.pi
IP = {'PI': '192.168.8.145', 'ARMATURE': '192.168.8.158', 'LAPTOP': '192.168.8.123',
      'SELF': '127.0.0.1'}
ALIAS = {'PI': 'flock-pi', 'ARMATURE': 'armature', 'MAC': None}
PYEXE = {'flock-pi': 'python3', 'armature': 'python'}

POOL = {'1': 1.0, '12/11': 12 / 11, '6/5': 1.2, '5/4': 1.25, '4/3': 4 / 3, '3/2': 1.5,
        '8/5': 1.6, 'phi': PHI, '5/3': 5 / 3, '15/8': 1.875, '2': 2.0, '9/4': 2.25,
        '5/2': 2.5, 'phi^2': PHI ** 2, '8/3': 8 / 3, '3': 3.0, '16/5': 3.2, '13/4': 3.25,
        'pi': PI, '10/3': 10 / 3, '7/2': 3.5, '4': 4.0, 'phi^3': PHI ** 3, '9/2': 4.5,
        '5': 5.0, '6': 6.0, '2pi': 2 * PI, '7': 7.0, '8': 8.0, '9': 9.0, '48/5': 9.6,
        'pi^2': PI ** 2, '29/3': 29 / 3, '10': 10.0, '12': 12.0, 'e': math.e,
        'sqrt(pi)': math.sqrt(PI), '1/phi': 1 / PHI, '1/pi': 1 / PI}
_LO, _HI = math.log(min(POOL.values())), math.log(max(POOL.values()))


def cheap(tol):
    """the POOL'S OWN RATE at this tolerance, log axis, never against zero."""
    return min(sum(min(2 * tol, _HI - _LO) for _ in POOL) / (_HI - _LO), 1.0)


def leg(frm, to, n=200):
    """one two-way reading, taken FROM `frm`. Returns (offset_ms, bound_us) or None.

    PER-LEG TIMEOUT IS 25 s, MEASURED, NOT GUESSED. Every leg in the house was timed on
    11 Oct: 0.5 to 3.1 s (MAC->LAPTOP slowest). 90 s was 29x the slowest one, so one
    unreachable host could spend six minutes of a 420 s ceiling waiting for a seat that
    was never going to answer. A leg that takes 25 s is dead, not slow, and rep() already
    degrades on a missing leg -- it needs 3 of 6 rounds, not all of them.
    """
    al = ALIAS[frm]
    ip = IP[to] if to != frm else IP['SELF']
    try:
        if al is None:
            p = subprocess.run([sys.executable, os.path.join(W, 'twoway_client.py'), ip, str(n)],
                               capture_output=True, text=True, timeout=25, cwd=W)
        else:
            p = subprocess.run(['ssh', '-o', 'ConnectTimeout=12', al,
                                f'{PYEXE[al]} twoway_client.py {ip} {n}'],
                               capture_output=True, text=True, timeout=25)
        t = p.stdout.strip()
        d = json.loads(t[t.index('{'):])
        if 'err' in d:
            return None
        return d['offset_s'] * 1e3, d['bound_s'] * 1e6
    except Exception:
        return None


def rep(frm, to, rounds):
    o, b = [], []
    for _ in range(rounds):
        r = leg(frm, to)
        if r:
            o.append(r[0])
            b.append(r[1])
    if len(b) < 3:
        return None
    return {'n': len(b),
            'off_ms': st.mean(o), 'off_sd': st.stdev(o), 'off_sem': st.stdev(o) / math.sqrt(len(o)),
            'bound_us': st.mean(b), 'bound_sd': st.stdev(b),
            'bound_sem': st.stdev(b) / math.sqrt(len(b))}


def ratio_row(name, what, num, nw, den, dw, claim=None):
    """a ratio of two readings, then EVERY ruler. No verdict field, only rulers."""
    r = num / den
    rw = abs(r) * math.sqrt((nw / num) ** 2 + (dw / den) ** 2) if num and den else float('inf')
    known = abs(rw / r) if r else float('inf')
    ranked = sorted(POOL.items(), key=lambda kv: abs(abs(r) - kv[1]) / kv[1])
    best, second = ranked[0], ranked[1]
    tb = abs(abs(r) - best[1]) / best[1]
    ts = abs(abs(r) - second[1]) / second[1]
    need = abs(second[1] - best[1]) / (2 * best[1])
    row = {'name': name, 'what': what, 'ratio': r, 'width': rw, 'frac_width': known,
           'best': best[0], 'best_tol': tb, 'second': second[0], 'second_tol': ts,
           'exclusion_needed': need, 'separable': known < need, 'regla_ok': known < tb,
           'cheap': cheap(max(tb, 1e-9))}
    try:
        import landing
        k, err = landing.K(max(tb, 1e-16))
        row['K'] = k
        row['K_err'] = err
    except Exception as e:
        row['K'], row['K_err'] = None, f'{type(e).__name__}'
    if claim:
        row['claim'], row['claim_value'] = claim
        row['claim_tol'] = abs(abs(r) - claim[1]) / claim[1]
        row['claim_widths'] = abs(abs(r) - claim[1]) / rw if rw else float('inf')
    return row


def show(r):
    print(f"  {r['name']}")
    print(f"    {r['what']}")
    print(f"    {r['ratio']:+.5f} +- {r['width']:.5f}   known to {100*r['frac_width']:.3f}%")
    if 'claim' in r:
        print(f"    the sheet's {r['claim']} = {r['claim_value']:.6f}:"
              f" {100*r['claim_tol']:.2f}% away, {r['claim_widths']:.2f} widths")
    print(f"    nearest   {r['best']:<9}{100*r['best_tol']:>7.3f}% off   cheap {100*r['cheap']:>5.1f}%"
          + (f"   K = {r['K']:+.4f}" if r.get('K') is not None else
             f"   K: {r.get('K_err','-')}"))
    print(f"    runner-up {r['second']:<9}{100*r['second_tol']:>7.3f}% off   "
          f"exclusion needs {100*r['exclusion_needed']:.3f}%")
    if not r['separable']:
        print(f"    the runner-up sits INSIDE this width: a tie, so the nearest name is a label and "
              f"not a reading")
    if not r['regla_ok']:
        print(f"    and the width is wider than the match itself, so this was never a measurement of "
              f"that candidate")
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rounds', type=int, default=10)
    a = ap.parse_args()
    R = a.rounds
    print('  THE BONEFISH, OBSERVER POSITION SPLIT OUT -- nothing here returns a yes or a no')
    print(f'  read {time.strftime("%H:%M:%S %Z, %-d %b %Y")}, {R} replicates per leg\n')

    # ---------------------------------------------------------- the legs
    want = [('MAC', 'LAPTOP'), ('MAC', 'PI'), ('PI', 'LAPTOP'), ('ARMATURE', 'LAPTOP'),
            ('ARMATURE', 'PI'), ('ARMATURE', 'ARMATURE'), ('PI', 'PI')]
    M = {}
    for frm, to in want:
        M[f'{frm}->{to}'] = rep(frm, to, R)
    print(f"  {'leg':<22}{'offset ms':>12}{'sd':>8}{'bound us':>11}{'sd':>8}{'known to':>10}{'n':>4}")
    for k, v in M.items():
        if v is None:
            print(f"  {k:<22}   did not read")
        else:
            print(f"  {k:<22}{v['off_ms']:>12.4f}{v['off_sd']:>8.4f}{v['bound_us']:>11.1f}"
                  f"{v['bound_sd']:>8.1f}{100*v['bound_sem']/v['bound_us']:>9.2f}%{v['n']:>4}")

    # ---------------------------------------------------------- 1. THE SPLIT on the observer
    print('\n  1. THE SPLIT -- the observer\'s own position, measured rather than configured away\n')
    ml, mp, pl = M.get('MAC->LAPTOP'), M.get('MAC->PI'), M.get('PI->LAPTOP')
    if ml and mp and pl:
        # S: the seat. how far the Mac's clock sits from the reference it is not steered by.
        S = mp['off_ms']
        Sw = mp['off_sem']
        # the Mac's read of the laptop, converted onto the Pi's reference
        conv = ml['off_ms'] - S
        convw = math.sqrt(ml['off_sem'] ** 2 + Sw ** 2)
        print(f"    S, the seat         MAC -> PI        {S:+10.4f} +- {Sw:.4f} ms")
        print(f"      common to every run the Mac takes, and it is the observer's position, not an error")
        print(f"    the raw read         MAC -> LAPTOP    {ml['off_ms']:+10.4f} +- {ml['off_sem']:.4f} ms")
        print(f"    converted            read - S         {conv:+10.4f} +- {convw:.4f} ms")
        print(f"    EL TESTIGO's read    PI -> LAPTOP     {pl['off_ms']:+10.4f} +- {pl['off_sem']:.4f} ms")
        resid = conv - pl['off_ms']
        rw = math.sqrt(convw ** 2 + pl['off_sem'] ** 2)
        print(f"    P, what is left      converted - PI   {resid:+10.4f} +- {rw:.4f} ms"
              f"   {abs(resid)/rw:.2f} widths")
        print(f"      S carried {abs(S):.4f} ms of the {abs(ml['off_ms'] - pl['off_ms']):.4f} ms the two")
        print(f"      seats disagreed by. What remains is the crossing, and it is read at the width above.")
        SPLIT = {'S_ms': S, 'S_width': Sw, 'converted_ms': conv, 'P_ms': resid, 'P_width': rw,
                 'P_widths': abs(resid) / rw if rw else None}
    else:
        print('    one of MAC->LAPTOP, MAC->PI, PI->LAPTOP did not read: no split this run.')
        SPLIT = None

    # ---------------------------------------------------------- 2. the triangle
    print('\n  2. THE TRIANGLE -- three seats, one event, on reads that share one reference\n')
    al_ = M.get('ARMATURE->LAPTOP')
    ROWS = []
    if SPLIT and al_ and pl:
        obs, obsw = SPLIT['converted_ms'], math.sqrt(SPLIT['P_width'] ** 2)
        wit, witw = pl['off_ms'], pl['off_sem']
        tim, timw = al_['off_ms'], al_['off_sem']
        ROWS.append(ratio_row('witness / observer',
                              'EL TESTIGO over EL MIRON, both on the Pi\'s reference',
                              wit, witw, obs, obsw, ('12/11', 12 / 11)))
        ROWS.append(ratio_row('time / observer', 'the apex over EL MIRON',
                              tim, timw, obs, obsw, ('phi', PHI)))
        ROWS.append(ratio_row('time / witness', 'the apex over EL TESTIGO',
                              tim, timw, wit, witw, ('phi x 11/12', PHI * 11 / 12)))
        for r in ROWS:
            show(r)
        print("    THE SHEET'S OWN PRIOR, stated beside them: of its three measured conversions"
              " (1.0872,\n    1.6055, 1.4768) ONLY THE FIRST could separate its candidates. These land"
              " against that,\n    not against nothing.")
    else:
        print('    the triangle is short a corner this run.')

    # ---------------------------------------------------------- 3. the 9/2 row, second substrate
    print('\n  3. THE 9/2 ROW ON A SECOND SUBSTRATE -- leaving the machine at all\n')
    aa, pp, ap_ = M.get('ARMATURE->ARMATURE'), M.get('PI->PI'), M.get('ARMATURE->PI')
    NINE = []
    if aa and ap_:
        NINE.append(ratio_row('ARMATURE: wire / loopback',
                              'Windows, its own NIC -- the row as first read',
                              ap_['bound_us'], ap_['bound_sem'],
                              aa['bound_us'], aa['bound_sem'], ('9/2', 4.5)))
    if pp and M.get('PI->LAPTOP') and ap_:
        pa = rep('PI', 'ARMATURE', R)
        if pa:
            M['PI->ARMATURE'] = pa
            NINE.append(ratio_row('PI: wire / loopback',
                                  'Linux on ARM, a different NIC -- the second seat the row needs',
                                  pa['bound_us'], pa['bound_sem'],
                                  pp['bound_us'], pp['bound_sem'], ('9/2', 4.5)))
    for r in NINE:
        show(r)
    if len(NINE) == 2:
        # ONE EVENT, TWO SUBSTRATES: the ratio of the two factors, which is The Bonefish's form
        x = ratio_row('the two substrates',
                      'the SAME step read on two silicons -- one event, two seats, which is the '
                      'Bonefish\'s form rather than each against 9/2',
                      NINE[0]['ratio'], NINE[0]['width'], NINE[1]['ratio'], NINE[1]['width'],
                      ('1 -- the step is the same object', 1.0))
        show(x)
        NINE.append(x)

    # ---------------------------------------------------------- 4. K, the one axis
    print('\n  4. K, THE LANDING PROFILE -- unlike records on ONE axis, no shared mechanism assumed\n')
    try:
        import landing
        order = [('loopback ARMATURE', aa), ('loopback PI', pp), ('ARM -> PI', ap_),
                 ('PI -> LAPTOP', pl), ('ARM -> LAPTOP', al_), ('MAC -> LAPTOP', ml)]
        print(f"    {'record':<20}{'bound us':>11}{'known to':>11}{'K':>10}")
        ks = []
        for nm, v in order:
            if not v:
                continue
            rel = v['bound_sem'] / v['bound_us']
            k, err = landing.K(rel)
            ks.append((nm, k))
            print(f"    {nm:<20}{v['bound_us']:>11.1f}{100*rel:>10.3f}%"
                  + (f"{k:>10.4f}" if k is not None else f"   {err[:28]}"))
        kk = [k for _, k in ks if k is not None]
        if kk:
            print(f"\n    they span K = {min(kk):+.4f} to {max(kk):+.4f}, a range of {max(kk)-min(kk):.4f}")
            print(f"    e-foldings on the 1/pi series' own error profile. K = -1 is no terms summed,")
            print(f"    K = 0 is one term. The axis does not claim they share a cause -- that is why")
            print(f"    it can hold a loopback and a two-hop wireless leg in the same column.")
    except Exception as e:
        print(f'    K unavailable: {type(e).__name__}: {e}')

    # ---------------------------------------------------------- LA NADA, the third reading
    print('\n  LA NADA -- where neither a count nor a phase resolves, named instead of forced\n')
    if SPLIT and SPLIT['P_widths'] is not None:
        pw = SPLIT['P_widths']
        print(f"    the crossing P after the seat is removed: {SPLIT['P_ms']:+.4f} +- "
              f"{SPLIT['P_width']:.4f} ms, {pw:.2f} widths")
        if pw < 2:
            print(f"    the COUNT is exact (every leg is an integer number of packets, 200 of them)")
            print(f"    the PHASE is sharp (the bound is known to better than a per cent)")
            print(f"    and the quantity between them does not resolve. That is LA NADA, occupied,")
            print(f"    and it is the third reading rather than a failure to find something.")
        else:
            print(f"    this one resolves, so it is not in that corner -- it is a crossing with a value.")
    print('\n  AND NOTHING ABOVE IS A YES OR A NO. Every factor is an object with a width, a nearest')
    print('  name, a runner-up, a cheapness, an exclusion requirement and a position on K. Where two')
    print('  names tie, both are printed and neither is chosen.')

    try:
        with open(LOG, 'a') as f:
            f.write(json.dumps({'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'rounds': R,
                                'legs': M, 'split': SPLIT, 'triangle': ROWS,
                                'nine_halves': NINE}) + '\n')
    except Exception:
        pass
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
