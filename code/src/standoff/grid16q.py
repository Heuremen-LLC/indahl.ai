"""ALL FOUR AT THE GATE, on the qutrit (Rigetti Cepheus q0) -- 2026-09-25, the redesign.

grid16.py (qubit version) was a dud: recruit and Blondie both just removed a body, so the four-way term was body-counting.
Here every switch is a DIFFERENT physical operation on one three-level standoff (psi, from step 3), all built from the two
things we calibrated and trust tonight -- 01 rotations and f12 pulses -- then the same post-selection read V(x):
  B  BLONDIE  the rig: post-select phi (x = x0 - pi) instead of undoing psi (x = x0). x0 measured in step 3.
  R  RECRUIT  between prep and read, rx(pi) on 0<->1: body A and body B trade places (one pulls another off with it).
  P  PINATA   between prep and read, TWO f12 pi pulses = a full 2-pi swing on 1<->2: populations come back unchanged, but the
              swung bodies come back with a MINUS sign. Only interference can see it (the 4-pi thing).
  S  SIX      the standoff is run twice: psi's prep applied again -> every path splits into three again (3 -> 9 histories).
Observable per arm: P0 after V (readout-corrected like step 3). Factorial: main effects, 2/3-way, and the FOUR-WAY term.
PRE-REGISTERED: the ideal model below predicts every arm and every interaction; the hardware test is whether the measured
four-way term matches the ideal one within its bootstrap error. A match = the chip's three-level interference obeys QM across
all 16 combinations. A miss = structure the ideal model doesn't have (drift, leakage, Stark shifts) -- a finding, not a failure.
  qvenv/bin/python grid16q.py --sim | --dry | --submit | --collect | --analyze
"""
import itertools, json, math, os, sys, time
import numpy as np
import braket_round1_step3 as s3

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = 3000
LABEL = 'grid16q all four at the gate (qutrit q0)'
X0 = json.load(open(os.path.join(HERE, 'step3_abl.json')))['x0']
ARMS = list(itertools.product((0, 1), repeat=4))   # (S, R, B, P)

def ops(S, R, B, P):
    o = list(s3.PREPS['psi']) * (2 if S else 1)
    if R: o.append(('rx', math.pi))
    if P: o += [('f12', math.pi, 0.0), ('f12', math.pi, 0.0)]
    return o + s3.V(X0 - math.pi if B else X0)

def ideal(arm):
    return abs(s3.run_ideal(ops(*arm))[0]) ** 2

def factorial(y):
    """y: dict arm -> value. Effects in +-1 coding: term(subset) = mean(y * prod(sign)) over arms."""
    out = {}
    for r in range(1, 5):
        for sub in itertools.combinations(range(4), r):
            out[''.join('SRBP'[i] for i in sub)] = float(np.mean([y[a] * np.prod([(1 if a[i] else -1) for i in sub]) for a in ARMS]))
    return out

def sim():
    x_ideal = math.pi   # in the ideal model psi's fringe peaks at pi
    global X0; keep = X0; X0 = x_ideal
    y = {a: ideal(a) for a in ARMS}
    for a in ARMS: print(' S R B P =', a, f'P0 {y[a]:.3f}')
    f = factorial(y); print('\nIDEAL effects:', {k: round(v, 3) for k, v in f.items()})
    # noisy: step-2 readout confusion + 3% short f12 angles, then the same correction step 3 uses; bootstrap at SHOTS
    R2 = json.load(open(os.path.join(HERE, 'step2_results.json')))['results']
    rd = {r['prep']: r['p_read1'] for r in R2 if r['part'] == 'A' and r['read'] == 'a'}
    r0, rn = rd[0], (rd[1] + rd[2]) / 2
    def noisy(a):
        o = [(op[0], op[1] * (0.97 if op[0] == 'f12' else 1), *op[2:]) for op in ops(*a)]
        pr = np.abs(s3.run_ideal(o)) ** 2; return sum(pr[k] * (1 - rd[k]) for k in range(3))
    rng = np.random.default_rng(212); fours = []
    for _ in range(400):
        yb = {a: ((rng.binomial(SHOTS, noisy(a)) / SHOTS) - (1 - rn)) / ((1 - r0) - (1 - rn)) for a in ARMS}
        fours.append(factorial(yb)['SRBP'])
    print(f"NOISY four-way: {np.mean(fours):+.4f} +/- {np.std(fours):.4f}   (ideal {f['SRBP']:+.4f})  at {SHOTS} shots/arm")
    X0 = keep
    print(f'{len(ARMS)} tasks x {SHOTS} = ${len(ARMS) * (s3.PER_TASK + SHOTS * s3.PER_SHOT):.2f}')

def build():
    from braket.circuits import Circuit
    from braket.aws import AwsDevice
    from braket.pulse import PulseSequence, DragGaussianWaveform
    dev = AwsDevice(s3.DEVICE); f12 = dev.frames[f'Transmon_{s3.QUBIT}_charge_tx_f12']; out = []
    for a in ARMS:
        c = Circuit().rz(s3.QUBIT, 0.0)
        for op in ops(*a):
            if op[0] == 'rx': c.rx(s3.QUBIT, op[1]); continue
            ps = PulseSequence()
            if op[2]: ps = ps.shift_phase(f12, op[2])
            ps = ps.play(f12, DragGaussianWaveform(s3.WF_LEN, s3.WF_SIGMA, 0.0, float(s3.A_PI12 * op[1] / math.pi), False))
            if op[2]: ps = ps.shift_phase(f12, -op[2])
            c.pulse_gate([s3.QUBIT], ps)
        out.append(Circuit().add_verbatim_box(c))
    return dev, out

def analyze():
    R = json.load(open(os.path.join(HERE, 'grid16q_results.json')))['results']
    R2 = json.load(open(os.path.join(HERE, 'step2_results.json')))['results']
    rd = {r['prep']: r['p_read1'] for r in R2 if r['part'] == 'A' and r['read'] == 'a'}
    r0, rn = rd[0], (rd[1] + rd[2]) / 2
    corr = lambda p: (p - (1 - rn)) / ((1 - r0) - (1 - rn))
    y = {tuple(r['arm']): corr(1 - r['p_read1']) for r in R}
    global X0; keep = X0; X0 = math.pi; yi = {a: ideal(a) for a in ARMS}; X0 = keep
    for a in ARMS: print(' S R B P =', a, f'measured {y[a]:.3f}   ideal {yi[a]:.3f}')
    fm, fi = factorial(y), factorial(yi)
    rng = np.random.default_rng(212); boots = []
    for _ in range(2000):
        yb = {a: corr(rng.binomial(SHOTS, 1 - next(r['p_read1'] for r in R if tuple(r['arm']) == a)) / SHOTS) for a in ARMS}
        boots.append(factorial(yb))
    print('\n effect   measured        ideal')
    for k in fm:
        e = np.std([b[k] for b in boots]); print(f'  {k:5} {fm[k]:+.4f} +/- {e:.4f}   {fi[k]:+.4f}   ({(fm[k] - fi[k]) / e:+.1f} sigma off)')
    json.dump({'measured': fm, 'ideal': fi, 'arms': {str(a): y[a] for a in ARMS}}, open(os.path.join(HERE, 'grid16q_analysis.json'), 'w'), indent=1)

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else '--sim'
    if mode == '--sim': sim(); return
    if mode == '--analyze': analyze(); return
    cost = len(ARMS) * (s3.PER_TASK + SHOTS * s3.PER_SHOT); L = json.load(open(s3.LEDGER))
    if mode in ('--dry', '--submit') and L['spent_est'] + cost > s3.CAP: raise SystemExit(f'BRAKE: ${cost:.2f} would pass ${s3.CAP:.2f} (spent ${L["spent_est"]:.2f})')
    print(f'{LABEL}: {len(ARMS)} tasks = ${cost:.2f}  (spent ${L["spent_est"]:.2f} / ${s3.CAP:.2f})')
    if mode == '--dry': dev, c = build(); print(c[-1]); return
    if mode == '--submit':
        dev, circs = build(); tasks = []
        for a, c in zip(ARMS, circs):
            t = dev.run(c, shots=SHOTS, disable_qubit_rewiring=True); tasks.append({'arm': a, 'arn': t.id}); print('sent', a, flush=True)
        L['spent_est'] = round(L['spent_est'] + cost, 4)
        L['entries'].append({'at': time.strftime('%Y-%m-%dT%H:%M:%S'), 'label': LABEL, 'tasks': len(tasks), 'cost_est': round(cost, 4)})
        json.dump(L, open(s3.LEDGER, 'w'), indent=1); json.dump({'tasks': tasks}, open(os.path.join(HERE, 'grid16q_tasks.json'), 'w'), indent=1)
        print(f'submitted {len(tasks)}; ledger ${L["spent_est"]:.2f} / ${s3.CAP:.2f}')
    if mode == '--collect':
        from braket.aws import AwsQuantumTask
        T = json.load(open(os.path.join(HERE, 'grid16q_tasks.json'))); out = []
        for t in T['tasks']:
            task = AwsQuantumTask(t['arn']); st = task.state(); r = {'arm': t['arm'], 'state': st}
            if st == 'COMPLETED':
                m = task.result().measurement_counts; tot = sum(m.values()); r['p_read1'] = sum(v for k, v in m.items() if '1' in k) / tot
            out.append(r)
        json.dump({'results': out}, open(os.path.join(HERE, 'grid16q_results.json'), 'w'), indent=1)
        print(sum(o['state'] == 'COMPLETED' for o in out), '/', len(out), 'complete')

if __name__ == '__main__':
    main()
