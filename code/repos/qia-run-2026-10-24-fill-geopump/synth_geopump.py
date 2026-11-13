"""synth_geopump.py -- planted worlds through the SAME analysis (analyze_geopump.run). Shot-by-shot quantum trajectories of the working
qubit S through the published circuit (ry/rz frame steps, partial swap XXPlusYY(2 varphi) with an ancilla in a basis state, projective
ancilla readout), with hardware-like noise common to all arms (T1/T2 of S over each collision interval, readout assignment flips on
recorded ancilla bits) and a PLANTED readout cost applied to S at every INCOMING readout (families A and Ap only, never Bp):
  W0 none | W1 extra relaxation gam_r = 0.0063 per incoming readout (= the T1 cost of one more 2.18 us of idle on S) | W2 coherent Z kick
  1 deg per readout (a PHASE: measured on 24 Oct to move Qtot_even by < 0.03 T even at 5 deg or 10 % dephasing, i.e. invisible to the heat;
  planted to show the run does NOT call it) | W3 both | W4 gam_r = 0.0006 (below resolution).
Same shots, realizations and job layout as the plan (2 copies; per tau: A 4 x 3000 shots; Ap and Bp 4 branches x K=12 x 250 shots).
Usage: synth_geopump.py [ndraws] [band]"""
import os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import geopump as G, analyze_geopump as AN
K, SH_R, SH_A = 12, 250, 3000
T1, T2, TCOL = 344e-6, 356e-6, 3.6e-6          # q47 record 24 Oct; S time per collision ~ 0.69 ms / 192
E10, E01 = 0.004, 0.012                         # assignment P(1|0), P(0|1) (their SM noise numbers)
WORLDS = {'W0_none': (0.0, 0.0, 0.0), 'W1_relax': (0.0, 0.0, 0.0063), 'W2_kick': (0.0, np.deg2rad(1.0), 0.0), 'W3_both': (0.0, np.deg2rad(1.0), 0.0063), 'W4_small': (0.0, 0.0, 0.0006)}

def traj(sch, init, n, rng, fam, bins_rows, p_d, delta, gam_r=0.0):
    """simulate n shots; bins_rows (n, 2N) per bath for Ap/Bp (prepared), None for A. returns recorded eL, eR in the family's format."""
    th = np.arccos(np.clip(init[2], -1, 1)); ph = np.arctan2(init[1], init[0])
    a0 = np.full(n, np.cos(th / 2), complex); a1 = np.full(n, np.sin(th / 2), complex) * np.exp(1j * ph)   # ry then rz (global phase dropped)
    a0, a1 = a0 * np.exp(-1j * ph / 2) / np.exp(-1j * ph / 2), a1
    gam = 1 - np.exp(-TCOL / T1); tphi = 1 / (1 / T2 - 1 / (2 * T1)); pz = 0.5 * (1 - np.exp(-TCOL / tphi))
    w = 4 * G.N if fam in ('A', 'Ap') else 2 * G.N; rec = {'L': np.zeros((n, w), np.uint8), 'R': np.zeros((n, w), np.uint8)}; idx = {'L': 0, 'R': 0}
    gp = sch[0]['g']
    def ry(a, x0, x1): c, s = np.cos(a / 2), np.sin(a / 2); return c * x0 - s * x1, s * x0 + c * x1
    def flip(bits): r = rng.random(n); return np.where(bits == 0, (r < E10).astype(int), (r >= E01).astype(int))
    for m, c in enumerate(sch):
        if m > 0: a0, a1 = ry(gp - c['g'], a0, a1)
        a0, a1 = a0 * np.exp(-0.5j * c['phi_drive']), a1 * np.exp(0.5j * c['phi_drive'])
        for bath in G.ORDER:
            i = idx[bath]; vp = c['th_L'] if bath == 'L' else c['th_R']
            # common noise on S over the collision interval: amplitude damping (physical |1> -> |0>) and pure dephasing
            jump = rng.random(n) < gam * np.abs(a1) ** 2
            a0 = np.where(jump, 1, a0); a1 = np.where(jump, 0, a1 * np.sqrt(1 - gam))
            nr = np.sqrt(np.abs(a0) ** 2 + np.abs(a1) ** 2); a0, a1 = a0 / nr, a1 / nr
            a1 = np.where(rng.random(n) < pz, -a1, a1)
            if fam == 'A': b_in = (rng.random(n) >= c['p_exc']).astype(int)
            else: b_in = bins_rows[bath][:, i]
            if fam in ('A', 'Ap'):
                rec[bath][:, 2 * i] = flip(b_in)
                if p_d > 0: a1 = np.where(rng.random(n) < p_d, -a1, a1)          # planted: extra dephasing per incoming readout
                if delta != 0: a1 = a1 * np.exp(1j * delta)                       # planted: coherent kick per incoming readout
                if gam_r > 0:                                                      # planted: extra relaxation per incoming readout
                    jr = rng.random(n) < gam_r * np.abs(a1) ** 2
                    a0 = np.where(jr, 1, a0); a1 = np.where(jr, 0, a1 * np.sqrt(1 - gam_r)); nr = np.sqrt(np.abs(a0) ** 2 + np.abs(a1) ** 2); a0, a1 = a0 / nr, a1 / nr
            # partial swap with ancilla |b_in>, then projective ancilla readout
            s2 = np.sin(vp) ** 2; cf = np.cos(vp); r = rng.random(n)
            ex0 = (b_in == 0) & (r < np.abs(a1) ** 2 * s2)       # anc 0 -> 1, S 1 -> 0
            ex1 = (b_in == 1) & (r < np.abs(a0) ** 2 * s2)       # anc 1 -> 0, S 0 -> 1
            b_out = np.where(ex0, 1, np.where(ex1, 0, b_in))
            n0 = np.where(ex0, 1, np.where(ex1, 0, np.where(b_in == 0, a0, a0 * cf)))
            n1 = np.where(ex0, 0, np.where(ex1, 1, np.where(b_in == 0, a1 * cf, a1)))
            nr = np.sqrt(np.abs(n0) ** 2 + np.abs(n1) ** 2); a0, a1 = n0 / nr, n1 / nr
            rec[bath][:, (2 * i + 1) if fam in ('A', 'Ap') else i] = flip(b_out); idx[bath] += 1
        gp = c['g']
    return rec['L'], rec['R']

def make_copy(rng, p_d, delta, gam_r=0.0):
    cp = {}
    for tau in AN.TAUS:
        blk = {'A': {}, 'Ap': {}, 'Bp': {}}
        for d in ('fwd', 'rev'):
            sch = G.schedule(AN.DB, tau, d == 'rev'); v0 = G.periodic(sch)
            for b, w, vec in G.branches(v0):
                eL, eR = traj(sch, vec, SH_A, rng, 'A', None, p_d, delta, gam_r); blk['A'][(d, b)] = (w, eL, eR)
                bins = [G.draw_bin(sch, rng) for _ in range(K)]
                rows = {bath: np.repeat(np.array([bk[bath] for bk in bins]), SH_R, axis=0) for bath in 'LR'}
                for fam in ('Ap', 'Bp'):
                    eL, eR = traj(sch, vec, K * SH_R, rng, fam, rows, p_d, delta, gam_r)
                    blk[fam][(d, b)] = (w, [(eL[k * SH_R:(k + 1) * SH_R], eR[k * SH_R:(k + 1) * SH_R], bins[k]) for k in range(K)])
        cp[tau] = blk
    return cp

if __name__ == '__main__':
    nd = int(sys.argv[1]) if len(sys.argv) > 1 else 40; band = float(sys.argv[2]) if len(sys.argv) > 2 else 95.0
    rng = np.random.default_rng(20261024); tally = {}
    print(f'synthetic: {nd} draws per world, band {band:g}%, K={K} x {SH_R} shots (Ap, Bp), A {SH_A} shots, 2 copies, taus {AN.TAUS}')
    for wname, (p_d, delta, gam_r) in WORLDS.items():
        for j in range(nd):
            data = [make_copy(rng, p_d, delta, gam_r), make_copy(rng, p_d, delta, gam_r)]
            res = AN.run(data, band=band, B=400, seed=j, quiet=True)
            for tau in AN.TAUS:
                for (name, k), v in res[tau].items():
                    if name.startswith(('R2', 'R4')): tally.setdefault((wname, tau, name, k), []).append(v['final'])
        print(f'  {wname} done', flush=True)
    print('world | tau | reading | key | ABOVE BELOW CONSISTENT CANNOT_TELL (of draws)')
    fc = []
    for (wname, tau, name, k), outs in sorted(tally.items()):
        c = {o: outs.count(o) for o in ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL')}
        print(f'  {wname:10s} {tau:4.0f} {name:16s} {k:9s} ' + ' '.join(f'{c[o]:3d}' for o in c))
        if wname in ('W0_none', 'W2_kick') or name.startswith('R4'): fc.append((c['ABOVE'] + c['BELOW']) / len(outs))   # truth zero in the heat
    print(f'FALSE-CALL RATE (every reading in W0 and W2, and R4 in every world, where the truth in the heat is zero): mean {np.mean(fc):.3f}, max {np.max(fc):.3f} per reading')
