"""THE TIME CORNER ON A SECOND VENDOR, WITH THE THIRD RUNG READ (Bones, 2026-10-04; Wayfinder: "Fire away until we're dry... ride triangulated").
Rigetti Cepheus-1-108Q, every qubit in parallel. The push train of time_wide.py (IBM), spaced in the qubit's own time (Cepheus T1 median ~27 us, so the
IBM ladder's fractions of the decay time become 1 / 3 / 8 / 20 us, plus back-to-back), with each qubit's own decay read in the same batch in three copies, and
the end state read on all three rungs: every arm is read plain ('e') and through the tuned 1<->2 swap then the 0<->1 flip ('ba'), and each batch carries
its own readout calibration (the 9/28 shuffle: eight sequences on the rest state), so rung-1 and rung-2 populations are separated per qubit and per arm.
No number of ours is written for it and nothing is parked on one.
Stages, one at a time, each checked before the next:
  tune-submit / tune-collect / tune-fit    each qubit's 1<->2 swap amplitude (8 amplitudes x 1000 shots)
  read-submit K / read-collect K           batch K = 1, 2, 3 (minutes apart): 8 calibration x 1500 shots + 25 arms x 2 readouts x 900 shots
  CORNERS: this run reads OUR laid clock (the spacing) against each qubit's OWN decay (three copies), plus the third rung. It has no witness clocks
  (every qubit is pushed); its witness side is read against the 9/28 Cepheus witness runs and the 4 October IBM runs, said so, not implied.
  analyze                                  raw rows (rung 1, rung 2, bookkeeping both ways) per arm, per batch
CAP: the whole plan (8 + 3 x 58 = 182 tasks, 8,000 + 3 x 57,000 = 179,000 shots) is the day's ceiling; a stage that would pass it is refused."""
import json, math, os, sys, time
import numpy as np
os.environ.setdefault('AWS_PROFILE', 'braket'); os.environ.setdefault('AWS_DEFAULT_REGION', 'us-west-1')
HERE = os.path.dirname(os.path.abspath(__file__)); LEDGER = os.path.join(HERE, 'braket_ledger.json')
DEVICE = "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q"; PER_TASK, PER_SHOT = 0.30, 0.000425
WF_LEN, WF_SIGMA = 32e-9, 6.794574402304e-9
TUNE_AMPS = [0.0, 0.06, 0.10, 0.14, 0.18, 0.24, 0.32, 0.50]; SH_TUNE = 1000
SEQS = ['e', 'a', 'b', 'ab', 'ba', 'aba', 'bb', 'bab']; SH_CAL = 1500
SPACINGS = [0, 1, 3, 8, 20]; PUSHES = 10; RULER = [3, 10, 30]; SH_ARM = 900
DAY_CAP_TASKS, DAY_CAP_SHOTS = 182, 179000
OUT = os.path.join(HERE, 'time20261004'); os.makedirs(OUT, exist_ok=True); STATE = os.path.join(OUT, 'state.json')
QS = sorted(int(r[0]) for r in json.load(open(os.path.join(HERE, 'cepheus_props_20260928.json'))))
def _ns(us): return float(f'{int(round(us * 1000 / 4)) * 4}e-9')
def state():
    try: return json.load(open(STATE))
    except Exception: return {'tasks': 0, 'shots': 0, 'stages': []}
def dev_frames():
    from braket.aws import AwsDevice
    dev = AwsDevice(DEVICE); return dev, {q: dev.frames[f'Transmon_{q}_charge_tx_f12'] for q in QS}
def f12(fr, amps):
    from braket.pulse import PulseSequence, DragGaussianWaveform
    ps = PulseSequence()
    for q in QS:
        if amps.get(q, 0) > 0: ps = ps.play(fr[q], DragGaussianWaveform(WF_LEN, WF_SIGMA, 0.0, float(amps[q]), False))
    return ps
def wait(c, fr, us):
    from braket.pulse import PulseSequence
    if us <= 0: return
    ps = PulseSequence()
    for q in QS: ps = ps.delay(fr[q], _ns(us))
    c.pulse_gate(QS, ps)
def readseq(c, fr, amps, seq):
    for ch in ('' if seq == 'e' else seq):
        if ch == 'a':
            for q in QS: c.rx(q, math.pi)
        else: c.pulse_gate(QS, f12(fr, amps))
def arms():
    A = []
    for s in ('OFF', 'ON', 'MID'):
        for g in SPACINGS: A.append({'key': f'{s}|g{g}', 'start': s, 'gap': g, 'pushes': PUSHES})
    for cp in 'abc':
        for w in RULER: A.append({'key': f'RULER|ON|w{w}|{cp}', 'start': 'ON', 'gap': None, 'wait': w})
    A.append({'key': 'RULER|OFF|w30', 'start': 'OFF', 'gap': None, 'wait': 30})
    return A
def build(fr, amps, arm, seq):
    from braket.circuits import Circuit
    c = Circuit()
    for q in QS: c.rz(q, 0.0)
    if arm['start'] == 'ON':
        for q in QS: c.rx(q, math.pi)
    elif arm['start'] == 'MID':
        for q in QS: c.rx(q, math.pi / 2)
    if arm.get('gap') is None: wait(c, fr, arm['wait'])
    else:
        for _ in range(arm['pushes']):
            wait(c, fr, arm['gap'])
            for q in QS: c.rx(q, math.pi)
    readseq(c, fr, amps, seq)
    return Circuit().add_verbatim_box(c)
def cal_circ(fr, amps, seq):
    from braket.circuits import Circuit
    c = Circuit()
    for q in QS: c.rz(q, 0.0)
    readseq(c, fr, amps, seq); return Circuit().add_verbatim_box(c)
def tune_circ(fr, a):
    from braket.circuits import Circuit
    c = Circuit()
    for q in QS: c.rz(q, 0.0)
    for q in QS: c.rx(q, math.pi)
    if a > 0: c.pulse_gate(QS, f12(fr, {q: a for q in QS}))
    for q in QS: c.rx(q, math.pi)
    return Circuit().add_verbatim_box(c)
def guard_and_book(label, items):
    S = state(); nt = len(items); ns = sum(n for *_, n in items)
    if S['tasks'] + nt > DAY_CAP_TASKS or S['shots'] + ns > DAY_CAP_SHOTS:
        sys.exit(f"REFUSED: {label} would take the day to {S['tasks'] + nt} tasks / {S['shots'] + ns} shots, past the cap {DAY_CAP_TASKS} / {DAY_CAP_SHOTS}")
    c = nt * PER_TASK + ns * PER_SHOT
    L = json.load(open(LEDGER)); L['cap'] = round(L['spent_est'] + c + 0.01, 4)        # Wayfinder: "Fire away until we're dry" (10/4), within the plan he was given
    L['spent_est'] = round(L['spent_est'] + c, 4); L['entries'].append({'at': time.strftime('%Y-%m-%dT%H:%M:%S'), 'label': label, 'tasks': nt, 'shots': ns, 'cost_est': round(c, 4)})
    json.dump(L, open(LEDGER, 'w'), indent=1)
    S['tasks'] += nt; S['shots'] += ns; S['stages'].append({'label': label, 'tasks': nt, 'shots': ns, 'at': time.strftime('%H:%M:%S')}); json.dump(S, open(STATE, 'w'), indent=1)
    print(f'{label}: {nt} tasks, {ns} shots; day so far {S["tasks"]} / {DAY_CAP_TASKS} tasks, {S["shots"]} / {DAY_CAP_SHOTS} shots')
def send(dev, items, fname):
    T = {'tasks': []}
    for tag, cc, n in items:
        t = dev.run(cc, shots=n, disable_qubit_rewiring=True); T['tasks'].append({'tag': tag, 'arn': t.id, 'sent': time.time()})
        json.dump(T, open(os.path.join(OUT, fname), 'w'), indent=1)
    print('sent', len(items), 'tasks ->', fname)
def collect(fname, npzname, wait_done=True):
    from braket.aws import AwsQuantumTask
    T = json.load(open(os.path.join(OUT, fname))); arrs = {}
    while True:
        st = [AwsQuantumTask(t['arn']).state() for t in T['tasks']]
        if not wait_done or all(s in ('COMPLETED', 'FAILED', 'CANCELLED') for s in st): break
        time.sleep(20)
    states = {}
    for t, s in zip(T['tasks'], st):
        states[s] = states.get(s, 0) + 1
        if s == 'COMPLETED':
            r = AwsQuantumTask(t['arn']).result(); mq = list(r.measured_qubits); m = np.asarray(r.measurements); arrs[json.dumps(t['tag'])] = m[:, [mq.index(q) for q in QS]]
    np.savez_compressed(os.path.join(OUT, npzname), **arrs); print('collected', states, '->', npzname)
def tune_fit():
    Z = dict(np.load(os.path.join(OUT, 'tune.npz'))); A = [a for a in TUNE_AMPS if json.dumps(['tune', a]) in Z]
    y = np.array([1 - Z[json.dumps(['tune', a])].mean(0) for a in A]); fit = {}
    for k, q in enumerate(QS):
        yy = y[:, k]; best = None
        for api in np.linspace(0.05, 0.9, 171):
            X = np.stack([np.ones(len(A)), np.cos(np.pi * np.array(A) / api)], 1); b, *_ = np.linalg.lstsq(X, yy, rcond=None); r = float(np.sum((X @ b - yy) ** 2))
            if best is None or r < best[0]: best = (r, api, b[1])
        fit[q] = {'a_pi12': best[1], 'swing': float(abs(best[2]) * 2), 'rms': math.sqrt(best[0] / len(A))}
    json.dump(fit, open(os.path.join(OUT, 'tune_fit.json'), 'w'), indent=1)
    old = json.load(open(os.path.join(HERE, 'chip', 'tune_fit.json')))
    d = [fit[q]['a_pi12'] - old[str(q)]['a_pi12'] for q in QS if str(q) in old and fit[q]['swing'] > 0.3 and old[str(q)]['swing'] > 0.3]
    print(f"tuned: {sum(v['swing'] > 0.3 for v in fit.values())} of {len(QS)} qubits swing > 0.3 (9/28: 95); median a_pi12 {np.median([v['a_pi12'] for v in fit.values()]):.3f} (9/28: 0.150); "
          f"change vs 9/28 on qubits good both days: median {np.median(d):+.3f}, middle half {np.percentile(d, 25):+.3f}..{np.percentile(d, 75):+.3f}")

# ---------------- BATCH 3, THE WITNESS (added 10/4 after batches 1-2 had no clocks inside; Wayfinder: "Observer. Witness. Triangles. Time.") ----------------
# Emitters: seeded order (202610043), each >= 5 links from every earlier one (so clocks sit at 1, 2 AND 3+ links -- at >= 3 the grid gave only 1 and 2: two lanes), only qubits whose swap is tuned.
# Clocks: every other qubit, put half-way after the starts, free through the train, read on two hands (X: rx(pi/2); Y: rz(pi/2) rx(pi/2)); distance to the
# nearest emitter read afterwards. Reference: the same clocks over laid windows with the emitters at rest and with the emitters held in |1>.
# Pairing: hand X with the emitters' plain read, hand Y with their 'ba' read (different qubits, read at the same moment).
WIT_STARTS = ['OFF', 'ON']; WIT_T = [0, 3, 10, 30, 80]; WIT_T_ON = [3, 10, 30]; EM_RULER = [3, 10, 30]
def roles(fit):
    E = json.load(open(os.path.join(OUT, 'cepheus_edges.json')))['edges']; nb = {q: set() for q in QS}
    for a, b in E:
        if a in nb and b in nb: nb[a].add(b); nb[b].add(a)
    def within4(s):
        d = {s: 0}; fr = [s]
        while fr:
            u = fr.pop(0)
            if d[u] == 4: continue
            for v in nb[u]:
                if v not in d: d[v] = d[u] + 1; fr.append(v)
        return set(d)
    em, blocked = [], set()
    for q in np.random.default_rng(202610043).permutation(QS):
        q = int(q)
        if q in blocked or not nb[q] or fit[str(q)]['swing'] <= 0.3: continue
        em.append(q); blocked |= within4(q)
    return sorted(em), [q for q in QS if q not in em], {q: sorted(nb[q]) for q in QS}
def wit_circ(fr, amps, EM, CL, start, gap, hand, em_seq, t_ref=None, em_hold=None):
    from braket.circuits import Circuit
    c = Circuit()
    for q in QS: c.rz(q, 0.0)
    if t_ref is None:
        if start == 'ON':
            for q in EM: c.rx(q, math.pi)
    elif em_hold == 'ON':
        for q in EM: c.rx(q, math.pi)
    for q in CL: c.rx(q, math.pi / 2)
    if t_ref is not None: wait(c, fr, t_ref)
    else:
        for _ in range(PUSHES):
            wait(c, fr, gap)
            for q in EM: c.rx(q, math.pi)
    if hand == 'Y':
        for q in CL: c.rz(q, math.pi / 2)
    for q in CL: c.rx(q, math.pi / 2)
    for ch in ('' if em_seq == 'e' else em_seq):
        if ch == 'a':
            for q in EM: c.rx(q, math.pi)
        else: c.pulse_gate(EM, f12(fr, {q: amps[q] for q in EM}))
    return Circuit().add_verbatim_box(c)
def wit_items(fr, amps, fit):
    EM, CL, NB = roles(fit); it = [(['cal', s, 3], cal_circ(fr, amps, s), SH_CAL) for s in SEQS]
    for st in WIT_STARTS:
        for g in SPACINGS:
            it += [([f'W|{st}|g{g}', 'X', 3], wit_circ(fr, amps, EM, CL, st, g, 'X', 'e'), SH_ARM), ([f'W|{st}|g{g}', 'Y', 3], wit_circ(fr, amps, EM, CL, st, g, 'Y', 'ba'), SH_ARM)]
    for t in WIT_T:
        it += [([f'REF|rest|T{t}', h, 3], wit_circ(fr, amps, EM, CL, None, None, h, 'e', t_ref=t, em_hold='OFF'), SH_ARM) for h in 'XY']
    for t in WIT_T_ON:
        it += [([f'REF|held1|T{t}', h, 3], wit_circ(fr, amps, EM, CL, None, None, h, 'e', t_ref=t, em_hold='ON'), SH_ARM) for h in 'XY']
    for w in EM_RULER:
        a = {'key': f'EMRULER|w{w}', 'start': 'ON', 'gap': None, 'wait': w}
        it += [([a['key'], s, 3], build(fr, amps, a, s), SH_ARM) for s in ('e', 'ba')]
    json.dump({'emitters': EM, 'clocks': CL, 'neighbours': NB}, open(os.path.join(OUT, 'wit_roles.json'), 'w'))
    return it, EM, CL
def main():
    m = sys.argv[1]
    if m == 'tune-submit':
        dev, fr = dev_frames(); items = [(['tune', a], tune_circ(fr, a), SH_TUNE) for a in TUNE_AMPS]
        guard_and_book('rigetti time: 1<->2 swap tune (108q)', items); send(dev, items, 'tune_tasks.json')
    elif m == 'tune-collect': collect('tune_tasks.json', 'tune.npz')
    elif m == 'tune-fit': tune_fit()
    elif m in ('read-dry', 'read-submit'):
        k = int(sys.argv[2]); fit = json.load(open(os.path.join(OUT, 'tune_fit.json'))); amps = {q: (fit[str(q)]['a_pi12'] if fit[str(q)]['swing'] > 0.3 else 0.0) for q in QS}
        dev, fr = dev_frames()
        items = [(['cal', s, k], cal_circ(fr, amps, s), SH_CAL) for s in SEQS] + [([a['key'], s, k], build(fr, amps, a, s), SH_ARM) for a in arms() for s in ('e', 'ba')]
        order = np.random.default_rng(202610040 + k).permutation(len(items)); items = [items[i] for i in order]
        if m == 'read-dry':
            print(f'batch {k}: {len(items)} tasks, {sum(n for *_, n in items)} shots; {sum(1 for v in amps.values() if v > 0)} qubits get the swap'); print(str(items[0][1])[:1200]); return
        guard_and_book(f'rigetti time: batch {k} (cal + 27 arms x 2 reads, 108q)', items); send(dev, items, f'read{k}_tasks.json')
    elif m == 'read-collect': k = int(sys.argv[2]); collect(f'read{k}_tasks.json', f'read{k}.npz')
    elif m in ('wit-dry', 'wit-submit'):
        fit = json.load(open(os.path.join(OUT, 'tune_fit.json'))); amps = {q: (fit[str(q)]['a_pi12'] if fit[str(q)]['swing'] > 0.3 else 0.0) for q in QS}
        dev, fr = dev_frames(); items, EM, CL = wit_items(fr, amps, fit)
        items = [items[i] for i in np.random.default_rng(2026100403).permutation(len(items))]
        print(f'witness batch: {len(items)} tasks, {sum(n for *_, n in items)} shots; {len(EM)} emitters, {len(CL)} clocks')
        if m == 'wit-dry': return
        guard_and_book('rigetti time: batch 3, THE WITNESS (cal + 10 trains x 2 + 16 clock references + 6 emitter ruler, 108q)', items); send(dev, items, 'read3_tasks.json')
    else: print(__doc__)
if __name__ == '__main__': main()
