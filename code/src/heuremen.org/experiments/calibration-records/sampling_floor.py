"""sampling_floor.py -- the sampling null behind sampling_floor.text: the median per-qubit change in IBM's readout_error that sampling alone
would give between two measurements of the same qubits, if nothing about the qubits changed.

Part 1 is the code that wrote sampling_floor.text on 22 Oct 2026 (night, US Eastern), kept as it ran. It was run inline and never committed
(commit a19fe7c added only its output). Recovered 3 Nov 2026 from the session transcript that ran it, on the outside referee's ask
(Sage, 3 Nov: "commit the null's code, not just its output"). Only the paths were made relative to this file. Same seed, same order.
Per qubit: each qubit's own prob_meas1_prep0 and prob_meas0_prep1 from the 22 Oct readout-audit records, two independent binomial draws
per state, readout_error = their mean, median of |r2/r1 - 1| over the qubits, median of that over 200 repeats.

Part 2 (added 3 Nov 2026, after the referee's read) draws at each record's real shot count instead of a fixed 4,096. The count is read from
the record the same way as shot_grid.py: 1,024 if every readout probability is a multiple of 1/1024, otherwise 4,096. The marrakesh record
used here (22 Oct) is on the 1/1024 grid (shot_grid.text). Run: python3 sampling_floor.py > sampling_floor.text"""
import json, os, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(H, '..', '2026-10-22-readout-audit')

# ---- Part 1, as run on 22 Oct 2026 ----
# Sampling floor for record note 8: median per-qubit |new/old - 1| of readout_error expected from 4096-shot sampling alone, if nothing changed (22 Oct 2026 night).
rng=np.random.default_rng(8)
files={'ibm_fez':os.path.join(A,'props_ro_ibm_fez.json'),'ibm_kingston':os.path.join(A,'props_ro_ibm_kingston.json'),'ibm_marrakesh':os.path.join(A,'props_ro_ibm_marrakesh.json')}
for c,f in files.items():
    d=json.load(open(f)); a=[];b=[]
    for q in d['qubits']:
        v={x['name']:x['value'] for x in q}
        if 'prob_meas1_prep0' in v and 'prob_meas0_prep1' in v: a.append(v['prob_meas1_prep0']); b.append(v['prob_meas0_prep1'])
    a=np.array(a); b=np.array(b); ch=[]
    for _ in range(200):
        r1=(rng.binomial(4096,a)/4096+rng.binomial(4096,b)/4096)/2; r2=(rng.binomial(4096,a)/4096+rng.binomial(4096,b)/4096)/2
        m=(r1>0)&(r2>0); ch.append(np.median(np.abs(r2[m]/r1[m]-1)))
    print(f'{c}: sampling alone, two 4096-shot measurements of the same qubits, median per-qubit change {100*np.median(ch):.1f} %')

# ---- Part 2, 3 Nov 2026: the same null at each record's real shot count ----
def shots(a, b):
    v = [x for x in np.concatenate([a, b]) if x not in (0, 1)]
    return 1024 if v and all(abs(x * 1024 - round(x * 1024)) < 1e-6 for x in v) else 4096
rng = np.random.default_rng(8)
for c, f in files.items():
    d = json.load(open(f)); a = []; b = []
    for q in d['qubits']:
        v = {x['name']: x['value'] for x in q}
        if 'prob_meas1_prep0' in v and 'prob_meas0_prep1' in v: a.append(v['prob_meas1_prep0']); b.append(v['prob_meas0_prep1'])
    a = np.array(a); b = np.array(b); n = shots(a, b); ch = []
    for _ in range(200):
        r1 = (rng.binomial(n, a) / n + rng.binomial(n, b) / n) / 2; r2 = (rng.binomial(n, a) / n + rng.binomial(n, b) / n) / 2
        m = (r1 > 0) & (r2 > 0); ch.append(np.median(np.abs(r2[m] / r1[m] - 1)))
    print(f'{c} (record {str(d.get("last_update_date"))[:16]}): sampling alone at the record\'s real shot count, two {n}-shot measurements, median per-qubit change {100 * np.median(ch):.1f} %')

# ---- Part 3, 3 Nov 2026: the null for every record pair Q9 cites, beside the observed change ----
# Pairs are made exactly as record_notes.py makes them (consecutive records of a processor by readout_error date). The earlier record's own
# per-qubit probabilities are taken as the truth; each side is drawn at its own record's real shot count. ratio = observed / null median;
# p97.5 = the 97.5th percentile of the null's median over the 200 repeats. Written for the referee's ask to name the thinnest margin.
import sys; sys.path.insert(0, H); import record_notes as RN
P = RN.P; byc = {}
for (chip, stamp), (d, src) in RN.records().items():
    if chip not in files: continue
    ro = []; pa = []; pb = []
    for q in d['qubits']:
        v = {x['name']: x for x in q}
        if 'readout_error' not in v: ro = None; break
        ro.append((v['readout_error']['value'], v['readout_error']['date']))
        pa.append(v.get('prob_meas1_prep0', {}).get('value')); pb.append(v.get('prob_meas0_prep1', {}).get('value'))
    if ro and None not in pa and None not in pb:
        byc.setdefault(chip, {})[ro[0][1]] = ([r[0] for r in ro], np.array(pa, float), np.array(pb, float))
CITED = open(os.path.join(H, 'results_record_notes.text')).read()   # the pairs results_record_notes.text lists (Q9's cited set); later records are marked new
print('\npair (readout_error dates)                              n old/new  observed  null median  null p97.5  ratio')
rows = []
for chip in files:
    ks = sorted(byc.get(chip, {}), key=P)
    for x, y in zip(ks, ks[1:]):
        (A, a, b), (B, a2, b2) = byc[chip][x], byc[chip][y]
        if len(A) != len(B): continue
        ch = [abs(v2 / v1 - 1) for v1, v2 in zip(A, B) if v1 > 0 and v2 > 0]
        if not ch or all(c == 0 for c in ch): continue
        obs = float(np.median(ch)); h = (P(y) - P(x)).total_seconds() / 3600
        n1, n2 = shots(a, b), shots(a2, b2); rng = np.random.default_rng(8); nul = []
        for _ in range(200):
            r1 = (rng.binomial(n1, a) / n1 + rng.binomial(n1, b) / n1) / 2; r2 = (rng.binomial(n2, a) / n2 + rng.binomial(n2, b) / n2) / 2
            m = (r1 > 0) & (r2 > 0); nul.append(np.median(np.abs(r2[m] / r1[m] - 1)))
        nm, p975 = float(np.median(nul)), float(np.percentile(nul, 97.5)); rows.append((obs / nm, chip, x, y, h, obs, nm))
        print(f'{chip:<13} {x[:16]} -> {y[:16]} {h:6.1f} h  {n1}/{n2}  {100 * obs:6.1f} %  {100 * nm:8.1f} %  {100 * p975:8.1f} %  {obs / nm:4.1f}x  {"above p97.5" if obs > p975 else "NOT above p97.5"}{"" if f"{chip} {x[:16]} -> {y[:16]}" in CITED else "  (not in results_record_notes.text)"}')
r = min(rows); print(f'thinnest margin (all pairs above): {r[1]} {r[2][:16]} -> {r[3][:16]} ({r[4]:.1f} h apart), observed {100 * r[5]:.1f} % against a null of {100 * r[6]:.1f} %, {r[0]:.1f}x')
