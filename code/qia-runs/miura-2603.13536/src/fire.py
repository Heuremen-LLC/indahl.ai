"""fire.py -- the free run for arXiv 2603.13536v1 (Miura, Kobe City College of Technology) on ibm_pittsburgh, Darkwave Disco
(sweep_run/sweep.py service()).  ONE job, 32 circuits, fixed in PLAN_2603.13536.md.text before any job:
  for each of 10 field instances (seeds 100..109): trot t=0.6 at 2400 shots + trot t=1.2 at 600 shots (build_2.py's aer_noise mix),
  ctrl (H layer, measure; no entangling gate) at 3000 shots;  readout seats |0..0> and |1..1> at 1000 shots each.
Layout: the 12-qubit heavy-hex ring of ibm_pittsburgh with the lowest (sum of stated CZ error on its 12 edges + sum of stated readout
error on its 12 qubits) in the record pulled just before the job, virtual qubit i -> ring[i] so every bond of the periodic chain is a
native edge (no SWAP; checked).  Transpile: preset optimization_level 1, seed_transpiler 13536, once.  SamplerV2, twirling OFF (gates and
measure), dynamical decoupling OFF, max_execution_time 30 s (the hard cap), shots per PUB.  One restart on an IBM-side ERROR, then HOLD.
Usage: fire.py (dry run, submits NOTHING) | fire.py --fire"""
import json, sys, time, os, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); RUN = os.path.dirname(HERE); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
import numpy as np
from assqd import heis_terms
from circuits import trotter, control, seat, rings, T0, T1, SH0, SH1, SHOTS, SEAT_SHOTS
CHIP = 'ibm_pittsburgh'; N = 12; SEEDS = list(range(100, 110)); TSEED = 13536; CAP = 30; MIN_REMAIN = 600; MS_PER_SHOT = 0.30; OVERHEAD = 3

def build():
    circs, meta = [], []
    for s in SEEDS:
        tm = heis_terms(N, s)
        circs += [trotter(N, tm, T0, name=f'trot_t0_{s}'), trotter(N, tm, T1, name=f'trot_t1_{s}'), control(N, name=f'ctrl_{s}')]
        meta += [dict(kind='trot', t=T0, seed=s, shots=SH0), dict(kind='trot', t=T1, seed=s, shots=SH1), dict(kind='ctrl', seed=s, shots=SHOTS)]
    circs += [seat(N, False, 'seat0'), seat(N, True, 'seat1')]; meta += [dict(kind='seat', one=0, shots=SEAT_SHOTS), dict(kind='seat', one=1, shots=SEAT_SHOTS)]
    return circs, meta

def pick_ring(b):
    tg = b.target; edges = set()
    for (a, c) in b.coupling_map.get_edges():
        if tg.instruction_supported('cz', (a, c)): edges.add(tuple(sorted((a, c))))
    def ez(a, c):
        v = [tg['cz'][e].error for e in ((a, c), (c, a)) if e in tg['cz'] and tg['cz'][e] is not None and tg['cz'][e].error is not None]
        return min(v) if v else None
    def er(q):
        p = tg['measure'].get((q,)); return None if p is None else p.error
    best = None
    for cyc in rings(sorted(edges)):
        es = [ez(cyc[i], cyc[(i + 1) % N]) for i in range(N)]; rs = [er(q) for q in cyc]
        if any(x is None or x >= 0.2 for x in es + rs): continue
        sc = sum(es) + sum(rs)
        if best is None or sc < best[0]: best = (sc, cyc, es, rs)
    return best

def check_isa(isa, ring):
    ringe = {tuple(sorted((ring[i], ring[(i + 1) % N]))) for i in range(N)}; bad = 0; ncz = 0
    for ins in isa.data:
        if ins.operation.num_qubits == 2:
            q = tuple(sorted(isa.find_bit(x).index for x in ins.qubits)); ncz += 1; bad += q not in ringe
    lay = isa.layout; fl = lay.final_index_layout() if lay is not None else None
    return bad, ncz, fl

if __name__ == '__main__':
    from sweep import service
    from qiskit.transpiler import generate_preset_pass_manager
    from qiskit_ibm_runtime import SamplerV2
    from qiskit import qpy
    s = service(); b = s.backend(CHIP); rem = s.usage().get('usage_remaining_seconds'); st = b.status()
    circs, meta = build(); best = pick_ring(b); sc, ring, es, rs = best
    pm = generate_preset_pass_manager(backend=b, optimization_level=1, initial_layout=ring, seed_transpiler=TSEED)
    isa = pm.run(circs); chk = [check_isa(c, ring) for c in isa]
    nbad = sum(x[0] for x in chk); perm_ok = all(x[2] is None or list(x[2]) == ring for x in chk)
    nshots = sum(m['shots'] for m in meta); est = nshots * MS_PER_SHOT / 1000 + OVERHEAD
    cz = [x[1] for x, m in zip(chk, meta) if m['kind'] == 'trot']; dep = max(c.depth() for c in isa)
    print(f'{CHIP}: operational {st.operational}, pending {st.pending_jobs}; ring {ring} score {sc:.4f} (CZ err {np.round(es,4).tolist()}, readout {np.round(rs,4).tolist()}); '
          f'{len(circs)} circuits, {nshots} shots; transpiled level 1 seed {TSEED}: 2q gates off the ring {nbad}, final layout = ring {perm_ok}, '
          f'2q per trot circuit {min(cz)}-{max(cz)}, max depth {dep}; twirling OFF, DD OFF; est {est:.1f} s (cap {CAP}), remaining {rem}'
          + ('' if '--fire' in sys.argv else '  -- DRY RUN, nothing submitted'), flush=True)
    if '--fire' not in sys.argv: sys.exit(0)
    if nbad or not perm_ok or est > CAP or rem is None or rem < MIN_REMAIN or rem < est + 30: print('STOP: layout/estimate/remaining check failed'); sys.exit(1)
    qpy.dump(isa, open(f'{RUN}/circuits_2603.13536.qpy', 'wb')); chash = hashlib.sha256(open(f'{RUN}/circuits_2603.13536.qpy', 'rb').read()).hexdigest()
    rec = dict(chip=CHIP, ring=ring, ring_score=sc, transpile_seed=TSEED, circuits_sha256=chash, meta=meta, nshots=nshots, est_s=est, cap_s=CAP,
               twirling='off (gates, measure)', dd='off', remaining_before=rem, attempts=[])
    for attempt in (1, 2):
        rem = s.usage().get('usage_remaining_seconds')
        if rem is None or rem < MIN_REMAIN or rem < est + 30: print(f'STOP: remaining {rem}'); break
        json.dump(b.properties(refresh=True).to_dict(), open(f'{RUN}/props_2603.13536_before_{attempt}.json', 'w'), default=str)   # record BEFORE the job
        json.dump(dict(rec, next_attempt=attempt), open(f'{RUN}/job_2603.13536.json', 'w'), default=str)
        smp = SamplerV2(mode=b); smp.options.twirling.enable_gates = False; smp.options.twirling.enable_measure = False
        smp.options.dynamical_decoupling.enable = False; smp.options.max_execution_time = CAP; smp.options.environment.job_tags = ['qia-2603.13536', f'attempt{attempt}']
        job = smp.run([(c, None, m['shots']) for c, m in zip(isa, meta)]); sub = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        print(f'SUBMITTED attempt {attempt} job {job.job_id()} {sub} (remaining before {rem})', flush=True)
        try:
            res = job.result(); ok = True
        except Exception as e:
            ok = False; print(f'IBM-side failure on attempt {attempt}: {type(e).__name__}: {str(e)[:300]}', flush=True)
        mt = job.metrics(); a = dict(attempt=attempt, job_id=job.job_id(), submitted_utc=sub, status=str(job.status()), usage=mt.get('usage'), timestamps=mt.get('timestamps'))
        rec['attempts'].append(a); json.dump(rec, open(f'{RUN}/job_2603.13536.json', 'w'), default=str)
        if ok:
            raw = [dict(m, counts={str(k): int(v) for k, v in pr.data.meas.get_counts().items()}) for m, pr in zip(meta, res)]
            json.dump(raw, open(f'{RUN}/raw_2603.13536.json', 'w')); print(f'DONE usage {a["usage"]}', flush=True); break
        if attempt == 2: print('HOLD: second IBM-side failure, nothing more submitted', flush=True)
    json.dump(b.properties(refresh=True).to_dict(), open(f'{RUN}/props_2603.13536_after.json', 'w'), default=str)
    print('ALL DONE -- now run analyze.py', flush=True)
