"""fire_pav.py --dry | --fire : job A = 7 pubs on ibm_fez (best_a, best_b, q25, q50, q75 at opt 1; best at opt 0 and opt 3), 4,096 shots;
job B (submitted right after A returns) = best at opt 1 once. Refuses if fez not active or remaining - CAP < RESERVE."""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
from pav import circuit, SHOTS
from pav_fill import analyse
from sweep import service
from qiskit import transpile
CAP, RESERVE = 40, 300
L = json.load(open(os.path.join(HERE, 'layouts_chosen.json')))
PLAN = [('best_a', 'best', 1), ('q25', 'q25', 1), ('best_opt0', 'best', 0), ('q50', 'q50', 1), ('best_opt3', 'best', 3), ('q75', 'q75', 1), ('best_b', 'best', 1)]
s = service(); rem = s.usage().get('usage_remaining_seconds'); be = s.backend('ibm_fez'); st = be.status(); print('remaining', rem, 'fez', st.status_msg, st.pending_jobs, flush=True)
fire = '--fire' in sys.argv
if fire and (rem is None or rem - CAP < RESERVE or str(st.status_msg).lower() != 'active'): sys.exit('REFUSED')
def build(lay, opt): return transpile(circuit(), be, optimization_level=opt, initial_layout=L[lay]['layout'], seed_transpiler=5)
pubs = [build(l, o) for _, l, o in PLAN]
info = {a: dict(depth=t.depth(), ops={k: int(v) for k, v in t.count_ops().items()}, measured=[t.find_bit(i.qubits[0]).index for i in t.data if i.operation.name == 'measure'] and
        [t.layout.final_index_layout()[4]] if t.layout else None) for (a, _, _), t in zip(PLAN, pubs)}
print(json.dumps(info), flush=True)
if not fire: open(os.path.join(HERE, 'dry_run_pav.text'), 'w').write(json.dumps(info, indent=1)); sys.exit(0)
from qiskit_ibm_runtime import SamplerV2
json.dump(be.properties(refresh=True).to_dict(), open(os.path.join(HERE, 'props_before.json'), 'w'), default=str)
jA = SamplerV2(mode=be).run(pubs, shots=SHOTS); recA = dict(job_id=jA.job_id(), submitted=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())); print('SUBMITTED A', recA, flush=True)
rA = jA.result(); raw = {a: r.data.c.get_counts() for (a, _, _), r in zip(PLAN, rA)}; recA['metrics'] = jA.metrics()
jB = SamplerV2(mode=be).run([build('best', 1)], shots=SHOTS); recB = dict(job_id=jB.job_id(), submitted=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())); print('SUBMITTED B', recB, flush=True)
raw['best_jobB'] = jB.result()[0].data.c.get_counts(); recB['metrics'] = jB.metrics()
json.dump(dict(A=recA, B=recB), open(os.path.join(HERE, 'jobs_pav.json'), 'w'), default=str); json.dump(raw, open(os.path.join(HERE, 'raw_counts.json'), 'w'))
out = analyse(raw); open(os.path.join(HERE, 'results_pav.text'), 'w').write(json.dumps(out, indent=1, default=float)); print(json.dumps(out, indent=1, default=float), flush=True)
