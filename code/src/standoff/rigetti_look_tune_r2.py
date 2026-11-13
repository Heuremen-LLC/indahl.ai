"""(6 OCT RE-TUNE for P2-R after the 18:32Z recalibration: 300 shots a task so the day stays at the 179,000-shot cap; Bones) THE LOOK ON CEPHEUS, STEP 1: TUNE (Bones, 2026-10-04; Wayfinder: "Hit like Disco, but don't let it drive. Bonefish."). The Bonefish's lines (witness = outside x 12/11, time = outside x phi) are written for
ONE LOOK timed three ways; Cepheus publishes no measure pulse, so the look is ours: a constant tone on each looked-at qubit's readout frame (its resonator, 7.2-7.4 GHz). This step finds the amplitude where the tone looks.
OBSERVER  the laid tone: 1 us at amplitude 0 / 0.03 / 0.06 / 0.12 / 0.25 / 0.5 on the seven emitters' readout frames, then 0.5 us for the resonator to empty.
TIME      the looked-at qubits themselves: held half-way (two hands: what of their coherence the tone leaves) and in |1> (what of their population it leaves).
WITNESS   every other qubit half-way through the same span, two hands (paired with the looked-at qubits' hands), by links 1 / 2 / 3+.
6 amplitudes x 3 arms = 18 tasks x 900 shots. No outcome written. BINARY CHECKPOINTS asserted: six amplitudes (three or more), three arms, clocks at 1 / 2 / 3+.
  python rigetti_look_tune.py dry | submit | collect"""
import math, os, sys
from collections import Counter
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rigetti_time as RT
import rigetti_triangle_c as C
RT.DAY_CAP_TASKS, RT.DAY_CAP_SHOTS = 10 ** 6, 10 ** 9
QS = RT.QS; EM = C.EM; CL = C.CL; SH = 300; TONE = 1.0; RING = 0.5
AMPS = [0.0, 0.03, 0.06, 0.12, 0.25, 0.5]; ARMS = ['X', 'Y', 'one']
assert len(AMPS) >= 3 and len(ARMS) >= 3 and all(Counter(min(C.D[q], 3) for q in CL if C.D[q]).get(k, 0) > 0 for k in (1, 2, 3)), 'binary checkpoint LOOK TUNE'
def ro_frames():
    from braket.aws import AwsDevice
    dev = AwsDevice(RT.DEVICE); return dev, {q: dev.frames[f'Transmon_{q}_readout_tx'] for q in EM}, {q: dev.frames[f'Transmon_{q}_charge_tx_f12'] for q in QS}
def tone(c, ro, a):
    from braket.pulse import PulseSequence, ConstantWaveform
    ps = PulseSequence()
    for q in EM: ps = ps.play(ro[q], ConstantWaveform(TONE * 1e-6, a)) if a > 0 else ps.delay(ro[q], TONE * 1e-6)
    c.pulse_gate(EM, ps)
def circ(ro, fr, a, arm):
    from braket.circuits import Circuit
    c = Circuit()
    for q in QS: c.rz(q, 0.0)
    for q in (QS if arm != 'one' else CL): c.rx(q, math.pi / 2)
    if arm == 'one':
        for q in EM: c.rx(q, math.pi)
    tone(c, ro, a); RT.wait(c, fr, RING)
    if arm == 'one':
        for q in CL: c.rx(q, math.pi / 2)
    else:
        if arm == 'Y':
            for q in QS: c.rz(q, math.pi / 2)
        for q in QS: c.rx(q, math.pi / 2)
    return Circuit().add_verbatim_box(c)
def items(ro, fr):
    it = [([arm, a], circ(ro, fr, a, arm), SH) for a in AMPS for arm in ARMS]
    return [it[i] for i in np.random.default_rng(2026100490).permutation(len(it))]
def main():
    m = sys.argv[1]
    if m in ('dry', 'submit'):
        dev, ro, fr = ro_frames(); it = items(ro, fr)
        print(f'LOOK TUNE: {len(it)} tasks, {sum(n for *_, n in it)} shots, est ${len(it) * RT.PER_TASK + sum(n for *_, n in it) * RT.PER_SHOT:.2f}; readout frames ' + ', '.join(f'q{q} {ro[q].frequency / 1e9:.4f} GHz' for q in EM))
        if m == 'dry':
            ins = [str(i) for i in [x for x in it if x[0] == ['X', 0.25]][0][1].instructions]
            print('X a=0.25:', len(ins), 'instr; pulse gates', sum('PulseGate' in x for x in ins)); return
        RT.guard_and_book('rigetti LOOK TUNE: our tone on 7 readout frames, 6 amplitudes, looked-at half-way/|1>, every clock', it); RT.send(dev, it, 'lookT2_tasks.json')
    elif m == 'collect': RT.collect('lookT2_tasks.json', 'lookT2.npz')
    else: print(__doc__)
if __name__ == '__main__':
    main()
