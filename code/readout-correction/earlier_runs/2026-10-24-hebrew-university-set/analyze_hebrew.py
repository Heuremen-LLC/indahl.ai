"""analyze_hebrew.py -- readings under PLAN_HEBREW: per copy, pooled, and FINAL = pooled outcome if the two copies agree, else CANNOT_TELL."""
import os, sys, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import hebrew as H
HERE = os.path.dirname(os.path.abspath(__file__)); rec = json.load(open(f'{HERE}/job_hebrew.json')); meta = rec['meta']
B = [np.load(f'{HERE}/raw_hebrew_J{c}.npz') for c in (0, 1)]; bits = [[z[f'fin_{i}'] for i in range(len(meta))] for z in B]
rng = np.random.default_rng(20261024)
r0 = H.readings(meta, bits[0], rng); r1 = H.readings(meta, bits[1], rng); rp = H.readings(meta + meta, bits[0] + bits[1], rng)
kg = H.kg_reading(meta + meta, bits[0] + bits[1], rng); kg0 = H.kg_reading(meta, bits[0], rng); kg1 = H.kg_reading(meta, bits[1], rng)
print(f'KNOWN-GOOD (21 Oct committed fez control run, 39-pack, N=8, median over 117 untouched: -1.618 deg [-2.085, -1.179]; rule: pooled median in '
      f'[-3.24, -0.81] and 99% upper end < 0): pooled {kg["median"]:+.3f} [{kg["lo"]:+.3f}, {kg["hi"]:+.3f}] -> {"PASS" if kg["PASS"] else "FAIL"}'
      f'  (copy 0 {kg0["median"]:+.3f}, copy 1 {kg1["median"]:+.3f})')
for k in r0:
    if k.startswith('_'): continue
    a, b_, p = r0[k], r1[k], rp[k]; fin = p[3] if a[3] == b_[3] else 'CANNOT_TELL'
    print(f'{k:42s} copy0 {a[0]:+.4f} [{a[1]:+.4f},{a[2]:+.4f}] {a[3]:11s} copy1 {b_[0]:+.4f} [{b_[1]:+.4f},{b_[2]:+.4f}] {b_[3]:11s} '
          f'pooled {p[0]:+.4f} [{p[1]:+.4f},{p[2]:+.4f}] -> FINAL {fin}')
print('profile median wrap(phi_M - phi_D) deg by N', H.NS, rp['_profile_M_D_deg'])
print('profile median wrap(phi_MD - phi_DD) deg by N', H.NS, rp['_profile_MD_DD_deg'])
print('state check P(1) on distance-3 |1> qubits at N=13 by arm', rp['_state_check_P1_at_N13'])
print('jobs', [(j.get('job_id'), (j.get('usage') or {}).get('qpu_charge_time_seconds')) for j in rec['jobs']])
