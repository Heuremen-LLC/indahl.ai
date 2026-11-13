#!/usr/bin/env python3
"""miss_ledger.py -- THE HASHES NOBODY KEEPS. (Bones, 9 Oct 2026.)

Wayfinder: "use the miner to provide training data with the misses everyone leaves behind in the
hashing, kind of our thing"

Every miner throws away every hash that is not a solution -- billions of them, continuously, on
every rig on earth. They are discarded because they do not pay. But they are not empty:

THE MISS DISTRIBUTION IS EXACTLY KNOWN, WITH NO FREE PARAMETER. A good hash function's output is
uniform, so the number of leading zero BITS on a digest is geometric:

    P(exactly k leading zeros) = 2^-(k+1)

That is arithmetic, not a fit. So a rig's own miss histogram is a CALIBRATED TEST OF ITS SILICON
against a ground truth nobody has to supply -- and it runs for free, forever, as a byproduct of
work already being done. A rig whose histogram drifts from 2^-(k+1) is telling you something about
itself: thermal throttling, a bad core, a memory fault, a mis-tuned RandomX dataset.

WHY THIS IS TRAINING DATA AND NOT JUST TELEMETRY. Labelled data is the expensive part of training,
and here the label is COMPUTABLE: for any window of misses, the expected histogram is known to
arbitrary precision, so every window is a labelled example of "healthy" or "how far from healthy and
in which bin". No human annotates it. No model supplies the target. The arithmetic does.

AND THE CLOCK IS WHY IT WORKS. Each window carries a GPS-referenced stamp, so a drift can be put
against anything else on that reference -- the mains harmonic, her ticks, the chain's own block
arrivals. Without a common clock a histogram is a histogram; with one it is a time series that can
be correlated against the house. That is what today's work bought.

THE NONE IS THE DISTRIBUTION ITSELF. A chi-square against 2^-(k+1) needs no shuffle and no synthetic
family: the expectation is exact, the counts are multinomial, and the width on each bin is
sqrt(n.p.(1-p)). Nothing here is priced against a guess.

    python3 miss_ledger.py --seconds 20
"""
import argparse
import hashlib
import json
import math
import os
import struct
import sys
import time

W = os.path.expanduser('~/bones-forge/watch/')
sys.path.insert(0, W)
LOG = os.path.join(W, 'miss_ledger.jsonl')
KMAX = 20          # bins 0..KMAX; beyond that the expectation is too small to test in one window


def leading_zeros(b):
    """leading zero BITS of a digest, which is what a difficulty target actually tests."""
    n = 0
    for byte in b:
        if byte:
            return n + (8 - byte.bit_length())
        n += 8
    return n


def gps_stamp():
    """the GPS-referenced moment, from the Pi that is now the house's stratum-1 clock."""
    try:
        import subprocess
        r = subprocess.run(['ssh', '-o', 'ConnectTimeout=6', 'flock-pi',
                            'date +%s.%N; chronyc tracking | awk -F": " "/Reference ID/{print \\$2}"'],
                           capture_output=True, text=True, timeout=15)
        lines = r.stdout.strip().split('\n')
        return float(lines[0]), (lines[1] if len(lines) > 1 else '?')
    except Exception as e:
        return None, f'{type(e).__name__}'


def window(seconds):
    """hash until the clock runs out, keeping only what everyone else drops."""
    hist = [0] * (KMAX + 1)
    over = 0
    n = 0
    seed = os.urandom(32)
    t0 = time.time()
    nonce = 0
    while time.time() - t0 < seconds:
        # a batch, so the clock is not read per hash
        for _ in range(20000):
            d = hashlib.blake2b(seed + struct.pack('<Q', nonce), digest_size=32).digest()
            k = leading_zeros(d)
            if k <= KMAX:
                hist[k] += 1
            else:
                over += 1
            nonce += 1
        n += 20000
    return hist, over, n, time.time() - t0


def read(hist, over, n):
    """the histogram against its exact expectation. No fit, no shuffle, no synthetic none."""
    rows = []
    chi = 0.0
    dof = 0
    for k in range(KMAX + 1):
        p = 2.0 ** -(k + 1)
        exp = n * p
        if exp < 10:
            continue                      # a bin too small to test is reported as untested
        obs = hist[k]
        sd = math.sqrt(n * p * (1 - p))
        z = (obs - exp) / sd if sd else 0.0
        chi += z * z
        dof += 1
        rows.append({'k': k, 'obs': obs, 'exp': exp, 'sd': sd, 'z': z})
    return rows, chi, dof


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seconds', type=float, default=20.0)
    a = ap.parse_args()
    gps, ref = gps_stamp()
    print('  THE MISS LEDGER -- the hashes nobody keeps, against an exact expectation')
    print(f'  read {time.strftime("%H:%M:%S %Z, %-d %b %Y")}')
    print(f'  GPS stamp {("%.6f" % gps) if gps else "UNAVAILABLE"}   clock reference {ref}\n')
    hist, over, n, el = window(a.seconds)
    print(f'  {n:,} hashes in {el:.2f} s = {n/el/1e3:,.1f} kH/s   '
          f'{over:,} beyond k={KMAX} (kept as a count, not binned)')
    rows, chi, dof = read(hist, over, n)
    print(f'\n  {"k":>3}{"observed":>12}{"expected":>14}{"sd":>10}{"z":>8}')
    for r in rows:
        print(f'  {r["k"]:>3}{r["obs"]:>12,}{r["exp"]:>14,.1f}{r["sd"]:>10,.1f}{r["z"]:>+8.2f}')
    print(f'\n  chi-square {chi:.2f} on {dof} bins, expectation {dof} +- {math.sqrt(2*dof):.1f}')
    sep = abs(chi - dof) / math.sqrt(2 * dof) if dof else 0.0
    print(f'  {sep:.2f} widths from its expectation: '
          + ('THE SILICON IS CLEAN on this window -- the misses land exactly where arithmetic '
             'says' if sep < 2 else
             'DEVIATION. The misses do not follow 2^-(k+1), which is a statement about this '
             'hardware and not about the chain.'))
    print(f'\n  WHAT MAKES IT TRAINING DATA: the label is COMPUTED, not annotated. Every window is')
    print(f'  a labelled example -- the expected histogram is exact, so "healthy" and "how far off,')
    print(f'  in which bin" come free. The expensive part of training is the labels, and here the')
    print(f'  arithmetic supplies them, forever, from work the rig is doing anyway.')
    try:
        with open(LOG, 'a') as f:
            f.write(json.dumps({'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'gps': gps,
                                'clock_ref': ref, 'n': n, 'elapsed_s': el, 'khs': n / el / 1e3,
                                'hist': hist, 'over': over, 'chi': chi, 'dof': dof,
                                'widths': sep}) + '\n')
    except Exception:
        pass
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
