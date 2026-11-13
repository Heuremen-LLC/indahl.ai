"""fire_ufsm_pairs.py [--fire] -- ADDENDUM 2 (24 Oct, after run 1 and addendum 1 data, BEFORE its job): is the 52 pp DD-off Fig 8(b) deficit
specific to pair [81, 82]? Their layout is not recorded (their notebook transpiles against a simulator). Same circuits (ufsm.circuits(1)),
same transpile settings (optimization_level 3, seed_transpiler 7), DD OFF (their Fig 8 cell has DD commented out), no twirling, on the
pairs ranked 2, 3, 4 by fire_ufsm.py's committed PAIR RULE on the record saved just before this job. One job; one restart then HOLD."""
import json, sys, time, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
import numpy as np, ufsm
from sweep import service
from qiskit import transpile
s = service(); b = s.backend('ibm_kingston'); rem = s.usage().get('usage_remaining_seconds')
props = b.properties(refresh=True).to_dict()
q = {i: {x['name']: x['value'] for x in ps} for i, ps in enumerate(props['qubits'])}
g = {(x['gate'], tuple(x['qubits'])): next((p['value'] for p in x['parameters'] if p['name'] == 'gate_error'), None) for x in props['gates']}
med = float(np.median([v['readout_error'] for v in q.values() if 'readout_error' in v]))
best = sorted((e, k[1]) for k, e in g.items() if k[0] == 'cz' and e is not None and 0 < e < 1 and all(q[x].get('readout_error', 1) <= med for x in k[1]))
seen, pairs = set(), []
for e, p in best:
    key = tuple(sorted(p))
    if key in seen: continue
    seen.add(key); pairs.append(list(p))
pairs = pairs[1:4]
print(f'ibm_kingston pairs ranked 2-4: {pairs}; 1 job x {8*len(pairs)} circuits x {ufsm.SHOTS}; est ~60 s; remaining {rem}')
if '--fire' not in sys.argv: print('DRY RUN'); sys.exit(0)
if rem is not None and rem < 100: print('STOP: seconds'); sys.exit(1)
json.dump(props, open(f'{HERE}/props_ufsm_before_pairs.json', 'w'), default=str)
C = ufsm.circuits(1)[:8]; T = []
for p in pairs: T += transpile(C, b, optimization_level=3, initial_layout=p, seed_transpiler=7)
from qiskit_ibm_runtime import SamplerV2
out = dict(pairs=pairs, jobs=[])
for attempt in (1, 2):
    smp = SamplerV2(mode=b); smp.options.twirling.enable_gates = False; smp.options.twirling.enable_measure = False; smp.options.dynamical_decoupling.enable = False
    job = smp.run(T, shots=ufsm.SHOTS); sub = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()); print('SUBMITTED', job.job_id(), sub, flush=True)
    out['jobs'].append(dict(job_id=job.job_id(), submitted_utc=sub)); json.dump(out, open(f'{HERE}/job_ufsm_pairs.json', 'w'), default=str)
    try: res = job.result(); break
    except Exception as e:
        print('IBM-side ERROR:', str(e)[:160]); out['jobs'][-1]['error'] = str(e)[:300]; json.dump(out, open(f'{HERE}/job_ufsm_pairs.json', 'w'), default=str)
        if attempt == 2: print('HOLD'); sys.exit(2)
P = ufsm.plan(1)[:8]; ents = {}
for i, p in enumerate(pairs):
    ents[str(p)] = [[k, l, {str(kk): int(v) for kk, v in pr.data.c.get_counts().items()}] for (k, l), pr in zip(P, res[8*i:8*i+8])]
json.dump(ents, open(f'{HERE}/raw_ufsm_pairs.json', 'w'))
m = job.metrics(); out['jobs'][-1].update(usage=m.get('usage'), timestamps=m.get('timestamps')); json.dump(out, open(f'{HERE}/job_ufsm_pairs.json', 'w'), default=str)
print('ALL DONE')
