#!/usr/bin/env python3
"""run_check.py: T1 and T2 (Hahn echo) measured together on chosen qubits, compared with IBM's published values. See PLAN.md (committed before this code).
  python3 run_check.py --selftest                                   no device, planted worlds and ideal circuits
  python3 run_check.py --backend ibm_boston --qubits 85 --estimate  prints the plan and the estimated QPU seconds, submits nothing
  python3 run_check.py --backend ibm_boston --qubits 85 --yes       submits one job on YOUR account
Your token: environment variable IBM_QUANTUM_TOKEN (and IBM_QUANTUM_INSTANCE if you use one). Never written to disk, never printed."""
import os, sys, json, argparse, datetime as D
import numpy as np
from scipy.optimize import curve_fit
NPTS, SHOTS, NBOOT = 16, 1000, 200
rng = np.random.default_rng(7)

def expo(t, A, T, B): return A * np.exp(-t / T) + B

def fit(t, p):
    """returns T in the units of t, or nan. p is the probability of the decaying outcome."""
    try:
        a = (p[0] - p[-1], max(t[-1] / 3, 1e-9), p[-1])
        po, _ = curve_fit(expo, t, p, p0=a, bounds=([-1.5, t[1] * 0.05, -0.5], [1.5, t[-1] * 50, 1.5]), maxfev=4000)
        if abs(po[0]) < 0.1: return float('nan')          # no visible decay: the fit says nothing
        return float(po[1])
    except Exception: return float('nan')

def boot(t, k, shots, n=NBOOT):
    """k: counts of the decaying outcome per delay. returns (T point, list of bootstrap T)"""
    p = np.asarray(k, float) / shots; T0 = fit(t, p); Ts = []
    for _ in range(n): Ts.append(fit(t, rng.binomial(shots, np.clip(p, 0, 1)) / shots))
    return T0, Ts

def interval(x):
    x = np.array([v for v in x if np.isfinite(v)])
    return (float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5)), len(x)) if len(x) >= 0.8 * NBOOT else (float('nan'), float('nan'), len(x))

def outcome(t1, t2, k1, k2, shots):
    """k1: counts of outcome 1 for the T1 circuits, k2: counts of outcome 0 for the echo circuits. returns dict"""
    if k1 is None or k2 is None: return dict(outcome='NOTHING_RETURNED')
    T1, b1 = boot(t1, k1, shots); T2, b2 = boot(t2, k2, shots)
    if not (np.isfinite(T1) and np.isfinite(T2)): return dict(outcome='CANNOT_TELL', t1_us=T1, t2_us=T2, why='a fit failed')
    r = [y / x for x, y in zip(b1, b2) if np.isfinite(x) and np.isfinite(y)]
    lo, hi, n = interval(r); l1 = interval(b1); l2 = interval(b2)
    lb1, ub1, lb2, ub2 = t1[1] * 0.05, t1[-1] * 50, t2[1] * 0.05, t2[-1] * 50      # the fit's own bounds (see fit()); a fit sitting on one is unbounded on that side
    on_bound = any(abs(v - b) <= 1e-6 * max(1.0, b) for v, b in ((T1, lb1), (T1, ub1), (T2, lb2), (T2, ub2))) or any(abs(v - b) <= 1e-6 * max(1.0, b) for v, b in ((l1[0], lb1), (l1[1], ub1), (l2[0], lb2), (l2[1], ub2)) if np.isfinite(v))
    oc = 'CANNOT_TELL' if (not np.isfinite(lo) or on_bound) else ('ABOVE' if lo > 2 else ('CONSISTENT' if hi <= 2 else 'CANNOT_TELL'))
    return dict(outcome=oc, t1_us=T1, t1_ci=l1[:2], t2_us=T2, t2_ci=l2[:2], ratio=T2 / T1, ratio_ci=[lo, hi], fit_on_bound=bool(on_bound))

def delays(Tpub, kind, t1pub):
    top = 3 * (Tpub if kind == 't1' else min(Tpub, 2 * t1pub)); return np.linspace(0, top, NPTS)

def snap(d_us, dt=None, gran=16):
    """delay as the device will run it: whole multiples of the timing granularity. returns (dt units or microseconds, actual microseconds of one wait)"""
    if dt is None: return d_us, d_us
    n = int(round(d_us * 1e-6 / dt / gran)) * gran; return n, n * dt * 1e6

def circuit(kind, d_us, qc_cls, dt=None, gran=16):
    """d_us is the total wait. with dt given the waits are in device units. returns (circuit, actual total wait in microseconds)"""
    qc = qc_cls(1, 1); unit = 'us' if dt is None else 'dt'
    if kind == 't1':
        w, act = snap(d_us, dt, gran); qc.x(0)
        if w > 0: qc.delay(w, 0, unit=unit)
    else:
        w, half = snap(d_us / 2, dt, gran); act = 2 * half; qc.h(0)
        if w > 0: qc.delay(w, 0, unit=unit)
        qc.x(0)
        if w > 0: qc.delay(w, 0, unit=unit)
        qc.h(0)
    qc.measure(0, 0); return qc, act

def selftest():
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator
    from qiskit import transpile
    ok = True; SEEDS = 30
    def world(T1, T2, top1=None):
        t1 = delays(T1, 't1', T1); t2 = delays(T2, 't2', top1 or T1)
        return t1, t2, 0.97 * np.exp(-t1 / T1) + 0.01, 0.5 * 0.97 * (1 + np.exp(-t2 / T2)) + 0.01
    worlds = [('T1=T2=100', 100, 100, 'CONSISTENT', None), ('T1=100 T2=150', 100, 150, 'CONSISTENT', None), ('T1=100 T2=200 (at the bound)', 100, 200, 'CANNOT_TELL', None),
              ('T1=100 T2=50', 100, 50, 'CONSISTENT', None), ('T1=100 T2=300 (ratio 3)', 100, 300, 'ABOVE', 300)]
    for name, T1, T2, want, top1 in worlds:
        t1, t2, p1, p2 = world(T1, T2, top1); right = cov1 = cov2 = 0
        for sd in range(SEEDS):
            global rng; rng = np.random.default_rng(100 + sd)
            r = outcome(t1, t2, rng.binomial(SHOTS, p1), rng.binomial(SHOTS, p2), SHOTS); right += r['outcome'] == want
            cov1 += r['t1_ci'][0] <= T1 <= r['t1_ci'][1]; cov2 += r['t2_ci'][0] <= T2 <= r['t2_ci'][1]
        good = right >= 0.9 * SEEDS and cov1 >= 0.85 * SEEDS and cov2 >= 0.85 * SEEDS; ok &= good
        print('planted', name, 'expected', want, 'right %d of %d' % (right, SEEDS), 'T1 inside interval %d, T2 inside interval %d' % (cov1, cov2), 'OK' if good else 'FAIL')
    t1, t2, _, _ = world(100, 100); flat = 0
    for sd in range(SEEDS):
        rng = np.random.default_rng(500 + sd); flat += outcome(t1, t2, rng.binomial(SHOTS, 0.5 * np.ones(NPTS)), rng.binomial(SHOTS, 0.5 * np.ones(NPTS)), SHOTS)['outcome'] == 'CANNOT_TELL'
    good = flat >= 0.9 * SEEDS; ok &= good; print('flat data reads CANNOT_TELL in %d of %d' % (flat, SEEDS), 'OK' if good else 'FAIL')
    t1, t2, _, _ = world(100, 100); short = 0                                   # decay of 0.5 us against a grid built for 100 us: the fit lands on its bound
    for sd in range(SEEDS):
        rng = np.random.default_rng(900 + sd); k1 = rng.binomial(SHOTS, 0.97 * np.exp(-t1 / 0.5) + 0.01); k2 = rng.binomial(SHOTS, 0.5 * 0.97 * (1 + np.exp(-t2 / 0.1)) + 0.01)
        short += outcome(t1, t2, k1, k2, SHOTS)['outcome'] == 'CANNOT_TELL'
    good = short >= 0.9 * SEEDS; ok &= good; print('decay far shorter than the grid reads CANNOT_TELL in %d of %d' % (short, SEEDS), 'OK' if good else 'FAIL')
    good = outcome(t1, t2, None, None, SHOTS)['outcome'] == 'NOTHING_RETURNED'; ok &= good; print('missing data -> NOTHING_RETURNED', 'OK' if good else 'FAIL')
    sim = AerSimulator()
    for kind, want in (('t1', '1'), ('t2', '0')):
        for d in (0, 5, 40):
            c = transpile(circuit(kind, d, QuantumCircuit)[0], sim); cnt = sim.run(c, shots=200).result().get_counts(); good = cnt.get(want, 0) == 200
            ok &= good; print('ideal circuit', kind, 'delay', d, cnt, 'OK' if good else 'FAIL')
    print('SELFTEST', 'PASSED' if ok else 'FAILED'); return ok

def published(backend, q):
    p = backend.properties(); return p.t1(q) * 1e6, p.t2(q) * 1e6, str(p.qubit_property(q).get('T1', (None, None))[1]), str(p.qubit_property(q).get('T2', (None, None))[1]), str(p.last_update_date)

def pick_control(backend):
    p = backend.properties(); best = None
    for q in range(backend.num_qubits):
        try: t1, t2 = p.t1(q) * 1e6, p.t2(q) * 1e6
        except Exception: continue
        if 100 <= t1 <= 300 and (best is None or abs(t2 / t1 - 1) < best[0]): best = (abs(t2 / t1 - 1), q)
    return best[1] if best else None

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--backend'); ap.add_argument('--qubits', default=''); ap.add_argument('--flagged', action='store_true', help='use the qubits flagged on indahl.ai/qia (one job per processor, pass --backend to pick which)'); ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--estimate', action='store_true'); ap.add_argument('--yes', action='store_true'); ap.add_argument('--out', default='results.json'); a = ap.parse_args()
    if a.selftest: sys.exit(0 if selftest() else 1)
    if a.flagged:
        import urllib.request
        fl = json.load(urllib.request.urlopen(urllib.request.Request('https://indahl.ai/qia/audit.json', headers={'User-Agent': 't1t2-check/0.1'}), timeout=30)).get('flagged', [])
        if not a.backend: sys.exit('flagged now: ' + ', '.join('%s q%s' % (f['backend'], f['qubit']) for f in fl) + '. Pass --backend to choose one.')
        a.qubits = ','.join(str(f['qubit']) for f in fl if f['backend'] == a.backend)
        if not a.qubits: sys.exit('nothing flagged on ' + a.backend)
    if not (a.backend and a.qubits): ap.error('--backend and --qubits are required (or --flagged)')
    tok = os.environ.get('IBM_QUANTUM_TOKEN');
    if not tok: sys.exit('set IBM_QUANTUM_TOKEN')
    from qiskit import QuantumCircuit, transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    kw = dict(channel='ibm_quantum_platform', token=tok)
    if os.environ.get('IBM_QUANTUM_INSTANCE'): kw['instance'] = os.environ['IBM_QUANTUM_INSTANCE']
    try: svc = QiskitRuntimeService(**kw); be = svc.backend(a.backend)
    except Exception as e: sys.exit('could not sign in or find the backend (%s). Check IBM_QUANTUM_TOKEN, set IBM_QUANTUM_INSTANCE to your instance CRN if you have more than one, and that your plan can see %s.' % (type(e).__name__, a.backend))
    qs = [int(x) for x in a.qubits.split(',')]; ctrl = pick_control(be)
    if ctrl is None: sys.exit('no control qubit with T1 100 to 300 us in the record')
    qs = qs + ([ctrl] if ctrl not in qs else []); jobs = []; secs = 0.0; rep = float(getattr(be, 'default_rep_delay', None) or 250e-6)
    for q in qs:
        t1p, t2p, d1, d2, stamp = published(be, q)
        for kind, Tp in (('t1', t1p), ('t2', t2p)):
            ds = delays(Tp, kind, t1p)
            for d in ds: jobs.append((q, kind, float(d))); secs += SHOTS * (d * 1e-6 + rep)
    print('qubits', qs, 'control', ctrl, 'circuits', len(jobs), 'estimated QPU seconds about %.0f' % secs)
    if a.estimate or not a.yes: print('not submitted (add --yes to submit on your account)'); return
    dt = be.dt; gran = getattr(be.target, 'granularity', None) or 16; built = [circuit(k, d, QuantumCircuit, dt, gran) for q, k, d in jobs]
    jobs = [(q, k, act) for (q, k, d), (c, act) in zip(jobs, built)]
    circs = [transpile(c, be, initial_layout=[q], optimization_level=0) for (q, k, _), (c, act) in zip(jobs, built)]
    job = SamplerV2(mode=be).run([(c,) for c in circs], shots=SHOTS); print('job', job.job_id(), 'submitted'); res = job.result()
    cnt = {}
    for (q, k, d), pr in zip(jobs, res):
        c = pr.data.c.get_counts(); cnt.setdefault((q, k), []).append((d, c.get('1', 0) if k == 't1' else c.get('0', 0)))
    out = dict(backend=a.backend, job_id=job.job_id(), ran=D.datetime.now(D.timezone.utc).isoformat(), shots=SHOTS, control=ctrl, qubits={})
    for q in qs:
        t1p, t2p, d1, d2, stamp = published(be, q); a1 = np.array(sorted(cnt[(q, 't1')])); a2 = np.array(sorted(cnt[(q, 't2')]))
        r = outcome(a1[:, 0], a2[:, 0], a1[:, 1], a2[:, 1], SHOTS); r.update(published_t1_us=t1p, published_t2_us=t2p, published_t1_date=d1, published_t2_date=d2, published_record=stamp, counts_t1=a1.tolist(), counts_t2=a2.tolist()); out['qubits'][str(q)] = r
    if out['qubits'][str(ctrl)]['outcome'] == 'ABOVE':
        for q, r in out['qubits'].items():
            if int(q) != ctrl: r['outcome_before_known_good'] = r['outcome']; r['outcome'] = 'CANNOT_TELL'
        out['known_good'] = 'FAILED: the control read ABOVE'
    else: out['known_good'] = 'passed' if out['qubits'][str(ctrl)]['outcome'] in ('CONSISTENT', 'CANNOT_TELL') else 'failed'
    json.dump(out, open(a.out, 'w'), indent=1); print('known-good:', out['known_good'])
    for q, r in out['qubits'].items(): print('q', q, r['outcome'], {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items() if k in ('t1_us', 't2_us', 'ratio', 'published_t1_us', 'published_t2_us')})
if __name__ == '__main__': main()
