"""Floor and ceiling of D_DATE (Addendum 1 to PLAN_ZHUKOV_R2): two simulated dates from synth_zhukov.gen, D_DATE through date_reading.ours, single process."""
import sys, os, collections
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import zhukov as Z, synth_zhukov as S, date_reading as DR
def dd(w1, w2, rng, method='strang8'):
    c1 = S.gen(dict(S.DEF, **w1), rng)[0]; c2 = S.gen(dict(S.DEF, **w2), rng)[0]
    m1, h1, _ = DR.ours(c1, method); m2, h2, _ = DR.ours(c2, method); d = m2 - m1; hw = float(np.hypot(h1, h2))
    return Z.outcome_vs_zero(d - hw, d + hw, Z.SCALE_C), d, hw
if __name__ == '__main__':
    rng = np.random.default_rng(20261029)
    for name, w1, w2, R, expect in (('NEITHER (same truth both dates)', {}, {}, 200, 'CONSISTENT'), ('PHASE +25 deg on date 2', {}, {'phase': 25.0}, 40, 'ABOVE'), ('DRIFT within each date, none between', {'lin': 0.02}, {'lin': 0.02}, 40, 'CONSISTENT')):
        got = collections.Counter(); ds = []
        for _ in range(R):
            o, d, hw = dd(w1, w2, rng); got[o] += 1; ds.append((d, hw))
        rate = got[expect] / R; ds = np.array(ds)
        print('%-40s %d runs: %s ; expected %s in %.0f%% ; median D %+.1f, median half-width %.1f' % (name, R, dict(got), expect, 100 * rate, np.median(ds[:, 0]), np.median(ds[:, 1])), flush=True)
