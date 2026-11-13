"""listen_discarded.py -- the half every push reading threw away (Bones, by hand, 10/2 evening). Outside every freeze; reads landed records only.
Every OFF-push number so far is the projection of each raw dot onto its bit's OFF->ON line. This keeps the rest of the dot:
  along   = position along OFF->ON (OFF = 0, ON = 1, lone looks)       -- what we always read
  perp    = position across that line, same units                        -- the discarded half
  spread  = across-line spread beyond what the two clouds carry          -- a third cloud off the line would widen it
  neither = shots more than 3 widths from BOTH clouds                    -- the edge and the off-both
Each arm is held against a plain two-cloud mix with the same along (OFF cloud and ON cloud in that proportion): the mix carries
perp 0, its own spread, its own neither. Means over readable bits (clouds > 4 widths apart), widths from shot resampling, three reads.
No verdict word.  python listen_discarded.py push|hold"""
import os, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, 'data', 'fire', 'ibm_pittsburgh'); NB = 100
RUNS = {'push': ([91, 92, 93], 'OFF|p0__L1', 'ON|p0__L1'), 'hold': ([71, 72, 73], 'OFF|w0__L1', 'ON|w0__L1')}


def per_bit(A, off, on):
    c0 = A[off].mean(0); c1 = A[on].mean(0); d = c1 - c0
    s0 = np.sqrt((np.abs(A[off] - c0) ** 2).mean(0) / 2); s1 = np.sqrt((np.abs(A[on] - c1) ** 2).mean(0) / 2)
    good = np.abs(d) / s0 > 4
    def coords(x):
        u = (x - c0) * np.conj(d) / np.abs(d) ** 2
        return np.real(u), np.imag(u)
    def neither(x):
        return ((np.abs(x - c0) > 3 * s0) & (np.abs(x - c1) > 3 * s1)).mean(0)
    out = {}
    for k, x in A.items():
        a, p = coords(x)
        out[k] = {'along': a.mean(0), 'perp': p.mean(0), 'pvar': p.var(0), 'neither': neither(x)}
    # the two clouds as templates for the mix
    t0 = out[off]; t1 = out[on]
    for k, v in out.items():
        f = np.clip(v['along'], 0, 1)
        v['pvar_x'] = v['pvar'] - ((1 - f) * t0['pvar'] + f * t1['pvar'])
        v['neither_x'] = v['neither'] - ((1 - f) * t0['neither'] + f * t1['neither'])
    return out, good


def read(r, off, on, rng):
    z = np.load(os.path.join(D, f'run{r}_results.npz')); A = {k: np.asarray(z[k]).astype(complex) for k in z.files}
    base, good = per_bit(A, off, on)
    boots = []
    for _ in range(NB):
        B = {}
        for k, v in A.items():
            B[k] = v[rng.integers(0, v.shape[0], v.shape[0])]
        b, _ = per_bit(B, off, on); boots.append(b)
    res = {}
    for k in A:
        res[k] = {}
        for q in ('along', 'perp', 'pvar_x', 'neither_x'):
            m = base[k][q][good].mean(); w = np.std([b[k][q][good].mean() for b in boots])
            res[k][q] = (m, w)
    return res, int(good.sum())


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else 'push'
    runs, off, on = RUNS[which]; rng = np.random.default_rng(20261003)
    R = []; nb = []
    for r in runs:
        res, n = read(r, off, on, rng); R.append(res); nb.append(n)
    print(f'THE DISCARDED HALF, {which} runs {runs}, ibm_pittsburgh; readable bits {nb}. Units: the bit\'s own OFF->ON distance.')
    print('   each quantity: read1 read2 read3 | all three (width) | each minus the other two')
    for k in sorted(R[0]):
        print(f'  {k}')
        for q, lab in (('along', 'along (what we always read)'), ('perp', 'perp (across the line)'), ('pvar_x', 'spread beyond the two-cloud mix'), ('neither_x', 'neither, beyond the two-cloud mix')):
            v = np.array([x[k][q][0] for x in R]); w = np.array([x[k][q][1] for x in R])
            m = v.mean(); mw = np.sqrt((w ** 2).sum()) / len(v); oth = [v[i] - np.delete(v, i).mean() for i in range(len(v))]
            print(f'     {lab:<36} ' + '  '.join(f'{a:+.4f}({b:.4f})' for a, b in zip(v, w)) + f'  | {m:+.4f} ({mw:.4f}) | ' + ' '.join(f'{o:+.4f}' for o in oth))


if __name__ == '__main__':
    main()
