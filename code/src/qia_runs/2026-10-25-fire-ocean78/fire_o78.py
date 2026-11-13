"""fire_o78.py --dry | --fire : one SamplerV2 job on ibm_fez, 7 pubs (COLLAPSED x3 default preset, REAL x3 opt 0, KG), 10000 shots, 40 qubits."""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
from o78 import QUBITS, S_LEVELS, SHOTS, logical, analyse
from sweep import service
from qiskit import transpile
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
CAP, RESERVE = 90, 300
s = service(); rem = s.usage().get('usage_remaining_seconds'); be = s.backend('ibm_fez'); st = be.status(); print('remaining', rem, 'fez', st.status_msg, st.pending_jobs, flush=True)
fire = '--fire' in sys.argv
if fire and (rem is None or rem - CAP < RESERVE or str(st.status_msg).lower() != 'active'): sys.exit('REFUSED')
pm = generate_preset_pass_manager(backend=be, initial_layout=QUBITS)   # the default preset, as a Qiskit 2.5.2 user gets it
pubs, tags = [], []
for S in S_LEVELS: pubs.append(pm.run(logical(S, 'X'))); tags.append(('COLLAPSED', str(S)))
for S in S_LEVELS: pubs.append(transpile(logical(S, 'X'), be, optimization_level=0, initial_layout=QUBITS)); tags.append(('REAL', str(S)))
pubs.append(transpile(logical(0, 'KG'), be, optimization_level=1, initial_layout=QUBITS)); tags.append(('KG', 'KG'))
info = [dict(tag=t, id_per_qubit=p.count_ops().get('id', 0) / len(QUBITS), ops=dict(p.count_ops()), duration_dt=p.estimate_duration(be.target, unit='dt') if hasattr(p, 'estimate_duration') else None) for t, p in zip(tags, pubs)]
for i in info: print('compiled', i, flush=True)
if not fire: open(os.path.join(HERE, 'dry_run_o78.text'), 'w').write(json.dumps(info, indent=1, default=str)); sys.exit(0)
P = be.properties(refresh=True); json.dump(P.to_dict(), open(os.path.join(HERE, 'props_before.json'), 'w'), default=str)
rec = {q: (P.t1(q), P.t2(q), P.qubit_property(q).get('prob_meas1_prep0', (P.readout_error(q),))[0]) for q in QUBITS}
from qiskit_ibm_runtime import SamplerV2
job = SamplerV2(mode=be).run(pubs, shots=SHOTS); meta = dict(job_id=job.job_id(), submitted=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())); print('SUBMITTED', meta, flush=True)
json.dump(meta, open(os.path.join(HERE, 'job_o78.json'), 'w'))
res = job.result(); raw = {'COLLAPSED': {}, 'REAL': {}, 'KG': {}}
for (arm, key), r in zip(tags, res): raw[arm][key] = r.data.c.get_counts()
m = job.metrics() or {}; meta.update(usage=m.get('usage'), timestamps=m.get('timestamps')); json.dump(meta, open(os.path.join(HERE, 'job_o78.json'), 'w'), default=str)
json.dump(raw, open(os.path.join(HERE, 'raw_counts_o78.json'), 'w')); json.dump({str(k): v for k, v in rec.items()}, open(os.path.join(HERE, 'record_used.json'), 'w'))
out = analyse(raw, rec); open(os.path.join(HERE, 'results_o78.text'), 'w').write(json.dumps(out, indent=1)); print(json.dumps(out, indent=1), 'usage', m.get('usage'), flush=True)
