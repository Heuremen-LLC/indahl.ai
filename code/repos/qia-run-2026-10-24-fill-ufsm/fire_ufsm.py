"""fire_ufsm.py [--fire] -- two jobs (copies, ABBA across them) on ibm_kingston (Darkwave Disco via sweep_run/sweep.py service()).
PAIR RULE (fixed before any job): from the record saved just before copy 1, among cz edges with stated gate_error in (0, 1) whose two qubits
both have stated readout_error <= the chip median, the lowest stated cz error (ties: lowest qubits); mode A = first qubit, mode B = second.
Both copies use that pair. Transpile once (their setting: optimization_level 3), initial_layout pair, seed_transpiler 7; no twirling,
no dynamical decoupling (their Fig 8 option cell is commented out; we set DD off explicitly and say so). Records before each job and after.
One restart per copy on an IBM-side ERROR, then HOLD."""
import json, sys, time, hashlib, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
import ufsm
from sweep import service, stated
from qiskit import transpile, qpy
CHIP = 'ibm_kingston'; CAP = 70
def pick(props):
    q, g = stated(props); med = np.median([q[i]['readout_error'] for i in q if 'readout_error' in q[i]])
    best = sorted((e, k[1]) for k, e in g.items() if k[0] == 'cz' and e is not None and 0 < e < 1 and all(q[x].get('readout_error', 1) <= med for x in k[1]))
    return list(best[0][1]), best[0][0], med
s = service(); b = s.backend(CHIP); rem = s.usage().get('usage_remaining_seconds')
props = b.properties(refresh=True).to_dict(); json.dump(props, open(f'{HERE}/props_ufsm_before_copy1.json', 'w'), default=str)
pair, cz, med = pick(props)
T = {c: transpile(ufsm.circuits(c), b, optimization_level=3, initial_layout=pair, seed_transpiler=7) for c in (1, 2)}
used = sorted({t.find_bit(qb).index for t in T[1] + T[2] for ins in t.data for qb in ins.qubits})
qpy.dump(T[1] + T[2], open(f'{HERE}/circuits_ufsm.qpy', 'wb')); ch = hashlib.sha256(open(f'{HERE}/circuits_ufsm.qpy', 'rb').read()).hexdigest()
ops = {k: dict(T[1][i].count_ops()) for i, (k, l) in enumerate(ufsm.plan(1)) if k in ('a', 'b') and l in (0,)} if False else {k: dict(t.count_ops()) for (k, l), t in zip(ufsm.plan(1), T[1]) if k in ('a', 'b')}
est = 2 * 8 * ufsm.SHOTS * 300e-6
print(f'{CHIP}: pair {pair} (stated cz {cz:.2e}, readout median {med:.4f}); physical used {used}; transpiled ops {ops}; 2 jobs x 8 circuits x {ufsm.SHOTS}; est {est:.0f} s (cap {CAP}); remaining {rem}')
if '--fire' not in sys.argv: print('DRY RUN, nothing submitted'); sys.exit(0)
if est > CAP or (rem is not None and rem < est + 30) or used != sorted(pair): print('STOP: cap, seconds or layout'); sys.exit(1)
from qiskit_ibm_runtime import SamplerV2
rec = dict(chip=CHIP, pair=pair, stated_cz=cz, circuits_sha256=ch, shots=ufsm.SHOTS, jobs=[])
for copy in (1, 2):
    if copy == 2: json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_ufsm_before_copy2.json', 'w'), default=str)
    for attempt in (1, 2):
        smp = SamplerV2(mode=b); smp.options.twirling.enable_gates = False; smp.options.twirling.enable_measure = False; smp.options.dynamical_decoupling.enable = False
        job = smp.run(T[copy], shots=ufsm.SHOTS); sub = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()); print('SUBMITTED copy', copy, job.job_id(), sub, flush=True)
        rec['jobs'].append(dict(copy=copy, job_id=job.job_id(), submitted_utc=sub)); json.dump(rec, open(f'{HERE}/job_ufsm.json', 'w'), default=str)
        try:
            res = job.result(); break
        except Exception as e:
            print('IBM-side ERROR:', str(e)[:160], flush=True); rec['jobs'][-1]['error'] = str(e)[:300]; json.dump(rec, open(f'{HERE}/job_ufsm.json', 'w'), default=str)
            if attempt == 2: print('HOLD after second failure'); sys.exit(2)
    ents = [[k, l, {str(kk): int(v) for kk, v in pr.data.c.get_counts().items()}] for (k, l), pr in zip(ufsm.plan(copy), res)]
    json.dump(ents, open(f'{HERE}/raw_ufsm_copy{copy}.json', 'w'))
    m = job.metrics(); rec['jobs'][-1].update(usage=m.get('usage'), timestamps=m.get('timestamps')); json.dump(rec, open(f'{HERE}/job_ufsm.json', 'w'), default=str)
json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_ufsm_after.json', 'w'), default=str); print('ALL DONE', flush=True)
