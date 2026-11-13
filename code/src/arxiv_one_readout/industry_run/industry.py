"""industry.py -- industry runs: jobs a company would actually submit, run the way Qiskit's defaults run them, checked against the
forecast a designer gets from IBM's published figures (PLAN_INDUSTRY.md).
Each job: an exact classical answer; the Qiskit default compile (generate_preset_pass_manager, optimization level 2, IBM's figures pick
the qubits); a FORECAST from Qiskit Aer NoiseModel.from_backend (IBM's record at firing; gate, readout and T1/T2 errors) plus
RelaxationNoisePass on the scheduled circuit; the hardware result; two copies of every circuit.
  BANK       6-asset portfolio, choose 3 (QAOA p=1, angles optimised on the exact simulator, as a user would)
  LOGISTICS  MaxCut on a 6-node 3-regular network (QAOA p=1, same)
  MATERIALS  8-site transverse-field Ising chain, Trotterised dynamics from all-up, 3 steps; per-site magnetisation <Z> (the
             experiment type of IBM's utility demonstration)
GREEN LIGHT (printed in the dry run, required to fire): BANK/LOGISTICS -- the forecast's most likely answer is the exact optimum;
MATERIALS -- forecast mean |<Z>| error against exact below 0.15.
Readings (PLAN): R1 the decision (top answer) hardware vs forecast; R2 total-variation distance hardware vs forecast against the forecast's
own shot-noise floor; R3 the number a user reports (expected cost / cut / mean magnetisation) hardware vs forecast, bootstrap interval."""
import os, sys, json, time, itertools
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); H = os.path.expanduser('~/bones-forge')
KEYFILE, INSTANCE = '.ibm_quantum_key_3', 'Darkwave Disco'
SHOTS = 4000; FC_SHOTS = 200000; P_LAYERS = int(os.environ.get('QAOA_P', '2'))

# ---------------- problems ----------------
MU = np.array([0.105, 0.072, 0.131, 0.058, 0.094, 0.117])            # synthetic expected returns (disclosed as synthetic market data)
SIG = np.array([[.040, .006, .012, .002, .008, .010], [.006, .025, .004, .003, .005, .004], [.012, .004, .060, .005, .011, .015],
                [.002, .003, .005, .018, .003, .002], [.008, .005, .011, .003, .035, .009], [.010, .004, .015, .002, .009, .050]])
QRISK, BUDGET, PEN = 0.5, 3, 0.1
def bank_cost(x): x = np.array(x); return QRISK * x @ SIG @ x - MU @ x + PEN * (x.sum() - BUDGET) ** 2
GRAPH = [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (0, 3), (1, 4), (2, 5)]  # 3-regular, 6 nodes (prism)
def cut(x): return sum(1 for a, b in GRAPH if x[a] != x[b])

def ising_terms(f, n):
    """exact diagonal cost f over bitstrings -> (h_i, J_ij, const) with f(x) = const + sum h_i z_i + sum J_ij z_i z_j, z = 1 - 2x"""
    X = np.array(list(itertools.product([0, 1], repeat=n))); Z = 1 - 2 * X; y = np.array([f(x) for x in X])
    cols = [np.ones(len(X))] + [Z[:, i] for i in range(n)] + [Z[:, i] * Z[:, j] for i, j in itertools.combinations(range(n), 2)]
    c, *_ = np.linalg.lstsq(np.column_stack(cols), y, rcond=None)
    assert np.allclose(np.column_stack(cols) @ c, y, atol=1e-9)
    h = c[1:n + 1]; J = {p: c[n + 1 + k] for k, p in enumerate(itertools.combinations(range(n), 2)) if abs(c[n + 1 + k]) > 1e-12}
    return h, J, c[0]

def qaoa(n, h, J, gammas, betas):
    from qiskit import QuantumCircuit
    gammas = np.atleast_1d(gammas); betas = np.atleast_1d(betas)
    qc = QuantumCircuit(n); qc.h(range(n))
    for gamma, beta in zip(gammas, betas):
        for i in range(n):
            if abs(h[i]) > 1e-12: qc.rz(2 * gamma * h[i], i)
        for (i, j), w in J.items(): qc.rzz(2 * gamma * w, i, j)
        qc.rx(2 * beta, range(n))
    qc.measure_all(); return qc

def exact_probs(qc):
    from qiskit.quantum_info import Statevector
    q = qc.remove_final_measurements(inplace=False); p = Statevector(q).probabilities_dict()
    return {k[::-1]: v for k, v in p.items()}   # key as x0 x1 ... (qubit 0 first)

def optima(n, score):
    X = [list(x) for x in itertools.product([0, 1], repeat=n)]; v = np.array([score(x) for x in X]); m = v.min()
    return {''.join(map(str, x)) for x, y in zip(X, v) if y <= m + 1e-9}

def opt_angles(n, h, J, score, p_layers, seed=3):
    """what a user does: optimise the angles on the exact simulator (expected cost), several random starts, keep the best"""
    from scipy.optimize import minimize
    from qiskit.quantum_info import Statevector
    X = list(itertools.product([0, 1], repeat=n)); val = {''.join(map(str, x)): score(list(x)) for x in X}
    def f(th):
        p = exact_probs(qaoa(n, h, J, th[:p_layers], th[p_layers:])); return sum(v * val[k] for k, v in p.items())
    rng = np.random.default_rng(seed); best = None
    for _ in range(8):
        r = minimize(f, rng.uniform(0.05, 1.2, 2 * p_layers), method='COBYLA', options=dict(maxiter=400, rhobeg=0.3))
        if best is None or r.fun < best.fun: best = r
    return best.fun, best.x[:p_layers], best.x[p_layers:]

def tfim_circuit(n=8, steps=3, dt=0.25, Jz=1.0, hx=1.2):
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(n)
    for _ in range(steps):
        for i in range(0, n - 1, 2): qc.rzz(-2 * Jz * dt, i, i + 1)
        for i in range(1, n - 1, 2): qc.rzz(-2 * Jz * dt, i, i + 1)
        qc.rx(2 * hx * dt, range(n))
    qc.measure_all(); return qc

def jobs():
    out = {}
    hB, JB, cB = ising_terms(bank_cost, 6); eB, gB, bB = opt_angles(6, hB, JB, bank_cost, P_LAYERS)
    out['BANK'] = dict(circuit=qaoa(6, hB, JB, gB, bB), score=bank_cost, kind='min', angles=(list(gB), list(bB)))
    negcut = lambda x: -cut(x)
    hL, JL, cL = ising_terms(negcut, 6); eL, gL, bL = opt_angles(6, hL, JL, negcut, P_LAYERS)
    out['LOGISTICS'] = dict(circuit=qaoa(6, hL, JL, gL, bL), score=negcut, kind='min', angles=(list(gL), list(bL)))
    out['MATERIALS'] = dict(circuit=tfim_circuit(), score=None, kind='mag')
    return out

# ---------------- forecast / analysis ----------------
def counts_to_x(counts, n):
    out = {}
    for k, v in counts.items():
        key = k.replace(' ', '')[-n:][::-1]; out[key] = out.get(key, 0) + v
    return out
def tvd(p, q): ks = set(p) | set(q); return 0.5 * sum(abs(p.get(k, 0) - q.get(k, 0)) for k in ks)
def norm(c): t = sum(c.values()); return {k: v / t for k, v in c.items()}

def forecast_counts(b, t, seed=11):
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, RelaxationNoisePass
    from qiskit.circuit import Delay
    props = b.properties(); n = b.num_qubits
    def get(fn, q):
        try: v = fn(q); return v if v and v > 0 else None
        except Exception: return None
    t1r = [get(props.t1, q) for q in range(n)]; t2r = [get(props.t2, q) for q in range(n)]
    m1 = float(np.median([v for v in t1r if v])); m2 = float(np.median([v for v in t2r if v]))
    t1 = [v or m1 for v in t1r]; t2 = [min(v or m2, 2 * t1[q]) for q, v in enumerate(t2r)]
    rp = RelaxationNoisePass(t1s=t1, t2s=t2, dt=b.dt, op_types=[Delay])
    sim = AerSimulator(noise_model=NoiseModel.from_backend(b, thermal_relaxation=True))
    return sim.run(rp(t), shots=FC_SHOTS, seed_simulator=seed).result().get_counts()

def readings(name, job, hw_copies, fc, n, rng=None):
    rng = rng or np.random.default_rng(13); res = {}
    exact = exact_probs(job['circuit']); pf = norm(counts_to_x(fc, n)); hw = [counts_to_x(c, n) for c in hw_copies]
    ph = norm({k: sum(h.get(k, 0) for h in hw) for k in set().union(*hw)}); N = sum(sum(h.values()) for h in hw)
    keys = sorted(set(pf) | set(ph) | set(exact)); P = np.array([ph.get(k, 0) for k in keys]); F = np.array([pf.get(k, 0) for k in keys])
    floor = [0.5 * np.abs(rng.multinomial(N, F) / N - F).sum() for _ in range(1000)]; t_obs = 0.5 * np.abs(P - F).sum()
    tb = [0.5 * np.abs(rng.multinomial(N, P) / N - F).sum() for _ in range(1000)]
    lo = np.percentile(tb, 2.5); f95 = np.percentile(floor, 95)
    res['R2'] = (t_obs, lo, f95, 'ABOVE' if lo > f95 else 'CONSISTENT')
    gap = 0.5 * sum(abs(h1 - h2) for h1, h2 in zip([norm(hw[0]).get(k, 0) for k in keys], [norm(hw[1]).get(k, 0) for k in keys]))
    print(f'-- {name}: {N} shots | copy-to-copy TVD {gap:.4f} | R2 TVD(hardware, forecast) {t_obs:.4f} (lower 2.5 % {lo:.4f}) vs forecast shot-noise floor 95th pct {f95:.4f} -> {res["R2"][3]}')
    if job['kind'] == 'min':
        sc = job['score']; val = {k: sc([int(c) for c in k]) for k in keys}; O = optima(n, sc); opt = sorted(O)[0]
        rank = lambda p: sorted(keys, key=lambda k: -p.get(k, 0))
        top_h, top_f, top_e = rank(ph)[0], rank(pf)[0], rank(exact)[0]
        r_opt_h, r_opt_f = min(rank(ph).index(o) for o in O) + 1, min(rank(pf).index(o) for o in O) + 1
        # stability of the hardware's top answer: share of bootstrap resamples whose top equals the forecast's top
        boots = [keys[int(np.argmax(rng.multinomial(N, P)))] for _ in range(1000)]; agree = np.mean([b_ in O for b_ in boots])
        print(f'   R1 decision: optimal set {sorted(O)} (value {val[opt]:+.4f}) | forecast top {top_f} (best optimum ranked {r_opt_f}) | hardware top {top_h} (best optimum ranked {r_opt_h}) | hardware top is an optimum in {100 * agree:.1f} % of resamples')
        ev = lambda p: sum(p.get(k, 0) * val[k] for k in keys)
        eb = [sum(v * val[k] for k, v in zip(keys, rng.multinomial(N, P) / N)) for _ in range(2000)]; lo3, hi3 = np.percentile(eb, [2.5, 97.5])
        o = 'ABOVE' if lo3 > ev(pf) else 'BELOW' if hi3 < ev(pf) else 'CONSISTENT'
        print(f'   R3 expected value: exact-ideal {ev(exact):+.4f} | forecast {ev(pf):+.4f} | hardware {ev(ph):+.4f} [{lo3:+.4f}, {hi3:+.4f}] -> hardware {o} forecast | P(an optimum): ideal {sum(exact.get(o, 0) for o in O):.3f}, forecast {sum(pf.get(o, 0) for o in O):.3f}, hardware {sum(ph.get(o, 0) for o in O):.3f}')
        res.update(R1=(opt, top_f, top_h, r_opt_f, r_opt_h, agree), R3=(ev(exact), ev(pf), ev(ph), lo3, hi3, o))
    else:
        def mags(p): return np.array([sum(v * (1 - 2 * int(k[i])) for k, v in p.items()) for i in range(n)])
        me, mf, mh = mags(exact), mags(pf), mags(ph)
        mb = [mags(dict(zip(keys, rng.multinomial(N, P) / N))).mean() for _ in range(2000)]; lo3, hi3 = np.percentile(mb, [2.5, 97.5])
        o = 'ABOVE' if lo3 > mf.mean() else 'BELOW' if hi3 < mf.mean() else 'CONSISTENT'
        print(f'   R3 mean magnetisation: exact {me.mean():+.4f} | forecast {mf.mean():+.4f} | hardware {mh.mean():+.4f} [{lo3:+.4f}, {hi3:+.4f}] -> hardware {o} forecast')
        print(f'   per site exact {np.round(me, 3)} | forecast {np.round(mf, 3)} | hardware {np.round(mh, 3)}')
        res['R3'] = (me.mean(), mf.mean(), mh.mean(), lo3, hi3, o)
    return res

def service():
    from qiskit_ibm_runtime import QiskitRuntimeService
    tok = open(H + '/' + KEYFILE).read().strip(); s = QiskitRuntimeService(channel='ibm_quantum_platform', token=tok)
    crn = [i['crn'] for i in s.instances() if i.get('name') == INSTANCE][0]
    return QiskitRuntimeService(channel='ibm_quantum_platform', token=tok, instance=crn)

def prepare(b):
    from qiskit.transpiler import generate_preset_pass_manager
    pm = generate_preset_pass_manager(optimization_level=2, backend=b, seed_transpiler=7)
    from qiskit import transpile
    J = jobs(); out = {}
    for name, job in J.items():
        t0 = pm.run(job['circuit']); lay = t0.layout.initial_index_layout(filter_ancillas=True)[:job['circuit'].num_qubits]
        t = transpile(t0, b, optimization_level=0, scheduling_method='alap')   # schedule for the relaxation pass (gates unchanged)
        fc = forecast_counts(b, t); n = job['circuit'].num_qubits
        out[name] = dict(job=job, t=t, fc=fc, layout=list(lay), n=n)
    return out

def green(name, P):
    job, fc, n = P['job'], P['fc'], P['n']; pf = norm(counts_to_x(fc, n)); exact = exact_probs(job['circuit'])
    if job['kind'] == 'min':
        O = optima(n, job['score']); top = max(pf, key=pf.get); ptop_e = max(exact, key=exact.get)
        return (top in O and ptop_e in O), f'optimal set {sorted(O)} | ideal top {ptop_e}, forecast top {top}; P(an optimum) ideal {sum(exact.get(k, 0) for k in O):.3f}, forecast {sum(pf.get(k, 0) for k in O):.3f}'
    mag = lambda p: np.array([sum(v * (1 - 2 * int(k[i])) for k, v in p.items()) for i in range(n)])
    err = np.abs(mag(pf) - mag(exact)).mean(); return err < 0.15, f'forecast mean |<Z> error| {err:.3f}'

if __name__ == '__main__':
    a = sys.argv; CHIP = a[-1]
    if '--fetch' in a:
        rec = json.load(open(f'{HERE}/job_industry_{CHIP}.json')); res = service().job(rec['job_id']).result(); out = {}
        for i, pr in enumerate(res): out[f'p{i}'] = json.dumps(pr.join_data().get_counts())
        json.dump(out, open(f'{HERE}/raw_industry_{CHIP}.json', 'w')); print('saved', CHIP); sys.exit(0)
    if '--analyze' in a:
        rec = json.load(open(f'{HERE}/job_industry_{CHIP}.json')); raw = json.load(open(f'{HERE}/raw_industry_{CHIP}.json')); J = jobs()
        print(f'=== {CHIP} job {rec["job_id"]}')
        for name, info in rec['jobs'].items():
            hw = [json.loads(raw[f'p{i}']) for i in info['pubs']]
            print(f'   layout (Qiskit default) {info["layout"]}'); readings(name, J[name], hw, info['forecast'], info['n'])
        sys.exit(0)
    FIRE = '--fire' in a; s = service(); b = s.backend(CHIP); P = prepare(b)
    for name, p in P.items():
        ok, msg = green(name, p); p['green'] = ok
        print(f'{CHIP} {name}: layout {p["layout"]} | ops {dict((k, v) for k, v in p["t"].count_ops().items() if k in ("cz", "sx", "measure"))} | GREEN LIGHT {"YES" if ok else "NO"}: {msg}')
    pubs, rec = [], dict(chip=CHIP, jobs={})
    for name, p in P.items():
        if not p['green']: continue
        idx = []
        for cp in (0, 1): idx.append(len(pubs)); pubs.append(p['t'])
        rec['jobs'][name] = dict(pubs=idx, layout=p['layout'], n=p['n'], forecast=p['fc'], angles=p['job'].get('angles'))
    dur = np.array([t.estimate_duration(b.target, 's') for t in pubs]); est = float(SHOTS * np.sum(dur + 290e-6)) if pubs else 0; rem = s.usage().get('usage_remaining_seconds')
    print(f'   {len(pubs)} circuits, ESTIMATED {est:.0f} s, remaining {rem}')
    if not FIRE or not pubs: sys.exit(0)
    if rem is not None and rem < est + 10: print('STOP: not enough seconds'); sys.exit(1)
    from qiskit_ibm_runtime import SamplerV2
    json.dump(b.properties().to_dict(), open(f'{HERE}/props_industry_{CHIP}.json', 'w'), default=str)
    job = SamplerV2(mode=b).run(pubs, shots=SHOTS); rec.update(job_id=job.job_id(), submitted_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    json.dump(rec, open(f'{HERE}/job_industry_{CHIP}.json', 'w'), default=str); print('SUBMITTED', CHIP, job.job_id(), flush=True)
