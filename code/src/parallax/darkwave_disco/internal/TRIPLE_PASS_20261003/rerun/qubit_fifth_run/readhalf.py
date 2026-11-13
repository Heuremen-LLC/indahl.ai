"""readhalf.py -- THE HALF-PUSH RUN, read as a three. By hand, outside the freeze. All bits, no cut, no two-way sort, no verdict word.
Per read, per bit, frame = the lone looks of OFFa (nothing) and ONa (one full push) at no wait (OFF = 0, ON = 1).
  level(start, wait)  = what the one look reads;   kept = level(wait) / level(none) for that start
  first-stretch clocks none->6.7 and 6.7->20 us, from the middle bits and bit by bit."""
import json, os, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, 'data', 'fire', 'ibm_pittsburgh'); med = lambda v: float(np.nanmedian(v))
ST = ['MIDa', 'MIDb', 'ONa', 'ONb']; NAMES = {'MIDa': 'in-between, one half-push', 'MIDb': 'in-between, full push + half-push', 'ONa': 'ON, one full push', 'ONb': 'ON, two half-pushes'}; TW = ['0', '6.7', '20']
R = []
for k in (1, 2, 3):
    mp = os.path.join(D, f'run{40 + k}_meta.json')
    if not os.path.exists(mp): print(f'read {k}: NOT LANDED (a row)'); continue
    m = json.load(open(mp)); z = np.load(os.path.join(D, f'run{40 + k}_results.npz')); L = lambda key: np.asarray(z[f'{key}__L1']).astype(complex)
    wr = {c['key']: c['pre_waits_realized_us'][0] for c in m['ledger']['circuits']}
    m0 = L('OFFa|w0').mean(0); d = L('ONa|w0').mean(0) - m0; al = lambda x: np.real((x - m0) * np.conj(d)) / np.abs(d) ** 2; sk = lambda v: ((v - v.mean(0)) ** 3).mean(0) / v.std(0) ** 3
    r = {'time': m['start_time'][11:19], 'w': [wr[f'ONa|w{x}'] for x in TW], 'sep': np.abs(d) / np.sqrt((np.abs(L('OFFa|w0') - m0) ** 2).mean(0) / 2), 'OFFb': al(L('OFFb|w0')).mean(0)}
    for s in ST:
        lev = np.array([al(L(f'{s}|w{x}')).mean(0) for x in TW]); r[s] = {'lev': lev, 'kept': lev / lev[0], 'skew': [med(sk(al(L(f'{s}|w{x}')))) for x in TW]}
    R.append(r)
n = len(R); w = np.array(R[0]['w']); print(f'THE HALF-PUSH RUN: ibm_pittsburgh, ALL {len(R[0]["sep"])} bits, {n} reads at ' + ' '.join(r['time'][:5] for r in R) + '; waits (us) ' + ' '.join(f'{x:.2f}' for x in w))
print('\n== WHAT THE ONE LOOK READS AT NO WAIT (middle bit; OFF = 0, ON by one full push = 1), each read')
for s in ST: print(f'   {NAMES[s]:<34} ' + '  '.join(f"{med(r[s]['lev'][0]):.4f}" for r in R))
print(f"   {'OFF, two full pushes':<34} " + '  '.join(f"{med(r['OFFb']):+.4f}" for r in R))
print('\n== WHAT IT KEEPS after 6.7 us and after 20 us (over its own no-wait level), middle bit, each read; then every bit over the reads')
for s in ST:
    K = np.array([r[s]['kept'] for r in R]); print(f'   {NAMES[s]:<34} 6.7: ' + ' '.join(f'{med(K[i, 1]):.4f}' for i in range(n)) + '   20: ' + ' '.join(f'{med(K[i, 2]):.4f}' for i in range(n)) + f'    | all reads: {med(np.nanmedian(K[:, 1], 0)):.4f}  {med(np.nanmedian(K[:, 2], 0)):.4f}')
print('\n== THE CLOCK IN EACH STRETCH (us), from the middle bits:  none->6.7 (each read)      6.7->20 (each read)      | bit by bit, middle, over the reads')
C = {}
for s in ST:
    K = np.array([r[s]['kept'] for r in R]); p = np.array([[med(K[i, j]) for j in range(3)] for i in range(n)])
    c1 = (w[1] - w[0]) / np.log(p[:, 0] / p[:, 1]); c2 = (w[2] - w[1]) / np.log(p[:, 1] / p[:, 2]); Km = np.nanmedian(K, 0)
    b1 = (w[1] - w[0]) / np.log(Km[0] / Km[1]); b2 = (w[2] - w[1]) / np.log(Km[1] / Km[2]); C[s] = (c1, c2)
    print(f'   {NAMES[s]:<34} ' + ' '.join(f'{x:6.0f}' for x in c1) + '      ' + ' '.join(f'{x:6.0f}' for x in c2) + f'      | {med(b1):6.0f}  {med(b2):6.0f}')
print('\n== EACH START AGAINST THE OTHERS, bit by bit: kept at 6.7 us, one start minus another (middle bit; each read; then all reads with its spread over the reads)')
for a_, b_ in (('MIDa', 'ONa'), ('MIDb', 'ONa'), ('ONb', 'ONa'), ('MIDa', 'MIDb'), ('MIDa', 'ONb'), ('MIDb', 'ONb')):
    for j, lab in ((1, '6.7'), (2, '20 ')):
        dd = np.array([r[a_]['kept'][j] - r[b_]['kept'][j] for r in R]); per = [med(x) for x in dd]
        print(f'   {a_} - {b_} at {lab}: ' + ' '.join(f'{x:+.4f}' for x in per) + f'    all: {np.mean(per):+.4f} +- {np.std(per, ddof=1) / np.sqrt(n) if n > 1 else float("nan"):.4f}')
print('\n== EACH READ MINUS THE MEAN OF THE OTHER TWO (kept at 6.7 us, middle bit): ' + '  '.join(f"{s}: " + ' '.join(f"{med(R[i][s]['kept'][1] - np.mean([R[j][s]['kept'][1] for j in range(n) if j != i], 0)):+.4f}" for i in range(n)) for s in ST) if n == 3 else '')
print('\n== LOPSIDEDNESS of the look along the line, by wait (none / 6.7 / 20), all reads:')
for s in ST: print(f'   {NAMES[s]:<34} ' + '  '.join(f"{np.mean([r[s]['skew'][j] for r in R]):+.3f}" for j in range(3)))
print('\n== ROWS (start ONa / MIDa kept at 6.7 and 20, each read): the short-clock and odd bits')
for b in (31, 36, 57, 66, 90, 137): print(f'   q{b:<4} ' + '  |  '.join(f"{r['ONa']['kept'][1][b]:+.3f} {r['ONa']['kept'][2][b]:+.3f} / {r['MIDa']['kept'][1][b]:+.3f} {r['MIDa']['kept'][2][b]:+.3f}" for r in R))
p = os.path.join(HERE, 'data', 'reads', 'maker_look_length_pittsburgh.json')
if os.path.exists(p):
    x = json.load(open(p)); v = np.array(x['measure_duration_us']); print(f"\n== THE MAKER'S STATED LOOK LENGTH on ibm_pittsburgh (read {x['read_at']}): middle {np.median(v):.3f} us, min {v.min():.3f}, max {v.max():.3f} ({len(v)} bits).  From inside (this morning): 3.2-3.7 us.")
else: print("\n== THE MAKER'S STATED LOOK LENGTH: NOT READ (a row)")
