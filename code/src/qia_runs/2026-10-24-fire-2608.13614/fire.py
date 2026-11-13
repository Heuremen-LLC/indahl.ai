"""fire.py -- the 2608.13614 free run on ibm_kingston (Darkwave Disco via sweep_run/sweep.py service()).
Two circuits (variant P = paper construction lambda 8, variant S = released script lambda 2.0), each the final p=4 QAOA circuit rebuilt by
MY sis_qubo.py with MY angles (known_good.json), transpiled ONCE (preset optimization_level 3 as the released script, seed_transpiler 2608),
ONE SamplerV2 job with both PUBs, 4096 shots each (released script), twirling OFF (gates and measure), dynamical decoupling OFF,
max_execution_time 60.  Before the job: remaining seconds (stop if < 600), estimate vs cap 30 s, backend record saved.
One restart on an IBM-side ERROR, then HOLD.
Usage: fire.py (dry run: transpile, print depth/2q count/estimate/remaining; submits nothing) | fire.py --fire"""
import json, sys, os, time, hashlib
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H); sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
from sis_qubo import build, circuit
CHIP = 'ibm_kingston'; CAP = 30; SHOTS = 4096; TSEED = 2608; MINREM = 600
if __name__ == '__main__':
    from sweep import service
    from qiskit import qpy
    from qiskit.transpiler import generate_preset_pass_manager
    from qiskit_ibm_runtime import SamplerV2
    kg = json.load(open(f'{H}/known_good.json'))
    s = service(); b = s.backend(CHIP); rem = s.usage().get('usage_remaining_seconds'); st = b.status()
    pm = generate_preset_pass_manager(backend=b, optimization_level=3, seed_transpiler=TSEED)
    circs, info = [], {}
    for v in 'PS':
        m = build(v); qc = circuit(m['h'], m['J'], np.array(kg[v]['angles'])); isa = pm.run(qc); circs.append(isa)
        ops = isa.count_ops(); n2 = sum(ops.get(g, 0) for g in ('cz', 'ecr', 'cx'))
        layout = isa.layout.final_index_layout() if isa.layout else None
        info[v] = dict(depth=isa.depth(), twoq=int(n2), ops={k: int(x) for k, x in ops.items()}, layout=layout, logical_twoq=int(qc.count_ops().get('cx', 0)))
    dt = b.target.dt or 0; rep = getattr(b.configuration(), 'default_rep_delay', 250e-6) or 250e-6
    try:
        from qiskit.transpiler.passes import ALAPScheduleAnalysis
        durs = [isa.estimate_duration(b.target) for isa in circs]
    except Exception: durs = [None, None]
    per = [((d or 0) + rep + 2e-6) for d in durs]; est = 2.0 + sum(SHOTS * p for p in per)
    print(f'{CHIP}: operational {st.operational}, pending {st.pending_jobs}; remaining {rem} s; circuits {json.dumps({v: {k: info[v][k] for k in ("depth", "twoq", "logical_twoq", "layout")} for v in info})}; '
          f'durations {durs} s, rep_delay {rep}; est {est:.1f} s (cap {CAP}); SamplerV2 {SHOTS} shots, twirling OFF, DD OFF', flush=True)
    json.dump(dict(info=info, durations=durs, rep_delay=rep, est=est), open(f'{H}/dryrun.json', 'w'), default=str)
    if '--fire' not in sys.argv: print('DRY RUN, nothing submitted'); sys.exit(0)
    if rem is not None and rem < MINREM: print(f'STOP: remaining {rem} < {MINREM}'); sys.exit(1)
    if est > CAP: print(f'STOP: estimate {est:.1f} > cap {CAP}'); sys.exit(1)
    qpy.dump(circs, open(f'{H}/circuits.qpy', 'wb')); chash = hashlib.sha256(open(f'{H}/circuits.qpy', 'rb').read()).hexdigest()
    rec = dict(chip=CHIP, shots=SHOTS, transpile_seed=TSEED, optimization_level=3, circuits_sha256=chash, variants=['P', 'S'], twirling=False, dd=False, jobs=[])
    for attempt in (1, 2):
        rem = s.usage().get('usage_remaining_seconds')
        if rem is not None and rem < MINREM: print(f'STOP: remaining {rem} < {MINREM}'); break
        json.dump(b.properties(refresh=True).to_dict(), open(f'{H}/props_before_{attempt}.json', 'w'), default=str)
        smp = SamplerV2(mode=b); smp.options.default_shots = SHOTS
        smp.options.twirling.enable_gates = False; smp.options.twirling.enable_measure = False; smp.options.dynamical_decoupling.enable = False
        smp.options.max_execution_time = 60; smp.options.environment.job_tags = ['qia-2608.13614', f'attempt{attempt}']
        job = smp.run([(c,) for c in circs], shots=SHOTS); sub = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        print(f'SUBMITTED attempt {attempt} job {job.job_id()} {sub} (remaining before {rem})', flush=True)
        try:
            res = job.result()
        except Exception as e:
            st_ = str(job.status()); rec['jobs'].append(dict(attempt=attempt, job_id=job.job_id(), submitted_utc=sub, status=st_, error=str(e)[:300]))
            json.dump(rec, open(f'{H}/job.json', 'w'), default=str); print(f'IBM-side ERROR attempt {attempt}: {st_}', flush=True)
            if attempt == 2: print('HOLD after one restart'); break
            continue
        raw = {v: {str(k): int(x) for k, x in pr.data.c.get_counts().items()} for v, pr in zip('PS', res)}
        json.dump(raw, open(f'{H}/raw_counts.json', 'w'))
        mt = job.metrics(); rec['jobs'].append(dict(attempt=attempt, job_id=job.job_id(), submitted_utc=sub, created=str(getattr(job, 'creation_date', '')), usage=mt.get('usage'), timestamps=mt.get('timestamps'), status=str(job.status())))
        json.dump(rec, open(f'{H}/job.json', 'w'), default=str); print(f'DONE usage {mt.get("usage")}', flush=True); break
    json.dump(b.properties(refresh=True).to_dict(), open(f'{H}/props_after.json', 'w'), default=str)
