"""fire_ufsm_dd.py [--fire] -- ADDENDUM run (defined after run 1's data): the SAME transpiled circuits as run 1 copy 1 (circuits_ufsm.qpy,
first 8), same pair, two jobs back to back: J1 with dynamical decoupling ON (XY4), J2 with DD OFF. No twirling. One restart then HOLD."""
import json, sys, time, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
import ufsm
from sweep import service
from qiskit import qpy
s = service(); b = s.backend('ibm_kingston'); rem = s.usage().get('usage_remaining_seconds')
T = qpy.load(open(f'{HERE}/circuits_ufsm.qpy', 'rb'))[:8]; rec = json.load(open(f'{HERE}/job_ufsm.json'))
print(f'ibm_kingston pair {rec["pair"]}; 2 jobs x 8 circuits x {ufsm.SHOTS}; est 38 s; remaining {rem}')
if '--fire' not in sys.argv: print('DRY RUN'); sys.exit(0)
if rem is not None and rem < 70: print('STOP: seconds'); sys.exit(1)
from qiskit_ibm_runtime import SamplerV2
out = dict(pair=rec['pair'], jobs=[])
for tag, dd in (('ddon', True), ('ddoff', False)):
    json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_ufsm_before_{tag}.json', 'w'), default=str)
    for attempt in (1, 2):
        smp = SamplerV2(mode=b); smp.options.twirling.enable_gates = False; smp.options.twirling.enable_measure = False
        smp.options.dynamical_decoupling.enable = dd
        if dd: smp.options.dynamical_decoupling.sequence_type = 'XY4'
        job = smp.run(T, shots=ufsm.SHOTS); sub = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()); print('SUBMITTED', tag, job.job_id(), sub, flush=True)
        out['jobs'].append(dict(tag=tag, job_id=job.job_id(), submitted_utc=sub)); json.dump(out, open(f'{HERE}/job_ufsm_dd.json', 'w'), default=str)
        try:
            res = job.result(); break
        except Exception as e:
            print('IBM-side ERROR:', str(e)[:160], flush=True); out['jobs'][-1]['error'] = str(e)[:300]; json.dump(out, open(f'{HERE}/job_ufsm_dd.json', 'w'), default=str)
            if attempt == 2: print('HOLD'); sys.exit(2)
    ents = [[k, l, {str(kk): int(v) for kk, v in pr.data.c.get_counts().items()}] for (k, l), pr in zip(ufsm.plan(1), res)]
    json.dump(ents, open(f'{HERE}/raw_ufsm_{tag}.json', 'w'))
    m = job.metrics(); out['jobs'][-1].update(usage=m.get('usage'), timestamps=m.get('timestamps')); json.dump(out, open(f'{HERE}/job_ufsm_dd.json', 'w'), default=str)
print('ALL DONE', flush=True)
