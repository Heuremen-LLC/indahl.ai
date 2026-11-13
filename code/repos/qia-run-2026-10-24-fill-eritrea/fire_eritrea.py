"""fire_eritrea.py -- the free calibration run for the Eritrea Institute of Technology teleportation benchmark on ibm_fez (Darkwave Disco, via sweep_run/sweep.py's service()).
Design (fixed before any job, PLAN_ERITREA.md.text): their full-protocol dynamic teleportation circuit, 4 angles x X/Y/Z = 12 circuits (eritrea.tele_circuit, rebuilt from their circuits/full_protocol.qasm, their code not run),
8,192 shots, physical qubits [0,1,2], optimization_level 1 as theirs, plus 4 Ramsey circuits on the feedforward neighbour (eritrea.ram_circuit, 4,900 shots), transpiled ONCE (seed_transpiler 42) and sent unchanged in four jobs, order ABBA:
  A1 (A order: 12 teleportation circuits then 4 Ramsey) | B1 (reversed) | B2 (reversed) | A2 (A order)
Each job is submitted after the previous finishes; the backend record (properties), the remaining seconds and the planned job are saved BEFORE every job. Layout and compiled durations saved.
Usage: fire_eritrea.py            (dry run: transpiles, prints layout, estimate, remaining seconds; submits nothing)
       fire_eritrea.py --fire"""
import json, sys, time, hashlib, os
sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sweep import service
import eritrea as E
from qiskit import transpile, qpy
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
HERE = os.path.dirname(os.path.abspath(__file__)); CHIP = 'ibm_fez'; CAP = 200; MAXEXEC = 50; LAYOUT = [0, 1, 2]; SEED = 42
REP_US = 300                                                 # repetition time used in RUN_CANDIDATES_3 and the audit estimate
PLAN = [('A1', E.A_ORDER), ('B1', E.B_ORDER), ('B2', E.B_ORDER), ('A2', E.A_ORDER)]
shots_of = lambda cid: E.SHOTS_T if cid.startswith('tele') else E.SHOTS_R
JOB_EST = sum(shots_of(c) for c in E.A_ORDER) * REP_US * 1e-6          # QPU seconds per job at 300 us per shot (estimate; dynamic-circuit shots may cost more)
EST = 4 * JOB_EST
def two_q(t): return sum(v for k, v in t.count_ops().items() if k in ('cz', 'ecr', 'cx'))
if __name__ == '__main__':
    s = service(); b = s.backend(CHIP); rem = s.usage().get('usage_remaining_seconds')
    qd = max(b.target['measure'][(q,)].duration for q in (0, 1))                       # stated measure duration, s
    delay_dt = int(round(qd / b.dt / 16)) * 16
    pm = generate_preset_pass_manager(optimization_level=1, backend=b, initial_layout=LAYOUT, seed_transpiler=SEED)
    tq = {c: pm.run(E.circuit_for(c, delay_dt)) for c in E.A_ORDER}
    info = {c: dict(depth=t.depth(), two_q=two_q(t), ops={k: int(v) for k, v in t.count_ops().items()}, shots=shots_of(c)) for c, t in tq.items()}
    print(f'{CHIP}: 12 teleportation circuits (4 angles x X/Y/Z, {E.SHOTS_T} shots) + 4 Ramsey circuits ({E.SHOTS_R} shots), 4 jobs A1 B1 B2 A2, physical qubits {LAYOUT}, '
          f'est {EST:.1f} s ({JOB_EST:.1f} s per job at {REP_US} us/shot; cap {CAP}), remaining {rem}; Ramsey idle = measure duration {qd * 1e9:.0f} ns = {delay_dt} dt', flush=True)
    for c in E.A_ORDER: print('  ', c, info[c])
    if '--fire' not in sys.argv: sys.exit(0)
    from qiskit_ibm_runtime import SamplerV2
    qpy.dump([tq[c] for c in E.A_ORDER], open(f'{HERE}/circuits_eritrea.qpy', 'wb')); chash = hashlib.sha256(open(f'{HERE}/circuits_eritrea.qpy', 'rb').read()).hexdigest()
    rec = dict(chip=CHIP, layout=LAYOUT, circuits=info, circuit_order_in_qpy=E.A_ORDER, circuit_hash=chash, delay_dt=delay_dt, planned=[p[0] for p in PLAN], jobs=[]); spent = 0.0; last = JOB_EST
    for label, order in PLAN:
        rem = s.usage().get('usage_remaining_seconds'); est = max(JOB_EST, last)                  # next job estimated at the larger of the plan and the last actual
        if spent + est > CAP: print(f'STOP: {spent} s spent + {est:.1f} s next > cap {CAP}'); break
        if rem is not None and rem < est + 30: print(f'STOP: remaining {rem} s < {est:.1f} + 30'); break
        json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_eritrea_before_{label}.json', 'w'), default=str)
        json.dump(dict(rec, next=label, remaining_before=rem), open(f'{HERE}/job_eritrea.json', 'w'), default=str)
        smp = SamplerV2(mode=b); smp.options.max_execution_time = MAXEXEC
        job = smp.run([(tq[c], None, shots_of(c)) for c in order])
        sub = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()); print(f'SUBMITTED job {label} {job.job_id()} {sub} (remaining before {rem})', flush=True)
        res = job.result(); raw = {c: {str(k): int(v) for k, v in pr.data.c2.get_counts().items()} for c, pr in zip(order, res)}
        json.dump(raw, open(f'{HERE}/raw_eritrea_{label}.json', 'w'))
        m = job.metrics(); u = (m.get('usage') or {}).get('quantum_seconds') or (m.get('usage') or {}).get('qpu_charge_time_seconds') or est; spent += u; last = u
        rec['jobs'].append(dict(label=label, order=order, job_id=job.job_id(), submitted_utc=sub, usage=m.get('usage'), timestamps=m.get('timestamps')))
        json.dump(rec, open(f'{HERE}/job_eritrea.json', 'w'), default=str)
        print(f'DONE job {label} usage {u} s (total {spent})', flush=True)
    json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_eritrea_after.json', 'w'), default=str)
    print('ALL DONE', spent, 's', flush=True)
