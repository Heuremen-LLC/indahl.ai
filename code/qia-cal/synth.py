"""synth.py: planted worlds through callib.analyse (PLAN.md). Prints false-call floors and recovery; exits nonzero if an expectation fails."""
import numpy as np, sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import callib as C
SRO, ST1, Q = 1000, 500, 156
def world(rng, stated, true):
    p10 = np.array([t['p10'] for t in true]); p01 = np.array([t['p01'] for t in true]); t1 = np.array([t['t1'] for t in true])
    c0 = rng.binomial(SRO, p10); c1z = rng.binomial(SRO, p01)
    d = np.array(C.DELAYS_US[1:], float); p1 = p10[:, None] + (1 - p01 - p10)[:, None] * np.exp(-d[None, :] / t1[:, None])
    ones = rng.binomial(ST1, np.clip(p1, 0, 1))
    return C.analyse(c0, c1z, ones, SRO, ST1, {i: stated[i] for i in range(Q)})
def stated_set(rng):   # Note 1: IBM's readout figures are counts out of 4,096
    return [dict(p10=float(rng.binomial(4096, rng.uniform(0.002, 0.03)) / 4096), p01=float(rng.binomial(4096, rng.uniform(0.005, 0.05)) / 4096), t1=float(rng.uniform(30, 350))) for _ in range(Q)]
ok = True; R = 40
fals = dict(p10=0, p01=0, t1=0); ct = 0
for s in range(R):
    rng = np.random.default_rng(1000 + s); st = stated_set(rng); rows, kg = world(rng, st, st)
    for k in fals: fals[k] += sum(r[k + '_outcome'] in ('ABOVE', 'BELOW') for r in rows)
    ct += sum(r['t1_outcome'] == 'CANNOT_TELL' for r in rows)
print('NULL world (IBM exactly right), %d runs x %d qubits: false calls per run p10 %.2f, p01 %.2f, t1 %.2f; T1 cannot-tell per run %.1f' % (R, Q, fals['p10'] / R, fals['p01'] / R, fals['t1'] / R, ct / R))
ok &= all(v / R < 1.0 for v in fals.values())
hit = dict(ro_dn=0, t1_dn=0, ro_up=0, t1_up=0, both=0, wrong=0)
for s in range(R):
    rng = np.random.default_rng(2000 + s); st = stated_set(rng); tr = [dict(x) for x in st]
    for i in range(10): tr[i]['p10'] *= 3; tr[i]['p01'] *= 3          # readout worse than stated -> IBM figure BELOW
    for i in range(10, 20): tr[i]['t1'] *= 0.4                         # T1 shorter than stated   -> IBM figure ABOVE
    for i in range(20, 30): tr[i]['p01'] *= 0.25                       # readout better than stated -> IBM figure ABOVE
    for i in range(30, 40): tr[i]['t1'] = min(tr[i]['t1'] * 2.5, 600)  # T1 longer than stated    -> IBM figure BELOW
    for i in range(40, 50): tr[i]['p01'] *= 3; tr[i]['t1'] *= 0.4      # BOTH on one qubit
    rows, kg = world(rng, st, tr)
    hit['ro_dn'] += sum(rows[i]['p01_outcome'] == 'BELOW' for i in range(10)); hit['t1_dn'] += sum(rows[i]['t1_outcome'] == 'ABOVE' for i in range(10, 20))
    hit['ro_up'] += sum(rows[i]['p01_outcome'] == 'ABOVE' for i in range(20, 30)); hit['t1_up'] += sum(rows[i]['t1_outcome'] == 'BELOW' for i in range(30, 40))
    hit['both'] += sum(rows[i]['p01_outcome'] == 'BELOW' and rows[i]['t1_outcome'] == 'ABOVE' for i in range(40, 50))
    hit['wrong'] += sum(rows[i]['t1_outcome'] == 'BELOW' for i in range(10, 20)) + sum(rows[i]['p01_outcome'] == 'ABOVE' for i in range(10)) + sum(rows[i]['p01_outcome'] == 'BELOW' for i in range(20, 30)) + sum(rows[i]['t1_outcome'] == 'ABOVE' for i in range(30, 40))
print('PLANTED, found (of 10 qubits x %d runs): readout x3 %.0f%%, T1 x0.4 %.0f%%, readout x0.25 %.0f%%, T1 x2.5 %.0f%%, BOTH on one qubit %.0f%%; wrong direction %d' % (R,
      *[100 * hit[k] / (10 * R) for k in ('ro_dn', 't1_dn', 'ro_up', 't1_up', 'both')], hit['wrong']))
ok &= hit['wrong'] == 0 and hit['ro_dn'] / (10 * R) > 0.8 and hit['t1_dn'] / (10 * R) > 0.6
rng = np.random.default_rng(3000); st = stated_set(rng); tr = [dict(x) for x in st]
for i in range(5): tr[i]['t1'] = 2.0
rows, kg = world(rng, st, tr); short = [rows[i]['t1_outcome'] for i in range(5)]
print('SHORT T1 (true 2 us, shortest delay 15 us):', short); ok &= all(o in ('CANNOT_TELL', 'ABOVE') for o in short)
rng = np.random.default_rng(4000); st = stated_set(rng); tr = [dict(x, p10=x['p10'] * 4, p01=x['p01'] * 4) for x in st]
rows, kg = world(rng, st, tr); print('GATE (all readout x4): known-good', kg['known_good']); ok &= kg['known_good'] == 'failed'
print('SYNTH', 'PASSED' if ok else 'FAILED'); sys.exit(0 if ok else 1)
