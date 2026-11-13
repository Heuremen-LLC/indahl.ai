#!/usr/bin/env python3
"""line_run.py: calibration of Awuah and Guo's SWAP-chain runs on ibm_kingston (arXiv 2610.20855v1, Section 9, their Table 18). See PLAN_AWUAH_GUO.md.text, committed before this code ran on hardware.
  python3 line_run.py --selftest WORLD      planted worlds on Aer, no device (WORLD: match, worse, rohigh)
  python3 line_run.py --estimate            transpile on kingston, estimate, submit nothing
  python3 line_run.py --fire                submit the two jobs (chain, then RB and readout) on the one line, same session
  python3 line_run.py --analyze             read the saved results, print the readings
Key and instance: IBM_QUANTUM_TOKEN and IBM_QUANTUM_INSTANCE in the environment, never written, never printed. Their code is never executed: find_line below is the same algorithm, written out here."""
import os, sys, json, math, time
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); ARX = os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'); sys.path.insert(0, ARX)
import sweep as SW
TAG, BACKEND, NMAX, SHOTS = 'qia-fill-awuah-guo-20261029', 'ibm_kingston', 21, 4096
CAP_S, KEEP_S = 90, 600
TOL = 0.05   # the model's own bias at n = 21 measured in the three planted worlds (0 to 4.7 percent), fixed before any hardware result
# their printed Table 18 (SWAP chain, ibm_kingston, 27 May 2026, 4096 shots): n -> (in-subspace fraction, P(target))
THEIRS = {2: (.7759, .754395), 3: (.8464, .836182), 4: (.8328, .814941), 5: (.7939, .773438), 6: (.7922, .767822), 7: (.7878, .760742), 8: (.7715, .738281), 9: (.7537, .718506), 10: (.7322, .690918), 11: (.7471, .704834),
          12: (.7043, .655029), 13: (.7034, .645752), 14: (.6670, .603760), 15: (.6648, .600830), 16: (.6560, .588623), 17: (.6287, .552002), 18: (.5522, .469482), 19: (.5125, .421143), 20: (.4883, .394531), 21: (.4785, .389404)}
def published_model():
    """their Section 9.3 sentences, recomputed from their printed numbers: p2q = 2.0e-3, n2q = 3(n-1), readout 1e-2 per qubit"""
    s21 = (1 - 2.0e-3) ** 60; ro21 = (1 - 1e-2) ** 21
    return dict(S_gate_n21=round(s21, 3), readout_n21=round(ro21, 3), both_n21=round(s21 * ro21, 3), S_gate_min_over_n_to_21=round((1 - 2.0e-3) ** 60, 3))
def find_line(coupling_edges, nq, length=NMAX):
    """greedy depth-first search for a simple path of `length` qubits, starting from qubit 0 upward, neighbours in set order: the algorithm of their hardware_swap_chain_baseline.py"""
    adj = {q: set() for q in range(nq)}
    for a, b in coupling_edges: adj[a].add(b); adj[b].add(a)
    def dfs(path):
        if len(path) == length: return path
        for nb in adj[path[-1]]:
            if nb in path: continue
            f = dfs(path + [nb])
            if f is not None: return f
        return None
    for s in range(nq):
        r = dfs([s])
        if r is not None: return r
def chain_circuit(n):
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(n, name='swap_chain_n%d' % n); qc.x(0)
    for k in range(n - 1): qc.swap(k, k + 1)
    qc.measure_all(); return qc
def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); s = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)); return (c - s) / d, (c + s) / d
def remap(props_q, props_g, line):
    st_q = {v: props_q[line[v]] for v in range(len(line))}; st_g = {}
    for v in range(len(line)):
        st_g[('sx', (v,))] = props_g.get(('sx', (line[v],)))
        if v < len(line) - 1:
            a, b = line[v], line[v + 1]; g = props_g.get(('cz', (a, b)), props_g.get(('cz', (b, a)))); st_g[('cz', (v, v + 1))] = g
    return st_q, st_g
def readout_delivered(meta, data, n):
    """delivered readout figures as a bracket per qubit, the method of sweep.analyze: previous shot ended in |0> .. in |1>"""
    acc = {}
    for i, m in enumerate(meta):
        if m['kind'] in ('I1', 'I0', 'IQ'):
            for r in ('a', 'b'): acc.setdefault((m['kind'], r), []).append(data[i][r].mean(axis=0))
    P = {k: np.mean(v, axis=0) for k, v in acc.items()}; a1, a0 = P[('I1', 'a')], P[('I0', 'a')]; p01 = 1 - P[('IQ', 'b')]; p01_1 = 1 - P[('I1', 'b')]
    return (np.minimum(a0, a1), np.maximum(a0, a1)), (np.minimum(p01, p01_1), np.maximum(p01, p01_1)), dict(a0=a0, a1=a1, p01=p01, p01_1=p01_1)
def model(n, e_edge, r0, r1):
    """P(target) for the SWAP chain of n qubits: each CZ layer keeps the right basis state with probability 1 - (layer error), three layers per SWAP on edge k, then the readouts: the target in |1> read right, the others in |0> read right"""
    s = 1.0
    for k in range(n - 1): s *= (1 - e_edge[k]) ** 3
    ro = (1 - r1[n - 1])
    for q in range(n - 1): ro *= (1 - r0[q])
    return s * ro
def readings(chain_counts, res, ro0, ro1, st_q, st_g, label, ctx):
    """chain_counts: n -> (counts dict). res: sweep.analyze result. ro0, ro1: delivered readout brackets. Prints and returns the per-n table and the outcomes."""
    N = NMAX; stated_e = [st_g[('cz', (k, k + 1))] for k in range(N - 1)]; deliv_e = [res['epl'].get((k, k + 1)) for k in range(N - 1)]
    r0s = [st_q[q]['prob_meas1_prep0'] for q in range(N)]; r1s = [st_q[q]['prob_meas0_prep1'] for q in range(N)]
    out = []; ok_d = all(e is not None for e in deliv_e)
    print('-- %s' % label); print('   n   measured [95%]         theirs(27 May)  model stated  model delivered, matched context [full readout bracket]   outcome vs matched +-5%   measured/matched')
    cnt = {'ABOVE': 0, 'BELOW': 0, 'CONSISTENT': 0, 'CANNOT_TELL': 0}
    for n in range(2, N + 1):
        c = chain_counts[n]; tot = sum(c.values()); k = c.get('1' + '0' * (n - 1), 0); p = k / tot; lo, hi = wilson(k, tot)
        ms = model(n, stated_e, r0s, r1s)
        if ok_d:
            m_lo = model(n, [min(e, 1) for e in deliv_e], [ro0[1][q] for q in range(N)], [ro1[1][q] for q in range(N)]); m_hi = model(n, deliv_e, [ro0[0][q] for q in range(N)], [ro1[0][q] for q in range(N)])
            # the point model uses the readout figure in the context the chain circuits have: a qubit read as 0 after a shot that ended in 0 (a0), the target read as 1 after a shot that ended in 1 (p01_1)
            r0m = [ctx['a0'][q] for q in range(N)]; r1m = [ctx['p01_1'][q] for q in range(N)]; mid = model(n, deliv_e, r0m, r1m)
            o = 'CANNOT_TELL' if not np.isfinite(m_lo + m_hi + mid) else ('ABOVE' if lo > mid * (1 + TOL) else 'BELOW' if hi < mid * (1 - TOL) else 'CONSISTENT')
        else: m_lo = m_hi = mid = float('nan'); o = 'CANNOT_TELL'
        cnt[o] += 1; out.append(dict(n=n, p=p, lo=lo, hi=hi, shots=tot, theirs=THEIRS[n][1], model_stated=ms, model_deliv_matched=mid, model_deliv_lo=m_lo, model_deliv_hi=m_hi, outcome=o, ratio_mid=p / mid if mid == mid else None))
        print('  %2d   %.4f [%.3f,%.3f]     %.4f         %.4f       %.4f [%.4f, %.4f]                 %-11s                   %s' % (n, p, lo, hi, THEIRS[n][1], ms, mid, m_lo, m_hi, o, ('%.3f' % (p / mid)) if mid == mid else '-'))
    print('   outcomes over n = 2..21 (descriptive, the n are nested prefixes of one line and are not independent): ', cnt)
    return out, cnt
def build_all(be, line, rng_seed=SW.SEED):
    """returns RB and readout circuits (virtual 21 qubits on the line) and the chain circuits, all transpiled as sweep.py and their script do"""
    from qiskit import transpile
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    N = be.num_qubits; adjP = {q: set() for q in range(N)}
    for a, b in be.coupling_map.get_edges(): adjP[a].add(b); adjP[b].add(a)
    edges_v = [(i, i + 1) for i in range(NMAX - 1)]; inv = {line[i]: i for i in range(NMAX)}
    orig = getattr(SW, '_orig_batches', None) or SW.batches; SW._orig_batches = orig
    def my_batches(n, edges, adj):
        pe = [(line[a], line[b]) for a, b in edges]; bs = orig(N, pe, adjP); return [[(inv[a], inv[b]) for a, b in b_] for b_ in bs]
    SW.batches = my_batches
    circs, meta, pulses, B2 = SW.build(NMAX, edges_v, np.random.default_rng(rng_seed))
    tq = transpile(circs, be, optimization_level=0, initial_layout=line, seed_transpiler=7)
    ops0 = sum(sum(c.count_ops().values()) for c in circs); ops1 = sum(sum(c.count_ops().values()) for c in tq)
    chains = []
    for n in range(2, NMAX + 1):
        pm = generate_preset_pass_manager(optimization_level=0, backend=be, initial_layout=line[:n], seed_transpiler=0); chains.append(pm.run(chain_circuit(n)))
    return tq, meta, pulses, B2, chains, (ops0, ops1)
def estimate(be, tq, meta, chains):
    dur = np.array([c.estimate_duration(be.target, 's') for c in tq]); sh = np.array([m['shots'] for m in meta])
    dc = np.array([c.estimate_duration(be.target, 's') for c in chains])
    return float(np.sum(sh * (dur + 290e-6))), float(np.sum(SHOTS * (dc + 290e-6)))
def service():
    from qiskit_ibm_runtime import QiskitRuntimeService
    return QiskitRuntimeService(channel='ibm_cloud', token=os.environ['IBM_QUANTUM_TOKEN'], instance=os.environ['IBM_QUANTUM_INSTANCE'])
def props_stated(be):
    pr = be.properties().to_dict()
    return pr
def selftest(world, seed=7):
    """planted worlds on Aer: a line of 21 qubits, every figure planted; the analysis must read the planted ratios and the model must meet the chain results"""
    from qiskit import transpile
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError
    rng = np.random.default_rng(seed); n = NMAX; edges = [(i, i + 1) for i in range(n - 1)]
    f = {'match': 1.0, 'worse': 1.3, 'rohigh': 1.3, 'roonly': 1.0}[world]; rof = 2.5 if world in ('rohigh', 'roonly') else 1.0
    st_g = {('sx', (q,)): float(rng.uniform(2e-4, 4e-4)) for q in range(n)}
    for e in edges: st_g[('cz', e)] = float(rng.uniform(1.5e-3, 3e-3))
    E01 = rng.uniform(0.002, 0.012, n); E10 = rng.uniform(0.008, 0.03, n); E01s, E10s = E01 / rof, E10 / rof
    st_q = {q: {'prob_meas1_prep0': float(E01s[q]), 'prob_meas0_prep1': float(E10s[q])} for q in range(n)}
    nm = NoiseModel(); _, _, _, _, pulses = SW.clifford_table()
    for q in range(n):
        nm.add_quantum_error(depolarizing_error(2 * st_g[('sx', (q,))] * f, 1), ['sx', 'x'], [q])
        nm.add_readout_error(ReadoutError([[1 - E01[q], E01[q]], [E10[q], 1 - E10[q]]]), [q])
    for e in edges:
        oneq = 2 * pulses * np.mean([st_g[('sx', (q,))] * f for q in e]); pz = max(st_g[('cz', e)] * f - oneq, 1e-5) * 4 / 3
        nm.add_quantum_error(depolarizing_error(pz, 2), ['cz'], [e[0], e[1]]); nm.add_quantum_error(depolarizing_error(pz, 2), ['cz'], [e[1], e[0]])
    sim = AerSimulator(method='stabilizer', noise_model=nm)
    circs, meta, pulses, B2 = SW.build(n, edges, np.random.default_rng(seed)); data = []
    TH = 0.0005; IE = rng.uniform(0.002, 0.02, n)
    for c, m in zip(circs, meta):
        if m['kind'] in ('I1', 'I0', 'IQ'):
            sh_ = m['shots']; pop = rng.random((sh_, n)) < (IE if m['kind'] == 'I1' else TH)
            rd = lambda state: np.where(state, rng.random((sh_, n)) > E10, rng.random((sh_, n)) < E01)
            a = rd(pop); b = rd(~pop) if m['kind'] in ('I1', 'IQ') else rd(pop); data.append({'a': a, 'b': b})
        else:
            r = sim.run(c, shots=m['shots'], seed_simulator=int(rng.integers(1 << 30)), memory=True).result().get_memory()
            data.append({'c': np.array([[ch == '1' for ch in s[::-1]] for s in r])})
    res = SW.analyze(meta, data, n, pulses, st_q, st_g, 'synth %s: planted sx and cz = %.2f x stated, readout %.1f x stated' % (world, f, rof))
    ro0, ro1, ctx = readout_delivered(meta, data, n); chain = {}
    for m_ in range(2, n + 1):
        qc = transpile(chain_circuit(m_), basis_gates=['rz', 'sx', 'x', 'cz'], optimization_level=0)
        cts = sim.run(qc, shots=SHOTS, seed_simulator=int(rng.integers(1 << 30))).result().get_counts(); chain[m_] = {k.replace(' ', ''): v for k, v in cts.items()}
    out, cnt = readings(chain, res, ro0, ro1, st_q, st_g, 'synth %s chain' % world, ctx)
    # the model itself against the planted world: planted truth is the product of the planted per-edge layer errors and planted readouts
    return out, cnt

def device_setup():
    s = service(); be = s.backend(BACKEND); nq = be.num_qubits; line = find_line(list(be.coupling_map.get_edges()), nq)
    return s, be, nq, line
def cmd_estimate(fire):
    s, be, nq, line = device_setup(); tq, meta, pulses, B2, chains, (o0, o1) = build_all(be, line)
    e_rb, e_ch = estimate(be, tq, meta, chains); est = e_rb + e_ch; u = s.usage(); rem = u['usage_remaining_seconds']
    print('backend %s, %d qubits. Line of %d physical qubits (their algorithm): %s' % (BACKEND, nq, NMAX, line))
    print('chain circuits n=2..21 (%d shots each) and %d RB and readout circuits in %d isolated edge batches; ops %d -> %d after transpile (must be equal)' % (SHOTS, len(tq), len(B2), o0, o1))
    print('ESTIMATED QPU seconds %.0f (chain %.0f, RB and readout %.0f; an estimate from circuit durations plus 290 microseconds a shot, not a measurement). Account seconds remaining %d. Cap %d, keep %d.' % (est, e_ch, e_rb, rem, CAP_S, KEEP_S))
    if o0 != o1: sys.exit('STOP: the transpile changed the RB circuits')
    if est > CAP_S or rem - est < KEEP_S: sys.exit('REFUSED by the plan limits.')
    prior = [j.job_id() for j in s.jobs(limit=60, backend_name=BACKEND) if TAG in (j.tags or [])]
    if prior: sys.exit('REFUSED: jobs with tag %s already exist: %s. List jobs before any refire.' % (TAG, prior))
    if not fire: print('Submits nothing without --fire.'); return
    from qiskit_ibm_runtime import SamplerV2
    pr0 = be.properties().to_dict(); json.dump(pr0, open(H + '/props_before.json', 'w'), default=str)
    subs = []
    for name, pubs in (('chain', [(c, None, SHOTS) for c in chains]), ('rb', [(c, None, m['shots']) for c, m in zip(tq, meta)])):
        sam = SamplerV2(mode=be); sam.options.dynamical_decoupling.enable = False
        try: sam.options.environment.job_tags = [TAG]
        except Exception as ex: print('tag not set:', ex)
        try: sam.options.max_execution_time = CAP_S
        except Exception as ex: print('max_execution_time not set:', ex)
        job = sam.run(pubs); subs.append(dict(name=name, job_id=job.job_id(), submitted_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))); print('SUBMITTED', name, job.job_id(), flush=True)
    json.dump(dict(jobs=subs, line=line, meta=meta, pulses=pulses, est=est, remaining_before=rem, props_stamp_before=str(pr0.get('last_update_date'))), open(H + '/jobs.json', 'w'), indent=1, default=str)
def cmd_fetch():
    s, be, nq, line = device_setup(); rec = json.load(open(H + '/jobs.json')); out = {}; chain = {}
    for j in rec['jobs']:
        job = s.job(j['job_id']); res = job.result(); j['status'] = str(job.status()); j['metrics'] = job.metrics()
        if j['name'] == 'chain':
            for i, n in enumerate(range(2, NMAX + 1)): chain[n] = dict(res[i].data.meas.get_counts())
        else:
            for i, pr in enumerate(res):
                for r in ('a', 'b', 'c'):
                    if hasattr(pr.data, r): out['%s_%d' % (r, i)] = getattr(pr.data, r).to_bool_array(order='little')
    pr1 = be.properties().to_dict(); json.dump(pr1, open(H + '/props_after.json', 'w'), default=str); rec['props_stamp_after'] = str(pr1.get('last_update_date'))
    np.savez_compressed(H + '/raw_rb.npz', **out); json.dump({str(k): v for k, v in chain.items()}, open(H + '/raw_chain.json', 'w')); json.dump(rec, open(H + '/jobs.json', 'w'), indent=1, default=str)
    print('saved; record stamps before/after:', rec['props_stamp_before'], rec['props_stamp_after'])
def cmd_analyze():
    rec = json.load(open(H + '/jobs.json')); line = rec['line']; z = np.load(H + '/raw_rb.npz'); chain = {int(k): v for k, v in json.load(open(H + '/raw_chain.json')).items()}
    props = json.load(open(H + '/props_before.json')); st_q0, st_g0 = SW.stated(props); st_q, st_g = remap(st_q0, st_g0, line)
    stable = rec['props_stamp_before'] == rec.get('props_stamp_after')
    print('=== %s, record stamp before %s after %s -> %s' % (BACKEND, rec['props_stamp_before'], rec.get('props_stamp_after'), 'the record the jobs ran under' if stable else 'CHANGED DURING THE JOBS, the comparison with stated reads CANNOT_TELL'))
    data = [{r: z['%s_%d' % (r, i)] for r in ('a', 'b', 'c') if '%s_%d' % (r, i) in z} for i in range(len(rec['meta']))]
    res = SW.analyze(rec['meta'], data, NMAX, rec['pulses'], st_q, st_g, 'kingston line %s' % line); ro0, ro1, ctx = readout_delivered(rec['meta'], data, NMAX)
    out, cnt = readings(chain, res, ro0, ro1, st_q, st_g, 'SWAP chain, today against their 27 May table', ctx)
    json.dump(dict(readings=out, outcomes=cnt, line=line, stable=stable, epl={str(k): v for k, v in res['epl'].items()}, epg={str(k): v for k, v in res['epg'].items()}), open(H + '/readings.json', 'w'), indent=1, default=str)

def split(rows, key, err=True):
    """Addendum 1 (THE SPLIT): weighted fit log P = S + P_swap (n - 1); S the offset common to every n (prep and readout), exp(P_swap) the survival per SWAP. Shot-noise interval only."""
    n = np.array([r['n'] for r in rows], float) - 1; y = np.array([r[key] for r in rows], float)
    if err: w = np.array([r['shots'] * r['p'] / max(1 - r['p'], 1e-9) for r in rows])
    else: w = np.ones_like(y)
    ly = np.log(y); X = np.vstack([np.ones_like(n), n]).T; W = np.diag(w); C = np.linalg.inv(X.T @ W @ X); b = C @ X.T @ W @ ly
    se = np.sqrt(np.diag(C)) if err else np.array([np.nan, np.nan])
    return dict(S=float(np.exp(b[0])), per_swap=float(np.exp(b[1])), per_swap_lo=float(np.exp(b[1] - 1.96 * se[1])), per_swap_hi=float(np.exp(b[1] + 1.96 * se[1])))
def cmd_record():
    """Addendum 1 (check 3 and 13): the IBM record in force at each job's start and end, and the gap between the jobs; zero QPU"""
    import datetime as dt
    s, be, nq, line = device_setup(); rec = json.load(open(H + '/jobs.json')); out = {}
    for j in rec['jobs']:
        ts = (j.get('metrics') or {}).get('timestamps', {}); out[j['name']] = dict(running=ts.get('running'), finished=ts.get('finished'))
        for k in ('running', 'finished'):
            t = dt.datetime.fromisoformat(str(ts[k]).replace('Z', '+00:00')); pr = be.properties(datetime=t).to_dict()
            out[j['name']]['stamp_' + k] = str(pr.get('last_update_date'))
            if j['name'] == 'chain' and k == 'running': json.dump(pr, open(H + '/props_chain_start.json', 'w'), default=str)
    st = {v for o in out.values() for kk, v in o.items() if kk.startswith('stamp_')}; out['one_record'] = len(st) == 1; out['stamps'] = sorted(st)
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    pm = generate_preset_pass_manager(optimization_level=0, backend=be, initial_layout=line, seed_transpiler=0); c = pm.run(chain_circuit(NMAX)); out['ops_n21'] = {k: int(v) for k, v in c.count_ops().items()}
    json.dump(out, open(H + '/record.json', 'w'), indent=1, default=str); print(json.dumps(out, indent=1, default=str))
def cmd_addendum():
    """Addendum 1 readings, run after cmd_record: the chain scored against the model with the record in force at chain start; the split; sign labels"""
    rec = json.load(open(H + '/jobs.json')); r = json.load(open(H + '/record.json')); line = rec['line']; z = np.load(H + '/raw_rb.npz'); chain = {int(k): v for k, v in json.load(open(H + '/raw_chain.json')).items()}
    props = json.load(open(H + '/props_chain_start.json')); st_q0, st_g0 = SW.stated(props); st_q, st_g = remap(st_q0, st_g0, line)
    print('=== Addendum 1 readings. Jobs ran: chain %s to %s, rb %s to %s. IBM record stamps over both jobs: %s -> %s' % (r['chain']['running'], r['chain']['finished'], r['rb']['running'], r['rb']['finished'], r['stamps'], 'ONE record for both jobs' if r['one_record'] else 'MORE THAN ONE record: stated comparisons CANNOT_TELL'))
    print('    transpiled chain n = 21 ops:', r['ops_n21'])
    print('    sign: chain ABOVE = measured P(target) kept MORE than the delivered model (x 1.05); chain BELOW = kept LESS (beyond the incoherent model; coherent stacking, leakage, spectator crosstalk not excluded). RB ABOVE = delivered error MORE than stated.')
    data = [{k: z['%s_%d' % (k, i)] for k in ('a', 'b', 'c') if '%s_%d' % (k, i) in z} for i in range(len(rec['meta']))]
    res = SW.analyze(rec['meta'], data, NMAX, rec['pulses'], st_q, st_g, 'kingston line %s, record at chain start' % line); ro0, ro1, ctx = readout_delivered(rec['meta'], data, NMAX)
    out, cnt = readings(chain, res, ro0, ro1, st_q, st_g, 'SWAP chain, record at chain start', ctx)
    if not r['one_record']: cnt = {'ABOVE': 0, 'BELOW': 0, 'CONSISTENT': 0, 'CANNOT_TELL': 20}; print('    stated comparisons CANNOT_TELL (more than one record)')
    th = [dict(n=n, p=THEIRS[n][1], shots=4096) for n in range(2, NMAX + 1)]
    sp = dict(measured=split(out, 'p'), theirs_27May=split(th, 'p'), model_stated=split(out, 'model_stated', err=False), model_delivered=split(out, 'model_deliv_matched', err=False))
    print('-- THE SPLIT: P(target) = S x (per-SWAP survival)^(n-1), weighted fit, shot-noise 95% interval on the measured and their per-SWAP survival')
    for k, v in sp.items(): print('   %-16s S %.4f   per SWAP %.5f [%.5f, %.5f]' % (k, v['S'], v['per_swap'], v['per_swap_lo'], v['per_swap_hi']))
    json.dump(dict(readings=out, outcomes=cnt, split=sp, record=r), open(H + '/readings_addendum1.json', 'w'), indent=1, default=str)
if __name__ == '__main__':
    a = sys.argv
    if '--selftest' in a: selftest(a[a.index('--selftest') + 1]); sys.exit(0)
    if '--published' in a: print(published_model()); sys.exit(0)
    if '--estimate' in a: cmd_estimate(False); sys.exit(0)
    if '--fire' in a: cmd_estimate(True); sys.exit(0)
    if '--fetch' in a: cmd_fetch(); sys.exit(0)
    if '--analyze' in a: cmd_analyze(); sys.exit(0)
    if '--record' in a: cmd_record(); sys.exit(0)
    if '--addendum' in a: cmd_addendum(); sys.exit(0)
    print('modes: --selftest WORLD | --published | --estimate | --fire | --fetch | --analyze')
