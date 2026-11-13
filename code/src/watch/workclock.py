#!/usr/bin/env python3
"""workclock.py -- EACH SEAT'S CLOCK RATE, MEASURED BY WORK, WITH THE PATH CANCELLED.
(Bones, 11 Oct 2026. Wayfinder's design.)

Wayfinder: "can't you time a fucking algorithm so it runs for a set time and use that for each
individual clock and do some robot shit with how the other clocks read that one?"

WHY THIS IS THE RIGHT INSTRUMENT, and it is a statement about arithmetic rather than a preference.
Every offset measured through NTP carries half the one-way delay, and that term is a SYSTEMATIC that
no amount of averaging removes -- measured tonight at P = 0.42 to 0.47 of the round-trip excess, i.e.
essentially the whole of it landing on one leg. So an OFFSET is path-contaminated by construction.

A DURATION IS NOT. If a constant path asymmetry d sits on the link, then every offset reading is
wrong by the same d:
    off_start = true_off_start + d
    off_end   = true_off_end   + d
and the DIFFERENCE kills it exactly:
    off_end - off_start = true_off_end - true_off_start      d cancels, identically
That difference, divided by the local interval, IS the clock rate error:
    rate_error = (off_end - off_start) / (t_end_local - t_start_local)
in seconds per second. THE SPLIT, used for what it is for: S is common to every run and cancels in
the interval; what is left is the thing.

AND THE WORK IS NOT DECORATION. Three reasons it is in here:
  1  it makes the endpoints REAL EVENTS rather than two idle sleeps, so the seat is doing what it
     normally does while being measured -- a clock measured idle is a clock measured in a state it
     is never in when it matters.
  2  ops / duration is a FREE SECOND CHANNEL, and it separates two things that a single number
     conflates: CPU SPEED shows up in ops completed, CLOCK RATE shows up in the offset difference.
     Neither can masquerade as the other here.
  3  the op count is an INVARIANT across machines -- the same loop, the same arithmetic, the same
     number of iterations -- which is the apparatus equalised across columns rather than hoped for.

THE INTERVAL IS SET BY EACH SEAT'S OWN CLOCK, ON PURPOSE AND NOT BY MINE. Asking a seat to run
"until the lockclock says stop" would measure the network again. Asking it to run for N of its own
seconds makes the local interval exact BY DEFINITION, so all the uncertainty lands in the two
lockclock probes, where it can be measured and reported.

    python3 workclock.py --run 60          run the job here and print one JSON line
    python3 workclock.py --all 60          run it on every seat and read the rates
"""
import hashlib
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PI = '192.168.8.145'
SEAT_PY = {'armature': r'C:\Users\Heure\AppData\Local\Programs\Python\Python313\python.exe',
           'laptop': 'python3', 'flock-pi': 'python3'}

# The job: SHA-256 chaining. Deterministic, CPU-bound, no I/O, no allocation growth, and the op
# count is exactly the iteration count on every machine. A floating-point loop would let one seat's
# FMA unit change the work; a hash chain cannot be reordered or vectorised away.
_JOB = r'''
import hashlib, json, socket, struct, sys, time

PI = sys.argv[1]
SECS = float(sys.argv[2])
BLOCK = 2000


def probe(tries=9):
    """best-of-n on the ROUND TRIP, which is selection on the apparatus and not on the answer."""
    best = None
    for _ in range(tries):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.settimeout(3)
            t0 = time.time(); s.sendto(b'\x1b' + 47 * b'\0', (PI, 123))
            d, _ = s.recvfrom(1024); t3 = time.time(); s.close()
            t1 = struct.unpack('!I', d[32:36])[0] - 2208988800 + struct.unpack('!I', d[36:40])[0]/2.0**32
            t2 = struct.unpack('!I', d[40:44])[0] - 2208988800 + struct.unpack('!I', d[44:48])[0]/2.0**32
            off, rtt = ((t1 - t0) + (t2 - t3)) / 2.0, (t3 - t0)
            if best is None or rtt < best[1]:
                best = (off, rtt)
        except Exception:
            pass
    return best


a = probe()
t_start = time.time()
h = hashlib.sha256(b'heuremen').digest()
ops = 0
# the loop checks the clock only every BLOCK ops, so the clock read is not itself the work
while time.time() - t_start < SECS:
    for _ in range(BLOCK):
        h = hashlib.sha256(h).digest()
    ops += BLOCK
t_end = time.time()
b = probe()

print(json.dumps({
    'ops': ops,
    't_start': t_start, 't_end': t_end,
    'local_interval': t_end - t_start,
    'off_start': a[0] if a else None, 'rtt_start': a[1] if a else None,
    'off_end': b[0] if b else None, 'rtt_end': b[1] if b else None,
    'digest': h.hex()[:16],
}))
'''


def run_here(secs):
    import tempfile
    with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as f:
        f.write(_JOB); p = f.name
    try:
        r = subprocess.run([sys.executable, p, PI, str(secs)],
                           capture_output=True, text=True, timeout=secs + 180)
        return _parse(r.stdout)
    finally:
        os.unlink(p)


def run_there(host, secs):
    py = SEAT_PY.get(host, 'python3')
    cmd = 'MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL="*" "%s" - %s %s' % (py, PI, secs)
    r = subprocess.run(['ssh', '-o', 'ConnectTimeout=15', host, cmd],
                       input=_JOB, capture_output=True, text=True, timeout=secs + 240)
    return _parse(r.stdout.replace('\r', ''))


def _parse(out):
    for line in reversed((out or '').strip().splitlines()):
        line = line.strip()
        if line.startswith('{'):
            try:
                return json.loads(line)
            except ValueError:
                continue
    return None


def rate_of(d, is_reference=False, ref_rms=None):
    """the clock rate error in parts per million, with the constant path term CANCELLED.

    Returns (ppm, width_ppm, note). The width is the two probes' own one-way ambiguities -- half
    each round trip -- in quadrature over the interval, because that is the only uncertainty left
    once the local interval is exact by construction.

    AND THE REFERENCE SEAT IS A DIFFERENT APPARATUS, which the first version of this function did
    not know. The Pi IS the lockclock, so it probes ITSELF: its rate error against itself is ZERO
    BY DEFINITION, and what the two offsets actually show is chrony's own servo moving its internal
    estimate. Worse, the network width formula is meaningless there -- a 0.026 ms self-probe gave a
    spurious 0.46 ppm width at T = 40 s, which manufactured "2.0 widths, the only seat outside one
    width" out of the reference's own noise. Its real width is chrony's offset stability:
    rms 104.7 us over the same interval is 3.70 ppm, against which the same reading is 0.2 widths.
    So the reference gets its own width and its own note, or it gets refused.
    """
    if not d or d.get('off_start') is None or d.get('off_end') is None:
        return None, None, 'a probe returned nothing: no rate available'
    T = d['local_interval']
    if T <= 0:
        return None, None, 'non-positive interval'
    drift = d['off_end'] - d['off_start']
    ppm = drift / T * 1e6
    if is_reference:
        if not ref_rms:
            return None, None, ('THE REFERENCE PROBES ITSELF: its rate against itself is zero by '
                                'definition and no width is available. REFUSED.')
        w = ref_rms * 2 ** 0.5 / T * 1e6
        return ppm, w, ('self-probe: this is chrony\'s SERVO, not a clock rate. width from its own '
                        'rms %.1f us, not from the path' % (ref_rms * 1e6))
    w = ((d['rtt_start'] / 2.0) ** 2 + (d['rtt_end'] / 2.0) ** 2) ** 0.5 / T * 1e6
    return ppm, w, 'drift %+.6f s over %.1f s' % (drift, T)


if __name__ == '__main__':
    args = sys.argv[1:]
    secs = 60.0
    for i, a in enumerate(args):
        if a in ('--run', '--all') and i + 1 < len(args):
            secs = float(args[i + 1])

    if '--run' in args:
        print(json.dumps(run_here(secs)))
        sys.exit(0)

    seats = [('mac', None), ('flock-pi', 'flock-pi'), ('armature', 'armature'), ('laptop', 'laptop')]
    print('  THE WORK CLOCK. Each seat runs the SAME sha256 chain for %.0f of ITS OWN seconds and'
          % secs)
    print('  probes the lockclock at both ends. A constant path asymmetry cancels in the')
    print('  DIFFERENCE of the two offsets, so what is left is the seat\'s own RATE.\n')
    # ALL FOUR AT ONCE, AND THE FIRST VERSION RAN THEM SEQUENTIALLY -- which made the whole
    # thing a drift measurement instead of a comparison. Four 45-minute arms in series is three
    # hours in which no two seats share an interval, and La Diferencia is explicit: a SEQUENTIAL
    # dyad measures drift, a SIMULTANEOUS one measures the thing. Threads, because every arm is
    # waiting on a subprocess or an ssh pipe and none of them holds the GIL.
    import threading
    got, lock = {}, threading.Lock()

    def arm(name, host):
        d = run_here(secs) if host is None else run_there(host, secs)
        with lock:
            got[name] = d

    th = [threading.Thread(target=arm, args=(n, h), daemon=True) for n, h in seats]
    for x in th:
        x.start()
    for x in th:
        x.join(timeout=secs + 300)

    print('  %-10s%12s%14s%13s%13s%11s' %
          ('seat', 'ops (M)', 'ops/s (M)', 'off start', 'off end', 'interval'))
    for name, _h in seats:
        d = got.get(name)
        if not d:
            print('  %-10s NOTHING RETURNED' % name); continue
        print('  %-10s%12.2f%14.3f%12.1fu%12.1fu%10.3fs'
              % (name, d['ops'] / 1e6, d['ops'] / d['local_interval'] / 1e6,
                 (d['off_start'] or 0) * 1e6, (d['off_end'] or 0) * 1e6, d['local_interval']))

    print('\n  THE RATE, path cancelled:')
    print('  %-10s%14s%12s%10s   %s' % ('seat', 'rate ppm', 'width ppm', 'widths', 'note'))
    try:
        import novatime
        _L = novatime.lock(max_age=0)
        _ref_rms = (_L['rms_offset_s'] ** 2 + _L['root_dispersion_s'] ** 2) ** 0.5 if _L else None
    except Exception:
        _ref_rms = None
    for name, _h in seats:
        ppm, w, note = rate_of(got.get(name), is_reference=(name == 'flock-pi'), ref_rms=_ref_rms)
        if ppm is None:
            print('  %-10s%14s%12s%10s   %s' % (name, '-', '-', '-', note)); continue
        print('  %-10s%+14.2f%12.2f%10.1f   %s'
              % (name, ppm, w, abs(ppm) / w if w else 0, note))
    print('\n  A rate inside one width is a clock that is not gaining or losing against the')
    print('  lockclock at all. A rate several widths out is a real frequency offset, and it is the')
    print('  one thing an NTP offset reading can never tell you, because the path sits inside it.')
