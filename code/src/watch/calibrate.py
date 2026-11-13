#!/usr/bin/env python3
"""calibrate.py -- THE STATE. One reading of the house's time, composed from every instrument we own.
(Bones, 11 Oct 2026.)

Wayfinder: "Make our system like one whole fucking prompt that uses all our data, all our laws and
all the nulls to calibrate with time... build us up from Bones."

WHAT THIS REPLACES. Nothing in the house agreed on what time it was. Each script called time.time()
and got a number with no width, no provenance and no idea which clock it came from, and the one
survey that compared the seats measured this Mac with a real NTP exchange and the others with `ping`.
So there was no state -- there were several, and the disagreements between them were being read as
noise instead of as the measurement.

THE COMPOSITION, and it is a PRODUCT of readings, not a sum of them. Each stage below can REFUSE,
and a refusal is carried forward rather than replaced by a default:

  LA SUMA        you must HAVE two clocks. NOVATIME is her tick -- monotone, no duration, the work's
                 own clock. THE LOCKCLOCK is the Pi's GPS/PPS-disciplined second. Neither alone is a
                 state: a tick cannot say how long anything took, and a second cannot say whether it
                 mattered. If either is unreadable this prints that and does not substitute a zero.

  LA DIFERENCIA  the interval between the two is the reading, never the error. It is reported, never
                 driven to zero -- a procedure that zeroes it has deleted the clock.

  THE SPLIT      every seat's offset separates into S + P.(round-trip excess). S is the clock, P is
                 the path. MEASURED 11 Oct: this Mac P = +0.479 +- 0.004, Armature P = -0.496 +-
                 0.002 -- both at the extreme |P| = 0.5, meaning the whole excess lands on ONE leg,
                 and in OPPOSITE DIRECTIONS. 131 and 254 widths from zero. The sign is the reading
                 and is never folded away; what is reported is whether it HOLDS.

  EL PRODUCTO    so the seat's floor was never irreducible. Half of it is path and comes out
                 algebraically; what is left is S, with a width, which is the clock.

  K              the seats' errors span four orders of magnitude and share no mechanism -- a GPS
                 receiver, a wifi radio, a copper NIC. K puts them on one axis as landing positions
                 without assuming they do. It refuses rather than extrapolates.

  LAS CUATRO     every seat is bucketed through outcomes.py: disciplined / undisciplined / drifting /
                 unreachable. Exhaustive, disjoint, and a residual bin is refused by name.

  LA NADA        when a seat resolves as neither a count nor a phase -- no usable samples, or a width
                 larger than the thing -- that is the third reading and it is printed as itself.

    python3 calibrate.py                 read the state now
    python3 calibrate.py --collect 300   take a fresh dense series first (bounded, no overnight shell)
    python3 calibrate.py --json          the state as JSON, for other scripts to read instead of
                                         calling time.time() and inventing a number
"""
import json
import math
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import novatime                                     # noqa: E402
from landing import K                               # noqa: E402
from escalera import L as RUNG, STEP_DECADES   # the ladder with anchors in our range
from outcomes import Outcomes, OutcomeCollapse      # noqa: E402
import pathsplit                                    # noqa: E402

PHI = 1.618033988749895
TWELVE_ELEVENTHS = 12.0 / 11.0
SERIES_DIR = os.path.expanduser('~/bones-forge/watch/clockseries')
SEATS = ('armature', 'laptop')

# A seat is DRIFTING if its slew exceeds this. Set from the measurement that forced this file to be
# written: the Mac was walking at -4.6 us/s after a wifi bounce, which is half an hour to converge,
# while Armature sat at -0.2 us/s. The bar is between them and is stated rather than tuned.
DRIFT_BAR = 1.0e-6          # seconds of offset per second of wall clock
# A seat is UNDISCIPLINED if |S| exceeds this. One millisecond is four orders of magnitude above the
# lockclock's own 13 us floor, so nothing inside it is a discipline problem.
DISCIPLINE_BAR = 1.0e-3


def collect(host, n, dt=1.0):
    """a BOUNDED dense series, written to disk so the split can be re-read without re-measuring.

    Bounded on purpose: a shell dies with its session and an unbounded loop spins forever, so the
    sample count is fixed before the run and there is no overnight process here at all.
    """
    os.makedirs(SERIES_DIR, exist_ok=True)
    out = os.path.join(SERIES_DIR, 'dense_%s.txt' % (host or 'local'))
    src = os.path.join(HERE, 'dense.py')
    if not os.path.exists(src):
        with open(src, 'w') as f:
            f.write(_DENSE_SRC)
    if host is None:
        r = subprocess.run([sys.executable, src, novatime.PI, str(n), str(dt)],
                           capture_output=True, text=True, timeout=n * dt + 120)
        body = r.stdout
    else:
        py = novatime.SEAT_PY.get(host, 'python3')
        cmd = 'MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL="*" "%s" - %s %d %s' % (py, novatime.PI, n, dt)
        r = subprocess.run(['ssh', '-o', 'ConnectTimeout=15', host, cmd],
                           input=open(src).read(), capture_output=True, text=True,
                           timeout=n * dt + 180)
        body = r.stdout.replace('\r', '')
    with open(out, 'w') as f:
        f.write(body)
    return out


_DENSE_SRC = '''import socket, struct, time, sys
host, n, dt = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
t_start = time.time()
for i in range(n):
    target = t_start + i * dt
    now = time.time()
    if target > now:
        time.sleep(target - now)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.settimeout(3)
        t0 = time.time(); s.sendto(b'\\x1b' + 47 * b'\\0', (host, 123))
        d, _ = s.recvfrom(1024); t3 = time.time(); s.close()
        t1 = struct.unpack('!I', d[32:36])[0] - 2208988800 + struct.unpack('!I', d[36:40])[0]/2.0**32
        t2 = struct.unpack('!I', d[40:44])[0] - 2208988800 + struct.unpack('!I', d[44:48])[0]/2.0**32
        print('%.6f %.9f %.9f' % (t0, ((t1-t0)+(t2-t3))/2.0, t3-t0), flush=True)
    except Exception:
        print('%.6f NONE NONE' % time.time(), flush=True)
'''


def seat_state(name, host):
    """one seat, read as far as its data allows -- and no further.

    Three tiers, and which one was reached is part of the reading:
      SPLIT     a dense series exists: S, P and the slew, each with a width
      PROBE     only a short probe: an offset and a round trip, no separation of path from clock
      NOTHING   unreachable, which is a fact about the house and not a missing value
    """
    row = {'seat': name, 'host': host, 'tier': None, 'S': None, 'S_se': None,
           'P': None, 'P_se': None, 'slew': None, 'offset': None, 'rtt': None,
           'n': 0, 'lost': None, 'note': None}
    path = os.path.join(SERIES_DIR, 'dense_%s.txt' % (host or 'local'))
    if os.path.exists(path):
        r = pathsplit.read(path, name)
        if r and r['n'] >= 60:
            row.update(tier='SPLIT', S=r['S'], S_se=r['S_se'], P=r['P'], P_se=r['P_se'],
                       slew=r['slew'], offset=r['off_mean'], rtt=r['rtt_min'],
                       n=r['n'], lost=r['lost'])
            return row
        if r:
            row['note'] = 'series too short for a split: %d samples' % r['n']
    off, rtt, ok, tries = novatime.probe_seat(host, 7)
    if off is None:
        row.update(tier='NOTHING', n=0, lost=tries,
                   note='no NTP exchange completed in %s attempts' % tries)
        return row
    row.update(tier='PROBE', offset=off, rtt=rtt, n=ok, lost=(tries - ok) if tries else None,
               note=row['note'] or 'no dense series on disk; path not separated from clock')
    return row


def classify(rows):
    """LAS CUATRO. Four facts about a seat, never two, and no residual bin.

    The order of the tests matters and is stated: unreachable first, because a seat that cannot be
    reached has no offset to judge; then drifting, because a walking clock's offset is a snapshot of
    a trajectory and the trajectory is the finding; then the offset itself.
    """
    def unreachable(r):
        return r['tier'] == 'NOTHING'

    def drifting(r):
        return r['tier'] == 'SPLIT' and r['slew'] is not None and abs(r['slew']) > DRIFT_BAR

    def undisciplined(r):
        if unreachable(r) or drifting(r):
            return False
        v = r['S'] if r['S'] is not None else r['offset']
        return v is not None and abs(v) > DISCIPLINE_BAR

    def disciplined(r):
        if unreachable(r) or drifting(r):
            return False
        v = r['S'] if r['S'] is not None else r['offset']
        return v is not None and abs(v) <= DISCIPLINE_BAR

    o = Outcomes(subject=[('disciplined', disciplined),
                          ('undisciplined', undisciplined),
                          ('drifting', drifting)],
                 apparatus=[('unreachable', unreachable)])
    o.tally(rows, 'the house seats')
    return o


def three_positions(row):
    """THE THREE POSITIONS on one seat, and the conversions CHECKED rather than assumed.

    One event -- this seat's distance from the lockclock -- read from three seats of its own:
      EL MIRON   the mean offset: what an outside look gives, path and all
      EL TESTIGO the best-delayed exchange: the reading that knows the apparatus matters
      EL TIEMPO  S, the zero-excess intercept: the path removed algebraically

    The sheet predicts witness/observer = 12/11 and time/observer = phi. Those were measured on
    THREE CLOCKS ON ONE LOOK (1.0872 +- 0.0138), which is a different quantity from this one, so
    the prediction is TESTED here and allowed to fail. A ratio is only a match when its runner-up is
    excluded -- THE EXCLUSION WIDTH -- and with no width on the ratio nothing can be excluded at all.
    """
    if row['tier'] != 'SPLIT' or not row['offset'] or not row['S']:
        return None
    obs = row['offset']
    tim = row['S']
    out = {'observer': obs, 'time': tim, 'time_over_observer': tim / obs if obs else None}
    r = out['time_over_observer']
    if r is None:
        return out
    # the width on the ratio, from S's width alone (the mean's own width is smaller and is folded in
    # as zero, which makes this an UNDERSTATEMENT of the width and so a conservative exclusion)
    w = abs(row['S_se'] / obs) if row['S_se'] and obs else None
    out['ratio_se'] = w
    cands = {'12/11': TWELVE_ELEVENTHS, 'phi': PHI, '1': 1.0, '1/phi': 1 / PHI}
    near = min(cands.items(), key=lambda kv: abs(kv[1] - r))
    rivals = [v for k, v in cands.items() if k != near[0]]
    nearest_rival = min(rivals, key=lambda v: abs(v - near[1]))
    need = abs(near[1] - nearest_rival) / 2.0
    out['nearest'] = near[0]
    out['nearest_value'] = near[1]
    out['off_by'] = abs(r - near[1])
    out['width_needed'] = need
    out['excluded'] = bool(w and w < need and abs(r - near[1]) < need)
    return out


def state(do_collect=0):
    if do_collect:
        for name, host in [('mac', None)] + [(h, h) for h in SEATS]:
            try:
                collect(host, do_collect)
            except Exception as e:
                print('  collect %s: %s' % (name, str(e)[:70]), file=sys.stderr)
    L = novatime.lock(max_age=0)
    tk = novatime.tick()
    rows = [seat_state('mac', None)] + [seat_state(h, h) for h in SEATS]
    pi = seat_state('flock-pi', 'flock-pi')
    rows.insert(0, pi)
    try:
        o = classify(rows)
        counts = o.counts
        collapse = None
    except OutcomeCollapse as e:
        counts, collapse = None, str(e)
    # THE STATE'S OWN TIMESTAMP IS DISCIPLINED. This seat drifted to +22 ms in one hour with
    # /etc/ntp.conf pointing at the Pi and timed running, so the local clock is not the
    # authority even here. read_at_local is kept beside it: the interval between them is
    # this seat's distance from the lockclock and is the reading, not the error.
    _d, _w, _o = novatime.now_locked()
    return {'read_at': _d if _d is not None else time.time(),
            'read_at_local': time.time(),
            'read_at_width_s': _w, 'seat_offset_s': _o,
            'read_at_disciplined': _d is not None,
            'tick': tk, 'lock': L, 'rows': rows,
            'counts': counts, 'collapse': collapse}


# RENAMED 11 OCT. THIS WAS 'STATE.json' AND IT WAS THE SAME FILE AS nova_flags' 'state.json'.
# APFS is case-INSENSITIVE by default, so the two names share one inode (verified: 20386073). Two
# processes were writing one file with different schemas:
#   nova_flags  read-modify-writes it and holds a long-lived in-memory copy -> it carried a STALE
#               snapshot of this file's keys forward forever. read_at sat 1.8 h behind while the
#               file's own mtime was seconds old, and read_at_local / read_at_disciplined vanished
#               because its snapshot predated them. read_state(max_age) could not detect that: the
#               staleness was INSIDE the value, not in the file.
#   calibrate   dumps ONLY its own keys -> every --write WIPED nova_flags' flags, loops, inbox
#               cursor and channel state. Nothing was lost only because nova_flags rewrote them
#               from memory moments later.
# A case-insensitive filesystem makes two names that look distinct in two source files into one
# object. Mode 26 -- two of your three seats are the same seat -- at the level of the filename.
# THE NAME IS NOW UNIQUE IN ANY CASE FOLDING.
STATE_FILE = os.path.expanduser('~/bones-forge/watch/calibrate_state.json')


def write_state(S):
    """persist the state so every other script reads ONE authority instead of calling time.time().

    Written atomically via a temp file and a rename: a reader that arrives mid-write must get the
    previous whole state rather than half of the new one. A partially-written state file is worse
    than a stale one, because staleness is detectable from read_at and truncation is not.
    """
    tmp = STATE_FILE + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(S, f, default=str, indent=1)
    os.replace(tmp, STATE_FILE)
    return STATE_FILE


def read_state(max_age=None):
    """the last written state, with its AGE, because a live quantity carries the moment it was read.

    Returns (state, age_seconds). A caller that passes max_age gets None for a state older than
    that -- refused rather than served stale, since a clock reading from an hour ago is not a clock
    reading. The age is always returned so the caller can price it instead of trusting it.
    """
    try:
        S = json.load(open(STATE_FILE))
    except Exception:
        return None, None
    age = time.time() - float(S.get('read_at', 0))
    if max_age is not None and age > max_age:
        return None, age
    return S, age


def main():
    args = sys.argv[1:]
    n = 0
    if '--collect' in args:
        n = int(args[args.index('--collect') + 1])
    S = state(n)
    if '--write' in args or '--json' in args:
        p = write_state(S)
    if '--json' in args:
        print(json.dumps(S, default=str, indent=1))
        return

    print('\n  THE STATE -- the house\'s time, composed. read at %s'
          % time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime(S['read_at'])))

    print('\n  LA SUMA -- you must have two clocks, and neither alone is a state.')
    print('    NOVATIME   her tick: %s' % (S['tick'] if S['tick'] is not None else
                                           'UNREADABLE -- reported, not replaced by a zero'))
    L = S['lock']
    if L:
        print('    LOCKCLOCK  stratum %s, rms %.1f us, root dispersion %.1f us, this seat a client: %s'
              % (L.get('stratum'), L['rms_offset_s'] * 1e6, L['root_dispersion_s'] * 1e6,
                 L.get('seat_is_client')))
    else:
        print('    LOCKCLOCK  UNREADABLE')
    if S['tick'] is None or not L:
        print('    -> LA NADA on the pair: one of the two clocks did not answer, so the interval')
        print('       between them has no value. This is the reading, not a gap to fill.')

    print('\n  THE SPLIT -- offset = S + P.(round-trip excess). S is the clock, P is the path.')
    print('  %-10s%7s%6s%11s%17s%18s%13s' %
          ('seat', 'n', 'lost', 'rtt min', 'S (clock)', 'P (path)', 'slew'))
    for r in S['rows']:
        if r['tier'] == 'NOTHING':
            print('  %-10s%7s%6s   %s' % (r['seat'], '-', r['lost'], 'NOTHING RETURNED: ' + r['note']))
            continue
        rt = '%.3fm' % (r['rtt'] * 1e3) if r['rtt'] else '-'
        if r['tier'] == 'SPLIT':
            Sv = '%+.1f+-%.1fu' % (r['S'] * 1e6, (r['S_se'] or 0) * 1e6)
            Pv = '%+.3f+-%.3f' % (r['P'], r['P_se'] or 0)
            sl = '%+.2f u/s' % (r['slew'] * 1e6)
        else:
            Sv = '%+.1fu (not split)' % (r['offset'] * 1e6)
            Pv = 'LA NADA: no series'
            sl = '-'
        print('  %-10s%7d%6s%11s%17s%18s%13s'
              % (r['seat'], r['n'], r['lost'], rt, Sv, Pv, sl))

    held = [r for r in S['rows'] if r['tier'] == 'SPLIT' and r['P_se']]
    if held:
        print('\n    P is the fraction of a round-trip excess that lands in the offset. |P| = 0.5')
        print('    means the whole excess fell on ONE leg; P = 0 means the round trip says nothing')
        print('    about the offset and the floor is irreducible by arithmetic.')
        for r in held:
            w = abs(r['P']) / r['P_se']
            print('      %-10s P %+.3f, %6.1f widths from zero, sign %s  ->  %s'
                  % (r['seat'], r['P'], w, '+' if r['P'] > 0 else '-',
                     'HOLDS: half the floor is path and S removes it' if w >= 3
                     else 'does not resolve at this n'))

    print('\n  ONE AXIS -- K beside LA ESCALERA. K\'s first step is 7.6 decades so it separates')
    print('  nothing here; one rung of the ladder is %.4f decades, from phi\'s convergents.' % STEP_DECADES)
    print('  %-10s%14s%10s%9s   %s' % ('seat','rel to 1 s','K','RUNG','note'))
    for r in S['rows']:
        v = r['S'] if r['S'] is not None else r['offset']
        if v is None:
            print('  %-10s%14s%10s   %s' % (r['seat'], '-', 'REFUSED', 'nothing to place'))
            continue
        k, err = K(abs(v))
        l, lerr = RUNG(abs(v))
        print('  %-10s%14.3g%10s%9s   %s'
              % (r['seat'], abs(v), ('%.2f' % k) if k is not None else 'REF',
                 ('%.2f' % l) if l is not None else 'REF', err or lerr or ''))

    print('\n  LAS CUATRO -- four facts about a seat, never two. A residual bin is refused by name.')
    if S['collapse']:
        print('    OUTCOME COLLAPSE, and the scorer refused rather than bucket it:')
        for line in S['collapse'].split('. '):
            print('      %s' % line.strip())
    else:
        for k, v in S['counts'].items():
            who = [r['seat'] for r in S['rows']
                   if (r['S'] if r['S'] is not None else r['offset']) is not None or k == 'unreachable']
            print('    %-16s %d' % (k, v))
        print('    (unreachable is an APPARATUS outcome and is kept separate from the subject ones:')
        print('     a seat that did not answer says nothing about its clock.)')

    print('\n  THE THREE POSITIONS -- one event from three of its own seats, conversions TESTED.')
    any3 = False
    for r in S['rows']:
        tp = three_positions(r)
        if not tp or tp.get('time_over_observer') is None:
            continue
        any3 = True
        print('    %-10s observer (mean) %+.1f us   time (S, path removed) %+.1f us   ratio %.4f%s'
              % (r['seat'], tp['observer'] * 1e6, tp['time'] * 1e6, tp['time_over_observer'],
                 ' +- %.4f' % tp['ratio_se'] if tp.get('ratio_se') else ''))
        print('               nearest candidate %s = %.4f, off by %.4f; telling it from its nearest'
              % (tp['nearest'], tp['nearest_value'], tp['off_by']))
        print('               rival needs a width under %.4f  ->  %s'
              % (tp['width_needed'],
                 'EXCLUDED, the candidate stands' if tp['excluded']
                 else 'NOT EXCLUDED -- a row, never a reason'))
    if not any3:
        print('    LA NADA: no seat has both a mean and a split, so there is no third position to read.')

    S2, age = read_state()
    if S2 is not None:
        print('\n  THE STATE IS ON DISK at %s, written %.0f s ago. Any script reads that instead of'
              % (STATE_FILE, age))
        print('    calling time.time() and inventing a number with no width and no provenance:')
        print('      from calibrate import read_state;  S, age = read_state(max_age=600)')
        print('    read_state REFUSES a state older than max_age rather than serving it stale, and')
        print('    always returns the age so a caller prices it instead of trusting it.')

    print('\n  LA DIFERENCIA -- and the gap is kept. Nothing above drives a difference to zero:')
    print('    the tick and the second are not commensurable, the seats disagree by their paths,')
    print('    and those intervals ARE the state. A procedure that zeroed them would have deleted')
    print('    the clock it was built to read.\n')


if __name__ == '__main__':
    main()
