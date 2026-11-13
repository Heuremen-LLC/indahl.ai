"""THE STANDOFF -- five doors, one room. Bones for Wayfinder, 2026-09-25.

Wayfinder's four solutions to the three-body Mexican standoff, plus his side question, as qubit experiments:
  Door 0  THE STANDOFF (side question: "what if there is no outcome?") -- GHZ / Mermin test. A classical answer sheet scores <= 2;
          quantum mechanics says 4. Also counts the FORBIDDEN outcomes (the "no outcome" floor).
  Door 1  BLONDIE (rig it, keep it looking like a standoff) -- the three-box paradox: pre-select, open a box, post-select.
          Three boxes live in two qubits: a third state faked with two. Discard rate reported (the honest price of rigging).
  Door 2  RECRUIT (match the frequency, then take one body with you) -- measure one body IN TUNE (X) and the other two lock
          into an entangled pair; control: measure it BY FORCE (Z) and they fall apart into two separate bodies.
  Door 3  PINATA (change the frequency entirely) -- a phase sweep: the standoff swings 3x as fast as one lone qubit (control).
  Door 4  THREE MORE BODIES -- a 6-qubit standoff; certificate: fidelity > 0.5 means genuinely 6-way entangled, not faking.

Run: ~/bones-forge/qvenv/bin/python standoff.py            (simulator: ideal + FakeFez noise model)
Every number printed is written to standoff_results.json with the circuit counts behind it. Receipts, not vibes.
"""
import json, math, sys, time
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import StatePreparation
from qiskit_aer import AerSimulator

SHOTS = 8192
OUT = {'made': time.strftime('%Y-%m-%dT%H:%M:%S'), 'shots': SHOTS, 'doors': {}}

def backends():
    ideal = AerSimulator()
    try:
        from qiskit_ibm_runtime.fake_provider import FakeFez
        fb = FakeFez(); noisy = AerSimulator.from_backend(fb)
        return [('ideal', ideal, None), ('fez-noise', noisy, fb)]
    except Exception as e:
        print('noise model unavailable:', e); return [('ideal', ideal, None)]

def run(qcs, sim, fb):
    # ideal: plain gates first -- Aer segfaults (exit 139) on raw StatePreparation blocks
    tq = transpile(qcs, backend=fb, optimization_level=1, seed_transpiler=7) if fb is not None else transpile(qcs, basis_gates=['cx', 'u', 'x', 'h', 'sdg', 'rz', 'measure'], optimization_level=1)
    res = sim.run(tq, shots=SHOTS, seed_simulator=11).result()
    return [res.get_counts(i) for i in range(len(qcs))]

def bits(key, n):  # qiskit keys are big-endian over clbits: rightmost char = clbit 0
    k = key.replace(' ', ''); return [int(k[-1 - i]) for i in range(n)]

def parity_exp(counts, idxs):
    tot = sum(counts.values()); s = 0
    for k, v in counts.items():
        b = bits(k, max(idxs) + 1); s += v * (-1) ** (sum(b[i] for i in idxs) % 2)
    return s / tot

def ghz(n, measure=True):
    qc = QuantumCircuit(n, n); qc.h(0)
    for i in range(n - 1): qc.cx(i, i + 1)
    return qc

def basis(qc, q, b):
    if b == 'X': qc.h(q)
    elif b == 'Y': qc.sdg(q); qc.h(q)

# ---------------- Door 0: THE STANDOFF (Mermin) ----------------
def door0():
    settings = ['XXX', 'XYY', 'YXY', 'YYX']
    qcs = []
    for s in settings:
        qc = ghz(3)
        for q, b in enumerate(s): basis(qc, q, b)
        qc.measure(range(3), range(3)); qcs.append(qc)
    z = ghz(3); z.measure(range(3), range(3)); qcs.append(z)
    return qcs, settings

def score0(counts, settings):
    E = {s: parity_exp(c, [0, 1, 2]) for s, c in zip(settings, counts[:4])}
    M = E['XXX'] - E['XYY'] - E['YXY'] - E['YYX']
    # forbidden ("no outcome"): odd parity in XXX, even parity in the three XYY-type; plus Z-basis anything but 000/111
    forb = 0; tot = 0
    for s, c in zip(settings, counts[:4]):
        want_even = (s == 'XXX')
        for k, v in c.items():
            even = sum(bits(k, 3)) % 2 == 0; tot += v
            if even != want_even: forb += v
    zc = counts[4]; zforb = sum(v for k, v in zc.items() if k.replace(' ', '') not in ('000', '111'))
    return {'E': E, 'M': M, 'classical_max': 2, 'quantum_ideal': 4, 'forbidden_fraction': forb / tot,
            'z_forbidden_fraction': zforb / sum(zc.values())}

# ---------------- Door 1: BLONDIE (three-box) ----------------
PSI = np.array([1, 1, 1, 0]) / math.sqrt(3)     # boxes A=|00> B=|01> C=|10> (index = q1q0), |11> unused
PHI = np.array([1, 1, -1, 0]) / math.sqrt(3)
BOX = {'A': (0, 0), 'B': (1, 0), 'C': (0, 1)}  # (q0, q1) values
def door1():
    qcs = []
    for box in ['A', 'B', 'C']:
        qc = QuantumCircuit(3, 3)
        qc.append(StatePreparation(PSI), [0, 1])
        b0, b1 = BOX[box]
        if not b0: qc.x(0)
        if not b1: qc.x(1)
        qc.ccx(0, 1, 2)                      # ancilla flips iff the ball is in this box (a strong, honest look)
        if not b0: qc.x(0)
        if not b1: qc.x(1)
        qc.append(StatePreparation(PHI).inverse(), [0, 1])   # post-selection basis: keep only |00>
        qc.measure([0, 1, 2], [0, 1, 2]); qcs.append(qc)
    return qcs

def score1(counts):
    out = {}
    for box, c in zip(['A', 'B', 'C'], counts):
        kept = {k: v for k, v in c.items() if bits(k, 3)[0] == 0 and bits(k, 3)[1] == 0}
        nk = sum(kept.values()); found = sum(v for k, v in kept.items() if bits(k, 3)[2] == 1)
        out[box] = {'kept_fraction': nk / sum(c.values()), 'found_in_box_given_kept': (found / nk) if nk else None}
    out['ideal'] = {'A': 1.0, 'B': 1.0, 'C': 0.2}
    return out

# ---------------- Door 2: RECRUIT ----------------
def door2():
    qcs = {}
    for how in ['X', 'Z']:                    # X = in tune (recruit), Z = by force (control)
        for pb in ['ZZ', 'XX', 'YY']:
            qc = ghz(3); basis(qc, 0, how)
            basis(qc, 1, pb[0]); basis(qc, 2, pb[1])
            qc.measure(range(3), range(3)); qcs[(how, pb)] = qc
    return qcs

def score2(cmap):
    out = {}
    for how in ['X', 'Z']:
        corr = {}
        for pb in ['ZZ', 'XX', 'YY']:
            c = cmap[(how, pb)]; tot = sum(c.values()); s = 0
            for k, v in c.items():
                b = bits(k, 3); sign = (-1) ** b[0]    # the recruited result steers which pair (Phi+ or Phi-)
                par = (-1) ** ((b[1] + b[2]) % 2)
                s += v * (par if pb == 'ZZ' else par * sign)
            corr[pb] = s / tot
        F = (1 + corr['ZZ'] + corr['XX'] - corr['YY']) / 4
        out['in_tune' if how == 'X' else 'by_force'] = {'corr': corr, 'bell_fidelity': F}
    out['ideal'] = {'in_tune': 1.0, 'by_force': 0.5, 'entangled_above': 0.5}
    return out

# ---------------- Door 3: PINATA ----------------
THETAS = np.linspace(0, 2 * math.pi, 25)
def door3():
    qcs = []
    for th in THETAS:
        qc = ghz(3)
        for q in range(3): qc.rz(th, q)
        for q in range(3): basis(qc, q, 'X')
        qc.measure(range(3), range(3)); qcs.append(qc)
    for th in THETAS:
        qc = QuantumCircuit(1, 1); qc.h(0); qc.rz(th, 0); qc.h(0); qc.measure(0, 0); qcs.append(qc)
    return qcs

def fit_freq(y):
    best = None
    for f in [1, 2, 3, 4, 6]:
        A = np.vstack([np.cos(f * THETAS), np.sin(f * THETAS), np.ones_like(THETAS)]).T
        coef, *_ = np.linalg.lstsq(A, y, rcond=None); r = y - A @ coef
        amp = math.hypot(coef[0], coef[1]); sse = float(r @ r)
        if best is None or sse < best[2]: best = (f, amp, sse)
    return {'frequency': best[0], 'amplitude': best[1]}

def score3(counts):
    n = len(THETAS)
    ghz_y = np.array([parity_exp(c, [0, 1, 2]) for c in counts[:n]])
    one_y = np.array([parity_exp(c, [0]) for c in counts[n:]])
    return {'standoff': fit_freq(ghz_y), 'lone_qubit': fit_freq(one_y), 'curves': {'theta': THETAS.tolist(), 'standoff': ghz_y.tolist(), 'lone': one_y.tolist()},
            'ideal': {'standoff_frequency': 3, 'lone_frequency': 1}}

# ---------------- Door 4: THREE MORE BODIES ----------------
TH6 = np.linspace(0, 2 * math.pi, 25)
def door4():
    qcs = []
    z = ghz(6); z.measure(range(6), range(6)); qcs.append(z)
    for th in TH6:
        qc = ghz(6)
        for q in range(6): qc.rz(th, q)
        for q in range(6): basis(qc, q, 'X')
        qc.measure(range(6), range(6)); qcs.append(qc)
    return qcs

def score4(counts):
    zc = counts[0]; tot = sum(zc.values())
    pop = (zc.get('000000', 0) + zc.get('111111', 0)) / tot
    y = np.array([parity_exp(c, list(range(6))) for c in counts[1:]])
    A = np.vstack([np.cos(6 * TH6), np.sin(6 * TH6), np.ones_like(TH6)]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None); C = math.hypot(coef[0], coef[1])
    F = (pop + C) / 2
    return {'populations_000000_111111': pop, 'oscillation_amplitude': C, 'fidelity': F, 'genuine_6_body': F > 0.5,
            'curve': y.tolist(), 'ideal': {'fidelity': 1.0, 'certificate_threshold': 0.5}}

def main():
    for name, sim, fb in backends():
        print(f'\n=== {name} ===', flush=True)
        d = {}
        qcs, settings = door0(); d['door0_standoff'] = score0(run(qcs, sim, fb), settings)
        print(f"Door 0 STANDOFF   Mermin M = {d['door0_standoff']['M']:.3f}  (classical max 2, quantum 4)   no-outcome floor {d['door0_standoff']['forbidden_fraction']:.3%}", flush=True)
        d['door1_blondie'] = score1(run(door1(), sim, fb))
        b = d['door1_blondie']; print(f"Door 1 BLONDIE    look in A: {b['A']['found_in_box_given_kept']:.3f}  look in B: {b['B']['found_in_box_given_kept']:.3f}  look in C: {b['C']['found_in_box_given_kept']:.3f}  (ideal 1 / 1 / 0.2)  kept {b['A']['kept_fraction']:.1%}", flush=True)
        m2 = door2(); keys = list(m2.keys()); cs = run([m2[k] for k in keys], sim, fb)
        d['door2_recruit'] = score2(dict(zip(keys, cs))); r = d['door2_recruit']
        print(f"Door 2 RECRUIT    in tune: pair fidelity {r['in_tune']['bell_fidelity']:.3f}   by force: {r['by_force']['bell_fidelity']:.3f}  (entangled above 0.5)", flush=True)
        d['door3_pinata'] = score3(run(door3(), sim, fb)); p = d['door3_pinata']
        print(f"Door 3 PINATA     standoff swings at {p['standoff']['frequency']}x (amp {p['standoff']['amplitude']:.2f}); lone qubit at {p['lone_qubit']['frequency']}x (amp {p['lone_qubit']['amplitude']:.2f})", flush=True)
        d['door4_six_bodies'] = score4(run(door4(), sim, fb)); s = d['door4_six_bodies']
        print(f"Door 4 SIX BODIES fidelity {s['fidelity']:.3f}  -> {'GENUINE 6-body standoff' if s['genuine_6_body'] else 'NOT certified (noise ate it)'}", flush=True)
        OUT['doors'][name] = d
    json.dump(OUT, open('standoff_results.json', 'w'), indent=1, default=float)
    print('\nreceipts: standoff_results.json', flush=True)

if __name__ == '__main__':
    main()
