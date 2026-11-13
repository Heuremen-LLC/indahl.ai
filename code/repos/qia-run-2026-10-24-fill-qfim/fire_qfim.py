"""fire_qfim.py -- the free calibration run for QFIM-bench (Vellore Institute of Technology) on ibm_marrakesh (Darkwave Disco, via sweep_run/sweep.py's service()).
Design (fixed before any job, PLAN_QFIM.md.text): their Tier A job = 8 circuits (ladder r0..r4, echo, readout zeros, readout ones; n=3, M=1, marked state = first weight-2
basis state, uniform start, matched diffusion, mcz oracle), rebuilt from their published construction (theirs/src/circuit.py, ladder_predictions.py) WITHOUT running their code,
transpiled ONCE (optimization_level=3, seed_transpiler=42 as theirs; physical qubits [5,6,7] for ladder/echo and [6,98,153] for readout and r0 as in their manifest; among the
orderings of those qubits the one whose depth and two-qubit count are nearest their published ones for that circuit is used (exact match if any); recorded. Today's compiler is not
theirs (qiskit 2.5.2 vs their 2.1.2), so five of the eight differ slightly; the compile is fixed once and identical in all four jobs), 8192 shots per circuit,
dynamical decoupling XpXm as theirs, and sent unchanged in four jobs, order ABBA:
  A1 (their day-1 circuit order) | B1 (reversed) | B2 (reversed) | A2 (their day-1 order)
Each job is submitted after the previous finishes; the backend record (properties), the remaining seconds and the planned job are saved BEFORE every job. Layout saved.
Usage: fire_qfim.py            (dry run: prints layout, estimate, remaining seconds; submits nothing)
       fire_qfim.py --fire"""
import json, sys, time, hashlib, itertools, os
sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
from sweep import service
from qiskit import QuantumCircuit, transpile, qpy
HERE = __file__.rsplit('/', 1)[0] or '.'; CHIP = 'ibm_kingston'; SHOTS = 8192; CAP = 300; MAXEXEC = 40
A_ORDER = ['ladder_n3_M1_r2', 'ladder_n3_M1_r1', 'readout_n3_zeros', 'ladder_n3_M1_r4', 'echo_n3_M1_r2', 'ladder_n3_M1_r3', 'readout_n3_ones', 'ladder_n3_M1_r0']   # their day 1
B_ORDER = A_ORDER[::-1]
PLAN = [('A1', A_ORDER, 20), ('B1', B_ORDER, 20), ('B2', B_ORDER, 20), ('A2', A_ORDER, 20)]   # (label, circuit order, estimated QPU s; logged 20.0 s per job of theirs)
EST = sum(p[2] for p in PLAN); N = 3
def flip_all_ones(qc):
    qc.h(N - 1); qc.mcx(list(range(N - 1)), N - 1); qc.h(N - 1)
def body(r, M=1):
    marked = [i for i in range(2 ** N) if bin(i).count('1') == 2][:M]
    qc = QuantumCircuit(N); qc.h(range(N))
    for _ in range(r):
        for i in sorted(marked):
            z = [p for p in range(N) if not (i >> p) & 1]
            for p in z: qc.x(p)
            flip_all_ones(qc)
            for p in z: qc.x(p)
        qc.h(range(N)); qc.x(range(N)); flip_all_ones(qc); qc.x(range(N)); qc.h(range(N))
    return qc
def circuit_for(cid):
    kind = cid.split('_')[0]
    if kind == 'ladder':
        qc = QuantumCircuit(N, N); qc.compose(body(int(cid.split('_')[3][1:])), inplace=True); qc.measure(range(N), range(N)); return qc
    if kind == 'echo':
        b = body(int(cid.split('_')[3][1:])); qc = QuantumCircuit(N, N); qc.compose(b, inplace=True); qc.barrier(); qc.compose(b.inverse(), inplace=True); qc.measure(range(N), range(N)); return qc
    qc = QuantumCircuit(N, N)
    if cid.endswith('ones'): qc.x(range(N))
    qc.measure(range(N), range(N)); return qc
man = json.load(open(f'{HERE}/theirs/manifest.json'))
day1 = next(j for j in man['jobs'] if j['label'] == 'tierA_day1')
PUB = {lab: ci for lab, ci in zip(day1['labels'], day1['circuits_info'])}     # their depth, two_qubit_gates, physical_qubits per circuit id
def two_q(t): return sum(v for k, v in t.count_ops().items() if k in ('cz', 'ecr', 'cx'))
if __name__ == '__main__':
    s = service(); b = s.backend(CHIP); tq, tinfo, matched = {}, {}, {}
    for cid in A_ORDER:
        want = PUB[cid]; qs = want['physical_qubits']; cand = []
        for perm in itertools.permutations(qs):
            t = transpile(circuit_for(cid), b, optimization_level=3, seed_transpiler=42, initial_layout=list(perm)); cand.append((perm, t))
        gap = [(abs(two_q(t) - want['two_qubit_gates']), abs(t.depth() - want['depth'])) for _, t in cand]   # exact (0, 0) wins, else the nearest by (2Q gap, depth gap)
        best = min(range(len(cand)), key=lambda i: gap[i]); pick = best if gap[best] == (0, 0) else None
        perm, t = cand[best]; tq[cid] = t; matched[cid] = pick is not None
        tinfo[cid] = dict(layout=list(perm), depth=t.depth(), two_q=two_q(t), his_depth=want['depth'], his_two_q=want['two_qubit_gates'], reproduces_his=pick is not None)
    used = sorted({tuple(sorted({t.find_bit(q).index for ins in t.data for q in ins.qubits})) for t in tq.values()}); rem = s.usage().get('usage_remaining_seconds')
    print(f'{CHIP}: 8 circuits (their Tier A), {SHOTS} shots, 4 jobs A1 B1 B2 A2, physical qubits {used}, depth and 2Q count both equal to his transpile in {sum(matched.values())}/8, 2Q count equal in {sum(v["two_q"] == v["his_two_q"] for v in tinfo.values())}/8, '
          f'est {EST} s (cap {CAP}), remaining {rem}', flush=True)
    for cid in A_ORDER: print('  ', cid, tinfo[cid])
    if '--fire' not in sys.argv: sys.exit(0)
    from qiskit_ibm_runtime import SamplerV2
    qpy.dump([tq[c] for c in A_ORDER], open(f'{HERE}/circuits_qfim.qpy', 'wb')); chash = hashlib.sha256(open(f'{HERE}/circuits_qfim.qpy', 'rb').read()).hexdigest()
    rec = dict(chip=CHIP, shots=SHOTS, circuits=tinfo, circuit_order_in_qpy=A_ORDER, circuit_hash=chash, planned=[p[0] for p in PLAN], jobs=[]); spent = 0
    for label, order, est in PLAN:
        rem = s.usage().get('usage_remaining_seconds')                                  # remaining seconds checked before EVERY job
        if spent + est > CAP: print(f'STOP: {spent} s spent + {est} s next > cap {CAP}'); break
        if rem is not None and rem < est + 30: print(f'STOP: remaining {rem} s < {est} + 30'); break
        json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_qfim_before_{label}.json', 'w'), default=str)
        json.dump(dict(rec, next=label, remaining_before=rem), open(f'{HERE}/job_qfim.json', 'w'), default=str)
        smp = SamplerV2(mode=b); smp.options.dynamical_decoupling.enable = True; smp.options.dynamical_decoupling.sequence_type = 'XpXm'; smp.options.max_execution_time = MAXEXEC
        job = smp.run([tq[c] for c in order], shots=SHOTS)
        sub = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()); print(f'SUBMITTED job {label} {job.job_id()} {sub} (remaining before {rem})', flush=True)
        res = job.result(); raw = {c: {str(k): int(v) for k, v in pr.data.c.get_counts().items()} for c, pr in zip(order, res)}
        json.dump(raw, open(f'{HERE}/raw_qfim_{label}.json', 'w'))
        m = job.metrics(); u = (m.get('usage') or {}).get('quantum_seconds') or (m.get('usage') or {}).get('qpu_charge_time_seconds') or est; spent += u
        rec['jobs'].append(dict(label=label, order=order, job_id=job.job_id(), submitted_utc=sub, usage=m.get('usage'), timestamps=m.get('timestamps')))
        json.dump(rec, open(f'{HERE}/job_qfim.json', 'w'), default=str)
        print(f'DONE job {label} usage {u} s (total {spent})', flush=True)
    json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_qfim_after.json', 'w'), default=str)
    print('ALL DONE', spent, 's', flush=True)
