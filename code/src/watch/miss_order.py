#!/usr/bin/env python3
"""miss_order.py -- THE HASHES NOBODY KEEPS, READ FROM THREE SEATS. (Bones, 10 Oct 2026.)

`miss_ledger.py` chi-squares the leading-zero histogram against the exact P(k) = 2^-(k+1). That is
a MAGNITUDE ON COUNTS, and step 15 says a magnitude is half a reading. One event, three seats:

    EL CONTEO   the histogram against 2^-(k+1).  Multinomial, exact, no fit.
    EL GIRO     the ORDER. For an iid series the lag-1 autocorrelation is exactly
                E[r] = -1/n with variance 1/n, and the WALD-WOLFOWITZ runs test on the series
                binarised at k>=1 (p = 1/2 exactly) has an exact null conditional on the margin.
                A rig drifting thermally makes correlated RUNS while its histogram stays perfect.
    SIX PLUS NONE  THE ABSENCE. The histogram counts what ARRIVED. What it discards is the
                WAITING -- the gaps between successive hashes that reach k or better. Those gaps
                are geometric(p = 2^-k) exactly: mean 1/p, variance (1-p)/p^2. And the bins the
                ledger never tests at all (expectation under 10) plus everything past KMAX are
                reported as a COUNT with its expectation, never silently dropped.

THE NONE IS ARITHMETIC IN ALL THREE SEATS. Nothing here is priced against a shuffle or a guess, and
nothing is fitted: a good hash function's output is uniform, so every expectation above is exact.

Everything streams -- no array of 30 million values is kept, only the sums each test needs.

    python3 miss_order.py --seconds 20
    python3 miss_order.py --tick
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
LOG = os.path.join(W, 'miss_order.jsonl')
KMAX = 20
THRESH = (4, 8, 12)          # the k values whose WAITING is read; p = 2^-k
MINEXP = 10.0


def leading_zeros(b):
    n = 0
    for byte in b:
        if byte:
            return n + (8 - byte.bit_length())
        n += 8
    return n


def gps_stamp():
    try:
        import subprocess
        r = subprocess.run(['ssh', '-o', 'ConnectTimeout=6', '-o', 'BatchMode=yes', 'flock-pi',
                            'date +%s.%N'], capture_output=True, text=True, timeout=15)
        return float(r.stdout.strip().split('\n')[0])
    except Exception:
        return None


def window(seconds):
    """hash until the clock runs out, keeping the three seats' sums and nothing else."""
    hist = [0] * (KMAX + 1)
    over = 0
    n = 0
    # EL GIRO, streaming
    s1 = s2 = sx = 0.0
    prev = None
    runs = 1
    n1 = 0
    prev_b = None
    # SIX PLUS NONE, streaming: last index at or above each threshold, and the gap sums
    last = {k: None for k in THRESH}
    gsum = {k: 0 for k in THRESH}
    gsq = {k: 0 for k in THRESH}
    gcnt = {k: 0 for k in THRESH}
    seed = os.urandom(32)
    nonce = 0
    t0 = time.time()
    while time.time() - t0 < seconds:
        for _ in range(20000):
            k = leading_zeros(hashlib.blake2b(seed + struct.pack('<Q', nonce),
                                              digest_size=32).digest())
            if k <= KMAX:
                hist[k] += 1
            else:
                over += 1
            s1 += k
            s2 += k * k
            if prev is not None:
                sx += prev * k
            prev = k
            b = 1 if k >= 1 else 0
            if b:
                n1 += 1
            if prev_b is not None and b != prev_b:
                runs += 1
            prev_b = b
            for th in THRESH:
                if k >= th:
                    if last[th] is not None:
                        g = nonce - last[th]
                        gsum[th] += g
                        gsq[th] += g * g
                        gcnt[th] += 1
                    last[th] = nonce
            nonce += 1
            n += 1
    return dict(hist=hist, over=over, n=n, elapsed=time.time() - t0,
                s1=s1, s2=s2, sx=sx, runs=runs, n1=n1,
                gsum=gsum, gsq=gsq, gcnt=gcnt)


def el_conteo(hist, n):
    rows, chi, dof = [], 0.0, 0
    untested = []
    for k in range(KMAX + 1):
        p = 2.0 ** -(k + 1)
        exp = n * p
        if exp < MINEXP:
            untested.append({'k': k, 'exp': exp, 'obs': hist[k]})
            continue
        sd = math.sqrt(n * p * (1 - p))
        z = (hist[k] - exp) / sd if sd else 0.0
        chi += z * z
        dof += 1
        rows.append({'k': k, 'obs': hist[k], 'exp': exp, 'sd': sd, 'z': z})
    return rows, chi, dof, untested


def el_giro(d):
    n = d['n']
    m = d['s1'] / n
    var = d['s2'] / n - m * m
    # lag-1 autocorrelation, and its EXACT null for an iid series: E[r] = -1/n, Var = 1/n
    r = (d['sx'] / (n - 1) - m * m) / var if var > 0 else 0.0
    z_r = (r + 1.0 / n) * math.sqrt(n)
    # WALD-WOLFOWITZ on the series binarised at k>=1, where p = 1/2 EXACTLY
    n1, N = d['n1'], n
    n2 = N - n1
    mu = 1 + 2.0 * n1 * n2 / N
    vr = 2.0 * n1 * n2 * (2.0 * n1 * n2 - N) / (N * N * (N - 1))
    z_w = (d['runs'] - mu) / math.sqrt(vr) if vr > 0 else 0.0
    return {'mean_k': m, 'var_k': var, 'lag1': r, 'z_lag1': z_r,
            'runs': d['runs'], 'runs_exp': mu, 'runs_sd': math.sqrt(vr), 'z_runs': z_w,
            'n1': n1, 'n2': n2}


def seis_mas_nada(d):
    """THE ABSENCE: the WAITING between arrivals, geometric(p) exactly."""
    out = []
    for th in THRESH:
        p = 2.0 ** -th
        m = d['gcnt'][th]
        if m < 30:
            out.append({'k': th, 'gaps': m, 'why': 'too few arrivals to read the waiting'})
            continue
        mean = d['gsum'][th] / m
        exp = 1.0 / p
        sd_one = math.sqrt((1 - p) / (p * p))
        sd_mean = sd_one / math.sqrt(m)
        obs_var = d['gsq'][th] / m - mean * mean
        out.append({'k': th, 'gaps': m, 'mean_gap': mean, 'exp_gap': exp,
                    'sd_mean': sd_mean, 'z': (mean - exp) / sd_mean,
                    'cv_obs': math.sqrt(obs_var) / mean if mean else None,
                    'cv_exp': sd_one / exp})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seconds', type=float, default=20.0)
    ap.add_argument('--tick', action='store_true')
    a = ap.parse_args()
    if a.tick:
        try:
            import tickguard
            if not tickguard.guard('miss_order', 150):
                return 0
        except Exception:
            pass
    secs = 8.0 if a.tick else a.seconds
    gps = gps_stamp()
    d = window(secs)
    rows, chi, dof, untested = el_conteo(d['hist'], d['n'])
    G = el_giro(d)
    A = seis_mas_nada(d)
    sep = abs(chi - dof) / math.sqrt(2 * dof) if dof else 0.0
    row = {'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'gps': gps, 'n': d['n'],
           'elapsed_s': d['elapsed'], 'khs': d['n'] / d['elapsed'] / 1e3,
           'conteo': {'chi': chi, 'dof': dof, 'widths': sep},
           'giro': G, 'nada': A,
           'over_kmax': d['over'], 'over_exp': d['n'] * 2.0 ** -(KMAX + 1),
           'untested_bins': len(untested)}
    try:
        with open(LOG, 'a') as f:
            f.write(json.dumps(row) + '\n')
    except Exception:
        pass
    speak = (sep >= 2.0 or abs(G['z_lag1']) >= 3.0 or abs(G['z_runs']) >= 3.0
             or any(abs(x.get('z', 0.0)) >= 3.0 for x in A))
    if a.tick and not speak:
        return 0
    print('  THE MISS LEDGER, THREE SEATS -- count, turn, and absence')
    print(f'  read {time.strftime("%H:%M:%S %Z, %-d %b %Y")}'
          + (f'   GPS {gps:.6f}' if gps else '   GPS UNAVAILABLE'))
    print(f'  {d["n"]:,} hashes in {d["elapsed"]:.2f} s = {d["n"]/d["elapsed"]/1e3:,.1f} kH/s\n')
    print(f'  EL CONTEO -- the histogram against 2^-(k+1), multinomial, exact')
    print(f'    chi-square {chi:.2f} on {dof} bins, expectation {dof} +- {math.sqrt(2*dof):.1f}'
          f'  = {sep:.2f} widths')
    print(f'\n  EL GIRO -- the ORDER, which the histogram throws away')
    print(f'    lag-1 autocorrelation {G["lag1"]:+.6f}   null is exactly -1/n = {-1.0/d["n"]:+.3e}'
          f' +- {1/math.sqrt(d["n"]):.3e}   z {G["z_lag1"]:+.2f}')
    print(f'    runs {G["runs"]:,} on {G["n1"]:,}+/{G["n2"]:,}-   expected '
          f'{G["runs_exp"]:,.1f} +- {G["runs_sd"]:.1f}   z {G["z_runs"]:+.2f}')
    print(f'\n  SIX PLUS NONE -- the WAITING between arrivals, geometric(p) exactly')
    print(f"    {'k':>3}{'gaps':>10}{'mean gap':>14}{'expected':>12}{'z':>8}{'CV obs':>9}{'CV exp':>9}")
    for x in A:
        if 'why' in x:
            print(f'    {x["k"]:>3}{x["gaps"]:>10}   {x["why"]}')
        else:
            print(f'    {x["k"]:>3}{x["gaps"]:>10,}{x["mean_gap"]:>14,.1f}{x["exp_gap"]:>12,.1f}'
                  f'{x["z"]:>+8.2f}{x["cv_obs"]:>9.4f}{x["cv_exp"]:>9.4f}')
    print(f'\n  AND THE ABSENCE THE LEDGER NEVER REPORTED: {len(untested)} bins have an expectation')
    print(f'  under {MINEXP} and were dropped without a word. Past k={KMAX}: {d["over"]:,} observed'
          f' against {row["over_exp"]:,.1f} expected.')
    for u in untested[:4]:
        print(f'    k={u["k"]:<3}expected {u["exp"]:.3f}, observed {u["obs"]}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
