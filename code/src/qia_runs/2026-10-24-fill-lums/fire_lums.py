"""fire_lums.py -- the free calibration run for arXiv 2609.13669 (LUMS) on ibm_fez, Darkwave Disco. Design fixed in PLAN_LUMS.md.text.
His first batched job (bps1: same parameter rows, same shots per row) for n = 8 (chain 124..147) and n = 10 (chain 107..120), both PUBs in
one job, his transpile (preset level 1, initial_layout = his chain, seed_transpiler 42), transpiled ONCE and sent unchanged in 12 jobs,
order T O O T T O O T T O O T (T = his settings: dynamical decoupling + gate and measurement twirling; O = dynamical decoupling only).
Each job submitted after the previous finishes; backend record and job state saved BEFORE every job. IBM-side ERROR: one restart of
that job, a second ERROR holds the run (HELD.md.text). Usage: fire_lums.py (dry run) | fire_lums.py --fire"""
import json, sys, os, time, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
import numpy as np, lums, circuits_lums as CL
from sweep import service
from qiskit import qpy
from qiskit.transpiler import generate_preset_pass_manager
CHIP = 'ibm_fez'; CAP = 320
s = service(); b = s.backend(CHIP); pubs = {}; rec = dict(chip=CHIP, order=lums.ORDER, sizes={}, jobs=[])
for n in (8, 10):
    d = lums.theirs(n); L = {j['tag']: j for j in d['ledger']['log']}; qc = CL.build(d)
    isa = generate_preset_pass_manager(optimization_level=1, backend=b, initial_layout=lums.CHAINS[n], seed_transpiler=42).run(qc)
    used = sorted({isa.find_bit(q).index for ins in isa.data for q in ins.qubits if ins.operation.name in ('cz', 'measure')})
    assert set(used) <= set(lums.CHAINS[n]), f'layout moved: {used}'
    n2q = sum(1 for ins in isa.data if ins.operation.name == 'cz'); d2q = isa.depth(lambda ins: ins.operation.name == 'cz')
    P = CL.bind_rows(isa, L['bps1']['params'], d['provenance']['p']); shots = L['bps1']['shots']
    pubs[n] = (isa, P, shots)
    rec['sizes'][n] = dict(chain=lums.CHAINS[n], rows=len(P), shots=shots, n2q=n2q, d2q=d2q, depth=isa.depth(),
                           his=dict(n2q=d['circuit']['n2q'], d2q=d['circuit']['depth2q'], depth=d['circuit']['depth']), his_pred_s=L['bps1']['qpu_predicted'])
est_job = sum(rec['sizes'][n]['his_pred_s'] for n in (8, 10)) - 3.0; est = est_job * len(lums.ORDER); rem = s.usage().get('usage_remaining_seconds')
for n in (8, 10): print(f'n={n}: {rec["sizes"][n]}')
print(f'{CHIP}: 12 jobs x 2 PUBs, est {est_job:.1f} s/job (his predicted metering), total {est:.0f} s (cap {CAP}), remaining {rem}', flush=True)
if '--fire' not in sys.argv: sys.exit(0)
if est > CAP or (rem is not None and rem < est + 60): print('STOP: estimate over cap or not enough seconds'); sys.exit(1)
qpy.dump([pubs[8][0], pubs[10][0]], open(f'{HERE}/circuits_lums.qpy', 'wb')); rec['circuit_hash'] = hashlib.sha256(open(f'{HERE}/circuits_lums.qpy', 'rb').read()).hexdigest()
from qiskit_ibm_runtime import SamplerV2
from qiskit_ibm_runtime.exceptions import RuntimeJobFailureError
spent = 0.0
for k, arm in enumerate(lums.ORDER):
    label = f'J{k+1:02d}{arm}'; tries = 0
    while True:
        json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_lums_before_{label}{"_retry" if tries else ""}.json', 'w'), default=str)
        json.dump(dict(rec, next=label), open(f'{HERE}/job_lums.json', 'w'), default=str)
        sm = SamplerV2(mode=b); sm.options.dynamical_decoupling.enable = True
        sm.options.twirling.enable_gates = arm == 'T'; sm.options.twirling.enable_measure = arm == 'T'
        job = sm.run([pubs[8], pubs[10]]); sub = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        print(f'SUBMITTED {label} {job.job_id()} {sub}', flush=True)
        try:
            res = job.result(); break
        except RuntimeJobFailureError as e:
            m = job.metrics(); rec['jobs'].append(dict(label=label, job_id=job.job_id(), submitted_utc=sub, status='ERROR', error=str(e)[:200], usage=m.get('usage')))
            json.dump(rec, open(f'{HERE}/job_lums.json', 'w'), default=str)
            if tries: open(f'{HERE}/HELD.md.text', 'w').write(f'HELD: {label} failed twice on IBM side ({str(e)[:160]}). Not refired.\n'); print('HELD', flush=True); sys.exit(2)
            tries += 1; print(f'ERROR {label}; one restart', flush=True)
    raw = {}
    for n, pr in zip((8, 10), res):
        raw[n] = [{str(i): int(c) for i, c in pr.data.c[r].get_int_counts().items()} for r in range(len(pubs[n][1]))]
    json.dump(raw, open(f'{HERE}/raw_lums_{label}.json', 'w'))
    m = job.metrics(); u = (m.get('usage') or {}).get('quantum_seconds') or (m.get('usage') or {}).get('seconds') or est_job; spent += float(u)
    rec['jobs'].append(dict(label=label, arm=arm, job_id=job.job_id(), submitted_utc=sub, usage=m.get('usage'), timestamps=m.get('timestamps')))
    json.dump(rec, open(f'{HERE}/job_lums.json', 'w'), default=str); print(f'DONE {label} usage {u} s (total {spent:.0f})', flush=True)
    if spent > CAP: print('STOP: cap reached'); break
json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_lums_after.json', 'w'), default=str); print('ALL DONE', round(spent), 's', flush=True)
