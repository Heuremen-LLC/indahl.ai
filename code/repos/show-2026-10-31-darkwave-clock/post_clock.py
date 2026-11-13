"""post_clock.py DAYDIR -- PLAN_CLOCK.md.text Addendum 3: second rulers beside the FINAL reading of one chip-fire. Writes DAYDIR/readings_second.text.
The FINAL rule and analyze_clock.py are unchanged. Planned from the 2 November fires on; for the 1 November fires these were defined after the data.
 (a) label stability: the pooled R2 reading over bootstrap seeds 1 to 20 (20,000 draws each), count of each outcome and the range of the band's ends;
 (b) per-qubit count: qubits where the 31 Oct table leaves a larger |residual| than today's table, and fewer, with the exact two-sided sign-test p;
 (c) signed median residual per arm (M, MC, M31, MT; deg per readout, 99 % qubit bootstrap, 20,000 draws): positive = the table puts back more
     than the readout took (over-correction), negative = less;
 (d) the shot-noise floor: median |residual| pooled against the copy-to-copy half-difference median, for M31 and MT."""
import json, os, sys
from math import comb
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import keystone as K, clock as C
D = os.path.abspath(sys.argv[1]); rec = json.load(open(f'{D}/job_clock.json')); S = rec['S']; keys = [tuple(k) for k in rec['keys']]; nq = len(S)
def Z(lab):
    z = np.load(f'{D}/raw_{lab}.npz'); order = list(range(len(keys))) if lab == 'A' else list(range(len(keys)))[::-1]
    return {keys[i]: z[f'fin_{i}'] for i in order}
ZA, ZB = Z('A'), Z('B'); P = {k: [ZA[k], ZB[k]] for k in ZA}; key = 'share M31 minus share MT (margin 0.05)'
import datetime as _dt
_jc = [j for j in rec['jobs'] if j['label'] == 'C' and j.get('status') == 'DONE'][-1]; _tC = (_jc.get('timestamps') or {}).get('running') or _jc['submitted_utc']   # when this fire's first data was taken
_A3 = '2026-11-01T12:08:49Z'   # Addendum 3 public (292a5e21)
L = [f'SECOND RULERS (PLAN_CLOCK Addendum 3), {rec["chip"]}, fire {rec["day_utc"]} UTC. ' + ('Defined after the data for this fire.' if _tC[:19] < _A3[:19] else 'Planned before this fire\'s data existed (Addendum 3 public 12:08:49 UTC 1 Nov, this fire\'s first job ran ' + _tC[11:19] + ' UTC).')]
labs, los, his = [], [], []
for sd in range(1, 21):
    o, _ = C.read(P, nq, np.random.default_rng(sd)); labs.append(o[key]['out']); los.append(o[key]['lo']); his.append(o[key]['hi'])
L.append('(a) pooled clock reading over 20 bootstrap seeds: ' + ', '.join(f'{k} {labs.count(k)}' for k in ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL') if labs.count(k)) +
         f' | lower end {min(los):+.4f} to {max(los):+.4f}, upper end {min(his):+.4f} to {max(his):+.4f}')
_, kp = C.read(P, nq, np.random.default_rng(31), B=10); _, ka = C.read({k: [v] for k, v in ZA.items()}, nq, np.random.default_rng(31), B=10)
_, kb = C.read({k: [v] for k, v in ZB.items()}, nq, np.random.default_rng(31), B=10)
w = int(np.sum(np.abs(kp['M31']) > np.abs(kp['MT']))); b = int(np.sum(np.abs(kp['M31']) < np.abs(kp['MT']))); n = w + b
p = min(1.0, 2 * sum(comb(n, i) for i in range(min(w, b) + 1)) / 2 ** n) if n else 1.0
L.append(f'(b) qubits where the 31 Oct table leaves a larger |residual| than today\'s table: {w}, smaller: {b}, of {nq}; exact two-sided sign test p = {p:.3f}')
r = np.random.default_rng(31)
for a in ('M', 'MC', 'M31', 'MT'):
    x = kp[a]; bs = [np.median(x[r.integers(0, nq, nq)]) for _ in range(20000)]; lo, hi = np.percentile(bs, [0.5, 99.5])
    L.append(f'(c) signed median {"kick" if a == "M" else "residual"} {a}: {np.median(x):+.3f} [{lo:+.3f}, {hi:+.3f}] deg/readout')
for a in ('M31', 'MT'):
    L.append(f'(d) {a}: median |residual| pooled {np.median(np.abs(kp[a])):.3f} deg/readout, shot-noise floor scale (copy-to-copy half-difference median) {np.median(np.abs(ka[a] - kb[a])) / 2:.3f}')
open(f'{D}/readings_second.text', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))

# ADDENDUM 4 (1 Nov 2026, after the outside referee of the ibm_kingston second fire): the seed spread for R3 and R4 too, the plan's
# copies-agree rule applied at each seed, the copy bands at the plan's own draw, and when today's table was measured relative to the copies.
L.append('ADDENDUM 4 lines: ' + ('defined after the data for this fire.' if rec['day_utc'] < '20261102' else 'planned before this fire.'))
ks = ['share M31 minus share MT (margin 0.05)', 'share MC minus share MT (margin 0.05)', 'share MC minus share M31 (margin 0.05)']
CA, CB = {k: [v] for k, v in ZA.items()}, {k: [v] for k, v in ZB.items()}
pool, rule = {k: [] for k in ks}, {k: [] for k in ks}
for sd in range(1, 21):
    r_ = np.random.default_rng(sd); oa = C.read(CA, nq, r_)[0]; ob = C.read(CB, nq, r_)[0]; op = C.read(P, nq, r_)[0]
    for k in ks: pool[k].append(op[k]['out']); rule[k].append(op[k]['out'] if oa[k]['out'] == ob[k]['out'] else 'CANNOT_TELL')
for k in ks:
    L.append(f'(e) {k.split(" (")[0]} over seeds 1-20: pooled label ' + ', '.join(f'{x} {pool[k].count(x)}' for x in ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL') if pool[k].count(x)) +
             ' | the plan\'s rule (pooled if the copies agree) ' + ', '.join(f'{x} {rule[k].count(x)}' for x in ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL') if rule[k].count(x)))
r_ = np.random.default_rng(31); oa = C.read(CA, nq, r_)[0]; ob = C.read(CB, nq, r_)[0]   # the plan's draw: analyze_clock.py reads A, then B, then pooled on one generator
for k in ks: L.append(f'(f) {k.split(" (")[0]} at the plan\'s draw: copy A {oa[k]["v"]:+.4f} [{oa[k]["lo"]:+.4f}, {oa[k]["hi"]:+.4f}] {oa[k]["out"]} | copy B {ob[k]["v"]:+.4f} [{ob[k]["lo"]:+.4f}, {ob[k]["hi"]:+.4f}] {ob[k]["out"]}')
ts = {j['label']: j.get('timestamps') for j in rec['jobs'] if j.get('status') == 'DONE'}
try:
    t = lambda s_: _dt.datetime.fromisoformat(s_.replace('Z', '+00:00'))
    L.append(f'(g) today\'s table (job C) created {ts["C"]["created"][11:19]}, ran {ts["C"]["running"][11:19]} to {ts["C"]["finished"][11:19]} UTC; copy A ran from {ts["A"]["running"][11:19]}, '
             f'{(t(ts["A"]["running"]) - t(ts["C"]["finished"])).total_seconds():.0f} s after job C finished; copy B from {ts["B"]["running"][11:19]}')
except Exception as e: L.append('(g) job timing not in the record: ' + type(e).__name__)
open(f'{D}/readings_second.text', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L[-8:]))
