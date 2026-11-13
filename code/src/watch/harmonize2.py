#!/usr/bin/env python3
"""harmonize2.py -- TWO MACHINES, ONE GRID, NO NETWORK IN THE MEASUREMENT. (Bones, 9 Oct 2026.)

Wayfinder: "harmonize. triangulate. witness. observer. time. the null is load bearing. avoid binary.
Ride."

THE IDEA. Two-way transfer over WiFi bottoms out at the path asymmetry -- the measured bound is about
+-2.3 ms and no number of packets lowers it, because it is a property of the path. The mains harmonic
has no path: the grid is the SAME grid at the Mac and at the laptop, and power-line propagation across
a house is nanoseconds. So if both machines read the phase of 120 Hz over the SAME wall interval, the
difference between their phases is a clock comparison with the network removed from the arithmetic.

    measured phase difference  =  (clock offset) x 120 Hz,  modulo one cycle

AND THE AMBIGUITY IS RESOLVED BY THE WIRE, which is the part that makes it usable. Phase repeats every
8.3333 ms. The UDP two-way reading is good to about +-2.3 ms, which is inside the half cycle of
4.1667 ms, so it says WHICH cycle and the phase supplies the fraction. Coarse from the wire, fine from
the harmonic, and the ambiguity condition CHECKED rather than assumed.

SIMULTANEITY IS THE ENGINEERING, and the calibration ledger is what buys it. An ssh round trip is
seconds, so "start now" on both machines does not overlap. Instead both are told to start at a named
GPS INSTANT: the laptop waits until its own clock (chrony + the Leo Bodnar GPSDO) reaches T, and the
Mac waits until its clock reaches T minus the measured offset. Each then reports the start it actually
achieved, and the residual start error is CARRIED rather than assumed to be zero.

THE NULL IS LOAD BEARING AND IT IS NOT ZERO. Two unrelated phases differ UNIFORMLY over the cycle, so
the none for this comparison is the uniform distribution -- sd 2.4056 ms, resultant R near
sqrt(pi)/(2.sqrt(n)), not R near 0 and certainly not a difference near zero. Measured earlier today on
two devices in ONE machine: R = 0.7192 against a none of 0.2558, Rayleigh 12.41, uniform reaching that
0.202 percent of the time -- separable, and still far from locked. That is the shape to expect here
too, and the verdict has four readings rather than two: UNIFORM, ABIERTO, PARTIAL, LOCKED.

    python3 harmonize2.py --trials 6 --seconds 8
"""
import argparse
import json
import math
import os
import statistics as st
import subprocess
import sys
import time

import numpy as np

W = os.path.expanduser('~/bones-forge/watch/')
sys.path.insert(0, W)
import calib                                                    # noqa: E402
from audio_clock import _hold_card, _release_card               # noqa: E402
from harmonize import fit, wrap, CYCLE_MS, LINE, SR             # noqa: E402

LOG = os.path.join(W, 'harmonize2.jsonl')
LAPTOP_UDP = '192.168.8.123'      # the echo, by address
LAPTOP_SSH = 'laptop'             # the ALIAS, which carries HostName AND User ctrai
# Using the raw IP for ssh took the LOCAL username and gave
# 'heuremen@192.168.8.123: Permission denied (publickey)'. UDP wants an address, ssh wants the
# alias; they are not interchangeable and one constant for both was the bug.
LEAD_S = 12.0                 # how far ahead to schedule the shared start


FAR = r'''
import subprocess, sys, time, json
T = float(sys.argv[1]); SEC = float(sys.argv[2]); SR = 48000
# wait until THIS machine's clock (chrony + GPSDO) reaches the named instant
while time.time() < T - 0.02:
    time.sleep(0.005)
t0 = time.time()
raw = subprocess.run(["arecord","-D","plughw:1,0","-f","S16_LE","-r",str(SR),"-c","1",
                      "-d",str(int(SEC)),"-t","raw","-q"], capture_output=True).stdout
t1 = time.time()
sys.stdout.write(json.dumps({"t0": t0, "t1": t1, "n": len(raw)//2}) + "\n")
sys.stdout.flush()
sys.stdout.buffer.write(raw)
'''


def far_capture(t_start, seconds):
    """start the laptop's capture at a named GPS instant and bring the samples back."""
    try:
        # BASE64, NOT json.dumps. The first version shipped the far-side script as
        # f'python3 -c {json.dumps(FAR)}' -- and json.dumps escapes the script's newlines as the
        # two characters backslash-n, which a double-quoted shell string passes through verbatim,
        # so python -c received backslash-n in its source and died before printing anything. The
        # symptom was 'ValueError: subsection not found' here, from looking for a newline in empty
        # output: an error about MY parsing, three layers away from the quoting that caused it.
        # Base64 has no characters any shell will touch.
        import base64
        b64 = base64.b64encode(FAR.encode()).decode()
        p = subprocess.run(['ssh', '-o', 'ConnectTimeout=10', LAPTOP_SSH,
                            f'python3 -c "import base64;exec(base64.b64decode(\'{b64}\'))" '
                            f'{t_start:.6f} {seconds:.1f}'],
                           capture_output=True, timeout=seconds + 60)
        if b'\n' not in p.stdout:
            return None, ('far side printed nothing. stderr: '
                          + (p.stderr.decode(errors='replace')[:300] or '(empty)'))
        nl = p.stdout.index(b'\n')
        meta = json.loads(p.stdout[:nl])
        x = np.frombuffer(p.stdout[nl + 1:], dtype='<i2').astype(np.float64) / 32768.0
        if len(x) < SR:
            return None, f'far side returned {len(x)} frames'
        return {'x': x, **meta}, None
    except Exception as e:
        return None, f'{type(e).__name__}: {e}'


def near_capture(t_start, seconds, mac_to_gps):
    """the Mac's capture, started so that it lands on the same GPS instant."""
    import soundcard as sc
    mic = next((m for m in sc.all_microphones(include_loopback=False)
                if 'usb audio device' in m.name.lower()), None)
    if mic is None:
        return None, 'no USB audio card'
    if not _hold_card(timeout=60):
        return None, 'card busy'
    try:
        target_mac = t_start - mac_to_gps        # the Mac clock reading that IS t_start on GPS
        while time.time() < target_mac - 0.02:
            time.sleep(0.005)
        with mic.recorder(samplerate=int(SR), channels=1) as r:
            t0 = time.time()
            x = np.asarray(r.record(numframes=int(SR * seconds))).ravel()
            t1 = time.time()
    except Exception as e:
        return None, f'{type(e).__name__}: {e}'
    finally:
        _release_card()
    return {'x': x, 't0': t0 + mac_to_gps, 't1': t1 + mac_to_gps, 'n': len(x)}, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--trials', type=int, default=6)
    ap.add_argument('--seconds', type=float, default=8.0)
    a = ap.parse_args()
    print('  HARMONIZE2 -- the Mac and the laptop on one grid, no network in the measurement')
    print(f'  read {time.strftime("%H:%M:%S %Z, %-d %b %Y")}\n')

    # the wire, for the coarse offset and for scheduling
    c = calib.two_way(LAPTOP_UDP, 150)
    if c is None:
        print('  LA NADA -- the UDP echo did not answer, so there is no coarse reading and no')
        print('  way to say which cycle. The harmonic alone is ambiguous mod 8.3333 ms.')
        return 1
    mac_to_gps = c['offset_s']
    print(f'  THE WIRE   mac is behind by {mac_to_gps*1e3:+.3f} ms, bound +-'
          f'{c["asym_bound_s"]*1e6:.1f} us  ({c["trials"]} packets)')
    print(f'  ambiguity  phase repeats every {CYCLE_MS:.4f} ms, half cycle {CYCLE_MS/2:.4f} ms')
    ok_amb = c['asym_bound_s'] * 1e3 < CYCLE_MS / 2
    print(f'  the coarse bound is ' + ('INSIDE' if ok_amb else 'OUTSIDE') +
          ' half a cycle, so the wire can' + ('' if ok_amb else 'NOT') + ' pick the cycle\n')

    print(f"  {'#':>3} {'mac Hz':>11} {'snr':>5} {'lap Hz':>11} {'snr':>5} "
          f"{'start err ms':>13} {'dphase ms':>11}")
    rows = []
    for i in range(a.trials):
        T = time.time() + mac_to_gps + LEAD_S         # a GPS instant, LEAD_S from now
        import threading
        box = {}

        def _far():
            box['far'] = far_capture(T, a.seconds)

        th = threading.Thread(target=_far)
        th.start()
        near, nerr = near_capture(T, a.seconds, mac_to_gps)
        th.join()
        far, ferr = box.get('far', (None, 'far thread produced nothing'))
        if near is None or far is None:
            # LABEL THE SIDE THAT ACTUALLY FAILED. The first version printed "near={nerr}",
            # which on a successful near capture prints None and reads exactly like "near is
            # None" -- so a far-side failure looked like both sides failing.
            which = []
            if near is None:
                which.append(f'NEAR failed: {nerr}')
            if far is None:
                which.append(f'FAR failed: {ferr}')
            print(f'  {i+1:>3}  ' + ';  '.join(which))
            continue
        fm = fit(near['x'])
        fl = fit(far['x'])
        # THE START ERROR IS CARRIED, NOT ASSUMED ZERO. Both sides report the start they actually
        # achieved, on the GPS reference, and the difference rotates the phase by exactly
        # 2.pi.f.dt -- so it is removed rather than hoped away.
        dstart = far['t0'] - near['t0']
        dphase = wrap(fm['phase'] - fl['phase'] - 2 * math.pi * LINE * dstart)
        rows.append({'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
                     'mac': {k: fm[k] for k in ('hz', 'phase', 'snr')},
                     'lap': {k: fl[k] for k in ('hz', 'phase', 'snr')},
                     'dstart_s': dstart, 'dphase_rad': dphase,
                     'dphase_ms': dphase / (2 * math.pi) * CYCLE_MS,
                     'mac_to_gps_s': mac_to_gps})
        print(f"  {i+1:>3} {fm['hz']:>11.5f} {fm['snr']:>5.1f} {fl['hz']:>11.5f} {fl['snr']:>5.1f} "
              f"{dstart*1e3:>13.3f} {rows[-1]['dphase_ms']:>+11.4f}")

    good = [r for r in rows if min(r['mac']['snr'], r['lap']['snr']) >= 3]
    print(f'\n  {len(good)} of {a.trials} trials usable (both snr >= 3)')
    if len(good) < 3:
        print('  fewer than 3: no circular reading.')
        return 1
    ph = [r['dphase_rad'] for r in good]
    d = [r['dphase_ms'] for r in good]
    n = len(ph)
    C = sum(math.cos(x) for x in ph) / n
    S = sum(math.sin(x) for x in ph) / n
    R = math.hypot(C, S)
    ray = 2 * n * R * R
    p_unif = math.exp(-ray / 2) if ray < 700 else 0.0
    R_none = math.sqrt(math.pi) / (2 * math.sqrt(n))
    mean_ms = math.atan2(S, C) / (2 * math.pi) * CYCLE_MS
    uni_sd = CYCLE_MS / math.sqrt(12)
    sd = st.stdev(d) if n > 1 else 0.0
    print(f'\n  THE NONE IS UNIFORM, NOT ZERO -- two unrelated phases differ uniformly on the cycle.')
    print(f'    uniform none      sd {uni_sd:.4f} ms,  R {R_none:.4f}')
    print(f'    measured          sd {sd:.4f} ms,  R {R:.4f}')
    print(f'    Rayleigh 2nR^2    {ray:.2f}  -> uniform reaches it {100*p_unif:.3g}% of the time')
    print(f'    circular mean     {mean_ms:+.4f} ms of the 120 Hz cycle')
    # FOUR READINGS, NOT TWO
    if R < R_none * 1.5:
        v = ('UNIFORM -- the two machines show no shared phase. Either the captures did not overlap '
             'or they are not reading one grid.')
    elif p_unif > 0.05:
        v = (f'ABIERTO -- R {R:.3f} against a none of {R_none:.3f}, uniform reaches it '
             f'{100*p_unif:.1f}% of the time. Not separable at {n} trials.')
    elif R > 0.9:
        v = (f'LOCKED -- R {R:.3f}. The grid is shared and the comparison is real; the circular '
             f'mean is the clock offset modulo the cycle, and the wire says which cycle.')
    else:
        v = (f'PARTIAL -- R {R:.3f}: separable from uniform ({100*p_unif:.3g}%) and far from '
             f'locked. A shared grid IS in here together with per-machine phase noise, and this '
             f'reading does not say which dominates.')
    print(f'    => {v}')
    if R >= R_none * 1.5 and p_unif <= 0.05:
        # the fine offset: combine the wire's cycle with the harmonic's fraction
        coarse_ms = mac_to_gps * 1e3
        k = round((coarse_ms - mean_ms) / CYCLE_MS)
        fine_ms = mean_ms + k * CYCLE_MS
        print(f'\n  COMBINED. wire {coarse_ms:+.3f} ms picks cycle k = {k}; harmonic fraction '
              f'{mean_ms:+.4f} ms')
        print(f'    mac behind gps = {fine_ms:+.4f} ms   (vs {coarse_ms:+.3f} ms from the wire '
              f'alone)')
        print(f'    they differ by {abs(fine_ms-coarse_ms):.4f} ms, against the wire\'s own bound '
              f'of {c["asym_bound_s"]*1e3:.4f} ms')
        print(f'    -> ' + ('consistent: the harmonic refines the wire without contradicting it'
                            if abs(fine_ms - coarse_ms) <= c['asym_bound_s'] * 1e3 else
                            'INCONSISTENT: the harmonic lands outside the wire\'s bound, so one of '
                            'them is wrong and the cycle choice cannot be trusted'))
    try:
        with open(LOG, 'a') as f:
            f.write(json.dumps({'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'n': n,
                                'R': R, 'R_none': R_none, 'rayleigh': ray, 'p_uniform': p_unif,
                                'circ_mean_ms': mean_ms, 'sd_ms': sd, 'uniform_sd_ms': uni_sd,
                                'mac_to_gps_s': mac_to_gps,
                                'wire_bound_s': c['asym_bound_s'],
                                'rows': good}) + '\n')
    except Exception:
        pass
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
