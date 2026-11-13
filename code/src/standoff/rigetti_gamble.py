"""RIGETTI'S GAMBLE -- 2026-09-28 night, Wayfinder paid for it. Cepheus q0 (the qutrit we tuned 9/25) + q1 (its CZ partner).
No outcome written. What is measured:
 SHUFFLE (the start): the at-rest state, shuffled across rungs 0/1/2 by hand (a = flip 0<->1, b = swap 1<->2 via the f12 frame),
   8 sequences, read. Fit together: how much sits on each rung at the start (p0,p1,p2), how the readout blurs each rung, and how
   clean the 1<->2 swap is. No outside ruler needed.
 BLINK + TRAIN (spread over time): 'ba' = swap 1<->2 THEN flip 0<->1 (rung 2 -> read as 0) now vs after a 60 us wait, in batches minutes apart. A drop after the
   wait = rung 2 carried in from the last shot draining; batch-to-batch jumps = blinking.
 BELL: q0,q1 joined (both-excited piece goes through the CZ) vs the same gates with q1 at rest; q0 read plain and after 'ba'.
   ENT minus PROD after 'ba' = the eaten one parked on q0's third rung.
  python rigetti_gamble.py sim | dry | submit | collect | analyze"""
import json, math, os, sys, time
import numpy as np
os.environ.setdefault('AWS_PROFILE', 'braket'); os.environ.setdefault('AWS_DEFAULT_REGION', 'us-west-1')
HERE = os.path.dirname(os.path.abspath(__file__)); LEDGER = os.path.join(HERE, 'braket_ledger.json')
DEVICE = "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q"; Q0, Q1 = 0, 1
PER_TASK, PER_SHOT = 0.30, 0.000425
A_PI12 = json.load(open(os.path.join(HERE, 'round1_fit.json')))['a_pi_12']; WF_LEN, WF_SIGMA = 32e-9, 6.794574402304e-9
SEQS = ['e', 'a', 'b', 'ab', 'ba', 'aba', 'bb', 'bab']          # applied left to right
SH_SHUF, SH_BLINK, SH_BELL, N_BATCH = 5000, 3000, 6000, 3
TASKS = os.path.join(HERE, 'gamble_tasks.json'); RES = os.path.join(HERE, 'gamble_results.json')
def _ns(us): return float(f'{int(round(us * 1000 / 4)) * 4}e-9')
def plan():
    arms = [('shuffle', {'seq': s, 'batch': 0}, SH_SHUF) for s in SEQS]
    for bt in range(1, N_BATCH + 1):
        arms += [('blink', {'seq': 'ba', 'wait_us': 0, 'batch': bt}, SH_BLINK), ('blink', {'seq': 'ba', 'wait_us': 60, 'batch': bt}, SH_BLINK),
                 ('blink', {'seq': 'e', 'wait_us': 0, 'batch': bt}, SH_BLINK)]
    arms += [('bell', {'arm': arm, 'read': rd, 'batch': 0}, SH_BELL) for arm in ('ENT', 'PROD') for rd in ('plain', 'ba')]
    return arms
def cost(arms): return sum(PER_TASK + n * PER_SHOT for _, _, n in arms)
def build(arms):
    from braket.circuits import Circuit; from braket.aws import AwsDevice; from braket.pulse import PulseSequence, DragGaussianWaveform
    dev = AwsDevice(DEVICE); f12 = dev.frames[f'Transmon_{Q0}_charge_tx_f12']
    pi12 = lambda: PulseSequence().play(f12, DragGaussianWaveform(WF_LEN, WF_SIGMA, 0.0, float(A_PI12), False))
    def apply(c, seq):
        for ch in seq:
            if ch == 'a': c.rx(Q0, math.pi)
            elif ch == 'b': c.pulse_gate([Q0], pi12())
    def ry(c, q, t): c.rz(q, -math.pi / 2); c.rx(q, t); c.rz(q, math.pi / 2)
    out = []
    for part, p, n in arms:
        c = Circuit().rz(Q0, 0.0)
        if part == 'shuffle': apply(c, p['seq'] if p['seq'] != 'e' else '')
        elif part == 'blink':
            if p['wait_us']: c.pulse_gate([Q0], PulseSequence().delay(f12, _ns(p['wait_us'])))
            apply(c, p['seq'] if p['seq'] != 'e' else '')
        else:
            c.rz(Q1, 0.0); ry(c, Q0, math.pi / 2)
            if p['arm'] == 'ENT': ry(c, Q1, math.pi / 2); c.cz(Q0, Q1); ry(c, Q1, -math.pi / 2)      # Bell pair (CX from q0 to q1)
            else: ry(c, Q1, math.pi / 2); ry(c, Q1, -math.pi / 2); c.cz(Q0, Q1)                     # same gates, q1 back at rest: no both-excited piece
            if p['read'] == 'ba': apply(c, 'ba')
        out.append(Circuit().add_verbatim_box(c))
    return dev, out
# ---------- the shuffle model: populations moved by imperfect flips/swaps, then a 3-rung -> bit readout ----------
def model(x, seq):
    p1, p2, r0, m1, m2, eta = x; P = np.array([1 - p1 - p2, p1, p2])
    for ch in seq:
        if ch == 'a': P = np.array([P[1], P[0], P[2]]) * .995 + P * .005
        elif ch == 'b': P = np.array([P[0], (1 - eta) * P[1] + eta * P[2], eta * P[1] + (1 - eta) * P[2]])
    return r0 * P[0] + m1 * P[1] + m2 * P[2]          # P(read 0)
def fit(y, n):
    from scipy.optimize import least_squares
    best = None
    for p2g in (0.001, 0.005, 0.02):
        for m2g in (0.05, 0.12):
            r = least_squares(lambda x: [(model(x, s if s != 'e' else '') - y[s]) / math.sqrt(max(y[s] * (1 - y[s]), 1e-4) / n[s]) for s in SEQS],
                              [0.05, p2g, 0.97, 0.01, m2g, 0.94], bounds=([0, 0, 0.8, 0, 0, 0.7], [0.3, 0.3, 1, 0.2, 0.5, 1]))
            if best is None or r.cost < best.cost: best = r
    J = best.jac; cov = np.linalg.pinv(J.T @ J); return best.x, np.sqrt(np.diag(cov)), best.cost
def sim():
    rng = np.random.default_rng(212)
    for p2 in (0.003, 0.015):
        truth = [0.05, p2, 0.965, 0.008, 0.11, 0.94]; y = {s: rng.binomial(SH_SHUF, model(truth, s if s != 'e' else '')) / SH_SHUF for s in SEQS}
        x, e, _ = fit(y, {s: SH_SHUF for s in SEQS}); print(f'SIM true rung2 {p2:.3%}: fit rung2 {x[1]:.3%} +/- {e[1]:.3%} | rung1 {x[0]:.3%} +/- {e[0]:.3%} | swap {x[5]:.3f}')
def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'dry'; arms = plan(); c = cost(arms)
    if mode == 'sim': sim(); print(f'{len(arms)} tasks, {sum(n for *_, n in arms)} shots, ${c:.2f}'); return
    if mode == 'dry':
        dev, circs = build(arms); print(f'{len(arms)} tasks, ${c:.2f}; device {dev.status}'); print(circs[3]); print(circs[-1]); return
    if mode == 'submit':
        L = json.load(open(LEDGER)); L['cap'] = round(L['spent_est'] + c + 0.01, 4)      # Wayfinder approved this spend 9/28 night
        dev, circs = build(arms); T = {'tasks': []}
        order = [i for i, a in enumerate(arms) if a[1]['batch'] in (0, 1)]
        for i in order:
            t = dev.run(circs[i], shots=arms[i][2], disable_qubit_rewiring=True); T['tasks'].append({'arm': arms[i], 'arn': t.id, 'sent': time.time()}); print('sent', arms[i][0], arms[i][1], flush=True)
        json.dump(T, open(TASKS, 'w'), indent=1)
        for bt in range(2, N_BATCH + 1):
            time.sleep(300)                                                               # blink batches minutes apart
            for i, a in enumerate(arms):
                if a[0] == 'blink' and a[1]['batch'] == bt:
                    t = dev.run(circs[i], shots=a[2], disable_qubit_rewiring=True); T['tasks'].append({'arm': a, 'arn': t.id, 'sent': time.time()}); print('sent', a[0], a[1], flush=True)
            json.dump(T, open(TASKS, 'w'), indent=1)
        L['spent_est'] = round(L['spent_est'] + c, 4); L['entries'].append({'at': time.strftime('%Y-%m-%dT%H:%M:%S'), 'label': "Rigetti's Gamble (shuffle, blink/train, Bell) q0/q1", 'tasks': len(arms), 'cost_est': round(c, 4)})
        json.dump(L, open(LEDGER, 'w'), indent=1); print('ALL SENT; ledger', L['spent_est']); return
    if mode == 'collect':
        from braket.aws import AwsQuantumTask
        T = json.load(open(TASKS)); out = []
        for t in T['tasks']:
            task = AwsQuantumTask(t['arn']); st = task.state(); r = {'arm': t['arm'], 'state': st}
            if st == 'COMPLETED': r['counts'] = task.result().measurement_counts
            out.append(r)
        json.dump({'results': out}, open(RES, 'w'), indent=1); print({s: sum(1 for r in out if r['state'] == s) for s in set(r['state'] for r in out)}); return
def analyze():
    R = json.load(open(RES))['results']; ok = [r for r in R if r['state'] == 'COMPLETED']
    def p0(r, bit=0):
        c = r['counts']; n = sum(c.values()); return sum(v for k, v in c.items() if k[bit] == '0') / n, n
    y, n = {}, {}
    for r in ok:
        if r['arm'][0] == 'shuffle': s_ = r['arm'][1]['seq']; y[s_], n[s_] = p0(r)
    if len(y) == len(SEQS):
        x, e, cost_ = fit(y, n)
        print(f"THE START (q0, shuffled across rungs 0/1/2, fitted together): rung 1 {x[0]:.2%} +/- {e[0]:.2%} | RUNG 2 {x[1]:.2%} +/- {e[1]:.2%}")
        print(f"   readout: rung0 reads 0 {x[2]:.3f}, rung1 misread as 0 {x[3]:.3f}, rung2 misread as 0 {x[4]:.3f}; swap clean {x[5]:.3f}; fit quality {2 * cost_ / 2:.1f} for 2 spare numbers")
    else: x = None; print('shuffle incomplete', len(y))
    B = {}
    for r in ok:
        if r['arm'][0] == 'blink': a = r['arm'][1]; B.setdefault(a['batch'], {})[(a['seq'], a['wait_us'])] = p0(r)[0]
    for bt in sorted(B):
        b = B[bt]; line = f"   batch {bt}: rung-2 read (swap then flip) now {b.get(('ba', 0), float('nan')):.4f}, after 60 us {b.get(('ba', 60), float('nan')):.4f}, plain {b.get(('e', 0), float('nan')):.4f}"
        if x is not None and ('ba', 0) in b: line += f"  -> rung 2 now ~{(b[('ba', 0)] - (x[2] * 0 + x[3] * x[0] + x[4] * 0)) :.4f} raw"
        print(line)
    print('BLINK/TRAIN: batches are minutes apart; now-vs-60us drop = rung 2 draining (carried); batch jumps = blinking')
    Bl = {}
    for r in ok:
        if r['arm'][0] == 'bell': a = r['arm'][1]; c = r['counts']; nn = sum(c.values()); Bl[(a['arm'], a['read'])] = (c, nn)
    if len(Bl) == 4:
        q0z = lambda k: sum(v for kk, v in Bl[k][0].items() if kk[0] == '0') / Bl[k][1]
        q1z = lambda k: sum(v for kk, v in Bl[k][0].items() if kk[1] == '0') / Bl[k][1]
        d = q0z(('ENT', 'ba')) - q0z(('PROD', 'ba')); se = math.sqrt(sum(q0z(k) * (1 - q0z(k)) / Bl[k][1] for k in (('ENT', 'ba'), ('PROD', 'ba'))))
        print(f"BELL: q0 reads 0 after swap-then-flip (= q0 was on rung 2): joined {q0z(('ENT', 'ba')):.4f} vs not joined {q0z(('PROD', 'ba')):.4f} -> extra {d:+.4f} +/- {se:.4f}")
        print(f"      plain reads: joined q0=1 {1 - q0z(('ENT', 'plain')):.4f}, q1=1 {1 - q1z(('ENT', 'plain')):.4f} | not joined q0=1 {1 - q0z(('PROD', 'plain')):.4f}, q1=1 {1 - q1z(('PROD', 'plain')):.4f}")
        ce = Bl[('ENT', 'plain')][0]; nn = Bl[('ENT', 'plain')][1]; print('      joined pair outcomes:', {k: round(v / nn, 4) for k, v in sorted(ce.items())})
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'analyze': analyze()
    else: main()
