"""fire_zhukov.py -- the free calibration run for A. Zhukov (independent), arXiv 2609.15411v2, on ibm_kingston (Darkwave Disco, via sweep_run/sweep.py's service()).
Design (fixed before any job, PLAN_ZHUKOV.md.text): set S = 86 circuits = 76 of HIS (raw/003 control block 68 + raw/005 chain-C Jt=4/3 coherence 8), loaded from his circuits.qpy as DATA and
sent UNCHANGED on HIS physical qubits (lane paths [16,3,2] [21,36,41] [96,103,104] [69,68,67] [129,118,109] [38,49,50]; his code and raw/*/source never executed), plus 10 of OURS: on qubit 16
(MM0 MM1: prepare 0 / 1 and measure twice back to back; DLY0 DLY1: prepare 0 / 1, idle 100 us, measure; two copies each) and the MM control on qubit 3 (MMC: prepare 0, measure twice; two copies). Options as his runtime_options: 1024 shots, init_qubits True,
rep_delay 250 us, classified, DD off, twirling off. Four jobs, order ABBA: A1 (his order, then ours) | B1 (reversed) | B2 (reversed) | A2. Each job is submitted after the previous
finishes; the backend record (properties), the remaining seconds and the planned job are saved BEFORE every job (props_zhukov_before_<job>.json, job_zhukov.json), the raw shots right after
(raw_zhukov_<job>.npz). If the layout no longer exists on kingston (a used qubit faulty or an edge missing from the coupling map), nothing is sent: BLOCKED.
Usage: fire_zhukov.py            (dry run: prints layout check, estimate, remaining seconds; submits nothing)
       fire_zhukov.py --fire"""
import json, sys, time, hashlib, os
sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
import numpy as np
from sweep import service
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, qpy
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import zhukov as Z
CHIP = 'ibm_kingston'; SHOTS = 1024; CAP = 150; MAXEXEC = 60; PER_CIRC = 0.285          # logged s per 1024-shot circuit on his three jobs: 0.28-0.29
SET24 = '531953a6d9de8abf8ab44a90db28f8519dcb465b977f643182fd90c5b6536a3e'   # 24 Oct circuit_hash
HIS_RAW_24OCT = '/private/tmp/claude-501/-Users-heuremen/80087010-0cb3-4ae5-9e13-362e6d5086ad/scratchpad/dl_q3/2609.15411/data/IBM_DM_data_v2/raw'
QPY = {'003': 'e8ba5532bc4e588348e8626e8612ae3da18a09c7682215960fb407f560bedcd7', '005': '6c076f81aaa4d35453bd0a399177248d7d6aa1dc454411f44799a8b5f13bb67e'}   # sha256 of his circuits.qpy
PLAN = [('A1', Z.A_ORDER), ('B1', Z.B_ORDER), ('B2', Z.B_ORDER), ('A2', Z.A_ORDER)]
EST = round(len(PLAN) * Z.NC * PER_CIRC)

def decode(v):            # BitArray value of a 3-bit register (clbit j <- path[j]) -> code with x1 = path[0] = MSB
    v = v.astype(np.uint8); return ((v & 1) << 2) | (v & 2) | ((v >> 2) & 1)
def load_set():
    """29 Oct repeat: the exact 86 circuits sent on 24 Oct (qia_runs/2026-10-24-fill-zhukov/circuits_zhukov.qpy), hash asserted against that run's job record."""
    f = os.path.expanduser('~/bones-forge/qia_runs/2026-10-24-fill-zhukov/circuits_zhukov.qpy'); raw = open(f, 'rb').read()
    assert hashlib.sha256(raw).hexdigest() == SET24, 'the 24 Oct circuit set changed'
    import io; circs = qpy.load(io.BytesIO(raw)); assert len(circs) == Z.NC
    for i, c in enumerate(Z.SET):
        if c['src'] != 'X': assert circs[i].metadata['pub_index'] == c['row'] and circs[i].metadata['spec'] == c['spec'], ('spec mismatch', i)
    return circs

def layout_check(b, circs):
    """BLOCKED unless every physical qubit his circuits touch is non-faulty on kingston today, every two-qubit gate sits on a coupling-map edge, and every op is in the target."""
    t = b.target; props = b.properties(refresh=True); faulty = set(props.faulty_qubits()); used = set(); edges = set(); bad = []; ops = set()
    cmap = set(map(tuple, b.coupling_map.get_edges()))
    for i, qc in enumerate(circs):
        for ins in qc.data:
            n = ins.operation.name; qs = tuple(qc.find_bit(x).index for x in ins.qubits)
            if n == 'barrier': used.update(qs); continue
            ops.add(n); used.update(qs)
            if n not in t.operation_names: bad.append(f'{Z.SETID[i]}: op {n} not in target')
            if len(qs) == 2: edges.add(qs)
    for e in sorted(edges):
        if e not in cmap: bad.append(f'edge {e} not in coupling map')
    for q in sorted(used & faulty): bad.append(f'qubit {q} faulty')
    return sorted(used), len(edges), sorted(ops), bad
def selftest_decode():
    from qiskit.primitives.containers import BitArray
    ba = BitArray.from_counts({'001': 7, '100': 3}, num_bits=3); v = ba.array[:, 0]; c = decode(v)
    assert sorted(set(c.tolist())) == [1, 4] and int((c == 4).sum()) == 7, 'decode: clbit0 (= q16 = x1) must be the MSB of the code'
    return True
if __name__ == '__main__':
    s = service(); b = s.backend(CHIP); circs = load_set(); selftest_decode(); st = b.status()
    used, ne, ops, bad = layout_check(b, circs); rem = s.usage().get('usage_remaining_seconds')
    paths = sorted({q for p in Z.PATH.values() for q in p})
    blocked = (not st.operational) or bad or not set(paths) <= set(used)
    print(f'{CHIP}: {Z.NC} circuits (76 his + 10 ours), {SHOTS} shots, 4 jobs A1 B1 B2 A2, physical qubits {len(used)} {used}, {ne} directed two-qubit edges, ops {ops}, operational {st.operational}, '
          f'layout {"BLOCKED: " + "; ".join(bad[:5]) if blocked else "available on kingston today"}, est {EST} s (cap {CAP}), remaining {rem}', flush=True)
    for lane, p in Z.PATH.items(): print('   lane', lane, p)
    if blocked: sys.exit(2)
    if '--fire' not in sys.argv: sys.exit(0)
    from qiskit_ibm_runtime import SamplerV2
    qpy.dump(circs, open(f'{HERE}/circuits_zhukov.qpy', 'wb')); chash = hashlib.sha256(open(f'{HERE}/circuits_zhukov.qpy', 'rb').read()).hexdigest()
    rec = dict(chip=CHIP, shots=SHOTS, set_ids=Z.SETID, circuit_hash=chash, his_qpy_sha256=QPY, planned=[p[0] for p in PLAN], jobs=[]); spent = 0
    for label, order in PLAN:
        est = Z.NC * PER_CIRC; rem = s.usage().get('usage_remaining_seconds')                       # remaining seconds checked before EVERY job
        if spent + est > CAP: print(f'STOP: {spent} s spent + {est:.0f} s next > cap {CAP}'); break
        if rem is not None and rem < est + 30: print(f'STOP: remaining {rem} s < {est:.0f} + 30'); break
        json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_zhukov_before_{label}.json', 'w'), default=str)
        json.dump(dict(rec, next=label, remaining_before=rem), open(f'{HERE}/job_zhukov.json', 'w'), default=str)
        smp = SamplerV2(mode=b); o = smp.options; o.max_execution_time = MAXEXEC; o.dynamical_decoupling.enable = False; o.environment.job_tags = ['qia-repeat-zhukov-20261029']
        o.twirling.enable_gates = False; o.twirling.enable_measure = False; o.execution.init_qubits = True; o.execution.rep_delay = 0.00025; o.execution.meas_type = 'classified'
        job = smp.run([circs[i] for i in order], shots=SHOTS)
        sub = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()); print(f'SUBMITTED job {label} {job.job_id()} {sub} (remaining before {rem})', flush=True)
        res = job.result(); codes = np.full((Z.NC, SHOTS, 6), 255, np.uint8)
        for i, pr in zip(order, res):
            c = Z.SET[i]
            if c['src'] == 'X':
                nm = c['spec']['name']
                if nm.startswith('MM'): codes[i, :, 0] = pr.data.m0.array[:, 0].astype(np.uint8) | (pr.data.m1.array[:, 0].astype(np.uint8) << 1)
                else: codes[i, :, 0] = pr.data.d0.array[:, 0].astype(np.uint8)
            else:
                for k, lane in enumerate(Z.LANES):
                    if lane in c['lanes']: codes[i, :, k] = decode(getattr(pr.data, f't{lane}').array[:, 0])
        np.savez_compressed(f'{HERE}/raw_zhukov_{label}.npz', codes=codes)
        m = job.metrics(); u = (m.get('usage') or {}).get('quantum_seconds') or (m.get('usage') or {}).get('qpu_charge_time_seconds') or est; spent += u
        rec['jobs'].append(dict(label=label, order=order, job_id=job.job_id(), submitted_utc=sub, usage=m.get('usage'), timestamps=m.get('timestamps')))
        json.dump(rec, open(f'{HERE}/job_zhukov.json', 'w'), default=str)
        print(f'DONE job {label} usage {u} s (total {spent})', flush=True)
    json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_zhukov_after.json', 'w'), default=str)
    print('ALL DONE', spent, 's', flush=True)
