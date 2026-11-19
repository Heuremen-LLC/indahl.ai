"""analyze_keystone.py -- every reading of PLAN_KEYSTONE.md.text, four outcomes, copies A and B and pooled; FINAL = pooled if A and B give the
same outcome, else CANNOT_TELL. Used unchanged by synth_keystone.py (planted data) and on the real jobs (--real CHIP).
Rulers: S and P parts -- median over qubits (pairs) with a 2,000-draw bootstrap over qubits (pairs), 99 % band (widened from the control
run's 95 % before any job: the first synthetic pass gave 22 % false calls, synth_results_keystone_FIRST.text). THE SPLIT: per-qubit residual
of a corrected arm regressed on the kick read in the OTHER copy (Theil-Sen slope, independent shot noise in x and y), bootstrap over qubits.
C part -- shot bootstrap, 400 draws, 99 % band, as the committed Pooters run."""
import json, os, sys, itertools
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import keystone as K
import pooters as PW
from analyze import wrap

KG_MEDIAN = {'ibm_kingston': -2.864, 'ibm_marrakesh': -2.393}   # committed 21 Oct pooled median kick, same estimator (wrapped, N = 8)

def med_reading(x, rng, ref=0.0, B=2000):
    m, lo, hi, n = K.boot_med(x, rng, B)
    return dict(v=m, lo=lo, hi=hi, n=n, out=K.outcome(lo, hi, ref))

def theil_sen(x, y):
    x = np.asarray(x); y = np.asarray(y); i, j = np.triu_indices(len(x), 1); dx = x[j] - x[i]; ok = np.abs(dx) > 1e-9
    return float(np.median((y[j] - y[i])[ok] / dx[ok]))
def split_reading(xA, yB, xB, yA, rng, B=600):
    """copy A reading = slope(y_A on x_B); copy B = slope(y_B on x_A); pooled = mean of both; bootstrap over qubits, 99 %.
    Returns readings vs 0 (everything given back) and vs 1 (nothing given back)."""
    n = len(xA); out = {}
    def one(f):
        v = f(np.arange(n)); bs = [f(rng.integers(0, n, n)) for _ in range(B)]; lo, hi = np.percentile(bs, [0.5, 99.5]); return v, lo, hi
    fa = lambda ix: theil_sen(xB[ix], yA[ix]); fb = lambda ix: theil_sen(xA[ix], yB[ix]); fp = lambda ix: 0.5 * (fa(ix) + fb(ix))
    for lab, f in (('A', fa), ('B', fb), ('pooled', fp)):
        v, lo, hi = one(f); out[lab] = (dict(v=v, lo=lo, hi=hi, n=n, out=K.outcome(lo, hi, 0.0)), dict(v=v, lo=lo, hi=hi, n=n, out=K.outcome(lo, hi, 1.0)))
    return out

def split_diff(R, a1, a2, rng, B=600):
    """slope(a1) - slope(a2), same resampled qubits for both (the time ladder: old table minus fresh table)"""
    xA, xB = R['A']['M']['kick'], R['B']['M']['kick']; n = len(xA); out = {}
    def sl(a, ix, which):
        return theil_sen(xB[ix], R['A'][a]['kick'][ix]) if which == 'A' else theil_sen(xA[ix], R['B'][a]['kick'][ix])
    fs = {'A': lambda ix: sl(a1, ix, 'A') - sl(a2, ix, 'A'), 'B': lambda ix: sl(a1, ix, 'B') - sl(a2, ix, 'B')}
    fs['pooled'] = lambda ix: 0.5 * (fs['A'](ix) + fs['B'](ix))
    for lab, f in fs.items():
        v = f(np.arange(n)); bs = [f(rng.integers(0, n, n)) for _ in range(B)]; lo, hi = np.percentile(bs, [0.5, 99.5])
        out[lab] = dict(v=v, lo=lo, hi=hi, n=n, out=K.outcome(lo, hi, 0.0))
    return out

def share_reading(absX, absM, rng, ref=0.5, B=2000):
    """share given back = 1 - median|residual of the corrected arm| / median|kick of the look| (same resampled qubits), 99 % band, vs ref"""
    absX = np.asarray(absX); absM = np.asarray(absM); n = len(absX)
    f = lambda ix: 1 - np.median(absX[ix]) / np.median(absM[ix])
    v = f(np.arange(n)); bs = [f(rng.integers(0, n, n)) for _ in range(B)]; lo, hi = np.percentile(bs, [0.5, 99.5])
    return dict(v=float(v), lo=float(lo), hi=float(hi), n=n, out=K.outcome(lo, hi, ref))

def part_S(ZA, ZB, S, rng):
    """Z*: {(arm, st): packed array}. Returns {copy: {reading: dict}}"""
    res = {}
    sets = {'A': {k: [v] for k, v in ZA.items()}, 'B': {k: [v] for k, v in ZB.items()}, 'pooled': {k: [ZA[k], ZB[k]] for k in ZA}}
    # shot floor per qubit for each arm's none: |phase_none(A) - phase_none(B)| / N (per copy), / sqrt 2 more for pooled
    ph = {}
    for c in ('A', 'B'):
        for a in ('D', 'DE'):
            x = K.spect_expect(sets[c][(a, 'X')], len(S)); y = K.spect_expect(sets[c][(a, 'Y')], len(S)); ph[(c, a)] = np.arctan2(y, x)
    R = {c: K.read_S(Zc, S, rng) for c, Zc in sets.items()}
    SPL = {a: split_reading(R['A']['M']['kick'], R['B'][a]['kick'], R['B']['M']['kick'], R['A'][a]['kick'], rng) for a in ('M', 'MC', 'MF', 'ME')}
    LAD = split_diff(R, 'MC', 'MF', rng)
    CEIL = {a: split_diff(R, 'M', a, rng) for a in ('MC', 'MF', 'ME')}
    for c, Zc in sets.items():
        r = R[c]; out = {}
        out['KG kick M (deg/readout)'] = med_reading(r['M']['kick'], rng)
        for a in ('MC', 'MF', 'ME'):
            out[f'S1 signed residual {a} (deg/readout)'] = med_reading(r[a]['kick'], rng)
        for a in ('M', 'MC', 'MF', 'ME'):
            out[f'S2 SPLIT slope {a} vs 0 (all given back)'] = SPL[a][c][0]; out[f'S2b SPLIT slope {a} vs 1 (none given back)'] = SPL[a][c][1]
        for a in ('M', 'MC', 'MF', 'ME'):
            out[f'S3 P(1) excess back-to-zero {a}'] = med_reading(r[a]['p1'], rng)
        for a in ('M', 'MC', 'MF', 'ME'):
            out[f'S4 coherence {a} minus none'] = med_reading(r[a]['coh'], rng)
        out['S4b coherence MC minus M (frame only)'] = med_reading(r['MC']['coh'] - r['M']['coh'], rng)
        out['S5 SPLIT slope MC minus MF (old vs fresh table)'] = LAD[c]
        for a in ('MC', 'MF', 'ME'):
            d0 = SPL[a][c][0]; out[f'S2c SPLIT slope {a} vs 0.5 (BELOW = more than half given back)'] = dict(d0, out=K.outcome(d0['lo'], d0['hi'], 0.5))
            out[f'S2d SPLIT slope M minus {a} (ABOVE = clears the ruler ceiling)'] = CEIL[a][c]
            out[f'S7 share given back {a} vs 0.5 (ABOVE = more than half)'] = share_reading(r[a]['abskick'], r['M']['abskick'], rng)
        out['S6 |kick| M minus |residual| MC (given back)'] = med_reading(r['M']['abskick'] - r['MC']['abskick'], rng)
        res[c] = out
    return res

def part_P(ZA, ZB, pairs, rng):
    res = {}
    sets = {'A': {k: [v] for k, v in ZA.items()}, 'B': {k: [v] for k, v in ZB.items()}, 'pooled': {k: [ZA[k], ZB[k]] for k in ZA}}
    RP = {c: K.read_P(Zc, pairs, rng) for c, Zc in sets.items()}
    fl = np.abs(np.degrees(wrap(RP['A']['D']['phi'] - RP['B']['D']['phi']))) / K.N_P
    FLOORP = {'A': fl, 'B': fl, 'pooled': fl / np.sqrt(2)}
    for c, Zc in sets.items():
        r = RP[c]; out = {}
        for a in ('M', 'MC', 'MF', 'ME'):
            nn = K.NONE[a]
            out[f'P1 Bell fidelity {a} minus none'] = med_reading(r[a]['fbell'] - r[nn]['fbell'], rng)
        for a in ('M', 'MC', 'MF', 'ME'):
            nn = K.NONE[a]; keep = r[nn]['conc'] > 0
            d = med_reading((r[a]['conc'] - r[nn]['conc'])[keep], rng); d['excluded_zero_none'] = int((~keep).sum()); out[f'P2 X-part concurrence {a} minus none'] = d
        out['P3 Bell fidelity MC minus M (given back)'] = med_reading(r['MC']['fbell'] - r['M']['fbell'], rng)
        pr = {a: np.degrees(wrap(r[a]['phi'] - r[K.NONE[a]]['phi'])) / K.N_P for a in ('M', 'MC', 'MF', 'ME')}
        out['P4a |pair phase| M minus copy floor (gate)'] = med_reading(np.abs(pr['M']) - FLOORP[c], rng)
        for a in ('MC', 'MF', 'ME'):
            out[f'P5 signed pair-phase residual {a} (deg/step)'] = med_reading(pr[a], rng)
            out[f'P4 pair-phase share given back {a} vs 0.5'] = share_reading(np.abs(pr[a]), np.abs(pr['M']), rng)
        out['P3b X-part concurrence MC minus M (frame only)'] = med_reading(r['MC']['conc'] - r['M']['conc'], rng)
        res[c] = out
    return res

def part_C(CA, CB, tot_end, rng, B=400):
    """C*: {arm: {setting: counts}}. Shot bootstrap 99 %."""
    pooled = {a: {st: {k: CA[a][st].get(k, 0) + CB[a][st].get(k, 0) for k in set(CA[a][st]) | set(CB[a][st])} for st in K.SET_C} for a in K.ARMS}
    res = {}
    EA = {a: PW.evec(PW.to_P(CA[a]))[1:] for a in ('D', 'M')}; EB = {a: PW.evec(PW.to_P(CB[a]))[1:] for a in ('D', 'M')}
    FLOORC = (float(np.sum((EA['D'] - EB['D']) ** 2)) + float(np.sum((EA['M'] - EB['M']) ** 2))) / 4   # pooled-vs-pooled scale (f2)
    for c, Cc in (('A', CA), ('B', CB), ('pooled', pooled)):
        def readings(C, infl=1):
            """infl = how many copies of the shot-noise floor sit inside a squared distance: 1 for the point, 2 inside a bootstrap draw"""
            F = K.read_C(C, tot_end); r = {}
            for a in ('M', 'MC', 'MF', 'ME'): r[f'C1 dF {a} minus none'] = F[a] - F[K.NONE[a]]
            r['C1 dF M with the total put back at the END minus D'] = F['M_endcorr'] - F['D']
            r['C2 F(MC) minus F(M) (given back)'] = F['MC'] - F['M']
            r['C3 F(MC) minus F(M put back at the end)'] = F['MC'] - F['M_endcorr']
            r['C2b recovered share (F(MC)-F(M))/(F(D)-F(M)) vs 0.5'] = (F['MC'] - F['M']) / (F['D'] - F['M']) if F['D'] != F['M'] else np.nan
            E = {a: PW.evec(PW.to_P(C[a]))[1:] for a in K.ARMS}; dM = float(np.sum((E['M'] - E['D']) ** 2)) - infl * FLOORC
            r['C4a look distance |E_M - E_D|^2 minus copy floor (gate)'] = dM
            for a in ('MC', 'MF', 'ME'):
                dX = float(np.sum((E[a] - E[K.NONE[a]]) ** 2)) - infl * FLOORC
                r[f'C4 distance share given back {a} vs 0.5'] = 1 - dX / dM if dM > 0 else np.nan
            return r, F
        r0, F0 = readings(Cc); bs = {k: [] for k in r0}
        for _ in range(B):
            rb, _ = readings({a: PW.resample(Cc[a], rng) for a in K.ARMS}, infl=2)
            for k, v in rb.items(): bs[k].append(v)
        out = {}
        for k, v in r0.items():
            b = np.asarray(bs[k], float); b = b[np.isfinite(b)]
            lo, hi = np.percentile(b, [0.5, 99.5]) if len(b) else (np.nan, np.nan)
            out[k] = dict(v=v, lo=lo, hi=hi, out=K.outcome(lo, hi, 0.5 if 'vs 0.5' in k else 0.0))
        out['F per arm'] = {a: round(F0[a], 4) for a in F0}
        res[c] = out
    return res

def final(res):
    """FINAL per reading: pooled outcome if A and B agree, else CANNOT_TELL"""
    f = {}
    for k, v in res['pooled'].items():
        if not isinstance(v, dict) or 'out' not in v: continue
        a, b = res['A'][k]['out'], res['B'][k]['out']
        f[k] = dict(v, final=v['out'] if a == b else 'CANNOT_TELL', A=a, B=b)
    return f

GATES = {'C1 dF M minus none': ('BELOW', ('C2 F(MC) minus F(M) (given back)', 'C2b recovered share (F(MC)-F(M))/(F(D)-F(M)) vs 0.5', 'C3 F(MC) minus F(M put back at the end)')),
         'C4a look distance |E_M - E_D|^2 minus copy floor (gate)': ('ABOVE', tuple(f'C4 distance share given back {a} vs 0.5' for a in ('MC', 'MF', 'ME'))),
         'P4a |pair phase| M minus copy floor (gate)': ('ABOVE', tuple(f'P4 pair-phase share given back {a} vs 0.5' for a in ('MC', 'MF', 'ME'))),
         'P1 Bell fidelity M minus none': ('BELOW', ('P3 Bell fidelity MC minus M (given back)',))}
def apply_gates(f):
    """a reading that needs the look resolved is CANNOT_TELL when its gate is not met (plan, after the referee)"""
    for g, (want, deps) in GATES.items():
        if g in f and f[g]['final'] != want:
            for d in deps:
                if d in f: f[d] = dict(f[d], final='CANNOT_TELL', gated=g)
    return f

def kg_pass(fS, chip):
    r = fS['KG kick M (deg/readout)']; m = KG_MEDIAN[chip]
    return r['hi'] < 0 and 2 * m <= r['v'] <= 0.5 * m, r

def fmt(name, f):
    lines = []
    for k, v in f.items():
        extra = f" excluded {v['excluded_zero_none']}" if 'excluded_zero_none' in v else ''
        lines.append(f"  {k:52s} {v['v']:+.4f} [{v['lo']:+.4f}, {v['hi']:+.4f}]  A {v['A']:11s} B {v['B']:11s} FINAL {v['final']}{extra}")
    return f'== {name}\n' + '\n'.join(lines)

if __name__ == '__main__' and '--real' in sys.argv:
    chip = sys.argv[sys.argv.index('--real') + 1]; rng = np.random.default_rng(20261031)
    job = json.load(open(f'{HERE}/job_keystone_{chip}.json')); keys = [tuple(k) for k in job['keys']]
    Z = {lab: np.load(f'{HERE}/raw_keystone_{chip}_{lab}.npz') for lab in ('A', 'B')}
    def part(Zl, p): return {(k[1], k[2]): Zl[f'fin_{keys.index(k)}'] for k in keys if k[0] == p}
    T = K.table(chip); S = [int(q) for q in T['S']]; pairs = [tuple(p) for p in T['pairs']]
    fS = final(part_S(part(Z['A'], 'S'), part(Z['B'], 'S'), S, rng)); ok, kg = kg_pass(fS, chip)
    print(f'{chip}: KNOWN-GOOD {"PASS" if ok else "FAIL"}: pooled median kick {kg["v"]:+.3f} [{kg["lo"]:+.3f}, {kg["hi"]:+.3f}] vs committed {KG_MEDIAN[chip]:+.3f} (window x0.5..x2, upper end < 0)')
    print(fmt('S spectators (117 untouched, N = 8)', fS))
    print(fmt('P Bell pairs (48, N = 4)', apply_gates(final(part_P(part(Z['A'], 'P'), part(Z['B'], 'P'), pairs, rng)))))
    clock = job['clock']; corr = K.committed_corr(chip, K.N_C); tot = [K.N_C * corr[q] for q in (clock[0], clock[2], clock[1])]   # c0, c1, s
    CC = {lab: {a: {st: K.counts3([Z[lab][f'fin_{keys.index(("C", a, st))}']]) for st in K.SET_C} for a in K.ARMS} for lab in ('A', 'B')}
    fC = part_C(CC['A'], CC['B'], tot, rng); print('  F per arm (pooled):', fC['pooled']['F per arm']); print(fmt(f'C clock c0, s, c1 = {clock} (look in the middle, N = 4)', apply_gates(final(fC))))
