"""THE WHOLE-CHIP GAMBLE -- 2026-09-28 night, Wayfinder paid: "we're looking for the fuck ups." Every Cepheus qubit in parallel.
No outcome written.  stage 1 TUNE: rx(pi) -> f12 push of amplitude a -> rx(pi) -> read, 8 amplitudes: each qubit's own rung-2 push.
stage 2 SHUFFLE: the at-rest state shuffled across rungs 0/1/2 (a = flip 0<->1, b = swap 1<->2), 8 sequences -> per-qubit rung 2
at the start (same fit as rigetti_gamble.py). stage 3 BLINK/DRAIN: 'ba' now, 'ba' after 60 us, plain, in 3 batches minutes apart.
  python rigetti_chip.py tune-dry|tune-submit|tune-collect|tune-fit|run-dry|run-submit|run-collect|analyze"""
import json, math, os, sys, time
import numpy as np
os.environ.setdefault('AWS_PROFILE', 'braket'); os.environ.setdefault('AWS_DEFAULT_REGION', 'us-west-1')
HERE = os.path.dirname(os.path.abspath(__file__)); LEDGER = os.path.join(HERE, 'braket_ledger.json')
DEVICE = "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q"; PER_TASK, PER_SHOT = 0.30, 0.000425
WF_LEN, WF_SIGMA = 32e-9, 6.794574402304e-9
AMPS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.75]; FINE = [0.04, 0.08, 0.12, 0.16, 0.24, 0.28, 0.32, 0.36]; SH_TUNE = 1000
SEQS = ['e', 'a', 'b', 'ab', 'ba', 'aba', 'bb', 'bab']; SH_SHUF = 5000; SH_BLINK = 2000; N_BATCH = 3
OUT = os.path.join(HERE, 'chip'); os.makedirs(OUT, exist_ok=True)
QS = sorted(int(r[0]) for r in json.load(open(os.path.join(HERE, 'cepheus_props_20260928.json'))))
def _ns(us): return float(f'{int(round(us * 1000 / 4)) * 4}e-9')
def dev_frames():
    from braket.aws import AwsDevice
    dev = AwsDevice(DEVICE); return dev, {q: dev.frames[f'Transmon_{q}_charge_tx_f12'] for q in QS}
def push(fr, amps):
    from braket.pulse import PulseSequence, DragGaussianWaveform
    ps = PulseSequence()
    for q in QS:
        if amps[q] > 0: ps = ps.play(fr[q], DragGaussianWaveform(WF_LEN, WF_SIGMA, 0.0, float(amps[q]), False))
    return ps
def circ(fr, seq, amps, wait_us=0, tune_amp=None):
    from braket.circuits import Circuit; from braket.pulse import PulseSequence
    c = Circuit()
    for q in QS: c.rz(q, 0.0)
    if tune_amp is not None:
        for q in QS: c.rx(q, math.pi)
        if tune_amp > 0: c.pulse_gate(QS, push(fr, {q: tune_amp for q in QS}))
        for q in QS: c.rx(q, math.pi)
        return Circuit().add_verbatim_box(c)
    if wait_us:
        ps = PulseSequence()
        for q in QS: ps = ps.delay(fr[q], _ns(wait_us))
        c.pulse_gate(QS, ps)
    for ch in ('' if seq == 'e' else seq):
        if ch == 'a':
            for q in QS: c.rx(q, math.pi)
        else: c.pulse_gate(QS, push(fr, amps))
    return Circuit().add_verbatim_box(c)
def spend(label, c):
    L = json.load(open(LEDGER)); L['cap'] = round(L['spent_est'] + c + 0.01, 4)     # Wayfinder approved, 9/28 night
    L['spent_est'] = round(L['spent_est'] + c, 4); L['entries'].append({'at': time.strftime('%Y-%m-%dT%H:%M:%S'), 'label': label, 'tasks': None, 'cost_est': round(c, 4)})
    json.dump(L, open(LEDGER, 'w'), indent=1); return L['spent_est']
def run_tasks(items, fname):
    dev, fr = dev_frames(); T = {'tasks': []}
    for tag, cc, n in items:
        t = dev.run(cc, shots=n, disable_qubit_rewiring=True); T['tasks'].append({'tag': tag, 'arn': t.id, 'sent': time.time()}); print('sent', tag, flush=True)
        json.dump(T, open(os.path.join(OUT, fname), 'w'), indent=1)
def collect(fname, npzname):
    from braket.aws import AwsQuantumTask
    T = json.load(open(os.path.join(OUT, fname))); arrs = {}; states = {}
    for t in T['tasks']:
        task = AwsQuantumTask(t['arn']); st = task.state(); states[json.dumps(t['tag'])] = st
        if st == 'COMPLETED':
            r = task.result(); mq = list(r.measured_qubits); m = np.asarray(r.measurements)
            arrs[json.dumps(t['tag'])] = m[:, [mq.index(q) for q in QS]]
    np.savez_compressed(os.path.join(OUT, npzname), **arrs); print({s: list(states.values()).count(s) for s in set(states.values())})
def main():
    mode = sys.argv[1]
    if mode.startswith('tune') or mode.startswith('fine'):
        if mode in ('tune-dry', 'tune-submit'):
            dev, fr = dev_frames(); items = [(('tune', a), circ(fr, None, None, tune_amp=a), SH_TUNE) for a in AMPS]
            c = sum(PER_TASK + n * PER_SHOT for *_, n in items); print(f'TUNE: {len(items)} tasks on {len(QS)} qubits, ${c:.2f}')
            if mode == 'tune-dry': print(str(items[3][1])[:1500]); return
            print('ledger', spend('whole-chip f12 tune (108q)', c)); run_tasks(items, 'tune_tasks.json'); return
        if mode == 'tune-collect': collect('tune_tasks.json', 'tune.npz'); return
        if mode == 'fine-submit':
            dev, fr = dev_frames(); items = [(('tune', a), circ(fr, None, None, tune_amp=a), SH_TUNE) for a in FINE]
            c = sum(PER_TASK + n * PER_SHOT for *_, n in items); print('ledger', spend('whole-chip f12 fine tune (108q)', c)); run_tasks(items, 'fine_tasks.json'); return
        if mode == 'fine-collect': collect('fine_tasks.json', 'fine.npz'); return
        if mode == 'tune-fit':
            Z = dict(np.load(os.path.join(OUT, 'tune.npz')))
            if os.path.exists(os.path.join(OUT, 'fine.npz')): Z.update(dict(np.load(os.path.join(OUT, 'fine.npz'))))
            ALL = sorted({a for a in AMPS + FINE if json.dumps(['tune', a]) in Z})
            y = np.array([1 - Z[json.dumps(['tune', a])].mean(0) for a in ALL])   # P(read 0), per qubit
            fit = {}
            for k, q in enumerate(QS):
                yy = y[:, k]; best = None
                for api in np.linspace(0.05, 0.9, 171):
                    X = np.stack([np.ones(len(ALL)), np.cos(np.pi * np.array(ALL) / api)], 1); b, res, *_ = np.linalg.lstsq(X, yy, rcond=None)
                    r = float(np.sum((X @ b - yy) ** 2))
                    if best is None or r < best[0]: best = (r, api, b[1])
                fit[q] = {'a_pi12': best[1], 'swing': float(abs(best[2]) * 2), 'rms': math.sqrt(best[0] / len(ALL))}
            json.dump(fit, open(os.path.join(OUT, 'tune_fit.json'), 'w'), indent=1)
            sw = sorted(fit.items(), key=lambda kv: kv[1]['swing'])
            print('median a_pi12', round(float(np.median([v['a_pi12'] for v in fit.values()])), 3), '| q0', fit.get(0), '\nweakest swings (rung 2 hard to reach):', [(q, round(v['swing'], 2)) for q, v in sw[:8]]); return
    if mode in ('run-dry', 'run-submit'):
        fit = json.load(open(os.path.join(OUT, 'tune_fit.json'))); amps = {q: (fit[str(q)]['a_pi12'] if fit[str(q)]['swing'] > 0.3 else 0.0) for q in QS}
        dev, fr = dev_frames(); items = [(('shuffle', s), circ(fr, s, amps), SH_SHUF) for s in SEQS]
        for bt in range(1, N_BATCH + 1):
            items += [(('blink', 'ba', 0, bt), circ(fr, 'ba', amps), SH_BLINK), (('blink', 'ba', 60, bt), circ(fr, 'ba', amps, wait_us=60), SH_BLINK), (('blink', 'e', 0, bt), circ(fr, 'e', amps), SH_BLINK)]
        c = sum(PER_TASK + n * PER_SHOT for *_, n in items); print(f'RUN: {len(items)} tasks, ${c:.2f}; {sum(1 for v in amps.values() if v > 0)} qubits get a rung-2 push')
        if mode == 'run-dry': return
        print('ledger', spend('whole-chip shuffle + blink/drain (108q)', c))
        first = [it for it in items if it[0][0] == 'shuffle' or it[0][-1] == 1]; run_tasks(first, 'run_tasks.json')
        for bt in range(2, N_BATCH + 1):
            time.sleep(300); T = json.load(open(os.path.join(OUT, 'run_tasks.json')))
            for tag, cc, n in [it for it in items if it[0][0] == 'blink' and it[0][-1] == bt]:
                t = dev.run(cc, shots=n, disable_qubit_rewiring=True); T['tasks'].append({'tag': tag, 'arn': t.id, 'sent': time.time()}); print('sent', tag, flush=True)
            json.dump(T, open(os.path.join(OUT, 'run_tasks.json'), 'w'), indent=1)
        print('ALL SENT'); return
    if mode == 'run-collect': collect('run_tasks.json', 'run.npz'); return
if __name__ == '__main__': main()

def analyze():
    from scipy.stats import spearmanr
    import rigetti_gamble as G
    Z = dict(np.load(os.path.join(OUT, 'run.npz'))); props = {int(r[0]): r for r in json.load(open(os.path.join(HERE, 'cepheus_props_20260928.json')))}
    tune = json.load(open(os.path.join(OUT, 'tune_fit.json'))); rows = []
    for k, q in enumerate(QS):
        y = {s: 1 - Z[json.dumps(['shuffle', s])][:, k].mean() for s in SEQS}; n = {s: Z[json.dumps(['shuffle', s])].shape[0] for s in SEQS}
        pushed = tune[str(q)]['swing'] > 0.3
        if pushed:
            x, e, cst = G.fit(y, n); p1, p2, ep1, ep2, eta = x[0], x[1], e[0], e[1], x[5]
        else: p1 = p2 = ep1 = ep2 = eta = cst = np.nan
        ba0 = [1 - Z[json.dumps(['blink', 'ba', 0, b])][:, k].mean() for b in range(1, N_BATCH + 1) if json.dumps(['blink', 'ba', 0, b]) in Z]
        ba6 = [1 - Z[json.dumps(['blink', 'ba', 60, b])][:, k].mean() for b in range(1, N_BATCH + 1) if json.dumps(['blink', 'ba', 60, b]) in Z]
        pl = [Z[json.dumps(['blink', 'e', 0, b])][:, k].mean() for b in range(1, N_BATCH + 1) if json.dumps(['blink', 'e', 0, b]) in Z]
        drain = np.mean(ba0) - np.mean(ba6) if ba0 and ba6 else np.nan
        sd_exp = math.sqrt(max(np.mean(ba0) * (1 - np.mean(ba0)), 1e-6) / SH_BLINK) if ba0 else np.nan
        blink = (np.std(ba0, ddof=1) / sd_exp) if len(ba0) > 1 else np.nan
        pr = props.get(q, [q, None, None, None, None])
        rows.append(dict(q=q, p1=p1, p2=p2, ep2=ep2, eta=eta, fitq=cst, drain=drain, blink=blink, rest1=1 - y['e'], plain_batches=pl,
                         readout=pr[3], T1=pr[1], T2=pr[2], pushed=bool(pushed)))
    json.dump(rows, open(os.path.join(OUT, 'chip_rows.json'), 'w'), indent=1, default=float)
    good = [r for r in rows if r['pushed'] and r['ep2'] == r['ep2'] and r['ep2'] < 0.01]
    print(f"{len(rows)} qubits; {len(good)} with a clean rung-2 number (+/- under 1%)")
    top = sorted(good, key=lambda r: -r['p2'] / max(r['ep2'], 1e-4))[:10]
    print('MOST ON RUNG 2 AT THE START:'); [print(f"   q{r['q']:<4} rung2 {r['p2']:.2%} +/- {r['ep2']:.2%} | rung1 {r['p1']:.2%} | readout {r['readout'] or float('nan'):.3f} T1 {1e6 * (r['T1'] or float('nan')):.1f} us | drain {r['drain']:+.4f} blink {r['blink']:.1f}") for r in top]
    z = np.array([r['p2'] / max(r['ep2'], 1e-4) for r in good]); print(f"rung-2 signal across clean qubits: {np.sum(z > 3)} above 3 noise units (chance ~{0.0013 * len(good):.1f}), mean {np.mean([r['p2'] for r in good]):.2%}")
    for key, lab in (('readout', 'readout fidelity'), ('T1', 'lifetime T1'), ('T2', 'memory T2')):
        ok = [r for r in good if r[key]]; rho, pv = spearmanr([r[key] for r in ok], [r['p2'] for r in ok]); print(f"   rung 2 at start vs {lab:18s} rho {rho:+.2f} (p {pv:.2g}, n {len(ok)})")
    dr = [r for r in rows if r['drain'] == r['drain']]; print(f"DRAIN (rung-2 read now minus after 60 us), chip mean {np.mean([r['drain'] for r in dr]):+.4f}; biggest:", [(r['q'], round(r['drain'], 3)) for r in sorted(dr, key=lambda r: -r['drain'])[:6]])
    bl = [r for r in rows if r['blink'] == r['blink']]; print('BLINK (batch-to-batch spread in noise units; ~1 = steady):', [(r['q'], round(r['blink'], 1)) for r in sorted(bl, key=lambda r: -r['blink'])[:6]])
    bad = sorted(rows, key=lambda r: (r['readout'] or 1))[:6]; print('THE FUCK-UPS (worst readout):', [(r['q'], round(r['readout'] or 0, 3), 'rung2', None if r['p2'] != r['p2'] else round(r['p2'], 4), 'rest reads 1', round(r['rest1'], 3)) for r in bad])
if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'analyze': analyze()
