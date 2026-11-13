"""synth.py -- plants every alternative and reads it with the committed analyze.read(); writes synth_results_2608.13614.text.
Worlds (each variant P and S separately, multinomial 4096 shots, energy tables and noiseless-QAOA distributions from known_good.json /
sis_qubo, nothing from any QPU):
 null      uniform over 1024                                   -> R1 CONSISTENT, R2 CONSISTENT
 ideal     noiseless QAOA p=4 (my angles)                      -> R1 ABOVE
 decohered 0.3 ideal + 0.7 uniform                             -> power reading (ABOVE expected only sometimes)
 below     uniform with the 10 low states at 0.2x              -> R1 BELOW
 bias      independent bits, P(bit=0)=0.62 (decay artefact)    -> R1 may move; R2 must read CONSISTENT
 both      P ideal + S below                                   -> combined CANNOT_TELL
 neither   both variants null                                  -> combined CONSISTENT
False-call rate = fraction of null (and bias-for-R2) draws not reading CONSISTENT, 2000 draws per world."""
import json, os, sys, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from sis_qubo import build, angles, qaoa_probs
from analyze import read, combine, NULL
kg = json.load(open(f'{H}/known_good.json')); rng = np.random.default_rng(20261024); N = 4096; R = 2000
W = {}
for v in 'PS':
    m = build(v); E = m['E']; pr = qaoa_probs(np.array(kg[v]['angles']), E); u = np.ones(1024) / 1024
    low = np.argsort(E, kind='stable')[:10]; bl = u.copy(); bl[low] *= 0.2; bl /= bl.sum()
    bias = np.array([np.prod([0.38 if (s >> (9 - q)) & 1 else 0.62 for q in range(10)]) for s in range(1024)])
    W[v] = dict(E=E, ideal=kg[v]['ideal_low10_fraction'], dist=dict(null=u, ideal=pr, decohered=0.3 * pr + 0.7 * u, below=bl, bias=bias))
def draw(p): c = rng.multinomial(N, p); return {format(s, '010b'): int(x) for s, x in enumerate(c) if x}
lines = []; tab = {}
for v in 'PS':
    for w, p in W[v]['dist'].items():
        rs = [read(draw(p), W[v]['E'], W[v]['ideal'], boot=0 or 20) for _ in range(R if w in ('null', 'bias') else 400)]
        c1 = {o: sum(r['R1'] == o for r in rs) / len(rs) for o in ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL')}
        c2 = {o: sum(r['R2'] == o for r in rs) / len(rs) for o in ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL')}
        tab[(v, w)] = (c1, c2); lines.append(f'{v} {w:9s} n={len(rs):4d}  R1 {c1}  R2 {c2}  exp.frac {float(p[np.argsort(W[v]["E"], kind="stable")[:10]].sum()):.4f}')
def comb(wp, ws, n=400):
    out = {}
    for _ in range(n):
        a = read(draw(W['P']['dist'][wp]), W['P']['E'], W['P']['ideal'], boot=20)['R1']; b = read(draw(W['S']['dist'][ws]), W['S']['E'], W['S']['ideal'], boot=20)['R1']
        o = combine(a, b); out[o] = out.get(o, 0) + 1 / n
    return out
both = comb('ideal', 'below'); neither = comb('null', 'null', 1000); hyp = comb('ideal', 'ideal')
lines.append(f'combined both (P ideal, S below): {both}'); lines.append(f'combined neither (null, null): {neither}'); lines.append(f'combined ideal,ideal: {hyp}')
fc = max(1 - tab[(v, 'null')][0]['CONSISTENT'] for v in 'PS'); fc2 = max(1 - tab[(v, w)][1]['CONSISTENT'] for v in 'PS' for w in ('null', 'bias'))
lines.append(f'FALSE-CALL RATE R1 (null, worst variant) = {fc:.4f}; R2 (null and bias, worst) = {fc2:.4f}; combined neither non-CONSISTENT = {1 - neither.get("CONSISTENT", 0):.4f}')
ok = fc <= 0.055 and fc2 <= 0.055 and all(tab[(v, 'ideal')][0]['ABOVE'] >= 0.8 for v in 'PS') and all(tab[(v, 'below')][0]['BELOW'] >= 0.8 for v in 'PS') and both.get('CANNOT_TELL', 0) >= 0.8
lines.append(f'SYNTH {"PASS" if ok else "FAIL"} (rule: false-call <= 5.5% on R1 and R2; ideal ABOVE >= 80%; below BELOW >= 80%; both -> CANNOT_TELL >= 80%)')
open(f'{H}/synth_results_2608.13614.text', 'w').write('\n'.join(lines) + '\n'); print('\n'.join(lines))
