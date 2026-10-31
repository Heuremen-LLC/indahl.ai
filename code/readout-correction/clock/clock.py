"""clock.py -- the Darkwave clock run (PLAN_CLOCK.md.text, 31 Oct 2026): how long a readout-phase correction table keeps giving back the
phase that a 39-qubit pack's mid-circuit readout puts on the untouched qubits next to it. Circuits are the keystone run's, unchanged
(keystone.py copied byte for byte): setup S, all 117 untouched qubits on the equator, N = 8 looks, settings X and Y.
Arms, same job, interleaved: D the pack idles | M the pack is read out, no correction | MC + the committed 21 Oct table | M31 + the table
measured on 31 Oct (keystone job C), held fixed for every later day | MT + today's table from this run's own calibration job C.
Correction = rz(-kick_q) on every untouched qubit after every look (virtual, zero duration); no qubit is selected or dropped by its kick."""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import keystone as K, analyze_keystone as A
ARMS = ['D', 'M', 'MC', 'M31', 'MT']
KARM = {'D': 'D', 'M': 'M', 'MC': 'MC', 'M31': 'MC', 'MT': 'MF'}   # keystone builder labels: MC and MF apply the table they are given
SETS = ['X', 'Y']; N = 8; SHOTS = 2000; MARGIN = 0.05
def table31(chip): return {int(q): v['k8'] for q, v in json.load(open(f'{HERE}/fresh31_kicks_{chip}.json'))['kicks'].items()}
def keys(): return [(a, st) for st in SETS for a in ARMS]
def build(n, E, S, a, st, tables, L_dt): return K.circ_S(n, E, S, KARM[a], st, tables.get(a, {}), L_dt, N=N)
def outcome_m(lo, hi, m=MARGIN):
    """four outcomes against 0 with an equivalence margin: CONSISTENT only if the whole band sits inside [-m, +m]"""
    if not (np.isfinite(lo) and np.isfinite(hi)): return 'CANNOT_TELL'
    if lo > 0: return 'ABOVE'
    if hi < 0: return 'BELOW'
    if -m <= lo and hi <= m: return 'CONSISTENT'
    return 'CANNOT_TELL'
def read(Zc, nq, rng, B=20000):   # addendum 2: 20,000 draws from the second fire on
    """Zc: {(arm, st): [packed fin arrays]}. Per qubit: phase vs D per look (deg); shares given back on the same resampled qubits."""
    ph = {a: np.arctan2(K.spect_expect(Zc[(a, 'Y')], nq), K.spect_expect(Zc[(a, 'X')], nq)) for a in ARMS}
    kick = {a: np.degrees(K.wrap(ph[a] - ph['D'])) / N for a in ('M', 'MC', 'M31', 'MT')}; ab = {a: np.abs(v) for a, v in kick.items()}
    out = {'KG kick M (deg/readout)': A.med_reading(kick['M'], rng)}
    for a in ('MC', 'M31', 'MT'): out[f'share given back {a} vs 0.5'] = A.share_reading(ab[a], ab['M'], rng)
    sh = lambda a, ix: 1 - np.median(ab[a][ix]) / np.median(ab['M'][ix])
    for a, b in (('M31', 'MT'), ('MC', 'MT'), ('MC', 'M31')):
        v = sh(a, np.arange(nq)) - sh(b, np.arange(nq)); bs = []
        for _ in range(B):
            ix = rng.integers(0, nq, nq); bs.append(sh(a, ix) - sh(b, ix))
        lo, hi = np.percentile(bs, [0.5, 99.5]); out[f'share {a} minus share {b} (margin 0.05)'] = dict(v=float(v), lo=float(lo), hi=float(hi), n=nq, out=outcome_m(lo, hi))
    return out, kick
def final(res):
    """FINAL per reading: the pooled outcome if copies A and B agree, else CANNOT_TELL (as the keystone run)"""
    f = {}
    for k, v in res['pooled'].items():
        if not isinstance(v, dict) or 'out' not in v: continue
        a, b = res['A'][k]['out'], res['B'][k]['out']; f[k] = dict(v, final=v['out'] if a == b else 'CANNOT_TELL', A=a, B=b)
    return f
def kg_pass(fin, chip):
    r = fin['KG kick M (deg/readout)']; m = A.KG_MEDIAN[chip]; return r['hi'] < 0 and 2 * m <= r['v'] <= 0.5 * m
