"""fire_tara.py [--fire] -- one job on ibm_fez (Darkwave Disco via sweep_run/sweep.py service()).
PAIR RULE (fixed before any job): from the record saved just before the job, among cz edges with a stated gate_error in (0, 1) whose
two qubits both have stated readout_error <= the chip median, take the edge with the lowest stated cz error (ties: lowest qubits);
q0 = first qubit of that edge, q1 = second. Transpile once, optimization_level 1, initial_layout [q0, q1], seed_transpiler 7; no twirling,
no dynamical decoupling (SamplerV2 defaults, set explicitly). Records saved before and after the job. One restart on an IBM-side ERROR,
then HOLD (no third attempt)."""
import json, sys, time, hashlib, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
import tara
from sweep import service, stated
from qiskit import transpile, qpy
CHIP = 'ibm_fez'; CAP = 40
def pick(props):
    q, g = stated(props); med = np.median([q[i]['readout_error'] for i in q if 'readout_error' in q[i]])
    best = sorted((e, k[1]) for k, e in g.items() if k[0] == 'cz' and e is not None and 0 < e < 1
                  and all(q[x].get('readout_error', 1) <= med for x in k[1]))
    return list(best[0][1]), best[0][0], med
s = service(); b = s.backend(CHIP); rem = s.usage().get('usage_remaining_seconds')
props = b.properties(refresh=True).to_dict(); json.dump(props, open(f'{HERE}/props_tara_before.json', 'w'), default=str)
pair, cz, med = pick(props); circs = tara.circuits()
tq = transpile(circs, b, optimization_level=1, initial_layout=pair, seed_transpiler=7)
phys = sorted({tq[0].find_bit(qb).index for ins in tq[0].data for qb in ins.qubits})
qpy.dump(tq, open(f'{HERE}/circuits_tara.qpy', 'wb')); ch = hashlib.sha256(open(f'{HERE}/circuits_tara.qpy', 'rb').read()).hexdigest()
nshots = tara.SHOTS * len(circs); est = nshots * 300e-6
print(f'{CHIP}: pair {pair} (stated cz {cz:.2e}, readout median {med:.4f}); physical used {phys}; {len(circs)} circuits x {tara.SHOTS} shots; est {est:.0f} s (cap {CAP}); remaining {rem}')
if '--fire' not in sys.argv: print('DRY RUN, nothing submitted'); sys.exit(0)
if est > CAP or (rem is not None and rem < est + 30): print('STOP: cap or seconds'); sys.exit(1)
from qiskit_ibm_runtime import SamplerV2
rec = dict(chip=CHIP, pair=pair, stated_cz=cz, circuits_sha256=ch, shots=tara.SHOTS, plan=[[k, l] for k, l in tara.plan()], jobs=[])
for attempt in (1, 2):
    smp = SamplerV2(mode=b); smp.options.twirling.enable_gates = False; smp.options.twirling.enable_measure = False; smp.options.dynamical_decoupling.enable = False
    job = smp.run(tq, shots=tara.SHOTS); sub = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()); print('SUBMITTED', job.job_id(), sub, flush=True)
    rec['jobs'].append(dict(job_id=job.job_id(), submitted_utc=sub)); json.dump(rec, open(f'{HERE}/job_tara.json', 'w'), default=str)
    try:
        res = job.result(); break
    except Exception as e:
        print('IBM-side ERROR:', str(e)[:160], flush=True); rec['jobs'][-1]['error'] = str(e)[:300]; json.dump(rec, open(f'{HERE}/job_tara.json', 'w'), default=str)
        if attempt == 2: print('HOLD after second failure'); sys.exit(2)
ents = [[k, l, {str(kk): int(v) for kk, v in pr.data.c.get_counts().items()}] for (k, l), pr in zip(tara.plan(), res)]
json.dump(ents, open(f'{HERE}/raw_tara.json', 'w'))
m = job.metrics(); rec['jobs'][-1].update(usage=m.get('usage'), timestamps=m.get('timestamps')); json.dump(rec, open(f'{HERE}/job_tara.json', 'w'), default=str)
json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_tara_after.json', 'w'), default=str)
print('DONE usage', (m.get('usage') or {}).get('quantum_seconds') or (m.get('usage') or {}).get('seconds'), flush=True)
