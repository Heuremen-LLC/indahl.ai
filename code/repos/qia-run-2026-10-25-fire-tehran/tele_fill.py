"""tele_fill.py -- analysis. raw = {arm: (alice ints, bob ints)}; arm = '<L>|<block>_<msg>_<bases>' for L in theirs/best/q50 (job A),
'<L>|probe_s<j>_<ax>' (job A), 'kg|native_product_HT_<bases>' (job A, last), 'jobB|<block>_<msg>_<bases>' (their chain, job B).
Readings (all fixed here, before any job):
  F        linear-tomography F +- bootstrap sd for every block, layout, message.
  THEIRS   f = (N1corr - N1none)/(native - N1none) on their chain with all three terms in ONE job (job A), beside their cross-job 1.057 / 0.975;
           f - 1 four outcomes (their claim: f = 1).
  DRIFT    job B - job A on their chain: native F, N1none F (four outcomes, a bound at minute spacing); and f_cross = their construction
           (N1corr from job B, N1none and native from job A) minus f_A: what one job-to-job step alone puts into f.
  LAYOUT   native F and f across theirs/best/q50: weighted chi2 (dof 2), ABOVE if p < 0.05 else CONSISTENT (range a bound).
  FINGER   TOMO-9 device fingerprint (nearest-rotation angle, rad, per leg) per layout +- bootstrap sd; chi2 across layouts per leg;
           the angle is biased up by shot noise, so 'resolved' = angle above the NULL FLOOR (95th percentile of the angle over the synth NULL
           replicates at these shots, finger_floor.json, measured before any job); below it = CANNOT_TELL (no rotation resolved); their chain today beside their 0.108 / 0.159 of 4 Oct (cross-day, labelled).
  KNOWN-GOOD  their chain native product_HT in-block vs its identical copy at the end of job A: |z| < 2.58 (shot noise, same apparatus).
  If the known-good fails: NOT DECIDED (no reading is claimed)."""
import numpy as np
from scipy import stats
from tele import BASES9, PROBES, tables, F_with_se, lin_F, message_state, fingerprint, recovered, frame_keys
MSGS = ('product_HT', 'bell_30_70'); LAYS = ('theirs', 'best', 'q50'); BLOCKS = ('native', 'N1none', 'N1corr')
def four(d, s):
    lo, hi = d - 1.96 * s, d + 1.96 * s; return dict(diff=d, sd=s, ci95=[lo, hi], outcome='ABOVE' if lo > 0 else 'BELOW' if hi < 0 else 'CONSISTENT')
def chi2(vals):
    v = np.array([x[0] for x in vals]); s = np.array([x[1] for x in vals]); w = 1 / s ** 2; m = (w * v).sum() / w.sum(); c = float((w * (v - m) ** 2).sum()); p = float(stats.chi2.sf(c, len(v) - 1))
    return dict(values=v.tolist(), sds=s.tolist(), range=float(v.max() - v.min()), chi2=c, dof=len(v) - 1, p=p, outcome='ABOVE (layout carries it)' if p < 0.05 else 'CONSISTENT (range is a bound)')
def Fblk(raw, pre, blk, msg, boot):
    t = tables({b: raw[f'{pre}|{blk}_{msg}_{b}'] for b in BASES9}); return F_with_se(t, message_state(msg), boot)
import json as _json, os as _os
_FF = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'finger_floor.json')
FLOOR = _json.load(open(_FF)) if _os.path.exists(_FF) else {'2': 0.0, '3': 0.0}
def finger(raw, pre, boot, seed=3):
    pt = {}
    for j in range(3):
        for _, ax in PROBES:
            a, o = raw[f'{pre}|probe_s{j}_{ax}']; pt[f'probe_s{j}_{ax}'] = np.bincount(frame_keys(a, o, ax * 2), minlength=4)
    a0 = fingerprint(pt); rng = np.random.default_rng(seed); bs = {2: [], 3: []}
    for _ in range(boot):
        r = fingerprint({k: rng.multinomial(int(c.sum()), c / c.sum()) for k, c in pt.items()})
        for q in (2, 3): bs[q].append(r[q])
    return {q: (a0[q], float(np.std(bs[q], ddof=1))) for q in (2, 3)}
def analyse(raw, boot=200):
    out = {'F': {}, 'f': {}}
    F = {L: {m: {b: Fblk(raw, L, b, m, boot) for b in BLOCKS} for m in MSGS} for L in LAYS}
    for L in LAYS:
        for m in MSGS:
            out['F'][f'{L}|{m}'] = {b: dict(F=F[L][m][b][0], sd=F[L][m][b][1]) for b in BLOCKS}
            out['f'][f'{L}|{m}'] = dict(zip(('f', 'sd'), recovered(F[L][m]['N1corr'], F[L][m]['N1none'], F[L][m]['native'])))
    kgt = tables({b: raw[f'kg|native_product_HT_{b}'] for b in BASES9}); kg = F_with_se(kgt, message_state('product_HT'), boot)
    k = four(kg[0] - F['theirs']['product_HT']['native'][0], float(np.hypot(kg[1], F['theirs']['product_HT']['native'][1])))
    out['KNOWN_GOOD'] = dict(rule='their chain native product_HT in-block vs identical copy at end of job A: |z| < 2.58', **k, z=k['diff'] / k['sd'], passed=bool(abs(k['diff'] / k['sd']) < 2.58))
    theirs_cross = {'product_HT': 1.057, 'bell_30_70': 0.975}
    out['THEIRS'] = {m: dict(f_one_job=out['f'][f'theirs|{m}'], their_cross_job=theirs_cross[m], f_minus_1=four(out['f'][f'theirs|{m}']['f'] - 1, out['f'][f'theirs|{m}']['sd'])) for m in MSGS}
    if any(k_.startswith('jobB|') for k_ in raw):
        out['DRIFT'] = {}
        for m in MSGS:
            B = {b: Fblk(raw, 'jobB', b, m, boot) for b in BLOCKS}; A = F['theirs'][m]
            fA = recovered(A['N1corr'], A['N1none'], A['native']); fX = recovered(B['N1corr'], A['N1none'], A['native'])
            out['DRIFT'][m] = dict(native=four(B['native'][0] - A['native'][0], float(np.hypot(B['native'][1], A['native'][1]))),
                                   N1none=four(B['N1none'][0] - A['N1none'][0], float(np.hypot(B['N1none'][1], A['N1none'][1]))),
                                   N1corr=four(B['N1corr'][0] - A['N1corr'][0], float(np.hypot(B['N1corr'][1], A['N1corr'][1]))),
                                   f_cross_minus_f_one_job=dict(f_cross=fX[0], f_one_job=fA[0], shift=fX[0] - fA[0],
                                       share_of_their_ci_halfwidth=(fX[0] - fA[0]) / {'product_HT': (1.177 - 0.952) / 2, 'bell_30_70': (1.017 - 0.934) / 2}[m]))
    out['LAYOUT'] = {m: dict(native=chi2([F[L][m]['native'] for L in LAYS]), f=chi2([recovered(F[L][m]['N1corr'], F[L][m]['N1none'], F[L][m]['native']) for L in LAYS])) for m in MSGS}
    fp = {L: finger(raw, L, boot) for L in LAYS}
    out['FINGER'] = {'per_layout': {L: {q: dict(angle=fp[L][q][0], sd=fp[L][q][1], resolved=bool(fp[L][q][0] > FLOOR[str(q)]), floor=FLOOR[str(q)]) for q in (2, 3)} for L in LAYS},
                     'chi2_leg2': chi2([fp[L][2] for L in LAYS]), 'chi2_leg3': chi2([fp[L][3] for L in LAYS]),
                     'theirs_4oct': {2: 0.1084, 3: 0.1593}, 'note': 'their chain today vs 4 Oct is a cross-day reading (three weeks, many recalibrations): labelled, not a layout reading'}
    if not out['KNOWN_GOOD']['passed']: out['VERDICT'] = 'NOT DECIDED: known-good failed'
    return out
