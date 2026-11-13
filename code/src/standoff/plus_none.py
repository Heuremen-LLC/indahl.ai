"""THE PLUS NONE -- 2026-09-26 (Wayfinder: "do it"). Rigetti Cepheus, qubit 99 (q0/q90 belong to the two-witness ring).

Five-step chain ("laws 1-5") on one qubit:  L1 rx(pi/2)  L2 rz(pi/3)  L3 rx(pi)  L4 rz(pi/3)  L5 rx(pi)
(L3-L5 = rx(pi) rz(pi/3) rx(pi) = rz(-pi/3) cancels L2: the chain leaves the qubit on the equator, and a static detuning
phase accumulated anywhere after L1 comes out of the chain unchanged -- which is what makes (a) and (b) a fair comparison.)
Then the sixth slot, a NONE, in three flavors at the same elapsed time D:
  (a) HAPPENS   : chain, then an empty scheduled slot (delay D), then analysis
  (b) NEVER     : no slot after L5; the same D is spent between L1 and L2, where the qubit is on the SAME equator orbit, so
                  T1, T2 and detuning act on it identically -- the only difference is WHERE in the chain the time lives
  (c) COUNTERFEIT: chain, rx(pi), delay D, rx(pi)  (= identity up to global phase; a flipped frame during D: textbook predicts
                  the detuning phase comes out with the opposite sign, and relaxation's z-shift flipped)
  ref: chain + analysis, no D
Analysis settings: S1 = rx(pi/2) ; S2 = rz(pi/2), rx(pi/2).  Read P(1).
TEXTBOOK: P_a = P_b exactly (for any T1, T2, detuning), at both D. Crazy-hat signature (pre-registered): |P_a - P_b| > 3 sigma
(bootstrap) at BOTH D = 2 us and 6 us, same sign, in the same setting.
  qvenv/bin/python plus_none.py --sim | --submit | --collect | --analyze
"""
import json, math, os, sys, time
import numpy as np
import braket_round1_step3 as s3

HERE = os.path.dirname(os.path.abspath(__file__))
Q = 99
DS = [2000, 6000]                      # ns, on the 4 ns grid
SETTINGS = ['S1', 'S2']
SHOTS = 1300
LABEL = 'plus-none q99 (a happens / b never / c counterfeit)'
JOB_CAP = 12.0
SEED_SLICE = (24000, 24064)             # middle of pup_seeds.bin (the ring used the end)
T1, T2 = 43.1e-6, 33.9e-6               # device properties for q99, 2026-09-26

def arms():
    a = [('ref', 0, s) for s in SETTINGS]
    for D in DS:
        for f in 'abc':
            for st in SETTINGS: a.append((f, D, st))
    return a

# ---------- Bloch model: ideal gates, amplitude damping T1, pure dephasing T2, static detuning delta ----------
def rot(axis, th):
    c, s = math.cos(th), math.sin(th)
    if axis == 'x': return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
def idle(v, D, delta):
    t = D * 1e-9; x, y, z = v
    ph = 2 * math.pi * delta * t; x, y = x * math.cos(ph) - y * math.sin(ph), x * math.sin(ph) + y * math.cos(ph)
    return np.array([x * math.exp(-t / T2), y * math.exp(-t / T2), 1 - (1 - z) * math.exp(-t / T1)])
def run_model(flavor, D, setting, delta=0.0):
    v = np.array([0., 0., 1.])
    L = [('x', math.pi / 2), ('z', math.pi / 3), ('x', math.pi), ('z', math.pi / 3), ('x', math.pi)]
    for k, (ax, th) in enumerate(L):
        v = rot(ax, th) @ v
        if flavor == 'b' and k == 0: v = idle(v, D, delta)
    if flavor == 'a': v = idle(v, D, delta)
    if flavor == 'c': v = rot('x', math.pi) @ v; v = idle(v, D, delta); v = rot('x', math.pi) @ v
    if setting == 'S2': v = rot('z', math.pi / 2) @ v
    v = rot('x', math.pi / 2) @ v
    return (1 - v[2]) / 2        # P(1)

def sim():
    for delta in (0.0, 30e3, 100e3):
        print(f'detuning {delta/1e3:.0f} kHz:')
        for f, D, st in arms():
            print(f'   {f} D={D:>4} {st}: P1 {run_model(f, D, st, delta):.4f}')
    print('max |a-b| over detunings/D/settings:', max(abs(run_model('a', D, st, d) - run_model('b', D, st, d)) for d in (0, 3e4, 1e5, 3e5) for D in DS for st in SETTINGS))
    n = len(arms()); print(f'{n} tasks x {SHOTS} = ${n * (s3.PER_TASK + SHOTS * s3.PER_SHOT):.2f}')

def build(arms_):
    from braket.circuits import Circuit
    from braket.aws import AwsDevice
    from braket.pulse import PulseSequence
    dev = AwsDevice(s3.DEVICE); fr = [dev.frames[f'Transmon_{Q}_charge_tx'], dev.frames[f'Transmon_{Q}_charge_tx_f12']]
    def delay(c, D):
        c.pulse_gate([Q], PulseSequence().delay(fr, float(f'{D}e-9')))
    out = []
    for f, D, st in arms_:
        c = Circuit().rz(Q, 0.0)
        c.rx(Q, math.pi / 2)
        if f == 'b': delay(c, D)
        c.rz(Q, math.pi / 3).rx(Q, math.pi).rz(Q, math.pi / 3).rx(Q, math.pi)
        if f == 'a': delay(c, D)
        if f == 'c': c.rx(Q, math.pi); delay(c, D); c.rx(Q, math.pi)
        if st == 'S2': c.rz(Q, math.pi / 2)
        c.rx(Q, math.pi / 2)
        out.append(Circuit().add_verbatim_box(c))
    return dev, out

def coin_order(n):
    b = open(os.path.join(HERE, 'pup_seeds.bin'), 'rb').read()[SEED_SLICE[0]:SEED_SLICE[1]]
    idx = list(range(n)); k = 0
    for i in range(n - 1, 0, -1):            # Fisher-Yates driven by the qubit bytes
        j = int.from_bytes(b[k:k + 2], 'big') % (i + 1); k += 2; idx[i], idx[j] = idx[j], idx[i]
    return idx

def main():
    m = sys.argv[1] if len(sys.argv) > 1 else '--sim'
    if m == '--sim': sim(); return
    A = arms(); tf = os.path.join(HERE, 'plus_none_tasks.json')
    if m == '--submit':
        cost = len(A) * (s3.PER_TASK + SHOTS * s3.PER_SHOT)
        if cost > JOB_CAP: raise SystemExit(f'JOB BRAKE: ${cost:.2f} > ${JOB_CAP}')
        order = coin_order(len(A)); dev, circs = build(A); tasks = []
        for i in order:
            L = json.load(open(s3.LEDGER)); one = s3.PER_TASK + SHOTS * s3.PER_SHOT
            if L['spent_est'] + one > s3.CAP: raise SystemExit(f'LEDGER BRAKE at task {len(tasks)}: spent ${L["spent_est"]:.2f}')
            t = dev.run(circs[i], shots=SHOTS, disable_qubit_rewiring=True)
            L['spent_est'] = round(L['spent_est'] + one, 4); json.dump(L, open(s3.LEDGER, 'w'), indent=1)
            tasks.append({'arm': A[i], 'arn': t.id, 'submitted': time.strftime('%Y-%m-%dT%H:%M:%S')}); print('sent', A[i], flush=True)
        L = json.load(open(s3.LEDGER)); L['entries'].append({'at': time.strftime('%Y-%m-%dT%H:%M:%S'), 'label': LABEL, 'tasks': len(tasks), 'cost_est': round(cost, 4)})
        json.dump(L, open(s3.LEDGER, 'w'), indent=1)
        json.dump({'qubit': Q, 'seed_slice': SEED_SLICE, 'order': order, 'tasks': tasks}, open(tf, 'w'), indent=1)
        print(f'submitted {len(tasks)}; ledger ${L["spent_est"]:.2f}')
    if m == '--collect':
        from braket.aws import AwsQuantumTask
        T = json.load(open(tf)); out = []
        for t in T['tasks']:
            task = AwsQuantumTask(t['arn']); st = task.state(); r = {'arm': t['arm'], 'state': st, 'submitted': t['submitted']}
            if st == 'COMPLETED':
                res = task.result(); r['shots'] = [int(x[0]) for x in res.measurements]
                md = task.metadata(); r['created'] = str(md.get('createdAt')); r['ended'] = str(md.get('endedAt'))
            out.append(r)
        json.dump({'qubit': Q, 'results': out}, open(os.path.join(HERE, 'plus_none_results.json'), 'w'))
        print(sum(o['state'] == 'COMPLETED' for o in out), '/', len(out), 'complete')
    if m == '--analyze':
        R = {tuple(r['arm']): np.array(r['shots']) for r in json.load(open(os.path.join(HERE, 'plus_none_results.json')))['results'] if r.get('shots')}
        rng = np.random.default_rng(212); out = {}
        for D in DS:
            for st in SETTINGS:
                a, b, c = R[('a', D, st)], R[('b', D, st)], R[('c', D, st)]
                boot = [rng.choice(a, len(a)).mean() - rng.choice(b, len(b)).mean() for _ in range(4000)]
                d, e = a.mean() - b.mean(), float(np.std(boot))
                out[f'{D}_{st}'] = {'Pa': a.mean(), 'Pb': b.mean(), 'Pc': c.mean(), 'ref': R[('ref', 0, st)].mean(), 'a_minus_b': d, 'err': e, 'sigma': d / e,
                                    'model_a_eq_b': run_model('a', D, st)}
                print(f'D={D} {st}: Pa {a.mean():.3f}  Pb {b.mean():.3f}  Pc {c.mean():.3f}  ref {R[("ref", 0, st)].mean():.3f}   a-b {d:+.4f} +/- {e:.4f} ({d/e:+.1f} sigma)')
        claim = any(all(abs(out[f'{D}_{st}']['sigma']) > 3 for D in DS) and np.sign(out[f'{DS[0]}_{st}']['a_minus_b']) == np.sign(out[f'{DS[1]}_{st}']['a_minus_b']) for st in SETTINGS)
        print('PRE-REGISTERED CLAIM (a != b beyond 3 sigma at both D, same sign, same setting):', 'MET' if claim else 'NOT MET')
        # open eyes: streaks and drift inside each task (exploratory)
        eyes = {}
        for k, s in R.items():
            runs = np.diff(np.flatnonzero(np.diff(np.r_[-1, s, -1]) != 0)); first, last = s[:len(s)//2].mean(), s[len(s)//2:].mean()
            eyes[str(k)] = {'longest_run': int(runs.max()), 'first_half': first, 'second_half': last}
        json.dump({'prereg': out, 'claim_met': bool(claim), 'open_eyes': eyes}, open(os.path.join(HERE, 'plus_none_analysis.json'), 'w'), indent=1, default=float)

if __name__ == '__main__':
    main()
