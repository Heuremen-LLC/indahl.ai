"""fire_shch.py --dry | --fire : jobs A1 fez, B1 kingston, B2 kingston, A2 fez; 8 circuits each (4 singlet + 4 product), 8000 shots, layout [109,110,118], opt 1."""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
from shch import circuits, analyse, SHOTS, LAYOUT
from sweep import service
from qiskit import transpile
ORDER = [('A1', 'ibm_fez'), ('B1', 'ibm_kingston'), ('B2', 'ibm_kingston'), ('A2', 'ibm_fez')]; CAP, RESERVE = 80, 300
s = service(); rem = s.usage().get('usage_remaining_seconds'); print('remaining', rem, flush=True); fire = '--fire' in sys.argv
if fire and (rem is None or rem - CAP < RESERVE): sys.exit('REFUSED')
isa = {}
for b in set(x[1] for x in ORDER):
    be = s.backend(b); isa[b] = [transpile(c, be, optimization_level=1, initial_layout=LAYOUT, seed_transpiler=3) for c in circuits()]
    print('compiled', b, [t.count_ops().get('cz', 0) for t in isa[b]], 'measured', sorted({t.find_bit(i.qubits[0]).index for t in isa[b] for i in t.data if i.operation.name == 'measure'}), flush=True)
if not fire: open(os.path.join(HERE, 'dry_run_shch.text'), 'w').write(json.dumps({b: [t.count_ops().get('cz', 0) for t in v] for b, v in isa.items()})); sys.exit(0)
from qiskit_ibm_runtime import SamplerV2
jobs = []
for label, b in ORDER:
    be = s.backend(b); st = be.status()
    if str(st.status_msg).lower() != 'active': print('SKIP', label, b, st.status_msg); continue
    json.dump(be.properties(refresh=True).to_dict(), open(os.path.join(HERE, 'props_before_%s.json' % label), 'w'), default=str)
    job = SamplerV2(mode=be).run(isa[b], shots=SHOTS); print('SUBMITTED', label, b, job.job_id(), flush=True)
    res = job.result(); m = job.metrics() or {}
    jobs.append(dict(label=label, backend=b, job_id=job.job_id(), counts=[r.data.c.get_counts() for r in res], usage=m.get('usage'), timestamps=m.get('timestamps')))
    json.dump(jobs, open(os.path.join(HERE, 'jobs_shch.json'), 'w'), default=str); print('DONE', label, 'usage', (m.get('usage') or {}).get('qpu_charge_time_seconds'), flush=True)
out = analyse(jobs); open(os.path.join(HERE, 'results_shch.text'), 'w').write(json.dumps(out, indent=1, default=float)); print(json.dumps(out, indent=1, default=float), flush=True)
