"""synth_abramson.py -- plants EVERY world in IQ records (his ten qubits' real fitted clouds, emissions and rates from known_good), runs the
committed estimator (onset.py + abramson.py) over A1 B1 B2 A2, tabulates outcomes. Gates fixed in PLAN before any run.
Usage: synth_abramson.py [--quick]  -> synth_results_abramson.text"""
import sys, os, json, time, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from onset import *; from abramson import *; from known_good import load_job
from multiprocessing import Pool
cz = json.load(open(f'{H}/known_good_abramson.json'))['czs']
def truth():
    R0, R1, a, T = load_job(1); fitsA = arm_fits(R0, R1, a); clouds = [(fit_cloud(R0[:, i]), fit_cloud(R1[:, i])) for i in range(NQ)]
    return fitsA, clouds
TRUTH = truth()
EFF = 0.0009; LIN = 0.0003; STEP = 0.0009          # per CZ-equivalent onset: his published CZ effect; linear drift per job; step (after job index 0)
WORLDS = {   # name: (cz_effect, drift kind, shots per item)
 'NEITHER': (0, None, 1000), 'CZ EFFECT only (0.09 %/CZ)': (EFF, None, 1000), 'DRIFT linear only (0.03 %/CZ-eq per job)': (0, 'lin', 1000),
 'DRIFT step only (0.09 %/CZ-eq after job 1)': (0, 'step', 1000), 'BOTH (linear drift + CZ effect)': (EFF, 'lin', 1000),
 'BOTH (step drift + CZ effect)': (EFF, 'step', 1000), 'LOW SHOTS (NEITHER at 100 shots/item)': (0, None, 100)}
# expectations (R1 guarded outcome, R2 outcome): sets of allowed outcomes; min fraction of runs that must be in the set
NOT = {'CONSISTENT', 'CANNOT_TELL'}; EXPECT = {
 'NEITHER': (NOT, NOT), 'CZ EFFECT only (0.09 %/CZ)': ({'ABOVE'}, NOT), 'DRIFT linear only (0.03 %/CZ-eq per job)': (NOT, {'ABOVE'}),
 'DRIFT step only (0.09 %/CZ-eq after job 1)': (NOT, {'ABOVE'}), 'BOTH (linear drift + CZ effect)': ({'ABOVE'}, {'ABOVE'}),
 'BOTH (step drift + CZ effect)': ({'ABOVE'}, {'ABOVE'}), 'LOW SHOTS (NEITHER at 100 shots/item)': (NOT, NOT)}
def gen_job(fit, cloud, a_i, shots, rng):
    c0, c1 = cloud; n = shots * 3
    def draw(c, k): return rng.multivariate_normal(c.mean, c.cov, k).view(complex).reshape(-1) if False else (lambda x: x[:, 0] + 1j * x[:, 1])(rng.multivariate_normal(c.mean, c.cov, k))
    A = np.array([[1 - a_i, a_i], [fit['b'], 1 - fit['b']]]); h = np.zeros((n, CYC), int); h[:, 0] = rng.random(n) < fit['pi']
    for t in range(1, CYC): h[:, t] = rng.random(n) < A[h[:, t - 1], 1]
    sym = np.empty((n, CYC), int)
    for s in (0, 1):
        m = h == s; e = np.array(fit['e_N'] if s == 0 else fit['e_P']); sym[m] = rng.choice(3, m.sum(), p=e / e.sum())
    z = np.empty((n, CYC), complex)
    for k, c in ((0, c0), (1, c1)):
        m = sym == k; z[m] = draw(c, m.sum())
    m = sym == 2; far = (c0.mean + c1.mean) / 2 + 40 * np.sqrt(np.diag(c0.cov)).max(); z[m] = far[0] + 1j * far[1]
    return z, draw(c0, shots), draw(c1, shots)
def world_run(args):
    name, seed, B = args; eff, drift, shots = WORLDS[name]; rng = np.random.default_rng(seed); fitsA, clouds = TRUTH
    sym = {}
    for j, lab in enumerate(LABELS):
        isB = lab.startswith('B'); arm = np.empty((shots * 3, CYC, NQ), complex); R0 = np.empty((shots, NQ), complex); R1 = np.empty((shots, NQ), complex)
        for i in range(NQ):
            a_i = fitsA[i]['a'] + (eff * cz[i] if isB else 0.0)
            if drift == 'lin': a_i += LIN * cz[i] * j
            if drift == 'step': a_i += STEP * cz[i] * (j >= 1)
            z, r0, r1 = gen_job(fitsA[i], clouds[i], max(a_i, 1e-6), shots, rng); arm[:, :, i] = z; R0[:, i] = r0; R1[:, i] = r1
        sym[lab] = to_symbols(R0, R1, arm.reshape(shots * 3, -1))
    return readings(sym, cz, B=B, seed=seed)
def main():
    quick = '--quick' in sys.argv; B = 40; out = []; t0 = time.time()
    n = {w: (10 if quick else (100 if (w == 'NEITHER' or w.startswith('LOW')) else 40)) for w in WORLDS}
    only = [a[7:] for a in sys.argv if a.startswith('--only=')]
    if only: n = {w: (k if any(o in w for o in only) else 0) for w, k in n.items()}
    print('SYNTHETIC TABLE (runs per world: ' + ', '.join(f'{w[:12]} {k}' for w, k in n.items()) + f'; null draws per run {B}; scale S {S_SCALE} %/CZ)', flush=True)
    rows = {}
    with Pool(14) as pool:
        for w in WORLDS:
            if not n[w]: rows[w] = []; continue
            res = pool.map(world_run, [(w, 7000 + 17 * k, B) for k in range(n[w])]); rows[w] = res
            print(f'  {w}: done {len(res)} runs, {time.time()-t0:.0f} s', flush=True)
    lines = ['TRUE planted values: CZ effect %.2f %%/CZ; linear drift %.2f %%/CZ-eq per job; step %.2f %%/CZ-eq after job index 0; onset of A from his real fits; scale S %.2f %%/CZ' % (100 * EFF, 100 * LIN, 100 * STEP, S_SCALE), '']
    allpass = True; hdr = f'{"world":46s} {"runs":>4s} {"R1 ABOVE/BELOW/CONS/CT":>24s} {"R2 ABOVE/BELOW/CONS/CT":>24s} {"R1 ok":>6s} {"R2 ok":>6s}  result'
    lines.append(hdr)
    for w, res in rows.items():
        if not res: continue
        c1 = {k: sum(r['R1_outcome'] == k for r in res) for k in ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL')}
        c2 = {k: sum(r['R2_outcome'] == k for r in res) for k in c1}; e1, e2 = EXPECT[w]; N = len(res)
        ok1 = sum(r['R1_outcome'] in e1 for r in res) / N; ok2 = sum(r['R2_outcome'] in e2 for r in res) / N
        need = 0.90 if (e1 == {'ABOVE'} or e2 == {'ABOVE'}) else 0.92   # power worlds: >=90 % resolve; null-type worlds: false rate <= 8 %
        if w == 'NEITHER' or w.startswith('LOW'):   # NEITHER false rate per scored reading: <= 5 % target, gate <= 8 % observed over 100 runs
            fr1 = 1 - ok1; fr2 = 1 - ok2; p = fr1 <= 0.08 and fr2 <= 0.08
        else:
            p = (ok1 >= (0.90 if e1 == {'ABOVE'} else 0.92)) and (ok2 >= (0.90 if e2 == {'ABOVE'} else 0.92))
        allpass &= p
        lines.append(f'{w:46s} {N:4d} {c1["ABOVE"]:5d}/{c1["BELOW"]:2d}/{c1["CONSISTENT"]:3d}/{c1["CANNOT_TELL"]:3d}     {c2["ABOVE"]:5d}/{c2["BELOW"]:2d}/{c2["CONSISTENT"]:3d}/{c2["CANNOT_TELL"]:3d}   {ok1:6.2f} {ok2:6.2f}  {"PASS" if p else "FAIL"}')
        if w == 'NEITHER' or w.startswith('LOW'): lines.append(f'      NEITHER false-resolution rate: R1 {100*(1-ok1):.1f} %  R2 {100*(1-ok2):.1f} %  (per scored reading; target <= about 5 %, gate <= 8 % observed)')
        lines.append('      median R1 %.4f (h %.4f)  median R2 %.4f (h %.4f)  %%/CZ; R1 raw (no guard) ABOVE/BELOW %d/%d' % (np.median([r['R1'] for r in res]), np.median([r['h1'] for r in res]), np.median([r['R2'] for r in res]), np.median([r['h2'] for r in res]), sum(r['R1_raw_outcome'] == 'ABOVE' for r in res), sum(r['R1_raw_outcome'] == 'BELOW' for r in res)))
    lines.append(''); lines.append('ALL WORLDS PASS' if allpass else 'SOME WORLD FAILED')
    txt = '\n'.join(lines); print(txt)
    open(f'{H}/synth_results_abramson{"_quick" if quick else ("_partial" if only else "")}.text', 'w').write(txt + '\n')
if __name__ == '__main__': main()
