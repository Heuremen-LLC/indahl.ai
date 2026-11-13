"""synth_cauca.py -- the analysis (cauca.py) run on PLANTED data before any job. Truths are THEIR OWN published numbers: A = their L2 raw means, B = their L0 raw means,
twin = their Table A1 twin. Worlds plant drift, level effects and twin gaps; EXPECTED outcomes are derived from the planted truth against the pre-fixed scales
(a cell is expected CANNOT_TELL if the analytic null half-width exceeds the scale; ABOVE/BELOW if |truth| > 2.5 x half-width; CONSISTENT if truth is exactly 0 and resolvable;
other cells are not scored). Every world must pass every scored cell."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, cauca as C
rng = np.random.default_rng(5); n = C.REPS * C.SHOTS
pA = C.PUB_RAW['L2'].copy(); pB = C.PUB_RAW['L0'].copy(); TW = C.PUB_TWIN.copy()
TWFIX = np.array([0.9624, 0.9235, 0.9096, 0.884, 0.8597, 0.8204, 0.7791, 0.7404])   # q1 readout entry replaced by an ordinary neighbour's (TWIN_RESCALE.md s.6)
big = np.array([N >= 6 for N in C.NS], float)
def jobs_from(ps):
    return [(rng.binomial(n, np.clip(p, 0, 1)).astype(float), np.full(8, float(n))) for p in ps]
def hw(p): return 1.96 * np.sqrt(p * (1 - p) / n)
W = {}
W['STABLE (their L2/L0 means, no drift, twin = their twin)'] = dict(ps=[pA, pB, pB, pA], tw=TW, r1=np.zeros(8), r2=pA - pB, r4=(TW - pA) - C.G0)
W['LINEAR DRIFT -0.02/job at N>=6, twin = their twin'] = dict(ps=[pA - 0.02 * 1 * big, pB - 0.02 * 2 * big, pB - 0.02 * 3 * big, pA - 0.02 * 4 * big], tw=TW, r1=-0.06 * big, r2=pA - pB, r4=(TW - (pA - 0.05 * big)) - C.G0)
W['STEP DRIFT -0.06 after job 2 at N>=6'] = dict(ps=[pA, pB, pB - 0.06 * big, pA - 0.06 * big], tw=TW, r1=-0.06 * big, r2=pA - pB, r4=(TW - (pA - 0.03 * big)) - C.G0)
W['NEITHER (B = A, no drift)'] = dict(ps=[pA, pA, pA, pA], tw=TW, r1=np.zeros(8), r2=np.zeros(8), r4=(TW - pA) - C.G0)
W['TWIN GAP GONE (hardware = twin)'] = dict(ps=[TW, pB, pB, TW], tw=TW, r1=np.zeros(8), r2=TW - pB, r4=np.zeros(8) - C.G0)
W['Q1 READOUT FIXED IN THE TWIN (hardware = theirs)'] = dict(ps=[pA, pB, pB, pA], tw=TWFIX, r1=np.zeros(8), r2=pA - pB, r4=(TWFIX - pA) - C.G0)
def expect(truth, scale, h):
    out = []
    for t, s, hh in zip(truth, scale, h):
        if hh > s: out.append('CANNOT_TELL')
        elif abs(t) > 2.5 * hh: out.append('ABOVE' if t > 0 else 'BELOW')
        elif t == 0: out.append('CONSISTENT')
        else: out.append(None)
    return out
allok = True
for name, w in W.items():
    jobs = jobs_from(w['ps']); lines, res = C.analyse(jobs, {1: w['tw'], 4: w['tw']}, rng)
    print('==', name); print('\n'.join(lines))
    h1 = hw(pA) * np.sqrt(2); h2 = hw(pA) * np.sqrt(2) / np.sqrt(2) * 1.0   # R2 pools 2 jobs per side: 2n shots each side
    h2 = 1.96 * np.sqrt(2 * pA * (1 - pA) / (2 * n)); h4 = hw(pA) / np.sqrt(2)
    ex = {'R1': expect(w['r1'], C.S_GAP, h1), 'R2': expect(w['r2'], C.S_LVL, h2), 'R4': expect(w['r4'], C.S_GAP, h4)}
    ok = True; scored = 0
    for k in ('R1', 'R2', 'R4'):
        for i, (e, o) in enumerate(zip(ex[k], res[k])):
            if e is None: continue
            scored += 1
            if e != o: ok = False; print(f'   MISMATCH {k} N={C.NS[i]}: expected {e} got {o}')
    print(f'   -> {"PASS" if ok else "FAIL"} ({scored} scored cells)'); allok &= ok
print('ALL WORLDS', 'PASS' if allok else 'FAIL')
# false-alarm rate on NEITHER over 300 seeds (information only)
fa = 0; tot = 0
for s in range(300):
    r = np.random.default_rng(1000 + s); jobs = [(r.binomial(n, pA).astype(float), np.full(8, float(n))) for _ in range(4)]
    _, res = C.analyse(jobs, {1: TW, 4: TW}, r)
    for k in ('R1', 'R2'):
        for o, sc in zip(res[k], (C.S_GAP if k == 'R1' else C.S_LVL)):
            if o != 'CANNOT_TELL': tot += 1; fa += o != 'CONSISTENT'
print(f'NEITHER x300 seeds: R1+R2 resolvable cells {tot}, non-CONSISTENT {fa} ({100 * fa / max(tot, 1):.1f} %; nominal 5 %)')
