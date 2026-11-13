"""read6.py -- reads the NONE ARM (look, look again, no time between) of any run that has `S|w0|cN` circuits: run 6 (Pittsburgh) and run 5 (Marrakesh),
side by side on ONE reader. By hand, outside the freeze. No cut, no verdict word.
  python read6.py"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import analyze as A
from common import STARTS

COPIES = [1, 2, 3]; SEED = 20261063; BOOT = 400


def q(D, copies):
    """frame = look 1 of the OFF and ON no-wait circuits of these copies ONLY (so both chips are read with the same kind of frame)."""
    ks = lambda s: [f'{s}|w0|c{c}' for c in copies]
    m0 = np.concatenate([D[k][0] for k in ks('OFF')]).mean(0); d = np.concatenate([D[k][0] for k in ks('ON')]).mean(0) - m0
    pr = lambda L: np.real((L - m0) * np.conj(d)) / np.abs(d) ** 2
    out = {}
    for s in STARTS:
        p1 = np.concatenate([pr(D[k][0]) for k in ks(s)]); p2 = np.concatenate([pr(D[k][1]) for k in ks(s)])
        out[f'none.{s}'] = np.median((p2 - p1).mean(0)); out[f'look1.{s}'] = np.median(p1.mean(0)); out[f'look2.{s}'] = np.median(p2.mean(0))
        out[f'look1skew.{s}'] = np.median(A.stats3(p1)[2]); out[f'look2skew.{s}'] = np.median(A.stats3(p2)[2])
        out[f'none_perbit.{s}'] = (p2 - p1).mean(0)
    return out


def read(chip, run):
    d = os.path.join(HERE, 'data', 'fire', chip); D, meta = A.load(d, run)
    D = {k: v for k, v in D.items() if '|w0|' in k}
    sets = {'ALL': COPIES, 'c1': [1], 'c2': [2], 'c3': [3]}; full = {n: q(D, c) for n, c in sets.items()}
    rng = np.random.default_rng(SEED); reps = {n: {} for n in sets}
    for _ in range(BOOT):
        R = {}
        for k, looks in D.items():
            i = rng.integers(0, looks[0].shape[0], looks[0].shape[0]); R[k] = [L[i] for L in looks]
        for n, c in sets.items():
            for k, v in q(R, c).items(): reps[n].setdefault(k, []).append(v)
    sep = np.abs(np.concatenate([D[f'ON|w0|c{c}'][0] for c in COPIES]).mean(0) - np.concatenate([D[f'OFF|w0|c{c}'][0] for c in COPIES]).mean(0))
    o = np.concatenate([D[f'OFF|w0|c{c}'][0] for c in COPIES]); sd = np.sqrt((np.abs(o - o.mean(0)) ** 2).mean(0) / 2)
    print(f"\n==== {chip}, run {run}: {meta['shots']} shots per circuit ({3 * meta['shots']} per start), bits {meta['all_q']}, fired {meta.get('start_time')}")
    print('  bits, separation / width: ' + '  '.join(f'q{b}:{s_ / w_:.1f}' for b, s_, w_ in zip(meta['all_q'], sep, sd)))
    rows = {}
    for k in [f'{x}.{s}' for x in ('none', 'look1', 'look2', 'look1skew', 'look2skew') for s in STARTS]:
        w = lambda n: float(np.nanstd(np.array(reps[n][k], float), ddof=1))
        cs = [full[c][k] for c in ('c1', 'c2', 'c3')]; rows[k] = {'value': float(full['ALL'][k]), 'width': w('ALL'), 'copies': [float(x) for x in cs]}
        print(f"  {k:<16} {full['ALL'][k]:>9.4f} +-{w('ALL'):<8.4f} | copies {cs[0]:>8.4f} {cs[1]:>8.4f} {cs[2]:>8.4f} (+-{w('c1'):.4f}) | each minus the other two " + ' '.join(f'{cs[i] - np.mean([cs[j] for j in range(3) if j != i]):>8.4f}' for i in range(3)))
    for s in STARTS:
        pb = np.array(reps['ALL'][f'none_perbit.{s}']).std(0, ddof=1)
        print(f"  none, each bit, {s:<3}: " + '  '.join(f'{v:+.3f}(+-{e:.3f})' for v, e in zip(full['ALL'][f'none_perbit.{s}'], pb)))
    return rows


if __name__ == '__main__':
    out = {}
    for chip, run in (('ibm_marrakesh', 5), ('ibm_pittsburgh', 9), ('ibm_kingston', 7)):
        try: out[chip] = read(chip, run)
        except Exception as e: print(f"\n==== {chip}, run {run}: CAN'T READ ({type(e).__name__}: {e})")
    json.dump(out, open(os.path.join(HERE, 'data', 'reads', 'none_arm_three_chips.json'), 'w'), indent=1)
