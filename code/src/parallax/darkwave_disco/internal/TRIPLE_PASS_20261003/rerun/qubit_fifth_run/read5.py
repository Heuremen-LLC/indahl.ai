"""read5.py -- reads RUN 5 (the none). Written by hand by Bones, outside the freeze (a reader, like parse_payload.py). No prediction exists, so nothing is scored.
  python read5.py [--dir data/fire/ibm_marrakesh] [--boot 200]
Raw I/Q is never cut to 0/1: each look is projected on the per-bit line from the OFF centre to the ON centre of look 1 (OFF = 0, ON = 1).
Pooling across the nine bits = MEDIAN. Widths = bootstrap over shots. Every quantity is given for the whole run and for each of the three copies,
and each copy is read against the other two. No cut, no verdict word. CAN'T READ is a row."""
import argparse, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import analyze as A
from common import STARTS, WAITS_US

W4 = [0] + list(WAITS_US); COPIES = [1, 2, 3]; SEED = 20261053


def quantities(D, meta, copies):
    """D: key -> [look1, look2] complex (shots x bits). Frame = look 1 of every OFF and ON circuit of these copies."""
    ks = lambda s: [f'{s}|w{w}|c{c}' for c in copies for w in W4]
    m0 = np.concatenate([D[k][0] for k in ks('OFF')]).mean(0); d = np.concatenate([D[k][0] for k in ks('ON')]).mean(0) - m0
    pr = lambda L: np.real((L - m0) * np.conj(d)) / np.abs(d) ** 2
    out = {}
    wr = A._wait_real({'circuits': meta['ledger']['circuits']}); ws = [wr[w] for w in WAITS_US]
    YG, YF = {}, {}
    for s in STARTS:
        l1 = np.concatenate([pr(D[k][0]) for k in ks(s)]); m, v, sk = A.stats3(l1)
        out[f'L1.{s}.mean'], out[f'L1.{s}.var'], out[f'L1.{s}.skew'] = np.median(m), np.median(v), np.median(sk)
        for w in W4:
            p1 = np.concatenate([pr(D[f'{s}|w{w}|c{c}'][0]) for c in copies]); p2 = np.concatenate([pr(D[f'{s}|w{w}|c{c}'][1]) for c in copies])
            out[f'F.{s}.w{w}'] = np.median(p2.mean(0)); out[f'gap.{s}.w{w}'] = np.median((p2 - p1).mean(0))
            out[f'L2skew.{s}.w{w}'] = np.median(A.stats3(p2)[2])
        YG[s] = [out[f'gap.{s}.w{w}'] for w in WAITS_US]; YF[s] = [out[f'F.{s}.w{w}'] for w in WAITS_US]
    tg, resid, _ = A.fit_fade(ws, YG, 'gap'); tf, _, _ = A.fit_fade(ws, YF, 'level')
    for k in STARTS + ['shared']: out[f'gapclock.{k}'] = tg[k]; out[f'levelclock.{k}'] = tf[k]
    out['ratio.shared'] = tg['shared'] / tf['shared'] if np.isfinite(tg['shared']) and np.isfinite(tf['shared']) else np.nan
    out['ratio.ON'] = tg['ON'] / tf['ON'] if np.isfinite(tg['ON']) and np.isfinite(tf['ON']) else np.nan
    out['remainder_rms'] = float(np.sqrt(np.mean(np.concatenate([resid[s] for s in STARTS]) ** 2)))
    # THE NONE ARM: the second look with no time between. What it reads minus what the first look read (same shots).
    for s in STARTS: out[f'none.{s}'] = out[f'gap.{s}.w0']
    # the bite at each wait, ON and MID: look 2 minus plain fading from look 1's own level at this run's own level clock
    for s in ('ON', 'MID'):
        for w in WAITS_US:
            out[f'bite.{s}.w{w}'] = out[f'F.{s}.w{w}'] - out[f'L1.{s}.mean'] * np.exp(-wr[w] / tf['shared']) if np.isfinite(tf['shared']) else np.nan
    return out


def resample(D, rng):
    R = {}
    for k, looks in D.items():
        i = rng.integers(0, looks[0].shape[0], looks[0].shape[0]); R[k] = [L[i] for L in looks]
    return R


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--dir', default=os.path.join(HERE, 'data', 'fire', 'ibm_marrakesh')); ap.add_argument('--boot', type=int, default=200); ap.add_argument('--run', type=int, default=5)
    a = ap.parse_args()
    D, meta = A.load(a.dir, a.run)
    print(f"RUN {a.run}, THE NONE SHAPE: chip {meta['chip']}, {meta['shots']} shots per circuit, 36 circuits, bits {meta['all_q']} ({meta['qubit_how']})" + ('  [SYNTHETIC DRY RUN]' if meta.get('synthetic_iq') else ''))
    print(f"fired {meta.get('start_time')}  ended {meta.get('end_time')}  order seed {meta.get('order_seed')}  NO PREDICTION WRITTEN")
    # the drawn bits
    ksO = [k for k in D if k.startswith('OFF|')]; ksN = [k for k in D if k.startswith('ON|')]
    o = np.concatenate([D[k][0] for k in ksO]); n = np.concatenate([D[k][0] for k in ksN]); sep = np.abs(n.mean(0) - o.mean(0)); sd = np.sqrt((np.abs(o - o.mean(0)) ** 2).mean(0) / 2)
    print('\n-- THE DRAWN BITS: OFF-to-ON separation / OFF cloud width at look 1 (a bit that cannot be told apart is a ROW)')
    for q, s_, w_ in zip(meta['all_q'], sep, sd): print(f"  q{q:<4} separation {s_:.3g}  width {w_:.3g}  ratio {s_ / w_:.2f}" + ("   CAN'T READ (clouds overlap)" if not s_ / w_ >= 1 else ''))
    sets = {'ALL': COPIES, 'c1': [1], 'c2': [2], 'c3': [3]}
    full = {n_: quantities(D, meta, c) for n_, c in sets.items()}
    rng = np.random.default_rng(SEED); reps = {n_: {k: [] for k in full['ALL']} for n_ in sets}
    for _ in range(a.boot):
        R = resample(D, rng)
        for n_, c in sets.items():
            q = quantities(R, meta, c)
            for k in q: reps[n_][k].append(q[k])
    def wd(n_, k):
        x = np.array(reps[n_][k], float); x = x[np.isfinite(x)]
        return float(np.std(x, ddof=1)) if x.size > 1 else float('nan')
    rows = {}
    def line(k, label=None):
        v = full['ALL'][k]; cs = [full[c][k] for c in ('c1', 'c2', 'c3')]
        oth = [cs[i] - np.mean([cs[j] for j in range(3) if j != i]) for i in range(3)]
        rows[k] = {'value': v, 'width': wd('ALL', k), 'copies': cs, 'copy_widths': [wd(c, k) for c in ('c1', 'c2', 'c3')], 'copy_minus_other_two': oth}
        f = lambda x: "CAN'T READ" if not np.isfinite(x) else f'{x:.4g}'
        print(f"  {(label or k):<26} {f(v):>10} +-{f(wd('ALL', k)):<9} | copies {f(cs[0]):>9} {f(cs[1]):>9} {f(cs[2]):>9} (+-{f(wd('c1', k))}) | each minus the other two {f(oth[0]):>9} {f(oth[1]):>9} {f(oth[2]):>9}")
    def block(title, ks):
        print('\n-- ' + title); [line(k) for k in ks]
    block('LOOK 1 (no wait, no earlier look of ours): level, spread, lopsidedness', [f'L1.{s}.{x}' for s in STARTS for x in ('mean', 'var', 'skew')])
    block('THE NONE ARM: look, look again with NO time between. Look 2 minus look 1 (same shots)', [f'none.{s}' for s in STARTS])
    block('what look 2 reads, each start, each wait (0 = none)', [f'F.{s}.w{w}' for s in STARTS for w in W4])
    block('look 2 minus look 1, each start, each wait', [f'gap.{s}.w{w}' for s in STARTS for w in W4])
    block('lopsidedness of look 2', [f'L2skew.{s}.w{w}' for s in STARTS for w in W4])
    block('GAP CLOCK (us; fit on the three real waits, as in Run 2)', [f'gapclock.{k}' for k in STARTS + ['shared']])
    block('LEVEL CLOCK with one earlier look (us)', [f'levelclock.{k}' for k in STARTS + ['shared']])
    block('GAP CLOCK / LEVEL CLOCK', ['ratio.shared', 'ratio.ON'])
    block('THE BITE: look 2 minus plain fading from look 1 at this run\'s own level clock', [f'bite.{s}.w{w}' for s in ('ON', 'MID') for w in WAITS_US])
    block('what the shared gap fit leaves (rms)', ['remainder_rms'])
    json.dump({'meta': {k: meta.get(k) for k in ('chip', 'shots', 'all_q', 'start_time', 'end_time', 'order_seed', 'pub_order_seeded')}, 'rows': rows}, open(os.path.join(a.dir, f'read{a.run}.json'), 'w'), indent=1, default=float)


if __name__ == '__main__':
    main()
