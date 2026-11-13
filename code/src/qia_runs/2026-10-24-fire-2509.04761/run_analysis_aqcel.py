"""run_analysis_aqcel.py -- applies the committed analyze_aqcel.analyze to raw_aqcel.json (B = 2000) and checks record changes."""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import analyze_aqcel as Z
meta = json.load(open(f'{HERE}/meta_aqcel.json')); ents = json.load(open(f'{HERE}/raw_aqcel.json'))
R = Z.analyze(ents, meta['meas'], meta['union'], meta['p'], B=2000, seed=1)
L = [f"PRIMARY {R['primary']} -- {R['why']}"]
for a, d in R['arms'].items():
    L.append(f"{a:4s} CZ {meta['cz'][a]:3d}  F {d['F']:.4f} [{d['lo']:.4f}, {d['hi']:.4f}]  raw {d['F_raw']:.4f}  copies {[round(x, 4) for x in d['F_copies']]}  drift ratio {d['drift_ratio']:.2f}{' FLAG' if d['drift'] else ''}  shots {d['shots']}")
L.append(f"D3 = F_V2 - F_CTRL {R['D3']['v']:+.4f} [{R['D3']['lo']:+.4f}, {R['D3']['hi']:+.4f}]")
L.append(f"D2 = F_V2 - F_Q    {R['D2']['v']:+.4f} [{R['D2']['lo']:+.4f}, {R['D2']['hi']:+.4f}]   (printed 0.99 - 0.46 = 0.53)")
L.append(f"SECONDARY {R['secondary']}")
L.append('calibration e0 ' + str([round(x, 4) for x in R['cal']['e0']]) + ' e1 ' + str([round(x, 4) for x in R['cal']['e1']]) + f" (union {meta['union']})")
# record changes on the used qubits / edges during the window
def load(f):
    return json.load(open(f'{HERE}/{f}'))
b, a = load('props_aqcel_before_1.json'), load('props_aqcel_after.json')
L.append(f"record last_update_date before {b.get('last_update_date')} after {a.get('last_update_date')}")
used = set(meta['union'])
ch = []
for i in used:
    vb = {x['name']: x['value'] for x in b['qubits'][i]}; va = {x['name']: x['value'] for x in a['qubits'][i]}
    for k in ('readout_error', 'prob_meas0_prep1', 'prob_meas1_prep0', 'T1', 'T2'):
        if vb.get(k) != va.get(k):
            ch.append((i, k, vb.get(k), va.get(k)))
L.append(f"record changes on the 13 measured qubits between before/after: {len(ch)} {ch[:6]}")
txt = '\n'.join(L); print(txt); open(f'{HERE}/results_aqcel.text', 'w').write(txt + '\n')
json.dump(R, open(f'{HERE}/readings_aqcel.json', 'w'), indent=1, default=float)
