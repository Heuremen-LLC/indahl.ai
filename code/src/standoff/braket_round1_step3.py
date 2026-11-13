"""THE STANDOFF, the fifth door, round 1 step 3 -- BLONDIE'S THREE-BOX, native, on one qutrit (Rigetti Cepheus q0).

Aharonov-Vaidman: boxes A, B, C = levels |0>, |1>, |2>. Pre-select psi = (|0> + i|1> + |2>)/sqrt3 (the phases our native gates
make); post-select phi = same with |2> sign-flipped. Opening ONE box is a strong (von Neumann) measurement: two incoherent
branches, "found" (the basis state |k>) and "not found" ((1-P_k)psi). ABL rule, from post-selection probabilities p of each
branch:  P(found in k | psi, phi) = w_y*p_y / (w_y*p_y + w_n*p_n),   w_y = 1/3, w_n = 2/3.
Ideal: A = 1, B = 1, C = 0.2. The magic sits in the "not found" branches of A and B going DARK (p_n = 0).

Native gates only (rx +-pi/2, rx pi) plus f12 pulses (angle = pi * amp / a_pi12, phase = f12 frame shift_phase):
  prep psi      rx(pi), f12(theta2, 0), rx(pi/2)           theta2 = 2 acos(sqrt(2/3))
  A-not-found   rx(pi), f12(pi/2, 0)                        ~ i|1> + |2>
  B-not-found   rx(pi/2), f12(pi, pi)                       ~ |0> + |2>
  C-not-found   rx(-pi/2)                                   ~ |0> + i|1>
  found A/B/C   (nothing) / rx(pi) / rx(pi), f12(pi, 0)
  post-select   V(x) = rx(-pi/2), f12(theta2, x), rx(pi), then read: P0 = 1 - P(read 1)
                x = pi undoes psi exactly (psi -> |0>); x = 0 is the phi test (psi -> 1/9).
PRE-REGISTERED (before any data): (1) x0 = where psi's fringe peaks, fit from psi's 8-point scan alone; the ABL numbers use each
branch's fringe fitted and read at x0 - pi (the phi setting). (2) P0 is corrected with step 2's measured confusion (prep 0/1/2
under plain read). (3) Branch sign conventions are checked by the sim; if the hardware fringe of a branch is mirrored, say so.
  qvenv/bin/python braket_round1_step3.py --sim | --dry | --submit | --collect | --analyze
"""
import json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CAP = 195.00   # 2026-09-26 Wayfinder: "just fucking hit it" -- ring rerun (~$22)
PER_TASK = 0.30; PER_SHOT = 0.000425
LEDGER = os.path.join(HERE, 'braket_ledger.json')
DEVICE = "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q"
QUBIT = 0
A_PI12 = json.load(open(os.path.join(HERE, 'round1_fit.json')))['a_pi_12']
WF_LEN, WF_SIGMA = 32e-9, 6.794574402304e-9
TH2 = 2 * math.acos(math.sqrt(2 / 3))
XS = [round(2 * math.pi * k / 8, 4) for k in range(8)]
SHOTS = 1000
LABEL = 'round1-step3 native three-box q0'
PREPS = {   # name: list of ops; ('rx', angle) or ('f12', angle, phase)
    'psi':   [('rx', math.pi), ('f12', TH2, 0.0), ('rx', math.pi / 2)],
    'A_not': [('rx', math.pi), ('f12', math.pi / 2, 0.0)],
    'B_not': [('rx', math.pi / 2), ('f12', math.pi, math.pi)],
    'C_not': [('rx', -math.pi / 2)],
    'A_yes': [],
    'B_yes': [('rx', math.pi)],
    'C_yes': [('rx', math.pi), ('f12', math.pi, 0.0)],
}
SCANNED = ['psi', 'A_not', 'B_not', 'C_not']

def V(x): return [('rx', -math.pi / 2), ('f12', TH2, x), ('rx', math.pi)]

def plan():
    arms = [(n, x) for n in SCANNED for x in XS]
    arms += [(n, math.pi) for n in ('A_yes', 'B_yes', 'C_yes')]   # basis states: their post-select p does not depend on x
    return arms

# ---------------- ideal qutrit model (same conventions as the circuits) ----------------
def U(op):
    M = np.eye(3, dtype=complex)
    if op[0] == 'rx':
        t = op[1]; M[0, 0] = M[1, 1] = math.cos(t / 2); M[0, 1] = M[1, 0] = -1j * math.sin(t / 2)
    else:
        t, p = op[1], op[2]; M[1, 1] = M[2, 2] = math.cos(t / 2)
        M[1, 2] = -1j * math.sin(t / 2) * np.exp(-1j * p); M[2, 1] = -1j * math.sin(t / 2) * np.exp(1j * p)
    return M

def run_ideal(ops):
    s = np.array([1, 0, 0], dtype=complex)
    for op in ops: s = U(op) @ s
    return s

def p0(name, x): return abs(run_ideal(PREPS[name] + V(x))[0]) ** 2

def abl(p):
    out = {}
    for k in 'ABC':
        py, pn = p[k + '_yes'], p[k + '_not']
        out[k] = (py / 3) / (py / 3 + 2 * pn / 3) if (py + pn) > 0 else float('nan')
    return out

def sim():
    s = run_ideal(PREPS['psi']); print('psi amplitudes', np.round(s, 3))
    for n in ('A_not', 'B_not', 'C_not'): print(n, 'amplitudes', np.round(run_ideal(PREPS[n]), 3))
    print('\npost-select P0 vs x (x = pi undoes psi; x = 0 is phi):')
    for n in SCANNED: print(f'  {n:6}', '  '.join(f'{p0(n, x):.3f}' for x in XS))
    for n in ('A_yes', 'B_yes', 'C_yes'): print(f'  {n:6} {p0(n, 0.0):.3f}')
    p = {n: p0(n, 0.0) for n in PREPS}
    print('\nIDEAL ABL at x = 0 (phi):', {k: round(v, 3) for k, v in abl(p).items()}, ' target A 1, B 1, C 0.2')
    # the same numbers after step 2's REAL readout confusion (prep k -> P(read 1)) and 6% f12 inefficiency, uncorrected
    R = json.load(open(os.path.join(HERE, 'step2_results.json')))['results']
    rd = {r['prep']: r['p_read1'] for r in R if r['part'] == 'A' and r['read'] == 'a'}
    def noisy(n):
        ops = [(o[0], o[1] * (0.97 if o[0] == 'f12' else 1), *o[2:]) for o in PREPS[n] + V(0.0)]
        s = run_ideal(ops); pr = np.abs(s) ** 2
        return sum(pr[k] * (1 - rd[k]) for k in range(3))
    pn = {n: noisy(n) for n in PREPS}
    print('NOISY (uncorrected) ABL  :', {k: round(v, 3) for k, v in abl(pn).items()})
    print(f'\n{len(plan())} tasks x {SHOTS} shots = ${len(plan()) * (PER_TASK + SHOTS * PER_SHOT):.2f}')

# ---------------- hardware ----------------
def build(arms):
    from braket.circuits import Circuit
    from braket.aws import AwsDevice
    from braket.pulse import PulseSequence, DragGaussianWaveform
    dev = AwsDevice(DEVICE); f12 = dev.frames[f'Transmon_{QUBIT}_charge_tx_f12']
    out = []
    for name, x in arms:
        c = Circuit().rz(QUBIT, 0.0)
        for op in PREPS[name] + V(x):
            if op[0] == 'rx': c.rx(QUBIT, op[1])
            else:   # phase set, pulse, phase restored -- the frame is left where it started
                ps = PulseSequence()
                if op[2]: ps = ps.shift_phase(f12, op[2])
                ps = ps.play(f12, DragGaussianWaveform(WF_LEN, WF_SIGMA, 0.0, float(A_PI12 * op[1] / math.pi), False))
                if op[2]: ps = ps.shift_phase(f12, -op[2])
                c.pulse_gate([QUBIT], ps)
        out.append(Circuit().add_verbatim_box(c))
    return dev, out

def analyze():
    R = json.load(open(os.path.join(HERE, 'step3_results.json')))['results']
    S2 = json.load(open(os.path.join(HERE, 'step2_results.json')))['results']
    rd = {r['prep']: r['p_read1'] for r in S2 if r['part'] == 'A' and r['read'] == 'a'}
    # P(read 0) = P0*(1-r0) + P1*(1-r1) + P2*(1-r2); the P1/P2 mix is unknown per arm, so correct with the two-outcome
    # approximation using r_not0 = mean(r1, r2):  P0 = (read0 - (1 - r_not0)) / ((1 - r0) - (1 - r_not0))
    r0, rn = rd[0], (rd[1] + rd[2]) / 2
    corr = lambda read0: (read0 - (1 - rn)) / ((1 - r0) - (1 - rn))
    d = {}
    for r in R:
        if r.get('state') != 'COMPLETED': continue
        d.setdefault(r['name'], {})[r['x']] = corr(1 - r['p_read1'])
    fit = {}
    for n in SCANNED:
        xs = np.array(sorted(d[n])); ys = np.array([d[n][x] for x in xs])
        X = np.vstack([np.ones_like(xs), np.cos(xs), np.sin(xs)]).T; c, *_ = np.linalg.lstsq(X, ys, rcond=None); fit[n] = c
        print(f'  {n:6}', '  '.join(f'{v:.3f}' for v in ys), f'   ideal', '  '.join(f'{p0(n, x):.3f}' for x in xs))
    c = fit['psi']; x0 = math.atan2(c[2], c[1]); print(f'psi fringe peaks at x0 = {x0:.3f} rad (ideal pi = 3.142)')
    xphi = x0 - math.pi
    at = lambda n: float(np.dot(fit[n], [1, math.cos(xphi), math.sin(xphi)]))
    p = {n: at(n) for n in SCANNED}
    for n in ('A_yes', 'B_yes', 'C_yes'): p[n] = float(np.mean(list(d[n].values())))
    print('post-select p at phi:', {k: round(v, 3) for k, v in p.items()})
    res = abl(p); print('\nABL, MEASURED:', {k: round(v, 3) for k, v in res.items()}, '   ideal A 1, B 1, C 0.2')
    json.dump({'x0': x0, 'p_at_phi': p, 'abl': res}, open(os.path.join(HERE, 'step3_abl.json'), 'w'), indent=1)

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else '--sim'
    if mode == '--sim': sim(); return
    if mode == '--analyze': analyze(); return
    arms = plan(); cost = len(arms) * (PER_TASK + SHOTS * PER_SHOT)
    L = json.load(open(LEDGER))
    if L['spent_est'] + cost > CAP: raise SystemExit(f'BRAKE: ${cost:.2f} would pass ${CAP:.2f} (spent ${L["spent_est"]:.2f})')
    print(f'{LABEL}: {len(arms)} tasks = ${cost:.2f}  (spent ${L["spent_est"]:.2f} / ${CAP:.2f})')
    if mode == '--dry': dev, circs = build(arms); print(circs[0]); return
    if mode == '--submit':
        dev, circs = build(arms); tasks = []
        for (name, x), circ in zip(arms, circs):
            t = dev.run(circ, shots=SHOTS, disable_qubit_rewiring=True); tasks.append({'name': name, 'x': x, 'arn': t.id})
            print('sent', name, x, flush=True)
        L['spent_est'] = round(L['spent_est'] + cost, 4)
        L['entries'].append({'at': time.strftime('%Y-%m-%dT%H:%M:%S'), 'label': LABEL, 'tasks': len(tasks), 'cost_est': round(cost, 4)})
        json.dump(L, open(LEDGER, 'w'), indent=1)
        json.dump({'device': DEVICE, 'tasks': tasks}, open(os.path.join(HERE, 'step3_tasks.json'), 'w'), indent=1)
        print(f'submitted {len(tasks)}; ledger ${L["spent_est"]:.2f} / ${CAP:.2f}')
    if mode == '--collect':
        from braket.aws import AwsQuantumTask
        T = json.load(open(os.path.join(HERE, 'step3_tasks.json'))); out = []
        for t in T['tasks']:
            task = AwsQuantumTask(t['arn']); st = task.state(); r = {'name': t['name'], 'x': t['x'], 'state': st}
            if st == 'COMPLETED':
                m = task.result().measurement_counts; tot = sum(m.values()); r['p_read1'] = sum(v for k, v in m.items() if '1' in k) / tot
            out.append(r)
        json.dump({'results': out}, open(os.path.join(HERE, 'step3_results.json'), 'w'), indent=1)
        print(sum(o['state'] == 'COMPLETED' for o in out), '/', len(out), 'complete')

if __name__ == '__main__':
    main()
