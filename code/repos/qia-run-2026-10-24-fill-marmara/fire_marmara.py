"""fire_marmara.py [--fire] -- four jobs on ibm_fez (Darkwave Disco via sweep_run/sweep.py service()): J1 DD OFF, J2 DD ON (XY4), J3 DD ON,
J4 DD OFF; each = 2 bracket + 64 messages (J2, J4 in reversed message order) + 2 bracket, 1024 shots. Physical qubits 0..5 (THEIR layout
for every n=6 message). Transpile once per job, optimization_level 3, initial_layout [0..5], seed_transpiler 7 (their fan-out + barrier: 17 CZ
per message). Record saved before every job and after. One restart per job on an IBM-side ERROR, then HOLD."""
import json, sys, time, hashlib, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
import marmara as M
from sweep import service
from qiskit import transpile, qpy
CHIP = 'ibm_fez'; CAP = 100
s = service(); b = s.backend(CHIP); rem = s.usage().get('usage_remaining_seconds')
T = {j: transpile(M.circuits(j), b, optimization_level=3, initial_layout=list(range(6)), seed_transpiler=7) for j, _ in M.JOBS}
cz = sorted({t.count_ops().get('cz', 0) for j in T for (k, l), t in zip(M.plan(j), T[j]) if k == 'm'})
used = sorted({t.find_bit(q).index for j in T for t in T[j] for ins in t.data for q in ins.qubits})
qpy.dump([t for j, _ in M.JOBS for t in T[j]], open(f'{HERE}/circuits_marmara.qpy', 'wb')); ch = hashlib.sha256(open(f'{HERE}/circuits_marmara.qpy', 'rb').read()).hexdigest()
est = 4 * 68 * M.SHOTS * 300e-6
print(f'{CHIP}: qubits used {used}; CZ per message {cz}; 4 jobs x 68 circuits x {M.SHOTS}; est {est:.0f} s (cap {CAP}); remaining {rem}')
if '--fire' not in sys.argv: print('DRY RUN, nothing submitted'); sys.exit(0)
if est > CAP or (rem is not None and rem < est + 30) or used != list(range(6)): print('STOP: cap, seconds or layout'); sys.exit(1)
from qiskit_ibm_runtime import SamplerV2
rec = dict(chip=CHIP, qubits=list(range(6)), circuits_sha256=ch, shots=M.SHOTS, cz_per_message=cz, jobs=[])
for j, dd in M.JOBS:
    json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_marmara_before_{j}.json', 'w'), default=str)
    for attempt in (1, 2):
        smp = SamplerV2(mode=b); smp.options.twirling.enable_gates = False; smp.options.twirling.enable_measure = False
        smp.options.dynamical_decoupling.enable = (dd == 'on')
        if dd == 'on': smp.options.dynamical_decoupling.sequence_type = 'XY4'
        job = smp.run(T[j], shots=M.SHOTS); sub = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()); print('SUBMITTED', j, dd, job.job_id(), sub, flush=True)
        rec['jobs'].append(dict(job=j, dd=dd, job_id=job.job_id(), submitted_utc=sub)); json.dump(rec, open(f'{HERE}/job_marmara.json', 'w'), default=str)
        try:
            res = job.result(); break
        except Exception as e:
            print('IBM-side ERROR:', str(e)[:160], flush=True); rec['jobs'][-1]['error'] = str(e)[:300]; json.dump(rec, open(f'{HERE}/job_marmara.json', 'w'), default=str)
            if attempt == 2: print('HOLD after second failure'); sys.exit(2)
    ents = [[k, l, {str(kk): int(v) for kk, v in pr.data.c.get_counts().items()}] for (k, l), pr in zip(M.plan(j), res)]
    json.dump(ents, open(f'{HERE}/raw_marmara_{j}.json', 'w'))
    m = job.metrics(); rec['jobs'][-1].update(usage=m.get('usage'), timestamps=m.get('timestamps')); json.dump(rec, open(f'{HERE}/job_marmara.json', 'w'), default=str)
json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_marmara_after.json', 'w'), default=str); print('ALL DONE', flush=True)
