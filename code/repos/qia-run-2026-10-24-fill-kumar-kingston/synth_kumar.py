"""synth_kumar.py -- plants EVERY world as per-instance <Xs> counts (binomial, 1000 shots) from his real per-setting means and his twirl-instance variance,
runs the committed readings (kumar.py) over A1 B1 B2 A2, tabulates outcomes. Gates fixed in PLAN before any run.
Planted truth: set A setting means = his job2 means, set B = his job4 means (SET worlds) or job2 means (others); twirl-instance effects N(0, tau_s^2) drawn fresh per run,
per set and setting, SHARED by the two jobs of a set (identical circuits), tau_s^2 = max(0, instance variance - binomial variance) from his data; shot noise independent per job.
Drift pattern = his job4-minus-job2 per-setting differences, total over the run (linear 0, 1/3, 2/3, 1; step 0, 1, 1, 1 after job 1). Stated projection: the record says
nothing changed (p_j = job2 baseline) unless the world offsets it.
Usage: synth_kumar.py [--quick] -> synth_results_kumar.text"""
import sys, os, json, time, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from kumar import *
from multiprocessing import Pool
def his(job):
    r = json.load(open(f'{H}/theirs/{job}_results.json')); return inst_of([s for s in r['subjobs'] if s['bench'] == 'probe'][0]['records'])
IA, IB = his('job2'), his('job4'); SETS = FACTORIAL
MUA = {s: IA[s].mean() for s in SETS}; MUB = {s: IB[s].mean() for s in SETS}
VB = {s: (1 - 0.5 * (MUA[s] ** 2 + MUB[s] ** 2)) / SHOTS for s in SETS}     # binomial variance of an instance mean
TAU = {s: float(np.sqrt(max(0.5 * (IA[s].var(ddof=1) + IB[s].var(ddof=1)) - VB[s], 0.10 * VB[s]))) for s in SETS}   # his estimate, floored at T = 1.10 (the qualification's median)
DELTA = {s: MUB[s] - MUA[s] for s in SETS}
LMC = {s: (s[1] - 2) * (s[2] - 2) for s in SETS}
G_LIN, G_STEP = [0, 1 / 3, 2 / 3, 1], [0, 1, 1, 1]
# world: (set effect on B 0/1, drift kind, shots, twirl-var spec (1 = his estimate; ('T', x) = instance variance x times binomial on every setting), B extra b_LM (log scale), DP offset (delivered - projection), runs)
WORLDS = {
 'NEITHER': (0, None, 1000, 1, 0.0, 0.0, 400),
 'SET (his job4-job2 pattern)': (1, None, 1000, 1, 0.0, 0.0, 100),
 'DRIFT linear only (his shift over the run)': (0, 'lin', 1000, 1, 0.0, 0.0, 100),
 'DRIFT step only (after job 1)': (0, 'step', 1000, 1, 0.0, 0.0, 100),
 'BOTH (linear drift + SET)': (1, 'lin', 1000, 1, 0.0, 0.0, 100),
 'BOTH (step drift + SET)': (1, 'step', 1000, 1, 0.0, 0.0, 100),
 'b_LM on B at his size (0.0038)': (0, None, 1000, 1, 0.0038, 0.0, 100),
 'b_LM on B at 3x his size (0.0114)': (0, None, 1000, 1, 0.0114, 0.0, 100),
 'STATED OFF (delivered above projection by 0.0168)': (0, None, 1000, 1, 0.0, S_DP, 100),
 'NEITHER, twirl variance heavy (T = 3)': (0, None, 1000, ('T', 3.0), 0.0, 0.0, 400),
 'LOW SHOTS (NEITHER at 100 shots)': (0, None, 100, 1, 0.0, 0.0, 400)}
NOT = {'CONSISTENT', 'CANNOT_TELL'}; ANY = None
# expected allowed outcomes (DA, SET, BLM, DP); None = not asserted in that world
EXPECT = {
 'NEITHER': (NOT, NOT, NOT, NOT), 'SET (his job4-job2 pattern)': (NOT, {'ABOVE'}, ANY, ANY),
 'DRIFT linear only (his shift over the run)': (('ABOVE',), NOT, NOT, ANY), 'DRIFT step only (after job 1)': (('ABOVE',), NOT, NOT, ANY),
 'BOTH (linear drift + SET)': (('ABOVE',), ('ABOVE',), ANY, ANY), 'BOTH (step drift + SET)': (('ABOVE',), ('ABOVE',), ANY, ANY),
 'b_LM on B at his size (0.0038)': (NOT, ANY, {'ABOVE', 'CANNOT_TELL'}, ANY), 'b_LM on B at 3x his size (0.0114)': (NOT, ANY, {'ABOVE'}, ANY),   # SET and DP not asserted in the b_LM worlds: the planted L x M factor also moves the baseline setting (1,1,1) by exp(+b)-1 (defect in the first table's expectations, fixed before any job)
 'STATED OFF (delivered above projection by 0.0168)': (NOT, NOT, NOT, {'ABOVE'}),
 'NEITHER, twirl variance heavy (T = 3)': (NOT, NOT, NOT, NOT), 'LOW SHOTS (NEITHER at 100 shots)': (NOT, NOT, NOT, NOT)}
def world_run(args):
    name, seed = args; eff, drift, shots, tv, blm_extra, dp_off, _ = WORLDS[name]; rng = np.random.default_rng(seed)
    true = {X: {s: np.clip((MUB[s] if (X == 'B' and eff) else MUA[s]) * np.exp(blm_extra * LMC[s] if (X == 'B') else 0.0) + rng.normal(0, (TAU[s] if tv == 1 else np.sqrt((tv[1] - 1) * VB[s])), K), -0.999, 0.999) for s in SETS} for X in 'AB'}
    g = {None: [0, 0, 0, 0], 'lin': G_LIN, 'step': G_STEP}[drift]; inst = {}
    for j, lab in enumerate(LABELS):
        X = SET_OF[lab]
        inst[lab] = {s: (2 * rng.binomial(shots, (1 + np.clip(true[X][s] + g[j] * DELTA[s], -0.999, 0.999)) / 2) / shots - 1.0) for s in SETS}
    p = {l: MUA[(1, 1, 1)] - dp_off for l in LABELS}
    return readings(inst, p)
def main():
    quick = '--quick' in sys.argv; out = []; t0 = time.time(); n = {w: (10 if quick else v[6]) for w, v in WORLDS.items()}; rows = {}
    print('SYNTHETIC TABLE (runs per world: ' + ', '.join(f'{w[:14]} {k}' for w, k in n.items()) + f'; band t(19) alpha {ALPHA}; scales S {S_SHIFT} / {S_BLM} / {S_DP})', flush=True)
    with Pool(8) as pool:
        for w in WORLDS: rows[w] = pool.map(world_run, [(w, 9000 + 17 * k) for k in range(n[w])]); print(f'  {w}: done {len(rows[w])} runs, {time.time()-t0:.0f} s', flush=True)
    lines = ['TRUE planted values: set A = his job2 means (baseline %.4f); set B = his job4 means (baseline %.4f) in SET worlds; shift %.4f over the run (linear 0,1/3,2/3,1 or step after job 1); twirl sd on baseline %.4f; b_LM worlds add +0.0038 / +0.0114 on B (log scale, L x M); STATED OFF %.4f; band t(19) at alpha %.2f; scales S: shift %.4f, b_LM %.4f, DP %.4f' % (MUA[(1,1,1)], MUB[(1,1,1)], DELTA[(1,1,1)], TAU[(1,1,1)], S_DP, ALPHA, S_SHIFT, S_BLM, S_DP), '']
    names = ('DA', 'SET', 'BLM', 'DP'); allpass = True
    lines.append(f'{"world":50s} {"runs":>4s}  ' + '  '.join(f'{k+" A/B/C/T":>16s}' for k in names) + '   ok DA/SET/BLM/DP        result')
    for w, res in rows.items():
        N = len(res); cnt = {k: {o: sum(r[k + '_outcome'] == o for r in res) for o in ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL')} for k in names}
        ok = []; rates = []; p = True
        for k, e in zip(names, EXPECT[w]):
            if e is None: ok.append(None); continue
            f = sum(r[k + '_outcome'] in e for r in res) / N; ok.append(f)
            if e == NOT or w.startswith('NEITHER') or w.startswith('LOW'): rates.append((k, 1 - f)); p &= (1 - f) <= 0.08
            else: p &= f >= 0.90
        allpass &= p
        lines.append(f'{w:50s} {N:4d}  ' + '  '.join(f'{cnt[k]["ABOVE"]:3d}/{cnt[k]["BELOW"]:2d}/{cnt[k]["CONSISTENT"]:3d}/{cnt[k]["CANNOT_TELL"]:3d}   ' for k in names) + '   ' + '/'.join('  - ' if o is None else f'{o:.2f}' for o in ok) + f'   {"PASS" if p else "FAIL"}')
        if w.startswith('NEITHER') or w.startswith('LOW'): lines.append('      NEITHER false-resolution rate per scored reading: ' + '  '.join(f'{k} {100*r:.1f} %' for k, r in rates) + '  (target <= about 5 %, gate <= 8 % observed)')
        lines.append('      median DA %.4f (h %.4f)  SET %.4f (h %.4f, guard %.4f)  BLM %.4f (h %.4f, guard %.4f)  DP %.4f (h %.4f)' % tuple(np.median([r[x] for r in res]) for x in ('DA', 'hDA', 'SET', 'hSET', 'guardSET', 'BLM', 'hBLM', 'guardBLM', 'DP', 'hDP')))
        lines.append('      SET unguarded false ABOVE/BELOW: %d/%d' % (sum(r['SET'] > r['hSET'] for r in res), sum(r['SET'] < -r['hSET'] for r in res)))
    lines += ['', 'ALL WORLDS PASS' if allpass else 'SOME WORLD FAILED']; txt = '\n'.join(lines); print(txt)
    open(f'{H}/synth_results_kumar{"_quick" if quick else ""}.text', 'w').write(txt + '\n')
if __name__ == '__main__': main()
