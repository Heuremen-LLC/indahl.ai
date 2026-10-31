"""fire_clock.py CHIP [--fire] -- builds, checks and (with --fire) submits one day of the Darkwave clock run (PLAN_CLOCK.md.text).
Dry run: roles from the committed table, every circuit built (MT with the 31 Oct table as a stand-in so the checks run; MT is REBUILT from job C
before job A), transpiled once (level 1, trivial layout, seed 31); checks: layout unmoved, no CZ, scheduled durations on the untouched qubits
equal for every arm, rz count larger in the corrected arms than in M, seconds estimate vs cap and vs what is left.
--fire: record -> job C (calibration, the keystone's 8 circuits) -> today's table -> MT rebuilt and re-checked -> job A -> job B (reversed).
Every classical register saved per shot. One restart on an IBM-side ERROR, then HOLD; the backend's job list is read before any re-attempt."""
import json, sys, os, time, hashlib, warnings; warnings.filterwarnings('ignore')
import numpy as np
sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
from sweep import service
from qiskit import transpile, qpy
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import keystone as K, clock as C
CHIP = sys.argv[1]; assert CHIP in ('ibm_kingston', 'ibm_marrakesh'); CAP = 60; SEED = 31
DAY = time.strftime('%Y%m%d_%H%M', time.gmtime())
T = K.table(CHIP); E = [int(q) for q in T['E']]; S = [int(q) for q in T['S']]; L_DT = int(T['L_dt'])
s = service(); b = s.backend(CHIP); n = b.num_qubits
def tables(today): return {'MC': K.committed_corr(CHIP, 8), 'M31': C.table31(CHIP), 'MT': today}
def build_all(tab): return {k: C.build(n, E, S, k[0], k[1], tab, L_DT) for k in C.keys()}
def build_cal(): return {k: K.circ_S(n, E, S, k[1], k[2], {}, L_DT, N=k[3]) for k in K.keys_cal()}
def tp(circs): return {k: transpile(c, b, optimization_level=1, initial_layout=list(range(n)), seed_transpiler=SEED) for k, c in circs.items()}
def check(TC, cal=False):
    bad = []
    for k, t in TC.items():
        if t.layout is not None and list(t.layout.final_index_layout()) != list(range(n)): bad.append(('layout moved', k))
        if t.count_ops().get('cz', 0): bad.append(('cz', k))
    if cal: return bad, {}
    dur = {}
    for a in C.ARMS:
        sc = transpile(TC[(a, 'X')], b, optimization_level=0, scheduling_method='alap', initial_layout=list(range(n)))
        dur[a] = max(sc.qubit_duration(q) for q in S)
    if len(set(dur[a] for a in ('D', 'M', 'MC', 'M31', 'MT'))) != 1: bad.append(('durations differ', dur))
    rzM = TC[('M', 'X')].count_ops().get('rz', 0)
    for a in ('MC', 'M31', 'MT'):
        if not TC[(a, 'X')].count_ops().get('rz', 0) > rzM: bad.append(('rz not added', a))
    return bad, dur
TC = tp(build_all(tables(C.table31(CHIP)))); TCAL = tp(build_cal())
bad, dur = check(TC); badc, _ = check(TCAL, cal=True); bad += badc
est = 2 * (len(C.keys()) * C.SHOTS * 0.30e-3 + 3) + (len(K.keys_cal()) * K.SHOTS['CAL'] * 0.30e-3 + 3)
rem = s.usage().get('usage_remaining_seconds')
print(f'{CHIP}: circuits {len(TC)} x 2 jobs + cal {len(TCAL)}; checks {"PASS" if not bad else "FAIL " + str(bad[:3])}; durations (dt) {dur}; est {est:.0f} s (cap {CAP}), remaining {rem}', flush=True)
if '--fire' not in sys.argv: sys.exit(0)
assert not bad, 'STOP: checks'
assert est <= CAP and rem is not None and rem >= est + 10, 'STOP: cap or seconds'
from qiskit_ibm_runtime import SamplerV2
OUT = os.path.join(HERE, f'day_{DAY}_{CHIP}'); os.makedirs(OUT, exist_ok=True)
rec = dict(chip=CHIP, day_utc=DAY, E=E, S=S, L_dt=L_DT, shots=C.SHOTS, seed_transpiler=SEED, keys=[list(k) for k in C.keys()], durations_dt=dur, jobs=[], dd='off', twirling='off')
def save_rec(): json.dump(rec, open(f'{OUT}/job_clock.json', 'w'), default=str)
def run(label, circs, shots_list):
    for attempt in (1, 2):
        json.dump(b.properties(refresh=True).to_dict(), open(f'{OUT}/props_before_{label}' + ('' if attempt == 1 else '_retry') + '.json', 'w'), default=str)
        smp = SamplerV2(mode=b); smp.options.dynamical_decoupling.enable = False; smp.options.twirling.enable_gates = False; smp.options.twirling.enable_measure = False
        job = smp.run([(c, None, sh) for c, sh in zip(circs, shots_list)]); sub = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        print(f'SUBMITTED {label} attempt {attempt} job {job.job_id()} {sub}', flush=True)
        rec['jobs'].append(dict(label=label, attempt=attempt, job_id=job.job_id(), submitted_utc=sub, status='SUBMITTED')); save_rec()
        res = None
        for tries in range(200):
            try: res = job.result(); break
            except Exception as ex:
                try: st = str(job.status())
                except Exception: st = 'UNKNOWN'
                print(f'WAIT {label}: {type(ex).__name__}; IBM status {st}', flush=True)
                if 'ERROR' in st or 'CANCEL' in st: break
                time.sleep(20)
        if res is not None:
            m = job.metrics(); rec['jobs'][-1].update(status='DONE', usage=m.get('usage'), timestamps=m.get('timestamps')); save_rec()
            print(f'DONE {label} usage {m.get("usage")}', flush=True); return res
        rec['jobs'][-1].update(status=f'IBM {st}'); save_rec()
        print('jobs on backend (newest 20):', [(j.job_id(), str(j.status())) for j in s.jobs(backend_name=CHIP, limit=20)], flush=True)
        if attempt == 2 or not ('ERROR' in st or 'CANCEL' in st): print('HOLD: not resubmitted', flush=True); sys.exit(2)
def save_raw(label, keys, order, res):
    arrs = {}
    for i, pr in zip(order, res):
        for reg in pr.data: arrs[f'{reg}_{i}'] = np.asarray(getattr(pr.data, reg).array)
    np.savez_compressed(f'{OUT}/raw_{label}.npz', **arrs)
kc = K.keys_cal(); resC = run('C', [TCAL[k] for k in kc], [K.SHOTS['CAL']] * len(kc)); save_raw('C', kc, list(range(len(kc))), resC)
ZC = {k: [np.asarray(resC[i].data.fin.array)] for i, k in enumerate(kc)}
today = {q: v['k8'] for q, v in K.fresh_from_cal(CHIP, ZC, S).items()}
json.dump(dict(chip=CHIP, from_job=rec['jobs'][-1]['job_id'], rule='keystone fresh_from_cal, k8', kicks=today), open(f'{OUT}/today_table.json', 'w'), indent=0)
TC = tp(build_all(tables(today))); bad, dur2 = check(TC); assert not bad, f'STOP after C: checks {bad[:3]}'
km = C.keys(); circs = [TC[k] for k in km]; qpy.dump(circs, open(f'{OUT}/circuits_main.qpy', 'wb'))
rec['circuit_hash_main'] = hashlib.sha256(open(f'{OUT}/circuits_main.qpy', 'rb').read()).hexdigest(); save_rec()
for label, order in (('A', list(range(len(km)))), ('B', list(range(len(km)))[::-1])):
    res = run(label, [circs[i] for i in order], [C.SHOTS] * len(order)); save_raw(label, km, order, res)
json.dump(b.properties(refresh=True).to_dict(), open(f'{OUT}/props_after.json', 'w'), default=str)
print('ALL DONE', CHIP, sum(((j.get('usage') or {}).get('quantum_seconds') or (j.get('usage') or {}).get('qpu_charge_time_seconds') or 0) for j in rec['jobs']), 's', flush=True)
