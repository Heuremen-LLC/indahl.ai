"""fire_keystone.py CHIP [--fire] -- builds, checks and (with --fire) submits the keystone run on one chip (PLAN_KEYSTONE.md.text). <our IBM instance>.
Dry run (default): roles from the committed table, clock qubits (kingston fixed; marrakesh by the plan's rule on today's record), every circuit
built with the committed correction (MF circuits get the committed table as a stand-in so the checks run; they are REBUILT from job C before A),
transpiled once (level 1, trivial layout, seed 31), checks: layout unmoved; CZ count clock 4 / pairs 48 / spectators 0; scheduled durations on the
untouched qubits equal for D, M, MC, MF and for DE, ME (and printed for ME minus M); rz count larger in MC than in M; seconds estimate vs cap.
--fire: record -> job C (calibration, 8 circuits) -> fresh table (fresh_kicks_CHIP.json, plan's branch rule) -> MF rebuilt and re-checked ->
job A (keys in order) -> job B (keys reversed). Record saved before every job; every classical register saved per shot (raw_keystone_CHIP_*.npz).
One restart on an IBM-side ERROR, then HOLD. Before any re-attempt the backend's job list since the plan commit is read (never refire from a log)."""
import json, sys, os, time, hashlib, warnings; warnings.filterwarnings('ignore')
import numpy as np
sys.path.insert(0, os.path.expanduser('<local helper folder>'))
from sweep import service
from qiskit import transpile, qpy
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import keystone as K
CHIP = sys.argv[1]; assert CHIP in ('ibm_kingston', 'ibm_marrakesh')
CAP = {'ibm_kingston': 240, 'ibm_marrakesh': 240}[CHIP]; SEED = 31
T = K.table(CHIP); E = [int(q) for q in T['E']]; S = [int(q) for q in T['S']]; PAIRS = [tuple(int(x) for x in p) for p in T['pairs']]
SING = [int(q) for q in T['singles']]; L_DT = int(T['L_dt'])
assert len(E) == 39 and len(S) == 117 and set(q for p in PAIRS for q in p) | set(SING) == set(S)
s = service(); b = s.backend(CHIP); n = b.num_qubits
props = b.properties(refresh=True)
rec_ok = lambda q: props.readout_error(q) < 0.05
def edge_ok(a, c):
    try: return props.gate_error('cz', [a, c]) < 0.01
    except Exception:
        try: return props.gate_error('cz', [c, a]) < 0.01
        except Exception: return False
if CHIP in K.CLOCK:
    CLK = K.CLOCK[CHIP]; assert all(rec_ok(q) for q in CLK) and edge_ok(CLK[0], CLK[1]) and edge_ok(CLK[1], CLK[2]), 'HOLD: clock record gate'
else:
    edges = sorted({tuple(sorted(e)) for e in b.coupling_map.get_edges()}); CLK = K.choose_clock(CHIP, edges, rec_ok, edge_ok)
    assert CLK, 'HOLD: no clock path passes the rule'
c0, sq, c1 = CLK; assert not {c0, sq, c1} & set(E)
def build_all(corr_tab):
    """corr_tab: {'MC': {N: {q: deg}}, 'MF': {N: {q: deg}}}"""
    out = {}
    for k in K.keys_main():
        part, arm, st = k; corr = corr_tab.get(arm, {})
        if part == 'S': out[k] = K.circ_S(n, E, S, arm, st, corr.get(K.N_S, {}), L_DT)
        elif part == 'P': out[k] = K.circ_P(n, E, PAIRS, SING, arm, st, corr.get(K.N_P, {}), L_DT)
        else: out[k] = K.circ_C(n, E, CLK, arm, st, corr.get(K.N_C, {}), L_DT)
    return out
def build_cal(): return {k: K.circ_S(n, E, S, k[1], k[2], {}, L_DT, N=k[3]) for k in K.keys_cal()}
def tp(circs): return {k: transpile(c, b, optimization_level=1, initial_layout=list(range(n)), seed_transpiler=SEED) for k, c in circs.items()}
def check(TC):
    bad = []
    for k, t in TC.items():
        if t.layout is not None and list(t.layout.final_index_layout()) != list(range(n)): bad.append(('layout moved', k))
        want = {'S': 0, 'P': len(PAIRS), 'C': 4, 'CAL': 0}[k[0]]
        if t.count_ops().get('cz', 0) != want: bad.append(('cz', k, t.count_ops().get('cz', 0), want))
    dur = {}
    for part, tg, st in (('S', S, 'X'), ('P', [q for p in PAIRS for q in p] + SING, 'XX'), ('C', [c0, c1, sq], 'XXX')):
        for arm in K.ARMS:
            sc = transpile(TC[(part, arm, st)], b, optimization_level=0, scheduling_method='alap', initial_layout=list(range(n)))
            dur[(part, arm)] = max(sc.qubit_duration(q) for q in tg)
        if not (dur[(part, 'D')] == dur[(part, 'M')] == dur[(part, 'MC')] == dur[(part, 'MF')]): bad.append(('duration D/M/MC/MF', part, [dur[(part, a)] for a in ('D', 'M', 'MC', 'MF')]))
        if dur[(part, 'DE')] != dur[(part, 'ME')]: bad.append(('duration DE/ME', part, dur[(part, 'DE')], dur[(part, 'ME')]))
        rzM = TC[(part, 'M', st)].count_ops().get('rz', 0); rzC = TC[(part, 'MC', st)].count_ops().get('rz', 0)
        if not rzC > rzM: bad.append(('rz not added in MC', part, rzM, rzC))
    return bad, {f'{p}_{a}': d for (p, a), d in dur.items()}
committed = {'MC': {N: K.committed_corr(CHIP, N) for N in (4, 8)}}
committed['MF'] = committed['MC']   # stand-in for the dry run only; MF is rebuilt from job C before job A
TC = tp(build_all(committed)); TCAL = tp(build_cal())
bad, dur = check({**TC, **TCAL})
est_main = sum(K.SHOTS[k[0]] for k in K.keys_main()) * 0.30e-3 + 4; est_cal = len(K.keys_cal()) * K.SHOTS['CAL'] * 0.30e-3 + 3
est = 2 * est_main + est_cal; rem = s.usage().get('usage_remaining_seconds')
print(f'{CHIP}: clock c0,s,c1 = {CLK}; L {L_DT} dt; circuits main {len(TC)} x 2 jobs + cal {len(TCAL)}; checks {"PASS" if not bad else "FAIL " + str(bad[:4])}; '
      f'durations (dt) {json.dumps(dur)}; ME minus M (S) {dur["S_ME"] - dur["S_M"]} dt; est {est:.0f} s (cap {CAP}), remaining {rem}', flush=True)
if '--fire' not in sys.argv: sys.exit(0)
assert not bad, 'STOP: checks'
assert est <= CAP and rem is not None and rem >= est + 30, 'STOP: cap or seconds'
from qiskit_ibm_runtime import SamplerV2
rec = dict(chip=CHIP, clock=list(CLK), E=E, S=S, pairs=[list(p) for p in PAIRS], singles=SING, L_dt=L_DT, shots=K.SHOTS, seed_transpiler=SEED,
           keys=[list(k) for k in K.keys_main()], keys_cal=[list(k) for k in K.keys_cal()], durations_dt=dur, jobs=[], dd='off', twirling='off')
def save_rec(): json.dump(rec, open(f'{HERE}/job_keystone_{CHIP}.json', 'w'), default=str)
def run(label, circs, shots_list):
    """submit once; wait on IBM's own status. A client-side exception (network, timeout) NEVER resubmits: the job is re-read by id.
    Resubmit (once) only when IBM reports the job ERROR or CANCELLED, after printing the backend's job list (list jobs before refire)."""
    for attempt in (1, 2):
        json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_keystone_{CHIP}_before_{label}' + ('' if attempt == 1 else '_retry') + '.json', 'w'), default=str)
        smp = SamplerV2(mode=b); smp.options.dynamical_decoupling.enable = False; smp.options.twirling.enable_gates = False; smp.options.twirling.enable_measure = False
        job = smp.run([(c, None, sh) for c, sh in zip(circs, shots_list)]); sub = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        print(f'SUBMITTED {label} attempt {attempt} job {job.job_id()} {sub}', flush=True)
        rec['jobs'].append(dict(label=label, attempt=attempt, job_id=job.job_id(), submitted_utc=sub, status='SUBMITTED')); save_rec()
        res = None
        for tries in range(200):
            try:
                res = job.result(); break
            except Exception as ex:
                try: st = str(job.status())
                except Exception: st = 'UNKNOWN'
                print(f'WAIT {label}: result() raised {type(ex).__name__}: {str(ex)[:120]}; IBM status {st}', flush=True)
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
        for reg in pr.data:
            arrs[f'{reg}_{i}'] = np.asarray(getattr(pr.data, reg).array)
    np.savez_compressed(f'{HERE}/raw_keystone_{CHIP}_{label}.npz', **arrs)
# job C
kc = K.keys_cal(); qpy.dump([TCAL[k] for k in kc], open(f'{HERE}/circuits_keystone_{CHIP}_C.qpy', 'wb'))
resC = run('C', [TCAL[k] for k in kc], [K.SHOTS['CAL']] * len(kc)); save_raw('C', kc, list(range(len(kc))), resC)
ZC = {k: [np.asarray(resC[i].data.fin.array)] for i, k in enumerate(kc)}
fresh = K.fresh_from_cal(CHIP, ZC, S)
json.dump(dict(chip=CHIP, from_job=rec['jobs'][-1]['job_id'], rule='t4 nearest 4 x committed N=4 kick; t8 nearest 2 x t4', kicks=fresh),
          open(f'{HERE}/fresh_kicks_{CHIP}.json', 'w'), indent=0)
tab = {'MC': committed['MC'], 'MF': {4: K.fresh_corr(CHIP, 4), 8: K.fresh_corr(CHIP, 8)}}
TC = tp(build_all(tab)); bad, dur2 = check(TC); assert not bad, f'STOP after C: checks {bad[:3]}'
km = K.keys_main(); circs = [TC[k] for k in km]; qpy.dump(circs, open(f'{HERE}/circuits_keystone_{CHIP}_main.qpy', 'wb'))
rec['circuit_hash_main'] = hashlib.sha256(open(f'{HERE}/circuits_keystone_{CHIP}_main.qpy', 'rb').read()).hexdigest(); save_rec()
shots = [K.SHOTS[k[0]] for k in km]
for label, order in (('A', list(range(len(km)))), ('B', list(range(len(km)))[::-1])):
    res = run(label, [circs[i] for i in order], [shots[i] for i in order])
    save_raw(label, km, order, res)
json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_keystone_{CHIP}_after.json', 'w'), default=str)
print('ALL DONE', CHIP, sum(((j.get('usage') or {}).get('quantum_seconds') or 0) for j in rec['jobs']), 's', flush=True)
