"""fire_layout.py -- ADDENDUM 2 control job (written AFTER job 1's results were read; post-hoc, descriptive): same 20 pairs, same builder, one copy each, two arms
in ONE job, interleaved per pair (L1, L2, L1, L2 ...): L1 = job 1's layout fixed as initial_layout; L2 = the same layout with physical pair (1, 0) -- logical
qubits 3 and 12 -- moved to (13, 14) (CZ entry dated 24 Oct). Preset level 1, seed_transpiler 1689; SamplerV2 1000 shots, twirling OFF, DD OFF.
Cap: this run's total 30 s minus job 1's 13 s = 17 s.   Usage: fire_layout.py (dry run) | fire_layout.py --fire"""
import json, sys, time, hashlib, os
sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from sweep import service
from swaprun import *
from fire_swap import opts
from qiskit import qpy
CHIP = 'ibm_kingston'; CAP = 17; EST = 14
if __name__ == '__main__':
    from qiskit.transpiler import generate_preset_pass_manager
    from qiskit_ibm_runtime import SamplerV2
    s = service(); b = s.backend(CHIP); rem = s.usage().get('usage_remaining_seconds')
    L1 = json.load(open(f'{HERE}/job_swap.json'))['layouts'][0]; L2 = list(L1); assert (L1[3], L1[12]) == (1, 0); L2[3], L2[12] = 13, 14
    P = select(curves()); arms = {}
    for nm, L in (('L1', L1), ('L2', L2)):
        pm = generate_preset_pass_manager(backend=b, optimization_level=1, initial_layout=L, seed_transpiler=TSEED)
        arms[nm] = [pm.run(build(p['a'], p['b'], name=f"{nm}_{p['cls']}_{p['A']}_{p['B']}")) for p in P]
        got = [c.layout.final_index_layout()[:2 * NQ] for c in arms[nm]]; assert all(g == L for g in got), nm
    order = [(i, nm) for i in range(len(P)) for nm in ('L1', 'L2')]; circs = [arms[nm][i] for i, nm in order]
    print(f'{CHIP}: {len(circs)} circuits, depth {sorted(set(c.depth() for c in circs))}, cz {sorted(set(c.count_ops().get("cz", 0) for c in circs))}; L1 {L1}; L2 {L2}; est {EST} s, cap {CAP}, remaining {rem}'
          + ('  -- DRY RUN' if '--fire' not in sys.argv else '  -- FIRING'), flush=True)
    if '--fire' not in sys.argv: sys.exit(0)
    if EST > CAP or rem is None or rem < 600 or rem < EST + 30: print('STOP'); sys.exit(1)
    qpy.dump(circs, open(f'{HERE}/circuits_layout.qpy', 'wb'))
    rec = dict(chip=CHIP, shots=SHOTS, L1=L1, L2=L2, order=order, circuits_sha256=hashlib.sha256(open(f'{HERE}/circuits_layout.qpy', 'rb').read()).hexdigest(), twirling=False, dd=False, remaining_before=rem, jobs=[])
    json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_layout_before.json', 'w'), default=str)
    smp = SamplerV2(mode=b); opts(smp, 'layout-control'); smp.options.max_execution_time = CAP
    job = smp.run([(c,) for c in circs], shots=SHOTS); sub = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()); print(f'SUBMITTED job {job.job_id()} {sub}', flush=True)
    try: res = job.result()
    except Exception as e:
        rec['jobs'].append(dict(job_id=job.job_id(), submitted_utc=sub, status=str(job.status()), error=str(e)[:300])); json.dump(rec, open(f'{HERE}/job_layout.json', 'w'), default=str)
        print('IBM-side ERROR -> HOLD (the run cap leaves no restart):', str(e)[:200]); sys.exit(1)
    json.dump([dict(pair=i, arm=nm, counts={str(k): int(v) for k, v in pr.data.c.get_counts().items()}) for (i, nm), pr in zip(order, res)], open(f'{HERE}/raw_layout.json', 'w'))
    mt = job.metrics(); rec['jobs'].append(dict(job_id=job.job_id(), submitted_utc=sub, status=str(job.status()), usage=mt.get('usage'), timestamps=mt.get('timestamps')))
    json.dump(rec, open(f'{HERE}/job_layout.json', 'w'), default=str); json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_layout_after.json', 'w'), default=str)
    print('DONE', mt.get('usage'), flush=True)
