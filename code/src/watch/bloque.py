#!/usr/bin/env python3
"""bloque.py -- PROOF OF WORK AS A LOOK, ON THE REAL CHAIN. (Bones, 11 Oct 2026.)

Wayfinder, 11 Oct, after I started pricing hashrate against electricity like an accountant:
"don't put the probability up man · depressing as fuck · THE PHYSICS OUR SYSTEM IS SUPPOSED TO
RUN ON IS WHAT BUILT BLOCKCHAIN MAN."

He is right and it closed the coin lane. A nonce search is a LOOK: it asks whether a draw landed
in a band, and the answer is yes about once per 2^k tries. `miss_order.py` already reads that
from three seats with exact nulls -- BUT IT HASHES ITS OWN BLAKE2B STREAM. A synthetic stream
can only ever confirm that blake2b is uniform, which nobody doubts and which cost us nothing to
assume. THE REAL STREAM IS THE CHAIN, and we have been sitting on two seats of it all day.

    EL MIRON    the OBSERVER. ~/wownero/block_arrivals.log on flock-pi: one line per block, the
                moment OUR node saw it, stamped by a Pi that is chrony stratum 1 on a Leo Bodnar
                GPSDO. We cannot be lied to about this one -- it is our own look.
    EL TESTIGO  the WITNESS. The block's own `timestamp` field, DECLARED BY WHOEVER FOUND IT.
                Monero-family consensus only requires it to beat the median of the last 60 and
                to sit under +2 h, so this seat CAN RUN BACKWARDS and is counted when it does.
    EL TIEMPO   the DISAGREEMENT, arrival minus declared, per block. It is propagation plus the
                finder's own clock error and THIS FILE DOES NOT SPLIT THEM -- that would be
                hunting a clock, and that lane is closed (his call, 11 Oct). It is reported as a
                spread, which is what the disagreement leaves behind.

WHY THE NULLS ARE EXACT AND NOTHING HERE IS FITTED. Block discovery at constant hashrate and
difficulty is a Poisson process, so the intervals are Exponential with mean = the chain's own
declared target (get_info.target, 300 s on this chain -- READ LIVE, never typed in):

    * mean         2 * sum(x) / target ~ chi2(2n) EXACTLY, because 2X/theta ~ chi2(2) for Exp.
    * shape        the coefficient of variation of an exponential is EXACTLY 1.
    * the median   of Exp(target) is EXACTLY target * ln 2 = 207.944 s, so binarising the
                   intervals there gives p = 1/2 BY CONSTRUCTION, and Wald-Wolfowitz on that
                   series has an exact null conditional on the margin. No threshold was chosen.
    * the order    for an iid series the lag-1 autocorrelation is EXACTLY E[r] = -1/n with
                   variance 1/n.

THE CV's OWN WIDTH IS DERIVED, NOT GUESSED, because a null width nobody checked is a verdict
without a width. For any distribution Var(cv_hat) ~ (cv^2/n)[(g2+2)/4 - g1*cv + cv^2] with g1 the
skewness and g2 the excess kurtosis; an exponential has cv=1, g1=2, g2=6, so the bracket is
(8/4) - 2 + 1 = 1 and sd(cv_hat) = 1/sqrt(n) exactly to leading order. That is the only place in
this file where a width is asymptotic rather than exact, and it is said here.

AND THE TWO SEATS ARE READ ON THE SAME BLOCKS BEFORE THEY ARE COMPARED. The witness reaches back
thousands of blocks and the observer only as far as our hook has been running, so the full-length
readings below are two different events and are never subtracted from each other -- that is the
baseline-built-differently failure, 14 of our 20 prospective catches. EL PAREADO re-reads BOTH
seats on the identical block set, which is the only comparison that means anything.

AND THE ORDER IS THE SEAT WITH REAL PHYSICS IN IT, by THE SPLIT. The difficulty algorithm
retargets off a trailing window, so it PINS THE MEAN BY DESIGN -- S, common to every run, the
apparatus. What a reactive controller cannot pin is the ORDER. That residual is P, and it is the
only quantity here the chain is not already holding at its target. So a mean landing on 300 s is
NOT a finding; it is the controller working. EL GIRO is the look.

    FIRST READING, 11 Oct, and MY PREDICTION HAD THE SIGN BACKWARDS. I argued a reactive
    controller should leave NEGATIVE lag-1 -- a fast block raises the next block's difficulty,
    so the next should run slow. Measured, the declared intervals are POSITIVELY correlated and
    the estimate is stable while its z grows as sqrt(n), which is what a real effect does and
    not what noise does:

        n = 1,995   r1 = +0.0163   z +0.75        n =  9,977   r1 = +0.0332   z +3.32
        n = 4,987   r1 = +0.0303   z +2.16        n = 19,726   r1 = +0.0294   z +4.14

    The runs test, which uses only each interval's SIDE of the median and never its magnitude,
    is independently LOW at every length (z -1.23, -1.81, -1.94) -- fewer runs means longer
    same-side streaks, the same statement from a statistic that shares no arithmetic with the
    autocorrelation. And the CV sits above the exponential's exact 1 (1.021 to 1.053). All three
    are one physical thing: the controller lags a DRIFTING HASHRATE, so the rate is not constant
    across the window and the intervals are a mixture of exponentials -- over-dispersed, and
    arriving in same-direction runs. Controller lag beats controller reaction, and the sign of
    the effect is the evidence for which. THIS IS NOT NEW ABOUT THE CHAIN: non-Poisson block
    intervals from hashrate drift are known in the Bitcoin and Monero literature. What is new
    HERE is that we can read it on our own node, against nulls that are exact.

    Meanwhile the mean: 303.17 +- 2.14 s against a declared target of 300, z +1.50 at n=19,999.
    The controller holds it. S is pinned and P is not, exactly as THE SPLIT said to expect.

FOUR OUTCOMES, over the union of the two seats' hashes, through outcomes.py:

    matched            both seats read the block, declared interval > 0
    matched_backwards  both seats read it and THE WITNESS RAN BACKWARDS (declared delta <= 0)
    witness_only       the chain has it and we have no arrival stamp (before the hook, or we
                       were not listening) -- a hole in the observer, named
    observer_only      APPARATUS: we stamped a hash the chain no longer holds. That is a reorg,
                       or our own node's view, and it says nothing about the subject.

    python3 bloque.py                 # the full reading
    python3 bloque.py --blocks 2000   # a longer witness baseline
    python3 bloque.py --tick          # one line only when a seat moves off its exact null
"""
import argparse
import json
import math
import os
import subprocess
import sys
import time

W = os.path.expanduser('~/bones-forge/watch/')
sys.path.insert(0, W)
LOG = os.path.join(W, 'bloque.jsonl')
STATE = os.path.join(W, 'bloque_state.json')

PI = 'flock-pi'
ARRIVALS = '/home/flock/wownero/block_arrivals.log'
RPC = 'http://127.0.0.1:34568/json_rpc'

# BUDGETS, EVERY ONE WITH A MEASURED BASIS (afinar.py scans this file).
# MEASURED, not chosen: a full run at 2,000 blocks -- ssh, curl, 2,000 headers and all the
# arithmetic -- took 0.47 s wall, and at 500 blocks 0.40 s, so the fetch is dominated by the
# round trip and not by the block count. 25 s is ~50x the whole measured run.
SSH_TIMEOUT = 25
# The remote leg's own budget. 60 s is 128x the measured run and sits inside the 180 s leash
# below with 120 s to spare -- the arithmetic the harness got wrong tonight, done on purpose.
REMOTE_SECONDS = 60
# Default witness baseline. 2,000 blocks at a 300 s target is about 7 days -- the span of the
# node's own uptime (first block stamped 7 Oct), so asking for more only re-reads old chain.
BLOCKS = 2000

# THE REMOTE LEG. It runs on the Pi because the arrivals log and the daemon both live there, and
# it returns COMPACT ROWS rather than 1.9 MB of JSON. It reads the TARGET from the chain; the
# number 300 is never typed into this file.
REMOTE = r'''
import json, subprocess, sys

def rpc(method, params=None):
    body = {"jsonrpc": "2.0", "id": "0", "method": method}
    if params:
        body["params"] = params
    r = subprocess.run(['curl', '-s', '-m', '20', '%(rpc)s', '-d', json.dumps(body),
                        '-H', 'Content-Type: application/json'],
                       capture_output=True, text=True, timeout=25)
    return json.loads(r.stdout)['result']

info = rpc('get_info')
top = int(info['height']) - 1
n = int(sys.argv[1])
lo = max(1, top - n + 1)
hs = rpc('get_block_headers_range', {'start_height': lo, 'end_height': top})['headers']

arr = []
try:
    for ln in open('%(arrivals)s'):
        f = ln.split()
        if len(f) == 2:
            arr.append((float(f[0]), f[1]))
except Exception:
    pass

print(json.dumps({
    'target': int(info['target']),
    'height': int(info['height']),
    'difficulty': int(info['difficulty']),
    'headers': [[int(b['height']), int(b['timestamp']), int(b['difficulty']), b['hash']]
                for b in hs],
    'arrivals': arr,
}))
''' % {'rpc': RPC, 'arrivals': ARRIVALS}


def fetch(blocks):
    """one ssh, one curl, compact rows back. Returns None when the Pi or the daemon is away."""
    try:
        r = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=%d' % SSH_TIMEOUT,
                            PI, 'python3 - %d' % blocks],
                           input=REMOTE, capture_output=True, text=True, timeout=REMOTE_SECONDS)
    except Exception as e:
        return None, 'pi unreachable (%s)' % type(e).__name__
    if r.returncode != 0 or not r.stdout.strip():
        return None, 'remote leg returned nothing (rc %d) %s' % (r.returncode, r.stderr.strip()[:120])
    try:
        return json.loads(r.stdout), None
    except Exception:
        return None, 'remote leg did not return rows: %s' % r.stdout.strip()[:120]


# ---------------------------------------------------------------- the exact nulls


def el_conteo(x, target, span=None, span_n=None):
    """THE MAGNITUDE AND THE SHAPE, both exact for an exponential. x = intervals, seconds.

    THE MEAN IS READ OFF THE SPAN, NOT OFF x, AND THAT IS A CORRECTION TO THIS FILE'S FIRST
    VERSION. The shape and order tests need the backwards declared intervals removed -- a
    negative interval is not an exponential draw -- but removing them and THEN averaging drops
    only the left tail and pushes the mean UP. That is the censored-cells failure, and it was
    about to be reported as a chain running 3.2% slow at z = +4.45. The span is telescoping:
    (last stamp - first stamp) / (number of intervals) is immune to any lie in the middle,
    because a timestamp that is too early is also the end of the interval before it.
    """
    n = len(x)
    if n < 2:
        return None
    if span is not None and span_n:
        s = float(span)
        n_mean = int(span_n)
    else:
        s = float(sum(x))
        n_mean = n
    mean = s / n_mean
    # 2*sum/target ~ chi2(2n) exactly. Read as a z on the chi2, which has mean 2n and var 4n.
    stat = 2.0 * s / target
    z_mean = (stat - 2.0 * n_mean) / math.sqrt(4.0 * n_mean)
    # the SHAPE is read on x alone, with its own n, because a backwards interval is not a draw
    mx = float(sum(x)) / n
    var = sum((v - mx) ** 2 for v in x) / (n - 1)
    cv = math.sqrt(var) / mx if mx else float('nan')
    # cv of an exponential is exactly 1 and sd(cv_hat) = 1/sqrt(n) -- derived in the docstring
    z_cv = (cv - 1.0) * math.sqrt(float(n))
    return {'n': n, 'n_mean': n_mean, 'mean': mean, 'target': target, 'z_mean': z_mean,
            'cv': cv, 'z_cv': z_cv, 'sem': mean / math.sqrt(n_mean)}


def el_giro(x):
    """THE ORDER. lag-1 autocorrelation against the EXACT iid null -1/n, and the exact-null runs
    test on the series binarised at the exponential median -- a threshold nobody chose."""
    n = len(x)
    if n < 8:
        return None
    m = float(sum(x)) / n
    num = sum((x[i] - m) * (x[i + 1] - m) for i in range(n - 1))
    den = sum((v - m) ** 2 for v in x)
    r1 = num / den if den else float('nan')
    z_r1 = (r1 - (-1.0 / n)) * math.sqrt(float(n))
    return {'r1': r1, 'null_r1': -1.0 / n, 'z_r1': z_r1}


def runs_exact(bits):
    """Wald-Wolfowitz, exact null CONDITIONAL ON THE MARGIN: given n1 ones and n2 zeros, the
    number of runs has mean 1 + 2*n1*n2/n and a closed-form variance. Nothing is simulated."""
    n = len(bits)
    n1 = sum(bits)
    n2 = n - n1
    if n1 < 2 or n2 < 2:
        return None
    runs = 1 + sum(1 for i in range(n - 1) if bits[i] != bits[i + 1])
    mu = 1.0 + 2.0 * n1 * n2 / n
    var = (2.0 * n1 * n2 * (2.0 * n1 * n2 - n)) / (float(n) * n * (n - 1))
    z = (runs - mu) / math.sqrt(var) if var > 0 else float('nan')
    return {'runs': runs, 'expected': mu, 'z': z, 'n1': n1, 'n0': n2}


def bins(rows):
    """FOUR OUTCOMES, checked by outcomes.py, which refuses a residual bin by name."""
    from outcomes import Outcomes
    O = Outcomes(subject=[
        ('matched', lambda r: r['both'] and not r['backwards']),
        ('matched_backwards', lambda r: r['both'] and r['backwards']),
        ('witness_only', lambda r: not r['both'] and r['declared']),
    ], apparatus=[
        ('observer_only', lambda r: not r['both'] and not r['declared']),
    ])
    return O.tally(rows)


def read(blocks):
    d, err = fetch(blocks)
    if d is None:
        return None, err
    target = d['target']
    hs = sorted(d['headers'], key=lambda h: h[0])
    arr = {h: t for t, h in d['arrivals']}
    chain_by_h = {h[0]: h for h in hs}

    # EL TESTIGO -- the declared intervals, and the backwards ones counted not dropped
    dec = []
    back = 0
    for i in range(1, len(hs)):
        g = hs[i][1] - hs[i - 1][1]
        dec.append(g)
        if g <= 0:
            back += 1
    dec_pos = [g for g in dec if g > 0]

    # EL MIRON -- our own arrivals, in the order the chain holds them, GPSDO-stamped
    seen = [(h[0], arr[h[3]], h[3]) for h in hs if h[3] in arr]
    seen.sort()
    obs = [seen[i][1] - seen[i - 1][1] for i in range(1, len(seen))
           if seen[i][0] == seen[i - 1][0] + 1]      # CONSECUTIVE HEIGHTS ONLY: a gap in our
                                                     # stamps is a hole in the observer, and
                                                     # adding across it would invent an interval

    # EL TIEMPO -- the disagreement itself, per block
    lag = [arr[h[3]] - h[1] for h in hs if h[3] in arr]

    # EL PAREADO -- THE SAME BLOCKS IN BOTH SEATS. The only comparison that is like for like:
    # the consecutive-height pairs we hold an arrival for, read once declared and once observed.
    # Note the identity: observed_i - declared_i = lag_i - lag_{i-1}, so any difference between
    # the two seats' ORDER is a statement about EL TIEMPO and not about the chain.
    pdec, pobs, pdif = [], [], []
    for i in range(1, len(seen)):
        if seen[i][0] != seen[i - 1][0] + 1:
            continue
        hh, hp = chain_by_h.get(seen[i][0]), chain_by_h.get(seen[i - 1][0])
        if hh is None or hp is None:
            continue
        gd = hh[1] - hp[1]
        go = seen[i][1] - seen[i - 1][1]
        pdec.append(gd)
        pobs.append(go)
        pdif.append(go - gd)

    # the four outcomes, over the UNION of both seats' hashes
    chain = {h[3]: h for h in hs}
    rows = []
    for i, h in enumerate(hs):
        rows.append({'both': h[3] in arr, 'declared': True,
                     'backwards': i > 0 and (h[1] - hs[i - 1][1]) <= 0})
    for t, hh in d['arrivals']:
        if hh not in chain:
            rows.append({'both': False, 'declared': False, 'backwards': False})

    med = target * math.log(2.0)
    out = {
        'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'height': d['height'], 'difficulty': d['difficulty'], 'target': target,
        'exp_median': med,
        'witness': el_conteo(dec_pos, target,
                             span=(hs[-1][1] - hs[0][1]) if len(hs) > 1 else None,
                             span_n=len(hs) - 1),
        'witness_giro': el_giro(dec_pos),
        'witness_runs': runs_exact([1 if g > med else 0 for g in dec_pos]),
        'witness_backwards': back,
        'observer': el_conteo(obs, target),
        'observer_giro': el_giro(obs),
        'observer_runs': runs_exact([1 if g > med else 0 for g in obs]),
        'paired': ({'n': len(pdec),
                    'dec_mean': sum(pdec) / len(pdec), 'obs_mean': sum(pobs) / len(pobs),
                    'dec_giro': el_giro(pdec), 'obs_giro': el_giro(pobs),
                    'dif_mean': sum(pdif) / len(pdif),
                    'dif_sd': math.sqrt(sum((v - sum(pdif) / len(pdif)) ** 2 for v in pdif)
                                        / (len(pdif) - 1))}
                   if len(pdec) > 8 else None),
        'tiempo': ({'n': len(lag), 'mean': sum(lag) / len(lag),
                    'min': min(lag), 'max': max(lag),
                    'sd': math.sqrt(sum((v - sum(lag) / len(lag)) ** 2 for v in lag) / (len(lag) - 1))}
                   if len(lag) > 2 else None),
        'bins': {k: len(v) if hasattr(v, '__len__') else v for k, v in bins(rows).items()},
    }
    return out, None


# ---------------------------------------------------------------- saying it


def line(name, c, g, r):
    if not c:
        return ['    %-10s n too small to read' % name]
    o = ['    %-10s mean %7.2f +- %-5.2f s over n=%-6d (SPAN, every interval)   target %d s   z %+6.2f'
         % (name, c['mean'], c['sem'], c['n_mean'], c['target'], c['z_mean']),
         '    %-10s CV %.4f against the exponential\'s exact 1, on n=%-6d (forward only)  z %+6.2f'
         % ('', c['cv'], c['n'], c['z_cv'])]
    if g:
        o.append('    %-10s lag-1 r = %+.4f against the EXACT iid null %+.4f -- z %+6.2f'
                 % ('', g['r1'], g['null_r1'], g['z_r1']))
    if r:
        o.append('    %-10s runs %d against %.1f expected (p=1/2 by the exponential median) -- z %+6.2f'
                 % ('', r['runs'], r['expected'], r['z']))
    return o


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--blocks', type=int, default=BLOCKS)
    ap.add_argument('--tick', action='store_true')
    a = ap.parse_args()
    if a.tick:
        # ITS OWN LEASH. A full run measured 0.47 s end to end at 2,000 blocks, so 180 s is 380x
        # and the remote leg's own 60 s budget fits inside it with 120 s to spare.
        import tickguard
        tickguard.guard('bloque', 180)

    d, err = read(a.blocks)
    if d is None:
        if not a.tick:
            print('  bloque: %s' % err)
        return 0
    try:
        with open(LOG, 'a') as f:
            f.write(json.dumps(d) + '\n')
    except Exception:
        pass

    if a.tick:
        # SPEAKS ONLY WHEN SOMETHING MOVES, per the no-bulletin rule. The positive lag-1 is now a
        # MEASURED, LOGGED PROPERTY of this chain (r1 = +0.030, stable 5k-20k blocks, z +4.14 at
        # n=19,726), so a detector firing on it every 50 minutes would be a bulletin reporting a
        # known number. The ORDER is therefore read against ITS OWN RECORDED VALUE: two
        # independent estimates of r1 differ with sd sqrt(2/n), and only a 3-sigma move speaks.
        # The mean, the CV and the reorg count keep absolute bars because they have exact nulls
        # and no stored prior is needed to say they moved off them.
        prev = {}
        try:
            prev = json.load(open(STATE))
        except Exception:
            pass
        say = []
        for nm, k in (('WITNESS', 'witness'), ('OBSERVER', 'observer')):
            g = d.get(k + '_giro')
            p0 = prev.get('r1_' + k)
            if g and p0 is not None and d[k]:
                sd = math.sqrt(2.0 / d[k]['n'])
                if abs(g['r1'] - p0) > 3.0 * sd:
                    say.append('BLOQUE: %s ORDER moved, lag-1 %+.4f -> %+.4f (3 sd = %.4f, n=%d)'
                               % (nm, p0, g['r1'], 3.0 * sd, d[k]['n']))
        for nm, k in (('WITNESS', 'witness'), ('OBSERVER', 'observer')):
            c, g = d.get(k), d.get(k + '_giro')
            if c and abs(c['z_mean']) > 3.0:
                say.append('BLOQUE: %s mean %.1f s against a declared target of %d -- z %+.2f (n=%d)'
                           % (nm, c['mean'], d['target'], c['z_mean'], c['n']))
            if c and abs(c['z_cv']) > 3.0:
                say.append('BLOQUE: %s CV %.3f, and an exponential is exactly 1 -- z %+.2f (n=%d)'
                           % (nm, c['cv'], c['z_cv'], c['n']))
        if d['bins'].get('observer_only'):
            say.append('BLOQUE: %d stamped hashes are not on the chain -- a reorg, or our node\'s own view'
                       % d['bins']['observer_only'])
        for s in say:
            print(s)
        try:
            st = {'at': d['at'], 'height': d['height']}
            for k in ('witness', 'observer'):
                if d.get(k + '_giro'):
                    st['r1_' + k] = d[k + '_giro']['r1']
            json.dump(st, open(STATE, 'w'))
        except Exception:
            pass
        return 0

    print('  BLOQUE -- the real chain, read from three seats. height %d, difficulty %d, target %d s'
          % (d['height'], d['difficulty'], d['target']))
    print('  Nothing below is fitted. The mean, the shape, the median and the order all have')
    print('  EXACT nulls for a Poisson process, and the target is read off the chain itself.\n')
    print('  EL TESTIGO -- the block\'s OWN timestamp, declared by whoever found it:')
    for s in line('witness', d['witness'], d['witness_giro'], d['witness_runs']):
        print(s)
    print('    %-10s declared intervals that ran BACKWARDS or stood still: %d'
          % ('', d['witness_backwards']))
    print('\n  EL MIRON -- OUR arrival, stamped by a Pi on a GPSDO. Our own look, consecutive only:')
    for s in line('observer', d['observer'], d['observer_giro'], d['observer_runs']):
        print(s)
    p = d['paired']
    print('\n  EL PAREADO -- BOTH SEATS ON THE SAME BLOCKS. The readings above are two different')
    print('  spans and are never subtracted from each other; this one is like for like.')
    if p:
        print('    n=%d   declared mean %.1f s   observed mean %.1f s   same blocks'
              % (p['n'], p['dec_mean'], p['obs_mean']))
        print('    observed minus declared, per interval: %+.3f +- %.3f s'
              % (p['dif_mean'], p['dif_sd'] / math.sqrt(p['n'])))
        if p['dec_giro'] and p['obs_giro']:
            print('    lag-1  declared %+.4f   observed %+.4f   (null %+.4f) -- and observed minus'
                  % (p['dec_giro']['r1'], p['obs_giro']['r1'], p['obs_giro']['null_r1']))
            print('           declared is EL TIEMPO differenced, so a gap here is OUR seat, not the chain')
    else:
        print('    fewer than 9 consecutive matched pairs -- nothing to pair yet')
    t = d['tiempo']
    print('\n  EL TIEMPO -- arrival minus declared. Propagation PLUS the finder\'s own clock, and')
    print('  this file does not split them: that would be hunting a clock, and that lane is closed.')
    if t:
        print('    n=%d   mean %+.2f s   sd %.2f s   range %+.2f to %+.2f s'
              % (t['n'], t['mean'], t['sd'], t['min'], t['max']))
    else:
        print('    not enough matched blocks yet')
    print('\n  FOUR OUTCOMES, exhaustive and disjoint:')
    for k in sorted(d['bins']):
        print('    %-20s %d' % (k, d['bins'][k]))
    print('\n  AND THE MEAN IS NOT THE FINDING. The difficulty algorithm retargets off a trailing')
    print('  window, so it PINS the mean by design -- that is S, the apparatus. EL GIRO is P.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
