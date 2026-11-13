"""P2-R, THE WITNESS ON OUR OWN LOOK AT FOUR LENGTHS (Bones, 2026-10-06; Wayfinder: "go for amazon"; calls/P2_OBSERVER_CALL_20261006.txt). Copy of the 4 Oct look triangle with the TONE LENGTH swept: our tone 0.5 / 1 / 1.5 / 2 us + 0.5 us empty = 1.0 / 1.5 / 2.0 / 2.5 us per look, one strength (0.045), k = 1-6; delays to 15 us; the no-tone look at 1.5 us kept as the scheduler check. An honest clock reads W = laid at every length; a fixed offset reads W - laid constant. Was: THE LOOK ON CEPHEUS, STEP 2: THE TRIANGLE (Bones, 2026-10-04). ONE's standing call, written in Seven before this run: the same look timed from three positions on a second chip reads witness / outside 1.09,
time / outside 1.62, time / witness 1.48 (12/11, phi, phi x 11/12). No new number written here.
OBSERVER  our look, laid: a 1-us tone on the seven looked-at qubits' readout frames then 0.5 us to empty = 1.5 us per look; strengths 0.03 / 0.045 / 0.06 (the look window, §225); k = 1 / 2 / 3 / 4 / 6 looks back to back.
          Beside it, delays of the same laid lengths with no tone: 0 / 1.5 / 3 / 4.5 / 6 / 9 us.
WITNESS   every other qubit a clock, half-way, its frame moved +100 kHz so it turns ~36 deg/us in the chip's own time; two hands. Time per look as a clock reads it = (turn per look) / (turn per us over the delays).
TIME      the looked-at qubits, prepared in |1>, read plainly in the same shots: their fall per look turned into time on their own fall over the delays.
3 strengths x 5 counts x 2 hands + 6 delays x 2 hands = 42 tasks x 1500 shots. BINARY CHECKPOINTS asserted: three strengths, five counts, six delays, clocks at 1 / 2 / 3+.
  python rigetti_look_triangle.py dry | submit | collect"""
import math, os, sys
from collections import Counter
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rigetti_time as RT
import rigetti_triangle_c as C
import rigetti_look_tune as LT
RT.DAY_CAP_TASKS, RT.DAY_CAP_SHOTS = 10 ** 6, 10 ** 9
SAVE = os.environ.get('P2R_SAVE', 'lookLengths_r1')
QS = RT.QS; EM = C.EM; CL = C.CL; SH = int(os.environ.get('P2R_SHOTS', '1400')); LOOK = LT.TONE + LT.RING; DETUNE = 100e3
TONES = [0.5, 1.0, 1.5, 2.0]; STRENGTH = float(os.environ.get('P2R_STRENGTH', '0.045')); STRENGTHS = [0.0, 0.03, 0.045, 0.06]; KS = [int(x) for x in os.environ.get('P2R_KS', '1,2,3,4,6').split(',')]; CHECK_KS = [1, 2, 4]; DELAYS = [0, 1.5, 3, 4.5, 6, 9, 12, 15]   # strength 0.0 = the look's laid time, no tone: the clocks must read 1.5 us per look there (the scheduler check)
assert len(TONES) >= 4 and len(KS) >= 4 and len(DELAYS) >= 6 and all(Counter(min(C.D[q], 3) for q in CL if C.D[q]).get(k, 0) > 0 for k in (1, 2, 3)), 'binary checkpoint LOOK TRIANGLE'
def frames():
    from braket.aws import AwsDevice
    dev = AwsDevice(RT.DEVICE)
    return dev, {q: dev.frames[f'Transmon_{q}_readout_tx'] for q in EM}, {q: dev.frames[f'Transmon_{q}_charge_tx_f12'] for q in QS}, {q: dev.frames[f'Transmon_{q}_charge_tx'] for q in CL}
def look(c, ro, fr, ch, a, tone=None):
    """2026-10-04 FIX (run 1: the clocks never waited for the tone): one pulse gate on EVERY qubit -- a barrier on all frames, the tone on the looked-at
    qubits' readout frames, the same length of delay on every other frame -- then the 0.5-us empty wait. Every clock now sits through the whole look."""
    from braket.pulse import PulseSequence, ConstantWaveform
    allf = list(ro.values()) + list(fr.values()) + list(ch.values()); ps = PulseSequence().barrier(allf)
    T = LT.TONE if tone is None else tone
    for q in EM: ps = ps.play(ro[q], ConstantWaveform(T * 1e-6, a)) if a > 0 else ps.delay(ro[q], T * 1e-6)
    ps = ps.delay(list(fr.values()) + list(ch.values()), T * 1e-6).barrier(allf)
    c.pulse_gate(QS, ps); RT.wait(c, fr, LT.RING)
def circ(ro, fr, ch, a, k, d, hand, tone=None):
    from braket.circuits import Circuit
    from braket.pulse import PulseSequence
    c = Circuit()
    for q in QS: c.rz(q, 0.0)
    ps = PulseSequence()
    for q in CL: ps = ps.shift_frequency(ch[q], DETUNE)
    c.pulse_gate(CL, ps)
    for q in EM: c.rx(q, math.pi)
    for q in CL: c.rx(q, math.pi / 2)
    if k:
        for _ in range(k):
            look(c, ro, fr, ch, a, tone)
    else: RT.wait(c, fr, d)
    if hand == 'Y':
        for q in CL: c.rz(q, math.pi / 2)
    for q in CL: c.rx(q, math.pi / 2)
    return Circuit().add_verbatim_box(c)
def items(ro, fr, ch):
    it = [(['look', STRENGTH, T, k, h], circ(ro, fr, ch, STRENGTH, k, 0, h, T), SH) for T in TONES for k in KS for h in 'XY']
    it += [(['check', 0.0, 1.0, k, h], circ(ro, fr, ch, 0.0, k, 0, h, 1.0), SH) for k in CHECK_KS for h in 'XY']
    it += [(['delay', 0, 0, d, h], circ(ro, fr, ch, 0, 0, d, h), SH) for d in DELAYS for h in 'XY']
    return [it[i] for i in np.random.default_rng(2026100611).permutation(len(it))]
def main():
    m = sys.argv[1]
    if m in ('dry', 'submit'):
        dev, ro, fr, ch = frames(); it = items(ro, fr, ch)
        print(f'P2-R LOOK LENGTHS: {len(it)} tasks, {sum(n for *_, n in it)} shots, est ${len(it) * RT.PER_TASK + sum(n for *_, n in it) * RT.PER_SHOT:.2f}; looks laid {[t + LT.RING for t in TONES]} us; clock frames +{DETUNE / 1e3:.0f} kHz')
        if m == 'dry':
            for tag in (['look', STRENGTH, 2.0, 3, 'Y'], ['delay', 0, 0, 4.5, 'X']):
                ins = [str(i) for i in [x for x in it if x[0] == tag][0][1].instructions]
                print(' ', tag, len(ins), 'instr; pulse gates', sum('PulseGate' in x for x in ins), '| q7 (looked-at):', [x.split("'operator': ")[1][:16] for x in ins if 'Qubit(7)' in x and "qubit_count': 107" not in x],
                      '| q9 (clock):', [x.split("'operator': ")[1][:16] for x in ins if 'Qubit(9)' in x and "qubit_count': 107" not in x and "qubit_count': 100" not in x])
            return
        RT.guard_and_book('rigetti P2-R LOOK LENGTHS: our look at 1.0/1.5/2.0/2.5 us x 1-6 looks vs delays to 15 us, clocks +100 kHz', it); RT.send(dev, it, SAVE + '_tasks.json')
    elif m == 'collect': RT.collect(SAVE + '_tasks.json', SAVE + '.npz')
    else: print(__doc__)
if __name__ == '__main__':
    main()
