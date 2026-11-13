"""synth.py -- planted worlds for the 2603.13536 readings (readings.py), run BEFORE any job.  Same 10 instances (seeds 100..109, n = 12; the paper's 5 = main.py's 100..104 plus 5 more),
same shot plan (trot arm 3000 shots, ctrl arm 3000 shots), the analysis exactly as committed.  Worlds:
  NEITHER  D1 planted null (AS-SQD replaced by 5 other random-expansion seeds), trot and ctrl both UNIFORM + readout error (1 % 0->1, 2 % 1->0)
  H1       D1 real, trot and ctrl both UNIFORM + readout (D2 null)
  H2       D1 planted null, trot = INFORMATIVE (50 % paper's contaminated ground 0.8 p0 + 0.2 p1, 50 % uniform) + readout, ctrl uniform
  BOTH     D1 real, trot INFORMATIVE, ctrl uniform
  ASYM     apparatus artefact: D1 planted null, trot and ctrl both uniform with heavy readout asymmetry (2 % 0->1, 10 % 1->0)
  ANTI     D1 real, trot concentrated on high-diagonal-energy strings (p ~ exp(+H_kk/2)) + readout, ctrl uniform
  IDEAL    D1 real, trot = noiseless rebuilt Trotter circuit (2400 shots t=0.6, 600 shots t=1.2) + readout, ctrl uniform
Null readings (planted truth 0): false resolution = ABOVE or BELOW.  Real readings: truth = mean point value over the world's runs;
scored on wrong-direction calls (must be <= ~5 %) and resolution in the truth's direction (power, printed).
Usage: python -I src/synth.py [runs_null runs_other]  -> synth_results_2603.13536.text"""
import sys, os, json, time, zlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np
from multiprocessing import Pool
from assqd import Model, sample, merge
from readings import analyze
from circuits import trotter, ideal_probs, SH0, SH1, T0, T1, SHOTS
N = 12; SEEDS = list(range(100, 110)); _G = {}

def ro(p, a, b):
    """per-qubit confusion: P(1|0) = a, P(0|1) = b on every qubit"""
    A = np.array([[1 - a, b], [a, 1 - b]]); q = p.reshape((2,) * N)
    for ax in range(N): q = np.moveaxis(np.tensordot(A, q, axes=([1], [ax])), 0, ax)
    q = q.reshape(-1); return q / q.sum()

def init():
    Ms = [Model(N, s) for s in SEEDS]; U = np.ones(1 << N) / (1 << N)
    d = dict(Ms=Ms, U=ro(U, 0.01, 0.02), UA=ro(U, 0.02, 0.10), INFO=[], ANTI=[], I0=[], I1=[])
    for M in Ms:
        d['INFO'].append(ro(0.5 * (0.8 * M.p0 + 0.2 * M.p1) + 0.5 * U, 0.01, 0.02))
        w = np.exp(+(M.diag - M.diag.max()) / 2); d['ANTI'].append(ro(w / w.sum(), 0.01, 0.02))
        d['I0'].append(ro(ideal_probs(trotter(N, M.terms, T0)), 0.01, 0.02)); d['I1'].append(ro(ideal_probs(trotter(N, M.terms, T1)), 0.01, 0.02))
    _G.update(d)

WORLDS = {  # name: (d1_null, trot kind, ctrl kind, expect_o1, expect_o2)   expect: 'null' or 'real'
    'NEITHER': (True, 'U', 'U', 'null', 'null'), 'H1': (False, 'U', 'U', 'real', 'null'), 'H2': (True, 'INFO', 'U', 'null', 'real'),
    'BOTH': (False, 'INFO', 'U', 'real', 'real'), 'ASYM': (True, 'UA', 'UA', 'null', 'null'), 'ANTI': (False, 'ANTI', 'U', 'real', 'real'),
    'IDEAL': (False, 'IDEAL', 'U', 'real', 'real')}

def draw(kind, i, rng):
    if kind == 'U': return sample(rng, _G['U'], SHOTS)
    if kind == 'UA': return sample(rng, _G['UA'], SHOTS)
    if kind in ('INFO', 'ANTI'): return sample(rng, _G[kind][i], SHOTS)
    if kind == 'IDEAL': return merge(sample(rng, _G['I0'][i], SH0), sample(rng, _G['I1'][i], SH1))

def one(args):
    w, k = args
    if not _G: init()
    d1n, tk, ck, _, _ = WORLDS[w]; rng = np.random.default_rng(zlib.crc32(f"{w}-{k}".encode()))
    trots = [draw(tk, i, rng) for i in range(len(SEEDS))]; ctrls = [draw(ck, i, rng) for i in range(len(SEEDS))]
    r = analyze(_G['Ms'], trots, ctrls, seed=k + 1, d1_null=d1n)
    return w, k, r['D1'], r['D2'], r['o1'], r['o2'], r['head']

if __name__ == '__main__':
    rn = int(sys.argv[1]) if len(sys.argv) > 1 else 200; ro_ = int(sys.argv[2]) if len(sys.argv) > 2 else 100; t0 = time.time()
    jobs = [(w, k) for w in WORLDS for k in range(rn if WORLDS[w][3] == 'null' and WORLDS[w][4] == 'null' else ro_)]
    with Pool(4, initializer=init) as P: res = P.map(one, jobs, chunksize=4)
    out = [f'synth for 2603.13536 readings (readings.py: t(n-1) 97.5 %, n = {len(SEEDS)} instances, M = 0.5 decade), {len(jobs)} runs, {time.time()-t0:.0f} s, Pool(4)']
    allpass = True; worst_null = 0.0
    for w, (d1n, tk, ck, e1, e2) in WORLDS.items():
        R = [r for r in res if r[0] == w]; n = len(R); line = [f'{w:8s} n={n:3d} trot={tk:5s} ctrl={ck:2s}']
        for j, (key, ex) in enumerate((('D1', e1), ('D2', e2))):
            pts = np.array([r[2 + j][0] for r in R]); hw = np.median([(r[2 + j][2] - r[2 + j][1]) / 2 for r in R]); oc = [r[4 + j] for r in R]
            cnt = {o: oc.count(o) for o in ('BELOW', 'ABOVE', 'CONSISTENT', 'CANNOT_TELL')}
            if ex == 'null':
                fr = (cnt['BELOW'] + cnt['ABOVE']) / n; worst_null = max(worst_null, fr); ok = fr <= 0.06
                line.append(f'{key} NULL: mean {pts.mean():+.3f}, median half-width {hw:.3f}; false resolution {100*fr:.1f} % {cnt} {"ok" if ok else "FAIL"}')
            else:
                tr = pts.mean(); se = pts.std(ddof=1) / np.sqrt(n); good = 'BELOW' if tr < 0 else 'ABOVE'; bad = 'ABOVE' if tr < 0 else 'BELOW'
                wr = cnt[bad] / n; pw = cnt[good] / n; ok = wr <= 0.06
                line.append(f'{key} REAL: truth (mean point) {tr:+.3f} +- {se:.3f}, median half-width {hw:.3f}; resolves {good} {100*pw:.0f} %, wrong direction {100*wr:.1f} % {cnt} {"ok" if ok else "FAIL"}')
            allpass &= ok
        heads = [r[6] for r in R]; line.append('headline ' + str({h: heads.count(h) for h in ('FILL', 'GAP', 'CLEAN', 'CANNOT_TELL')}))
        out.append(' | '.join(line))
    out.append(f'worst null false-resolution rate {100*worst_null:.1f} % (target <= ~5 %); ALL WORLDS {"PASS" if allpass else "FAIL"}')
    txt = '\n'.join(out); print(txt); open(os.path.join(HERE, '..', 'synth_results_2603.13536.text'), 'w').write(txt + '\n')
    json.dump([list(map(lambda x: x if not isinstance(x, tuple) else list(x), r)) for r in res], open(os.path.join(HERE, '..', 'synth_raw_2603.13536.json'), 'w'))
