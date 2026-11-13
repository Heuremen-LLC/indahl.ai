#!/usr/bin/env python3
"""extract_rigetti_extra.py -- builds data/rigetti_extra.json from the PRIVATE raw files (read-only; needs numpy).
Not needed to run verify_rigetti_extra.py. Kept so the extraction is auditable.
Inputs (never modified):  standoff/time20261004/{triB,triA,q0_last,triF}.npz + *_tasks.json, wit_roles.json, cepheus_edges.json,
standoff/cepheus_props_20260928.json (qubit list), standoff/chip/whead_tasks.json + standoff/raw_repull/<task-id>.json.gz (28 Sep)."""
import json, gzip, os, time
import numpy as np
S = '/Users/heuremen/bones-forge/standoff'; T4 = S + '/time20261004'
OUT = '/Users/heuremen/bones-forge/heuremen.org-staging/rigetti_extra/data/rigetti_extra.json'
QS = sorted(int(r[0]) for r in json.load(open(S + '/cepheus_props_20260928.json')))
idx = {q: i for i, q in enumerate(QS)}
roles = json.load(open(T4 + '/wit_roles.json')); EM = roles['emitters']
NB = {int(k): v for k, v in roles['neighbours'].items()}
NBRS = sorted({n for q in EM for n in NB[q]} - set(EM))
uuid = lambda arn: arn.split('/')[-1]
utc = lambda t: time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(t))
def tasks(fn): return json.load(open(T4 + '/' + fn))['tasks']
def npz(fn): return {tuple(json.loads(k)): v for k, v in np.load(T4 + '/' + fn).items()}
D = {'meta': {'qubit_ids': QS, 'edges': json.load(open(T4 + '/cepheus_edges.json'))['edges']}}

# ---------------- FINDING A: triB
Z = npz('triB.npz'); Tk = tasks('triB_tasks.json')
order = EM + NBRS
A = {'emitters': EM, 'neighbours_of_emitter': {str(q): NB[q] for q in EM}, 'all_neighbours': NBRS, 'bit_order': order, 'shots': 900,
     'tasks': [{'tag': t['tag'], 'task_id': uuid(t['arn']), 'sent_utc': utc(t['sent'])} for t in Tk], 'e_packed': {}, 'ba_emitter_ones': {}}
for r in (1, 2, 3):
    for s in ('rest', 'pushed', 'clock'):
        z = Z[(s, 'e', r)][:, [idx[q] for q in order]]
        A['e_packed'][f'{r}|{s}'] = [int(sum(int(b) << i for i, b in enumerate(row))) for row in z]
        A['ba_emitter_ones'][f'{r}|{s}'] = [int(Z[(s, 'ba', r)][:, idx[q]].sum()) for q in EM]
D['finding_a'] = A

# ---------------- FINDING B
def counts(Zd, cols):
    return {json.dumps(list(k)): [int(v[:, idx[q]].sum()) for q in cols] for k, v in Zd.items() if k[0] != 'cal' and v.shape[0] <= 1000}
# 28 Sep headline (raw_repull)
W = json.load(open(S + '/chip/whead_tasks.json'))['tasks']; c28 = {}; tk28 = []
for t in W:
    d = json.load(gzip.open(f"{S}/raw_repull/{uuid(t['arn'])}.json.gz")); m = np.array(d['results']['measurements'])
    assert list(d['results']['measuredQubits']) == [0, 9]
    c28[json.dumps(t['tag'])] = [int(m[:, 0].sum()), int(m[:, 1].sum()), int(m.shape[0])]
    tk28.append({'tag': t['tag'], 'task_id': uuid(t['arn']), 'created_utc': d['task']['createdAt'][:19] + 'Z', 'shots': d['task']['shots']})
D['sep28'] = {'emitter': 0, 'clock': 9, 'tasks': tk28, 'ones_q0_q9_shots': c28}
# 4 Oct triA and q0_last: all 107 qubits
def block(fn, tfn):
    Zd = {k: v for k, v in npz(fn).items() if k[0] != 'cal'}; Tk = tasks(tfn)
    return {'tasks': [{'tag': t['tag'], 'task_id': uuid(t['arn']), 'sent_utc': utc(t['sent'])} for t in Tk if t['tag'][0] != 'cal'],
            'shots': 900, 'ones_all_qubits': {json.dumps(list(k)): [int(x) for x in v.sum(0)] for k, v in Zd.items()}}
D['oct4_triA'] = block('triA.npz', 'triA_tasks.json')
D['oct4_q0_last'] = block('q0_last.npz', 'q0_last_tasks.json')
# triF: 22 neighbours + 7 emitters
Zf = {k: v for k, v in npz('triF.npz').items() if k[0] != 'cal'}; Tf = tasks('triF_tasks.json'); cols = EM + NBRS
D['oct4_triF'] = {'emitters': EM, 'neighbours_of_emitter': {str(q): NB[q] for q in EM}, 'columns': cols, 'shots': 900, 'windows_us': [0.25, 0.5, 1, 2, 4, 6],
    'tasks': [{'tag': t['tag'], 'task_id': uuid(t['arn']), 'sent_utc': utc(t['sent'])} for t in Tf if t['tag'][0] != 'cal'],
    'ones': {json.dumps(list(k)): [int(v[:, idx[q]].sum()) for q in cols] for k, v in Zf.items()}}
json.dump(D, open(OUT, 'w'), separators=(',', ':'))
print('wrote', OUT, os.path.getsize(OUT), 'bytes')
