"""synth_clock.py -- planted worlds through the UNCHANGED clock.py readers (packed bit arrays in IBM's BitArray layout), both chips.
Kick truth per qubit and the tables come from the real files. Worlds (expected FINAL outcomes written here before the run):
  WH holds:  today's kick = the 31 Oct table + N(0, 0.15 deg) (only the table's own calibration noise). expect CONSISTENT or CANNOT_TELL.
  WJ jitter: today's kick = the 31 Oct table + N(0, 0.25 deg). Sensitivity probe, no expected outcome: its rates are reported as found.
             (First pass, synth_results_clock_FIRST.text: this jitter sat inside WH and read BELOW in 2 of 10 marrakesh draws.)
  WA aged:   today's kick = 0.7 x the 31 Oct table + N(0, 1 deg).     expect M31 - MT BELOW.
  WM moved:  today's kick = the 31 Oct table + N(0, 1.5 deg) per qubit (no scale change).  expect M31 - MT BELOW.
  W0 null:   no kick.                                                  expect the known-good check to FAIL (chip not decided).
Today's table MT = today's kick + N(0, 0.15 deg) (a 4,000-shot calibration). D carries a free precession N(0, 15 deg) per qubit, shared by
every arm. Coherence per qubit = the committed table's (floor 0.03). Usage: synth_clock.py [NDRAW] -> synth_results_clock.text"""
import sys, os, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import keystone as K, clock as C
def pack(B):
    sh, nb = B.shape; nby = (nb + 7) // 8; P = np.zeros((sh, nby * 8), np.uint8); P[:, :nb] = B
    by = np.packbits(P.reshape(sh, nby, 8), axis=2, bitorder='little').reshape(sh, nby); return by[:, ::-1].copy()
_t = np.random.default_rng(1).integers(0, 2, (5, 21)); assert all((K.bits(pack(_t), k) == _t[:, k]).all() for k in range(21)), 'pack layout'
EXPECT = {'WH': ('CONSISTENT', 'CANNOT_TELL'), 'WJ': 'ANY', 'WA': ('BELOW',), 'WM': ('BELOW',), 'W0': None}
def run(chip, world, rng):
    T = K.table(chip); S = [int(q) for q in T['S']]; COH = {int(q): max(0.03, v[3]) for q, v in T['kicks_deg_per_readout'].items()}
    t31 = C.table31(chip); com = K.committed_corr(chip, 8)
    if world == 'WH': k = {q: t31[q] + rng.normal(0, 0.15) for q in S}
    elif world == 'WJ': k = {q: t31[q] + rng.normal(0, 0.25) for q in S}
    elif world == 'WA': k = {q: 0.7 * t31[q] + rng.normal(0, 1) for q in S}
    elif world == 'WM': k = {q: t31[q] + rng.normal(0, 1.5) for q in S}
    else: k = {q: 0.0 for q in S}
    today = {q: k[q] + rng.normal(0, 0.15) for q in S}; free = {q: rng.normal(0, 15) for q in S}
    corr = {'MC': com, 'M31': t31, 'MT': today}
    c = np.array([COH[q] for q in S])
    def copy():
        Z = {}
        for a in C.ARMS:
            ph = np.radians(np.array([free[q] + (C.N * k[q] if a != 'D' else 0) - (C.N * corr[a][q] if a in corr else 0) for q in S])); tot = ph - np.pi / 2
            for st in C.SETS:
                ev = c * (np.cos(tot) if st == 'X' else np.sin(tot)); Z[(a, st)] = pack((rng.random((C.SHOTS, len(S))) < (1 - ev) / 2).astype(np.uint8))
        return Z
    ZA, ZB = copy(), copy()
    res = {}
    for lab, Zc in (('A', {kk: [v] for kk, v in ZA.items()}), ('B', {kk: [v] for kk, v in ZB.items()}), ('pooled', {kk: [ZA[kk], ZB[kk]] for kk in ZA})):
        res[lab] = C.read(Zc, len(S), rng, B=400)[0]
    fin = C.final(res); return fin, C.kg_pass(fin, chip)
if __name__ == '__main__':
    nd = int(sys.argv[1]) if len(sys.argv) > 1 else 10; rng = np.random.default_rng(31); lines = []; bad = 0
    for chip in ('ibm_kingston', 'ibm_marrakesh'):
        for w in ('WH', 'WJ', 'WA', 'WM', 'W0'):
            tally = {}; kgp = 0
            for d in range(nd):
                fin, kg = run(chip, w, rng); kgp += kg
                o = fin['share M31 minus share MT (margin 0.05)']['final'] if kg else 'NOT DECIDED (known-good failed)'
                tally[o] = tally.get(o, 0) + 1
                ok = True if EXPECT[w] == 'ANY' else ((not kg) if EXPECT[w] is None else (kg and o in EXPECT[w]))
                if not ok: bad += 1
            lines.append(f'{chip} {w}: known-good passed {kgp}/{nd}; M31 - MT FINAL {tally}; expected {EXPECT[w] or "known-good FAIL"}')
            print(lines[-1], flush=True)
    lines.append(f'MISMATCHES against the expected outcomes: {bad} of {nd * 8} draws with an expected outcome')
    open(os.path.join(HERE, 'synth_results_clock.text'), 'w').write('SYNTHETIC, clock.py readers unchanged, %d draws per world per chip (31 Oct 2026)\n' % nd + '\n'.join(lines) + '\n')
    print(lines[-1])
