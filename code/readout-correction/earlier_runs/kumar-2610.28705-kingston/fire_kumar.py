"""fire_kumar.py -- the free calibration run for Aryan Kumar's mid-circuit-measurement spectator probe (arXiv 2610.28705v1) on ibm_marrakesh
(<our IBM instance>, via sweep_run/sweep.py's service()).  ONE chip: his question (drift / twirl set / stated record on the PROBE, qubits 4-5-6) lives in his marrakesh jobs 2, 4, 5;
kingston only carries his pilots.  His open question: "A separately planned follow-up meets a +-0.005 equivalence criterion ... both repeat runs nevertheless trigger the drift rule."
Design (fixed before any job, PLAN_KUMAR.md.text): circuits rebuilt by my own builder (kumar.py; his code never run) for his job2 set (A, seed 20261003) and job4 set (B, seed 20261007),
200 circuits each (10 settings x 20 twirls), twirl metadata checked equal to his manifests, layout [4,5,6], transpiled ONCE (preset level 1, seed_transpiler 24, as his run_job) and the
SAME transpiled circuits sent in every job of a set; SamplerV2, 1000 shots, twirling OFF, dynamical decoupling OFF; four jobs back to back in the order A1 B1 B2 A2.
Before every job: remaining seconds checked, the backend record (properties) and the planned job saved.
Usage: fire_kumar.py            (dry run: rebuilds, checks and prints the layout, estimate and remaining seconds; submits NOTHING)
       fire_kumar.py --fire     (submits)"""
import json, sys, time, hashlib, os
import numpy as np
sys.path.insert(0, os.path.expanduser('<local helper folder>'))
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from sweep import service
from kumar import *
from qiskit import qpy
DRAW_KEYS = ('setting', 'cz_twirl', 'folds', 'mcm_twirl', 'fin_map', 'window_dt', 'echo', 'twirl', 'seed', 'pad_on')
CHIP = 'ibm_kingston'; CAP = 280; MAXEXEC = 100; EST_JOB = 59; TSEED = 24
PLAN = [('A1', 'A'), ('B1', 'B'), ('B2', 'B'), ('A2', 'A')]; EST = EST_JOB * len(PLAN)          # his logged probe sub-job: 58.9 s (job4), 58 s (job2)
if __name__ == '__main__':
    from qiskit.transpiler import generate_preset_pass_manager
    s = service(); b = s.backend(CHIP); rem = s.usage().get('usage_remaining_seconds'); st = b.status(); tim = Timing(b.target)
    assert 'if_else' in b.target.operation_names and 'measure_2' in b.target.operation_names
    sets = {}; eqn = 0; tot = 0; isa_bad = 0; depth = 0
    pm = generate_preset_pass_manager(backend=b, optimization_level=1, initial_layout=LAYOUT, seed_transpiler=TSEED)
    for X, seed, job in (('A', SEED_A, 'job2'), ('B', SEED_B, 'job4')):
        hm = his_probe_metas(f'{HERE}/theirs/{job}_manifest.json'); built = build_set(seed, tim, hm)
        isa = [pm.run(qc) for qc, _ in built]; eqn += sum(all(m[k] == h[k] for k in DRAW_KEYS) for (qc, m), h in zip(built, hm)); tot += len(hm)   # companion: draws only, timing fields come from kingston (addendum 3)
        isa_bad += sum(bool(check_isa(qc, i)) for (qc, _), i in zip(built, isa)); depth = max(depth, max(i.depth() for i in isa)); sets[X] = (built, isa)
    from qiskit_ibm_runtime import SamplerV2
    smp = SamplerV2(mode=b); smp.options.default_shots = SHOTS; smp.options.twirling.enable_gates = False; smp.options.twirling.enable_measure = False; smp.options.dynamical_decoupling.enable = False
    print(f'{CHIP}: operational {st.operational}, pending {st.pending_jobs}; his probe sets rebuilt by my own builder: twirl metadata equals his manifests in {eqn}/{tot} instances '
          f'(A = job2 seed {SEED_A}, B = job4 seed {SEED_B}), layout {LAYOUT}, transpiled once (level 1, seed {TSEED}; ISA check failures {isa_bad}, max depth {depth}), '
          f'SamplerV2 {SHOTS} shots, twirling OFF, DD OFF (options set offline), 4 jobs A1 B1 B2 A2 of 200 circuits, est {EST} s (cap {CAP}), remaining {rem}  -- DRY RUN, nothing submitted' if '--fire' not in sys.argv
          else f'{CHIP}: FIRING, est {EST} s, cap {CAP}, remaining {rem}', flush=True)
    if '--fire' not in sys.argv: sys.exit(0)
    if eqn != tot or isa_bad or EST > CAP or (rem is not None and rem < EST + 30): print('STOP: metadata/ISA check failed, estimate over cap or not enough seconds'); sys.exit(1)
    allc = {X: sets[X][1] for X in 'AB'}; qpy.dump(allc['A'] + allc['B'], open(f'{HERE}/circuits_kumar.qpy', 'wb')); chash = hashlib.sha256(open(f'{HERE}/circuits_kumar.qpy', 'rb').read()).hexdigest()
    json.dump({X: [m for _, m in sets[X][0]] for X in 'AB'}, open(f'{HERE}/metas_kumar.json', 'w'))
    rec = dict(chip=CHIP, shots=SHOTS, layout=LAYOUT, circuits_sha256=chash, transpile_seed=TSEED, seeds=dict(A=SEED_A, B=SEED_B), planned=[p[0] for p in PLAN], jobs=[]); spent = 0; est = EST_JOB
    for label, X in PLAN:
        rem = s.usage().get('usage_remaining_seconds')                                         # remaining seconds checked before EVERY job
        if spent + est > CAP: print(f'STOP: {spent} s spent + {est} s next > cap {CAP}'); break
        if rem is not None and rem < est + 30: print(f'STOP: remaining {rem} s < {est} + 30'); break
        json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_kumar_before_{label}.json', 'w'), default=str)      # record BEFORE the job
        json.dump(dict(rec, next=label, remaining_before=rem), open(f'{HERE}/job_kumar.json', 'w'), default=str)
        smp = SamplerV2(mode=b); smp.options.default_shots = SHOTS; smp.options.twirling.enable_gates = False; smp.options.twirling.enable_measure = False
        smp.options.dynamical_decoupling.enable = False; smp.options.max_execution_time = MAXEXEC; smp.options.environment.job_tags = ['kumar-abba', label]
        job = smp.run([(c,) for c in allc[X]], shots=SHOTS); sub = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        print(f'SUBMITTED job {label} {job.job_id()} {sub} (remaining before {rem})', flush=True)
        res = job.result(); ents = []
        for (qc, m), pr in zip(sets[X][0], res):
            d = pr.data; ents.append(dict(setting=m['setting'], twirl=m['twirl'], counts_fin={str(k): int(v) for k, v in d.fin.get_counts().items()}, counts_mcm={str(k): int(v) for k, v in d.mcm.get_counts().items()}))
        json.dump(ents, open(f'{HERE}/raw_kumar_{label}.json', 'w'))
        mt = job.metrics(); u = (mt.get('usage') or {}).get('quantum_seconds') or (mt.get('usage') or {}).get('qpu_charge_time_seconds') or est; spent += u; est = max(EST_JOB, u)
        rec['jobs'].append(dict(label=label, set=X, job_id=job.job_id(), submitted_utc=sub, usage=mt.get('usage'), timestamps=mt.get('timestamps')))
        json.dump(rec, open(f'{HERE}/job_kumar.json', 'w'), default=str); print(f'DONE job {label} usage {u} s (total {spent})', flush=True)
    json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_kumar_after.json', 'w'), default=str)
    print('ALL DONE', spent, 's -- now run analyze_kumar.py', flush=True)
