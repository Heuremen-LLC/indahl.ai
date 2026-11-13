"""fire_aqcel.py [--dry | --fire] -- one job on ibm_fez (Darkwave Disco via sweep_run/sweep.py service()).
--dry : save the record, build the arms (arms.py, seed 11, optimization_level 3), freeze them to circuits_aqcel.qpy + meta_aqcel.json,
        write synth_inputs_aqcel.json and dry_run_aqcel.text. Nothing submitted.
--fire: load the FROZEN circuits (sha256 must equal meta), check usage_remaining_seconds >= 600 and estimate <= CAP, save the record
        just before the job, submit ONE SamplerV2 job (24 pubs, plan order), twirling off (gates and measure), dynamical decoupling off,
        rep_delay = backend default (paper: 0.0005 s; stated difference), no other options. One restart on an IBM-side ERROR, then HOLD.
        Saves raw_aqcel.json, job_aqcel.json (ids, times, usage), record after."""
import json, sys, time, hashlib, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
import arms, aqcel_rebuild as A
from sweep import service
from qiskit import qpy
CHIP = 'ibm_fez'; CAP = 60; MIN_REMAIN = 600; SEC_PER_SHOT = 0.30e-3; OVERHEAD = 3


def sha(f):
    return hashlib.sha256(open(f, 'rb').read()).hexdigest()


s = service(); b = s.backend(CHIP); rem = s.usage().get('usage_remaining_seconds')
if '--dry' in sys.argv:
    json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_aqcel_dry.json', 'w'), default=str)
    B = arms.build(b)
    qpy.dump(B['circs'], open(f'{HERE}/circuits_aqcel.qpy', 'wb'))
    p = A.ideal_dist(B['logical']['Q'])
    dctrl = arms.noiseless_isa_dist(B['isa']['CTRL'], B['meas']['CTRL'])
    noiseless = {k: A.hellinger_fidelity(p, arms.noiseless_isa_dist(B['isa'][k], B['meas'][k])) for k in arms.ARMS}
    cz = {k: B['isa'][k].count_ops().get('cz', 0) for k in arms.ARMS}
    meta = dict(chip=CHIP, seed=arms.SEED, thr=arms.THR, plan=B['plan'], shots=B['shots'], meas=B['meas'], union=B['union'], cz=cz,
                depth={k: B['isa'][k].depth() for k in arms.ARMS}, noiseless_F=noiseless, p=p, circuits_sha256=sha(f'{HERE}/circuits_aqcel.qpy'))
    json.dump(meta, open(f'{HERE}/meta_aqcel.json', 'w'), indent=1)
    json.dump(dict(meas=B['meas'], union=B['union'], p=p, d_ctrl=dctrl), open(f'{HERE}/synth_inputs_aqcel.json', 'w'), indent=1)
    est = sum(B['shots']) * SEC_PER_SHOT + OVERHEAD
    txt = (f'{CHIP} dry run {time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}: CZ {cz}; depth {meta["depth"]}; measured {B["meas"]}; '
           f'noiseless F vs ideal {({k: round(v, 4) for k, v in noiseless.items()})}; {len(B["circs"])} pubs, {sum(B["shots"])} shots; '
           f'est {est:.0f} s (cap {CAP}); remaining {rem}; circuits sha256 {meta["circuits_sha256"]}\nDRY RUN, nothing submitted\n')
    open(f'{HERE}/dry_run_aqcel.text', 'w').write(txt); print(txt); sys.exit(0)

if '--fire' not in sys.argv:
    print('use --dry or --fire'); sys.exit(1)
meta = json.load(open(f'{HERE}/meta_aqcel.json'))
assert sha(f'{HERE}/circuits_aqcel.qpy') == meta['circuits_sha256'], 'frozen circuits changed'
circs = qpy.load(open(f'{HERE}/circuits_aqcel.qpy', 'rb'))
est = sum(meta['shots']) * SEC_PER_SHOT + OVERHEAD
print(f'{CHIP}: {len(circs)} pubs, {sum(meta["shots"])} shots, est {est:.0f} s (cap {CAP}), remaining {rem}', flush=True)
if est > CAP or rem is None or rem < MIN_REMAIN:
    print('STOP: cap or seconds'); sys.exit(1)
from qiskit_ibm_runtime import SamplerV2
rec = dict(chip=CHIP, circuits_sha256=meta['circuits_sha256'], options=dict(twirling_gates=False, twirling_measure=False, dd=False,
           rep_delay='backend default'), jobs=[])
for attempt in (1, 2):
    json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_aqcel_before_{attempt}.json', 'w'), default=str)
    smp = SamplerV2(mode=b)
    smp.options.twirling.enable_gates = False; smp.options.twirling.enable_measure = False; smp.options.dynamical_decoupling.enable = False
    pubs = [(c, None, n) for c, n in zip(circs, meta['shots'])]
    job = smp.run(pubs); sub = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()); print('SUBMITTED', job.job_id(), sub, flush=True)
    rec['jobs'].append(dict(job_id=job.job_id(), submitted_utc=sub)); json.dump(rec, open(f'{HERE}/job_aqcel.json', 'w'), indent=1, default=str)
    try:
        res = job.result(); break
    except Exception as e:
        print('IBM-side ERROR:', str(e)[:160], flush=True); rec['jobs'][-1]['error'] = str(e)[:300]
        json.dump(rec, open(f'{HERE}/job_aqcel.json', 'w'), indent=1, default=str)
        if attempt == 2:
            print('HOLD after second failure'); sys.exit(2)
ents = []
for (lab, r), pr in zip(meta['plan'], res):
    reg = pr.data.c if hasattr(pr.data, 'c') else getattr(pr.data, list(pr.data.keys())[0])
    ents.append([lab, r, {str(k): int(v) for k, v in reg.get_counts().items()}])
json.dump(ents, open(f'{HERE}/raw_aqcel.json', 'w'))
m = job.metrics(); rec['jobs'][-1].update(usage=m.get('usage'), timestamps=m.get('timestamps'))
json.dump(rec, open(f'{HERE}/job_aqcel.json', 'w'), indent=1, default=str)
json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_aqcel_after.json', 'w'), default=str)
print('DONE usage', m.get('usage'), flush=True)
