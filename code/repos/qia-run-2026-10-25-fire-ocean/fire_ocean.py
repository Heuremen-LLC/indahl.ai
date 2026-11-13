"""fire_ocean.py --dry | --fire : one SamplerV2 job on ibm_fez, 80 circuits (5 groups x basis/GHZ x 8 reps), 500 shots, record saved before/after."""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
from ocean import GROUPS, SHOTS, circuits, analyse
from sweep import service
from qiskit import transpile
CAP, RESERVE = 150, 300
s = service(); rem = s.usage().get('usage_remaining_seconds'); be = s.backend('ibm_fez'); st = be.status(); print('remaining', rem, 'fez', st.status_msg, st.pending_jobs, flush=True)
fire = '--fire' in sys.argv
if fire and (rem is None or rem - CAP < RESERVE or str(st.status_msg).lower() != 'active'): sys.exit('REFUSED')
C = circuits(); isa = []
for qc in C:
    g = qc.name.split('|')[0]; isa.append(transpile(qc, be, initial_layout=GROUPS[g], optimization_level=1, seed_transpiler=7))
chk = {}
for qc, t in zip(C, isa):
    g, kind, _ = qc.name.split('|'); chk.setdefault((g, kind), set()).add((t.count_ops().get('cz', 0), tuple(sorted({t.find_bit(i.qubits[0]).index for i in t.data if i.operation.name == 'measure'}))))
for k, v in chk.items(): print('compiled', k, v, flush=True)
if not fire:
    open(os.path.join(HERE, 'dry_run_ocean.text'), 'w').write('\n'.join('%s %s' % (k, v) for k, v in chk.items()) + '\n'); sys.exit(0)
json.dump(be.properties(refresh=True).to_dict(), open(os.path.join(HERE, 'props_before.json'), 'w'), default=str)
from qiskit_ibm_runtime import SamplerV2
job = SamplerV2(mode=be).run(isa, shots=SHOTS); rec = dict(job_id=job.job_id(), submitted=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
json.dump(rec, open(os.path.join(HERE, 'job_ocean.json'), 'w')); print('SUBMITTED', rec, flush=True)
res = job.result(); R = {}
for qc, r in zip(C, res):
    g, kind, _ = qc.name.split('|'); R.setdefault(g, {'basis': [], 'ghz': []})[kind].append(r.data.c.get_counts())
m = job.metrics() or {}; rec.update(usage=m.get('usage'), timestamps=m.get('timestamps')); json.dump(rec, open(os.path.join(HERE, 'job_ocean.json'), 'w'), default=str)
json.dump(R, open(os.path.join(HERE, 'raw_counts_ocean.json'), 'w'))
json.dump(be.properties(refresh=True).to_dict(), open(os.path.join(HERE, 'props_after.json'), 'w'), default=str)
out = analyse(R); open(os.path.join(HERE, 'results_ocean.text'), 'w').write(json.dumps(out, indent=1)); print(json.dumps(out, indent=1), 'usage', m.get('usage'), flush=True)
