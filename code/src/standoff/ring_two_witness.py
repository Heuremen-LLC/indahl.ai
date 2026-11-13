"""THE RING -- two-witness KCBS contextuality on Rigetti Cepheus qutrits (q0 and q90), quantum-coin ordering, a time ruler.
2026-09-26, Bones (Wayfinder: "two witnesses is what we've been missing... we flip quantum coins").

KCBS: five real unit vectors v_j = (cos t, sin t cos(4 pi j/5), sin t sin(4 pi j/5)), cos^2 t = cos(pi/5)/(1+cos(pi/5)); v_j is
orthogonal to v_{j+1}. State |0> = (1,0,0): P(v_j) = cos^2 t = 0.4472 each; ring sum S = sqrt5 = 2.236. Any noncontextual model: S <= 2.
Context j = orthonormal basis {v_j, v_{j+1}, w_j}; a real orthogonal O_j maps it to |0>,|1>,|2>; read P0 = P(v_j), P1 = P(v_{j+1}).

WHY THIS IS CONVENTION-PROOF: O_j = G01(a) G12(b) G01(c) (real Givens rotations = Euler angles). We run X-type rotations instead
(01 drive pulse, f12 pulse, phase 0 or pi only). An X-type sequence = D (real sequence) D^dagger with D = diag(1, i, -1), and a sign
flip in either frame's rotation convention = conjugation by a diagonal +-1 matrix. Every such D fixes |0> (our state) and the readout
basis, so every probability is unchanged. No state prep, no free phases, no rz -- nothing whose sign we never measured.
Arbitrary 01 angles: a pulse on Transmon_q_charge_tx with the chip's own calibrated rx(pi) DRAG shape, amplitude scaled linearly by
angle/pi (the chip's own rx(pi/2) calibration is exactly half its rx(pi) amplitude -- checked). Negative angles: shift_phase pi.
f12 on q0: step 1's Rabi (a_pi 0.494, 32 ns shape). f12 on q90: calibrated here by a short Rabi first.

Readout: two schemes per context (plain; rx(pi) before readout, which swaps 0<->1 and leaves 2). Raw: P0 = 1-a, P1 = 1-b.
Corrected: solve [Ca; Cb; 1] P = [a; b; 1] with each witness's confusion rows measured IN THE SAME JOB (interleaved).
Time ruler: every context at 0 us and 5 us wait before readout. Order: shuffled by quantum coins (pup_seeds.bin, bytes from the END).
  qvenv/bin/python ring_two_witness.py --sim | --rabi-submit | --rabi-collect | --submit | --collect | --analyze
"""
import hashlib, json, math, os, sys, time
import numpy as np
import braket_round1_step3 as s3

HERE = os.path.dirname(os.path.abspath(__file__))
DEVICE = s3.DEVICE
QS = (0, 90)
CAL01 = {int(k): v for k, v in json.load(open(os.path.join(HERE, 'ring_01cal.json'))).items()}
F12 = {0: {'len': 32e-9, 'sigma': 6.794574402304e-9, 'amp_pi': s3.A_PI12}}          # q90 filled from its Rabi
RABI_F = os.path.join(HERE, 'ring_rabi_q90.json')
if os.path.exists(os.path.join(HERE, 'ring_rabi_q90_fit.json')):
    F12[90] = {'len': 40e-9, 'sigma': 8.49321800288e-9, 'amp_pi': json.load(open(os.path.join(HERE, 'ring_rabi_q90_fit.json')))['a_pi_12']}
BUDGET = 33.0
BUDGET_START = 115.7325     # ledger spent_est when this job began; this job may add at most BUDGET
DELAYS_NS = (0, 5000)
SHOTS_MAIN = 1900
RABI_AMPS = [round(0.04 * k, 3) for k in range(9)]   # 0 .. 0.32
SHOTS_RABI = 300

# ---------------- KCBS geometry ----------------
T = math.acos(math.sqrt(math.cos(math.pi / 5) / (1 + math.cos(math.pi / 5))))
V = [np.array([math.cos(T), math.sin(T) * math.cos(4 * math.pi * j / 5), math.sin(T) * math.sin(4 * math.pi * j / 5)]) for j in range(5)]

def G01(t): c, s = math.cos(t), math.sin(t); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.]])
def G12(t): c, s = math.cos(t), math.sin(t); return np.array([[1., 0, 0], [0, c, -s], [0, s, c]])

def context_angles(j):
    """Euler angles (c, b, a) so that G01(a) G12(b) G01(c) maps v_j->e0, v_{j+1}->e1 (up to sign)."""
    a_, b_ = V[j], V[(j + 1) % 5]; w = np.cross(a_, b_); w /= np.linalg.norm(w)
    target = np.vstack([a_, b_, w])          # rows: O maps row_k -> e_k  =>  O = target (orthogonal)
    if np.linalg.det(target) < 0: target[2] *= -1
    R = target   # closed-form ZXZ Euler: R = G01(a) G12(b) G01(c) -> R[2,:] = [sb sc, sb cc, cb], R[:,2] = [sa sb, -ca sb, cb]
    bb = math.acos(max(-1.0, min(1.0, R[2, 2]))); cc = math.atan2(R[2, 0], R[2, 1]); aa = math.atan2(R[0, 2], -R[1, 2])
    x = np.array([cc, bb, aa]); err = np.linalg.norm(G01(aa) @ G12(bb) @ G01(cc) - R)
    return x, err

# ---------------- qutrit model, hardware conventions (same U as step 3) ----------------
def U(op):
    M = np.eye(3, dtype=complex); t = op[1]
    if op[0] == 'x01': M[0, 0] = M[1, 1] = math.cos(t / 2); M[0, 1] = M[1, 0] = -1j * math.sin(t / 2)
    else: M[1, 1] = M[2, 2] = math.cos(t / 2); M[1, 2] = M[2, 1] = -1j * math.sin(t / 2)
    return M

def ops_for(j):
    """X-type ops reproducing context j's Euler angles. Rotation G(theta) real <-> X(2*theta) (G is a half-angle-free rotation matrix;
    X(phi) has cos(phi/2)), so pulse angle = 2*Euler angle."""
    (c, b, a), _ = context_angles(j)
    w = lambda x: (x + math.pi) % (2 * math.pi) - math.pi   # 01 pulses are first and last: wrapping adds a -1 only on {0,1}, which is
    return [('x01', w(2 * c)), ('x12', 2 * b), ('x01', w(2 * a))]   # a global phase (first op, level 2 empty) or an output phase (last op)

def probs(ops):
    s = np.array([1, 0, 0], dtype=complex)
    for op in ops: s = U(op) @ s
    return np.abs(s) ** 2

def sim():
    print(f't = {T:.6f} rad; P(v_j) ideal = {math.cos(T)**2:.4f}; sqrt5 = {math.sqrt(5):.4f}')
    for j in range(5): assert abs(V[j] @ V[(j + 1) % 5]) < 1e-12
    S0 = S1 = 0
    for j in range(5):
        (c, b, a), err = context_angles(j)
        O = G01(a) @ G12(b) @ G01(c)
        p = probs(ops_for(j))
        pr = np.abs(O @ np.array([1., 0, 0])) ** 2
        print(f'context {j}: euler err {err:.1e}  pulses(rad) ' + ' '.join(f'{o[0]} {o[1]:+.4f}' for o in ops_for(j)) +
              f'  P0 {p[0]:.4f} P1 {p[1]:.4f} P2 {p[2]:.4f}  (real-O check {pr[0]:.4f} {pr[1]:.4f})')
        assert abs(p[0] - math.cos(T) ** 2) < 1e-6 and abs(p[1] - math.cos(T) ** 2) < 1e-6
        S0 += p[0]; S1 += p[1]
    print(f'ideal ring sum via outcome-0 channel {S0:.4f}, via outcome-1 channel {S1:.4f}')
    # expected RAW on hardware with step 2's measured q0 confusion
    R = json.load(open(os.path.join(HERE, 'step2_results.json')))['results']
    ra = {r['prep']: r['p_read1'] for r in R if r['part'] == 'A' and r['read'] == 'a'}
    rb = {r['prep']: r['p_read1'] for r in R if r['part'] == 'A' and r['read'] == 'b'}
    Sraw = 0
    for j in range(5):
        p = probs(ops_for(j)); a = sum(p[k] * ra[k] for k in range(3)); b = sum(p[k] * rb[k] for k in range(3))
        Sraw += (1 - a + 1 - b) / 2
    print(f'expected RAW ring sum on q0 with step-2 confusion (no decay): {Sraw:.4f}   noncontextual bound 2.0000')
    for j in range(5):
        for op in ops_for(j):
            q0amp = (CAL01[0]['amp_pi'] if op[0] == 'x01' else F12[0]['amp_pi']) * abs(op[1]) / math.pi
            assert q0amp <= 1.0, f'q0 amplitude {q0amp:.3f} > 1 in context {j}'
    print('all q0 pulse amplitudes <= 1')
    print(f'plan cost: rabi {len(RABI_AMPS)} x {SHOTS_RABI} = ${len(RABI_AMPS) * (s3.PER_TASK + SHOTS_RABI * s3.PER_SHOT):.2f}; '
          f'main {len(plan())} x {SHOTS_MAIN} = ${len(plan()) * (s3.PER_TASK + SHOTS_MAIN * s3.PER_SHOT):.2f}')

# ---------------- hardware ----------------
def plan():
    arms = [('cal', {'prep': k, 'read': r}) for k in (0, 1, 2) for r in ('a', 'b')]
    arms += [('ctx', {'j': j, 'read': r, 'delay_ns': d}) for j in range(5) for r in ('a', 'b') for d in DELAYS_NS]
    return arms

def coins(n, back=64):
    raw = open(os.path.join(HERE, 'pup_seeds.bin'), 'rb').read()
    off = len(raw) - back; sl = raw[off:off + 64]
    order = list(range(n)); stream = hashlib.sha256(sl).digest() + hashlib.sha256(sl[::-1]).digest(); k = 0
    for i in range(n - 1, 0, -1):   # Fisher-Yates with quantum bytes (extended through SHA-256 of the slice)
        v = int.from_bytes(stream[k:k + 2], 'big'); k += 2
        if k >= len(stream): stream += hashlib.sha256(stream).digest()
        jj = v % (i + 1); order[i], order[jj] = order[jj], order[i]
    return order, {'file': 'pup_seeds.bin', 'offset': off, 'len': 64, 'hex': sl.hex(), 'file_size_at_draw': len(raw)}

def ledger_check(cost, label):
    L = json.load(open(s3.LEDGER))
    if L['spent_est'] + cost > s3.CAP: raise SystemExit(f'BRAKE (cap): {label} ${cost:.2f} would pass ${s3.CAP}')
    tag = 'ring rerun:' if label.startswith('ring rerun:') else 'ring:'; cap_ = 23.0 if tag == 'ring rerun:' else BUDGET
    mine = sum(e['cost_est'] for e in L['entries'] if str(e.get('label', '')).startswith(tag))   # this job's own entries only (the ledger is shared)
    if mine + cost > cap_ + 1e-6: raise SystemExit(f'BRAKE (job budget ${cap_}): {label} ${cost:.2f}; this job has spent ${mine:.2f}')
    return L

def book(L, cost, label, n):
    L['spent_est'] = round(L['spent_est'] + cost, 4)
    L['entries'].append({'at': time.strftime('%Y-%m-%dT%H:%M:%S'), 'label': label, 'tasks': n, 'cost_est': round(cost, 4)})
    json.dump(L, open(s3.LEDGER, 'w'), indent=1)

def builder():
    from braket.circuits import Circuit
    from braket.aws import AwsDevice
    from braket.pulse import PulseSequence, DragGaussianWaveform
    dev = AwsDevice(DEVICE)
    fr01 = {q: dev.frames[f'Transmon_{q}_charge_tx'] for q in QS}; fr12 = {q: dev.frames[f'Transmon_{q}_charge_tx_f12'] for q in QS}
    def pulse(q, kind, theta):
        ps = PulseSequence(); neg = theta < 0; th = abs(theta)
        if kind == 'x01':
            c = CAL01[q]; fr = fr01[q]; wf = DragGaussianWaveform(c['len_ns'] * 1e-9, c['sigma_ns'] * 1e-9, c['beta'], float(c['amp_pi'] * th / math.pi), False)
        else:
            c = F12[q]; fr = fr12[q]; wf = DragGaussianWaveform(c['len'], c['sigma'], 0.0, float(c['amp_pi'] * th / math.pi), False)
        if neg: ps = ps.shift_phase(fr, math.pi)
        ps = ps.play(fr, wf)
        if neg: ps = ps.shift_phase(fr, -math.pi)
        return ps
    def delay(q, ns):
        return PulseSequence().delay([fr01[q], fr12[q]], float(f'{int(round(ns / 4)) * 4}e-9'))
    return dev, Circuit, pulse, delay

def build_main(arms):
    dev, Circuit, pulse, delay = builder(); out = []
    for kind, p in arms:
        c = Circuit()
        for q in QS: c.rz(q, 0.0)
        for q in QS:
            if kind == 'cal':
                if p['prep'] >= 1: c.rx(q, math.pi)
                if p['prep'] == 2: c.pulse_gate([q], pulse(q, 'x12', math.pi))
            else:
                for op in ops_for(p['j']):
                    if abs(op[1]) < 1e-9: continue
                    if op[0] == 'x01':   # 2026-09-26: the chip REJECTS user pulses on the 01 frame (20 tasks failed); build the 01 rotation
                        c.rx(q, math.pi / 2); c.rz(q, op[1]); c.rx(q, -math.pi / 2)   # from natives. Convention-proof: checked in sim, 64 combos.
                    else: c.pulse_gate([q], pulse(q, op[0], op[1]))
                if p['delay_ns']: c.pulse_gate([q], delay(q, p['delay_ns']))
            if p['read'] == 'b': c.rx(q, math.pi)
        out.append(Circuit().add_verbatim_box(c))
    return dev, out

def build_rabi():
    dev, Circuit, pulse, delay = builder()
    from braket.pulse import PulseSequence, DragGaussianWaveform
    out = []
    for a in RABI_AMPS:
        c = Circuit().rz(90, 0.0).rx(90, math.pi)
        if a > 0:
            ps = PulseSequence().play(dev.frames['Transmon_90_charge_tx_f12'], DragGaussianWaveform(40e-9, 8.49321800288e-9, 0.0, a, False))
            c.pulse_gate([90], ps)
        c.rx(90, math.pi)       # step-1 method: |2> survives the last rx(pi) and reads 1; |1> returns to 0
        out.append(Circuit().add_verbatim_box(c))
    return dev, out

def submit(label, arms, circs, shots, tf, order=None, coinrec=None):
    cost = len(circs) * (s3.PER_TASK + shots * s3.PER_SHOT); L = ledger_check(cost, label)
    dev = circs[0] and None
    from braket.aws import AwsDevice
    dev = AwsDevice(DEVICE); tasks = []
    idx = order if order is not None else list(range(len(circs)))
    for i in idx:
        t = dev.run(circs[i], shots=shots, disable_qubit_rewiring=True)
        tasks.append({'i': i, 'arm': arms[i], 'arn': t.id, 'submitted': time.strftime('%Y-%m-%dT%H:%M:%S')}); print('sent', arms[i], flush=True)
    book(L, cost, label, len(tasks))
    json.dump({'device': DEVICE, 'qubits': QS, 'shots': shots, 'coins': coinrec, 'tasks': tasks}, open(tf, 'w'), indent=1)
    print(f'submitted {len(tasks)}; ledger ${L["spent_est"]:.2f}')

def collect(tf, outf):
    from braket.aws import AwsQuantumTask
    T_ = json.load(open(tf)); res = []
    for t in T_['tasks']:
        task = AwsQuantumTask(t['arn']); st = task.state(); r = dict(t); r['state'] = st
        if st == 'COMPLETED':
            rr = task.result(); md = task.metadata()
            r['measured_qubits'] = list(rr.measured_qubits)
            r['shots_bits'] = [''.join(str(int(b)) for b in row) for row in rr.measurements]   # per shot, execution order as returned
            r['created'] = str(md.get('createdAt')); r['ended'] = str(md.get('endedAt'))
        res.append(r)
    json.dump({**{k: v for k, v in T_.items() if k != 'tasks'}, 'results': res}, open(outf, 'w'))
    print(sum(x['state'] == 'COMPLETED' for x in res), '/', len(res), 'complete')

def rabi_fit():
    R = json.load(open(os.path.join(HERE, 'ring_rabi_q90_results.json')))['results']
    pts = []
    for r in R:
        if r['state'] != 'COMPLETED': continue
        col = r['measured_qubits'].index(90); p1 = np.mean([int(s[col]) for s in r['shots_bits']])
        pts.append((r['arm']['amp'], p1))
    pts.sort(); a = np.array([x for x, _ in pts]); y = np.array([v for _, v in pts]); best = None
    for api in np.linspace(0.05, 0.6, 1101):
        X = np.vstack([np.ones_like(a), np.sin(math.pi * a / (2 * api)) ** 2]).T
        cf, *_ = np.linalg.lstsq(X, y, rcond=None); e = ((X @ cf - y) ** 2).sum()
        if best is None or e < best[0]: best = (e, api, cf)
    e, api, cf = best
    fit = {'a_pi_12': round(float(api), 4), 'offset': round(float(cf[0]), 4), 'contrast': round(float(cf[1]), 4), 'rmse': round(math.sqrt(e / len(a)), 4), 'points': pts}
    json.dump(fit, open(os.path.join(HERE, 'ring_rabi_q90_fit.json'), 'w'), indent=1); print(json.dumps(fit))

def analyze():
    D = json.load(open(os.path.join(HERE, 'ring_results.json'))); res = [r for r in D['results'] if r['state'] == 'COMPLETED']
    rr = os.path.join(HERE, 'ring_rerun_results.json')   # 2026-09-26: contexts from the native-01 rerun; cal rows from the first job
    if os.path.exists(rr): res = [r for r in res if r['arm'][0] == 'cal'] + [r for r in json.load(open(rr))['results'] if r['state'] == 'COMPLETED']
    rng = np.random.default_rng(212); SQ5 = math.sqrt(5); PID = math.cos(T) ** 2; Pideal = np.array([PID, PID, 1 - 2 * PID])
    def bits(r, q): col = r['measured_qubits'].index(q); return np.array([int(s[col]) for s in r['shots_bits']])
    def key(r): a = r['arm']; return (a[0],) + tuple(sorted(a[1].items()))
    print('tasks in analysis:', len(res))
    by = {key(r): r for r in res}
    def est(q, draw):   # draw(task_bits) -> resampled bits (identity for point estimate)
        B = {k: draw(bits(r, q)) for k, r in by.items()}
        Ca = [B[('cal', ('prep', k), ('read', 'a'))].mean() for k in range(3)]; Cb = [B[('cal', ('prep', k), ('read', 'b'))].mean() for k in range(3)]
        M = np.array([Ca, Cb, [1, 1, 1]])
        out = {}
        for d in DELAYS_NS:
            P0c, P1c, P0r, P1r = [], [], [], []
            for j in range(5):
                a = B[('ctx', ('delay_ns', d), ('j', j), ('read', 'a'))].mean(); b = B[('ctx', ('delay_ns', d), ('j', j), ('read', 'b'))].mean()
                Pc = np.linalg.solve(M, [a, b, 1.0]); P0c.append(Pc[0]); P1c.append(Pc[1]); P0r.append(1 - a); P1r.append(1 - b)
            Sc = sum(0.5 * (P0c[j] + P1c[(j - 1) % 5]) for j in range(5)); Sr = sum(0.5 * (P0r[j] + P1r[(j - 1) % 5]) for j in range(5))
            Dj = [P0c[j] - P1c[(j - 1) % 5] for j in range(5)]
            out[d] = {'S_corr': Sc, 'S_raw': Sr, 'D': Dj, 'P0c': P0c, 'P1c': P1c}
        apred = Pideal @ np.array(Ca); bpred = Pideal @ np.array(Cb)
        out['S_raw_pred'] = 5 * 0.5 * ((1 - apred) + (1 - bpred)); out['Ca'] = Ca; out['Cb'] = Cb
        return out
    report = {'pre_registered': {}, 'open_eyes': {}}
    for q in QS:
        pt = est(q, lambda x: x); boots = [est(q, lambda x: rng.choice(x, len(x))) for _ in range(2000)]
        W = {'S_raw_pred': pt['S_raw_pred'], 'confusion_a': pt['Ca'], 'confusion_b': pt['Cb']}
        for d in DELAYS_NS:
            sc = np.std([b[d]['S_corr'] for b in boots]); sr = np.std([b[d]['S_raw'] for b in boots])
            dsd = [np.std([b[d]['D'][j] for b in boots]) for j in range(5)]
            W[f'{d}ns'] = {'S_corr': pt[d]['S_corr'], 'S_corr_sd': sc, 'S_raw': pt[d]['S_raw'], 'S_raw_sd': sr,
                           'contextual(>2+3sd)': bool(pt[d]['S_corr'] > 2 + 3 * sc),
                           'beyond_quantum_candidate': bool(pt[d]['S_corr'] > SQ5 + 3 * sc and pt[d]['S_raw'] > pt['S_raw_pred'] + 3 * sr),
                           'consistency_D': [round(x, 4) for x in pt[d]['D']], 'consistency_z': [round(pt[d]['D'][j] / dsd[j], 2) for j in range(5)],
                           'P_v_ctx_outcome0': [round(x, 4) for x in pt[d]['P0c']], 'P_v_ctx_outcome1': [round(x, 4) for x in pt[d]['P1c']]}
        dsdiff = np.std([b[DELAYS_NS[1]]['S_corr'] - b[DELAYS_NS[0]]['S_corr'] for b in boots])
        W['time_ruler_rise_z'] = (pt[DELAYS_NS[1]]['S_corr'] - pt[DELAYS_NS[0]]['S_corr']) / dsdiff
        report['pre_registered'][f'q{q}'] = W
    report['pre_registered']['CLAIM_beyond_quantum'] = all(report['pre_registered'][f'q{q}'][f'{d}ns']['beyond_quantum_candidate'] for q in QS for d in (0,))
    zs = []
    for r in res:
        x, y = bits(r, QS[0]), bits(r, QS[1]); n = len(x)
        phi = 0.0 if x.std() == 0 or y.std() == 0 else float(np.corrcoef(x, y)[0, 1]); zs.append((key(r), round(phi * math.sqrt(n), 2)))
    report['pre_registered']['cross_witness_z'] = zs
    report['pre_registered']['cross_witness_flags'] = [z for z in zs if abs(z[1]) > 3]
    # ---------------- OPEN EYES (exploratory) ----------------
    oe = {'runs_z_flags': [], 'half_drift_flags': [], 'both_one_excess': [], 'notes': []}
    for r in res:
        for q in QS:
            x = bits(r, q); n = len(x); n1 = x.sum(); n0 = n - n1
            if 0 < n1 < n:
                runs = 1 + int((x[1:] != x[:-1]).sum()); mu = 2 * n0 * n1 / n + 1; var = (mu - 1) * (mu - 2) / (n - 1)
                z = (runs - mu) / math.sqrt(var) if var > 0 else 0
                if abs(z) > 3: oe['runs_z_flags'].append((key(r), q, round(z, 2)))
            h = n // 2; p1, p2 = x[:h].mean(), x[h:].mean(); sd = math.sqrt(max(1e-9, x.mean() * (1 - x.mean())) * (1 / h + 1 / (n - h)))
            zd = (p2 - p1) / sd
            if abs(zd) > 3: oe['half_drift_flags'].append((key(r), q, round(zd, 2)))
        x, y = bits(r, QS[0]), bits(r, QS[1]); obs = int((x & y).sum()); exp = len(x) * x.mean() * y.mean()
        oe['both_one_excess'].append((key(r), obs, round(exp, 1)))
    tot_o = sum(o for _, o, _ in oe['both_one_excess']); tot_e = sum(e for _, _, e in oe['both_one_excess'])
    oe['both_one_pooled'] = {'observed': tot_o, 'expected': round(tot_e, 1), 'z': round((tot_o - tot_e) / math.sqrt(max(tot_e, 1)), 2)}
    oe['task_count'] = len(res); oe['runs_tests'] = len(res) * 2
    report['open_eyes'] = oe
    json.dump(report, open(os.path.join(HERE, 'ring_analysis.json'), 'w'), indent=1, default=float)
    print(json.dumps(report, indent=1, default=lambda o: float(o) if isinstance(o, (np.floating,)) else str(o))[:6000])

if __name__ == '__main__':
    m = sys.argv[1] if len(sys.argv) > 1 else '--sim'
    if m == '--sim': sim()
    elif m == '--rabi-submit':
        dev, circs = build_rabi(); arms = [{'amp': a} for a in RABI_AMPS]
        submit('ring: q90 f12 Rabi', arms, circs, SHOTS_RABI, os.path.join(HERE, 'ring_rabi_q90_tasks.json'))
    elif m == '--rabi-collect': collect(os.path.join(HERE, 'ring_rabi_q90_tasks.json'), os.path.join(HERE, 'ring_rabi_q90_results.json')); rabi_fit()
    elif m == '--dry':
        arms = plan(); dev, circs = build_main(arms); print(circs[7]); print(len(circs), 'circuits')
    elif m == '--submit':
        assert 90 in F12, 'q90 f12 not calibrated yet (run --rabi-collect)'
        arms = plan(); dev, circs = build_main(arms); order, rec = coins(len(arms))
        submit('ring: two-witness KCBS main', arms, circs, SHOTS_MAIN, os.path.join(HERE, 'ring_tasks.json'), order, rec)
    elif m == '--collect': collect(os.path.join(HERE, 'ring_tasks.json'), os.path.join(HERE, 'ring_results.json'))
    elif m == '--analyze': analyze()
    elif m == '--rerun':   # the 20 contexts only, native 01 build; next unused quantum-coin bytes (49856-49919, just before the first slice)
        arms = [a for a in plan() if a[0] == 'ctx']; dev, circs = build_main(arms); order, rec = coins(len(arms), back=128)
        assert rec['offset'] == 49856, rec
        submit('ring rerun: 20 contexts, native 01', arms, circs, SHOTS_MAIN, os.path.join(HERE, 'ring_rerun_tasks.json'), order, rec)
    elif m == '--rerun-collect': collect(os.path.join(HERE, 'ring_rerun_tasks.json'), os.path.join(HERE, 'ring_rerun_results.json'))
    elif m == '--diag':   # one cheap acceptance test of the native-01 circuit (context 1, 5 us, scheme b), 100 shots
        arms = [('ctx', {'j': 1, 'read': 'b', 'delay_ns': 5000})]; dev, circs = build_main(arms)
        submit('ring: native-01 acceptance diagnostic', arms, circs, 100, os.path.join(HERE, 'ring_diag_tasks.json'))
