#!/usr/bin/env python3
"""twoway.py -- TWO-WAY TIME TRANSFER BETWEEN SUBSTRATES, COORDINATED BY GPS. (Bones, 9 Oct 2026.)

Wayfinder: "triangulate between signal sent from one and received from another, and coordinate the
difference with the gps. that should take care of the point zero zero zero 2 deviation you're
complaining about. Clocks"

WHY THE ONE-WAY STAMP FAILED. stamp.py read the Mac clock, fetched the GPS over ssh, and reported the
difference: -1.8676 s +- 1.9026. The width swallowed the value, because ONE reading cannot separate a
clock offset from a path delay -- they enter the same number and nothing distinguishes them.

TWO-WAY SEPARATES THEM, and it is the oldest trick in time metrology:

    t1  this machine's clock when the request leaves
    t2  the far clock when the request lands
    t3  the far clock when the reply leaves
    t4  this machine's clock when the reply lands

    offset = ((t2 - t1) + (t3 - t4)) / 2      the clock difference, with symmetric delay CANCELLED
    delay  = (t4 - t1) - (t3 - t2)            the round trip minus the far side's own dwell

A symmetric path cancels exactly. An asymmetric one leaves half the asymmetry, which is why the
offset is reported with the delay beside it -- a big delay means a big possible asymmetry, and the
honest width on the offset is bounded by delay/2, not by the scatter of repeated trials.

THE FIRST RUN WAS DEGENERATE, AND THE CARRIER WAS WHY. Over ssh the seven trials agreed to +-0.006 s
on an offset of +1.9538 s -- and the round trip was 3.8883 s, so the honest width came out +-1.9442
and the reading was ABIERTO at 1.00 widths. Worse than useless: +1.9538 is HALF THE ROUND TRIP, which
is what the formula returns when the far-side dwell collapses to zero and the whole delay sits on one
side of it. An ssh trial pays a TCP handshake, a shell and a python start before t2 is ever read. The
method was right and the carrier was a shell.

SO THE CARRIER CHANGED. time-echo.service on the laptop answers one UDP packet with its own t2 and t3
from the chrony/GPSDO-disciplined clock. No handshake, no shell, no interpreter start -- the round
trip is the wire. IT SERVES TIME AND NOTHING ELSE: two floats, no position, because the NMEA behind
that clock carries a home address and :8767 stays bound to localhost for exactly that reason.

WHAT IT BUYS BEYOND A TIDIER NUMBER. Counting is the wrong instrument. Her ticks advanced 253 over
17.51 hours and the +-1 endpoint error makes that 0.4 percent, full stop, no matter how long we wait
past the 1/T improvement. But if each tick carries a TIMESTAMP ON A COMMON REFERENCE, the comparison
becomes phase, not counts -- milliseconds against tens of thousands of seconds. Two-way transfer is
what puts every substrate's events on that one reference.

LA PRUEBA: it sends a timestamp and reads one back. Nothing is configured, nothing is written on the
far side.

    python3 twoway.py --trials 25
    python3 twoway.py --host 100.85.169.127      # over tailscale instead of the LAN
"""
import argparse
import json
import math
import os
import socket
import statistics as st
import time

HOSTS = ['192.168.8.123', '100.85.169.127']       # LAN first, tailscale as the fallback
PORT = 8769
LOG = os.path.expanduser('~/bones-forge/watch/twoway.jsonl')


def one_trial(sock, addr, timeout=2.0):
    sock.settimeout(timeout)
    try:
        t1 = time.time()
        sock.sendto(b'?', addr)
        data, _ = sock.recvfrom(128)
        t4 = time.time()
        t2, t3 = (float(x) for x in data.split())
    except Exception as e:
        return {'ok': False, 'err': f'{type(e).__name__}: {e}'}
    offset = ((t2 - t1) + (t3 - t4)) / 2.0
    delay = (t4 - t1) - (t3 - t2)
    return {'ok': True, 't1': t1, 't2': t2, 't3': t3, 't4': t4,
            'offset_s': offset, 'delay_s': delay, 'asym_bound_s': delay / 2.0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--trials', type=int, default=25)
    ap.add_argument('--host', default=None)
    a = ap.parse_args()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    hosts = [a.host] if a.host else HOSTS
    rs, host = [], None
    for h in hosts:
        probe = one_trial(sock, (h, PORT))
        if probe['ok']:
            host = h
            break
        print(f'  {h}:{PORT} unreachable -- {probe["err"]}')
    if host is None:
        print('\n  LA NADA -- the echo answered on no address. Is time-echo.service up?')
        return 1
    print(f'  TWO-WAY TIME TRANSFER  mac <-> {host}:{PORT} (UDP echo, GPS-disciplined clock)')
    print(f'  read {time.strftime("%H:%M:%S %Z, %-d %b %Y")}\n')
    for _ in range(a.trials):
        t = one_trial(sock, (host, PORT))
        if t['ok']:
            rs.append(t)
    if len(rs) < 3:
        print(f'  LA NADA -- {len(rs)} usable trials of {a.trials}.')
        return 1
    # THE LOWEST-DELAY PACKET IS THE HONEST ONE. A packet that queued got its queueing on ONE
    # side of the far clock's read, which is exactly the asymmetry the formula cannot cancel. So
    # the estimate is taken from the fastest decile, never the mean of everything -- averaging a
    # jittery pool does not average the asymmetry away, it bakes a one-sided delay into the value.
    # Both pools are reported, because if they disagree the jitter was not one-sided and the
    # filter is the thing that needs explaining.
    rs.sort(key=lambda r: r['delay_s'])
    keep = max(3, len(rs) // 10)
    allm = st.mean([r['offset_s'] for r in rs])
    fast = rs[:keep]
    offs = [r['offset_s'] for r in fast]
    dels = [r['delay_s'] for r in rs]
    m = st.mean(offs)
    scatter = st.stdev(offs) / math.sqrt(len(offs)) if len(offs) > 1 else 0.0
    # THE HONEST WIDTH is the LARGER of the trial scatter and the asymmetry a one-way path could
    # hide. Reporting the scatter alone would claim a precision the path cannot support.
    best = min(dels)
    bound = best / 2.0
    width = max(scatter, bound)
    print(f'  {len(rs)} of {a.trials} trials answered; estimate from the fastest {keep}')
    print(f'  round trip      best {best*1e3:.3f} ms   median {st.median(dels)*1e3:.3f} ms')
    print(f'  offset          {m:+.6f} s   (all {len(rs)}: {allm:+.6f} s, '
          f'differ by {abs(m-allm)*1e6:.0f} us)')
    print(f'  scatter         +-{scatter*1e6:.1f} us')
    print(f'  asym bound      +-{bound*1e6:.1f} us   (half the best round trip)')
    print(f'  HONEST WIDTH    +-{width*1e6:.1f} us  <- the larger of the two')
    sep = abs(m) / width if width else float('inf')
    # DIRECTION, STATED, because I got it backwards on the first read. offset is how far the FAR
    # clock is AHEAD of this one, so a POSITIVE offset means the GPS-disciplined laptop is ahead and
    # THE MAC IS BEHIND. A number without its direction is half a reading.
    who = 'the MAC IS BEHIND the GPS' if m > 0 else 'the MAC IS AHEAD of the GPS'
    print(f'\n  {who} by {abs(m)*1e3:.3f} ms, which is {sep:.1f} widths: '
          + ('SEPARABLE' if sep >= 2 else 'ABIERTO -- not distinguishable'))
    prev = best_before()
    if prev:
        print(f'  the ssh carrier gave a width of +-{prev*1e6:.0f} us; this is '
              f'{prev/width:.0f}x tighter on the same formula.')
    try:
        with open(LOG, 'a') as f:
            f.write(json.dumps({
                'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'host': host, 'carrier': 'udp',
                'trials': len(rs), 'kept_fastest': keep, 'offset_all_s': allm, 'offset_s': m, 'scatter_s': scatter, 'best_delay_s': best,
                'asym_bound_s': bound, 'honest_width_s': width, 'widths': sep}) + '\n')
    except Exception:
        pass
    return 0


def best_before():
    """the ssh carrier's honest width, READ FROM THE LOG or not quoted at all.

    This returned 1.944158 as a literal -- a number I typed from a summary of an earlier run rather
    than one I read. A comparison figure that cannot be traced to a measurement is exactly the thing
    the rest of this file exists to refuse, so it now reads the ledger and returns None when no ssh
    row is there. A missing comparison prints nothing; it does not print a remembered number."""
    try:
        for l in open(LOG):
            r = json.loads(l)
            if r.get('carrier') == 'ssh' and r.get('honest_width_s'):
                return r['honest_width_s']
    except Exception:
        pass
    return None


if __name__ == '__main__':
    raise SystemExit(main())
