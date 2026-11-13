"""fire_qusoft.py -- the free calibration run for arXiv:2610.20855 (Awuah, Guo; QuSoft / University of Amsterdam) on ibm_kingston (Darkwave Disco, via sweep_run/sweep.py's service()).
Design (fixed before any job, PLAN_QUSOFT.md.text): three of THEIR circuits, rebuilt from their published construction WITHOUT running their code, transpiled ONCE and sent unchanged in four jobs, order ABBA:
  SWAP chain n=21 and n=11 (X on qubit 0, SWAP(k,k+1), measure_all; optimization_level 0, initial_layout = first n qubits of the greedy-DFS line from physical qubit 0 on the coupling map, seed_transpiler 0),
  HP_8 at r*=7 (PauliEvolutionGate, second-order Suzuki-Trotter, t = pi/2, X on qubit 0, measure_all; optimization_level 3, seed_transpiler 0, no layout),
  4096 shots, default Sampler options (no dynamical decoupling, no twirling, no mitigation: theirs).
Inside EVERY job, on the qubits those circuits measure: a readout-string circuit per target (prepare the target bit-string, measure) and sweep.py's isolated-batch two-qubit RB (RB2) on every edge the three
circuits use. A = targets, readout strings, RB batches in that order; B = A reversed. Jobs A1 B1 B2 A2. The backend record, the remaining seconds and the planned job are saved BEFORE every job.
Usage: fire_qusoft.py            (dry run: builds, transpiles, checks, prints the layout, the estimate and the remaining seconds; submits nothing)
       fire_qusoft.py --fire"""
import json, sys, time, hashlib, os, numpy as np
sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
from sweep import service, clifford_table, put, batches, snap
from qiskit import QuantumCircuit, transpile, qpy
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.quantum_info import SparsePauliOp, Clifford, Statevector
from qiskit.synthesis import SuzukiTrotter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import qusoft as Q
CHIP = 'ibm_kingston'; CAP = 250; MAXEXEC = 150; SHOTS = Q.SHOTS; RB_SHOTS = Q.RB_SHOTS; M2 = Q.M2; SEEDS = Q.RB_SEEDS; RB_SEED = 20261024; REP = 290e-6
PLAN_LABELS = ['A1', 'B1', 'B2', 'A2']; THEIR_BILLED = {'chain21': 3, 'chain11': 3, 'hp8': 3}     # QPU seconds billed per job, their Tables 18 and 12

def find_line(b, length):
    """the greedy DFS of their find_heavy_hex_line (swap_chain/hardware_swap_chain_baseline.py), rewritten: neighbours in the iteration order of a set of ints, start qubit 0, 1, ..."""
    adj = {q: set() for q in range(b.num_qubits)}
    for a, c in b.coupling_map.get_edges(): adj[a].add(c); adj[c].add(a)
    def dfs(path):
        if len(path) == length: return path
        for nb in adj[path[-1]]:
            if nb in path: continue
            f = dfs(path + [nb])
            if f is not None: return f
        return None
    for s in range(b.num_qubits):
        r = dfs([s])
        if r is not None: return r
    raise RuntimeError('no line')
def chain_circuit(n):
    qc = QuantumCircuit(n); qc.x(0)
    for k in range(n - 1): qc.swap(k, k + 1)
    qc.measure_all(); return qc
def hp_circuit(n, r, measure=True):
    N = n + 1; terms = []
    for k in range(1, n + 1):
        w = np.sqrt(k * (n - k + 1))
        for P in ('X', 'Y'):
            lab = ['I'] * N; lab[k - 1] = P; lab[k] = P; terms.append((''.join(reversed(lab)), 0.5 * w))
    qc = QuantumCircuit(N); qc.x(0); qc.append(PauliEvolutionGate(SparsePauliOp.from_list(terms), time=np.pi / 2, synthesis=SuzukiTrotter(order=2, reps=r)), range(N))
    if measure: qc.measure_all()
    return qc
def phys_of(isa):
    ph = {}
    for ins in isa.data:
        if ins.operation.name == 'measure': ph[isa.find_bit(ins.clbits[0]).index] = isa.find_bit(ins.qubits[0]).index
    return [ph[i] for i in range(len(ph))]
def cz_pairs(isa):
    w = {}
    for ins in isa.data:
        if ins.operation.num_qubits == 2 and ins.operation.name != 'barrier':
            e = tuple(sorted(isa.find_bit(q).index for q in ins.qubits)); w[e] = w.get(e, 0) + 1
    return w
def readout_circuit(nq, phys):
    N = len(phys); qc = QuantumCircuit(nq, N); qc.x(phys[N - 1])
    for i in range(N): qc.measure(phys[i], i)
    return qc
def rb_circuits(nq, edges, adj, rng):
    """sweep.py's RB2 construction on the given edges: isolated batches (nearest qubits >= 3 links apart), layers of [random 1q Clifford on both qubits, CZ], lengths M2, SEEDS random draws per length,
    then the inverse two-qubit Clifford. Returns [(name, circuit, meta)]."""
    els, ops, mul, inv, pulses = clifford_table(); layer = {}; invcache = {}
    def L(a, b):
        if (a, b) not in layer:
            c2 = QuantumCircuit(2); c2.compose(els[a].to_circuit(), [0], inplace=True); c2.compose(els[b].to_circuit(), [1], inplace=True); c2.cz(0, 1); layer[(a, b)] = Clifford(c2)
        return layer[(a, b)]
    def inv2(c):
        k = c.tableau.tobytes()
        if k not in invcache:
            t = transpile(c.adjoint().to_circuit(), basis_gates=['rz', 'sx', 'cz'], coupling_map=[[0, 1], [1, 0]], optimization_level=1)
            invcache[k] = [(i.operation.name, [t.find_bit(x).index for x in i.qubits], snap(float(i.operation.params[0])) if i.operation.params else None) for i in t.data]
        return invcache[k]
    out = []; eidx = {tuple(e): i for i, e in enumerate(edges)}
    for bi, bat in enumerate(batches(nq, edges, adj)):
        for m in M2:
            for s in range(SEEDS):
                qs = [q for e in bat for q in e]; qc = QuantumCircuit(nq, len(qs)); cur = {e: Clifford(QuantumCircuit(2)) for e in bat}
                for step in range(m):
                    for e in bat:
                        a, b2 = rng.integers(0, 24, 2); put(qc, ops[a], e[0]); put(qc, ops[b2], e[1]); qc.cz(e[0], e[1]); cur[e] = cur[e].compose(L(a, b2))
                    qc.barrier(qs)
                for e in bat:
                    for nm, qq, p in inv2(cur[e]):
                        tq = [e[x] for x in qq]
                        if nm == 'rz': qc.rz(p, tq[0])
                        elif nm == 'sx': qc.sx(tq[0])
                        elif nm == 'cz': qc.cz(tq[0], tq[1])
                qc.barrier(qs); qc.measure(qs, list(range(len(qs))))
                out.append((f'RB_b{bi}_m{m}_s{s}', qc, dict(edge_idx=[eidx[tuple(e)] for e in bat], m=m, seed=s, batch=bi, qubits=qs)))
    return out
def build_all(b):
    nq = b.num_qubits; line = find_line(b, 21); info = {}; isa = {}
    isa['chain21'] = generate_preset_pass_manager(optimization_level=0, backend=b, initial_layout=line[:21], seed_transpiler=0).run(chain_circuit(21))
    isa['chain11'] = generate_preset_pass_manager(optimization_level=0, backend=b, initial_layout=line[:11], seed_transpiler=0).run(chain_circuit(11))
    isa['hp8'] = generate_preset_pass_manager(optimization_level=3, backend=b, seed_transpiler=0).run(hp_circuit(8, 7))
    phys = {c: phys_of(isa[c]) for c in Q.TARGETS}; w = {c: cz_pairs(isa[c]) for c in Q.TARGETS}
    line_edges = [tuple(sorted((line[i], line[i + 1]))) for i in range(20)]
    hp_edges = sorted(e for e in w['hp8'] if e not in line_edges); edges = line_edges + hp_edges
    # every cz of the three circuits must sit on a design edge
    for c in Q.TARGETS: assert all(e in edges for e in w[c]), (c, [e for e in w[c] if e not in edges])
    W = [[w[c].get(tuple(e), 0) for e in edges] for c in Q.TARGETS]
    adj = {q: set() for q in range(nq)}
    for a, c in b.coupling_map.get_edges(): adj[a].add(c); adj[c].add(a)
    rb = rb_circuits(nq, edges, adj, np.random.default_rng(RB_SEED)); lay = list(range(nq))
    ro = {c: transpile(readout_circuit(nq, phys[c]), b, optimization_level=0, initial_layout=lay, seed_transpiler=0) for c in Q.TARGETS}
    rbt = transpile([x[1] for x in rb], b, optimization_level=0, initial_layout=lay, seed_transpiler=7)
    ops0 = sum(sum(x[1].count_ops().values()) for x in rb); ops1 = sum(sum(t.count_ops().values()) for t in rbt)
    names = [f'T_{c}' for c in Q.TARGETS] + [f'R_{c}' for c in Q.TARGETS] + [x[0] for x in rb]
    circ = {**{f'T_{c}': isa[c] for c in Q.TARGETS}, **{f'R_{c}': ro[c] for c in Q.TARGETS}, **{x[0]: t for x, t in zip(rb, rbt)}}
    shots = {n: (SHOTS if n[0] in 'TR' and not n.startswith('RB') else RB_SHOTS) for n in names}
    design = dict(chip=CHIP, line=line, edges=[list(e) for e in edges], W=W, line_idx=list(range(20)), phys=phys, pnl=[1.0, 1.0, Q.pnl_hp(8, 7)],
                  rb_meta={x[0]: x[2] for x in rb}, n2q={c: int(sum(w[c].values())) for c in Q.TARGETS}, depth={c: isa[c].depth() for c in Q.TARGETS}, seeds=dict(chain=0, hp=0, rb_circuits=RB_SEED, rb_transpile=7),
                  rb_shots=RB_SHOTS, rb_seeds=SEEDS, M2=M2, ops_before_after_rb=[ops0, ops1])
    return names, circ, shots, design, isa
def est_seconds(names, circ, shots, b, scale=1.0):
    tot = 0.0
    for n in names:
        c = circ[n]; dur = c.estimate_duration(b.target, 's') if hasattr(c, 'estimate_duration') else 0.0; tot += shots[n] * (dur + REP)
    return tot * scale
def getc(pr):
    reg = 'meas' if hasattr(pr.data, 'meas') else 'c'; return getattr(pr.data, reg).get_counts()

if __name__ == '__main__':
    s = service(); b = s.backend(CHIP); names, circ, shots, design, isa = build_all(b); rem = s.usage().get('usage_remaining_seconds')
    # --- known-good additions that need qiskit (the rest is qusoft.py's R0)
    T = Q.parse_theirs(); t12 = {d['n']: d for d in T['t12']}
    sv = Statevector(hp_circuit(8, 7, measure=False).decompose(reps=3)); pt = abs(sv.data[1 << 8]) ** 2
    print(f'KG3 rebuilt HP_8 (r=7) logical circuit, noiseless statevector target probability {pt:.6f}; their Aer value (Table 12 / 11) {t12[8]["aer"]:.6f} -> {"PASS" if f"{pt:.6f}" == f"{t12[8]["aer"]:.6f}" else "FAIL"}')
    from qiskit_aer import AerSimulator
    sim = AerSimulator(method='stabilizer'); bad = 0; chk = [n for n in names if n.startswith('RB_b0_') and (n.endswith('m30_s0') or n.endswith('m100_s1'))]
    for n in chk:
        r = sim.run(circ[n], shots=64, seed_simulator=3).result().get_counts(); bad += sum(v for k, v in r.items() if set(k) != {'0'})
    print(f'KG4 RB circuits {chk} simulated noiselessly (stabilizer, 64 shots each): {bad} shots with any bit set -> {"PASS" if bad == 0 else "FAIL"}')
    ratio_ok = design['ops_before_after_rb'][0] == design['ops_before_after_rb'][1]
    print(f'{CHIP}: line of 21 (their greedy DFS from qubit 0) {design["line"]}; coupling-map qubits {b.num_qubits}')
    for c in Q.TARGETS: print(f'   {c}: physical qubits (clbit order) {design["phys"][c]}, cz {design["n2q"][c]} (theirs: chain21 60, chain11 30, hp8 198), depth {design["depth"][c]}')
    nb = max(m['batch'] for m in design['rb_meta'].values()) + 1
    print(f'   design edges {len(design["edges"])} (20 line + {len(design["edges"]) - 20} HP_8-only), RB: {nb} isolated batches x {len(M2)} lengths x {SEEDS} seeds = {len(design["rb_meta"])} circuits at {RB_SHOTS} shots; RB transpile left the op count unchanged: {ratio_ok} ({design["ops_before_after_rb"]})')
    ftar = est_seconds([f'T_{c}' for c in Q.TARGETS], circ, shots, b); billed = sum(THEIR_BILLED.values()); k = max(1.0, billed / ftar)
    est = est_seconds(names, circ, shots, b, k) + 2.0; total = est * len(PLAN_LABELS)
    print(f'   estimate: formula for their three targets {ftar:.1f} s against their billed {billed} s -> scale {k:.2f}; one job {est:.1f} s (shots x (duration + 290 us) x scale + 2 s), four jobs {total:.0f} s, cap {CAP}, remaining {rem}')
    print(f'{CHIP}: 3 targets + 3 readout strings + {len(design["rb_meta"])} RB circuits per job, 4 jobs A1 B1 B2 A2, est {total:.0f} s (cap {CAP}), remaining {rem}', flush=True)
    if '--fire' not in sys.argv: sys.exit(0)
    if not ratio_ok: print('STOP: transpile changed the RB circuits'); sys.exit(1)
    qpy.dump([circ[n] for n in names], open(f'{HERE}/circuits_qusoft.qpy', 'wb')); chash = hashlib.sha256(open(f'{HERE}/circuits_qusoft.qpy', 'rb').read()).hexdigest()
    design.update(circuit_hash=chash, names=names, shots=shots); json.dump(design, open(f'{HERE}/design_qusoft.json', 'w'), default=str)
    from qiskit_ibm_runtime import SamplerV2
    rec = dict(chip=CHIP, circuit_hash=chash, planned=PLAN_LABELS, est_per_job=est, jobs=[]); spent = 0.0
    for label in PLAN_LABELS:
        order = names if label[0] == 'A' else names[::-1]; rem = s.usage().get('usage_remaining_seconds')                      # remaining seconds checked before EVERY job
        if spent + est > CAP: print(f'STOP: {spent} s spent + {est} s next > cap {CAP}'); break
        if rem is not None and rem < est + 30: print(f'STOP: remaining {rem} s < {est} + 30'); break
        json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_qusoft_before_{label}.json', 'w'), default=str)
        json.dump(dict(rec, next=label, remaining_before=rem), open(f'{HERE}/job_qusoft.json', 'w'), default=str)
        smp = SamplerV2(mode=b); smp.options.max_execution_time = MAXEXEC
        job = smp.run([(circ[n], None, shots[n]) for n in order]); sub = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        print(f'SUBMITTED job {label} {job.job_id()} {sub} (remaining before {rem})', flush=True)
        res = job.result(); raw = {n: {str(k_): int(v) for k_, v in getc(pr).items()} for n, pr in zip(order, res)}
        json.dump(raw, open(f'{HERE}/raw_qusoft_{label}.json', 'w'))
        m = job.metrics(); u = (m.get('usage') or {}).get('quantum_seconds') or (m.get('usage') or {}).get('qpu_charge_time_seconds') or est; spent += u
        rec['jobs'].append(dict(label=label, order=order, job_id=job.job_id(), submitted_utc=sub, usage=m.get('usage'), timestamps=m.get('timestamps'))); json.dump(rec, open(f'{HERE}/job_qusoft.json', 'w'), default=str)
        print(f'DONE job {label} usage {u} s (total {spent})', flush=True)
        if spent / (PLAN_LABELS.index(label) + 1) * len(PLAN_LABELS) > CAP: print(f'STOP: projected {spent / (PLAN_LABELS.index(label) + 1) * len(PLAN_LABELS):.0f} s for four jobs > cap {CAP}'); break
    json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_qusoft_after.json', 'w'), default=str)
    print('ALL DONE', spent, 's', flush=True)
