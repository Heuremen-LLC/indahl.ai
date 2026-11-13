#!/usr/bin/env python3
"""reread_count.py: what the Note 3 re-read (30 Oct 2026) changed, run by run. Heuremen LLC, 3 Nov 2026.
Compares each re-read file data/res_<job>n3.json with the original data/res_<job>.json it corrects, qubit by qubit.
A readout call is an ABOVE or BELOW outcome on P(1|0) or P(0|1). Written for the outside referee's ask (Sage, 3 Nov):
print how much the call count moved, not just that no verdict did. Standard library only. Output: reread_count.text"""
import json, glob, os
H = os.path.dirname(os.path.abspath(__file__)); D = ('ABOVE', 'BELOW')
tot = dict(runs=0, before=0, after=0, withdrawn=0, flipped=0, new=0, t1_changed=0, known_good=0); out = []
out.append('run (UTC)                 n_ibm  calls before -> after')
for f in sorted(glob.glob(os.path.join(H, 'data', 'res_*n3.json'))):
    a = json.load(open(f)); b = json.load(open(f[:-len('n3.json')] + '.json')); bq = {x['qubit']: x for x in b['qubits']}
    cb = ca = 0
    for x in a['qubits']:
        y = bq[x['qubit']]
        for k in ('p10_outcome', 'p01_outcome'):
            ob, oa = y[k], x[k]; cb += ob in D; ca += oa in D
            tot['withdrawn'] += ob in D and oa == 'CONSISTENT'; tot['flipped'] += ob in D and oa in D and ob != oa
            tot['new'] += ob not in D and oa in D
        tot['t1_changed'] += y['t1_outcome'] != x['t1_outcome']
    tot['runs'] += 1; tot['before'] += cb; tot['after'] += ca; tot['known_good'] += a['known_good'] == 'passed'
    out.append(f"{a['processor']:<14} {a['window_utc'][0][:16]}  {a['ibm_readout_shots']:>5}  {cb:>4} -> {ca}")
t = tot
out += ['', f"runs re-read: {t['runs']}; re-read at n = 4,096: " + ', '.join(l.split()[0] + ' ' + l.split()[1] for l in out[1:] if l.split()[2] == '4096'),
        f"readout calls: {t['before']:,} -> {t['after']:,} ({t['withdrawn']} withdrew to CONSISTENT, {100 * t['withdrawn'] / t['before']:.0f} %)",
        f"calls that changed direction: {t['flipped']}; new calls: {t['new']}; T1 outcomes changed: {t['t1_changed']}",
        f"runs passing known-good after the re-read: {t['known_good']} of {t['runs']}"]
open(os.path.join(H, 'reread_count.text'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
