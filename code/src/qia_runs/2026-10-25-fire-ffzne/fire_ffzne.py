"""fire_ffzne.py --dry | --fire : job A (ibm_fez) = 6 Estimator PUBs, their options (resilience 0, TREX on, gate twirling auto, DD XY4,
10,000 shots), their circuit (50-qubit QIC r=1) compiled at opt 3, seed 42 on each chosen layout: s1_a, q25, mid, q75, worst, s1_b. Job B right after A
returns: s1 again. Refuses if fez not active or remaining - CAP < RESERVE."""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
from ffzne import build_qic, observable
from ffzne_fill import analyse
from sweep import service
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
CAP, RESERVE = 200, 300
L = json.load(open(os.path.join(HERE, 'layouts_chosen.json'))); SC = {k: L[k]['score'] for k in ('s1', 'mid', 'worst', 'q25', 'q75')}
s = service(); rem = s.usage().get('usage_remaining_seconds'); be = s.backend('ibm_fez'); st = be.status(); print('remaining', rem, 'fez', st.status_msg, st.pending_jobs, flush=True)
fire = '--fire' in sys.argv
if fire and (rem is None or rem - CAP < RESERVE or str(st.status_msg).lower() != 'active'): sys.exit('REFUSED')
qc, obs = build_qic(), observable()
def pub(lay):
    t = generate_preset_pass_manager(optimization_level=3, backend=be, initial_layout=L[lay]['layout'], seed_transpiler=42).run(qc)
    return (t, [obs.apply_layout(t.layout)]), dict(depth=t.depth(), cz=int(t.count_ops().get('cz', 0)), first_last=[L[lay]['layout'][0], L[lay]['layout'][-1]])
A = [('s1_a', 's1'), ('q25', 'q25'), ('mid', 'mid'), ('q75', 'q75'), ('worst', 'worst'), ('s1_b', 's1')]
built = [(k, *pub(l)) for k, l in A]; info = {k: m for k, _, m in built}; print(json.dumps(info), flush=True)
if not fire: open(os.path.join(HERE, 'dry_run_ffzne.text'), 'w').write(json.dumps(info, indent=1)); sys.exit(0)
from qiskit_ibm_runtime import EstimatorV2, EstimatorOptions
o = EstimatorOptions(); o.default_shots = 10000; o.resilience_level = 0; o.twirling.enable_gates = True; o.twirling.num_randomizations = 'auto'
o.resilience.measure_mitigation = True; o.dynamical_decoupling.enable = True; o.dynamical_decoupling.sequence_type = 'XY4'
json.dump(be.properties(refresh=True).to_dict(), open(os.path.join(HERE, 'props_before.json'), 'w'), default=str)
jA = EstimatorV2(mode=be, options=o).run([p for _, p, _ in built]); recA = dict(job_id=jA.job_id(), submitted=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), info=info); print('SUBMITTED A', recA['job_id'], recA['submitted'], flush=True)
rA = jA.result(); ev = {k: (float(r.data.evs[0]), float(r.data.stds[0])) for (k, _, _), r in zip(built, rA)}; recA['metrics'] = jA.metrics()
pB, _ = pub('s1'); jB = EstimatorV2(mode=be, options=o).run([pB]); recB = dict(job_id=jB.job_id(), submitted=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())); print('SUBMITTED B', recB['job_id'], recB['submitted'], flush=True)
r = jB.result()[0]; ev['s1_jobB'] = (float(r.data.evs[0]), float(r.data.stds[0])); recB['metrics'] = jB.metrics()
json.dump(dict(A=recA, B=recB), open(os.path.join(HERE, 'jobs_ffzne.json'), 'w'), default=str); json.dump(ev, open(os.path.join(HERE, 'raw_evs.json'), 'w'))
out = analyse(ev, SC); open(os.path.join(HERE, 'results_ffzne.text'), 'w').write(json.dumps(out, indent=1, default=float)); print(json.dumps(out, indent=1, default=float), flush=True)
