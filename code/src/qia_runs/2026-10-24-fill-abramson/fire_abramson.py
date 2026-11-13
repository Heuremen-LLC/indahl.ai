"""fire_abramson.py -- the free calibration run for Nadav Abramson's raw-readout experiment (full paper l.1026-1034, l.487) on ibm_kingston
(Darkwave Disco, via sweep_run/sweep.py's service()).  His confound: arm A (ibm_kingston-2026-10-14-exp3-1: H, wait, H, readout and reset) ran 18:22:12Z,
arm B (exp3-2: A plus two CZs with each usual partner) 8 min 10 s later, "leaving temporal drift confounded with the change."
Design (fixed before any job, PLAN_ABRAMSON.md.text): his exp3-1 and exp3-2 circuits loaded from circuits.qpy.gz AS DATA, unchanged (same ten measured qubits
51 53 55 69 71 73 75 89 91 93), 1000 shots per item, kerneled raw IQ through the Executor as he sent them (init_qubits, rep_delay 250 us, scheduler_timing),
four jobs back to back in the order A1 B1 B2 A2.  Before every job: remaining seconds checked, backend record (properties) and the planned job saved.
Usage: fire_abramson.py            (dry run: prints the layout, estimate and remaining seconds; submits NOTHING)
       fire_abramson.py --fire     (submits; needs his word)"""
import json, sys, time, hashlib, gzip, os
sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
from sweep import service
from qiskit import qpy
HERE = os.path.dirname(os.path.abspath(__file__)); CHIP = 'ibm_kingston'; SHOTS = 1000; CAP = 120; MAXEXEC = 12; REP_DELAY = 250e-6
PLAN = [('A1', 'exp3-1', 4), ('B1', 'exp3-2', 4), ('B2', 'exp3-2', 4), ('A2', 'exp3-1', 4)]     # (label, his job, logged QPU s per job of his: 4 each)
EST = sum(p[2] for p in PLAN)
def his(j): return f'{HERE}/theirs/ibm_kingston-2026-10-14-{j}'
def load(j):
    raw = open(his(j) + '/circuits.qpy.gz', 'rb').read(); return qpy.load(gzip.open(his(j) + '/circuits.qpy.gz', 'rb')), hashlib.sha256(raw).hexdigest()
def measured(c):
    return [c.find_bit(i.qubits[0]).index for i in sorted((i for i in c.data if i.operation.name == 'measure'), key=lambda i: c.find_bit(i.clbits[0]).index)][:10]
def program(cs):
    from qiskit_ibm_runtime import QuantumProgram
    from qiskit_ibm_runtime.options_models import ExecutorOptions
    p = QuantumProgram(shots=SHOTS, meas_level='kerneled')
    for c in cs: p.append_circuit_item(c)
    o = ExecutorOptions(); o.execution.init_qubits = True; o.execution.rep_delay = REP_DELAY; o.execution.scheduler_timing = True
    return p, o
if __name__ == '__main__':
    s = service(); b = s.backend(CHIP); cA, hA = load('exp3-1'); cB, hB = load('exp3-2'); rem = s.usage().get('usage_remaining_seconds')
    qa, qb = measured(cA[2]), measured(cB[2]); assert qa == qb, (qa, qb)
    from qiskit_ibm_runtime.quantum_program.params_converters import QUANTUM_PROGRAM_PARAMS_CONVERTERS as CV
    enc = {k: len(str(CV['v2.0'].encoder(*program(c)).model_dump(mode='json'))) for k, c in (('A', cA), ('B', cB))}
    st = b.status()
    print(f'{CHIP}: operational {st.operational}, pending {st.pending_jobs}; his exp3-1 (arm A, {len(cA)} items, cz {cA[2].count_ops().get("cz", 0)}) and exp3-2 (arm B, {len(cB)} items, cz {cB[2].count_ops().get("cz", 0)}) '
          f'loaded unchanged (sha256 {hA[:12]}, {hB[:12]}), same ten measured qubits {qa}, kerneled raw IQ via Executor (payload encodes offline: {enc}), {SHOTS} shots/item, '
          f'4 jobs A1 B1 B2 A2, est {EST} s (cap {CAP}), remaining {rem}  -- DRY RUN, nothing submitted' if '--fire' not in sys.argv else f'{CHIP}: FIRING, est {EST} s, cap {CAP}, remaining {rem}', flush=True)
    if '--fire' not in sys.argv: sys.exit(0)
    from qiskit_ibm_runtime import Executor
    import numpy as np
    rec = dict(chip=CHIP, shots=SHOTS, his_circuit_sha256=dict(A=hA, B=hB), measured_qubits=qa, planned=[p[0] for p in PLAN], jobs=[]); spent = 0
    for label, hj, est in PLAN:
        rem = s.usage().get('usage_remaining_seconds')                                  # remaining seconds checked before EVERY job
        if spent + est > CAP: print(f'STOP: {spent} s spent + {est} s next > cap {CAP}'); break
        if rem is not None and rem < est + 30: print(f'STOP: remaining {rem} s < {est} + 30'); break
        json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_abramson_before_{label}.json', 'w'), default=str)   # record BEFORE the job
        json.dump(dict(rec, next=label, remaining_before=rem), open(f'{HERE}/job_abramson.json', 'w'), default=str)
        p, o = program(cA if hj == 'exp3-1' else cB); o.environment.max_execution_time = MAXEXEC; o.environment.job_tags = ['abramson-abba', label]
        job = Executor(mode=b, options=o).run(p); sub = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        print(f'SUBMITTED job {label} {job.job_id()} {sub} (remaining before {rem})', flush=True)
        res = job.result(); arrays = {}
        for k, out in enumerate(res):
            for name, v in dict(out).items(): arrays[f'{k}/{name}'] = np.asarray(v)
        np.savez_compressed(f'{HERE}/raw_abramson_{label}.npz', **arrays)
        m = job.metrics(); u = (m.get('usage') or {}).get('quantum_seconds') or (m.get('usage') or {}).get('qpu_charge_time_seconds') or est; spent += u
        rec['jobs'].append(dict(label=label, his_job=hj, job_id=job.job_id(), submitted_utc=sub, usage=m.get('usage'), timestamps=m.get('timestamps')))
        json.dump(rec, open(f'{HERE}/job_abramson.json', 'w'), default=str); print(f'DONE job {label} usage {u} s (total {spent})', flush=True)
    json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_abramson_after.json', 'w'), default=str)
    print('ALL DONE', spent, 's -- now run analyze_abramson.py', flush=True)
