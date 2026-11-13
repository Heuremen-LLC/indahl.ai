"""fire_usp.py -- the free calibration run for arXiv 2609.33255 on ibm_kingston (Darkwave Disco via sweep_run/sweep.py service()).
Design (PLAN_USP.md.text, fixed before any job): their exact submitted circuits (20 non-mutant entries) for qubit sets A, B, C = 60 circuits, rebuilt by usp.parse_isa
(60/60 equal to their manifest's op count, depth and 2-qubit-arity count), sent UNCHANGED (transpile at level 0 with identity layout must leave them equal, else STOP).
Order: S_pre (our committed Part 0 sweep, sweep_run/fire_sweep_rep.py usp_pre) | G1 (60 circuits, seeded shuffle) | G2 (same circuits, reversed order) | S_post (sweep usp_post).
2048 shots per circuit. The backend record is saved before every G job. One restart then HOLD on an IBM-side ERROR.
Usage: fire_usp.py           dry run (build, check, estimate, remaining seconds; submits nothing)
       fire_usp.py --fire"""
import json, os, subprocess, sys, time, hashlib
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); SW = os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run')
sys.path.insert(0, HERE); sys.path.insert(0, SW)
import usp
from sweep import service
from qiskit import transpile, qpy
CHIP = 'ibm_kingston'; SHOTS = 2048; CAP = 160; ORDER_SEED = 20261024; PY = os.path.expanduser('~/bones-forge/qvenv/bin/python3')

def build():
    circs, meta = [], []
    for s in 'ABC':
        for lab, kind, b, case, exp, src in usp.entries(s):
            circs.append(usp.parse_isa(src)); meta.append(dict(set=s, label=lab, kind=kind, builder=b, case=case, expected=exp))
    return circs, meta

def counts_of(pr):
    r = getattr(pr.data, 'meas', None)
    if r is None: raise RuntimeError('no meas register')
    return {str(k): int(v) for k, v in r.get_counts().items()}

def sweep(tag, step):
    out = subprocess.run([PY, '-I', f'{SW}/fire_sweep_rep.py', tag, f'--{step}', CHIP], capture_output=True, text=True)
    lines = [l for l in (out.stdout + out.stderr).splitlines() if not any(w in l.lower() for w in ('token', 'crn', 'warning'))]
    print(f'  sweep {tag} {step}: ' + (lines[-1] if lines else '(no output)'), flush=True); return out.returncode

s = service(); b = s.backend(CHIP); circs, meta = build()
tq = transpile(circs, b, optimization_level=0, initial_layout=list(range(b.num_qubits)), seed_transpiler=7)
same = all(sum(a.count_ops().values()) == sum(c.count_ops().values()) and a.count_ops().get('cz', 0) == c.count_ops().get('cz', 0) for a, c in zip(circs, tq))
dur = np.array([c.estimate_duration(b.target, 's') for c in tq]); est = float(np.sum(SHOTS * (dur + 290e-6))) * 2
rem = s.usage().get('usage_remaining_seconds')
print(f'{CHIP}: {len(circs)} circuits (3 sets x 20), unchanged by level-0 transpile: {same}; G jobs ESTIMATED {est:.0f} s for both copies (+ 2 sweeps ~19 s each), cap {CAP}, remaining {rem}', flush=True)
if '--fire' not in sys.argv: sys.exit(0)
if not same: print('STOP: transpile changed their circuits'); sys.exit(1)
if est > CAP or (rem is not None and rem < est + 60): print('STOP: estimate over cap or not enough seconds'); sys.exit(1)
from qiskit_ibm_runtime import SamplerV2
qpy.dump(circs, open(f'{HERE}/circuits_usp.qpy', 'wb')); chash = hashlib.sha256(open(f'{HERE}/circuits_usp.qpy', 'rb').read()).hexdigest()
order1 = list(np.random.default_rng(ORDER_SEED).permutation(len(circs))); order2 = order1[::-1]
rec = dict(chip=CHIP, shots=SHOTS, circuit_hash=chash, order1=[int(i) for i in order1], meta=meta, jobs=[], sweeps=['usp_pre', 'usp_post'])
json.dump(rec, open(f'{HERE}/job_usp.json', 'w'), indent=1)
if sweep('usp_pre', 'fire') == 0: sweep('usp_pre', 'fetch')
for tag, order in (('G1', order1), ('G2', order2)):
    for attempt in (1, 2):
        json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_usp_before_{tag}_{attempt}.json', 'w'), default=str)
        job = SamplerV2(mode=b).run([tq[i] for i in order], shots=SHOTS); sub = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        print(f'SUBMITTED job {tag} attempt {attempt} {job.job_id()} {sub}', flush=True)
        try:
            res = job.result(); break
        except Exception as e:
            print(f'ERROR {tag} attempt {attempt}: {str(e)[:160]}', flush=True); rec['jobs'].append(dict(label=tag, attempt=attempt, job_id=job.job_id(), error=str(e)[:300]))
            json.dump(rec, open(f'{HERE}/job_usp.json', 'w'), indent=1)
            if attempt == 2: print('HOLD: second failure, run held'); sys.exit(2)
    rows = [dict(meta[i], counts=counts_of(pr)) for i, pr in zip(order, res)]
    json.dump(rows, open(f'{HERE}/raw_usp_{tag}.json', 'w'))
    m = job.metrics(); rec['jobs'].append(dict(label=tag, attempt=attempt, job_id=job.job_id(), submitted_utc=sub, usage=m.get('usage'), timestamps=m.get('timestamps')))
    json.dump(rec, open(f'{HERE}/job_usp.json', 'w'), indent=1, default=str)
    print(f'DONE job {tag} usage {(m.get("usage") or {}).get("qpu_charge_time_seconds")} s', flush=True)
if sweep('usp_post', 'fire') == 0: sweep('usp_post', 'fetch')
json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_usp_after.json', 'w'), default=str)
print('ALL DONE', flush=True)
