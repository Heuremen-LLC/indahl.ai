"""fire_kyiv_ext.py (ADDENDUM 2) -- jobs 5 (H2) and 6 (H0) after jobs 1-4, same transpiled circuits, so jobs 3-6 are H0 H2 H2 H0 (ABBA).
fire_kyiv.py -- the free calibration run for arXiv:2607.20377 on ibm_fez (Darkwave Disco, via sweep_run/sweep.py's service()).
Design (fixed before any job, PLAN_KYIV.md.text): the author's 300 public H0 circuits (identical to H2), transpiled ONCE
(optimization_level=1, seed_transpiler=24, as their pipeline's level) and sent unchanged in four jobs in the order H0, H2, H0, H2,
1024 shots each, their runtime options per regime (H2: gate twirling, active-accum, measure twirling off). Each job is submitted
after the previous finishes; the backend record (properties) is saved before every job and after the last. Layout saved.
Usage: fire_kyiv.py            (dry run: prints layout, estimate, remaining seconds)
       fire_kyiv.py --fire"""
import json, sys, time, csv
sys.path.insert(0, __import__('os').path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
from sweep import service
from qiskit import qpy, transpile
HERE = __file__.rsplit('/', 1)[0] or '.'; CHIP = 'ibm_fez'; SHOTS = 1024; ORDER = ['H2', 'H0']; FIRST = 5; EST_PER_JOB = 84
OPTS = json.load(open(f'{HERE}/theirs/zz4_wave1_runtime_options.json'))['regimes']
cs = qpy.load(open(f'{HERE}/theirs/zz4_wave1_circuits.qpy', 'rb')); idx = list(csv.DictReader(open(f'{HERE}/theirs/zz4_wave1_circuit_index.csv')))
H0 = [(r, c) for r, c in zip(idx, cs) if r['regime'] == 'H0']; assert len(H0) == 300
s = service(); b = s.backend(CHIP)
tq = transpile([c for _, c in H0], b, optimization_level=1, seed_transpiler=24)
lay = sorted({tuple(t.layout.final_index_layout()) for t in tq}); rem = s.usage().get('usage_remaining_seconds')
print(f'{CHIP}: 300 circuits, layouts {lay[:3]}{"..." if len(lay) > 3 else ""} ({len(lay)} distinct), est {EST_PER_JOB * 2} s, remaining {rem}', flush=True)
if '--fire' not in sys.argv: sys.exit(0)
if rem is not None and rem < EST_PER_JOB * 2 + 30: print('STOP: not enough seconds'); sys.exit(1)
from qiskit_ibm_runtime import SamplerV2
rec = json.load(open(f'{HERE}/job_kyiv.json')); assert len(rec['jobs']) == 4 and [list(l) for l in lay] == rec['layouts'], 'STOP: first four jobs not done or layout changed'
def opts(reg):
    o = OPTS[reg]['sampler_options']; d = {'dynamical_decoupling': {'enable': False}, 'twirling': dict(o['twirling'])}
    for k in ('num_randomizations', 'shots_per_randomization'):
        if d['twirling'].get(k) == 'auto': d['twirling'][k] = 'auto'
    return d
for k, reg in enumerate(ORDER, FIRST):
    json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_kyiv_before_{k}.json', 'w'), default=str)
    smp = SamplerV2(mode=b, options=opts(reg)); job = smp.run([(t, None, SHOTS) for t in tq])
    sub = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()); print(f'SUBMITTED job {k} {reg} {job.job_id()} {sub}', flush=True)
    res = job.result(); ents = []
    for (r, _), pr in zip(H0, res):
        ents.append(dict(counts=pr.data.meas.get_counts(), shots_observed=SHOTS, metadata=dict(circuit_metadata=dict(i=int(r['i']), j=int(r['j'])))))
    json.dump(ents, open(f'{HERE}/raw_kyiv_{k}.json', 'w'))
    m = job.metrics(); rec['jobs'].append(dict(label=str(k), regime=reg, job_id=job.job_id(), submitted_utc=sub, usage=m.get('usage'), timestamps=m.get('timestamps')))
    json.dump(rec, open(f'{HERE}/job_kyiv.json', 'w'), default=str)
    print(f'DONE job {k} {reg} usage {m.get("usage")}', flush=True)
json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_kyiv_after_ext.json', 'w'), default=str)
print('ALL DONE', flush=True)
