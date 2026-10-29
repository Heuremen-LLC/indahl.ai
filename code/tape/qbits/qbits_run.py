#!/usr/bin/env python3
"""qbits_run.py: quantum bits for the TAPE beacon and a fairness reading per processor. See ../PLAN.md Addendum 2 and PLAN_QBITS.md.text (committed before this code).
  python3 qbits_run.py --selftest                          no device: planted worlds
  python3 qbits_run.py --estimate --backend ibm_fez        prints the plan and the estimate, submits nothing
  python3 qbits_run.py --backend ibm_fez --yes             submits ONE job
Key and instance: environment IBM_QUANTUM_TOKEN and IBM_QUANTUM_INSTANCE. Never written to disk, never printed."""
import os, sys, json, math, hashlib, argparse, datetime as D
import numpy as np
SHOTS_PLUS, SHOTS_Z, MAXSEC, MIN_REMAIN, EST_PER_SHOT = 4096, 1024, 20, 300, 4.0e-4
NRAND, SHOTS_R, TAG = 32, 128, 'tape-qbits-20261029'
H = os.path.dirname(os.path.abspath(__file__))
def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 1.0)
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); s = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)); return ((c - s) / d, (c + s) / d)
def analyse(plus, rprep, rread, z0, z1, stated=None):
    """plus: (shots, qubits) Hadamard readings. rprep: (R, qubits) the 0/1 each qubit was prepared in for each of R random-pattern circuits; rread: (R, shots, qubits) their readings.
    z0, z1: (shots, qubits) readings of no gate and of X. stated: optional dict of IBM's published per-qubit prob_meas1_prep0 and prob_meas0_prep1 with the record stamps."""
    S, Q = plus.shape; k = plus.sum(0); p = k / S
    # readout error in the same neighbour context as the Hadamard circuit: qubits prepared in random patterns (/q 29 Oct: all-0 and all-1 contexts are not the Hadamard context)
    R = rprep.shape[0]; n0 = (rprep == 0).sum(0) * rread.shape[1]; n1 = (rprep == 1).sum(0) * rread.shape[1]
    e01 = np.array([rread[:, :, q][rprep[:, q] == 0].sum() / max(n0[q], 1) for q in range(Q)]); e10 = np.array([1 - rread[:, :, q][rprep[:, q] == 1].sum() / max(n1[q], 1) for q in range(Q)])
    pred = 0.5 * (e01 + 1 - e10)
    se = np.sqrt(np.maximum(p * (1 - p), 1e-12) / S + (np.maximum(e01 * (1 - e01), 1e-12) / np.maximum(n0, 1) + np.maximum(e10 * (1 - e10), 1e-12) / np.maximum(n1, 1)) / 4)
    match = float(np.mean(np.abs(p - pred) <= 2 * se)); out_q = int(np.sum(np.abs(p - 0.5) > 3 * np.sqrt(0.25 / S)))
    m = float(p.mean()); sd = float(p.std(ddof=1)) if Q > 1 else 0.0; half = 1.96 * sd / math.sqrt(max(Q, 1)); lo, hi = m - half, m + half   # the qubit is the unit (/q check 22), not the shot
    r = np.array([np.corrcoef(plus[:, i], plus[:, i + 1])[0, 1] for i in range(Q - 1) if plus[:, i].std() > 0 and plus[:, i + 1].std() > 0]) if Q > 1 else np.array([])
    rlim = 3 / math.sqrt(S); corr_pairs = int(np.sum(np.abs(r) > rlim)) if r.size else 0
    stuck = int(np.sum((p < 0.02) | (p > 0.98)))
    outcome = 'CANNOT_TELL' if S < 100 else ('CONSISTENT' if lo <= 0.5 <= hi else ('ABOVE' if lo > 0.5 else 'BELOW'))
    flags = []
    if stuck: flags.append('stuck qubits %d' % stuck)
    if out_q > max(3, 0.02 * Q): flags.append('qubits beyond 3 sigma of a fair coin: %d of %d' % (out_q, Q))
    if corr_pairs > max(3, 0.05 * len(r)): flags.append('adjacent pairs correlated: %d of %d' % (corr_pairs, len(r)))
    if match < 0.8: flags.append('Hadamard readings match the prediction from the random-context readouts on only %.0f%% of qubits' % (100 * match))
    out = dict(shots=S, qubits=Q, mean_qubit_p1=m, mean_ci=[lo, hi], outcome=outcome, median_abs_bias=float(np.median(np.abs(p - 0.5))), qubits_beyond_3sigma=out_q, adjacent_pairs=int(len(r)), correlated_pairs=corr_pairs,
                stuck=stuck, match_prediction=match, flags=flags, usable=not flags, p1_by_qubit=[round(float(x), 5) for x in p])
    # stated against delivered: IBM's published readout errors against the pure-context circuits (all 0, all X)
    if stated and stated.get('stable'):
        d01 = z0.mean(0); d10 = 1 - z1.mean(0); res = {}
        for nm, dv, st, nn in (('prob_meas1_prep0', d01, np.array(stated['prob_meas1_prep0'], float), z0.shape[0]), ('prob_meas0_prep1', d10, np.array(stated['prob_meas0_prep1'], float), z1.shape[0])):
            ok = ~np.isnan(st); ci = [wilson(int(round(dv[q] * nn)), nn) for q in range(Q)]
            inside = [ci[q][0] <= st[q] <= ci[q][1] for q in range(Q) if ok[q]]; rat = [dv[q] / st[q] for q in range(Q) if ok[q] and st[q] > 0]
            res[nm] = dict(qubits=int(ok.sum()), stated_inside_delivered_interval=float(np.mean(inside)) if inside else None, median_delivered_over_stated=float(np.median(rat)) if rat else None)
        out['stated_vs_delivered'] = res; out['record_stamp'] = stated.get('stamp')
    elif stated: out['stated_vs_delivered'] = 'CANNOT_TELL: the published record changed during the job'
    return out
def pack(plus):
    return np.packbits(plus.astype(np.uint8).ravel()).tobytes()
def sim_world(rng, S, Q, p_plus=None, e01=None, e10=None, corr=0.0, xtalk=0.0, stuck=0, biased=0):
    """a planted world. True bit b_i; readout flips with a base error and, when xtalk > 0, an extra 1-to-0 or 0-to-1 error when the neighbour below is 1. Returns the arrays analyse() wants."""
    e01 = np.full(Q, 0.0 if e01 is None else e01); e10 = np.full(Q, 0.0 if e10 is None else e10)
    def read(b):
        prev = np.zeros_like(b); prev[:, 1:] = b[:, :-1]
        f01 = e01 + xtalk * prev; f10 = e10
        flip = np.where(b == 0, rng.random(b.shape) < f01, rng.random(b.shape) < f10); return (b ^ flip).astype(np.uint8)
    pp = np.full(Q, 0.5 if p_plus is None else p_plus)
    if biased: pp[:biased] = 0.58
    bp = (rng.random((S, Q)) < pp).astype(np.uint8)
    if corr: m = rng.random((S, Q - 1)) < corr; bp[:, 1:] = np.where(m, bp[:, :-1], bp[:, 1:])
    if stuck: bp[:, :stuck] = 0
    plus = read(bp); z0 = read(np.zeros((S, Q), np.uint8)); z1 = read(np.ones((S, Q), np.uint8))
    rprep = (rng.random((NRAND, Q)) < 0.5).astype(np.uint8); rread = np.stack([read(np.tile(rprep[r], (SHOTS_R, 1))) for r in range(NRAND)])
    return plus, rprep, rread, z0, z1
def selftest():
    rng = np.random.default_rng(11); S, Q = 2048, 64; res = {}
    def show(name, r): res[name] = r; print('%-34s outcome %-11s mean p1 %.4f usable %-5s flags %s' % (name, r['outcome'], r['mean_qubit_p1'], r['usable'], r['flags']))
    show('fair', analyse(*sim_world(rng, S, Q)))
    show('readout asymmetry only', analyse(*sim_world(rng, S, Q, e01=0.01, e10=0.03)))
    show('readout crosstalk', analyse(*sim_world(rng, S, Q, e01=0.01, e10=0.03, xtalk=0.06)))
    w = sim_world(rng, S, Q, e01=0.01, e10=0.03, xtalk=0.06); naive = analyse(w[0], np.tile(np.zeros((1, Q), np.uint8), (NRAND, 1)), np.stack([w[3]] * NRAND), w[3], w[4])
    print('%-34s the all-0 and all-1 prediction alone would read usable %s, match %.0f%% (the fix matters)' % ('readout crosstalk, naive', naive['usable'], 100 * naive['match_prediction']))
    show('twelve biased qubits', analyse(*sim_world(rng, S, Q, biased=12)))
    show('three stuck qubits', analyse(*sim_world(rng, S, Q, stuck=3)))
    show('neighbours copy 30 percent', analyse(*sim_world(rng, S, Q, corr=0.3)))
    show('too few shots', analyse(*sim_world(rng, 60, Q)))
    # the floor: how often a fair world is flagged (/q check 16)
    fl = sum(1 for _ in range(200) if not analyse(*sim_world(rng, 1024, 32))['usable']); floor = fl / 200.0; print('FLOOR: %d of 200 fair worlds flagged, %.1f percent (the plan requires at most 5 percent)' % (fl, 100 * floor))
    ok = (res['fair']['usable'] and res['readout asymmetry only']['usable'] and res['readout crosstalk']['usable'] and not res['twelve biased qubits']['usable'] and not res['three stuck qubits']['usable']
          and not res['neighbours copy 30 percent']['usable'] and res['too few shots']['outcome'] == 'CANNOT_TELL' and floor <= 0.05 and not naive['usable'])
    print('SELFTEST', 'PASS' if ok else 'FAIL'); return ok
def ordertest():
    """the qubit-order check (/q check 17) with Qiskit's own local sampler: X on qubit 2 only must read 1 at index 2 of our unpacked rows."""
    from qiskit import QuantumCircuit
    from qiskit.primitives import StatevectorSampler
    n = 11; c = QuantumCircuit(n, n); c.x(2); c.x(9); c.measure(range(n), range(n)); r = StatevectorSampler().run([(c, None, 5)]).result()[0]; ba = r.data.c
    a2 = np.unpackbits(ba.array, axis=1); w = a2.shape[1]; a2 = a2[:, w - ba.num_bits:][:, ::-1]
    ok = [int(x) for x in a2[0]] == [0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0]; print('ORDERTEST', 'PASS' if ok else 'FAIL', [int(x) for x in a2[0]]); return ok
def circuits(n, patterns):
    from qiskit import QuantumCircuit
    out = []
    def mk(name, xs, h=False):
        c = QuantumCircuit(n, n)
        for q in range(n):
            if q in xs: c.x(q)
            if h: c.h(q)
        c.measure(range(n), range(n)); c.name = name; return c
    out.append(mk('z0', set())); out.append(mk('z1', set(range(n)))); out.append(mk('plus', set(), True))
    for r in range(patterns.shape[0]): out.append(mk('rand%d' % r, set(int(q) for q in np.nonzero(patterns[r])[0])))
    return out
def service():
    from qiskit_ibm_runtime import QiskitRuntimeService
    return QiskitRuntimeService(channel='ibm_cloud', token=os.environ['IBM_QUANTUM_TOKEN'], instance=os.environ['IBM_QUANTUM_INSTANCE'])
def stated_record(be, n):
    pr = be.properties(); g = lambda nm: [pr.qubit_property(q, nm)[0] if pr.qubit_property(q, nm) else float('nan') for q in range(n)]
    return dict(prob_meas1_prep0=g('prob_meas1_prep0'), prob_meas0_prep1=g('prob_meas0_prep1'), stamp=str(pr.last_update_date))
def bits(r):
    ba = r.data.c; a2 = np.unpackbits(ba.array, axis=1); w = a2.shape[1]; a2 = a2[:, w - ba.num_bits:]; return a2[:, ::-1].astype(np.uint8)   # qubit 0 first
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--selftest', action='store_true'); ap.add_argument('--ordertest', action='store_true'); ap.add_argument('--estimate', action='store_true'); ap.add_argument('--yes', action='store_true'); ap.add_argument('--backend'); a = ap.parse_args()
    if a.selftest: sys.exit(0 if selftest() else 1)
    if a.ordertest: sys.exit(0 if ordertest() else 1)
    if not a.backend: sys.exit('--backend needed')
    s = service(); be = s.backend(a.backend); n = be.num_qubits
    shots = [SHOTS_Z, SHOTS_Z, SHOTS_PLUS] + [SHOTS_R] * NRAND; est = sum(shots) * EST_PER_SHOT
    u = s.usage(); rem = u['usage_remaining_seconds']; pend = be.status().pending_jobs
    print('backend %s, %d qubits, pending jobs %d. Circuits: no gate (%d shots), X (%d), Hadamard (%d), and %d random-pattern circuits (%d shots each), all qubits in one job. Raw bits: %d.' % (a.backend, n, pend, SHOTS_Z, SHOTS_Z, SHOTS_PLUS, NRAND, SHOTS_R, SHOTS_PLUS * n))
    print('Estimated QPU seconds %.1f (an estimate from %.1e s per shot, not a measurement). Account seconds remaining %d. Cap per run %d, minimum to remain %d.' % (est, EST_PER_SHOT, rem, MAXSEC, MIN_REMAIN))
    if est > MAXSEC or rem - est < MIN_REMAIN: sys.exit('REFUSED by the plan limits.')
    prior = [j.job_id() for j in s.jobs(limit=50, backend_name=a.backend) if TAG in (j.tags or [])]
    if prior: sys.exit('REFUSED: a job with tag %s already exists on %s: %s. List jobs before any refire.' % (TAG, a.backend, prior))
    if not a.yes: print('Submits nothing without --yes.'); return
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from qiskit_ibm_runtime import SamplerV2
    rng = np.random.default_rng(17); patterns = (rng.random((NRAND, n)) < 0.5).astype(np.uint8)
    pm = generate_preset_pass_manager(optimization_level=0, backend=be, initial_layout=list(range(n))); isa = [pm.run(c) for c in circuits(n, patterns)]
    rec0 = stated_record(be, n); sam = SamplerV2(mode=be)
    try: sam.options.max_execution_time = MAXSEC
    except Exception as e: print('max_execution_time not set:', e)
    try: sam.options.environment.job_tags = [TAG]
    except Exception as e: print('tag not set:', e)
    job = sam.run([(isa[i], None, shots[i]) for i in range(len(isa))]); jid = job.job_id(); print('job', jid, flush=True)
    t = D.datetime.now(D.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    try: res = job.result()
    except Exception as e: print('NOTHING_RETURNED', type(e).__name__, str(e)[:200]); json.dump(dict(backend=a.backend, job_id=jid, t=t, outcome='NOTHING_RETURNED'), open(H + '/runs/failed_%s.json' % t, 'w')); sys.exit(1)
    rec1 = stated_record(be, n); stable = rec0['stamp'] == rec1['stamp']; rec0['stable'] = stable
    z0, z1, plus = bits(res[0]), bits(res[1]), bits(res[2]); rread = np.stack([bits(res[3 + r]) for r in range(NRAND)])
    rd = analyse(plus, patterns, rread, z0, z1, rec0); raw = pack(plus); ext = hashlib.sha256(raw).hexdigest()
    try: used = job.usage()
    except Exception: used = None
    try: met = job.metrics()
    except Exception: met = None
    out = dict(backend=a.backend, job_id=jid, tag=TAG, t=t, shots=SHOTS_PLUS, qubits=n, raw_sha256=hashlib.sha256(raw).hexdigest(), extracted=ext, reading=rd, qpu_seconds_used=used, job_metrics=met, estimate=est, remaining_before=rem, record_stamps=[rec0['stamp'], rec1['stamp']])
    os.makedirs(H + '/runs', exist_ok=True); os.makedirs(H + '/new', exist_ok=True)
    open(H + '/runs/%s_%s.bits' % (a.backend, t), 'wb').write(raw); json.dump(out, open(H + '/runs/%s_%s.json' % (a.backend, t), 'w'), indent=1, default=str); json.dump(out, open(H + '/new/%s_%s.json' % (a.backend, t), 'w'), default=str)
    print(json.dumps({k: out[k] for k in ('backend', 'job_id', 'extracted', 'qpu_seconds_used')}, default=str), rd['outcome'], rd['flags'])
if __name__ == '__main__': main()
