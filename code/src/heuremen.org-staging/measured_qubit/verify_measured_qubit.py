#!/usr/bin/env python3
"""verify_measured_qubit.py -- recompute the measured-qubit time-equivalent table from the published data.

    python3 verify_measured_qubit.py

No account, no network, standard library only. Reads data/measured_qubit.json (per-qubit levels from the 3 look-wide reads on each of 7 chips,
~0.9 MB) and data/ruler_check.json (the 30 us and 300 us survivals of the ruler copies, ~0.2 MB).

What is computed (plain words).
  The chip's stated readout duration O is read from the backend's published measure duration (median over qubits).
  A measured qubit that is read k times (k = 1,2,3,4,6,9 back-to-back readouts) loses some of its excitation. We turn that loss into a TIME by asking
  how long the same qubit, left alone, takes to lose that much on its OWN fading curve (log-linear through 0 / 10 / 20 / 40 us of plain waiting).
  That is the 'T1-equivalent time' of k readouts for that qubit. Then the time per readout is a slope over k, two ways:
    "3-and-9": (time after 9 readouts - time after 3 readouts) / 6
    "1-9 fit": least-squares slope of time against k over k = 1,2,3,4,6,9
  Per chip and per read, the median over qubits is taken, then divided by O ("qubit / stated"). The 'spectators' are the phase clocks (qubits held
  half-way, whose hand turns while the far qubits are read): their per-readout time is read the same two ways on the clock's own turn curve
  (angle = c1 t + c2 t^2 through 10/20/30 us), and "qubit / spectators" is the qubit median over the spectator median.
  Each table entry is the mean over the 3 reads; the +- is the sample standard deviation (n-1) of the 3 reads (read-to-read spread, no resampling).
ASSUMPTION: the method reads the loss as if the plain fading were a single exponential (log-linear in time). README.md says why that is not exact.
OK = matches the supplied value at the quoted 3-decimal precision; DIFFERS = does not; NO CLAIM = nothing to compare (computed only).
"""
import cmath, json, math, os, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, 'data', 'measured_qubit.json')))
LOOKS = D['looks']; OWN = D['own_waits_us']; I3, I9 = LOOKS.index(3), LOOKS.index(9)

# ---- the values the audit supplied: (mean, sd) for qubit / stated, 3-and-9 then 1-9 fit
CLAIM = {
    'ibm_kingston':   {'3and9': (1.661, 0.086), 'fit': (1.677, 0.078)},
    'ibm_marrakesh':  {'3and9': (1.516, 0.070), 'fit': (1.509, 0.024)},
    'ibm_fez':        {'3and9': (1.540, 0.224), 'fit': (1.600, 0.186)},
    'ibm_pittsburgh': {'3and9': (1.340, 0.063), 'fit': (1.360, 0.087)},
    'ibm_boston':     {'3and9': (1.348, 0.136), 'fit': (1.333, 0.124)},
    'ibm_phoenix':    {'3and9': (1.351, 0.124), 'fit': (1.323, 0.056)},
}
ORDER = ['ibm_kingston', 'ibm_marrakesh', 'ibm_fez', 'ibm_pittsburgh', 'ibm_boston', 'ibm_phoenix', 'ibm_aachen']


def clip(x, lo, hi): return min(max(x, lo), hi)
def median(v): return st.median(v) if v else float('nan')
def slope(x, y):
    mx, my = sum(x) / len(x), sum(y) / len(y)
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / sum((a - mx) ** 2 for a in x)


def unwrap(a):
    out = [a[0]]
    for i in range(1, len(a)):
        d = a[i] - a[i - 1]; dm = (d + math.pi) % (2 * math.pi) - math.pi
        if dm == -math.pi and d > 0: dm = math.pi
        out.append(out[-1] + (d if abs(d) < math.pi else dm))
    return out


def read_estimates(rd):
    sep = rd['sep']
    # qubit side: the looked-at qubits' own fading
    ts = [0.0] + OWN; tfit, t39 = [], []
    for q, v in rd['far'].items():
        if sep[q] <= 3: continue
        L = [clip(x, 0.02, 1.0) for x in [1.0] + v['AW']]; sl = slope(ts, [math.log(x) for x in L])
        if sl >= 0: continue
        teq = [math.log(clip(x, 0.02, 1.0)) / sl for x in v['A']]
        tfit.append(slope([float(k) for k in LOOKS], teq)); t39.append((teq[I9] - teq[I3]) / 6)
    # spectator side: the phase clocks
    wfit, w39 = [], []
    tt = [10.0, 20.0, 30.0]
    for w in sorted(rd['clocks'], key=int):
        c = rd['clocks'][w]; wo = str(c['witness_of'])
        H = {}
        for a, xy in list(c['T'].items()) + [('K' + k, v) for k, v in c['K'].items()]:
            H[a if a in c['T'] else a] = complex(2 * xy[0] - 1, -(2 * xy[1] - 1))
        H0 = H['0']
        if not (abs(H0) > 0.15 and sep[w] > 3 and sep[wo] > 3): continue
        ang = lambda h: cmath.phase(h / H0)
        uw = unwrap([0.0] + [ang(H[str(t)]) for t in (10, 20, 30)])[1:]
        # least squares y = c0 t + c1 t^2 (no intercept)
        s11 = sum(t * t for t in tt); s12 = sum(t ** 3 for t in tt); s22 = sum(t ** 4 for t in tt)
        b1 = sum(t * y for t, y in zip(tt, uw)); b2 = sum(t * t * y for t, y in zip(tt, uw)); det = s11 * s22 - s12 * s12
        c0 = (b1 * s22 - b2 * s12) / det; c1 = (s11 * b2 - s12 * b1) / det
        teq = []
        for k in LOOKS:
            a = ang(H['K' + str(k)])
            if c1 == 0: r = [a / c0] if c0 else []
            else:
                disc = c0 * c0 + 4 * c1 * a
                r = [(-c0 + sg * math.sqrt(disc)) / (2 * c1) for sg in (1, -1)] if disc >= 0 else []
            r = [x for x in r if -5 < x < 60]
            teq.append(min(r, key=lambda x: abs(x - a / c0)) if r and c0 else float('nan'))
        ok = [(k, t) for k, t in zip(LOOKS, teq) if math.isfinite(t)]
        if len(ok) >= 4: wfit.append(slope([float(k) for k, _ in ok], [t for _, t in ok]))
        if math.isfinite(teq[I3]) and math.isfinite(teq[I9]): w39.append((teq[I9] - teq[I3]) / 6)
    return {'T fit': median(tfit), 'T 3and9': median(t39), 'W fit': median(wfit), 'W 3and9': median(w39), 'nT': len(tfit), 'nW': len(wfit)}


def ms(v): return sum(v) / len(v), st.stdev(v)
def ok(val, claim, tol=0.0005): return abs(round(val, 3) - claim) < tol


results = {}
for chip in ORDER:
    c = D['chips'][chip]; O = c['maker_us']; rows = {'3and9': [], 'fit': [], 'sp3and9': [], 'spfit': []}; ids = []
    for k in ('1', '2', '3'):
        rd = c['reads'][k]; e = read_estimates(rd); ids.append((rd['run'], rd['job_id']))
        rows['3and9'].append(e['T 3and9'] / O); rows['fit'].append(e['T fit'] / O)
        rows['sp3and9'].append(e['T 3and9'] / e['W 3and9']); rows['spfit'].append(e['T fit'] / e['W fit'])
    results[chip] = (O, rows, ids, e['nT'], e['nW'])

print(f'{"chip":<15}{"stated O":>9}  {"estimator":<9}{"computed":>17}  {"supplied":>15}  verdict')
bad = 0; n = 0
for chip in ORDER:
    O, rows, ids, nT, nW = results[chip]
    for key, name in (('3and9', '3-and-9'), ('fit', '1-9 fit')):
        m, s = ms(rows[key]); cl = CLAIM.get(chip, {}).get(key)
        if cl is None: v = 'NO CLAIM (computed only)'
        else:
            n += 2; g1, g2 = ok(m, cl[0]), ok(s, cl[1]); bad += (not g1) + (not g2)
            v = ('OK' if g1 else 'DIFFERS(mean)') + ' / ' + ('OK' if g2 else 'DIFFERS(sd)')
        print(f'{chip:<15}{O:>8.3f}u  {name:<9}{m:>9.3f} +- {s:.3f}  ' + (f'{cl[0]:>7.3f} +- {cl[1]:.3f}' if cl else f'{"-":>15}') + f'  {v}')
print(f'\nqubit / stated: {n - bad} of {n} supplied numbers reproduced at 3-decimal precision, {bad} DIFFER.')

print('\nqubit / spectators (no values were supplied; computed only):')
for chip in ORDER:
    O, rows, ids, nT, nW = results[chip]
    a, b = ms(rows['sp3and9']), ms(rows['spfit'])
    print(f'{chip:<15} 3-and-9 {a[0]:.3f} +- {a[1]:.3f}   1-9 fit {b[0]:.3f} +- {b[1]:.3f}   (last read: {nT} qubits, {nW} spectator clocks)')

print('\nper-read qubit / stated (3-and-9 | 1-9 fit):')
for chip in ORDER:
    O, rows, ids, *_ = results[chip]
    print(f'{chip:<15}' + '  '.join(f'run {r}: {a:.4f} | {b:.4f}' for (r, _), a, b in zip(ids, rows['3and9'], rows['fit'])))

# ---- the single-exponential check: is the ON survival at 30 us below the one-exponential line through 300 us?
R = json.load(open(os.path.join(HERE, 'data', 'ruler_check.json')))
print('\nsingle-exponential check (time_wide ruler copies a,b,c per kept qubit): share of qubit-copies whose survival at 30 us sits BELOW S300^(30/300)')
shares = []
for chip, runs in R['chips'].items():
    for run, r in runs.items():
        tot = low = 0
        for q, cp in r['bits'].items():
            for cc, (s30, s300) in cp.items():
                tot += 1; low += clip(s30, 0.02, 1.0) < clip(s300, 0.02, 0.98) ** (30 / 300)
        if tot: shares.append(100 * low / tot); print(f'  {chip:<15} run {run}: {low}/{tot} = {100 * low / tot:.1f} %  job {r["job_id"]}')
print(f'  range over these {len(shares)} reads: {min(shares):.1f} - {max(shares):.1f} %  (supplied: 62-84 %)')
