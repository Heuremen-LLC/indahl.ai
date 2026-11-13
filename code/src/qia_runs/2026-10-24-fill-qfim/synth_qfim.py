"""synth_qfim.py -- qfim.py run on PLANTED data before any job. Truths are the authors' own published 5-job means for the 8 circuits (theirs/raw/analysis.json), pulled toward
1/8 (extra depolarising noise, eps) as a function of job position t = 0..3 (order A1 B1 B2 A2) and of the circuit's slot in the job (0..7 in that job's order). Counts are drawn
binomially at 8192 shots (their count) unless stated; their five published jobs are redrawn from the same truth in every run (a noisy sample, as in life), so R4's truth is the world, not their sample.
Worlds: NEITHER (nothing moves), EFFECT only (slot effect: later slots in a job carry extra noise, no drift), DRIFT step (after job index 1), DRIFT linear, BOTH (linear + slot),
JITTER (each job carries its own random offset, neither linear nor a step), SMALL linear (below detection), LOW SHOTS (60 per circuit: the null is wider than their published spread -> CANNOT_TELL).
SCORING (fixed here, before any job): each world is run REPS times (fresh counts each time). For each pooled reading (R1 R2 R3 R4), TRUE = the statistic on the noise-free truth,
U = median over runs of the null's 97.5 % bound. Expected outcome: ABOVE if TRUE >= 1.5 U, CONSISTENT if TRUE <= 0.2 U, in between = GREY (reported, not scored); LOW SHOTS expects
CANNOT_TELL on every reading incl. R1c. R1c (per circuit) is reported, not scored outside LOW SHOTS. A world PASSES if every scored reading returns its expected outcome in >= 85 % of runs."""
import sys, numpy as np, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qfim as Q
K, pub = Q.load_theirs(); theirs_p = K / Q.SHOTS; T0 = theirs_p.mean(axis=0); pm = T0
SLOT = {'A': {c: i for i, c in enumerate(Q.A_ORDER)}, 'B': {c: i for i, c in enumerate(Q.B_ORDER)}}
def world(eps_of):
    """eps_of(t, slot_pos, c_index) -> extra noise; returns P_true (4, 8) in ORDER."""
    P = np.zeros((4, 8))
    for t, j in enumerate(Q.ORDER):
        for ci, c in enumerate(Q.CIRCS):
            e = eps_of(t, SLOT[j[0]][c], ci); P[t, ci] = (1 - e) * T0[ci] + e / 8
    return P
JIT = np.array([0.0, 0.03, -0.0, 0.025])   # job-level offsets, not linear and not a step (fixed pattern: +0, +3 %, 0, +2.5 %)
WORLDS = {
 'NEITHER': (lambda t, s, c: 0.0, 8192),
 'EFFECT only (slot: +0.6 % noise per slot, no drift)': (lambda t, s, c: 0.006 * s, 8192),
 'DRIFT step (+6 % noise after job index 1)': (lambda t, s, c: 0.06 * (t >= 2), 8192),
 'DRIFT linear (+2 % noise per job)': (lambda t, s, c: 0.02 * t, 8192),
 'BOTH (linear drift + slot effect)': (lambda t, s, c: 0.02 * t + 0.006 * s, 8192),
 'JITTER (job-level offsets, neither linear nor step)': (lambda t, s, c: JIT[t], 8192),
 'SMALL linear (+0.1 % per job, below detection)': (lambda t, s, c: 0.001 * t, 8192),
 'LOW SHOTS (NEITHER at 60 shots)': (lambda t, s, c: 0.0, 60)}
REPS, BREP = 40, 500
SCORED = ['R1 JOB-SD (RMS)', 'R2 STEP (RMS)', 'R3 SLOT (RMS)', 'R4 SINCE (RMS, not drift)']
if __name__ == '__main__':
    rng = np.random.default_rng(5); table = []
    for name, (eps_of, shots) in WORLDS.items():
        Pt = world(eps_of); true = {k: float(v) for k, v in Q.stats(Pt, pm).items()}
        gen = lambda: rng.binomial(shots, Pt) / shots
        th = lambda: rng.binomial(Q.SHOTS, T0, size=(5, 8)) / Q.SHOTS     # their 5 jobs are a noisy draw of the truth too (not the truth itself)
        print('==', name); print('\n'.join(Q.analyse(gen(), pub, th(), rng, shots=shots)[0]))
        runs = [Q.analyse(gen(), pub, th(), rng, B=BREP, shots=shots)[1] for _ in range(REPS)]
        print('   TRUE (noise-free): ' + ', '.join(f'{k.split(" (")[0]} {v:.4f}' for k, v in true.items() if not k.startswith('R1c')))
        ok = True
        for k in (SCORED + (list(true)[4:] if shots < 1000 else [])):
            U = float(np.median([r[k][4] for r in runs])); t = true[k]
            exp = 'CANNOT_TELL' if shots < 1000 else 'ABOVE' if t >= 1.5 * U else 'CONSISTENT' if t <= 0.2 * U else 'GREY'
            got = [r[k][5] for r in runs]; rate = float(np.mean([g == exp for g in got])); dist = {o: got.count(o) for o in ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL') if got.count(o)}
            good = exp == 'GREY' or rate >= 0.85; ok &= good
            print(f'   {k:42s} expect {exp:11s} got {dist} ({rate:.0%} as expected) {"[not scored]" if exp == "GREY" else ""} -> {"ok" if good else "FAIL"}')
        table.append((name, ok))
    print('\nSYNTHETIC TABLE (' + str(REPS) + ' runs per world)'); [print(f'  {"PASS" if ok else "FAIL"}  {n}') for n, ok in table]
    print('ALL WORLDS PASS' if all(ok for _, ok in table) else 'NOT ALL WORLDS PASS')
