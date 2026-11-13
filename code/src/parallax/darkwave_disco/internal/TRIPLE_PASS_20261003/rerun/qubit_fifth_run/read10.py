"""read10.py -- THE SHORT-WAIT COLUMN, READ BIT BY BIT ACROSS TIME. By hand, outside the freeze. No cut, no verdict word.
For each chip: what look 2 reads after the 60 us wait (and look 2 minus look 1), per bit, in every run that has those circuits, on one frame rule
(OFF = 0, ON = 1 from look 1 of that run's OWN short-wait OFF and ON circuits only), then each read minus the one before it.
  python read10.py"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from common import STARTS

OLD = os.path.join(HERE, '..', 'qubit_three_runs', 'data', 'fire'); NEW = os.path.join(HERE, 'data', 'fire')
READS = {'ibm_pittsburgh': [('last night (blank, unopened)', OLD, 2, ['{s}|w60']), ('this morning (opened)', NEW, 9, ['{s}|w60|c1', '{s}|w60|c2', '{s}|w60|c3']), ('now', NEW, 10, ['{s}|w60|c1', '{s}|w60|c2', '{s}|w60|c3'])],
         'ibm_kingston': [('last night', OLD, 2, ['{s}|w60']), ('now', NEW, 10, ['{s}|w60|c1', '{s}|w60|c2', '{s}|w60|c3'])]}


def one(root, chip, run, pats):
    d = os.path.join(root, chip); meta = json.load(open(os.path.join(d, f'run{run}_meta.json')))
    if meta.get('complete') is not True: raise RuntimeError('not marked complete')
    z = np.load(os.path.join(d, f'run{run}_results.npz'))
    L = lambda s, k: np.concatenate([np.asarray(z[p.format(s=s) + f'__L{k}']).astype(complex) for p in pats])
    m0 = L('OFF', 1).mean(0); dd = L('ON', 1).mean(0) - m0; pr = lambda x: np.real((x - m0) * np.conj(dd)) / np.abs(dd) ** 2
    out = {'bits': meta['all_q'], 'fired': meta.get('start_time'), 'shots': L('ON', 1).shape[0]}
    for s in STARTS:
        p1, p2 = pr(L(s, 1)), pr(L(s, 2)); n = p1.shape[0]
        out[s] = {'look1': p1.mean(0), 'look2': p2.mean(0), 'e2': p2.std(0, ddof=1) / np.sqrt(n), 'gap': (p2 - p1).mean(0), 'eg': (p2 - p1).std(0, ddof=1) / np.sqrt(n)}
    return out


f3 = lambda a: ' '.join(f'{x:+.3f}' for x in a)
res = {}
for chip, reads in READS.items():
    print(f'\n==== {chip}'); got = []
    for name, root, run, pats in reads:
        try: r = one(root, chip, run, pats)
        except Exception as e: print(f"  {name} (run {run}): CAN'T READ ({type(e).__name__}: {e})"); continue
        got.append((name, r)); print(f"  {name}: run {run}, fired {r['fired']}, {r['shots']} shots per start, bits {r['bits']}")
    for s in ('ON', 'MID', 'OFF'):
        print(f'  -- start {s}: what look 2 reads after the short wait, each bit | middle bit')
        for name, r in got: print(f"     {name:<30} {f3(r[s]['look2'])} | {np.median(r[s]['look2']):+.3f}   (widths ~{np.median(r[s]['e2']):.3f})")
        for (na, a), (nb, b) in zip(got, got[1:]):
            dlt = b[s]['look2'] - a[s]['look2']; w = np.hypot(a[s]['e2'], b[s]['e2'])
            print(f"     CHANGE {na} -> {nb}:\n       {'':<27}{f3(dlt)} | middle {np.median(dlt):+.3f}\n       in its own widths:         {' '.join(f'{x:+6.1f}' for x in dlt / w)}   rms over the nine bits {np.sqrt(np.mean(dlt ** 2)):.3f}")
            res[f'{chip}|{s}|{na}->{nb}'] = {'change': dlt.tolist(), 'in_widths': (dlt / w).tolist(), 'rms': float(np.sqrt(np.mean(dlt ** 2))), 'median': float(np.median(dlt))}
json.dump(res, open(os.path.join(HERE, 'data', 'reads', 'short_wait_across_time.json'), 'w'), indent=1)
