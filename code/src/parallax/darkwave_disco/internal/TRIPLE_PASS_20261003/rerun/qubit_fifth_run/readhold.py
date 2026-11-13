"""readhold.py -- THE HOLD RUN (and the one TURNS read), read as a three. By hand, outside the freeze. All bits, no cut, no verdict word.
Frame = lone looks of OFF and ON at no wait. LEFT = what the last look reads after our 300 us, per arm.
"TIME THE BIT SAYS PASSED" = 300 us x ln(LEFT) / ln(LEFT with nothing done): the bit's own fading as the yardstick, no fit, no clock of ours."""
import json, os, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, 'data', 'fire', 'ibm_pittsburgh'); med = lambda v: float(np.nanmedian(v))
ARMS = ['N0', 'L1', 'L3', 'L9', 'P1', 'P3', 'P9']; NAME = {'N0': 'nothing', 'L1': '1 look on the way', 'L3': '3 looks', 'L9': '9 looks', 'P1': 'parked once (far side for the 2nd half)', 'P3': 'parked on alternate quarters', 'P9': 'parked on alternate tenths'}
R = []
for k in (1, 2, 3):
    mp = os.path.join(D, f'run{70 + k}_meta.json')
    if not os.path.exists(mp): print(f'hold read {k}: NOT LANDED (a row)'); continue
    m = json.load(open(mp)); z = np.load(os.path.join(D, f'run{70 + k}_results.npz')); L = lambda key, i: np.asarray(z[f'{key}__L{i}']).astype(complex)
    m0 = L('OFF|w0', 1).mean(0); d = L('ON|w0', 1).mean(0) - m0; al = lambda x: np.real((x - m0) * np.conj(d)) / np.abs(d) ** 2
    nl = {c['key']: c['n_looks'] for c in m['ledger']['circuits']}
    r = {'time': m['start_time'][11:19], 'left': {a: al(L(f'ON|{a}', nl[f'ON|{a}'])).mean(0) for a in ARMS}, 'ladder': {a: [al(L(f'ON|{a}', i)).mean(0) for i in range(1, nl[f'ON|{a}'] + 1)] for a in ('L1', 'L3', 'L9')},
         'offL9': [al(L('OFF|L9', i)).mean(0) for i in range(1, 11)], 'offP9': al(L('OFF|P9', 1)).mean(0), 'sep': np.abs(d) / np.sqrt((np.abs(L('OFF|w0', 1) - m0) ** 2).mean(0) / 2)}
    R.append(r)
n = len(R); nb = len(R[0]['sep']); print(f'THE HOLD RUN: ibm_pittsburgh, ALL {nb} bits, {n} reads at ' + ' '.join(r['time'][:5] for r in R) + '; every arm: START ON, 300 us of our time, last look')
print("\n== WHAT IS LEFT AT THE LAST LOOK (middle bit), each read | all reads | TIME THE BIT SAYS PASSED (us; nothing-done = 300 by definition), each read | all")
T = {}
for a in ARMS:
    lf = np.array([r['left'][a] for r in R]); t = np.array([300 * np.log(np.clip(r['left'][a], 1e-6, None)) / np.log(np.clip(r['left']['N0'], 1e-6, None)) for r in R]); T[a] = t
    tm = [300 * np.log(med(r['left'][a])) / np.log(med(r['left']['N0'])) for r in R]
    print(f'   {NAME[a]:<40} ' + ' '.join(f'{med(x):.4f}' for x in lf) + f' | {med(np.nanmedian(lf, 0)):.4f} | from the middle bits: ' + ' '.join(f'{x:6.1f}' for x in tm) + f' | bit by bit: {med(np.nanmedian(t, 0)):6.1f}')
print('\n== EACH ARM MINUS NOTHING-DONE, bit by bit (what is left; middle bit; each read; then the mean and its spread over the reads)')
for a in ARMS[1:]:
    per = [med(r['left'][a] - r['left']['N0']) for r in R]; print(f'   {NAME[a]:<40} ' + ' '.join(f'{x:+.4f}' for x in per) + f'    all: {np.mean(per):+.4f} +- {np.std(per, ddof=1) / np.sqrt(n) if n > 1 else float("nan"):.4f}')
print('\n== WHAT PLAIN BOOKKEEPING SAYS THE PARKED ARMS SHOULD LEAVE, from nothing-done ALONE (time only runs while the bit is ON; a lost bit that gets pushed starts over): a RULER ROW')
def book(p300, nseg, start_on=True):
    q = p300 ** (1.0 / nseg); on, off = (1.0, 0.0) if start_on else (0.0, 1.0)
    for _ in range(nseg): on, off = off + on * (1 - q), on * q        # fade for one stretch (ON -> OFF with chance 1-q), then the push swaps the two
    return on
for a, nseg in (('P1', 2), ('P3', 4), ('P9', 10)):
    bk = [book(med(r['left']['N0']), nseg) for r in R]; ms = [med(r['left'][a]) for r in R]
    print(f'   {NAME[a]:<40} bookkeeping ' + ' '.join(f'{x:.4f}' for x in bk) + '   measured ' + ' '.join(f'{x:.4f}' for x in ms) + '   measured minus bookkeeping ' + ' '.join(f'{x - y:+.4f}' for x, y in zip(ms, bk)))
print('\n== THE LOOKS ON THE WAY (ON start): what each look reads, in order (middle bit; mean of the reads)')
for a in ('L1', 'L3', 'L9'): print(f'   {NAME[a]:<20} ' + ' '.join(f"{np.mean([med(r['ladder'][a][i]) for r in R]):.3f}" for i in range(len(R[0]['ladder'][a]))))
n0 = np.mean([med(r['left']['N0']) for r in R]); print(f'   plain fading through the same moments from nothing-done alone (L9 times): ' + ' '.join(f'{n0 ** ((i + 1) / 10):.3f}' for i in range(10)))
print('\n== RULER ROWS: OFF with nine looks on the way, each look (middle bit, mean of reads): ' + ' '.join(f"{np.mean([med(r['offL9'][i]) for r in R]):+.4f}" for i in range(10)))
print('   OFF with ten pushes (half its time on the far side), last look: ' + ' '.join(f"{med(r['offP9']):+.4f}" for r in R) + '     bookkeeping from nothing-done: ' + ' '.join(f"{book(med(r['left']['N0']), 10, False):.4f}" for r in R))
if n == 3: print('\n== EACH READ MINUS THE MEAN OF THE OTHER TWO (what is left, middle bit): ' + '  '.join(f"{a}: " + ' '.join(f"{med(R[i]['left'][a] - np.mean([R[j]['left'][a] for j in range(3) if j != i], 0)):+.4f}" for i in range(3)) for a in ARMS))
json.dump({a: [med(r['left'][a]) for r in R] for a in ARMS}, open(os.path.join(HERE, 'data', 'reads', 'hold_run.json'), 'w'))
# ---- the one TURNS read
mp = os.path.join(D, 'run61_meta.json')
if os.path.exists(mp):
    m = json.load(open(mp)); z = np.load(os.path.join(D, 'run61_results.npz')); L = lambda key: np.asarray(z[f'{key}__L1']).astype(complex)
    m0 = L('OFF0|w0').mean(0); d = L('ON2|w0').mean(0) - m0; al = lambda x: np.real((x - m0) * np.conj(d)) / np.abs(d) ** 2; wm = lambda a: 1.2533 * np.nanstd(a) / np.sqrt(np.isfinite(a).sum())
    print(f"\n==== THE TURNS READ (one read, fired {m['start_time'][11:19]}; it was in the air before the run was pulled): level at none / 6.7 / 20 us (middle bit), and kept minus ON's kept")
    lev = {s: np.array([al(L(f'{s}|w{x}')).mean(0) for x in ('0', '6.7', '20')]) for s in ('T1', 'T3', 'T5', 'T9', 'ON2', 'ON6')}; kp = {s: v / v[0] for s, v in lev.items()}
    for s, nm in (('T1', 'in-between, 1 quarter-turn'), ('T3', 'in-between, 3 quarter-turns (far side)'), ('T5', 'in-between, 5 (same side as 1)'), ('T9', 'in-between, 9 (same side as 1)'), ('ON2', 'ON, 2 quarter-turns'), ('ON6', 'ON, 6 quarter-turns')):
        print(f'   {nm:<40} ' + ' '.join(f'{med(x):.4f}' for x in lev[s]) + ('' if s == 'ON2' else '    kept minus ON: ' + ' '.join(f'{med(kp[s][j] - kp["ON2"][j]):+.4f} +- {wm(kp[s][j] - kp["ON2"][j]):.4f}' for j in (1, 2))))
    print(f"   OFF by 4 quarter-turns reads {med(al(L('OFF4|w0')).mean(0)):+.4f}")
