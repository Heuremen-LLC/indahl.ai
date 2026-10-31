"""fire_pooters.py -- builds, checks and (with --fire) submits the Page-Wootters run (PLAN_POOTERS.md.text). ibm_kingston, <our IBM instance>.
Physical qubits fixed by the plan: c0 = 3, s = 16, c1 = 23 (path 3-16-23); pack E = the 39 emitters of the 21 Oct control run.
27 tomography settings x 2 arms (M: pack read out 4 times, default measure; D: pack idles 4 x 545 dt). 2 jobs, ABBA:
J1 = settings in order, M then D for each; J2 = settings reversed, D then M. Same transpiled circuits in both jobs.
Checks before any job: trivial layout, 4 CZ per circuit (no routing), M and D scheduled durations equal on c0, c1, s; record holds the gate.
Per-shot bitstrings saved (fin + the 4 pack readouts in arm M) so outcome-conditioned readings are possible later.
Record saved before every job; one restart on an IBM-side ERROR, then HOLD.
Usage: fire_pooters.py (dry run)  |  fire_pooters.py --fire"""
import json, sys, os, time, hashlib, warnings; warnings.filterwarnings('ignore')
import numpy as np
sys.path.insert(0, os.path.expanduser('<local helper folder>'))
from sweep import service
from qiskit import QuantumCircuit, ClassicalRegister, transpile, qpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pooters import SETTINGS, THETA, NREAD
HERE = os.path.dirname(os.path.abspath(__file__)); CHIP = 'ibm_kingston'; SHOTS = 2000; CAP = 90; RESERVE = 430; L_DT = 545
C0, S_, C1 = 3, 16, 23
E = json.load(open(os.path.expanduser('../earlier_runs/control_run/job_ibm_kingston.json')))['E']
assert len(E) == 39 and not {C0, S_, C1} & set(E)
def rot(qc, q, b):
    if b == 'X': qc.h(q)
    elif b == 'Y': qc.sdg(q); qc.h(q)
def build(n, arm, st):
    regs = [ClassicalRegister(len(E), f'm{k}') for k in range(NREAD)]; fin = ClassicalRegister(3, 'fin'); qc = QuantumCircuit(n)
    for r in regs: qc.add_register(r)
    qc.add_register(fin)
    qc.h(C0); qc.h(C1); qc.cry(THETA, C0, S_); qc.cry(2 * THETA, C1, S_); qc.barrier()
    for k in range(NREAD):
        if arm == 'M': qc.measure(E, regs[k])
        else:
            for q in E: qc.delay(L_DT, q, unit='dt')
        qc.barrier()
    for q, b in zip((C0, C1, S_), st): rot(qc, q, b)
    qc.measure(C0, fin[0]); qc.measure(C1, fin[1]); qc.measure(S_, fin[2])
    return qc
s = service(); b = s.backend(CHIP); n = b.num_qubits
keys = [(arm, st) for st in SETTINGS for arm in ('M', 'D')]
T = {k: transpile(build(n, *k), b, optimization_level=1, initial_layout=list(range(n)), seed_transpiler=24) for k in keys}
for k, t in T.items():
    assert t.layout is None or list(t.layout.final_index_layout()) == list(range(n)), ('layout moved', k)
    assert t.count_ops().get('cz', 0) == 4, ('cz count', k, t.count_ops().get('cz'))
dur = {}
for k in [('M', 'XXX'), ('D', 'XXX'), ('M', 'ZZZ'), ('D', 'ZZZ')]:
    sc = transpile(T[k], b, optimization_level=0, scheduling_method='alap', initial_layout=list(range(n)))
    dur[f'{k[0]}_{k[1]}'] = {q: sc.qubit_duration(q) for q in (C0, C1, S_)}
eq = all(dur[f'M_{x}'] == dur[f'D_{x}'] for x in ('XXX', 'ZZZ'))
rem = s.usage().get('usage_remaining_seconds'); est = round(2 * len(keys) * SHOTS * 0.34e-3 + 6)
print(f'{CHIP}: c0,s,c1 = {C0},{S_},{C1}; {len(keys)} circuits per job x 2 jobs x {SHOTS} shots; cz per circuit 4; '
      f'scheduled durations on c0,c1,s (dt) {json.dumps(dur)} -> equal M vs D: {eq}; est {est} s (cap {CAP}), remaining {rem}, reserve {RESERVE}', flush=True)
assert eq, 'M and D durations differ on the history qubits: STOP'
if '--fire' not in sys.argv: sys.exit(0)
if est > CAP or rem is None or rem - est < RESERVE: print('STOP: over cap or would cut the reserve for the queued free runs'); sys.exit(1)
p = b.properties(refresh=True)
for q in (C0, C1, S_):
    ro = p.readout_error(q); assert ro < 0.05, f'HOLD: q{q} readout_error {ro} >= 0.05 in today\'s record'
for e in ((C0, S_), (S_, C1)):
    ge = p.gate_error('cz', list(e)); assert ge < 0.01, f'HOLD: cz {e} gate_error {ge} >= 0.01'
from qiskit_ibm_runtime import SamplerV2
circs = [T[k] for k in keys]; qpy.dump(circs, open(f'{HERE}/circuits_pooters.qpy', 'wb'))
chash = hashlib.sha256(open(f'{HERE}/circuits_pooters.qpy', 'rb').read()).hexdigest()
rec = dict(chip=CHIP, shots=SHOTS, layout=[C0, C1, S_], layout_note='layout list order = c0, c1, s', E=E, keys=keys, circuit_hash=chash,
           durations_dt=dur, jobs=[], dd='off (SamplerV2 default; set explicitly)', twirling='off')
ORDER = {'J1': list(range(len(keys))), 'J2': [i for st in reversed(SETTINGS) for i in (keys.index(('D', st)), keys.index(('M', st)))]}
spent = 0
for J, order in ORDER.items():
    for attempt in (1, 2):
        json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_pooters_before_{J}' + ('' if attempt == 1 else '_retry') + '.json', 'w'), default=str)
        json.dump(dict(rec, next=J), open(f'{HERE}/job_pooters.json', 'w'), default=str)
        smp = SamplerV2(mode=b); smp.options.dynamical_decoupling.enable = False; smp.options.twirling.enable_gates = False; smp.options.twirling.enable_measure = False
        job = smp.run([circs[i] for i in order], shots=SHOTS); sub = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        print(f'SUBMITTED {J} attempt {attempt} job {job.job_id()} {sub}', flush=True)
        try:
            res = job.result(); break
        except Exception as ex:
            m = job.metrics(); u = (m.get('usage') or {}).get('qpu_charge_time_seconds') or 0; spent += u
            rec['jobs'].append(dict(label=J, attempt=attempt, job_id=job.job_id(), submitted_utc=sub, status='ERROR', error=str(ex)[:200], usage=m.get('usage')))
            json.dump(rec, open(f'{HERE}/job_pooters.json', 'w'), default=str); print(f'ERROR {J} attempt {attempt}: {str(ex)[:160]}', flush=True)
            if attempt == 2: print('HOLD: second IBM-side failure; not refired', flush=True); sys.exit(2)
    ents = [dict(arm=keys[i][0], setting=keys[i][1], counts={str(k): int(v) for k, v in pr.data.fin.get_counts().items()}) for i, pr in zip(order, res)]
    json.dump(ents, open(f'{HERE}/raw_pooters_{J}.json', 'w'))
    shots = {}
    for i, pr in zip(order, res):   # per-shot bitstrings, aligned across registers: fin (s c1 c0) and, in arm M, the pack's 4 readouts
        tag = f'{keys[i][0]}_{keys[i][1]}'; shots[f'fin_{tag}'] = np.array(pr.data.fin.get_bitstrings())
        if keys[i][0] == 'M':
            for k in range(NREAD): shots[f'm{k}_{tag}'] = np.array(getattr(pr.data, f'm{k}').get_bitstrings())
    np.savez_compressed(f'{HERE}/shots_pooters_{J}.npz', **shots)
    m = job.metrics(); u = (m.get('usage') or {}).get('qpu_charge_time_seconds') or 0; spent += u
    rec['jobs'].append(dict(label=J, attempt=attempt, job_id=job.job_id(), submitted_utc=sub, usage=m.get('usage'), timestamps=m.get('timestamps')))
    json.dump(rec, open(f'{HERE}/job_pooters.json', 'w'), default=str); print(f'DONE {J} usage {u} s (total {spent})', flush=True)
json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_pooters_after.json', 'w'), default=str)
print('ALL DONE', spent, 's', flush=True)
