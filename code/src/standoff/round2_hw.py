"""ROUND 2 on hardware -- the pointer weak measurement designed in round2_weak.py (read its docstring first). Rigetti Cepheus
q0 = the qutrit (three boxes), q1 = the pointer. Same ops and conventions as the sim; q1 gets only native rx/rz; one native CZ.
  --cal-dry | --cal-submit : 9 calibration tasks (qutrit parked in 0/1/2, pointer tomography X/Y/Z), un-post-selected.
                             Answers the real unknown first: what the CZ does when level 2 is occupied (phase zeta, leakage).
  --run-dry | --run-submit : the 3 shelving configs x 3 bases at g = pi/4 (9 tasks) -- only after the calibration looks sane.
  --collect | --analyze
Same ledger brake as every other step (braket_ledger.json, CAP from step 3).
"""
import json, math, os, sys, time
import numpy as np
import braket_round1_step3 as s3
import round2_weak as rw

HERE = os.path.dirname(os.path.abspath(__file__))
Q, P = 0, 1
SHOTS = int(os.environ.get("R2SHOTS", "1000"))
X0 = json.load(open(os.path.join(HERE, 'step3_abl.json')))['x0']
XPHI = X0 - math.pi                           # step 3's measured phi setting
G = math.pi / 4

def cal_arms(): return [('cal', l, b) for l in (0, 1, 2) for b in 'XYZ']
def run_arms(): return [('run', c, b) for c in 'ABC' for b in 'XYZ']

def build(arms):
    from braket.circuits import Circuit
    from braket.aws import AwsDevice
    from braket.pulse import PulseSequence, DragGaussianWaveform
    dev = AwsDevice(s3.DEVICE); f12 = dev.frames[f'Transmon_{Q}_charge_tx_f12']
    def qut(c, op):
        if op[0] == 'rx': c.rx(Q, op[1]); return
        ps = PulseSequence()
        if op[2]: ps = ps.shift_phase(f12, op[2])
        ps = ps.play(f12, DragGaussianWaveform(s3.WF_LEN, s3.WF_SIGMA, 0.0, float(s3.A_PI12 * op[1] / math.pi), False))
        if op[2]: ps = ps.shift_phase(f12, -op[2])
        c.pulse_gate([Q], ps)
    def ry(c, t):   # ry(t) = rz(-pi/2) rx(t) rz(pi/2), rx only at native angles
        c.rz(P, math.pi / 2); c.rx(P, t); c.rz(P, -math.pi / 2)
    out = []
    for kind, which, basis in arms:
        c = Circuit().rz(Q, 0.0).rz(P, 0.0)
        if kind == 'cal':
            if which >= 1: qut(c, ('rx', math.pi))
            if which == 2: qut(c, ('f12', math.pi, 0.0))
            pre, post = [], []
        else:
            for op in s3.PREPS['psi']: qut(c, op)
            pre, post = rw.SHELVE[which]
        ry(c, 2 * G)                                   # pointer cos g|0> + sin g|1>, g = pi/4 -> ry(pi/2)
        for op in pre: qut(c, op)
        c.cz(Q, P)
        for op in post: qut(c, op)
        if kind == 'run':
            for op in s3.V(XPHI): qut(c, op)
        if basis == 'X': ry(c, -math.pi / 2)
        elif basis == 'Y': c.rx(P, math.pi / 2)
        out.append(Circuit().add_verbatim_box(c))
    return dev, out

def spend(label, arms, submit):
    cost = len(arms) * (s3.PER_TASK + SHOTS * s3.PER_SHOT); L = json.load(open(s3.LEDGER))
    if L['spent_est'] + cost > s3.CAP: raise SystemExit(f'BRAKE: ${cost:.2f} would pass ${s3.CAP:.2f} (spent ${L["spent_est"]:.2f})')
    print(f'{label}: {len(arms)} tasks = ${cost:.2f}  (spent ${L["spent_est"]:.2f} / ${s3.CAP:.2f})')
    dev, circs = build(arms)
    if not submit: print(circs[-1]); return
    tf = os.path.join(HERE, 'round2_tasks.json'); T = json.load(open(tf)) if os.path.exists(tf) else {'tasks': []}
    for a, c in zip(arms, circs):
        t = dev.run(c, shots=SHOTS, disable_qubit_rewiring=True); T['tasks'].append({'arm': a, 'arn': t.id}); print('sent', a, flush=True)
    L['spent_est'] = round(L['spent_est'] + cost, 4)
    L['entries'].append({'at': time.strftime('%Y-%m-%dT%H:%M:%S'), 'label': label, 'tasks': len(arms), 'cost_est': round(cost, 4)})
    json.dump(L, open(s3.LEDGER, 'w'), indent=1); json.dump(T, open(tf, 'w'), indent=1)
    print(f'submitted; ledger ${L["spent_est"]:.2f} / ${s3.CAP:.2f}')

def collect():
    from braket.aws import AwsQuantumTask
    T = json.load(open(os.path.join(HERE, 'round2_tasks.json'))); out = []
    for t in T['tasks']:
        task = AwsQuantumTask(t['arn']); st = task.state(); r = {'arm': t['arm'], 'state': st}
        if st == 'COMPLETED':
            m = task.result().measurement_counts; tot = sum(m.values())
            # key = bits in measured-qubit order (q0, q1). q = 1 when the qutrit reads 0 (post-selected), b = pointer bit
            r['p'] = {f'{int(k[0] == "0")}{k[1]}': v / tot for k, v in m.items()}
        out.append(r)
    json.dump({'results': out}, open(os.path.join(HERE, 'round2_results.json'), 'w'), indent=1)
    print(sum(o['state'] == 'COMPLETED' for o in out), '/', len(out), 'complete')

def analyze():
    R = json.load(open(os.path.join(HERE, 'round2_results.json')))['results']
    rw.NOISY = True
    def cnt(kind, which):
        d = {}
        for r in R:
            a = r['arm']
            if a[0] == kind and a[1] == which and r['state'] == 'COMPLETED':
                d[a[2]] = {(int(k[0]), int(k[1])): v for k, v in r['p'].items()}
                for q in (0, 1):
                    for b in (0, 1): d[a[2]].setdefault((q, b), 0.0)
        return d
    cal = {l: rw.bloch_from_counts(cnt('cal', l), post=False) for l in (0, 1, 2) if len(cnt('cal', l)) == 3}
    for l, v in cal.items(): print(f'cal level {l}: pointer Bloch x {v[0]:+.3f} y {v[1]:+.3f} z {v[2]:+.3f}  |xy| {math.hypot(v[0], v[1]):.3f}')
    if len(cal) == 3:
        ph = rw.phases_from_cal(cal); print('CZ phases (rad): ', {k: round(v, 3) for k, v in ph.items()}, '  ideal 0, pi, zeta')
        print('  |xy| well below the level-0 value on level 2 = the CZ is scrambling/leaking level 2, not just phasing it')
        runs = {c: cnt('run', c) for c in 'ABC'}
        if all(len(v) == 3 for v in runs.values()):
            Rs = {c: rw.R_of(rw.bloch_from_counts(runs[c]), G) for c in 'ABC'}
            W = rw.fit_W(Rs, ph); print('\nWEAK VALUES  A {:+.3f}  B {:+.3f}  C {:+.3f}   (QM +1, +1, -1)'.format(*W))
            json.dump({'phases': ph, 'W': list(W), 'R': {c: [Rs[c].real, Rs[c].imag] for c in Rs}}, open(os.path.join(HERE, 'round2_analysis.json'), 'w'), indent=1)

if __name__ == '__main__':
    m = sys.argv[1] if len(sys.argv) > 1 else '--cal-dry'
    if m in ('--cal-dry', '--cal-submit'): spend('round2 calibration (CZ vs level 2)', cal_arms(), m.endswith('submit'))
    elif m in ('--run-dry', '--run-submit'): spend('round2 weak values (3 configs x 3 bases)', run_arms(), m.endswith('submit'))
    elif m == '--collect': collect()
    elif m == '--analyze': analyze()
