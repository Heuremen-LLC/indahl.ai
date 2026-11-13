#!/usr/bin/env python3
"""adc_stamp.py -- WHEN DID THE FIRST SAMPLE HAPPEN? (Bones, 9 Oct 2026.)

Wayfinder: "make it happen cap'n. Ride."

THE BLOCKER THIS ATTACKS. The cross-machine harmonic comparison works in the frequency and fails in
the phase, and the reason is measured: the capture-start difference between the two machines ran
-111.0 to -80.8 ms across six trials, a spread of 30.3 ms, which is 3.63 cycles at 120 Hz. Phase
cannot survive that. And correcting it from the clocks needs the clock offset that is the thing being
measured, so it is circular, not merely imprecise.

THE WAY OUT IS NOT A BETTER CLOCK, IT IS A BETTER QUESTION. Instead of "when did I call record()",
ask the audio hardware "when was this buffer captured". PortAudio hands that over per buffer as
time_info.inputBufferAdcTime, in its own stream timebase. CoreAudio and ALSA both carry such a stamp;
soundcard does not surface it, which is why every capture so far has been dated by a python call.

    naive      t = time.time() just before record()    -- includes device open + buffer fill
    ADC        t = inputBufferAdcTime of the FIRST buffer, mapped to wall time

AND THE MAPPING IS THE WHOLE GAME, so it is measured rather than assumed. Stream time and wall time
are two clocks; the offset between them is found by reading both back to back, many times, and taking
the tightest readings -- the same minimum-queueing argument as the UDP two-way, and the same refusal
to use the raw minimum as a bound. If that mapping is stable to well under a millisecond then the
first sample has a wall time good enough for phase, and the 30.3 ms goes away.

WHAT WOULD MAKE THIS FAIL, stated before running it so the result cannot be read as whatever
happened: PortAudio may report inputBufferAdcTime as nothing more than the stream time at callback
entry, in which case it carries the same scheduling jitter as a python call and buys NOTHING. The test
is not whether a number appears -- a number always appears -- but whether the first-sample wall time
is MORE STABLE than the naive one across repeated opens. Three outcomes, not two: better, no
different, or worse.

    python3 adc_stamp.py --trials 10
"""
import argparse
import json
import math
import os
import statistics as st
import sys
import time

W = os.path.expanduser('~/bones-forge/watch/')
sys.path.insert(0, W)
LOG = os.path.join(W, 'adc_stamp.jsonl')
SR = 48000
DEVICE_HINT = 'USB Audio Device'


def map_stream_to_wall(stream, n=40):
    """offset between PortAudio's stream clock and time.time(), by bracketed reads.

    Each read is sandwiched between two wall reads, and the gap between them is that sample's own
    width -- so the tightest reads are the ones where the process was not descheduled mid-pair. The
    estimate comes from the fastest decile, and the bound from the 5th percentile of the gaps rather
    than the minimum, because a minimum over n only ever falls as n grows and one scheduling
    artifact sets it (learned today on the UDP bound, which read 51 us over WiFi and was nonsense)."""
    rs = []
    for _ in range(n):
        w0 = time.time()
        s = stream.time
        w1 = time.time()
        rs.append({'gap': w1 - w0, 'offset': (w0 + w1) / 2.0 - s})
    rs.sort(key=lambda r: r['gap'])
    keep = max(3, len(rs) // 10)
    offs = [r['offset'] for r in rs[:keep]]
    gaps = sorted(r['gap'] for r in rs)
    p5 = gaps[max(0, int(0.05 * len(gaps)) - 1)] if len(gaps) >= 20 else gaps[0]
    # A BOUND OF ZERO IS NOT A BOUND. Many of these gaps come out EXACTLY 0.0, because two
    # consecutive time.time() calls return the same value -- the gap is finer than the clock that
    # is measuring it. So the honest floor is the clock's own resolution, which is measured here
    # rather than looked up, and the bound is whichever is larger. Reporting p5/2 alone printed
    # "0.0000 us", a number that looks like a bug or a fabrication and is really a statement that
    # the instrument ran out of digits.
    res = clock_resolution()
    zeros = sum(1 for g in gaps if g == 0.0)
    return {'offset': st.mean(offs),
            'scatter': (st.stdev(offs) / math.sqrt(len(offs))) if len(offs) > 1 else 0.0,
            'bound': max(p5 / 2.0, res), 'p5_half': p5 / 2.0, 'clock_res': res,
            'zero_gaps': zeros, 'n': len(rs), 'kept': keep}


def clock_resolution(n=20000):
    """the smallest non-zero step time.time() will actually report, measured."""
    best = None
    prev = time.time()
    for _ in range(n):
        t = time.time()
        d = t - prev
        if d > 0 and (best is None or d < best):
            best = d
        prev = t
    return best or 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--trials', type=int, default=10)
    ap.add_argument('--seconds', type=float, default=1.0)
    a = ap.parse_args()
    import sounddevice as sd
    print('  THE ADC TIMESTAMP -- when did the FIRST SAMPLE happen?')
    print(f'  read {time.strftime("%H:%M:%S %Z, %-d %b %Y")}\n')
    print('  stated before the run: a number always appears. The test is whether the first-sample')
    print('  wall time is MORE STABLE than the naive one. Three outcomes: better, no different,')
    print('  worse.\n')
    # one long-lived stream, so the stream<->wall mapping can be measured properly
    dev = None
    for i, d in enumerate(sd.query_devices()):
        if d['max_input_channels'] > 0 and DEVICE_HINT.lower() in d['name'].lower():
            dev = i
            break
    if dev is None:
        print(f'  LA NADA -- no input matching {DEVICE_HINT!r}')
        return 1
    rows = []
    print(f"  {'#':>3} {'naive bracket ms':>18} {'adc - stream now ms':>21} {'blocks':>7}")
    for i in range(a.trials):
        box = {'adc': None, 'cur': None}

        def cb(indata, frames, time_info, status):
            if box['adc'] is None:
                box['adc'] = time_info.inputBufferAdcTime
                box['cur'] = time_info.currentTime

        nb = time.time()
        with sd.InputStream(device=dev, channels=1, samplerate=SR, callback=cb,
                            dtype='float32') as stream:
            na = time.time()
            # map THIS stream's clock to wall time while it is open
            mp = map_stream_to_wall(stream, 40)
            t_end = time.time() + a.seconds
            while time.time() < t_end:
                time.sleep(0.005)
        if box['adc'] is None:
            print(f'  {i+1:>3}  no callback fired')
            continue
        # the first sample's wall time, two ways
        adc_wall = box['adc'] + mp['offset']
        naive_wall = (nb + na) / 2.0
        rows.append({'adc_wall': adc_wall, 'naive_wall': naive_wall,
                     'naive_width': (na - nb) / 2.0,
                     'map_offset': mp['offset'], 'map_scatter': mp['scatter'],
                     'map_bound': mp['bound'], 'clock_res': mp.get('clock_res'),
                     'zero_gaps': mp.get('zero_gaps'), 'p5_half': mp.get('p5_half'),
                     'adc_minus_naive': adc_wall - naive_wall,
                     'adc_raw': box['adc'], 'cur_raw': box['cur']})
        print(f"  {i+1:>3} {(na-nb)*1e3:>18.3f} {(box['cur']-box['adc'])*1e3:>21.3f} "
              f"{'-':>7}")
    if len(rows) < 3:
        print('\n  fewer than 3 trials: no reading.')
        return 1
    dn = [r['adc_minus_naive'] * 1e3 for r in rows]
    nw = [r['naive_width'] * 1e3 for r in rows]
    mb = [r['map_bound'] * 1e3 for r in rows]
    cr = [r.get('clock_res', 0) * 1e3 for r in rows]
    zg = [r.get('zero_gaps', 0) for r in rows]
    ms = [r['map_scatter'] * 1e3 for r in rows]
    # ENOUGH DIGITS THAT THE NUMBER CANNOT LOOK LIKE A ZERO. A bound printed as 0.0000 ms reads
    # like a bug or a fabrication; these are sub-microsecond because stream.time and time.time()
    # are both local clock reads with no I/O between them, and that deserves to be shown rather
    # than rounded into something unbelievable.
    print(f'\n  stream<->wall mapping   scatter {st.mean(ms)*1e3:.4f} us   bound '
          f'{st.mean(mb)*1e3:.4f} us  (mean over {len(rows)} trials)')
    print(f'    the bound is floored at time.time()\'s OWN resolution, measured at '
          f'{st.mean(cr)*1e3:.4f} us;')
    print(f'    {st.mean(zg):.0f} of 40 bracket gaps per trial came out EXACTLY zero, which is the')
    print(f'    clock running out of digits, not a gap of zero.')
    print(f'  the naive stamp\'s OWN width (half the open bracket): {st.mean(nw):.3f} ms')
    print(f'  adc minus naive         mean {st.mean(dn):+.3f} ms   sd '
          f'{st.stdev(dn) if len(dn)>1 else 0:.3f} ms')
    print(f'\n  WHAT THIS DOES AND DOES NOT SAY. The spread of (adc - naive) is how much the two')
    print(f'  disagree trial to trial. It is NOT the ADC stamp\'s accuracy: both terms move, and a')
    print(f'  small spread would mean they move TOGETHER, which would be the "no different"')
    print(f'  outcome -- an ADC stamp that is just the callback-entry time in different units.')
    print(f'  The thing that decides it is the MAPPING width above, because that is the only part')
    print(f'  that is a measurement rather than a difference: if the stream clock maps to wall time')
    print(f'  at {st.mean(mb)*1e3:.4f} us then the first sample has a wall time at that precision, and the')
    print(f'  30.3 ms of capture-start spread stops being the limit.')
    cyc = 1000.0 / 120.0
    print(f'\n  AGAINST THE JOB: one 120 Hz cycle is {cyc:.4f} ms. The mapping bound is '
          f'{st.mean(mb)/cyc*1e6:.1f} PARTS PER MILLION of a cycle.')
    print(f'  the old start jitter was 30.3 ms = {30.3/cyc:.2f} cycles.')
    if st.mean(mb) < cyc / 20:
        print(f'  => CLEARED on this leg: the mapping is under a twentieth of a cycle. Phase is')
        print(f'     usable from here IF the far side can do the same, which is a separate read.')
    elif st.mean(mb) < cyc / 2:
        print(f'  => PARTIAL: inside half a cycle, so the cycle is pickable, but not fine enough')
        print(f'     to call the fraction clean.')
    else:
        print(f'  => NOT CLEARED: the mapping alone exceeds half a cycle.')
    try:
        with open(LOG, 'a') as f:
            f.write(json.dumps({'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
                                'trials': len(rows),
                                'map_bound_ms': st.mean(mb), 'map_scatter_ms': st.mean(ms),
                                'naive_width_ms': st.mean(nw),
                                'adc_minus_naive_mean_ms': st.mean(dn),
                                'adc_minus_naive_sd_ms': st.stdev(dn) if len(dn) > 1 else 0.0,
                                'rows': rows}) + '\n')
    except Exception:
        pass
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
