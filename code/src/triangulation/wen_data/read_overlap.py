#!/usr/bin/env python3
"""read_overlap.py -- the blind_spot_overlap instrument, read against a null.

A Jaccard on its own is a number with no ruler. Two seats that each miss a lot of
cases will share misses by arithmetic alone, so the question is never "is the overlap
high" but "is it higher than two INDEPENDENT seats of these exact miss-counts would
give". The null here is exact, not resampled: draw |A| and |B| misses uniformly from
the n held-out cases and the shared count is hypergeometric.

    python3 read_overlap.py pods/tick4/stdout.log
"""
import json, math, re, sys

def hyper_sf(k, n, a, b):
    """P(shared >= k) for |A|=a, |B|=b drawn from n."""
    def lc(x, y):
        if y < 0 or y > x: return -math.inf
        return math.lgamma(x+1) - math.lgamma(y+1) - math.lgamma(x-y+1)
    tot = 0.0
    for i in range(k, min(a, b) + 1):
        tot += math.exp(lc(b, i) + lc(n-b, a-i) - lc(n, a))
    return min(1.0, tot)

def main(path):
    lines = [l for l in open(path, errors='replace') if 'blind_spot_overlap' in l]
    if not lines: return print('no blind_spot_overlap rows in', path)
    last = lines[-1]
    rnd = re.search(r'EXAM round (\d+)', last)
    key = re.search(r'"(blind_spot_overlap[^"]*)"', last).group(1)
    i = last.find('{'); d = 0; end = None
    for k, c in enumerate(last[i:], i):
        if c == '{': d += 1
        elif c == '}':
            d -= 1
            if d == 0: end = k; break
    ov = json.loads(last[i:end+1])[key]

    n = ov['cases']; miss = ov['misses_each']
    print('\n  BLIND-SPOT OVERLAP -- %s, round %s' % (path, rnd.group(1) if rnd else '?'))
    print('  %d held-out cases. Misses: %s' % (n, ', '.join('%s %d' % kv for kv in sorted(miss.items(), key=lambda x: x[1]))))
    print('  all three stooges missed the same case %d times (%.1f%% of the pool)\n'
          % (ov['all_stooges_missed_together'], 100*ov['all_stooges_missed_together']/n))

    print('  %-16s %7s %7s %9s %9s %7s   %s' % ('pair','both','either','jaccard','chance','ratio','P(>=both)'))
    rows = []
    for pair, v in ov['pairs'].items():
        a_name, b_name = pair.split('&')
        a, b = miss[a_name], miss[b_name]
        exp_both = a * b / n
        exp_either = a + b - exp_both
        exp_j = exp_both / exp_either if exp_either else float('nan')
        ratio = v['jaccard'] / exp_j if exp_j else float('nan')
        p = hyper_sf(v['both_missed'], n, a, b)
        rows.append((ratio, pair, v, exp_j, p))
    for ratio, pair, v, exp_j, p in sorted(rows, reverse=True):
        print('  %-16s %7d %7d %9.3f %9.3f %6.1fx   %.2e'
              % (pair, v['both_missed'], v['either'], v['jaccard'], exp_j, ratio, p))

    top = sorted(rows, reverse=True)[0]
    print('\n  The design asks that the seats\' blind spots NOT overlap. Ranked against the')
    print('  independence null, the pair that breaks it is %s at %.1fx chance (p = %.1e).'
          % (top[1], top[0], top[4]))
    others = sorted(rows, reverse=True)[1:]
    print('  Every other pair sits between %.1fx and %.1fx.' % (others[-1][0], others[0][0]))

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'pods/tick4/stdout.log')
