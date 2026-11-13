"""known_good.py -- GATE 2: reproduce his published Kingston numbers (full paper l.1032-1034) from his raw IQ with onset.py (own code)."""
import sys, os, gzip, json, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from onset import *
from qiskit import qpy
def load_job(j):
    z = np.load(f'{H}/theirs/ibm_kingston-2026-10-14-exp3-{j}/results.npz'); run = json.load(open(f'{H}/theirs/ibm_kingston-2026-10-14-exp3-{j}/run.json'))
    R0, R1 = z['0/m_iq'], z['1/m_iq']; arm = np.concatenate([z[f'{k}/m_iq'] for k in (2, 3, 4)])
    d = {i['duration_dt'] for i in run['items'][2:]}; assert len(d) == 1
    return R0, R1, arm, d.pop() / 30 * run['dt'] * 1e6
def cz_per_qubit():
    cs = qpy.load(gzip.open(f'{H}/theirs/ibm_kingston-2026-10-14-exp3-2/circuits.qpy.gz', 'rb')); c = cs[2]
    meas = {c.find_bit(i.clbits[0]).index: c.find_bit(i.qubits[0]).index for i in c.data if i.operation.name == 'measure'}
    qs = [meas[k] for k in range(10)]                                    # measured qubit of clbit 0..9 (first cycle)
    cnt = {q: 0 for q in qs}
    for i in c.data:
        if i.operation.name == 'cz':
            for q in i.qubits:
                qq = c.find_bit(q).index
                if qq in cnt: cnt[qq] += 1
    return qs, [cnt[q] // (30) for q in qs]                               # per cycle (30 cycles per arm copy)
if __name__ == '__main__':
    qs, cz = cz_per_qubit(); print('measured qubits', qs, 'CZ per cycle (arm B)', cz)
    fits = {}
    for arm, j in (('A', 1), ('B', 2)):
        R0, R1, a, T = load_job(j); fits[arm] = arm_fits(R0, R1, a); print(arm, 'period us', round(T, 4))
    life = {k: [lifetime_us(f['b'], 4.864) for f in v] for k, v in fits.items()}
    mA, mB = float(np.median(life['A'])), float(np.median(life['B']))
    per_cz = float(np.median([(onset(fits['B'][i]) - onset(fits['A'][i])) / cz[i] for i in range(10)]))
    print(f'median persistent-state lifetime  A (no CZ) {mA:.2f} us   B (CZ) {mB:.2f} us   paired B-A onset per CZ {100*per_cz:.4f} %')
    print('present A', [f['present'] for f in fits['A']], 'present B', [f['present'] for f in fits['B']])
    print('onset A', [round(onset(f), 4) for f in fits['A']]); print('onset B', [round(onset(f), 4) for f in fits['B']])
    # uncertainty: bootstrap over the ten qubits (units), same statistic
    rng = np.random.default_rng(0); L = []
    for _ in range(4000):
        ix = rng.integers(0, 10, 10); L.append((np.median([life['A'][i] for i in ix]), np.median([life['B'][i] for i in ix]), np.median([(onset(fits['B'][i]) - onset(fits['A'][i])) / cz[i] for i in ix])))
    L = np.array(L); lo, hi = np.percentile(L, [2.5, 97.5], 0)
    print('qubit-bootstrap 95%%:  A [%.1f, %.1f] us  B [%.1f, %.1f] us  per-CZ [%.4f, %.4f] %%' % (lo[0], hi[0], lo[1], hi[1], 100 * lo[2], 100 * hi[2]))
    pub = dict(A=40, B=32, cz=0.09)
    ok = abs(mA - 40) < 0.5 and abs(mB - 32) < 0.5 and abs(100 * per_cz - 0.09) < 0.005
    inint = lo[0] <= 40 <= hi[0] and lo[1] <= 32 <= hi[1] and 100 * lo[2] <= 0.09 <= 100 * hi[2]
    print('published (rounded as printed): A 40 us, B 32 us, 0.09 % per CZ; agree within rounding:', ok, '; published inside my qubit-bootstrap interval:', inint)
    json.dump(dict(A_us=mA, B_us=mB, per_cz_pct=100 * per_cz, boot_lo=list(lo), boot_hi=list(hi), agree_rounding=bool(ok), inside=bool(inint), czs=cz, qubits=qs), open(f'{H}/known_good_abramson.json', 'w'), default=float)
