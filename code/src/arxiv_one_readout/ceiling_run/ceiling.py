"""ceiling.py -- the ceiling run: how far below the forecast built from IBM's published figures can a workload's success fall, when the
workload is built on purpose to stack every effect we have measured (PLAN_CEILING.md). Built to find the largest gap, and said so.
Workload: 10 data qubits on the best line by IBM's figures (demo.best), the QAOA-shaped U of the Portfolio Run, then R rounds, then U^-1,
measure the data (correct output all zeros). Every qubit coupled to the line and not on it is an ANCILLA, held in |0>.
  READ-R : each round measures every ancilla mid-circuit (the error-correction pattern: data held while neighbours are read)
  IDLE-R : each round is an idle of exactly the readout's scheduled length on every qubit (the equal idle)
  R in {0, 4, 8, 16}; READ-0 and IDLE-0 are the same circuit (built-in known-good).
FORECAST: Qiskit Aer, NoiseModel.from_backend on IBM's record at firing (gate errors, readout errors, T1/T2 relaxation during gates) plus
RelaxationNoisePass (T1/T2 relaxation during every scheduled idle and delay), on the same compiled, scheduled circuits: the standard
noise-aware forecast a designer builds from IBM's published figures.
  ceiling.py CHIP | --fire CHIP | --fetch CHIP | --analyze CHIP | --synth WORLD"""
import os, sys, json, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); H = os.path.expanduser('~/bones-forge')
sys.path.insert(0, os.path.join(HERE, '..', 'demo_run')); sys.path.insert(0, os.path.join(HERE, '..', 'sweep_run'))
KEYFILE, INSTANCE = '.ibm_quantum_key_3', 'Darkwave Disco'
ROUNDS = [0, 4, 8, 16]; SHOTS = 4000; SIM_SHOTS = 4000

def layout(b, props):
    import demo as D
    n = b.num_qubits; edges = sorted({tuple(sorted(e)) for e in b.coupling_map.get_edges()}); paths = D.lines(edges, n)
    sxc, czc = D.counts_template(b, paths[0]); (pi, line), _ = D.best(paths, sxc, czc, *D.ibm_errors(props))
    adj = {q: set() for q in range(n)}
    for a, c in edges: adj[a].add(c); adj[c].add(a)
    anc = sorted({v for q in line for v in adj[q] if v not in line})
    return list(line), anc

def build(line, anc, mlen_us, R, arm):
    import demo as D
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    nd, na = len(line), len(anc); u = D.workload().remove_final_measurements(inplace=False)
    uu = u.copy(); 
    # D.workload() = [U, barrier, U^-1, barrier, measure]; take U as the first half of its gates
    from qiskit import QuantumCircuit as QC
    U = QC(nd); half = []
    for ins in D.workload().data:
        if ins.operation.name == 'barrier': break
        half.append(ins)
    for ins in half: U.append(ins.operation, [U.qubits[D.workload().find_bit(q).index] for q in ins.qubits])
    q = QuantumRegister(nd + na, 'q'); c = ClassicalRegister(nd, 'c'); regs = [q, c]
    m = ClassicalRegister(max(1, na * R), 'm'); regs.append(m)
    qc = QuantumCircuit(*regs); D_ = list(range(nd)); A_ = list(range(nd, nd + na))
    qc.compose(U, D_, inplace=True); qc.barrier()
    for r in range(R):
        if arm == 'READ': qc.measure(A_, [m[r * na + k] for k in range(na)])
        else: qc.delay(mlen_us, list(range(nd + na)), unit='us')
        qc.barrier()
    qc.compose(U.inverse(), D_, inplace=True); qc.barrier(); qc.measure(D_, c)
    return qc

def compiled(b, line, anc, plant_kick_deg=0.0):
    from qiskit import transpile
    mlen = b.target['measure'][(anc[0],)].duration * 1e6
    items = []
    for R in ROUNDS:
        for arm in (('READ', 'IDLE') if R else ('READ',)):
            qc = build(line, anc, mlen, R, arm)
            if plant_kick_deg and arm == 'READ' and R:   # synthetic only: a per-readout phase on the data qubits, planted after the rounds
                from qiskit import QuantumCircuit
                pos = [i for i, ins in enumerate(qc.data) if ins.operation.name == 'barrier'][R]
                for k in range(len(line)): qc.data.insert(pos, type(qc.data[0])(__import__('qiskit').circuit.library.RZGate(np.deg2rad(plant_kick_deg) * R), [qc.qubits[k]], []))
            t = transpile(qc, b, optimization_level=1, initial_layout=list(line) + list(anc), scheduling_method='alap', seed_transpiler=7)
            items.append((t, dict(arm=arm, R=R)))
    return items, mlen

def forecast(b, items, seed=11, extra_kick=0.0):
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, RelaxationNoisePass
    from qiskit.circuit import Delay
    nm = NoiseModel.from_backend(b, thermal_relaxation=True)
    props = b.properties(); n = b.num_qubits
    def get(fn, q):
        try: v = fn(q); return v if v and v > 0 else None
        except Exception: return None
    t1r = [get(props.t1, q) for q in range(n)]; t2r = [get(props.t2, q) for q in range(n)]
    m1 = float(np.median([v for v in t1r if v])); m2 = float(np.median([v for v in t2r if v]))
    forecast.missing = {'T1': [q for q in range(n) if t1r[q] is None], 'T2': [q for q in range(n) if t2r[q] is None]}
    t1 = [v or m1 for v in t1r]; t2 = [min(v or m2, 2 * t1[q]) for q, v in enumerate(t2r)]   # a hole in IBM's record takes the chip median
    rp = RelaxationNoisePass(t1s=t1, t2s=t2, dt=b.dt, op_types=[Delay])
    sim = AerSimulator(noise_model=nm, method='automatic'); out = []
    for t, m in items:
        tt = rp(t); r = sim.run(tt, shots=SIM_SHOTS, seed_simulator=seed).result().get_counts()
        cdata = {}
        for k, v in r.items():
            key = k.split(' ')[-1]; cdata[key] = cdata.get(key, 0) + v
        out.append(cdata.get('0' * len(next(iter(cdata))), 0) / SIM_SHOTS)
    return out

def service():
    from qiskit_ibm_runtime import QiskitRuntimeService
    tok = open(H + '/' + KEYFILE).read().strip(); s = QiskitRuntimeService(channel='ibm_quantum_platform', token=tok)
    crn = [i['crn'] for i in s.instances() if i.get('name') == INSTANCE][0]
    return QiskitRuntimeService(channel='ibm_quantum_platform', token=tok, instance=crn)

def readings(meta, succ, fc, label):
    rng = np.random.default_rng(9); res = {}
    print(f'-- {label}')
    for i, m in enumerate(meta):
        if m.get('copy', 0): continue
    arms = {}
    for i, m in enumerate(meta): arms.setdefault((m['arm'], m['R']), []).append(i)
    for (arm, R), idx in sorted(arms.items(), key=lambda x: (x[0][1], x[0][0])):
        x = np.concatenate([succ[i] for i in idx]); f = np.mean([fc[i] for i in idx]); d = x.mean()
        bs = [rng.choice(x, len(x)).mean() for _ in range(4000)]; lo, hi = np.percentile(bs, [2.5, 97.5])
        o = 'BELOW' if hi < f else 'ABOVE' if lo > f else 'CONSISTENT'; res[(arm, R)] = (d, lo, hi, f, o)
        cp = [succ[i].mean() for i in idx]
        print(f'   {arm}-{R:<2} delivered {d:.4f} [{lo:.4f}, {hi:.4f}] (copies {", ".join(f"{v:.4f}" for v in cp)}) | forecast {f:.4f} | delivered/forecast {d / f:.3f} -> {o}')
    for R in ROUNDS[1:]:
        a, bb = res[('READ', R)], res[('IDLE', R)]
        k = (a[0] / a[3]) / (bb[0] / bb[3]); print(f'   R={R:<2} readout-only share: (READ delivered/forecast) / (IDLE delivered/forecast) = {k:.3f}')
    return res

def synth(world):
    """planted: the 'hardware' is the forecast model itself (null) or the forecast model plus a planted per-readout phase on the data qubits
    (kick) -- read by the same readings. Runs on the live backend's map and record; no job is submitted."""
    s = service(); b = s.backend('ibm_kingston'); props = b.properties().to_dict(); line, anc = layout(b, props)
    items, mlen = compiled(b, line, anc); fc = forecast(b, items)
    kick = {'null': 0.0, 'kick': 2.0}[world]
    hw_items, _ = compiled(b, line, anc, plant_kick_deg=kick)
    hw = forecast(b, hw_items, seed=29)
    rng = np.random.default_rng(5)
    meta, succ, f2 = [], [], []
    for (t, m), p, f in zip(items, hw, fc):
        for cp in (0, 1): meta.append(dict(m, copy=cp)); succ.append((rng.random(SHOTS) < p).astype(float)); f2.append(f)
    readings(meta, succ, f2, f'synth {world} (line {line}, {len(anc)} ancillas, planted kick {kick} deg per readout)')

if __name__ == '__main__':
    a = sys.argv
    if '--synth' in a: synth(a[a.index('--synth') + 1]); sys.exit(0)
    CHIP = a[-1]; FIRE = '--fire' in a
    if '--fetch' in a:
        rec = json.load(open(f'{HERE}/job_ceiling_{CHIP}.json')); res = service().job(rec['job_id']).result()
        np.savez_compressed(f'{HERE}/raw_ceiling_{CHIP}.npz', **{f'c_{i}': pr.data.c.to_bool_array(order='little') for i, pr in enumerate(res)}); print('saved', CHIP); sys.exit(0)
    if '--analyze' in a:
        rec = json.load(open(f'{HERE}/job_ceiling_{CHIP}.json')); z = np.load(f'{HERE}/raw_ceiling_{CHIP}.npz')
        succ = [(~z[f'c_{i}'].any(axis=1)).astype(float) for i in range(len(rec['meta']))]
        print(f'=== {CHIP} job {rec["job_id"]} | line {rec["line"]} | {len(rec["anc"])} ancillas | readout {rec["mlen_us"]:.3f} us')
        readings(rec['meta'], succ, rec['forecast'], CHIP); sys.exit(0)
    s = service(); b = s.backend(CHIP); props = b.properties().to_dict(); line, anc = layout(b, props)
    items, mlen = compiled(b, line, anc); fc = forecast(b, items)
    print(f'{CHIP}: line {line}, ancillas {anc} ({len(anc)}), readout {mlen:.3f} us | IBM record holes (chip median used): {forecast.missing}')
    for (t, m), f in zip(items, fc): print(f'   {m["arm"]}-{m["R"]}: forecast success {f:.4f}, duration {t.estimate_duration(b.target, "s") * 1e6:.1f} us, ops {dict((k, v) for k, v in t.count_ops().items() if k in ("cz", "sx", "measure", "delay"))}')
    pubs, meta, fcs = [], [], []
    for (t, m), f in zip(items, fc):
        for cp in (0, 1): pubs.append(t); meta.append(dict(m, copy=cp)); fcs.append(f)
    dur = np.array([t.estimate_duration(b.target, 's') for t in pubs]); est = float(SHOTS * np.sum(dur + 290e-6)); rem = s.usage().get('usage_remaining_seconds')
    print(f'   {len(pubs)} circuits, ESTIMATED {est:.0f} s, remaining {rem}')
    if not FIRE: sys.exit(0)
    if rem is not None and rem < est + 10: print('STOP: not enough seconds'); sys.exit(1)
    from qiskit_ibm_runtime import SamplerV2
    json.dump(props, open(f'{HERE}/props_ceiling_{CHIP}.json', 'w'), default=str)
    job = SamplerV2(mode=b).run(pubs, shots=SHOTS)
    json.dump(dict(chip=CHIP, job_id=job.job_id(), submitted_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), meta=meta, forecast=fcs, line=line, anc=anc, mlen_us=mlen), open(f'{HERE}/job_ceiling_{CHIP}.json', 'w'))
    print('SUBMITTED', CHIP, job.job_id(), flush=True)
