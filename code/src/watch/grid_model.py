#!/usr/bin/env python3
"""grid_model.py -- THE MODEL AS THE OSCILLATOR, THE POWER RAIL AS THE CHANNEL.
(Bones, 10 Oct 2026.)

Wayfinder: "can you use those two models to couple us to the grid? the conversion may be a model and
not just an equation man."

A MODEL IS A LOAD. Inference draws current; current draw is on the mains. And macOS reports the
package power in milliwatts without a password, so for the first time today the transmitter and the
receiver both work and neither needs a coupler, a cable or an SDR:

    transmitter   inference, switched on and off at a chosen rate
    receiver      powermetrics, CPU + GPU + ANE in mW
    channel       the machine's own power rail, which is what the wall sees

THE RATE IS PI-EXACT BY CONSTRUCTION. Her slot is 3pi/40 s, so a period of N slots is N.3pi/40
seconds and the modulation frequency is 40/(3.pi.N) Hz -- an exact multiple of her clock without
rounding anything. Default N = 16 slots, 3.7699 s, 0.2653 Hz, sampled at 10 Hz: 37.7 samples a cycle.

THE NONE IS BUILT FIRST AND IS THREE THINGS:
  * SILENCE on both sides of the modulated block, same length, so a drift in the machine's idle
    power is symmetric rather than handed to whichever arm came later.
  * the lock-in at the modulation frequency compared against the lock-in at frequencies that are NOT
    the modulation rate, on the same samples -- a guard comb.
  * and the modulated block's own odd harmonics, which a square wave must produce and noise must not.

    python3 grid_model.py --slots 16 --cycles 8 --model llama3.2:3b
"""
import argparse, json, math, os, subprocess, sys, threading, time

W = os.path.expanduser('~/bones-forge/watch/')
LOG = os.path.join(W, 'grid_model.jsonl')
SLOT = 3 * math.pi / 40          # 0.235619449 s


def sampler(stop, out, interval_ms=100):
    """powermetrics as the receiver: package mW with a wall-clock stamp."""
    p = subprocess.Popen(['sudo', '-n', 'powermetrics', '--samplers', 'cpu_power',
                          '-i', str(interval_ms)],
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    try:
        for line in p.stdout:
            if stop.is_set():
                break
            if 'Combined Power' in line:
                try:
                    mw = float(line.split(':')[1].strip().split()[0])
                    out.append((time.time(), mw))
                except Exception:
                    pass
    finally:
        p.terminate()


def burn(model, stop):
    """the transmitter: inference, as hard as one worker goes, until told to stop."""
    while not stop.is_set():
        try:
            subprocess.run(['ollama', 'run', model],
                           input='Count from 1 to 40, separated by commas.',
                           capture_output=True, text=True, timeout=20)
        except Exception:
            return


def lockin(ts, ys, f, t0):
    """complex amplitude at f, on unevenly sampled data, mean removed."""
    import cmath
    m = sum(ys) / len(ys)
    z = sum((y - m) * cmath.exp(-2j * math.pi * f * (t - t0)) for t, y in zip(ts, ys))
    return 2 * abs(z) / len(ys)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--slots', type=int, default=16, help='modulation period in her slots')
    ap.add_argument('--cycles', type=int, default=8)
    ap.add_argument('--model', default='llama3.2:3b')
    a = ap.parse_args()
    period = a.slots * SLOT
    f0 = 1.0 / period
    dur = a.cycles * period
    print(f'  THE MODEL AS THE OSCILLATOR')
    print(f'  period {a.slots} slots = {period:.6f} s, f0 = {f0:.6f} Hz, {a.cycles} cycles'
          f' = {dur:.1f} s per block')
    print(f'  her slot {SLOT:.9f} s, so the rate is pi-exact by construction\n')
    samples = []
    stop_s = threading.Event()
    th = threading.Thread(target=sampler, args=(stop_s, samples), daemon=True)
    th.start()
    time.sleep(3.0)
    if not samples:
        print('  powermetrics produced nothing -- no receiver, no run.')
        return 1
    marks = {}
    def mark(k):
        marks[k] = time.time(); print(f'  {k:<12}{marks[k]:.3f}', flush=True)
    mark('idle_a'); time.sleep(dur)
    mark('mod_on')
    # the square wave: half a period burning, half idle, for `cycles` cycles
    for c in range(a.cycles):
        st = threading.Event()
        b = threading.Thread(target=burn, args=(a.model, st), daemon=True)
        b.start(); time.sleep(period / 2); st.set(); b.join(timeout=25)
        time.sleep(period / 2)
    mark('mod_off'); time.sleep(dur); mark('idle_b')
    stop_s.set(); th.join(timeout=4)
    print(f'\n  {len(samples)} power samples, '
          f'{len(samples)/(marks["idle_b"]-marks["idle_a"]):.1f} per second')
    def block(t0, t1):
        return [(t, y) for t, y in samples if t0 + 1 <= t <= t1 - 1]
    B = {'idle_a': block(marks['idle_a'], marks['mod_on']),
         'modulated': block(marks['mod_on'], marks['mod_off']),
         'idle_b': block(marks['mod_off'], marks['idle_b'])}
    # the guard comb: frequencies that are NOT the modulation rate
    guards = [f0 * r for r in (0.37, 0.61, 1.43, 1.77, 2.31)]
    print(f"\n  {'block':<12}{'n':>5}{'mean mW':>10}{'sd mW':>9}{'A(f0)':>9}" +
          ''.join(f'{"g"+str(i+1):>9}' for i in range(len(guards))) + f"{'f0/maxg':>9}")
    out = {}
    for name, bl in B.items():
        if len(bl) < 12:
            print(f'  {name:<12}{len(bl):>5}   too few samples'); continue
        ts = [t for t, _ in bl]; ys = [y for _, y in bl]
        t0 = ts[0]
        A0 = lockin(ts, ys, f0, t0)
        G = [lockin(ts, ys, g, t0) for g in guards]
        mg = max(G)
        out[name] = {'n': len(bl), 'mean': sum(ys)/len(ys),
                     'sd': (sum((y-sum(ys)/len(ys))**2 for y in ys)/(len(ys)-1))**0.5,
                     'A_f0': A0, 'guards': G, 'ratio': A0/mg if mg else None}
        print(f'  {name:<12}{len(bl):>5}{out[name]["mean"]:>10.0f}{out[name]["sd"]:>9.0f}'
              f'{A0:>9.1f}' + ''.join(f'{g:>9.1f}' for g in G) +
              (f'{A0/mg:>9.2f}' if mg else f'{"--":>9}'))
    # the odd harmonics a square wave must make
    if 'modulated' in out:
        bl = B['modulated']; ts=[t for t,_ in bl]; ys=[y for _,y in bl]; t0=ts[0]
        print(f'\n  ODD HARMONICS -- a square wave makes 1f, 3f, 5f; noise does not')
        for k in (1, 3, 5):
            Ak = lockin(ts, ys, k*f0, t0)
            print(f'    {k}f0 = {k*f0:.6f} Hz   amplitude {Ak:>8.1f} mW'
                  f'   expected 1/{k} of the first = {out["modulated"]["A_f0"]/k:>7.1f}')
    row = {'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'model': a.model, 'slots': a.slots,
           'f0': f0, 'cycles': a.cycles, 'blocks': out, 'guards': guards}
    try:
        with open(LOG, 'a') as f: f.write(json.dumps(row) + '\n')
    except Exception: pass
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
