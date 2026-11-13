#!/usr/bin/env python3
"""harmonize3.py -- BOTH LEGS HARDWARE-DATED. (Bones, 9 Oct 2026.)

harmonize2 read the grid at two machines and got the FREQUENCY right (mac - laptop +0.003263 Hz
against a none of 0.008828, 3.7x tighter -- one grid, no network in it) and the PHASE as UNIFORM:
R 0.4974 against a none of 0.3618, Rayleigh 2.97, uniform reaching it 22.7 % of the time.

THE REASON WAS MEASURED, NOT GUESSED: the capture-start difference ran -111.0 to -80.8 ms across six
trials, a spread of 30.3 ms = 3.63 cycles at 120 Hz, and correcting it from the clocks needs the very
offset being measured. Circular, not merely imprecise.

SO BOTH ENDS NOW ASK THE HARDWARE WHEN THE FIRST SAMPLE HAPPENED, and neither dates a capture by
when a program returned:

    MAC      sounddevice/PortAudio time_info.inputBufferAdcTime, mapped to wall time by bracketed
             reads. ADC-to-callback held to sd 19.1 us over 24 opens.
    LAPTOP   ctypes straight at libasound: snd_pcm_status_get_trigger_htstamp, the instant the
             stream was triggered, mapped CLOCK_MONOTONIC -> CLOCK_REALTIME the same bracketed way
             (bound 238.4 ns, the clock's own measured resolution). Trigger minus a tightly
             bracketed naive stamp: sd 3.92 us over 12 opens.
    sounddevice is not usable on the laptop -- Pa_Initialize dies on "PulseAudio_Initialize: Can't
    connect to server" with no user audio session over ssh, and there is no gcc or libasound2-dev
    for a C helper. ctypes needs neither.

AND THE POINT IS NOT TO START TOGETHER. The far side missed its requested instant by -1.631 ms in
the smoke test and it does not matter: the start is KNOWN to 238 ns, so it is subtracted. Starting
precisely is hard; knowing when you started is cheap.

WHAT IS BEING TESTED. Each side's line fit gives the phase at ITS first sample; that sample has a
hardware time on that machine's own clock; the two clocks differ by the offset the UDP two-way
measures. Extrapolate both phases to one common instant and the leftover is the part the clocks and
the stamps cannot explain. If the apparatus is sound the leftover CONCENTRATES.

THE NONE IS UNIFORM, NOT ZERO. Two unrelated phases differ uniformly over the 8.3333 ms cycle --
sd 2.4056 ms, resultant R near sqrt(pi)/(2.sqrt(n)). A difference near zero is not the null and never
was. Four readings, never two: UNIFORM / ABIERTO / PARTIAL / LOCKED.

    python3 harmonize3.py --trials 8 --seconds 6
"""
import argparse
import base64
import json
import math
import os
import statistics as st
import subprocess
import sys
import threading
import time

import numpy as np

W = os.path.expanduser('~/bones-forge/watch/')
sys.path.insert(0, W)
import calib                                                        # noqa: E402
from audio_clock import _hold_card, _release_card                   # noqa: E402
from harmonize import fit, wrap, CYCLE_MS, LINE, SR                  # noqa: E402

LOG = os.path.join(W, 'harmonize3.jsonl')
LAPTOP_UDP = '192.168.8.123'
LAPTOP_SSH = 'laptop'
FAR = '/tmp/far_stamped.py'
DEVICE_HINT = 'USB Audio Device'


def map_stream_to_wall(stream, n=40):
    """PortAudio stream clock -> wall clock, bracketed, fastest decile, floored at the clock's own
    measured resolution. A bound of 0.0 is the instrument running out of digits, not a bound."""
    rs = []
    for _ in range(n):
        w0 = time.time()
        s = stream.time
        w1 = time.time()
        rs.append({'gap': w1 - w0, 'off': (w0 + w1) / 2.0 - s})
    rs.sort(key=lambda r: r['gap'])
    keep = max(3, len(rs) // 10)
    offs = [r['off'] for r in rs[:keep]]
    res, prev = None, time.time()
    for _ in range(20000):
        t = time.time()
        d = t - prev
        if d > 0 and (res is None or d < res):
            res = d
        prev = t
    gaps = sorted(r['gap'] for r in rs)
    p5 = gaps[max(0, int(0.05 * len(gaps)) - 1)]
    return {'off': st.mean(offs),
            'scatter': st.stdev(offs) / math.sqrt(len(offs)) if len(offs) > 1 else 0.0,
            'bound': max(p5 / 2.0, res or 0.0)}


def near(t_start_gps, seconds, mac_to_gps):
    """Mac capture, first-sample time from the ADC stamp, returned on the GPS reference."""
    import sounddevice as sd
    dev = next((i for i, d in enumerate(sd.query_devices())
                if d['max_input_channels'] > 0 and DEVICE_HINT.lower() in d['name'].lower()), None)
    if dev is None:
        return None, f'no input matching {DEVICE_HINT!r}'
    if not _hold_card(timeout=90):
        return None, 'card busy'
    box = {'adc': None, 'chunks': []}

    def cb(indata, frames, time_info, status):
        if box['adc'] is None:
            box['adc'] = time_info.inputBufferAdcTime
        box['chunks'].append(indata.copy())
    try:
        target_mac = t_start_gps - mac_to_gps
        with sd.InputStream(device=dev, channels=1, samplerate=int(SR), callback=cb,
                            dtype='float32') as stream:
            mp = map_stream_to_wall(stream)
            while time.time() < target_mac + seconds + 0.3:
                time.sleep(0.005)
    except Exception as e:
        return None, f'{type(e).__name__}: {e}'
    finally:
        _release_card()
    if box['adc'] is None or not box['chunks']:
        return None, 'no callback fired'
    x = np.concatenate([c.ravel() for c in box['chunks']])
    # the first sample's time, on the GPS reference: ADC stamp -> mac wall -> gps
    t0_gps = box['adc'] + mp['off'] + mac_to_gps
    return {'x': x, 't0_gps': t0_gps, 'map_bound': mp['bound'], 'map_scatter': mp['scatter'],
            'n': len(x)}, None


def far(t_start_gps, seconds):
    """laptop capture. Its clock IS the GPS reference (chrony + the Leo Bodnar GPSDO), so the
    trigger htstamp needs no conversion -- which is exactly why the GPSDO lives on that machine."""
    try:
        p = subprocess.run(['ssh', '-o', 'ConnectTimeout=10', LAPTOP_SSH,
                            f'python3 {FAR} {t_start_gps:.6f} {seconds:.1f}'],
                           capture_output=True, timeout=seconds + 70)
        if b'\n' not in p.stdout:
            return None, ('far side printed nothing. stderr: '
                          + (p.stderr.decode(errors='replace')[:300] or '(empty)'))
        nl = p.stdout.index(b'\n')
        meta = json.loads(p.stdout[:nl])
        raw = p.stdout[nl + 1:]
        x = np.frombuffer(raw, dtype='<i2').astype(np.float64) / 32768.0
        if len(x) < SR // 2:
            return None, f'far returned {len(x)} frames'
        return {'x': x, 't0_gps': meta['t0'], 'map_bound': meta['map']['bound'],
                'map_scatter': meta['map']['scatter'], 'n': len(x)}, None
    except Exception as e:
        return None, f'{type(e).__name__}: {e}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--trials', type=int, default=8)
    ap.add_argument('--seconds', type=float, default=6.0)
    a = ap.parse_args()
    print('  HARMONIZE3 -- both legs hardware-dated, one grid, no network in the measurement')
    print(f'  read {time.strftime("%H:%M:%S %Z, %-d %b %Y")}\n')
    c = calib.two_way(LAPTOP_UDP, 150)
    if c is None:
        print('  LA NADA -- the UDP echo did not answer, so no coarse offset and no cycle choice.')
        return 1
    mac_to_gps = c['offset_s']
    print(f'  THE WIRE   mac behind by {mac_to_gps*1e3:+.3f} ms, bound '
          f'+-{c["asym_bound_s"]*1e6:.1f} us ({c["trials"]} packets)')
    print(f'  ambiguity  cycle {CYCLE_MS:.4f} ms, half {CYCLE_MS/2:.4f} ms -- the wire is '
          + ('inside' if c['asym_bound_s'] * 1e3 < CYCLE_MS / 2 else 'OUTSIDE') + ' half a cycle\n')
    print(f"  {'#':>3} {'mac snr':>8} {'lap snr':>8} {'dt0 ms':>10} {'resid ms':>10}")
    rows = []
    for i in range(a.trials):
        T = time.time() + mac_to_gps + 10.0
        box = {}

        def _f():
            box['far'] = far(T, a.seconds)
        th = threading.Thread(target=_f)
        th.start()
        n, nerr = near(T, a.seconds, mac_to_gps)
        th.join()
        f, ferr = box.get('far', (None, 'far thread produced nothing'))
        if n is None or f is None:
            which = []
            if n is None:
                which.append(f'NEAR: {nerr}')
            if f is None:
                which.append(f'FAR: {ferr}')
            print(f'  {i+1:>3}  ' + ';  '.join(which))
            continue
        fm, fl = fit(n['x']), fit(f['x'])
        if min(fm['snr'], fl['snr']) < 3:
            print(f"  {i+1:>3} {fm['snr']:>8.1f} {fl['snr']:>8.1f}  snr under 3, dropped")
            continue
        # TRIM TO A COMMON WINDOW -- do not extrapolate. (Fixed 9 Oct 18:24.)
        #
        # The first version extrapolated each phase back to a reference instant using its own
        # hardware t0, and read UNIFORM: R 0.3410 against a none of 0.3133, uniform reaching it
        # 39.5 % of the time. The stamps were not the problem -- mac map bound 0.715 us, laptop
        # 238.4 ns -- the EXTRAPOLATION DISTANCE was. dt0 came out -9.93 SECONDS, because the Mac
        # opens its stream at once while the laptop waits for the named instant, so the Mac's first
        # sample sits a whole lead-time earlier. Extrapolating 9.93 s is 0.78 of the 12.73 s
        # coherence time measured tonight, and across most of a tau_c the grid's own wander has
        # already moved the phase. I was carrying the signal across the very interval the
        # linewidth says it stops being predictable.
        #
        # The hardware stamps make the right move available: each t0 says exactly which sample is
        # the reference instant, so BOTH captures are SLICED to start there and the fits cover the
        # same wall clock window. No extrapolation at all, which is strictly better than a short one.
        ref = max(n['t0_gps'], f['t0_gps'])
        im = int(round((ref - n['t0_gps']) * SR))
        il = int(round((ref - f['t0_gps']) * SR))
        xm, xl = n['x'][im:], f['x'][il:]
        keep = min(len(xm), len(xl))
        if keep < int(SR * 1.0):
            print(f'  {i+1:>3}  overlap only {keep/SR:.2f} s after trimming, dropped')
            continue
        fm, fl = fit(xm[:keep]), fit(xl[:keep])
        if min(fm['snr'], fl['snr']) < 3:
            print(f"  {i+1:>3} {fm['snr']:>8.1f} {fl['snr']:>8.1f}  snr under 3 after trim, dropped")
            continue
        # the residual sub-sample offsets, which trimming cannot remove, are carried as a rotation
        rm = (ref - n['t0_gps']) * SR - im
        rl = (ref - f['t0_gps']) * SR - il
        pm = fm['phase'] + 2 * math.pi * LINE * (rm / SR)
        pl = fl['phase'] + 2 * math.pi * LINE * (rl / SR)
        resid = wrap(pm - pl)
        dt0 = (n['t0_gps'] - f['t0_gps']) * 1e3
        print(f'      trimmed: mac +{im} samples, laptop +{il}, overlap {keep/SR:.2f} s')
        rows.append({'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
                     'mac': {k: fm[k] for k in ('hz', 'phase', 'snr')},
                     'lap': {k: fl[k] for k in ('hz', 'phase', 'snr')},
                     'mac_t0_gps': n['t0_gps'], 'lap_t0_gps': f['t0_gps'],
                     'mac_map_bound': n['map_bound'], 'lap_map_bound': f['map_bound'],
                     'dt0_ms': dt0, 'resid_rad': resid,
                     'resid_ms': resid / (2 * math.pi) * CYCLE_MS,
                     'mac_to_gps_s': mac_to_gps})
        print(f"  {i+1:>3} {fm['snr']:>8.1f} {fl['snr']:>8.1f} {dt0:>10.3f} "
              f"{rows[-1]['resid_ms']:>+10.4f}")
    if len(rows) < 3:
        print('\n  fewer than 3 usable trials: no circular reading.')
        return 1
    ph = [r['resid_rad'] for r in rows]
    ms = [r['resid_ms'] for r in rows]
    n_t = len(ph)
    C = sum(math.cos(x) for x in ph) / n_t
    S = sum(math.sin(x) for x in ph) / n_t
    R = math.hypot(C, S)
    ray = 2 * n_t * R * R
    p_unif = math.exp(-ray / 2) if ray < 700 else 0.0
    R_none = math.sqrt(math.pi) / (2 * math.sqrt(n_t))
    uni_sd = CYCLE_MS / math.sqrt(12)
    sd = st.stdev(ms) if n_t > 1 else 0.0
    print(f'\n  THE STAMPS: mac map bound {st.mean([r["mac_map_bound"] for r in rows])*1e6:.3f} us, '
          f'laptop {st.mean([r["lap_map_bound"] for r in rows])*1e9:.1f} ns')
    print(f'  THE NONE IS UNIFORM: sd {uni_sd:.4f} ms, R {R_none:.4f}')
    print(f'  MEASURED           : sd {sd:.4f} ms, R {R:.4f}')
    print(f'  Rayleigh 2nR^2 {ray:.2f}  -> uniform reaches it {100*p_unif:.3g}% of the time')
    if R < R_none * 1.5:
        v = 'UNIFORM -- still no shared phase. The stamps did not fix it and something else is wrong.'
    elif p_unif > 0.05:
        v = (f'ABIERTO -- R {R:.3f} against a none of {R_none:.3f}; uniform reaches it '
             f'{100*p_unif:.1f}% of the time at {n_t} trials.')
    elif R > 0.9:
        v = (f'LOCKED -- R {R:.3f}. Two machines on one grid with hardware-dated samples, and the '
             f'leftover phase concentrates. harmonize2 had R 0.4974 at 22.7% with software stamps.')
    else:
        v = (f'PARTIAL -- R {R:.3f}, separable from uniform at {100*p_unif:.3g}% and short of '
             f'locked. Better than the software stamps and not yet clean.')
    print(f'  => {v}')
    try:
        with open(LOG, 'a') as f2:
            f2.write(json.dumps({'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'n': n_t, 'R': R,
                                 'R_none': R_none, 'rayleigh': ray, 'p_uniform': p_unif,
                                 'sd_ms': sd, 'uniform_sd_ms': uni_sd,
                                 'wire_bound_s': c['asym_bound_s'], 'rows': rows}) + '\n')
    except Exception:
        pass
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
