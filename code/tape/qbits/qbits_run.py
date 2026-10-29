#!/usr/bin/env python3
"""qbits_run.py: quantum bits for the TAPE beacon and a fairness reading per processor. See ../PLAN.md Addendum 2 and PLAN_QBITS.md.text (committed before this code).
  python3 qbits_run.py --selftest                          no device: planted worlds
  python3 qbits_run.py --estimate --backend ibm_fez        prints the plan and the estimate, submits nothing
  python3 qbits_run.py --backend ibm_fez --yes             submits ONE job
Key and instance: environment IBM_QUANTUM_TOKEN and IBM_QUANTUM_INSTANCE. Never written to disk, never printed."""
import os, sys, json, math, hashlib, argparse, datetime as D
import numpy as np
SHOTS_PLUS, SHOTS_Z, MAXSEC, MIN_REMAIN, EST_PER_SHOT = 4096, 1024, 20, 300, 4.0e-4
H = os.path.dirname(os.path.abspath(__file__))
def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 1.0)
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); s = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)); return ((c - s) / d, (c + s) / d)
def analyse(plus, z0, z1):
    """plus: (shots, qubits) 0/1 array of Hadamard readings. z0, z1: (shots, qubits) readings of no gate and X. Returns the fairness reading."""
    S, Q = plus.shape; k = plus.sum(0); p = k / S
    e01 = z0.mean(0); e10 = 1 - z1.mean(0); pred = 0.5 * (e01 + 1 - e10)
    se = np.sqrt(np.maximum(p * (1 - p), 1e-12) / S + (np.maximum(e01 * (1 - e01), 1e-12) / z0.shape[0] + np.maximum(e10 * (1 - e10), 1e-12) / z1.shape[0]) / 4)
    match = float(np.mean(np.abs(p - pred) <= 2 * se)); out_q = int(np.sum(np.abs(p - 0.5) > 3 * np.sqrt(0.25 / S)))
    pooled_k, pooled_n = int(k.sum()), S * Q; lo, hi = wilson(pooled_k, pooled_n)
    r = np.array([np.corrcoef(plus[:, i], plus[:, i + 1])[0, 1] for i in range(Q - 1) if plus[:, i].std() > 0 and plus[:, i + 1].std() > 0]) if Q > 1 else np.array([])
    rlim = 3 / math.sqrt(S); corr_pairs = int(np.sum(np.abs(r) > rlim)) if r.size else 0
    stuck = int(np.sum((p < 0.02) | (p > 0.98)))
    outcome = 'CONSISTENT' if lo <= 0.5 <= hi else ('ABOVE' if lo > 0.5 else 'BELOW')
    flags = []
    if stuck: flags.append('stuck qubits %d' % stuck)
    if out_q > max(3, 0.02 * Q): flags.append('qubits beyond 3 sigma of a fair coin: %d of %d' % (out_q, Q))
    if corr_pairs > max(3, 0.05 * len(r)): flags.append('adjacent pairs correlated: %d of %d' % (corr_pairs, len(r)))
    if match < 0.8: flags.append('Hadamard readings match the prediction from the 0 and 1 readouts on only %.0f%% of qubits' % (100 * match))
    return dict(shots=S, qubits=Q, pooled_p1=pooled_k / pooled_n, pooled_ci=[lo, hi], outcome=outcome, median_abs_bias=float(np.median(np.abs(p - 0.5))), qubits_beyond_3sigma=out_q, adjacent_pairs=int(len(r)), correlated_pairs=corr_pairs,
                stuck=stuck, match_prediction=match, flags=flags, usable=not flags)
def pack(plus):
    return np.packbits(plus.astype(np.uint8).ravel()).tobytes()
def selftest():
    rng = np.random.default_rng(11); S, Q = 2048, 64; res = {}
    def world(name, p, corr=0.0, e01=0.0, e10=0.0):
        pl = (rng.random((S, Q)) < p).astype(np.uint8)
        if corr: m = rng.random((S, Q - 1)) < corr; pl[:, 1:] = np.where(m, pl[:, :-1], pl[:, 1:])
        z0 = (rng.random((S, Q)) < e01).astype(np.uint8); z1 = (rng.random((S, Q)) >= e10).astype(np.uint8)
        r = analyse(pl, z0, z1); res[name] = r; print('%-34s outcome %-10s pooled %.4f usable %-5s flags %s' % (name, r['outcome'], r['pooled_p1'], r['usable'], r['flags']))
    world('fair', 0.5)
    world('readout asymmetry only', 0.5 * (0.01 + 1 - 0.03), e01=0.01, e10=0.03)
    pb = np.full(Q, 0.5); pb[:12] = 0.58; pb = np.tile(pb, (1, 1))[0]
    pl = (rng.random((S, Q)) < pb).astype(np.uint8); r = analyse(pl, np.zeros((S, Q), np.uint8), np.ones((S, Q), np.uint8)); res['twelve biased qubits'] = r; print('%-34s outcome %-10s pooled %.4f usable %-5s flags %s' % ('twelve biased qubits', r['outcome'], r['pooled_p1'], r['usable'], r['flags']))
    pl = (rng.random((S, Q)) < 0.5).astype(np.uint8); pl[:, :3] = 0; r = analyse(pl, np.zeros((S, Q), np.uint8), np.ones((S, Q), np.uint8)); res['three stuck qubits'] = r; print('%-34s outcome %-10s pooled %.4f usable %-5s flags %s' % ('three stuck qubits', r['outcome'], r['pooled_p1'], r['usable'], r['flags']))
    world('neighbours copy 30 percent', 0.5, corr=0.3)
    ok = res['fair']['usable'] and res['readout asymmetry only']['usable'] and not res['twelve biased qubits']['usable'] and not res['three stuck qubits']['usable'] and not res['neighbours copy 30 percent']['usable']
    print('SELFTEST', 'PASS' if ok else 'FAIL'); return ok
def circuits(n):
    from qiskit import QuantumCircuit
    out = []
    for kind in ('z0', 'z1', 'plus'):
        c = QuantumCircuit(n, n)
        for q in range(n):
            if kind == 'z1': c.x(q)
            if kind == 'plus': c.h(q)
        c.measure(range(n), range(n)); c.name = kind; out.append(c)
    return out
def service():
    from qiskit_ibm_runtime import QiskitRuntimeService
    return QiskitRuntimeService(channel='ibm_cloud', token=os.environ['IBM_QUANTUM_TOKEN'], instance=os.environ['IBM_QUANTUM_INSTANCE'])
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--selftest', action='store_true'); ap.add_argument('--estimate', action='store_true'); ap.add_argument('--yes', action='store_true'); ap.add_argument('--backend'); a = ap.parse_args()
    if a.selftest: sys.exit(0 if selftest() else 1)
    if not a.backend: sys.exit('--backend needed')
    s = service(); be = s.backend(a.backend); n = be.num_qubits; shots = [SHOTS_Z, SHOTS_Z, SHOTS_PLUS]; est = sum(shots) * EST_PER_SHOT
    u = s.usage(); rem = u['usage_remaining_seconds']; pend = be.status().pending_jobs
    print('backend %s, %d qubits, pending jobs %d. Circuits: no gate (%d shots), X (%d shots), Hadamard (%d shots), all qubits in one job. Raw bits: %d.' % (a.backend, n, pend, SHOTS_Z, SHOTS_Z, SHOTS_PLUS, SHOTS_PLUS * n))
    print('Estimated QPU seconds %.1f (an estimate from %.1e s per shot, not a measurement). Account seconds remaining %d. Cap per run %d, minimum to remain %d.' % (est, EST_PER_SHOT, rem, MAXSEC, MIN_REMAIN))
    if est > MAXSEC or rem - est < MIN_REMAIN: sys.exit('REFUSED by the plan limits.')
    if not a.yes: print('Submits nothing without --yes.'); return
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from qiskit_ibm_runtime import SamplerV2
    pm = generate_preset_pass_manager(optimization_level=0, backend=be, initial_layout=list(range(n))); isa = [pm.run(c) for c in circuits(n)]
    sam = SamplerV2(mode=be)
    try: sam.options.max_execution_time = MAXSEC
    except Exception as e: print('max_execution_time not set:', e)
    job = sam.run([(isa[i], None, shots[i]) for i in range(3)]); jid = job.job_id(); print('job', jid, flush=True)
    res = job.result(); t = D.datetime.now(D.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    def bits(r, shots_):
        ba = r.data.c; a2 = np.unpackbits(ba.array, axis=1); w = a2.shape[1]; a2 = a2[:, w - ba.num_bits:]   # shots x bits, most significant first
        return a2[:, ::-1].astype(np.uint8)                                                                      # qubit 0 first
    z0, z1, plus = [bits(r, 0) for r in res]
    rd = analyse(plus, z0, z1); raw = pack(plus); ext = hashlib.sha256(raw).hexdigest()
    try: used = job.usage()
    except Exception: used = None
    out = dict(backend=a.backend, job_id=jid, t=t, shots=SHOTS_PLUS, qubits=n, raw_sha256=hashlib.sha256(raw).hexdigest(), extracted=ext, reading=rd, qpu_seconds_used=used, estimate=est, remaining_before=rem)
    os.makedirs(H + '/runs', exist_ok=True); os.makedirs(H + '/new', exist_ok=True)
    open(H + '/runs/%s_%s.bits' % (a.backend, t), 'wb').write(raw); json.dump(out, open(H + '/runs/%s_%s.json' % (a.backend, t), 'w'), indent=1); json.dump(out, open(H + '/new/%s_%s.json' % (a.backend, t), 'w'))
    print(json.dumps({k: out[k] for k in ('backend', 'job_id', 'extracted', 'qpu_seconds_used')}), rd['outcome'], rd['flags'])
if __name__ == '__main__': main()
