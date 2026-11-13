"""SPOOKY (Bones, 2026-10-07; Wayfinder: "how would you show entanglement through a state change over time? ... see if it smells like Bonefish"). Cepheus, our tone at 0.03.
Six pairs (L, P) on good CZ couplers, spread apart. L is LOOKED AT (our tone on its readout frame); P is NEVER looked at. Both start half-way (rx pi/2).
  ENT1  one CZ: the pair entangled -- each of L and P alone is a 50/50 MIX
  PROD2 two CZs (they cancel): not entangled -- each of L and P alone is a whole SUPERPOSITION
  ENT3  three CZs: entangled again, one more CZ of time than PROD2 and two more than ENT1 (the time ladder)
  looks on L: k = 0 / 1 / 2 / 4; every other qubit a clock (frame +100 kHz, half-way, two hands); delays 0-15 us every 1.5 us (the ruler).
  CHECK (no clocks): L measured in X, P in Z after the CZs: <X_L Z_P> = 1 if entangled, 0 if not.
Call hashed first: darkwave_disco/calls/SPOOKY_CALL_20261007.txt.   python rigetti_spooky.py dry | submit | collect"""
import json, math, os, sys
import numpy as np
os.environ.setdefault('P2R_STRENGTH', '0.03'); os.environ.setdefault('P2R_SHOTS', '1500'); os.environ['P2R_SAVE'] = os.environ.get('SPOOKY_SAVE', 'spooky_r1')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rigetti_triangles as T
PAIRS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'spooky_pairs.json')))
T.EM = sorted(l for l, p in PAIRS)                            # the looked-at qubits = the L's (so the tone and the readout frames go on L only)
import rigetti_triangle_c as C
import rigetti_look_lengths as L
RT = L.RT; QS = L.QS; EM = L.EM; SH = L.SH; A = L.STRENGTH; TONE = 1.0; DETUNE = L.DETUNE
PS = sorted(p for l, p in PAIRS); CL = [q for q in QS if q not in EM and q not in PS]
ARMS = {'ENT1': 1, 'PROD2': 2, 'ENT3': 3}; KS = [int(x) for x in os.environ.get('SPOOKY_KS', '0,1,2,4').split(',')]; DELAYS = [0, 1.5, 3, 4.5, 6, 7.5, 9, 10.5, 12, 13.5, 15]


def frames():
    from braket.aws import AwsDevice
    dev = AwsDevice(RT.DEVICE)
    return dev, {q: dev.frames[f'Transmon_{q}_readout_tx'] for q in EM}, {q: dev.frames[f'Transmon_{q}_charge_tx_f12'] for q in QS}, {q: dev.frames[f'Transmon_{q}_charge_tx'] for q in CL}


def look(c, ro, fr, ch):
    from braket.pulse import PulseSequence, ConstantWaveform
    allf = list(ro.values()) + list(fr.values()) + list(ch.values()); ps = PulseSequence().barrier(allf)
    for q in EM: ps = ps.play(ro[q], ConstantWaveform(TONE * 1e-6, A))
    ps = ps.delay(list(fr.values()) + list(ch.values()), TONE * 1e-6).barrier(allf)
    c.pulse_gate(QS, ps); RT.wait(c, fr, L.LT.RING)


def circ(ro, fr, ch, arm, k, hand, d=0.0, check=False):
    from braket.circuits import Circuit
    from braket.pulse import PulseSequence
    c = Circuit()
    for q in QS: c.rz(q, 0.0)
    if not check:
        ps = PulseSequence()
        for q in CL: ps = ps.shift_frequency(ch[q], DETUNE)
        c.pulse_gate(CL, ps)
    for l, p in PAIRS: c.rx(l, math.pi / 2); c.rx(p, math.pi / 2)
    for _ in range(ARMS[arm]):
        for l, p in PAIRS: c.cz(l, p)
    if check:
        for l, p in PAIRS: c.rx(l, math.pi / 2)                   # L into X (after rx pi/2 prep, a second rx pi/2 maps the X-ish axis onto Z); P read in its own basis after rx pi/2
        return Circuit().add_verbatim_box(c)
    for q in CL: c.rx(q, math.pi / 2)
    for _ in range(k): look(c, ro, fr, ch)
    if d: RT.wait(c, fr, d)
    if hand == 'Y':
        for q in CL: c.rz(q, math.pi / 2)
    for q in CL: c.rx(q, math.pi / 2)
    return Circuit().add_verbatim_box(c)


def items(ro, fr, ch):
    it = [(['arm', a, k, h], circ(ro, fr, ch, a, k, h), SH) for a in ARMS for k in KS for h in 'XY']
    it += [(['delay', d, h], circ(ro, fr, ch, 'PROD2', 0, h, d), SH) for d in DELAYS for h in 'XY']
    it += [(['check', a], circ(ro, fr, ch, a, 0, None, check=True), SH) for a in ARMS]
    return [it[i] for i in np.random.default_rng(2026100714).permutation(len(it))]


def main():
    m = sys.argv[1]
    if m in ('dry', 'submit'):
        dev, ro, fr, ch = frames(); it = items(ro, fr, ch)
        print(f'SPOOKY: {len(it)} tasks; pairs {PAIRS}; clocks {len(CL)}')
        if m == 'dry':
            ins = [str(i) for i in [x for x in it if x[0] == ['arm', 'ENT3', 2, 'Y']][0][1].instructions]
            l, p = PAIRS[0]
            print('  ENT3/k2/Y:', len(ins), 'instr; CZ', sum('CZ' in x for x in ins), '; L', l, [x.split("'operator': ")[1][:12] for x in ins if f'Qubit({l})' in x and 'PulseGate' not in x][:6],
                  '; P', p, [x.split("'operator': ")[1][:12] for x in ins if f'Qubit({p})' in x and 'PulseGate' not in x][:6])
            return
        RT.guard_and_book('rigetti SPOOKY: entangled vs product pairs, L looked at, P never; clocks', it); RT.send(dev, it, L.SAVE + '_tasks.json')
    elif m == 'collect': RT.collect(L.SAVE + '_tasks.json', L.SAVE + '.npz')
    else: print(__doc__)


if __name__ == '__main__':
    main()
