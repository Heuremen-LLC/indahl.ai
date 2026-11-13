"""THE PUNCH (Bones, 2026-10-07; Wayfinder: "how do we punch that crosstalk photon fucker before he opens his mouth?"). Cepheus, the dose clusters of rigetti_look_dose.py
(plus of 4 around clock 13, T of 3 around 44, pair around 56, single 88), our tone at strength 0.03, 1.0 us + 0.5 us empty per look. Crosstalk's own predictions are
hashed first: darkwave_disco/calls/CROSSTALK_PUNCH_CALL_20261007.txt.
  STATES  the looked-at qubits held in |0> / |1> / half-way while k = 1-4 looks land; clocks read on two hands. Readout photons see the three nearly alike.
  ECHO    the looked-at qubits in |1>; k = 2 / 4 looks split k/2 + pi on every clock + k/2; beside it the same laid time with NO tone split by the same pi (d = 3 / 6 us),
          and the pi alone (k = 0). A frequency shift during the looks cancels under the pi; anything that is not a frequency shift stays.
  DELAYS  0 / 1.5 / 3 / 4.5 / 6 / 9 / 12 / 15 us, no echo: each clock's own turn per us (the ruler for both).
  python rigetti_look_punch.py dry | submit | collect"""
import math, os, sys
import numpy as np
os.environ.setdefault('P2R_STRENGTH', '0.03'); os.environ.setdefault('P2R_SHOTS', '1500'); os.environ['P2R_SAVE'] = os.environ.get('PUNCH_SAVE', 'lookPunch_r1')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rigetti_look_dose as D
L = D.L; RT = L.RT; QS = L.QS; EM = L.EM; CL = L.CL; SH = L.SH; A = L.STRENGTH; T = 1.0; DETUNE = L.DETUNE
STATES = ['0', '1', 'half']; KS = [1, 2, 3, 4]; ECHO_KS = [2, 4]; DELAYS = L.DELAYS


def circ(ro, fr, ch, state, k, hand, echo=False, d=0.0, tone=True):
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
    def half(n, dd):
        for _ in range(n): L.look(c, ro, fr, ch, A if tone else 0.0, T)
        if dd: RT.wait(c, fr, dd)
    if echo:
        half(k // 2, d / 2)
        for q in CL: c.rx(q, math.pi)
        half(k // 2, d / 2)
    else:
        half(k, d)
    if hand == 'Y':
        for q in CL: c.rz(q, math.pi / 2)
    for q in CL: c.rx(q, math.pi / 2)
    return Circuit().add_verbatim_box(c)


def items(ro, fr, ch):
    it = [(['state', s, k, h], circ(ro, fr, ch, s, k, h), SH) for s in STATES for k in KS for h in 'XY']
    it += [(['echo', 'look', k, h], circ(ro, fr, ch, '1', k, h, echo=True), SH) for k in ECHO_KS for h in 'XY']
    it += [(['echo', 'laid', k, h], circ(ro, fr, ch, '1', 0, h, echo=True, d=k * (T + L.LT.RING)), SH) for k in ECHO_KS for h in 'XY']
    it += [(['echo', 'pi', 0, h], circ(ro, fr, ch, '1', 0, h, echo=True), SH) for h in 'XY']
    it += [(['delay', '1', d, h], circ(ro, fr, ch, '1', 0, h, d=d), SH) for d in DELAYS for h in 'XY']
    return [it[i] for i in np.random.default_rng(2026100712).permutation(len(it))]


def main():
    m = sys.argv[1]
    if m in ('dry', 'submit'):
        dev, ro, fr, ch = L.frames(); it = items(ro, fr, ch)
        print(f'PUNCH: {len(it)} tasks, {sum(n for *_, n in it)} shots; looked-at {EM}; strength {A}; look {T} + {L.LT.RING} us')
        if m == 'dry':
            for tag in (['echo', 'look', 4, 'Y'], ['state', 'half', 2, 'X'], ['echo', 'laid', 2, 'X']):
                ins = [str(i) for i in [x for x in it if x[0] == tag][0][1].instructions]
                print(' ', tag, len(ins), 'instr; pulse gates', sum('PulseGate' in x for x in ins), '| q12 (looked-at):', [x.split("'operator': ")[1][:14] for x in ins if 'Qubit(12)' in x and "qubit_count': 1)" in x.replace('qubit_count\': 1,', "qubit_count': 1)")][:6],
                      '| q13 (centre clock):', [x.split("'operator': ")[1][:14] for x in ins if "Qubit(13)" in x and 'Rx' in x or ("Qubit(13)" in x and 'Rz' in x)][:6])
            return
        RT.guard_and_book('rigetti PUNCH: looked-at in |0>/|1>/half, k 1-4; echoed looks k 2/4 vs echoed laid time; delays', it); RT.send(dev, it, L.SAVE + '_tasks.json')
    elif m == 'collect': RT.collect(L.SAVE + '_tasks.json', L.SAVE + '.npz')
    else: print(__doc__)


if __name__ == '__main__':
    main()
