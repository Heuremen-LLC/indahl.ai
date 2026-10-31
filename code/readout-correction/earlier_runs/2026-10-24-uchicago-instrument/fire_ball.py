"""fire_ball.py -- builds, checks and (with --fire) submits the UChicago run (PLAN_BALL.md.text). ibm_kingston, <our IBM instance>.
Dry run (default): selects the 20 targets by THEIR printed rule from the record in force, builds every circuit, transpiles (optimization 0, no DD,
trivial layout), checks (a) the Z-twirl bits change only rz (virtual) gates, (b) arm C readout and idle circuits have equal scheduled durations on
every neighbour, (c) the estimate and the cap; writes selection_ball.json and synth_config.json. Submits nothing.
--fire: re-reads the record, applies the HOLD rules, saves the record before each job, submits J1 then J2 (ABBA), saves per-shot bits.
One restart on an IBM-side ERROR, then HOLD."""
import json, sys, os, time, hashlib, warnings; warnings.filterwarnings('ignore')
import numpy as np
sys.path.insert(0, os.path.expanduser('<local helper folder>'))
from sweep import service
from qiskit import QuantumCircuit, ClassicalRegister, transpile, qpy
HERE = os.path.dirname(os.path.abspath(__file__)); CHIP = 'ibm_kingston'
Q = 20; NINST = 10; NINST_C = 2; SH_A = 1000; SH_LO = 400; SH_C = 1000; L = 3; L_DT = 545
CAP = 150; RESERVE = 430; PER_SHOT = 0.34e-3; SEED = 20261024
PAULIS = ['I', 'X', 'Y', 'Z']

def select(props, edges, n):
    """their rule (S7.1): nonadjacent qubits spanning a range of backend-reported readout error. Ours, made explicit:
    candidates readout_error < 0.05; sort by readout_error; for quantiles (i + 0.5)/Q take the nearest-ranked candidate that is not adjacent to
    (or equal to) one already chosen and has at least one neighbour with readout_error < 0.05 (for arm C)."""
    ro = {q: props['ro'][q] for q in range(n)}
    nbr = {q: set() for q in range(n)}
    for a, b in edges: nbr[a].add(b); nbr[b].add(a)
    cand = sorted([q for q in range(n) if ro[q] < 0.05 and any(ro[x] < 0.05 for x in nbr[q])], key=lambda q: (ro[q], q))
    chosen = []
    for i in range(Q):
        want = (i + 0.5) / Q * (len(cand) - 1)
        order = sorted(range(len(cand)), key=lambda r: (abs(r - want), r))
        for r in order:
            q = cand[r]
            if q in chosen or any(q in nbr[c] for c in chosen): continue
            chosen.append(q); break
    chosen = sorted(chosen, key=lambda q: (ro[q], q))
    NB = sorted(set().union(*[nbr[t] for t in chosen]) - set(chosen))
    lo = [chosen[k] for k in (2, 7, 12, 17)]          # four representative targets across the readout-error range
    return chosen, NB, lo

def proto(qc, qs, P, cbits, regs, measure=True):
    """their learning circuit on every qubit in qs: P on |0>, then L x (Z^c, MCM). cbits[(q, l)] in {0,1}."""
    for q in qs:
        if P == 'X': qc.x(q)
        elif P == 'Y': qc.y(q)
        elif P == 'Z': qc.z(q)
    qc.barrier()
    for l in range(L):
        for q in qs:
            if cbits[(q, l)]: qc.z(q)
        if measure: qc.measure(qs, regs[l])
        else:
            for q in qs: qc.delay(L_DT, q, unit='dt')
        qc.barrier()

def build_all(n, T, NB, LO, rng):
    circs, meta = [], []
    def regs_for(k):
        return [ClassicalRegister(k, f'm{l+1}') for l in range(L)]
    for arm, measured in (('A', T), ('Bhi', T + NB)):
        for P in PAULIS:
            for inst in range(NINST):
                cb = {(q, l): int(rng.integers(2)) for q in measured for l in range(L)}
                qc = QuantumCircuit(n); rs = regs_for(len(measured))
                for r in rs: qc.add_register(r)
                proto(qc, measured, P, cb, rs); circs.append(qc); meta.append(dict(arm=arm, P=P, inst=inst, shots=SH_A))
    for t in LO:
        for P in PAULIS:
            for inst in range(NINST):
                cb = {(t, l): int(rng.integers(2)) for l in range(L)}
                qc = QuantumCircuit(n); rs = regs_for(1)
                for r in rs: qc.add_register(r)
                proto(qc, [t], P, cb, rs); circs.append(qc); meta.append(dict(arm='Blo', target=t, P=P, inst=inst, shots=SH_LO))
    for P in PAULIS:
        for inst in range(NINST_C):
            cb = {(q, l): int(rng.integers(2)) for q in T for l in range(L)}
            for basis in ('X', 'Y'):
                for arm in ('CM', 'CD'):
                    qc = QuantumCircuit(n); rs = regs_for(len(T)); fin = ClassicalRegister(len(NB), 'fin')
                    for r in rs: qc.add_register(r)
                    qc.add_register(fin)
                    for q in NB: qc.h(q)
                    proto(qc, T, P, cb, rs, measure=(arm == 'CM'))
                    for q in NB:
                        if basis == 'X': qc.h(q)
                        else: qc.sdg(q); qc.h(q)
                    qc.measure(NB, fin)
                    circs.append(qc); meta.append(dict(arm=arm, P=P, inst=inst, basis=basis, shots=SH_C))
    return circs, meta

def interleave(meta):
    """round-robin over the arm groups so every arm spans the whole job: A, Bhi, Blo (4 per turn), C (1 per turn)."""
    G = {k: [i for i, m in enumerate(meta) if m['arm'] in k] for k in (('A',), ('Bhi',), ('Blo',), ('CM', 'CD'))}
    step = {('A',): 1, ('Bhi',): 1, ('Blo',): 4, ('CM', 'CD'): 1}
    out = []
    while any(G.values()):
        for k in G:
            out += G[k][:step[k]]; G[k] = G[k][step[k]:]
    assert sorted(out) == list(range(len(meta)))
    return out

def record(b):
    p = b.properties(refresh=True); n = b.num_qubits
    def g(q, name):
        try: return p.qubit_property(q, name)[0]
        except Exception: return None
    return p, dict(ro=[p.readout_error(q) for q in range(n)], p10=[g(q, 'prob_meas1_prep0') for q in range(n)],
                   p01=[g(q, 'prob_meas0_prep1') for q in range(n)], T1=[g(q, 'T1') for q in range(n)], stamp=str(p.last_update_date))

if __name__ == '__main__':
    s = service(); b = s.backend(CHIP); n = b.num_qubits
    edges = sorted({tuple(sorted(e)) for e in b.coupling_map.get_edges()})
    p, R = record(b)
    sel_path = f'{HERE}/selection_ball.json'
    if os.path.exists(sel_path):           # fixed by the plan once written
        sel = json.load(open(sel_path)); T, NB, LO = sel['targets'], sel['neighbours'], sel['Blo']
    else:
        T, NB, LO = select(R, edges, n)
        json.dump(dict(targets=T, neighbours=NB, Blo=LO, record_stamp=R['stamp'], rule='select() in fire_ball.py'), open(sel_path, 'w'), indent=1)
    rng = np.random.default_rng(SEED)
    circs, meta = build_all(n, T, NB, LO, rng)
    tq = transpile(circs, b, optimization_level=0, initial_layout=list(range(n)), seed_transpiler=24)
    # (a) twirl bits change only rz: non-rz op counts equal across instances of the same arm/setting
    groups = {}
    for t, m in zip(tq, meta):
        k = (m['arm'], m['P'], m.get('target'), m.get('basis'))
        ops = {o: c for o, c in t.count_ops().items() if o != 'rz'}
        groups.setdefault(k, set()).add(json.dumps(sorted(ops.items())))
    twirl_virtual = all(len(v) == 1 for v in groups.values())
    # (b) equal scheduled durations on neighbours, arm C readout vs idle (first pair of each basis)
    dur_ok = True; dur = {}
    for basis in ('X', 'Y'):
        iM = next(i for i, m in enumerate(meta) if m['arm'] == 'CM' and m['basis'] == basis)
        iD = next(i for i, m in enumerate(meta) if m['arm'] == 'CD' and m['basis'] == basis and m['P'] == meta[iM]['P'] and m['inst'] == meta[iM]['inst'])
        sM = transpile(tq[iM], b, optimization_level=0, scheduling_method='alap', initial_layout=list(range(n)))
        sD = transpile(tq[iD], b, optimization_level=0, scheduling_method='alap', initial_layout=list(range(n)))
        dM = [sM.qubit_duration(q) for q in NB]; dD = [sD.qubit_duration(q) for q in NB]
        dur[basis] = (sorted(set(dM)), sorted(set(dD))); dur_ok &= (dM == dD)
    shots = sum(m['shots'] for m in meta); est = round(2 * shots * PER_SHOT + 6); rem = s.usage().get('usage_remaining_seconds')
    nb_ok = [R['ro'][q] < 0.05 for q in NB]
    print(f'{CHIP}: record {R["stamp"]}; targets {T}; neighbours {len(NB)} ({sum(nb_ok)} with readout_error < 0.05); Blo {LO}; '
          f'circuits per job {len(circs)} (A 40, Bhi 40, Blo 160, C 32), shots per job {shots}; twirl only rz: {twirl_virtual}; '
          f'neighbour durations equal readout vs idle: {dur_ok} {dur}; est {est} s (cap {CAP}), remaining {rem}, reserve {RESERVE}', flush=True)
    # synthetic config from this record (product model; eta_dn from T1 over one measure length plus 0.002, eta_up 0.001)
    tm = L_DT * b.dt
    tp = [[R['p10'][q] or R['ro'][q], R['p01'][q] or R['ro'][q], float(1 - np.exp(-tm / (R['T1'][q] or 2e-4)) + 0.002), 0.001] for q in T]
    json.dump(dict(Q=len(T), NB=len(NB), shots_A=4 * NINST * SH_A, shots_Blo=4 * NINST * SH_LO, shots_C_per_basis=4 * NINST_C * SH_C,
                   targets_params=tp, nb_readout=[[R['p10'][q] or R['ro'][q], R['p01'][q] or R['ro'][q]] for q in NB],
                   Blo_idx=[T.index(t) for t in LO], draws=40), open(f'{HERE}/synth_config.json', 'w'), indent=1)
    assert twirl_virtual, 'twirl changed non-rz gates: STOP'
    assert dur_ok, 'arm C readout and idle durations differ on neighbours: STOP'
    if '--fire' not in sys.argv: sys.exit(0)
    if est > CAP or rem is None or rem - est < RESERVE: print('STOP: over cap or would cut the reserve'); sys.exit(1)
    bad = [q for q in T if R['ro'][q] >= 0.05]
    if bad: print(f'HOLD: targets {bad} have readout_error >= 0.05 in the record in force'); sys.exit(1)
    from qiskit_ibm_runtime import SamplerV2
    qpy.dump(tq, open(f'{HERE}/circuits_ball.qpy', 'wb')); chash = hashlib.sha256(open(f'{HERE}/circuits_ball.qpy', 'rb').read()).hexdigest()
    order1 = interleave(meta); order2 = order1[::-1]          # arms round-robin inside each job (check 13); J2 reversed (ABBA)
    rec = dict(chip=CHIP, targets=T, neighbours=NB, Blo=LO, nb_readout_ok=nb_ok, circuit_hash=chash, meta=meta, jobs=[])
    for J, order in (('J1', order1), ('J2', order2)):
        for attempt in (1, 2):
            p, R = record(b); json.dump(p.to_dict(), open(f'{HERE}/props_ball_before_{J}{"_retry" if attempt == 2 else ""}.json', 'w'), default=str)
            job = SamplerV2(mode=b).run([(tq[i], None, meta[i]['shots']) for i in order])
            sub = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()); print(f'SUBMITTED {J} {job.job_id()} {sub}', flush=True)
            rec['jobs'].append(dict(label=J, job_id=job.job_id(), submitted_utc=sub, attempt=attempt)); json.dump(rec, open(f'{HERE}/job_ball.json', 'w'), default=str)
            try:
                res = job.result(); break
            except Exception as e:
                print(f'ERROR {J} attempt {attempt}: {str(e)[:160]}', flush=True)
                if attempt == 2: print('HOLD after one restart'); sys.exit(1)
        out = {}
        for pos, (i, pr) in enumerate(zip(order, res)):
            for nm in ('m1', 'm2', 'm3', 'fin'):
                if hasattr(pr.data, nm): out[f'{nm}_{i}'] = getattr(pr.data, nm).to_bool_array(order='little')
        np.savez_compressed(f'{HERE}/raw_ball_{J}.npz', **out)
        m = job.metrics(); rec['jobs'][-1].update(usage=m.get('usage'), timestamps=m.get('timestamps')); json.dump(rec, open(f'{HERE}/job_ball.json', 'w'), default=str)
        print(f'DONE {J} usage {(m.get("usage") or {}).get("qpu_charge_time_seconds")} s', flush=True)
    json.dump(record(b)[0].to_dict(), open(f'{HERE}/props_ball_after.json', 'w'), default=str)
    print('ALL DONE', flush=True)
