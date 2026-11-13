"""known_good.py -- KNOWN-GOOD: their released raw ancilla bits (ibm_kingston, Sept 2026) through OUR estimator (geopump.py).
Must reproduce (1) their published odd heats per job (fig3c / fig3d job CSVs) to <= 1e-8 and (2) their SM Table 1 hardware noise
contribution Delta Q_even = Q_even(measured) - Q_even(ideal model) to the printed 2 decimals, at every tau of the tau scan."""
import json, glob, os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import geopump as G
H = os.path.dirname(os.path.abspath(__file__)) + '/theirs'
TABLE1 = {5: (1.56, 1.12), 15: (2.00, 1.66), 20: (2.08, 1.73), 40: (3.53, 4.42), 60: (3.57, 4.56), 80: (3.67, 4.70)}   # hw dQ_L,even, dQ_R,even (SM Table 1)
pub = {}
for l in open(H + '/fig3c_pumped_heat_vs_tau_measured.csv'):
    if l[0] in '#t': continue
    t = l.strip().split(','); pub[t[5]] = (float(t[1]), float(t[3]))
for l in open(H + '/fig3d_pumped_heat_vs_deltaB_jobs.csv'):
    if l[0] in '#d': continue
    t = l.strip().split(','); pub[t[5]] = (float(t[1]), float(t[3]))

def heats_from_bits(z, dB, tau):
    means = {}; se2 = {'L': 0, 'R': 0}
    for d, rev in (('fwd', False), ('rev', True)):
        sch = G.schedule(dB, tau, rev)
        for b in ('plus', 'minus'):
            w = float(z[f'{d}_{b}_weight'])
            if f'{d}_{b}_eL' in z.files: qL, qR = G.shot_heat(sch, 'A', z[f'{d}_{b}_eL'], z[f'{d}_{b}_eR'])
            else: qL, qR = z[f'{d}_{b}_QL'], z[f'{d}_{b}_QR']
            means[(d, b)] = (w, (qL.mean(), qR.mean()))
    return G.combine(means)

worst, rows = 0.0, []
for f in sorted(glob.glob(H + '/tau*.npz')) + sorted(glob.glob(H + '/deltaB/*.npz')):
    z = np.load(f); jid = str(z['job_id']); tau = float(z['tau']) if 'tau' in z.files else 60.0
    dB = 0.45 if '/tau' in f else float(os.path.basename(f)[2:8])
    r = heats_from_bits(z, dB, tau); p = pub[jid]; d = max(abs(r['QL_odd'] - p[0]), abs(r['QR_odd'] - p[1])); worst = max(worst, d)
    line = f'{jid} tau={tau:g} dB={dB:.3f}  QL_odd ours {r["QL_odd"]:+.6f} theirs {p[0]:+.6f}  QR_odd ours {r["QR_odd"]:+.6f} theirs {p[1]:+.6f}  |diff| {d:.1e}'
    if '/tau' in f:
        idl = G.ideal(dB, tau); dL, dR = r['QL_even'] - idl['QL_even'], r['QR_even'] - idl['QR_even']; tL, tR = TABLE1[int(tau)]
        ok = abs(round(dL, 2) - tL) < 0.0051 and abs(round(dR, 2) - tR) < 0.0051; rows.append(ok)
        line += f'  | dQ_even hw ours L {dL:.3f} R {dR:.3f} vs Table 1 {tL:.2f} {tR:.2f} -> {"MATCH" if ok else "DIFFER"}'
    print(line)
ok = worst <= 1e-8 and all(rows)
print(f'KNOWN-GOOD: max |odd diff| over {len(pub)} published jobs {worst:.1e} (must be <= 1e-8); Table 1 even rows matched {sum(rows)}/{len(rows)} -> {"PASS" if ok else "FAIL"}')
