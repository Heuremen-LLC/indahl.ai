"""readtail.py -- THE TAIL RUN, read as a three (three reads, each against the other two). By hand, outside the freeze. All bits, no cut, no two-way sort, no verdict word.
The object: what a look costs and WHEN the cost lands. Per bit, per read, from its own circuits (ON; MID as the second ruler):
  kept(w)   = what look 2 reads after a wait w, over what look 1 read (no wait: w = 0)
  long clock = the clock between the 60 and 300 us looks
  EXTRA(w)  = long clock x ln(1 / kept(w)) - w   : how much MORE time than the wait the bit says has passed (us). By construction EXTRA(60) = EXTRA(300).
  stretch clocks: the clock inside each stretch none->6.7, 6.7->20, 20->60, each over the long clock."""
import json, os, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, 'data', 'fire', 'ibm_pittsburgh'); TW = ['0', '6.7', '20', '60', '300']
med = lambda v: float(np.nanmedian(v)); q = lambda v: f'[{np.nanpercentile(v, 25):+.2f} {np.nanpercentile(v, 75):+.2f}]'
R = []
for k in (1, 2, 3):
    mp = os.path.join(D, f'run{20 + k}_meta.json')
    if not os.path.exists(mp): print(f"read {k}: NOT LANDED (a row)"); continue
    m = json.load(open(mp)); z = np.load(os.path.join(D, f'run{20 + k}_results.npz')); wr = {c['key']: c['pre_waits_realized_us'][1] for c in m['ledger']['circuits']}
    L = lambda key, i: np.asarray(z[f'{key}__L{i}']).astype(complex)
    off1 = L('OFF|w0', 1); on1 = np.concatenate([L(f'ON|w{w}', 1) for w in TW]); m0 = off1.mean(0); d = on1.mean(0) - m0
    u = lambda x: (x - m0) * np.conj(d) / np.abs(d) ** 2; al = lambda x: np.real(u(x)); ac = lambda x: np.imag(u(x)); sk = lambda v: ((v - v.mean(0)) ** 3).mean(0) / v.std(0) ** 3
    r = {'time': m['start_time'][11:19], 'w': [wr[f'ON|w{w}'] for w in TW], 'sep': np.abs(d) / np.sqrt((np.abs(off1 - m0) ** 2).mean(0) / 2), 'off2': al(L('OFF|w0', 2)).mean(0)}
    for s in ('ON', 'MID'):
        lev = np.array([al(L(f'{s}|w{w}', 1)).mean(0) for w in TW]); F = np.array([al(L(f'{s}|w{w}', 2)).mean(0) for w in TW]); kept = F / lev; w = np.array(r['w'])
        tl = (w[4] - w[3]) / np.log(kept[3] / kept[4]); tl = np.where((tl > 5) & (tl < 5000), tl, np.nan)
        r[s] = {'kept': kept, 'tl': tl, 'extra': tl * np.log(1 / kept) - w[:, None],
                'stretch': np.array([(w[i + 1] - w[i]) / np.log(kept[i] / kept[i + 1]) for i in range(3)]) / tl,
                'skew2': np.array([sk(al(L(f'{s}|w{w_}', 2))) for w_ in TW]), 'across2': np.array([ac(L(f'{s}|w{w_}', 2)).mean(0) for w_ in TW]), 'acrossvar2': np.array([ac(L(f'{s}|w{w_}', 2)).var(0) for w_ in TW])}
    R.append(r)
n = len(R); nb = len(R[0]['sep'])
print(f'THE TAIL RUN: ibm_pittsburgh, ALL {nb} bits, {n} reads at ' + ' '.join(r['time'][:5] for r in R) + '; waits laid (us): ' + ' '.join(f'{x:.2f}' for x in R[0]['w']))
for s in ('ON', 'MID'):
    print(f'\n==== start {s}' + (' (the second ruler: its own circuits)' if s == 'MID' else ''))
    print('  WHAT LOOK 2 KEEPS of what look 1 read, middle bit:        none     6.7      20       60       300')
    for r in R: print(f"     read {r['time'][:5]}                                      " + '  '.join(f'{med(x):.4f}' for x in r[s]['kept']) + f"     long clock {med(r[s]['tl']):.0f} us ({int(np.isfinite(r[s]['tl']).sum())} bits placed)")
    print('  EXTRA TIME the bit says has passed beyond the wait (us), middle bit [quarter points]:   none            6.7             20              60 (= 300)')
    for r in R: print(f"     read {r['time'][:5]}    " + '   '.join(f"{med(x):5.2f} {q(x)}" for x in r[s]['extra'][:4]))
    E = np.array([r[s]['extra'] for r in R]); Em = np.nanmedian(E, 0)
    print('     each bit over the reads, then the middle bit:   ' + '   '.join(f'{med(x):5.2f}' for x in Em[:4]) + '      steps: ' + '  '.join(f'{med(Em[i + 1] - Em[i]):+.2f}' for i in range(3)))
    print('     each read minus the mean of the other two (middle bit): ' + ' | '.join(' '.join(f'{med(E[i, j] - np.delete(E, i, 0)[:, j].mean(0)):+.2f}' for j in range(4)) for i in range(n)) if n == 3 else '')
    print('  THE CLOCK INSIDE EACH STRETCH over the long clock, middle bit [quarter points]:      none->6.7        6.7->20         20->60')
    for r in R: print(f"     read {r['time'][:5]}    " + '   '.join(f"{med(x):5.3f} {q(x)}" for x in r[s]['stretch']))
    St = np.nanmedian(np.array([r[s]['stretch'] for r in R]), 0); print('     each bit over the reads, then the middle bit:   ' + '   '.join(f'{med(x):5.3f}' for x in St))
    tl = np.nanmedian(np.array([r[s]['tl'] for r in R]), 0); o = np.argsort(tl); o = o[np.isfinite(tl[o])]; th = np.array_split(o, 3)
    print('  BY THIRDS OF THE CHIP sorted on the long clock (short / middle / long): long clock | EXTRA at none, 6.7, 20, 60 (us) | the same as a share of the long clock (x1000)')
    for t in th: print(f"     {med(tl[t]):5.0f} us | " + '  '.join(f'{med(Em[j][t]):5.2f}' for j in range(4)) + '  | ' + '  '.join(f'{med(Em[j][t] / tl[t]) * 1000:5.1f}' for j in range(4)))
    print('  LOPSIDEDNESS of look 2 along the line, middle bit, by wait:   ' + '  '.join(f"{med(np.array([r[s]['skew2'][j] for r in R])):+.3f}" for j in range(5)))
    print('  ACROSS the line (the other half of each dot), look 2: mean by wait ' + '  '.join(f"{med(np.array([r[s]['across2'][j] for r in R])):+.4f}" for j in range(5)) + '   spread ' + '  '.join(f"{med(np.array([r[s]['acrossvar2'][j] for r in R])):.4f}" for j in range(5)))
print('\n==== OFF, no wait: what look 2 reads (middle bit), per read: ' + '  '.join(f"{med(r['off2']):+.4f}" for r in R))
print('\n==== THE BITS THAT DO NOT BEHAVE (rows): what look 2 keeps at none / 6.7 / 20 / 60 / 300, start ON, each read')
odd = sorted(set([31, 36, 47, 57, 66, 90, 137, 155]) | set(int(b) for b in np.where(~np.isfinite(np.array([r['ON']['tl'] for r in R])).all(0))[0]))
for b in odd: print(f'   q{b:<4} ' + '  |  '.join(' '.join(f'{x:+.3f}' for x in r['ON']['kept'][:, b]) for r in R) + f"   sep/width {med([r['sep'][b] for r in R]):.1f}")
json.dump({'times': [r['time'] for r in R], 'waits': R[0]['w'], 'ON_extra': np.array([r['ON']['extra'] for r in R]).tolist(), 'MID_extra': np.array([r['MID']['extra'] for r in R]).tolist(), 'ON_tl': np.array([r['ON']['tl'] for r in R]).tolist()}, open(os.path.join(HERE, 'data', 'reads', 'tail_run.json'), 'w'))
