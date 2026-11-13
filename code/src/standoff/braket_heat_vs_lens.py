"""HEAT vs LENS through the third level (Rabi population measurement) -- Rigetti Cepheus q0, 2026-09-28 (Bones; Wayfinder: "do it").
PRE-REGISTERED (written before any shot):
  A (heat):  f12 pulse amp a (0 .. 2*pi of the 1<->2 swing) -> rx(pi) -> read.   P(read 0) = Pe * cos^2(theta/2) * contrast + offset
  B (ref):   rx(pi) -> f12 pulse amp a -> rx(pi) -> read.                         P(read 0) = Pg * cos^2(theta/2) * contrast + offset
  amplitude(A) / amplitude(B) = Pe / Pg  -- the readout contrast (the lens) CANCELS. Heat Pe = r/(1+r).
  D (one look): prep 0 read; prep 1 read.  P(read 1 | prep 0) = heat + lens misread. Lens share = P(read1|prep0) - Pe.
  Fit: least squares of y = A0 + A1*cos(pi*a/a_pi) per arm (cos^2(theta/2) = (1+cos theta)/2); amplitude = |A1|.
  Report whatever comes out; 1-sigma from the fit residuals.
Cost gate: the ledger's own cap (braket_ledger.json). qvenv/bin/python braket_heat_vs_lens.py --sim | --dry | --submit | --collect | --analyze"""
import json, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); LEDGER = os.path.join(HERE, 'braket_ledger.json')
DEVICE = "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q"; QUBIT = 0
PER_TASK, PER_SHOT = 0.30, 0.000425
A_PI12 = json.load(open(os.path.join(HERE, 'round1_fit.json')))['a_pi_12']
WF_LEN, WF_SIGMA = 32e-9, 6.794574402304e-9
AMPS = [0.0, A_PI12]      # 2026-09-28 redesign after --sim: 7 points x 1500 gave heat 3% +/- 2.5% (useless). Two points (theta 0 and pi) carry all the
                          # swing: amplitude = (y(0) - y(pi))/2. 10,000 shots each on arm A -> +/- ~0.8% on the heat. Pulse miscalibration cancels in A/B.
SHOTS_A, SHOTS_B, SHOTS_D = 10000, 500, 1000   # D doubles as the third-state-at-rest probe (a + b - 1)
LABEL = 'heat-vs-lens RPM q0 (parallax, third level)'; TASKS = os.path.join(HERE, 'heatlens_tasks.json'); RES = os.path.join(HERE, 'heatlens_results.json')
def plan():
    return [('A', {'amp': a}, SHOTS_A) for a in AMPS] + [('B', {'amp': a}, SHOTS_B) for a in AMPS] + [('D', {'prep': s}, SHOTS_D) for s in (0, 1)]
def cost(arms): return sum(PER_TASK + n * PER_SHOT for _, _, n in arms)
def ledger(c):
    L = json.load(open(LEDGER))
    if L['spent_est'] + c > L['cap']: raise SystemExit(f"BRAKE: ${c:.2f} would pass the cap: spent ${L['spent_est']:.2f} of ${L['cap']:.2f}. Refused.")
    return L
def build(arms):
    from braket.circuits import Circuit; from braket.aws import AwsDevice; from braket.pulse import PulseSequence, DragGaussianWaveform
    dev = AwsDevice(DEVICE); f12 = dev.frames[f'Transmon_{QUBIT}_charge_tx_f12']
    wf = lambda a: DragGaussianWaveform(WF_LEN, WF_SIGMA, 0.0, float(a), False); out = []
    for part, p, n in arms:
        c = Circuit().rz(QUBIT, 0.0)
        if part == 'A':
            if p['amp'] > 0: c.pulse_gate([QUBIT], PulseSequence().play(f12, wf(p['amp'])))
            c.rx(QUBIT, math.pi)
        elif part == 'B':
            c.rx(QUBIT, math.pi)
            if p['amp'] > 0: c.pulse_gate([QUBIT], PulseSequence().play(f12, wf(p['amp'])))
            c.rx(QUBIT, math.pi)
        elif p['prep'] == 1: c.rx(QUBIT, math.pi)
        out.append(Circuit().add_verbatim_box(c))
    return dev, out
def fit(amps, y, n=None):
    # two points at theta 0 and pi: offset = mean, swing amplitude = (y0 - ypi)/2, binomial error from the shot counts
    y0, yp = y[0], y[-1]; n = n or [1, 1]
    e = 0.5 * math.sqrt(y0 * (1 - y0) / n[0] + yp * (1 - yp) / n[-1])
    return (0.5 * (y0 + yp), 0.5 * (y0 - yp)), (0.0, e)
def sim():
    pe, contrast, off = 0.03, 0.86, 0.07; rng = np.random.default_rng(212)
    ya = [off + contrast * pe * math.cos(math.pi * a / A_PI12 / 2) ** 2 + rng.normal(0, math.sqrt(.25 / SHOTS_A)) for a in AMPS]
    yb = [off + contrast * (1 - pe) * math.cos(math.pi * a / A_PI12 / 2) ** 2 + rng.normal(0, math.sqrt(.25 / SHOTS_B)) for a in AMPS]
    (a0, a1), (_, ea) = fit(AMPS, ya, [SHOTS_A] * 2); (b0, b1), (_, eb) = fit(AMPS, yb, [SHOTS_B] * 2); r = abs(a1) / abs(b1)
    print(f'SIM with true heat 3.0%: fitted heat {r/(1+r)*100:.2f}% (amp A {abs(a1):.4f}+/-{ea:.4f}, amp B {abs(b1):.4f}+/-{eb:.4f})')
def analyze():
    R = json.load(open(RES))['results']; g = lambda part: sorted([x for x in R if x['part'] == part and x['state'] == 'COMPLETED'], key=lambda x: x.get('amp', x.get('prep', 0)))
    A, B, D = g('A'), g('B'), g('D')
    ya = [1 - x['p_read1'] for x in A]; yb = [1 - x['p_read1'] for x in B]
    (a0, a1), (_, ea) = fit([x['amp'] for x in A], ya, [x['shots'] for x in A]); (b0, b1), (_, eb) = fit([x['amp'] for x in B], yb, [x['shots'] for x in B])
    r = abs(a1) / abs(b1); pe = r / (1 + r); epe = pe * math.hypot(ea / abs(a1) if a1 else 0, eb / abs(b1))
    d0 = next(x['p_read1'] for x in D if x['prep'] == 0); d1 = 1 - next(x['p_read1'] for x in D if x['prep'] == 1)
    out = {'heat_Pe': pe, 'heat_err': epe, 'amp_A': abs(a1), 'amp_A_err': ea, 'amp_B': abs(b1), 'amp_B_err': eb, 'one_look_read1_prep0': d0,
           'lens_share_prep0': d0 - pe, 'one_look_read0_prep1': d1, 'A_points': ya, 'B_points': yb}
    json.dump(out, open(os.path.join(HERE, 'heatlens_analysis.json'), 'w'), indent=1)
    print(f"HEAT (in the tank), readout-proof: Pe = {pe*100:.2f}% +/- {epe*100:.2f}%")
    print(f"ONE LOOK says 'prepared 0, read 1' = {d0*100:.2f}%  ->  lens share = {(d0-pe)*100:+.2f}%   (prepared 1, read 0 = {d1*100:.2f}%)")
    # THE THIRD STATE AT REST (step-2 identity; readout lumps 2 with 1): a = P(read1 | rest), b = P(read1 | rx(pi) from rest)
    # a + b - 1 = (1 - 2f) * P2  for a symmetric misread f  ->  population in |2> that nobody put there.
    a_, b_ = d0, 1 - d1; nA = next(x['shots'] for x in D if x['prep'] == 0); nB = next(x['shots'] for x in D if x['prep'] == 1)
    p2 = a_ + b_ - 1; ep2 = math.sqrt(a_ * (1 - a_) / nA + b_ * (1 - b_) / nB)
    out['third_state_at_rest_raw'] = p2; out['third_state_err'] = ep2; json.dump(out, open(os.path.join(HERE, 'heatlens_analysis.json'), 'w'), indent=1)
    print(f"THIRD STATE AT REST (a+b-1, before dividing by 1-2f): {p2*100:+.2f}% +/- {ep2*100:.2f}%  -> {'OCCUPIED beyond noise' if p2 > 3*ep2 else 'not resolved from zero'}")
def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else '--dry'; arms = plan(); c = cost(arms)
    if mode == '--sim': sim(); print(f'{len(arms)} tasks, {sum(n for *_, n in arms)} shots, ${c:.2f}'); return
    if mode == '--analyze': analyze(); return
    if mode == '--collect':
        from braket.aws import AwsQuantumTask
        T = json.load(open(TASKS)); out = []
        for t in T['tasks']:
            task = AwsQuantumTask(t['arn']); st = task.state(); r = {k: v for k, v in t.items() if k != 'arn'}; r['state'] = st
            if st == 'COMPLETED':
                m = task.result().measurement_counts; tot = sum(m.values()); r['p_read1'] = sum(v for k, v in m.items() if k[-1] == '1') / tot; r['counts'] = dict(m)
            out.append(r)
        json.dump({'device': DEVICE, 'qubit': QUBIT, 'a_pi12': A_PI12, 'results': out}, open(RES, 'w'), indent=1)
        print(sum(o['state'] == 'COMPLETED' for o in out), '/', len(out), 'complete'); return
    L = ledger(c); print(f'{LABEL}: {len(arms)} tasks, ${c:.2f}  (spent ${L["spent_est"]:.2f} of cap ${L["cap"]:.2f})')
    dev, circs = build(arms)
    if mode == '--dry': print('device', dev.status, '| built', len(circs), 'circuits. e.g. A @ pi:\n', circs[3]); return
    if mode == '--submit':
        tasks = []
        for (part, p, n), circ in zip(arms, circs):
            t = dev.run(circ, shots=n, disable_qubit_rewiring=True); tasks.append({'part': part, **p, 'shots': n, 'arn': t.id}); print('sent', part, p, flush=True)
        L['spent_est'] = round(L['spent_est'] + c, 4); L['entries'].append({'at': time.strftime('%Y-%m-%dT%H:%M:%S'), 'label': LABEL, 'tasks': len(tasks), 'cost_est': round(c, 4)})
        json.dump(L, open(LEDGER, 'w'), indent=1); json.dump({'device': DEVICE, 'qubit': QUBIT, 'tasks': tasks}, open(TASKS, 'w'), indent=1)
        print(f'submitted {len(tasks)}; ledger now ${L["spent_est"]:.2f} / ${L["cap"]:.2f}')
if __name__ == '__main__': main()
