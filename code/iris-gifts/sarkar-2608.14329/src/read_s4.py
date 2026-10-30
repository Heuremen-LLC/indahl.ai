#!/usr/bin/env python3
"""S4 readings: our live similarities (runs/s4_*) against their released per-cluster similarities and verdicts. Our code."""
import json, os, glob, math, statistics
H = os.path.dirname(os.path.abspath(__file__)); B = os.path.join(H, '..', 'theirs', 'tree_a2e47ae')
sig = lambda z: 1 / (1 + math.exp(-z))
for key in ('minilm', 'bge'):
    r1 = json.load(open(H + '/runs/s4_%s_r1.json' % key)); r2 = json.load(open(H + '/runs/s4_%s_r2.json' % key))
    rep = max(abs(a[f] - b[f]) for i in r1['sims'] for p in r1['sims'][i] for a, b in zip(r1['sims'][i][p], r2['sims'][i][p]) for f in ('avg_positive_sim', 'avg_negative_sim'))
    print('%s (%s @ %s): repeat floor, max |r1 - r2| over every scenario, principle and cluster: %.2e' % (key, r1['meta']['model'], r1['meta']['revision'][:12], rep))
    diffs, n, missing, vt, vflip, sdiff = [], 0, 0, 0, 0, []
    for f in sorted(glob.glob(B + '/runs/*_%s_*.json' % key)):
        d = json.load(open(f)); split = d['split']; ds = []
        for s in d['per_scenario']:
            if 'assessments' not in s: continue
            if s['id'] not in r1['sims']: missing += 1; continue
            for a in s['assessments']:
                ours = {c['cluster_id']: c for c in r1['sims'][s['id']][a['principle_id']]}
                for c in a['cluster_assessments']:
                    o = ours[c['cluster_id']]
                    for fld in ('avg_positive_sim', 'avg_negative_sim'):
                        ds.append(abs(o[fld] - c[fld])); n += 1
                sh = sum(o['w'] * sig(o['avg_positive_sim'] - o['avg_negative_sim']) for o in ours.values()) / sum(o['w'] for o in ours.values())
                sdiff.append(abs(sh - a['confidence_score'])); vt += 1
                vflip += (sh < r1['principles'][a['principle_id']]) != a['escalation_required']
        diffs += ds
        print('  %-11s %4d values | max |ours - theirs| %.2e | median %.2e' % (split, len(ds), max(ds), statistics.median(ds)))
    print('  all splits: %d similarity values, max %.2e, median %.2e, values off by more than 1e-6: %d | Eq. 2 score max |diff| %.2e | verdicts differing from theirs %d of %d | scenarios not found %d' % (
        n, max(diffs), statistics.median(diffs), sum(x > 1e-6 for x in diffs), max(sdiff), vflip, vt, missing))
