"""fire_swap.py -- the free calibration run for arXiv 2508.16895v2 (Ang swap-test circuit) on ibm_kingston (Darkwave Disco via sweep_run/sweep.py service()).
Design fixed in PLAN_SWAP.md.text before any job: 20 pairs (swaprun.select) x 2 copies = 40 circuits in ONE job, order copy 1 pairs 0..19 then copy 2 pairs 19..0;
my own builder (swaprun.build; equals their released qasm2 2926/2926); transpiled once per pair (preset level 1, seed_transpiler 1689, layout chosen by the
transpiler as their 'default settings'); copy 2 sends the SAME transpiled circuit; SamplerV2, 1000 shots, twirling OFF (gates and measure), dynamical decoupling OFF.
Before the job: remaining seconds checked (stop if < 600 or < estimate + 30), the backend record (properties, refresh) and the planned job saved.
One restart on an IBM-side ERROR, then HOLD.   Usage: fire_swap.py (dry run, submits nothing) | fire_swap.py --fire"""
import json, sys, time, hashlib, os
sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from sweep import service
from swaprun import *
from qiskit import qpy
CHIP = 'ibm_kingston'; CAP = 30; MAXEXEC = 30; EST = 14          # 40 circuits x 1000 shots = 40,000 shots x ~0.285 ms (our kingston job today: 200,000 shots, 57 s) = 11.4 s + ~2 s
def opts(smp, tag):
    smp.options.default_shots = SHOTS; smp.options.twirling.enable_gates = False; smp.options.twirling.enable_measure = False
    smp.options.dynamical_decoupling.enable = False; smp.options.max_execution_time = MAXEXEC; smp.options.environment.job_tags = ['swap-2508.16895', tag]
if __name__ == '__main__':
    from qiskit.transpiler import generate_preset_pass_manager
    from qiskit_ibm_runtime import SamplerV2
    s = service(); b = s.backend(CHIP); rem = s.usage().get('usage_remaining_seconds'); st = b.status()
    P = select(curves()); pm = generate_preset_pass_manager(backend=b, optimization_level=1, seed_transpiler=TSEED)
    isa = [pm.run(build(p['a'], p['b'], name=f"{p['cls']}_{p['A']}_{p['B']}")) for p in P]
    order = [(i, 1) for i in range(len(P))] + [(i, 2) for i in reversed(range(len(P)))]; circs = [isa[i] for i, _ in order]
    ops = [dict(isa[i].count_ops()) for i in range(len(P))]; depth = [isa[i].depth() for i in range(len(P))]
    lay = [isa[i].layout.final_index_layout()[:2 * NQ] for i in range(len(P))]
    print(f'{CHIP}: operational {st.operational}, pending {st.pending_jobs}; {len(P)} pairs x 2 copies = {len(circs)} circuits, depth {min(depth)}-{max(depth)}, '
          f'cz {sorted(set(o.get("cz", 0) for o in ops))}, ops e.g. {ops[0]}; SamplerV2 {SHOTS} shots, twirling OFF, DD OFF; est {EST} s (cap {CAP}), remaining {rem}'
          + ('  -- DRY RUN, nothing submitted' if '--fire' not in sys.argv else '  -- FIRING'), flush=True)
    if '--fire' not in sys.argv: sys.exit(0)
    if EST > CAP or rem is None or rem < 600 or rem < EST + 30: print('STOP: estimate over cap or remaining seconds under 600 / estimate + 30'); sys.exit(1)
    qpy.dump(circs, open(f'{HERE}/circuits_swap.qpy', 'wb')); chash = hashlib.sha256(open(f'{HERE}/circuits_swap.qpy', 'rb').read()).hexdigest()
    rec = dict(chip=CHIP, shots=SHOTS, circuits_sha256=chash, transpile_seed=TSEED, order=order, pairs=[dict(cls=p['cls'], A=p['A'], B=p['B'], F=p['F']) for p in P],
               layouts=lay, depth=depth, ops=ops, twirling=False, dd=False, remaining_before=rem, jobs=[])
    spent = 0
    for attempt in (1, 2):
        rem = s.usage().get('usage_remaining_seconds')
        if spent + EST > CAP or rem < 600 or rem < EST + 30: print(f'STOP before attempt {attempt}: spent {spent}, remaining {rem}'); break
        json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_swap_before_{attempt}.json', 'w'), default=str)     # record BEFORE the job
        json.dump(dict(rec, next=f'attempt {attempt}'), open(f'{HERE}/job_swap.json', 'w'), default=str)
        smp = SamplerV2(mode=b); opts(smp, f'attempt{attempt}')
        job = smp.run([(c,) for c in circs], shots=SHOTS); sub = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        print(f'SUBMITTED attempt {attempt} job {job.job_id()} {sub} (remaining before {rem})', flush=True)
        try:
            res = job.result()
        except Exception as e:
            mt = job.metrics(); u = (mt.get('usage') or {}).get('quantum_seconds') or 0; spent += u
            rec['jobs'].append(dict(attempt=attempt, job_id=job.job_id(), submitted_utc=sub, status=str(job.status()), error=str(e)[:300], usage=mt.get('usage'), timestamps=mt.get('timestamps')))
            json.dump(rec, open(f'{HERE}/job_swap.json', 'w'), default=str); print(f'IBM-side ERROR on attempt {attempt}: {str(e)[:200]}', flush=True)
            if attempt == 2: print('HOLD: second error, no more restarts'); 
            continue
        raw = [dict(pair=i, copy=c, counts={str(k): int(v) for k, v in pr.data.c.get_counts().items()}) for (i, c), pr in zip(order, res)]
        json.dump(raw, open(f'{HERE}/raw_swap.json', 'w'))
        mt = job.metrics(); u = (mt.get('usage') or {}).get('quantum_seconds'); spent += u or 0
        rec['jobs'].append(dict(attempt=attempt, job_id=job.job_id(), submitted_utc=sub, status=str(job.status()), usage=mt.get('usage'), timestamps=mt.get('timestamps')))
        json.dump(rec, open(f'{HERE}/job_swap.json', 'w'), default=str); print(f'DONE job {job.job_id()} usage {u} s', flush=True)
        break
    json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_swap_after.json', 'w'), default=str)
    print('ALL DONE', spent, 's -- now run analyze_swap.py', flush=True)
