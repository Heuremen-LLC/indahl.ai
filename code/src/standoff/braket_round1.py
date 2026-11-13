"""THE STANDOFF, the fifth door: the third state. Round 1, step 1 -- find level 2 on Rigetti Cepheus q0 (f12 Rabi).

Each circuit: rx(pi) [0->1]  ->  f12 pulse, amplitude a [1<->2]  ->  rx(pi) [1->0]  ->  measure.
Whatever the f12 pulse moved into |2> stays there through the last rx(pi) and reads as "1"; the rest returns to |0>.
So P(read 1) vs a is the Rabi oscillation of the THIRD STATE. Its first peak = the pi pulse that lands the qubit in |2>.

HARD BRAKE: every submit goes through ledger() -- it adds the cost BEFORE sending and refuses anything that would push the
cumulative total past CAP. AWS budget emails are only warnings; this is the brake.
  python braket_round1.py --dry    (cost only, nothing sent)
  python braket_round1.py --submit (sends; task ARNs saved to round1_tasks.json)
  python braket_round1.py --collect (gathers results when done -> round1_results.json)
"""
import json, math, os, sys, time
import numpy as np

CAP = 50.00; PER_TASK = 0.30; PER_SHOT = 0.000425
LEDGER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'braket_ledger.json')
DEVICE = "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q"
QUBIT = 0
AMPS = np.round(np.linspace(0.0, 0.8, 21), 4)
SHOTS = 300
WF_LEN, WF_SIGMA = 32e-9, 6.794574402304e-9     # the chip's own calibrated rx drag-gaussian shape for q0

def ledger(n_tasks, shots_each, label):
    L = json.load(open(LEDGER)) if os.path.exists(LEDGER) else {'cap': CAP, 'spent_est': 0.0, 'entries': []}
    cost = n_tasks * PER_TASK + n_tasks * shots_each * PER_SHOT
    if L['spent_est'] + cost > CAP:
        raise SystemExit(f'BRAKE: {label} would cost ${cost:.2f}; spent ${L["spent_est"]:.2f} of ${CAP:.2f}. Refused.')
    return L, cost

def build():
    from braket.circuits import Circuit
    from braket.aws import AwsDevice
    from braket.pulse import PulseSequence, DragGaussianWaveform
    dev = AwsDevice(DEVICE)
    f12 = dev.frames[f'Transmon_{QUBIT}_charge_tx_f12']
    circs = []
    for a in AMPS:
        ps = PulseSequence().play(f12, DragGaussianWaveform(WF_LEN, WF_SIGMA, 0.0, float(a), False))
        c = Circuit().rx(QUBIT, math.pi).pulse_gate([QUBIT], ps).rx(QUBIT, math.pi)
        circs.append(Circuit().add_verbatim_box(c))
    return dev, circs

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else '--dry'
    L, cost = ledger(len(AMPS), SHOTS, 'round1-step1 f12 rabi q0')
    print(f'round1 step1: {len(AMPS)} tasks x {SHOTS} shots = ${cost:.2f}  (spent so far ${L["spent_est"]:.2f} / cap ${CAP:.2f})')
    if mode == '--dry':
        dev, circs = build(); print('built', len(circs), 'circuits; first:\n', circs[1]); return
    if mode == '--submit':
        dev, circs = build()
        tasks = []
        for a, c in zip(AMPS, circs):
            t = dev.run(c, shots=SHOTS, disable_qubit_rewiring=True)
            tasks.append({'amp': float(a), 'arn': t.id})
            print('sent', a, t.id[-12:], flush=True)
        L['spent_est'] = round(L['spent_est'] + cost, 4)
        L['entries'].append({'at': time.strftime('%Y-%m-%dT%H:%M:%S'), 'label': 'round1-step1 f12 rabi q0', 'tasks': len(tasks), 'shots': SHOTS, 'cost_est': round(cost, 4)})
        json.dump(L, open(LEDGER, 'w'), indent=1)
        json.dump({'device': DEVICE, 'qubit': QUBIT, 'tasks': tasks}, open('round1_tasks.json', 'w'), indent=1)
        print(f'submitted {len(tasks)} tasks; ledger now ${L["spent_est"]:.2f} / ${CAP:.2f}')
    if mode == '--collect':
        from braket.aws import AwsQuantumTask
        T = json.load(open('round1_tasks.json')); out = []
        for t in T['tasks']:
            task = AwsQuantumTask(t['arn']); st = task.state()
            if st != 'COMPLETED': out.append({'amp': t['amp'], 'state': st}); continue
            m = task.result().measurement_counts; tot = sum(m.values())
            p1 = sum(v for k, v in m.items() if k[-1] == '1' or k[0] == '1') / tot
            out.append({'amp': t['amp'], 'state': st, 'counts': dict(m), 'p_read1': p1})
        json.dump({'device': T['device'], 'qubit': T['qubit'], 'results': out}, open('round1_results.json', 'w'), indent=1)
        done = [o for o in out if o.get('state') == 'COMPLETED']
        print(f'{len(done)}/{len(out)} complete')
        for o in done: print(f"  amp {o['amp']:.3f}  P(level 2 -> reads 1) = {o['p_read1']:.3f}")

if __name__ == '__main__':
    main()
