"""fire_vqc.py --dry | --fire : job A on ibm_fez = 5 PUBs (theirs_a, best, q50, q75, theirs_b), each one opt-3 parameterised ISA circuit with the
84 test rows bound (their method), 1,024 shots; job B right after A returns = theirs_jobB. 'theirs' = initial_layout [144, 143, 142, 141] (their
recorded placement). Refuses if fez not active or remaining - CAP < RESERVE."""
import sys, os, json, time, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
from vqc import features, p_exact, W, SHOTS
from vqc_fill import analyse
from sweep import service
from qiskit.circuit.library import z_feature_map, real_amplitudes
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
CAP, RESERVE = 220, 300
L = json.load(open(os.path.join(HERE, 'layouts_chosen.json'))); LAY = {'theirs': [144, 143, 142, 141], 'best': L['best']['layout'], 'q50': L['q50']['layout'], 'q75': L['q75']['layout']}
Q, y = features(); pe = np.array([p_exact(x) for x in Q])
s = service(); rem = s.usage().get('usage_remaining_seconds'); be = s.backend('ibm_fez'); st = be.status(); print('remaining', rem, 'fez', st.status_msg, st.pending_jobs, flush=True)
fire = '--fire' in sys.argv
if fire and (rem is None or rem - CAP < RESERVE or str(st.status_msg).lower() != 'active'): sys.exit('REFUSED')
fm, an = z_feature_map(4, reps=1), real_amplitudes(4, reps=3, entanglement='linear'); circ = fm.compose(an); circ.measure_all()
def pub(lay):
    isa = generate_preset_pass_manager(optimization_level=3, backend=be, initial_layout=LAY[lay], seed_transpiler=42).run(circ)
    fi = {p: i for i, p in enumerate(fm.parameters)}; ai = {p: i for i, p in enumerate(an.parameters)}
    vals = np.column_stack([Q[:, fi[p]] if p in fi else np.full(len(Q), W[ai[p]]) for p in isa.parameters])
    meas = [isa.find_bit(i.qubits[0]).index for i in isa.data if i.operation.name == 'measure']
    return (isa, vals), dict(depth=isa.depth(), cz=int(isa.count_ops().get('cz', 0)), measured=meas)
A = [('theirs_a', 'theirs'), ('best', 'best'), ('q50', 'q50'), ('q75', 'q75'), ('theirs_b', 'theirs')]
built = [(k, *pub(l)) for k, l in A]; info = {k: m for k, _, m in built}; print(json.dumps(info), flush=True)
if not fire: open(os.path.join(HERE, 'dry_run_vqc.text'), 'w').write(json.dumps(info, indent=1)); sys.exit(0)
from qiskit_ibm_runtime import SamplerV2
json.dump(be.properties(refresh=True).to_dict(), open(os.path.join(HERE, 'props_before.json'), 'w'), default=str)
def counts(r):
    b = r.data.meas; return [{format(k, '04b'): int(v) for k, v in b.get_int_counts(i).items()} for i in range(len(Q))]
jA = SamplerV2(mode=be).run([p for _, p, _ in built], shots=SHOTS); recA = dict(job_id=jA.job_id(), submitted=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), info=info); print('SUBMITTED A', recA['job_id'], recA['submitted'], flush=True)
rA = jA.result(); raw = {k: counts(r) for (k, _, _), r in zip(built, rA)}; recA['metrics'] = jA.metrics()
pB, mB = pub('theirs'); jB = SamplerV2(mode=be).run([pB], shots=SHOTS); recB = dict(job_id=jB.job_id(), submitted=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), info=mB); print('SUBMITTED B', recB['job_id'], recB['submitted'], flush=True)
raw['theirs_jobB'] = counts(jB.result()[0]); recB['metrics'] = jB.metrics()
json.dump(dict(A=recA, B=recB), open(os.path.join(HERE, 'jobs_vqc.json'), 'w'), default=str); json.dump(raw, open(os.path.join(HERE, 'raw_counts.json'), 'w'))
out = analyse(raw, pe, y); open(os.path.join(HERE, 'results_vqc.text'), 'w').write(json.dumps(out, indent=1, default=float)); print(json.dumps(out, indent=1, default=float), flush=True)
