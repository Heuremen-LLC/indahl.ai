#!/usr/bin/env python3
"""Written-off anomalies vs outside holes. Pre-registered: biblioteca 2026-09-26 ~22:00Z LINEUP ADDENDUM. Run with qvenv python."""
import json, os, re
import numpy as np
import lineup as L

H = os.path.dirname(os.path.abspath(__file__))
jobs = json.load(open(os.path.join(H, 'anomaly_jobs.json')))
short = {'first-look': 'A1 first-look dip', 'empty corner': 'A2 corner-11', 't=30': 'A3 t=30 excess', 'Kingston q1': 'A4 Kingston q1'}
for j in jobs:
    j['A'] = next(v for k, v in short.items() if j['anomaly'].startswith(k))
    j['t0'], j['t1'] = L.ts(j['running']), L.ts(j['finished'])

# ---- (a) calibration check ----
recs = [json.loads(l) for l in open(os.path.join(H, 'outside_holes.jsonl'))]
recs = [r for r in recs if r['provider'] == 'ibm-calibration']
cal = []
for j in jobs:
    hits = []
    for r in recs:
        be, _, part = r['device'].partition('/')
        if be != j['backend']:
            continue
        a = L.ts(r['at']); b = L.ts(r['ended']) if r['ended'] else float('inf')
        if not (a <= j['t0'] and b >= j['t1']):
            continue
        qs = [int(x) for x in re.findall(r'\d+', part)] if part else None
        if r['kind'] == 'no-calibration' or (qs and set(qs) & set(j['qubits'])):
            hits.append({'kind': r['kind'], 'device': r['device'], 'at': r['at'], 'ended': r['ended'] or 'open', 'reason': r['reason']})
    # nearest recorded IBM calibration-condition change on that backend touching the job's qubits (any time)
    near = []
    for r in recs:
        be, _, part = r['device'].partition('/')
        qs = [int(x) for x in re.findall(r'\d+', part)] if part else []
        if be == j['backend'] and set(qs) & set(j['qubits']):
            for t in (L.ts(r['at']),) + ((L.ts(r['ended']),) if r['ended'] else ()):
                near.append((abs(t - j['t0']) / 3600, r['device'], r['kind'], r['at'], r['ended'] or 'open'))
    near.sort()
    cal.append({'A': j['A'], 'job': j['job'], 'backend': j['backend'], 'qubits': j['qubits'], 'running': j['running'],
                'finished': j['finished'], 'active_holes_on_its_qubits': hits,
                'nearest_condition_change_h': [dict(zip(('hours', 'device', 'kind', 'at', 'ended'), n)) for n in near[:3]]})

# ---- (b) timeline test ----
S = L.load()
rng = np.random.default_rng(20260926)
res = []
for A in sorted({j['A'] for j in jobs}):
    win = L.merge([(j['t0'], j['t1']) for j in jobs if j['A'] == A])
    for X in ('NIST', 'IBM'):
        bx = L.truncate_weeks(S[X]['blocks'])
        weeks = [int(round((e - s) / L.WEEK)) for s, e in bx]

        def met(offs):
            h = L.shift_iv(S[X]['holes'], bx, offs) if any(offs) else L.clip(S[X]['holes'], bx)
            p = L.shift_pts(S[X]['pts'], bx, offs) if any(offs) else np.sort(S[X]['pts'])
            m = {'M0': L.overlap_len(win, h)}
            for W, k in ((300, 'M5'), (3600, 'M60')):
                m[k] = int(sum(((p >= a - W) & (p <= b + W)).any() for a, b in win))
            return m
        obs = met([0.0] * len(bx))
        null = {k: [] for k in obs}
        for _ in range(L.NSHIFT):
            for k, v in met([float(rng.integers(1, w)) * L.WEEK for w in weeks]).items():
                null[k].append(v)
        for k in obs:
            n = np.array(null[k], float); ge = int((n >= obs[k]).sum())
            res.append({'anomaly': A, 'vs': X, 'metric': k, 'n_windows': len(win), 'window_s': float((win[:, 1] - win[:, 0]).sum()),
                        'observed': obs[k], 'null_mean': float(n.mean()), 'p': ge / L.NSHIFT, 'p_conservative': (1 + ge) / (L.NSHIFT + 1)})
for r in res:
    r['p_bonf'] = min(1.0, r['p'] * len(res)); r['survives'] = r['p_bonf'] < 0.05
# nearest NIST hole to each anomaly (plain distance, descriptive)
nearest = {}
for A in sorted({j['A'] for j in jobs}):
    t = min(j['t0'] for j in jobs if j['A'] == A)
    for X in ('NIST', 'IBM'):
        h = S[X]['holes']
        inside = bool(((h[:, 0] <= t) & (h[:, 1] >= t)).any())
        d = np.minimum(np.abs(h[:, 0] - t), np.abs(h[:, 1] - t)).min() / 3600
        nearest[f'{A} vs {X}'] = {'inside_hole': inside, 'nearest_hole_edge_h': round(float(d), 2)}
out = {'preregistered': 'gridsong/biblioteca.md 2026-09-26 ~22:00Z LINEUP ADDENDUM', 'ligo': 'no public LIGO data after 2025-01-28: untestable',
       'calibration_check': cal, 'timeline_test': res, 'n_tests': len(res), 'nearest': nearest,
       'survivors': [f"{r['anomaly']} vs {r['vs']} {r['metric']}" for r in res if r['survives']]}
json.dump(out, open(os.path.join(H, 'anomaly_lineup_results.json'), 'w'), indent=1)
for c in cal:
    print(c['A'], c['job'], c['backend'], 'active:', [(h['device'], h['kind'], h['at'], h['ended']) for h in c['active_holes_on_its_qubits']],
          'nearest:', [(round(n['hours'], 1), n['device'], n['kind']) for n in c['nearest_condition_change_h'][:2]])
for r in res:
    print(r['anomaly'], r['vs'], r['metric'], r['observed'], round(r['null_mean'], 3), r['p'], r['p_bonf'])
print(nearest)
print('survivors', out['survivors'])
