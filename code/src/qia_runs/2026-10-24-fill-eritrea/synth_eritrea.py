"""synth_eritrea.py -- eritrea.py run on PLANTED data before any job. Truth = the exact model (convention B or A) of THEIR OWN stamped record (theirs/raw_data/main_calibration.json), so the planted world is their circuit on their numbers,
with depolarising gap g_j per job (E -> E (1 - g_j)), a per-readout Ramsey kick delta (degrees; Ramsey contrast 0.92), and, in two worlds, a record that moves between jobs (CZ(1,2) 0.0362 / 0.0021, their two stamps).
Counts are drawn binomially at 8192 (teleportation) and 4900 (Ramsey) unless stated. The model used in the reading is built from the record of THAT job, as in the real run.
Worlds: NEITHER (hardware = converted model, nothing moves, no kick), CONVENTION-A TRUE (hardware = their-convention model), GAP (hardware worse than both models), DRIFT step, DRIFT linear, KICK only (-1.62 deg per readout, our fez full-pack size),
BOTH (kick + drift step), JITTER (job-level offsets), SMALL (below detection), RECORD MOVES hardware follows it, RECORD MOVES hardware ignores it, LOW SHOTS (300 / 100: the null is wider than their scales -> CANNOT_TELL).
SCORING (fixed here, before any job): each world is run REPS times (fresh counts each time). For each scored reading (R1 R2 R3 R4), TRUE = the statistic on the noise-free truth; Uhi, Ulo = medians over runs of the null band's upper and lower ends.
Expected outcome: ABOVE if TRUE >= 1.5 Uhi, BELOW if TRUE <= 1.5 Ulo, CONSISTENT if 0.2 Ulo <= TRUE <= 0.2 Uhi, otherwise GREY (reported, not scored); LOW SHOTS expects CANNOT_TELL. A world PASSES if every scored reading returns its expected outcome in >= 85 % of runs;
in NEITHER every scored reading must in addition show a false rate (share of runs NOT as expected) of at most about 5 % (<= 6 % allowed for the 300-run sampling)."""
import sys, os, copy, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eritrea as E
raw = E.load_theirs(); SC = E.their_scales(raw)[:2]
CAL = json.load(open(f'{E.T}/raw_data/main_calibration.json'))
def with_cz12(cal, v):
    c = copy.deepcopy(cal)
    for g in c['gates']:
        if g['gate'] == 'cz' and tuple(g['qubits']) in ((1, 2), (2, 1)):
            for p in g['parameters']:
                if p['name'] == 'gate_error': p['value'] = v
    return c
REC_MOVES = [with_cz12(CAL, v) for v in (0.0362, 0.0021, 0.0021, 0.0362)]       # their 14 Jun and 17 Jun stamps, one record per job
EA, EB = E.model_E(CAL, 'A'), E.model_E(CAL, 'B')
MODS_STATIC = {'A': np.array([EA] * 4), 'B': np.array([EB] * 4)}
MODS_MOVE = E.record_models(REC_MOVES)
R_CONTRAST = 0.92
def ram_truth(delta):
    ph = np.radians([2 * delta, 0.0]); return np.stack([R_CONTRAST * np.cos(ph), R_CONTRAST * np.sin(ph)], axis=1)       # (arm R, arm I) x (X, Y)
Z4 = np.zeros(4)
# name: (hardware truth per job (4,4,3), models, delta, shots_t, shots_r)
def gap(base, g): return np.array([base * (1 - gj) for gj in g])
WORLDS = {
 'NEITHER (hardware = converted model)': (gap(EB, Z4), MODS_STATIC, 0.0, 8192, 4900),
 'CONVENTION-A TRUE (hardware = their-convention model)': (gap(EA, Z4), MODS_STATIC, 0.0, 8192, 4900),
 'GAP (hardware 6 % worse than both models)': (gap(EB, [0.06] * 4), MODS_STATIC, 0.0, 8192, 4900),
 'DRIFT step (+5 % gap after job index 1)': (gap(EB, [0, 0, 0.05, 0.05]), MODS_STATIC, 0.0, 8192, 4900),
 'DRIFT linear (+2 % gap per job)': (gap(EB, [0, 0.02, 0.04, 0.06]), MODS_STATIC, 0.0, 8192, 4900),
 'KICK only (-1.62 deg per readout)': (gap(EB, Z4), MODS_STATIC, -1.62, 8192, 4900),
 'BOTH (kick -1.62 + drift step)': (gap(EB, [0, 0, 0.05, 0.05]), MODS_STATIC, -1.62, 8192, 4900),
 'JITTER (job-level offsets, neither linear nor step)': (gap(EB, [0, 0.04, 0, 0.03]), MODS_STATIC, 0.0, 8192, 4900),
 'SMALL (gap 0.1 % per job, kick 0.15 deg: below detection)': (gap(EB, [0, 0.001, 0.002, 0.003]), MODS_STATIC, 0.15, 8192, 4900),
 'RECORD MOVES, hardware follows it (model B of each job record)': (np.array([E.model_E(c, 'B') for c in REC_MOVES]), MODS_MOVE, 0.0, 8192, 4900),
 'RECORD MOVES, hardware ignores it (hardware = model B of job 1 record)': (np.array([E.model_E(REC_MOVES[0], 'B')] * 4), MODS_MOVE, 0.0, 8192, 4900),
 'LOW SHOTS (NEITHER at 300 / 100 shots)': (gap(EB, Z4), MODS_STATIC, 0.0, 300, 100)}
REPS, BNULL = 300, 2000
SCORED = ['R1 LINK-A (hw F - model F, their convention)', 'R2 LINK-B (hw F - model F, converted)', 'R3 DRIFT (F(A2) - F(A1))', 'R4 KICK (deg per readout, (psi_R - psi_I)/2)']
def truth_stats(Et, mods, delta):
    Ft = E.Fa(Et); Ek = ram_truth(delta); kick = (E.psi_deg(Ek[0]) - E.psi_deg(Ek[1])) / 2
    return {SCORED[0]: float(np.mean(Ft - E.Fa(mods['A']))), SCORED[1]: float(np.mean(Ft - E.Fa(mods['B']))), SCORED[2]: float(Ft[3] - Ft[0]), SCORED[3]: float(kick)}
if __name__ == '__main__':
    if '--band95' in sys.argv: E.BAND = (2.5, 97.5); print('BAND 2.5-97.5 (first design, kept only to show the floor that made us widen it; ADDENDUM 1)')
    rng = np.random.default_rng(5); table = []; neither_rates = None
    for name, (Et, mods, delta, st, sr) in WORLDS.items():
        true = truth_stats(Et, mods, delta); Ek = ram_truth(delta)
        gen = lambda: (rng.binomial(st, np.clip((1 + Et) / 2, 0, 1)), rng.binomial(sr, np.clip((1 + np.broadcast_to(Ek, (4, 2, 2))) / 2, 0, 1)))
        print('==', name); Jt, Jr = gen(); print('\n'.join(E.analyse(Jt, Jr, mods, SC, rng, B=BNULL, shots_t=st, shots_r=sr)[0]))
        runs = [E.analyse(*gen(), mods, SC, rng, B=BNULL, shots_t=st, shots_r=sr, Bint=200)[1] for _ in range(REPS)]
        print('   TRUE (noise-free): ' + ', '.join(f'{k.split(" ")[0]} {v:+.5f}' for k, v in true.items()))
        ok = True; rates = {}
        for k in SCORED:
            Uhi = float(np.median([r[k][4] for r in runs])); Ulo = float(np.median([r[k][3] for r in runs])); t = true[k]
            exp = 'CANNOT_TELL' if st < 1000 else 'ABOVE' if t >= 1.5 * Uhi else 'BELOW' if t <= 1.5 * Ulo else 'CONSISTENT' if 0.2 * Ulo <= t <= 0.2 * Uhi else 'GREY'
            got = [r[k][5] for r in runs]; rate = float(np.mean([g == exp for g in got])); rates[k] = rate
            dist = {o: got.count(o) for o in ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL') if got.count(o)}
            good = exp == 'GREY' or rate >= 0.85
            if name.startswith('NEITHER'): good &= (1 - rate) <= 0.06
            ok &= good
            print(f'   {k.split(" (")[0]:12s} TRUE {t:+.5f} null band [{Ulo:+.5f}, {Uhi:+.5f}] expect {exp:11s} got {dist} ({rate:.1%} as expected, false rate {1 - rate:.1%}) {"[not scored]" if exp == "GREY" else ""} -> {"ok" if good else "FAIL"}')
        if name.startswith('NEITHER'): neither_rates = rates
        table.append((name, ok))
    print('\nSYNTHETIC TABLE (' + str(REPS) + ' runs per world)'); [print(f'  {"PASS" if ok else "FAIL"}  {n}') for n, ok in table]
    print('NEITHER false rates per scored reading: ' + ', '.join(f'{k.split(" ")[0]} {1 - v:.1%}' for k, v in neither_rates.items()))
    print('ALL WORLDS PASS' if all(ok for _, ok in table) else 'NOT ALL WORLDS PASS')
