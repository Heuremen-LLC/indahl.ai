"""Repeat for the Awuah-Guo kingston run, edge (9,10). Plan: PLAN_REPEAT.md.text (committed before any job).
  python3 repeat.py --selftest     planted worlds on Aer, no device
  python3 repeat.py --estimate     zero QPU: build, transpile, estimate seconds
  python3 repeat.py --fire         one job, tag qia-fill-awuah-guo-repeat-20261029
  python3 repeat.py --fetch / --analyze"""
import json, math, os, sys, time
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(H))
import line_run as LR
BACKEND, TAG, CAP_S, KEEP_S, SH_T, SH_C = 'ibm_kingston', 'qia-fill-awuah-guo-repeat-20261029', 40, 600, 2048, 4096
EDGES = [(8, 9), (9, 10), (10, 11)]; SUSPECT = (9, 10); INPUTS = ['00', '01', '10', '11']   # input string = (bit of a, bit of b)
MARGIN = 0.05
def truth_circuit(bits):
    """CZ framed as a CNOT: H(a) CZ(a,b) H(a). Virtual 0 = a, 1 = b. Expected out: a' = a xor b, b' = b."""
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(2, name='truth_' + bits)
    if bits[0] == '1': qc.x(0)
    if bits[1] == '1': qc.x(1)
    qc.h(0); qc.cz(0, 1); qc.h(0); qc.measure_all(); return qc
def expected(bits):
    a, b = int(bits[0]), int(bits[1]); return '%d%d' % (b, a ^ b)   # qiskit key: qubit 1 left, qubit 0 right
def frac_correct(counts_by_input):
    k = sum(c.get(expected(i), 0) for i, c in counts_by_input.items()); n = sum(sum(c.values()) for c in counts_by_input.values()); lo, hi = LR.wilson(k, n); return k / n, lo, hi, n
def outcome_edge(s, ctrls):
    """four outcomes for the suspect edge against its two neighbours (the known-good seats on the same chip, same job)"""
    if min(c[0] for c in ctrls) < 0.90: return 'CANNOT_TELL (a control edge read below 0.90: the instrument is not known-good)'
    lo_c = min(c[1] for c in ctrls); hi_c = max(c[2] for c in ctrls)
    if s[2] < lo_c - MARGIN: return 'BELOW'
    if s[1] > hi_c + MARGIN: return 'ABOVE'
    if s[1] >= lo_c - MARGIN and s[2] <= hi_c + MARGIN: return 'CONSISTENT'
    return 'CANNOT_TELL'
def ratio(k14, n14, k15, n15):
    p14, p15 = k14 / n14, k15 / n15; r = p15 / p14; se = r * math.sqrt((1 - p14) / (n14 * p14) + (1 - p15) / (n15 * p15)); return r, r - 1.96 * se, r + 1.96 * se
def outcome_ratio(r, stated_ratio):
    lo, hi = r[1], r[2]
    if hi < stated_ratio * (1 - MARGIN): return 'BELOW'
    if lo > stated_ratio * (1 + MARGIN): return 'ABOVE'
    if lo >= stated_ratio * (1 - MARGIN) and hi <= stated_ratio * (1 + MARGIN): return 'CONSISTENT'
    return 'CANNOT_TELL'
def report(tt, chain, stated_ratio, label):
    print('--', label); res = {}
    for e in EDGES:
        f = frac_correct(tt[e]); res[e] = f; print('   edge %s truth table, fraction correct %.4f [%.4f, %.4f] over %d shots' % (e, f[0], f[1], f[2], f[3]))
        for i in INPUTS:
            c = tt[e][i]; n = sum(c.values()); top = sorted(c.items(), key=lambda x: -x[1])[:4]; print('      in %s expect %s: %s' % (i, expected(i), ', '.join('%s %.3f' % (b, k / n) for b, k in top)))
    o = outcome_edge(res[SUSPECT], [res[e] for e in EDGES if e != SUSPECT]); print('   edge %s against its neighbours (margin %.2f): %s' % (SUSPECT, MARGIN, o))
    k14 = chain[14].get('1' + '0' * 13, 0); k15 = chain[15].get('1' + '0' * 14, 0); n14 = sum(chain[14].values()); n15 = sum(chain[15].values())
    r = ratio(k14, n14, k15, n15); o2 = outcome_ratio(r, stated_ratio)
    print('   chain P(target) n=14 %.4f, n=15 %.4f, ratio %.3f [%.3f, %.3f] vs stated-model ratio %.4f -> %s' % (k14 / n14, k15 / n15, r[0], r[1], r[2], stated_ratio, o2))
    return dict(edges={str(e): res[e] for e in EDGES}, edge_outcome=o, chain_ratio=r, chain_outcome=o2)
def selftest():
    from qiskit import transpile
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError
    out = {}
    for world, pbad in (('null', None), ('broken', 0.8), ('mild', 0.02)):
        tt = {}
        for e in EDGES:
            nm = NoiseModel(); p2 = (pbad if (e == SUSPECT and pbad) else 0.003); nm.add_quantum_error(depolarizing_error(p2, 2), ['cz'], [0, 1]); nm.add_quantum_error(depolarizing_error(5e-4, 1), ['sx', 'x'], [0]); nm.add_quantum_error(depolarizing_error(5e-4, 1), ['sx', 'x'], [1])
            for q in (0, 1): nm.add_readout_error(ReadoutError([[0.995, 0.005], [0.015, 0.985]]), [q])
            sim = AerSimulator(method='stabilizer', noise_model=nm); tt[e] = {}
            for i in INPUTS:
                c = transpile(truth_circuit(i), basis_gates=['cz', 'sx', 'rz', 'x'], optimization_level=0); tt[e][i] = sim.run(c, shots=SH_T, seed_simulator=11).result().get_counts()
        # chain: planted per-SWAP survival, n=14 then n=15 crossing the suspect edge
        rng = np.random.default_rng(3); p14 = 0.75; p15 = p14 * (0.985 if not pbad else (1 - pbad) ** 3 * 0.985 + 0.25 * (1 - (1 - pbad) ** 3) if pbad > 0.1 else (1 - pbad) ** 3 * 0.985)
        chain = {14: {'1' + '0' * 13: int(rng.binomial(SH_C, p14)), 'x': 0}, 15: {'1' + '0' * 14: int(rng.binomial(SH_C, p15)), 'x': 0}}
        chain[14]['x'] = SH_C - chain[14]['1' + '0' * 13]; chain[15]['x'] = SH_C - chain[15]['1' + '0' * 14]
        out[world] = report(tt, chain, 0.985 * (1 - 0.00496) ** 3 / 0.985 * 0.985, 'synth %s (suspect edge depolarizing %s)' % (world, pbad))
    exp = {'null': ('CONSISTENT', 'CONSISTENT'), 'broken': ('BELOW', 'BELOW'), 'mild': (None, None)}
    ok = all(out[w]['edge_outcome'].startswith(exp[w][0]) and out[w]['chain_outcome'] == exp[w][1] for w in ('null', 'broken'))
    print('SELFTEST', 'PASS' if ok else 'FAIL', '(null must read CONSISTENT on both; broken must read BELOW on both; mild is printed, not gated)')
def build(be, line):
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    circs, meta = [], []
    for e in EDGES:
        pm = generate_preset_pass_manager(optimization_level=0, backend=be, initial_layout=list(e), seed_transpiler=0)
        for i in INPUTS: circs.append(pm.run(truth_circuit(i))); meta.append(dict(kind='truth', edge=list(e), inp=i, shots=SH_T))
    for n in (14, 15):
        pm = generate_preset_pass_manager(optimization_level=0, backend=be, initial_layout=line[:n], seed_transpiler=0); circs.append(pm.run(LR.chain_circuit(n))); meta.append(dict(kind='chain', n=n, shots=SH_C))
    return circs, meta
def cmd_fire(fire):
    s = LR.service(); be = s.backend(BACKEND); line = json.load(open(os.path.join(os.path.dirname(H), 'jobs.json')))['line']
    line_now = LR.find_line(list(be.coupling_map.get_edges()), be.num_qubits); assert line_now == line, 'line changed'
    circs, meta = build(be, line); dur = np.array([c.estimate_duration(be.target, 's') for c in circs]); sh = np.array([m['shots'] for m in meta])
    est = float(np.sum(sh * (dur + 290e-6))); rem = s.usage()['usage_remaining_seconds']
    print('%d circuits (%d truth-table, 2 chain), ESTIMATED %.0f QPU s; remaining %d; cap %d keep %d' % (len(circs), len(circs) - 2, est, rem, CAP_S, KEEP_S))
    for c, m in zip(circs, meta):
        if m['kind'] == 'truth': assert c.count_ops().get('cz', 0) == 1, 'truth circuit must hold one CZ'
    if est > CAP_S or rem - est < KEEP_S: sys.exit('REFUSED by the plan limits')
    prior = [j.job_id() for j in s.jobs(limit=60, backend_name=BACKEND) if TAG in (j.tags or [])]
    if prior: sys.exit('REFUSED: tag already used: %s' % prior)
    if not fire: print('Submits nothing without --fire.'); return
    from qiskit_ibm_runtime import SamplerV2
    json.dump(be.properties().to_dict(), open(H + '/props_before.json', 'w'), default=str)
    sam = SamplerV2(mode=be); sam.options.dynamical_decoupling.enable = False; sam.options.environment.job_tags = [TAG]; sam.options.max_execution_time = CAP_S
    job = sam.run([(c, None, m['shots']) for c, m in zip(circs, meta)]); print('SUBMITTED', job.job_id(), flush=True)
    json.dump(dict(job_id=job.job_id(), meta=meta, est=est, remaining_before=rem, line=line, submitted_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())), open(H + '/job.json', 'w'), indent=1)
def cmd_fetch():
    import datetime as dt
    s = LR.service(); be = s.backend(BACKEND); rec = json.load(open(H + '/job.json')); job = s.job(rec['job_id']); res = job.result(); rec['metrics'] = job.metrics(); ts = rec['metrics']['timestamps']
    rec['stamps'] = sorted({str(be.properties(datetime=dt.datetime.fromisoformat(str(ts[k]).replace('Z', '+00:00'))).to_dict().get('last_update_date')) for k in ('running', 'finished')})
    json.dump(be.properties(datetime=dt.datetime.fromisoformat(str(ts['running']).replace('Z', '+00:00'))).to_dict(), open(H + '/props_job_start.json', 'w'), default=str)
    rec['counts'] = [dict(res[i].data.meas.get_counts()) for i in range(len(rec['meta']))]; json.dump(rec, open(H + '/job.json', 'w'), indent=1, default=str); print('saved; stamps', rec['stamps'])
def cmd_analyze():
    rec = json.load(open(H + '/job.json')); p = json.load(open(H + '/props_job_start.json')); tt = {e: {} for e in EDGES}; chain = {}
    for m, c in zip(rec['meta'], rec['counts']):
        if m['kind'] == 'truth': tt[tuple(m['edge'])][m['inp']] = c
        else: chain[m['n']] = c
    st = {}
    for g in p['gates']:
        if g['gate'] == 'cz': st[tuple(sorted(g['qubits']))] = [(x['value'], str(x.get('date'))) for x in g['parameters'] if x['name'] == 'gate_error'][0]
    for e in EDGES: print('   IBM record at job start %s: cz %s error %.5f dated %s' % (p.get('last_update_date'), e, st[tuple(sorted(e))][0], st[tuple(sorted(e))][1][:16]))
    stated_ratio = (1 - st[SUSPECT][0]) ** 3
    print('=== repeat job %s, ran %s to %s, record stamps %s -> %s' % (rec['job_id'], rec['metrics']['timestamps']['running'], rec['metrics']['timestamps']['finished'], rec['stamps'], 'one record' if len(rec['stamps']) == 1 else 'MORE THAN ONE record'))
    out = report(tt, chain, stated_ratio, 'kingston repeat'); out['stamps'] = rec['stamps']; json.dump(out, open(H + '/readings_repeat.json', 'w'), indent=1, default=str)
if __name__ == '__main__':
    a = sys.argv
    if '--selftest' in a: selftest()
    elif '--estimate' in a: cmd_fire(False)
    elif '--fire' in a: cmd_fire(True)
    elif '--fetch' in a: cmd_fetch()
    elif '--analyze' in a: cmd_analyze()
    else: print(__doc__)
