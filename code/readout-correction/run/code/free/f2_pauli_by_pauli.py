"""f2_pauli_by_pauli.py -- THE GAP check on the two free readings (zero QPU; DEFINED AFTER THE 24 Oct DATA, labelled).
F is one projection (onto the ideal state); a corrected state could still differ from the idle state in components F does not see.
Ruler 1: Pauli by Pauli. r = E_X - E_D over all 63 expectations (pooled copies); chi2 = sum r^2 / var_boot(r) against 63 (diagonal variances,
         settings shared between Paulis, so read as a scale, not an exact test). Floor: the same chi2 for E_D(J1) - E_D(J2) and E_M(J1) - E_M(J2).
Ruler 2: norms. ||E_X - E_D||^2 against the copy floor (||E_D(J1) - E_D(J2)||^2 + ||E_M(J1) - E_M(J2)||^2) / 4 (pooled-vs-pooled scale).
Also: F(T E_D) - F(E_M) (rotation-only forward prediction minus the measured look) with a 99 % shot-bootstrap band."""
import sys, json, numpy as np
P = '../earlier_runs/2026-10-24-page-wootters'; sys.path.insert(0, P)
import pooters as T
tot = np.radians([4 * -3.065, 4 * -18.1202, 4 * -7.6073])            # c0, c1, s: committed 21 Oct, per readout x 4
R = T.kron3(T.qmap(tot[0], 1), T.qmap(tot[1], 1), T.qmap(tot[2], 1)); Rinv = R.T.copy()
for i in range(3): pass
Rinv = T.kron3(T.qmap(-tot[0], 1), T.qmap(-tot[1], 1), T.qmap(-tot[2], 1))
raw = {j: json.load(open(f'{P}/raw_pooters_{j}.json')) for j in ('J1', 'J2')}
C = {j: {a: {e['setting']: e['counts'] for e in raw[j] if e['arm'] == a} for a in 'DM'} for j in raw}
def pool(a): return {st: {k: C['J1'][a][st].get(k, 0) + C['J2'][a][st].get(k, 0) for k in set(C['J1'][a][st]) | set(C['J2'][a][st])} for st in T.SETTINGS}
CP = {a: pool(a) for a in 'DM'}
E = lambda c: T.evec(T.to_P(c))
def stats(CD, CM):
    ED, EM = E(CD), E(CM); return dict(r_corr=(Rinv @ EM - ED)[1:], r_raw=(EM - ED)[1:], r_fwd=(EM - R @ ED)[1:], dF_fwd=T.fidelity(R @ ED) - T.fidelity(EM))
rng = np.random.default_rng(2610)
pt = stats(CP['D'], CP['M']); bs = [stats(T.resample(CP['D'], rng), T.resample(CP['M'], rng)) for _ in range(400)]
var = {k: np.var([b[k] for b in bs], axis=0) for k in ('r_corr', 'r_raw', 'r_fwd')}
fl = {}
for a in 'DM':
    d = (E(C['J1'][a]) - E(C['J2'][a]))[1:]
    bsd = [(E(T.resample(C['J1'][a], rng)) - E(T.resample(C['J2'][a], rng)))[1:] for _ in range(200)]
    fl[a] = (float(np.sum(d ** 2 / np.var(bsd, axis=0))), float(np.sum(d ** 2)))
floor_norm = (fl['D'][1] + fl['M'][1]) / 4
out = ['f2_pauli_by_pauli.py -- 24 Oct Pooters data, pooled copies (DEFINED AFTER THE DATA). 63 non-identity Pauli expectations.']
out.append(f'  copy floor chi2: D(J1)-D(J2) {fl["D"][0]:.1f}, M(J1)-M(J2) {fl["M"][0]:.1f} (63 expected under shot noise alone)')
out.append(f'  copy floor norm (pooled-vs-pooled scale) {floor_norm:.4f}')
for k, lab in (('r_raw', 'look, uncorrected, minus idle'), ('r_corr', 'look corrected by the committed 21 Oct kicks, minus idle'), ('r_fwd', 'look minus idle rotated by the committed kicks (forward)')):
    chi2 = float(np.sum(pt[k] ** 2 / var[k])); nrm = float(np.sum(pt[k] ** 2)); big = np.argsort(-np.abs(pt[k] / np.sqrt(var[k])))[:3]
    lab3 = [''.join('IXYZ'[x] for x in np.unravel_index(i + 1, (4, 4, 4))) for i in big]
    out.append(f'  {lab:58s} chi2 {chi2:8.1f}  norm {nrm:.4f}  ({nrm / floor_norm:.2f} x floor)  largest |r|/sd at {lab3} = {[round(float(abs(pt[k][i]) / np.sqrt(var[k][i])), 1) for i in big]}')
lo, hi = np.percentile([b['dF_fwd'] for b in bs], [0.5, 99.5])
out.append(f'  forward prediction F(idle rotated) - F(look measured) = {pt["dF_fwd"]:+.4f} [{lo:+.4f}, {hi:+.4f}] (99 % shot bootstrap)')
open('f2_results.text', 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
