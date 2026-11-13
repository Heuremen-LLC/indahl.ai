"""THE STANDOFF, the fifth door, round 1 step 2 -- read the third state properly, and time Tuco's escape. Rigetti Cepheus q0.

Step 1 found the 1<->2 pi pulse (f12 amp a_pi = 0.494, 94% landed in |2>). Before any three-box, three things:
  A. READOUT: prepare |0>, |1>, |2>; read each two ways -- plain (R_a) and after rx(pi) (R_b, swaps 0<->1, leaves 2).
     If |2> reads as "1" plainly:  P0 = 1 - a,  P1 = 1 - b,  P2 = a + b - 1   (a, b = P(read 1) under R_a, R_b).
  B. TUCO'S NOOSE (Wayfinder: "he probably got out of that noose somehow"): park in |2>, wait t, read both ways.
     Level 2 decays faster than level 1 -- this is his clock (T1 of |2>, and where he lands: |1> then |0>).
  C. RAMSEY ON 1<->2: rx(pi), f12 pi/2, wait t, f12 pi/2 with a phase advanced 2*pi*DET*t, rx(pi), read.
     Fringes give the 1<->2 frequency error and dephasing -- the phase control the native three-box needs.

Same HARD BRAKE as step 1: ledger() refuses anything past CAP. Local model of expected signals: --sim (free).
  qvenv/bin/python braket_round1_step2.py --sim | --dry | --submit | --collect
"""
import json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CAP = 100.00;   # 2026-09-25 Wayfinder: $100 of free credit covers it -- 'let it fucking ride'
PER_TASK = 0.30; PER_SHOT = 0.000425
LEDGER = os.path.join(HERE, 'braket_ledger.json')
DEVICE = "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q"
QUBIT = 0
A_PI12 = json.load(open(os.path.join(HERE, 'round1_fit.json')))['a_pi_12']
WF_LEN, WF_SIGMA = 32e-9, 6.794574402304e-9
SHOTS_A = 1000
SHOTS_B = 300
SHOTS_C = 300
DELAYS_B = [0, 1, 2, 4, 6, 9, 13, 18, 25, 35]            # microseconds
DELAYS_C = [round(x * 0.1, 2) for x in range(0, 16)]      # 0 .. 1.5 us
DET = 4.0e6                                               # 4 MHz virtual detuning -> ~6 fringes over 1.5 us
LABEL = 'round1-step2b ramsey alias breaker q0' if os.environ.get('STEP2B') else 'round1-step2 readout+tuco+ramsey q0'

def plan():
    arms = []
    if os.environ.get('STEP2B'):   # 2b: alias breaker -- Ramsey only, sampled every 0.05 us (Nyquist 10 MHz)
        return [('C', {'delay_us': round(0.05 * k, 2)}, 500) for k in range(0, 21)]
    for s in (0, 1, 2):
        for r in ('a', 'b'): arms.append(('A', {'prep': s, 'read': r}, SHOTS_A))
    for t in DELAYS_B:
        for r in ('a', 'b'): arms.append(('B', {'delay_us': t, 'read': r}, SHOTS_B))
    for t in DELAYS_C: arms.append(('C', {'delay_us': t}, SHOTS_C))
    return arms

def cost(arms):
    return sum(PER_TASK + n * PER_SHOT for _, _, n in arms)

def ledger_check(c):
    L = json.load(open(LEDGER)) if os.path.exists(LEDGER) else {'cap': CAP, 'spent_est': 0.0, 'entries': []}
    if L['spent_est'] + c > CAP:
        raise SystemExit(f'BRAKE: {LABEL} would cost ${c:.2f}; spent ${L["spent_est"]:.2f} of ${CAP:.2f}. Refused.')
    return L

def _ns(us):   # exact 4 ns grid: 0.05*1e-6 is 50.0000000004 ns in floats, which Rigetti rejects
    return float(f'{int(round(us * 1000 / 4)) * 4}e-9')

def build(arms):
    from braket.circuits import Circuit
    from braket.aws import AwsDevice
    from braket.pulse import PulseSequence, DragGaussianWaveform
    dev = AwsDevice(DEVICE)
    f12 = dev.frames[f'Transmon_{QUBIT}_charge_tx_f12']
    wf = lambda a: DragGaussianWaveform(WF_LEN, WF_SIGMA, 0.0, float(a), False)
    pi12 = lambda: PulseSequence().play(f12, wf(A_PI12))
    out = []
    for part, p, n in arms:
        c = Circuit().rz(QUBIT, 0.0)   # a do-nothing native gate: prep |0>/read plain is otherwise an empty circuit, which Braket refuses
        if part == 'A':
            if p['prep'] >= 1: c.rx(QUBIT, math.pi)
            if p['prep'] == 2: c.pulse_gate([QUBIT], pi12())
            if p['read'] == 'b': c.rx(QUBIT, math.pi)
        elif part == 'B':
            ps = PulseSequence().play(f12, wf(A_PI12))
            if p['delay_us'] > 0: ps = ps.delay(f12, _ns(p['delay_us']))
            c.rx(QUBIT, math.pi).pulse_gate([QUBIT], ps)
            if p['read'] == 'b': c.rx(QUBIT, math.pi)
        else:
            t = p['delay_us'] * 1e-6
            ps = PulseSequence().play(f12, wf(A_PI12 / 2))
            if t > 0: ps = ps.delay(f12, _ns(p['delay_us']))
            ps = ps.shift_phase(f12, (2 * math.pi * DET * t) % (2 * math.pi)).play(f12, wf(A_PI12 / 2))
            c.rx(QUBIT, math.pi).pulse_gate([QUBIT], ps).rx(QUBIT, math.pi)
        out.append(Circuit().add_verbatim_box(c))
    return dev, out

def sim():
    """Expected signals with step 1's losses: 94% transfer into |2>, 7% readout floor; T1(2->1) guessed 10 us, T2* 1 us."""
    land, floor, T1, T2 = 0.94, 0.07, 10.0, 1.0
    rng = np.random.default_rng(212)
    print('A. readout (P read 1), expected:')
    P = {0: (1, 0, 0), 1: (0, 1, 0), 2: (0, 1 - land, land)}
    for s, (p0, p1, p2) in P.items():
        a = floor + (1 - 2 * floor) * (p1 + p2); b = floor + (1 - 2 * floor) * (p0 + p2)
        print(f'   prep {s}: R_a {a:.3f}  R_b {b:.3f}  ->  P2 = a+b-1 = {a + b - 1:+.3f}')
    print(f'B. Tuco: P2(t) = {land:.2f}*exp(-t/T1); binomial noise at {SHOTS_B} shots ~ +/-{math.sqrt(0.25 / SHOTS_B) * 1.41:.3f} on P2')
    for t in DELAYS_B:
        p2 = land * math.exp(-t / T1); noisy = p2 + rng.normal(0, math.sqrt(0.25 / SHOTS_B) * 1.41)
        print(f'   t {t:>4} us  P2 {p2:.3f}  (one draw {noisy:.3f})')
    print('C. Ramsey on 1<->2: fringe contrast vs noise')
    for t in DELAYS_C[::3]:
        c = math.exp(-t / T2) * land * (1 - 2 * floor)
        print(f'   t {t:.1f} us  contrast {c:.3f}  vs noise {math.sqrt(0.25 / SHOTS_C):.3f}')

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else '--dry'
    arms = plan(); c = cost(arms)
    if mode == '--sim': sim(); print(f'\n{len(arms)} tasks, ${c:.2f}'); return
    L = ledger_check(c)
    print(f'{LABEL}: {len(arms)} tasks = ${c:.2f}  (spent so far ${L["spent_est"]:.2f} / cap ${CAP:.2f})')
    if mode == '--dry':
        dev, circs = build(arms); print('built', len(circs), 'circuits; a Ramsey one:\n', circs[-5]); return
    if mode == '--submit':
        dev, circs = build(arms); tasks = []
        for (part, p, n), circ in zip(arms, circs):
            t = dev.run(circ, shots=n, disable_qubit_rewiring=True)
            tasks.append({'part': part, **p, 'shots': n, 'arn': t.id}); print('sent', part, p, t.id[-12:], flush=True)
        L['spent_est'] = round(L['spent_est'] + c, 4)
        L['entries'].append({'at': time.strftime('%Y-%m-%dT%H:%M:%S'), 'label': LABEL, 'tasks': len(tasks), 'cost_est': round(c, 4)})
        json.dump(L, open(LEDGER, 'w'), indent=1)
        json.dump({'device': DEVICE, 'qubit': QUBIT, 'a_pi12': A_PI12, 'det_hz': DET, 'tasks': tasks}, open(os.path.join(HERE, 'step2b_tasks.json' if os.environ.get('STEP2B') else 'step2_tasks.json'), 'w'), indent=1)
        print(f'submitted {len(tasks)}; ledger now ${L["spent_est"]:.2f} / ${CAP:.2f}')
    if mode == '--collect':
        from braket.aws import AwsQuantumTask
        T = json.load(open(os.path.join(HERE, 'step2b_tasks.json' if os.environ.get('STEP2B') else 'step2_tasks.json'))); out = []
        for t in T['tasks']:
            task = AwsQuantumTask(t['arn']); st = task.state(); r = {k: v for k, v in t.items() if k != 'arn'}; r['state'] = st
            if st == 'COMPLETED':
                m = task.result().measurement_counts; tot = sum(m.values())
                r['p_read1'] = sum(v for k, v in m.items() if '1' in k) / tot; r['counts'] = dict(m)
            out.append(r)
        json.dump({**{k: v for k, v in T.items() if k != 'tasks'}, 'results': out}, open(os.path.join(HERE, 'step2b_results.json' if os.environ.get('STEP2B') else 'step2_results.json'), 'w'), indent=1)
        print(sum(o['state'] == 'COMPLETED' for o in out), '/', len(out), 'complete')

if __name__ == '__main__':
    main()
