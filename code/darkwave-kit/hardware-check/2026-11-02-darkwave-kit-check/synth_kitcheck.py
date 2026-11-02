"""synth_kitcheck.py -- runs the PLAN_KITCHECK readings on planted counts. Every alternative the plan can read is planted:
  A  kit and study read the same turn, correction right            -> R1 CONSISTENT, R2a CONSISTENT, R2b ABOVE
  B  the kit reads the turn with the wrong sign (bug)              -> R1 not CONSISTENT, R2 fails
  C  the kit reads a turn 1 deg/readout too big on every target    -> R1 not CONSISTENT
  D  no turn at all (null world): kicks 0                          -> R1 CONSISTENT, R2a CONSISTENT, R2b CANNOT_TELL (nothing to give back)
  E  correction applied with the wrong sign on hardware            -> R2a not CONSISTENT, R2b BELOW
Counts are binomial draws at 4,000 shots from the planted phases with coherence 0.85 (idle) and 0.80 (readout)."""
import sys, os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import kitcheck as KC
K = KC.K; DK = KC.DK
CHIP = 'ibm_kingston'; T = K.table(CHIP); S = [int(q) for q in T['S']]; m = len(S); SH = 4000
COM = np.array([T['kicks_deg_per_readout'][str(q)][8] for q in S])
def packed(p1, rng):
    nby = (m + 7) // 8; arr = np.zeros((SH, nby), np.uint8)
    bits = (rng.random((SH, m)) < p1[None, :]).astype(np.uint8)
    for k in range(m): arr[:, nby - 1 - k // 8] |= bits[:, k] << (k % 8)
    return arr
def arm(phase, r, basis, rng):
    return packed((1 - r * (np.cos(phase) if basis == 'X' else np.sin(phase))) / 2, rng)
def world(true, kit_bias=0.0, kit_sign=1.0, corr_sign=1.0, seed=5):
    rng = np.random.default_rng(seed); ph0 = np.radians(-90.0) + rng.normal(0, 0.05, m); t = np.radians(true)
    kit = {}
    for N in DK.NS:
        for b in DK.BASES:
            kit[(N, 'D', b)] = arm(ph0, 0.85, b, rng); kit[(N, 'M', b)] = arm(ph0 + N * (kit_sign * t + np.radians(kit_bias)), 0.80, b, rng)
    cal = {}
    for k in K.keys_cal():
        _, a, b, N = k; cal[k] = arm(ph0 + (N * t if a == 'M' else 0), 0.80 if a == 'M' else 0.85, b, rng)
    kt = KC.kit_table(kit, S); st = KC.study_table(CHIP, cal, S)
    est = np.radians(np.array([kt[q]['deg_per_readout'] for q in S]))
    a2 = {}
    for b in DK.BASES:
        a2[(4, 'D', b)] = arm(ph0, 0.85, b, rng); a2[(4, 'M', b)] = arm(ph0 + 4 * t, 0.80, b, rng)
        a2[(4, 'MC', b)] = arm(ph0 + 4 * (t - corr_sign * est), 0.80, b, rng)
    return KC.r1(kt, st, S), KC.r2(a2, S, kt)
true = COM + np.random.default_rng(1).normal(0, 0.3, m)
cases = [('A same turn, right correction', dict(true=true)), ('B kit sign flipped', dict(true=true, kit_sign=-1.0)),
         ('C kit 1 deg too big', dict(true=true, kit_bias=1.0)), ('D null world', dict(true=np.zeros(m))), ('E correction sign wrong on hardware', dict(true=true, corr_sign=-1.0))]
L = []
for name, kw in cases:
    R1, R2 = world(**kw)
    L.append(f"{name}: R1 {R1['median']:+.3f} [{R1['band'][0]:+.3f}, {R1['band'][1]:+.3f}] {R1['outcome']} | R2a {R2['residual']['median']:+.3f} [{R2['residual']['band'][0]:+.3f}, {R2['residual']['band'][1]:+.3f}] {R2['residual']['outcome']} | R2b {R2['share_given_back']['median']:+.3f} [{R2['share_given_back']['band'][0]:+.3f}, {R2['share_given_back']['band'][1]:+.3f}] n={R2['share_given_back']['n']} {R2['share_given_back']['outcome']}")
want = {'A': ('CONSISTENT', 'CONSISTENT', 'ABOVE'), 'D': ('CONSISTENT', 'CONSISTENT', None)}
ok = (L[0].count('CONSISTENT') == 2 and L[0].endswith('ABOVE') and 'R1' in L[1] and ' CONSISTENT |' not in L[1].split('|')[0]
      and ' CONSISTENT |' not in L[2].split('|')[0] and 'R2a' in L[4] and ' CONSISTENT |' not in L[4].split('|')[1] and L[4].endswith('BELOW'))
L.append('SYNTH ' + ('PASS: every planted alternative reads as planted' if ok else 'FAIL'))
open(os.path.join(HERE, 'synth_kitcheck_results.text'), 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
