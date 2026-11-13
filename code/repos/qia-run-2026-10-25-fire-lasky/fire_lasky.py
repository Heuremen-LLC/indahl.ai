"""fire_lasky.py --dry | --fire : 4 back-to-back jobs on ibm_fez, each pubs [GHZ3, GHZ3, GHZ5, GHZ5], 1024 shots, pinned layouts, opt 1."""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
from lasky import circuit, analyse, LAYOUT, SHOTS
from sweep import service
from qiskit import transpile
CAP, RESERVE, NJOBS = 40, 300, 4
s = service(); rem = s.usage().get('usage_remaining_seconds'); be = s.backend('ibm_fez'); st = be.status(); print('remaining', rem, 'fez', st.status_msg, st.pending_jobs, flush=True)
fire = '--fire' in sys.argv
if fire and (rem is None or rem - CAP < RESERVE or str(st.status_msg).lower() != 'active'): sys.exit('REFUSED')
T = {k: transpile(circuit(k), be, optimization_level=1, initial_layout=LAYOUT[k], seed_transpiler=5) for k in ('GHZ3', 'GHZ5')}
for k, t in T.items(): print('compiled', k, dict(t.count_ops()), 'duration_dt', t.estimate_duration(be.target, unit='dt'), flush=True)
if not fire: open(os.path.join(HERE, 'dry_run_lasky.text'), 'w').write(json.dumps({k: dict(t.count_ops()) for k, t in T.items()})); sys.exit(0)
from qiskit_ibm_runtime import SamplerV2
jobs = []
for i in range(NJOBS):
    json.dump(be.properties(refresh=True).to_dict(), open(os.path.join(HERE, 'props_before_%d.json' % i), 'w'), default=str)
    job = SamplerV2(mode=be).run([T['GHZ3'], T['GHZ3'], T['GHZ5'], T['GHZ5']], shots=SHOTS); print('SUBMITTED', i, job.job_id(), flush=True)
    res = job.result(); m = job.metrics() or {}
    c = [r.data.c.get_counts() for r in res]; jobs.append(dict(job_id=job.job_id(), GHZ3=c[:2], GHZ5=c[2:], timestamps=m.get('timestamps')))
    json.dump(jobs, open(os.path.join(HERE, 'jobs_lasky.json'), 'w'), default=str)
out = analyse(jobs); open(os.path.join(HERE, 'results_lasky.text'), 'w').write(json.dumps(out, indent=1)); print(json.dumps(out, indent=1), flush=True)
