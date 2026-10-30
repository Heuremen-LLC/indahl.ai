"""fire_lima.py -- the free calibration run for arXiv:2605.08251 on ibm_marrakesh (Darkwave Disco, via sweep_run/sweep.py's service()).
Design (fixed before any job, PLAN_LIMA.md.text): the author's 10 QAOA MaxCut graphs (seeds 606..1506, n=5, p=1, gamma 0.8, beta 0.6, edges from his seeded
random_graph_edges) at noise scales 1 and 3, built from his published construction (theirs/src/circuits.py, folding.py: canonicalise to rx/rz/cx, fold every gate
G -> G G^dag G for scale 3, which is what his fold_gates_at_random does at an integer scale) WITHOUT running his code, transpiled ONCE
(optimization_level=0 as his runner; routing seed per circuit = first of 24..83 that reproduces his published gate counts for it, else 24; recorded) and sent unchanged in six jobs, 4000 shots per circuit (his count), order ABBA over arms:
  P1 (both scales, 20 circuits) | S1a (l=1, 10) S1b (l=3, 10) | S2a (l=3, 10) S2b (l=1, 10) | P2 (both scales, 20)
Each job is submitted after the previous finishes; the backend record (properties) and the planned job are saved BEFORE every job. Layout saved.
Usage: fire_lima.py            (dry run: prints layout, estimate, remaining seconds; submits nothing)
       fire_lima.py --fire"""
import json, sys, time, gzip, glob, hashlib
import numpy as np
sys.path.insert(0, __import__('os').path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
from sweep import service
from qiskit import QuantumCircuit, transpile, qpy
HERE = __file__.rsplit('/', 1)[0] or '.'; CHIP = 'ibm_fez'; SHOTS = 4000; CAP = 300
SEEDS = [606, 707, 808, 909, 1001, 1102, 1203, 1304, 1405, 1506]
PLAN = [('P1', (1, 3), 27), ('S1a', (1,), 14), ('S1b', (3,), 14), ('S2a', (3,), 14), ('S2b', (1,), 14), ('P2', (1, 3), 27)]   # (label, scales, estimated QPU s; his 20-circuit job billed 27 s)
EST = sum(p[2] for p in PLAN)
def edges_of(seed, n=5, p=0.5):
    rng = np.random.default_rng(seed); return [(u, v) for u in range(n) for v in range(u + 1, n) if rng.random() < p]   # his random_graph_edges
def qaoa(n, E):
    c = QuantumCircuit(n, n)
    for q in range(n): c.h(q)
    for u, v in E: c.rzz(0.8, u, v)
    for q in range(n): c.rx(2.0 * 0.6, q)
    c.measure(range(n), range(n)); return c
def fold3(c):
    out = QuantumCircuit(*c.qregs, *c.cregs)
    for ins in c.data:
        op = ins.operation
        if op.name in ('measure', 'barrier'): out.append(op, ins.qubits, ins.clbits); continue
        out.append(op, ins.qubits); out.append(op.inverse(), ins.qubits); out.append(op, ins.qubits)
    return out
def build():
    circs = []
    for s in SEEDS:
        base = transpile(qaoa(5, edges_of(s)), basis_gates=['rx', 'rz', 'cx', 'measure'], optimization_level=0)
        circs += [(s, 1, base), (s, 3, fold3(base))]
    return circs
s = service(); b = s.backend(CHIP); CI = build()
def his_counts(sd, l):
    m = json.loads(gzip.open(glob.glob(f'{HERE}/theirs/raw/*seed_{sd}_n5_r1_lambda_{l}_ibm_marrakesh_4000.json.gz')[0]).read())['metadata']['transpiled_metrics']['operation_counts']
    return {k: v for k, v in m.items() if k != 'measure'}
def same(t, want): return {k: v for k, v in t.count_ops().items() if k != 'measure'} == want
tq, tseed, theirs = [], {}, {}
for sd, l, c in CI:   # his runner left routing unseeded; the first seed 24..83 that reproduces his gate counts for this circuit is used (fixed, recorded), else 24
    want = his_counts(sd, l); cand = [transpile(c, b, optimization_level=0, seed_transpiler=k) for k in range(24, 84)]
    pick = next((i for i, t in enumerate(cand) if same(t, want)), None); theirs[(sd, l)] = pick is not None; tseed[f'{sd}_{l}'] = 24 + (pick or 0); tq.append(cand[pick or 0])
used = sorted({tuple(sorted({t.find_bit(q).index for ins in t.data for q in ins.qubits})) for t in tq}); lay = used; rem = s.usage().get('usage_remaining_seconds')
print(f'{CHIP}: 20 circuits (10 graphs x lambda 1,3), {SHOTS} shots, 6 jobs P1 S1(l1,l3) S2(l3,l1) P2, physical qubits {lay[:2]}{"..." if len(lay) > 2 else ""} ({len(lay)} distinct), '
      f'gate counts equal to his transpile in {sum(theirs.values())}/20, est {EST} s (cap {CAP}), remaining {rem}', flush=True)
if '--fire' not in sys.argv: sys.exit(0)
if EST > CAP or (rem is not None and rem < EST + 30): print('STOP: estimate over cap or not enough seconds'); sys.exit(1)
from qiskit_ibm_runtime import SamplerV2
qpy.dump(tq, open(f'{HERE}/circuits_lima.qpy', 'wb')); chash = hashlib.sha256(open(f'{HERE}/circuits_lima.qpy', 'rb').read()).hexdigest()
rec = dict(chip=CHIP, shots=SHOTS, physical_qubits=[list(l) for l in lay], transpile_seeds=tseed, circuit_hash=chash, planned=[p[0] for p in PLAN], jobs=[]); spent = 0
def counts_of(pr):
    for name in ('meas', 'c'):
        r = getattr(pr.data, name, None)
        if r is not None: return {str(k): int(v) for k, v in r.get_counts().items()}
    raise RuntimeError('no counts register')
for label, lams, est in PLAN:
    if spent + est > CAP: print(f'STOP: {spent} s spent + {est} s next > cap {CAP}'); break
    idx = [i for i, (sd, l, _) in enumerate(CI) if l in lams]; assert [CI[i][1] for i in idx] == ([1, 3] * 10 if lams == (1, 3) else [lams[0]] * 10)
    json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_lima_before_{label}.json', 'w'), default=str)
    json.dump(dict(rec, next=label), open(f'{HERE}/job_lima.json', 'w'), default=str)
    smp = SamplerV2(mode=b); job = smp.run([tq[i] for i in idx], shots=SHOTS)
    sub = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()); print(f'SUBMITTED job {label} {job.job_id()} {sub}', flush=True)
    res = job.result(); ents = [dict(graph_seed=CI[i][0], scale=CI[i][1], counts=counts_of(pr)) for i, pr in zip(idx, res)]
    json.dump(ents, open(f'{HERE}/raw_lima_{label}.json', 'w'))
    m = job.metrics(); u = (m.get('usage') or {}).get('qpu_charge_time_seconds') or est; spent += u
    rec['jobs'].append(dict(label=label, scales=list(lams), job_id=job.job_id(), submitted_utc=sub, usage=m.get('usage'), timestamps=m.get('timestamps')))
    json.dump(rec, open(f'{HERE}/job_lima.json', 'w'), default=str)
    print(f'DONE job {label} usage {u} s (total {spent})', flush=True)
json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_lima_after.json', 'w'), default=str)
print('ALL DONE', spent, 's', flush=True)
