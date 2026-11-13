"""fire_n47.py --dry | --fire : one SamplerV2 job on ibm_kingston (their chip), five arms, shots per arm as in ARMS (100k on their prediction circuit), opt level 1 (theirs)."""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
from n47 import ARMS, circuit, analyse
from sweep import service
from qiskit import transpile
CAP, RESERVE = 150, 300
s = service(); rem = s.usage().get('usage_remaining_seconds'); be = s.backend('ibm_kingston'); st = be.status(); print('remaining', rem, 'kingston', st.status_msg, st.pending_jobs, flush=True)
fire = '--fire' in sys.argv
if fire and (rem is None or rem - CAP < RESERVE or str(st.status_msg).lower() != 'active'): sys.exit('REFUSED')
isa = []; meta = []
for name, N, phi, v, shots in ARMS:
    t = transpile(circuit(N, phi, v), be, optimization_level=1, seed_transpiler=7); isa.append((t, shots))
    meta.append(dict(arm=name, layout=t.layout.final_index_layout()[:N], cz=t.count_ops().get('cz', 0), depth=t.depth(), shots=shots)); print('compiled', meta[-1], flush=True)
if not fire: open(os.path.join(HERE, 'dry_run_n47.text'), 'w').write(json.dumps(meta, indent=1)); sys.exit(0)
json.dump(be.properties(refresh=True).to_dict(), open(os.path.join(HERE, 'props_before.json'), 'w'), default=str)
from qiskit_ibm_runtime import SamplerV2
job = SamplerV2(mode=be).run([(t, None, sh) for t, sh in isa]); rec = dict(job_id=job.job_id(), submitted=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), meta=meta)
json.dump(rec, open(os.path.join(HERE, 'job_n47.json'), 'w')); print('SUBMITTED', rec['job_id'], flush=True)
res = job.result(); raw = {m['arm']: r.data.c.get_counts() for m, r in zip(meta, res)}
m = job.metrics() or {}; rec.update(usage=m.get('usage'), timestamps=m.get('timestamps')); json.dump(rec, open(os.path.join(HERE, 'job_n47.json'), 'w'), default=str)
json.dump(raw, open(os.path.join(HERE, 'raw_counts_n47.json'), 'w')); json.dump(be.properties(refresh=True).to_dict(), open(os.path.join(HERE, 'props_after.json'), 'w'), default=str)
out = analyse(raw); open(os.path.join(HERE, 'results_n47.text'), 'w').write(json.dumps(out, indent=1)); print(json.dumps(out, indent=1), 'usage', m.get('usage'), flush=True)
