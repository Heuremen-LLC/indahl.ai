#!/usr/bin/env python3
"""dos_asientos.py -- THE SAME JOB IN BOTH SEATS, AND THE SPLIT BETWEEN THEM. (Bones, 12 Oct 2026.)

THE FAULT THIS EXISTS FOR WAS LIVE FOR 5.5 HOURS AND NOTHING SAW IT. The tick bus runs
Python 3.9.6 and this shell runs 3.14.7, and `datetime.fromisoformat` before 3.11 rejects an
offset written `-0400`. vigencia.py therefore reported `dead 1 / no_record 16` on the bus and
`dead 5 / no_record 9` in my hand, eight runs apart, and NEITHER SEAT KNEW THE OTHER EXISTED.
See [[project-two-pythons-one-house]]. The guard that would have caught it is not a version
check -- it is running the instrument in the seat it actually runs in and comparing.

THREE RUNS PER JOB, NOT TWO, because a difference between two runs is not a difference between
two seats. THE SPLIT:

    S   what any repeat gives     -- the apparatus: drift, a GPS fix moving, her cycle advancing
    P   what the SEAT gives       -- the only part that is about the interpreter

and a field is seat-dependent only where P shows it and S does not.

AND THE ORDER OF THE THREE RUNS IS THE WHOLE MEASUREMENT, which this file got wrong first.
Running shell, shell, BUS puts S between two adjacent runs and P across a longer gap, so any
drifting quantity lands in P. It reported reloj_casa's GPS as SEAT-DEPENDENT at `sats_used`
9 vs 8 and `hdop` 0.56 vs 0.57 -- the fix had genuinely changed between runs. Interleaved
shell, BUS, shell, S and P span the same stretch of wall time and reloj_casa came back AGREE
with S = P = 3. That is differencing across unequal intervals, and the fix was the order.

THE NULL IS MEASURED, NOT TYPED. Across 7 jobs that produced comparable rows, the two seats
differed on 9 numeric fields out of several hundred, every one of them in the last bit or two
of a float64:

    max relative difference   1.133e-15     ( 5.1 ULP )
    median                    1.395e-16     ( under 1 ULP )
    float64 epsilon           2.220e-16
    coarsest figure reported anywhere in this house   ~1e-4

so the margin is ELEVEN ORDERS OF MAGNITUDE. That is summation order differing between two
builds of CPython, it is not a statement about any reading, and it is priced here rather than
raised. The bar below is 1e-9: six decades above the noise and five below anything we report, so
it cannot fire on float dust and cannot miss a real divergence.

THIS IS A TOOL, NOT A TICK JOB. One pass runs every job three times; measured at 97 s wall for
nine jobs, which is a third of a tick spent to re-confirm a null, every tick, forever -- the
bulletin he retired. Run it after changing a bus job, or when two seats disagree about anything.

    python3 dos_asientos.py              # the table
    python3 dos_asientos.py --selftest   # planted seat-dependence, both directions
"""
# ---------------------------------------------------------------------------------------------
# THIS FILE IS NOT A CONSUMER, AND SAYING SO IS NOT OPTIONAL.
#
# The JOBS table below names nine ledgers as string literals, so vigencia.py's dependency scan
# counted this file as a READER of all nine the moment it existed -- live 9 -> 16 and
# unread 27 -> 20. Every one of those moves was an artifact going from "NOBODY READS THIS, so
# its silence costs nothing" to "something stands on this". NOTHING STARTED STANDING ON THEM.
# A tool that opens a ledger to COMPARE TWO RUNS OF IT makes no claim about the world from its
# contents, and load is supposed to count the statements that would be wrong if the ledger went
# stale. THE INSTRUMENT CHANGED THE READING IT WAS BUILT TO CHECK, which is our own hat in the
# data, and the fix is to declare it rather than let a heuristic guess at it.
VIGENCIA_NOT_A_CONSUMER = True
# ---------------------------------------------------------------------------------------------
import argparse
import json
import os
import subprocess
import sys
import time

W = os.path.dirname(os.path.abspath(__file__))
SHELL = sys.executable


def bus_seat():
    """THE BUS'S OWN DECLARATION OF ITS INTERPRETER, not a path typed in this file.

    tick_bus.py writes `executable` and `python` into tickbus.json every tick (added 12 Oct,
    because nothing in the house recorded which Python it was). Reading it here means this tool
    cannot drift away from the seat it is supposed to be testing -- if launchd ever hands the
    bus a different interpreter, this follows it without an edit. The fallback is the path
    measured off `ps` on the running process today, and it is LABELLED as a fallback so a
    silent substitution can never pass for a reading.
    """
    try:
        d = json.load(open(os.path.join(W, 'tickbus.json')))
        e = d.get('executable')
        if e and os.path.exists(e):
            return e, 'declared by the bus in tickbus.json'
    except Exception:
        pass
    f = ('/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/'
         'Versions/3.9/Resources/Python.app/Contents/MacOS/Python')
    return f, 'FALLBACK -- the bus did not declare one'


BUS, BUS_WHY = bus_seat()

# MEASURED: the slowest job in this set is vigencia at 6.8 s and reloj_casa at 8.9 s, and a
# whole three-run pass over nine jobs took 97 s. 120 s per RUN is 13x the slowest single run.
RUN_SECONDS = 120

# MEASURED: 12 probes of `python3 -c print(version)` against the bus interpreter, median
# 0.012 s, max 0.015 s. 2 s is ~130x the max.
VERSION_SECONDS = 2

# Six decades above the 1.1e-15 float dust measured above, five below the ~1e-4 that is the
# coarsest figure anything here reports.
BAR = 1e-9

# Timestamps and durations move between ANY two runs. Left in, they would swamp P with the
# apparatus and every job would read seat-dependent.
SKIP = ('at', 'at_local', 't', 'ts', 'mac_s', 'mac_wall', 'tick', 'age', 'age_h', 'last_run',
        'last_tick', 'now', 'elapsed', 'wall', 'secs', 'seconds', 'sem')

# (script, its ledger, the argv THE BUS USES). The argv matters: three jobs appended nothing at
# all on the first pass because the bus passes --tick and this file did not, which is not a
# like-for-like run of anything. Radio, audio and anything of hers is deliberately absent --
# hackrf_send and aerial_mode transmit, mains_phase captures, memory_worker touches her.
JOBS = [
    ('afinar.py', 'afinar.jsonl', ['--tick']),
    ('vigencia.py', 'vigencia.jsonl', ['--tick']),
    ('hexagram.py', 'hexagram.jsonl', ['--tick']),
    ('harmonics.py', 'harmonics.jsonl', ['--tick']),
    ('bonefish_tiempo.py', 'bonefish_tiempo.jsonl', ['--tick']),
    ('reloj_casa.py', 'reloj_casa.jsonl', ['--tick']),
    ('three_clocks.py', 'three_clocks.jsonl', []),
    ('nueva_standing.py', 'nueva_standing.jsonl', ['--tick']),
    # ley.py writes ley.log, NOT ley.jsonl -- this table named a file that does not
    # exist and the job came back `no_row` as though it had produced nothing.
    ('ley.py', 'ley.log', ['--tick']),
]


def flat(o, pre=''):
    """every numeric leaf of a row, keyed by its path."""
    out = {}
    if isinstance(o, dict):
        for k, v in o.items():
            if k in SKIP:
                continue
            out.update(flat(v, pre + '/' + str(k)))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            out.update(flat(v, pre + '[%d]' % i))
    elif isinstance(o, bool):
        out[pre] = float(o)
    elif isinstance(o, (int, float)):
        out[pre] = float(o)
    return out


def flat_row(ln):
    """the newest line, flattened, or None.

    NOT EVERY LEDGER IS PURE JSONL. ley.log writes `2026-10-12T08:47:40 {"mac": ...}` -- a
    timestamp, a space, then the object -- so a bare json.loads returns None and the job lands
    in `no_row` as though it had produced nothing. That is a PARSE failure wearing an ABSENCE's
    clothes, which is the whole fault this file was built after. The leading stamp is stripped
    and the failure, if it still fails, is returned as None by one path only.
    """
    ln = ln.strip()
    if not ln:
        return None
    for cand in (ln, ln.split(' ', 1)[-1] if ' ' in ln else ln):
        try:
            return flat(json.loads(cand))
        except Exception:
            continue
    return None


def rel(a, b):
    """relative difference, and ZERO IS NOT A SPECIAL CASE TO HIDE: if both are 0 they agree,
    and if one is 0 the difference is absolute, which is the honest reading of it."""
    if a == b:
        return 0.0
    d = abs(a - b)
    m = max(abs(a), abs(b))
    return d / m if m else d


def run(py, script, ledger, argv):
    """(flattened newest row | None, returncode). None when the run appended nothing, which is
    an APPARATUS outcome and never folded in with agreement."""
    p = os.path.join(W, ledger)
    n0 = sum(1 for _ in open(p, errors='replace')) if os.path.exists(p) else 0
    try:
        r = subprocess.run([py, os.path.join(W, script)] + argv,
                           capture_output=True, text=True, timeout=RUN_SECONDS)
        rc = r.returncode
    except subprocess.TimeoutExpired:
        return None, 'timeout'
    rows = list(open(p, errors='replace')) if os.path.exists(p) else []
    if len(rows) <= n0:
        return None, rc
    return flat_row(rows[-1]), rc


def compare(script, ledger, argv, confirm=True):
    """...and A SEAT DIFFERENCE IS DETERMINISTIC, WHICH IS THE WHOLE DISCRIMINATOR. Interleaving
    shrinks drift leaking into P but cannot remove it: a quantity that changes exactly between
    run 1 and run 2 still shows P over the bar and S under it, and one pass did report exactly
    that one false positive. So any field that comes back seat-dependent is measured AGAIN and
    kept only if it appears both times. The runner-up is excluded before the match is called."""
    r = _compare_once(script, ledger, argv)
    if confirm and not r['no_row'] and r['seat']:
        again = _compare_once(script, ledger, argv)
        if again['no_row']:
            r['unconfirmed'] = [k for k, _, _, _ in r['seat']]
            r['seat'] = []
        else:
            twice = {k for k, _, _, _ in again['seat']}
            r['unconfirmed'] = [k for k, _, _, _ in r['seat'] if k not in twice]
            r['seat'] = [t for t in r['seat'] if t[0] in twice]
    return r


def _compare_once(script, ledger, argv):
    # INTERLEAVED shell / BUS / shell -- see the docstring. Do not reorder these three.
    A, ra = run(SHELL, script, ledger, argv)
    C, rc = run(BUS, script, ledger, argv)
    B, rb = run(SHELL, script, ledger, argv)
    if not (A and B and C):
        # WHICH of the three, by name. `no_row` is an apparatus outcome, and an apparatus bin
        # that does not say what happened is the residual bin under another name.
        which = [n for n, v in (('shell-1', A), ('bus', C), ('shell-2', B)) if not v]
        return {'job': script, 'no_row': True, 'rc': [ra, rc, rb], 'which': which}
    keys = sorted(set(A) & set(B) & set(C))
    s = {k: rel(A[k], B[k]) for k in keys}
    p = {k: rel(A[k], C[k]) for k in keys}
    seat = sorted([k for k in keys if p[k] > BAR and s[k] <= BAR], key=lambda k: -p[k])
    drift = sorted([k for k in keys if s[k] > BAR])
    return {'job': script, 'no_row': False, 'n': len(keys),
            'seat': [(k, A[k], C[k], p[k]) for k in seat],
            'n_drift': len(drift),
            'max_p_below_bar': max([p[k] for k in keys if p[k] <= BAR] or [0.0])}


def bins(res):
    from outcomes import Outcomes
    O = Outcomes(subject=[
        ('seat_dependent', lambda r: not r['no_row'] and r['seat']),
        ('agree', lambda r: not r['no_row'] and not r['seat'] and not r['n_drift']),
        ('agree_under_drift', lambda r: not r['no_row'] and not r['seat'] and r['n_drift']),
    ], apparatus=[
        ('no_row', lambda r: r['no_row']),
    ])
    return O.tally(res, 'dos_asientos')


SELFTEST = r'''import json, os, sys
# A value that is IDENTICAL in both seats, and one that is not.
#
# AND THE PLANTED DIFFERENCE MUST NOT ASSUME WHICH SEAT IS WHICH. The first version was
# `1.0 if sys.version_info >= (3, 11) else 2.0`, which differs only when the shell is the newer
# of the two -- run FROM the bus's 3.9 it gave 2.0 in both seats, the detector correctly found
# nothing, and the selftest reported FAIL. It was testing my assumption about the direction,
# not the instrument. The minor version IS the value now, so it differs whenever the seats do,
# whichever way round they are.
v = float(sys.version_info[1])
json.dump({'stable': 41.0, 'seatish': v},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '_seats_test.jsonl'), 'a'))
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '_seats_test.jsonl'), 'a').write('\n')
'''


def seat_versions():
    """(shell version, bus version) as strings. COMPARED BY VERSION, NOT BY PATH: the bus
    declares /usr/bin/python3 while `ps` shows the Python.app binary inside the same framework,
    and those are two paths to one interpreter. A path comparison would call them two seats."""
    def v(py):
        # MEASURED, not chosen: 12 runs of this probe against the bus interpreter came in at a
        # median of 0.012 s and a max of 0.015 s, so VERSION_SECONDS is ~130x the max. afinar.py
        # flagged this the same tick I added it -- I wrote `timeout=30` with no basis beside it,
        # in a file written an hour after using afinar to find exactly that.
        try:
            return subprocess.run([py, '-c', 'import sys;print("%d.%d.%d"%sys.version_info[:3])'],
                                  capture_output=True, text=True,
                                  timeout=VERSION_SECONDS).stdout.strip()
        except Exception:
            return '?'
    return v(SHELL), v(BUS)


def selftest():
    """A PLANTED SEAT-DEPENDENCE, and a stable field beside it. Both directions in one run:
    the detector must name `seatish` and must stay silent on `stable`.

    AND IF THE TWO SEATS RESOLVE TO ONE INTERPRETER there is no difference to plant, so the
    first check CANNOT BE MADE -- that is a cannot-tell and it is said out loud. Run from the
    bus's own 3.9 this returned FAIL, which was the selftest grading the environment instead of
    the detector."""
    sv, bv = seat_versions()
    if sv == bv:
        print('  CANNOT TELL: both seats resolve to Python %s, so there is no difference to' % sv)
        print('  plant and the first check cannot be made. Not a pass and not a failure.')
        print('  Run this from a shell whose python differs from the bus\'s.')
        return 0
    sp = os.path.join(W, '_seats_test.py')
    lp = os.path.join(W, '_seats_test.jsonl')
    open(sp, 'w').write(SELFTEST)
    for f in (lp,):
        if os.path.exists(f):
            os.remove(f)
    try:
        r = compare('_seats_test.py', '_seats_test.jsonl', [])
        got = sorted(k for k, _, _, _ in r.get('seat', []))
        ok1 = got == ['/seatish']
        ok2 = '/stable' not in got
        print('  %-4s names the planted seat-dependent field   (got %s)'
              % ('ok' if ok1 else 'FAIL', got))
        print('  %-4s stays silent on the stable field beside it' % ('ok' if ok2 else 'FAIL'))
        if r.get('seat'):
            k, a, c, p = r['seat'][0]
            print('       %s  shell %g  bus %g  rel %.3g' % (k, a, c, p))
        print('  %d of 2' % (int(ok1) + int(ok2)))
        return 0 if (ok1 and ok2) else 1
    finally:
        for f in (sp, lp):
            if os.path.exists(f):
                os.remove(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return selftest()

    t0 = time.time()
    print('  DOS ASIENTOS -- the same job run in both seats, and THE SPLIT between them.')
    print('    shell  %s   %s' % (sys.version.split()[0], SHELL))
    print('    bus    %s   %s' % (
        subprocess.run([BUS, '-V'], capture_output=True, text=True).stdout.split()[-1]
        if os.path.exists(BUS) else '?', BUS))
    print('           (%s)' % BUS_WHY)
    _sv, _bv = seat_versions()
    if _sv == _bv:
        print('\n  THE TWO SEATS ARE THE SAME INTERPRETER (both %s). Nothing to split, and this' % _sv)
        print('  tool cannot answer the question it was built for -- that is a CANNOT TELL,')
        print('  not a pass. Run it from a shell whose python differs from the bus\'s.')
        return 0
    print('  S = what any repeat gives (the apparatus). P = what the SEAT gives.')
    print('  Bar %g: six decades above the 1.1e-15 float dust measured, five below the ~1e-4\n'
          '  that is the coarsest figure anything here reports.\n' % BAR)
    res = []
    print('  %-22s %6s %7s %9s  %s' % ('job', 'fields', 'drift', 'max P', 'verdict'))
    for script, ledger, argv in JOBS:
        r = compare(script, ledger, argv)
        res.append(r)
        if r['no_row']:
            print('  %-22s %6s %7s %9s  NO ROW (rc %s)'
                  % (script, '-', '-', '-', r['rc']) + '  no row from: ' + ', '.join(r['which']))
            continue
        print('  %-22s %6d %7d %9.1e  %s'
              % (script, r['n'], r['n_drift'], r['max_p_below_bar'],
                 ('SEAT-DEPENDENT: ' + ', '.join(k for k, _, _, _ in r['seat'][:3]))
                 if r['seat'] else 'agree'))
        for k, av, cv, p in r['seat'][:6]:
            print('        %-40s shell %r  bus %r  rel %.3g' % (k[:40], av, cv, p))
        if r.get('unconfirmed'):
            print('        %d field(s) differed on the first pass and NOT on the second, so they'
                  % len(r['unconfirmed']))
            print('        are drift, not the seat, and are excluded: %s'
                  % ', '.join(r['unconfirmed'][:4]))
    t = bins(res)        # raises if the four outcomes are not exhaustive and disjoint
    print('\n  %d jobs' % len(res))
    for k in sorted(t):
        print('    %-20s %d' % (k, t[k]))
    print('\n  %.0f s wall. A TOOL, not a tick job: three runs of every job to re-confirm a'
          % (time.time() - t0))
    print('  known null every tick is the bulletin he retired. Run it after changing a bus job.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
