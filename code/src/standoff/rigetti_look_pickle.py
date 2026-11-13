"""THE PICKLE (Bones, 2026-10-07; Wayfinder: "chase that state dependent shit ... it's superposition, it's what the witness or observer see"). Cepheus, the dose clusters,
our tone at 0.03, 1.0 + 0.5 us per look, ONE WHOLE BATCH (no reorders, every delay). Three seats on the state dependence:
  STATES   the looked-at qubits in |0> / |1> / half-way (superposition)
  OFFSETS  the tone moved -1.5 / 0 / +1.5 MHz off the readout frame's own frequency (light's state ordering moves with it; a resonator pulled by its qubit's state),
           and NO TONE (the same laid looks dark: what the looked-at state does to its neighbours with no light)
  LOOKS    k = 1 / 2 / 4, clocks on two hands; delays 0-15 us every 1.5 us for the ruler.
Call hashed first: darkwave_disco/calls/PICKLE_CALL_20261007.txt.   python rigetti_look_pickle.py dry | submit | collect"""
import math, os, sys
import numpy as np
os.environ.setdefault('P2R_STRENGTH', '0.03'); os.environ.setdefault('P2R_SHOTS', '1500'); os.environ['P2R_SAVE'] = os.environ.get('PICKLE_SAVE', 'lookPickle_r2')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rigetti_look_dose as D
L = D.L; RT = L.RT; QS = L.QS; EM = L.EM; CL = L.CL; SH = L.SH; A = L.STRENGTH; T = 1.0; DETUNE = L.DETUNE
STATES = ['0', '1', 'half']; OFFS = [-1.5e6, 0.0, 1.5e6, None]; KS = [1, 2, 4]; DELAYS = [0, 1.5, 3, 4.5, 6, 7.5, 9, 10.5, 12, 13.5, 15]     # OFFS None = the same looks with NO tone (always-on coupling by state, no light)


def look(c, ro, fr, ch, off):
    if off is None:
        from braket.pulse import PulseSequence
        allf = list(ro.values()) + list(fr.values()) + list(ch.values()); ps = PulseSequence().barrier(allf).delay(allf, T * 1e-6).barrier(allf)
        c.pulse_gate(QS, ps); RT.wait(c, fr, L.LT.RING); return
    from braket.pulse import PulseSequence, ConstantWaveform
    allf = list(ro.values()) + list(fr.values()) + list(ch.values()); ps = PulseSequence().barrier(allf)
    for q in EM:
        if off: ps = ps.shift_frequency(ro[q], off)
        ps = ps.play(ro[q], ConstantWaveform(T * 1e-6, A))
        if off: ps = ps.shift_frequency(ro[q], -off)
    ps = ps.delay(list(fr.values()) + list(ch.values()), T * 1e-6).barrier(allf)
    c.pulse_gate(QS, ps); RT.wait(c, fr, L.LT.RING)


def circ(ro, fr, ch, state, off, k, hand, d=0.0):
    from braket.circuits import Circuit
    from braket.pulse import PulseSequence
    c = Circuit()
    for q in QS: c.rz(q, 0.0)
    ps = PulseSequence()
    for q in CL: ps = ps.shift_frequency(ch[q], DETUNE)
    c.pulse_gate(CL, ps)
    for q in EM:
        if state == '1': c.rx(q, math.pi)
        elif state == 'half': c.rx(q, math.pi / 2)
    for q in CL: c.rx(q, math.pi / 2)
    for _ in range(k): look(c, ro, fr, ch, off)
    if d: RT.wait(c, fr, d)
    if hand == 'Y':
        for q in CL: c.rz(q, math.pi / 2)
    for q in CL: c.rx(q, math.pi / 2)
    return Circuit().add_verbatim_box(c)


def items(ro, fr, ch):
    it = [(['state', s, off, k, h], circ(ro, fr, ch, s, off, k, h), SH) for s in STATES for off in OFFS for k in KS for h in 'XY']
    it += [(['delay', d, h], circ(ro, fr, ch, '1', 0.0, 0, h, d), SH) for d in DELAYS for h in 'XY']
    return [it[i] for i in np.random.default_rng(2026100713).permutation(len(it))]


def main():
    m = sys.argv[1]
    if m in ('dry', 'submit'):
        dev, ro, fr, ch = L.frames(); it = items(ro, fr, ch)
        print(f'PICKLE: {len(it)} tasks, {sum(n for *_, n in it)} shots; looked-at {EM}; offsets {OFFS}')
        if m == 'dry':
            ins = [str(i) for i in [x for x in it if x[0] == ['state', 'half', 1.5e6, 2, 'Y']][0][1].instructions]
            print('  half/+1.5MHz/k2/Y:', len(ins), 'instr; pulse gates', sum('PulseGate' in x for x in ins), '; q12 ops', [x.split("'operator': ")[1][:14] for x in ins if 'Qubit(12)' in x and 'PulseGate' not in x])
            return
        RT.guard_and_book('rigetti PICKLE: looked-at |0>/|1>/half x tone offset -1.5/0/+1.5 MHz x k 1/2/4; delays', it); RT.send(dev, it, L.SAVE + '_tasks.json')
    elif m == 'collect': RT.collect(L.SAVE + '_tasks.json', L.SAVE + '.npz')
    else: print(__doc__)


if __name__ == '__main__':
    main()
