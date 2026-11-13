#!/usr/bin/env python3
"""Per-chip witness/maker table for the paper. Uses the SAME rules, seed and bootstrap as
verify.py in the released data (data/clocks/*.json). Usage: python3 -I recompute_table.py <path-to-three-positions-dir>"""
import json, glob, os, sys, random, statistics as st
D = sys.argv[1]
CUT = 4.0
rows = {}
for f in sorted(glob.glob(os.path.join(D, 'data', 'clocks', '*.json'))):
    c = json.load(open(f)); n = c['chip']; L = c['stated_look_us']
    def est(sel):
        random.seed(20261011)
        v = st.median(sel) / L
        bs = [st.median(random.choices(sel, k=len(sel))) / L for _ in range(400)]
        return v, st.pstdev(bs)
    allc = [k['reported_look_us'] for k in c['clocks']]
    above = [k['reported_look_us'] for k in c['clocks'] if k['detuning_deg_per_us'] > CUT]
    phys = [x for x in above if x > 0]
    rows[n] = dict(stated=L, n_all=len(allc), n_above=len(above), n_neg=len(above) - len(phys),
                   n_phys=len(phys), cut=est(above), phys=est(phys))
for n, r in rows.items():
    print('%-15s L=%.3f nall=%d nabove=%d nneg=%d nphys=%d  cut %.4f+-%.4f  phys %.4f+-%.4f  witness_us(phys)=%.3f'
          % (n, r['stated'], r['n_all'], r['n_above'], r['n_neg'], r['n_phys'], *r['cut'], *r['phys'], r['phys'][0]*r['stated']))
