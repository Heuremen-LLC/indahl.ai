"""fire_res0.py -- the 98-115 s deciding run for arXiv 2608.04486v3 (Roy; Jadavpur / Presidency), ibm_kingston. Plan: PLAN_RES0.md.text.
Their question: does the hardware separate the label variance Var C2 = <C2^2> - <C2>^2 of the MIXED state (exact 240) from the SOLVABLE
state (exact 0)? Their resilience-2 run printed 236 +- 78 vs 36 +- 136 (difference 1.28 sigma). This run: same two states, same physical
qubits as their released record, same 4,000 shots per basis, resilience 0 (no TREX, no ZNE), EstimatorV2, one job.
--synth  : run the analysis on planted results (no IBM).   --fire : submit (refuses if remaining seconds < 400 or chip not up)."""
import sys, os, json, time, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import pds
from qiskit import QuantumCircuit
from qiskit.circuit.library import StatePreparation
from qiskit.quantum_info import SparsePauliOp, Operator, Statevector

SHOTS = 4000
LAYOUT = {'solvable': [73, 79, 72, 74], 'mixed': [148, 60, 47, 21]}   # from their kingston_device_N3.json
nq, Ce, ex = pds.exemplars(3)
A = SparsePauliOp.from_operator(Operator(Ce)).simplify()          # C2
B = SparsePauliOp.from_operator(Operator(Ce @ Ce)).simplify()     # C2^2
STATES = {'solvable': ex[1]['w'], 'mixed': ex[0]['w']}

def circuit(kind):
    qc = QuantumCircuit(nq)
    w = STATES[kind]
    if not np.allclose(np.abs(w), np.eye(2 ** nq)[0]): qc.append(StatePreparation(w), range(nq))
    return qc

def analyse(vals):
    """vals[kind] = dict(A=<C2>, sA, B=<C2^2>, sB). Var and its error propagated as independent, exactly as the paper's record says."""
    out = {}
    for k, v in vals.items():
        var = v['B'] - v['A'] ** 2; err = float(np.sqrt(v['sB'] ** 2 + 4 * v['A'] ** 2 * v['sA'] ** 2))
        out[k] = dict(C2=v['A'], C2_err=v['sA'], C2sq=v['B'], C2sq_err=v['sB'], VarC2=var, VarC2_err=err)
    d = out['mixed']['VarC2'] - out['solvable']['VarC2']; s = float(np.hypot(out['mixed']['VarC2_err'], out['solvable']['VarC2_err']))
    lo, hi = d - 1.96 * s, d + 1.96 * s
    # four outcomes for "mixed above solvable"; CANNOT_TELL if the 95% width is wider than the exact gap itself (240)
    oc = 'CANNOT_TELL' if 2 * 1.96 * s > 240 else ('ABOVE' if lo > 0 else 'BELOW' if hi < 0 else 'CONSISTENT')
    out['difference'] = dict(value=d, sigma=s, ci95=[lo, hi], z=d / s if s else None, outcome=oc,
                             exact=240.0, theirs_res2=dict(mixed='236 +- 78', solvable='36 +- 136', diff_sigma=1.28))
    return out

def synth():
    rng = np.random.default_rng(7); res = {}
    from qiskit.primitives import StatevectorEstimator
    est = StatevectorEstimator(default_precision=0.0)
    ideal = {k: [float(est.run([(circuit(k), [A, B])]).result()[0].data.evs[i]) for i in (0, 1)] for k in STATES}
    import cost  # noqa -- per-shot widths at 4,000 shots/basis come from cost_out.text
    co = json.load(open(os.path.join(HERE, 'cost_out.text')))
    def planted(name, shift):
        vals = {}
        for k, key in (('solvable', '1'), ('mixed', '0')):
            a, b = ideal[k]; per = co['states'][key]['per_shot']
            sA, sB = float(np.sqrt(per['VA'] / SHOTS)), float(np.sqrt(per['VB'] / SHOTS))
            if name == 'NULL (both states read as mixed)': a, b = ideal['mixed']
            vals[k] = dict(A=a + rng.normal(0, sA), sA=sA, B=b + rng.normal(0, sB) + shift.get(k, 0), sB=sB)
        return analyse(vals)
    res['IDEAL (exact states, shot noise only)'] = planted('ideal', {})
    res['NULL (both states read as mixed)'] = planted('NULL (both states read as mixed)', {})
    res['NOISY (device bias pulls solvable up by +200 in C2^2)'] = planted('noisy', {'solvable': 200.0})
    res['_ideal_expectations'] = ideal
    return res

if __name__ == '__main__':
    if '--synth' in sys.argv:
        r = synth(); open(os.path.join(HERE, 'synth_res0_results.text'), 'w').write(json.dumps(r, indent=1, default=float))
        for k, v in r.items():
            if not k.startswith('_'): print(k, '->', v['difference']['outcome'], 'diff %.1f +- %.1f' % (v['difference']['value'], v['difference']['sigma']))
        sys.exit(0)
    if '--fire' not in sys.argv: sys.exit('use --synth or --fire')
    sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
    from sweep import service
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from qiskit_ibm_runtime import EstimatorV2
    s = service(); b = s.backend('ibm_kingston'); st = b.status(); rem = s.usage().get('usage_remaining_seconds')
    print('kingston', st.operational, st.status_msg, st.pending_jobs, 'remaining', rem, flush=True)
    if not st.operational or str(st.status_msg).lower() != 'active': sys.exit('REFUSED: kingston not active')
    KUMAR_RESERVE, EST_MAX = 300, 115   # his order: always keep Kumar's marrakesh run (est 236 s, cap 280) funded
    if rem is None or rem - EST_MAX < KUMAR_RESERVE: sys.exit('REFUSED: remaining %s - est %d would leave < %d s reserved for Kumar' % (rem, EST_MAX, KUMAR_RESERVE))
    pubs, meta = [], []
    for kind in ('solvable', 'mixed'):
        pm = generate_preset_pass_manager(optimization_level=3, backend=b, initial_layout=LAYOUT[kind], seed_transpiler=11)
        isa = pm.run(circuit(kind)); ops = [o.apply_layout(isa.layout) for o in (A, B)]
        pubs.append((isa, ops)); meta.append(dict(kind=kind, layout=LAYOUT[kind], depth=isa.depth(), two_q=isa.num_nonlocal_gates()))
    print('compiled', meta, flush=True)
    json.dump(b.properties(refresh=True).to_dict(), open(os.path.join(HERE, 'props_before_res0.json'), 'w'), default=str)
    est = EstimatorV2(mode=b); est.options.default_shots = SHOTS; est.options.resilience_level = 0
    job = est.run(pubs); jid = job.job_id(); t0 = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    rec = dict(job_id=jid, submitted=t0, shots_per_basis=SHOTS, resilience=0, meta=meta)
    json.dump(rec, open(os.path.join(HERE, 'job_res0.json'), 'w'), default=str); print('SUBMITTED', jid, t0, flush=True)
    res = job.result()
    vals = {m['kind']: dict(A=float(r.data.evs[0]), sA=float(r.data.stds[0]), B=float(r.data.evs[1]), sB=float(r.data.stds[1])) for m, r in zip(meta, res)}
    m = job.metrics() or {}; rec.update(usage=m.get('usage'), timestamps=m.get('timestamps'), raw=vals)
    json.dump(rec, open(os.path.join(HERE, 'job_res0.json'), 'w'), default=str)
    json.dump(b.properties(refresh=True).to_dict(), open(os.path.join(HERE, 'props_after_res0.json'), 'w'), default=str)
    out = analyse(vals); open(os.path.join(HERE, 'results_res0.text'), 'w').write(json.dumps(out, indent=1, default=float))
    print(json.dumps(out['difference'], default=float), 'usage', m.get('usage'), flush=True)
