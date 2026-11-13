"""clock.py -- does a fixed circuit's output on IBM hardware reveal WHEN it ran? (PLAN_CLOCK.md) The test behind HSBC + IBM
arXiv:2509.17715, whose own text says "we cannot exclude that the order of processing these quantum circuits on hardware ... would yield
some form of non-trivial information leakage with respect to the RFQ outcome labels".
One fixed input (seed 0): RX(theta_q) on every qubit, then 2 blocks of Heisenberg couplings (RZZ, RXX, RYY at 0.2 rad) on every coupling
edge (three edge colourings), measure all. SamplerV2, 4096 shots, Pauli twirling on (as the paper used). The SAME circuit is run as J
sequential jobs (each submitted when the previous returns). Features per job = per-qubit <Z>, also from two half-shot splits.
Readings:
  R1 DRIFT  per qubit, between-job variance of <Z> against the shot-noise variance from the half splits; share of qubits whose excess is
            significant (F test with (J-1, J) degrees of freedom, 1 % per qubit); chip-level F with permutation null.
  R2 CLOCK  leave-one-job-out ridge regression from the per-qubit features to the job's run time; R^2 and mean absolute error (minutes);
            null = the same with run times shuffled (2000 permutations); ABOVE if the observed R^2 exceeds the null's 95th percentile.
  clock.py --synth null|drift | CHIP --fire J | --analyze CHIP"""
import os, sys, json, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); H = os.path.expanduser('~/bones-forge')
KEYFILE, INSTANCE = '.ibm_quantum_key_3', 'Darkwave Disco'; SHOTS = 4096

def circuit(b):
    from qiskit import QuantumCircuit
    n = b.num_qubits; rng = np.random.default_rng(0); qc = QuantumCircuit(n)
    qc.rx(rng.uniform(0, np.pi, n), range(n)) if False else [qc.rx(float(t), q) for q, t in enumerate(rng.uniform(0, np.pi, n))]
    edges = sorted({tuple(sorted(e)) for e in b.coupling_map.get_edges()}); colours = []
    left = list(edges)
    while left:
        used, c, rest = set(), [], []
        for e in left:
            if e[0] in used or e[1] in used: rest.append(e)
            else: c.append(e); used |= set(e)
        colours.append(c); left = rest
    for _ in range(2):
        for c in colours:
            for a, z in c: qc.rzz(0.2, a, z); qc.rxx(0.2, a, z); qc.ryy(0.2, a, z)
    qc.measure_all(); return qc

def features(bits):
    z = 1 - 2 * bits.astype(float); h = bits.shape[0] // 2
    return z.mean(0), z[:h].mean(0), z[h:].mean(0)

def readings(F, A, B, t, label, rng=None):
    rng = rng or np.random.default_rng(1); J, n = F.shape
    sn = ((A - B) ** 2).mean(0) / 4                     # shot-noise variance of the full-shot mean per qubit
    vb = F.var(0, ddof=1); ratio = vb / np.maximum(sn, 1e-9)
    from scipy.stats import f as fdist          # shot noise is itself ESTIMATED from J half-split pairs: an F test, not chi-square
    p = fdist.sf(ratio, J - 1, J); frac = float((p < 0.01).mean())
    Fchip = float(np.median(vb / np.maximum(sn, 1e-9)))
    print(f'-- {label}: {J} jobs over {(t.max() - t.min()) / 60:.1f} min, {n} qubits')
    print(f'   R1 DRIFT: qubits with between-job variance beyond shot noise (p < 0.01): {100 * frac:.1f} % (null expects 1 %) | median variance ratio {Fchip:.2f} (null 1)')
    def loo_r2(y):
        Xc = F - F.mean(0); pred = np.zeros(J)
        for k in range(J):
            m = np.ones(J, bool); m[k] = False; X = Xc[m]; yk = y[m] - y[m].mean()
            lam = 1e-2 * np.trace(X @ X.T) / J
            w = X.T @ np.linalg.solve(X @ X.T + lam * np.eye(m.sum()), yk); pred[k] = Xc[k] @ w + y[m].mean()
        return 1 - ((pred - y) ** 2).sum() / ((y - y.mean()) ** 2).sum(), np.abs(pred - y).mean() / 60
    r2, mae = loo_r2(t); null = [loo_r2(rng.permutation(t))[0] for _ in range(2000)]; q95 = float(np.percentile(null, 95))
    out = 'ABOVE' if r2 > q95 else 'CONSISTENT'
    print(f'   R2 CLOCK: leave-one-job-out R^2 {r2:.3f}, mean error {mae:.1f} min | shuffled-time null 95th pct {q95:.3f} -> {out} (p = {np.mean(np.array(null) >= r2):.4f})')
    return dict(frac=frac, Fchip=Fchip, r2=r2, mae=mae, q95=q95, out=out)

def synth(world, J=16, n=156, seed=4):
    rng = np.random.default_rng(seed); base = rng.uniform(-0.6, 0.6, n); t = np.cumsum(rng.uniform(40, 70, J)); F, A, B = [], [], []
    walk = np.zeros(n)
    for k in range(J):
        if world == 'drift': walk = walk + rng.normal(0, 0.006, n)
        p = np.clip((1 - (base + walk)) / 2, 0, 1); bits = rng.random((SHOTS, n)) < p; f, a, b = features(bits); F.append(f); A.append(a); B.append(b)
    return readings(np.array(F), np.array(A), np.array(B), t, f'synth {world}')

def service():
    from qiskit_ibm_runtime import QiskitRuntimeService
    tok = open(H + '/' + KEYFILE).read().strip(); s = QiskitRuntimeService(channel='ibm_quantum_platform', token=tok)
    crn = [i['crn'] for i in s.instances() if i.get('name') == INSTANCE][0]
    return QiskitRuntimeService(channel='ibm_quantum_platform', token=tok, instance=crn)

if __name__ == '__main__':
    a = sys.argv
    if '--synth' in a: synth(a[a.index('--synth') + 1]); sys.exit(0)
    if '--analyze' in a:
        chip = a[-1]; d = np.load(f'{HERE}/raw_clock_{chip}.npz'); rec = json.load(open(f'{HERE}/job_clock_{chip}.json'))
        F, A, B = [], [], []
        for k in range(len(rec['jobs'])): f, x, y = features(d[f'b_{k}']); F.append(f); A.append(x); B.append(y)
        t = np.array([j['run_epoch'] for j in rec['jobs']], float)
        print(f'=== {chip}: jobs {rec["jobs"][0]["job_id"]} .. {rec["jobs"][-1]["job_id"]}')
        readings(np.array(F), np.array(A), np.array(B), t - t.min(), chip); sys.exit(0)
    chip = a[a.index('--fire') + 1]; J = int(a[a.index('--fire') + 2]); s = service(); b = s.backend(chip)
    from qiskit import transpile
    from qiskit_ibm_runtime import SamplerV2
    tq = transpile(circuit(b), b, optimization_level=1, seed_transpiler=7)
    print(f'{chip}: {tq.num_qubits} qubits, ops {dict((k, v) for k, v in tq.count_ops().items() if k in ("cz", "sx", "measure"))}, est {SHOTS * (tq.estimate_duration(b.target, "s") + 290e-6):.1f} s/job, remaining {s.usage().get("usage_remaining_seconds")}', flush=True)
    json.dump(b.properties().to_dict(), open(f'{HERE}/props_clock_{chip}.json', 'w'), default=str)
    smp = SamplerV2(mode=b); smp.options.default_shots = SHOTS; smp.options.twirling.enable_gates = True; smp.options.twirling.num_randomizations = 'auto'
    rec = dict(chip=chip, shots=SHOTS, jobs=[]); out = {}
    for k in range(J):
        job = smp.run([tq]); r = job.result(); bits = r[0].data.meas.to_bool_array(order='little')
        ts = job.metrics().get('timestamps', {}); run = ts.get('running') or ts.get('created')
        import datetime as dt
        ep = dt.datetime.fromisoformat(run.replace('Z', '+00:00')).timestamp()
        rec['jobs'].append(dict(k=k, job_id=job.job_id(), running=run, run_epoch=ep, usage=job.metrics().get('usage', {}).get('quantum_seconds')))
        out[f'b_{k}'] = bits; np.savez_compressed(f'{HERE}/raw_clock_{chip}.npz', **out); json.dump(rec, open(f'{HERE}/job_clock_{chip}.json', 'w'), default=str)
        print(f'   job {k + 1}/{J} {job.job_id()} ran {run}', flush=True)
    print('DONE', chip, 'remaining', s.usage().get('usage_remaining_seconds'))
