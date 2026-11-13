"""synth_lima.py -- lima.py run on PLANTED data before any job. Truths are the author's own published distributions (his 20 raw count vectors,
10 graphs x lambda 1, 3), mixed toward the uniform distribution by eps (extra depolarising noise) as a function of job position t = 0..5
(order P1, S1a, S1b, S2a, S2b, P2). Counts are drawn at 4000 shots per circuit (his count) unless stated.
Worlds: NEITHER (nothing moves), EFFECT only (S jobs carry extra noise, no drift), DRIFT step (after job index 2), DRIFT linear, BOTH (linear + effect),
SMALL linear (below detection), LOW SHOTS (60 per circuit: the null is wider than his published gain -> CANNOT_TELL on every reading).
SCORING (fixed here, before any job): each world is run REPS times (fresh counts each time). For each reading, TRUE = the statistic on the noise-free truth,
H = median over runs of the null half-width. Expected outcome: signed readings ABOVE if TRUE >= 2H, BELOW if TRUE <= -2H, CONSISTENT if |TRUE| <= 0.35H;
R4 (a positive statistic with a shot-noise floor) ABOVE if TRUE >= 1.5 x the null's upper bound, CONSISTENT if TRUE <= 0.2 x it; in between = GREY, reported, not scored.
A world PASSES if every scored reading returns its expected outcome in >= 85 % of runs (a two-sided 95 % rule alone gives 5 % false calls)."""
import json, sys, numpy as np, lima as A
edges, y, cmean, counts = A.load_theirs(); V = A.obs_matrix(edges)
T = {l: np.array([counts[(s, l)] / counts[(s, l)].sum() for s in A.SEEDS]) for l in (1, 3)}
isS = lambda j: j.startswith('S')
def world(eps_of):
    return {j: {l: (1 - eps_of(t, j)) * T[l] + eps_of(t, j) / 32 for l in A.LAMS[j]} for t, j in enumerate(A.ORDER)}
WORLDS = {
 'NEITHER': (lambda t, j: 0.0, 4000),
 'EFFECT only (S jobs +6 % noise, no drift)': (lambda t, j: 0.06 * isS(j), 4000),
 'DRIFT step (+8 % noise after job index 2)': (lambda t, j: 0.08 * (t >= 3), 4000),
 'DRIFT linear (+2 % noise per job)': (lambda t, j: 0.02 * t, 4000),
 'BOTH (linear drift + S jobs +6 %)': (lambda t, j: 0.02 * t + 0.06 * isS(j), 4000),
 'SMALL linear (+0.15 % per job, below detection)': (lambda t, j: 0.0015 * t, 4000),
 'LOW SHOTS (NEITHER at 60 shots)': (lambda t, j: 0.0, 60)}
REPS, BREP = 40, 500
def gen(P, shots, rng): return {j: {l: np.array([rng.multinomial(shots, P[j][l][g]) for g in range(10)]) for l in P[j]} for j in P}
if __name__ == '__main__':
    rng = np.random.default_rng(5); table = []
    for name, (eps_of, shots) in WORLDS.items():
        P = world(eps_of); true = {k: float(v) for k, v in A.stats(A.means(P, V), y).items()}
        print('==', name); print('\n'.join(A.analyse(gen(P, shots, rng), V, y, rng)[0]))
        runs = [A.analyse(gen(P, shots, rng), V, y, rng, B=BREP)[1] for _ in range(REPS)]
        print('   TRUE (noise-free): ' + ', '.join(f'{k.split("  ")[0]} {v:+.4f}' for k, v in true.items()))
        ok = True
        for k, t in true.items():
            H = float(np.median([(r[k][4] - r[k][3]) / 2 for r in runs])); U = float(np.median([r[k][4] for r in runs]))
            if shots < 1000: exp = 'CANNOT_TELL'
            elif k.startswith('R4'): exp = 'ABOVE' if t >= 1.5 * U else 'CONSISTENT' if t <= 0.2 * U else 'GREY'
            else: exp = 'ABOVE' if t >= 2 * H else 'BELOW' if t <= -2 * H else 'CONSISTENT' if abs(t) <= 0.35 * H else 'GREY'
            got = [r[k][5] for r in runs]; rate = float(np.mean([g == exp for g in got])); dist = {o: got.count(o) for o in ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL') if got.count(o)}
            good = exp == 'GREY' or rate >= 0.85; ok &= good
            print(f'   {k:24s} expect {exp:11s} got {dist} ({rate:.0%} as expected) {"" if exp != "GREY" else "[not scored]"} -> {"ok" if good else "FAIL"}')
        table.append((name, ok))
    print('\nSYNTHETIC TABLE (' + str(REPS) + ' runs per world)'); [print(f'  {"PASS" if ok else "FAIL"}  {n}') for n, ok in table]
    print('ALL WORLDS PASS' if all(ok for _, ok in table) else 'NOT ALL WORLDS PASS')
