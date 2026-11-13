"""readsides.py -- THE SIDES RUN. By hand, outside the freeze. All bits, no cut, no verdict word.
Frame = the lone looks of OFF and ON at no wait. For each start: level at none / 6.7 / 20 us, kept = level(wait) / level(none), and kept minus ON's.
Then the three boxes side by side: does the early term follow the ANGLE (S0, S120, S240, S180 against each other), the PATH (S180 against FAR), or neither."""
import json, os, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, 'data', 'fire', 'ibm_pittsburgh'); med = lambda v: float(np.nanmedian(v))
ST = ['S0', 'S120', 'S240', 'S180', 'FAR', 'ON']; TW = ['0', '6.7', '20']; ANG = {'S0': 0, 'S120': 120, 'S240': 240, 'S180': 180}
for k in (1, 2, 3):
    mp = os.path.join(D, f'run{50 + k}_meta.json')
    if not os.path.exists(mp): print(f'read {k}: NOT FIRED / NOT LANDED (a row)'); continue
    m = json.load(open(mp)); z = np.load(os.path.join(D, f'run{50 + k}_results.npz')); L = lambda key: np.asarray(z[f'{key}__L1']).astype(complex)
    m0 = L('OFF|w0').mean(0); d = L('ON|w0').mean(0) - m0; al = lambda x: np.real((x - m0) * np.conj(d)) / np.abs(d) ** 2; ac = lambda x: np.imag((x - m0) * np.conj(d)) / np.abs(d) ** 2
    nsh = L('ON|w0').shape[0]; print(f"THE SIDES RUN, read {k}: ibm_pittsburgh, all {len(d)} bits, fired {m['start_time'][11:19]}, {nsh} shots")
    lev = {s: np.array([al(L(f'{s}|w{x}')).mean(0) for x in TW]) for s in ST}; err = {s: np.array([al(L(f'{s}|w{x}')).std(0, ddof=1) / np.sqrt(nsh) for x in TW]) for s in ST}
    kept = {s: lev[s] / lev[s][0] for s in ST}; wmid = lambda a: 1.2533 * np.nanstd(a) / np.sqrt(np.isfinite(a).sum())      # width of a middle value across the bits
    print('\n== LEVEL the one look reads (middle bit):        none      6.7       20      | across the line at none')
    for s in ST: print(f'   {s:<5}                                       ' + '   '.join(f'{med(lev[s][j]):.4f}' for j in range(3)) + f"   | {med(ac(L(f'{s}|w0')).mean(0)):+.4f}")
    print('\n== KEPT minus ON\'s kept, bit by bit (middle bit +- its width across the bits):     at 6.7 us            at 20 us')
    E = {}
    for s in ST[:-1]:
        e = [kept[s][j] - kept['ON'][j] for j in (1, 2)]; E[s] = e; print(f'   {s:<5}                                          ' + '      '.join(f'{med(x):+.4f} +- {wmid(x):.4f}' for x in e))
    print('\n== BOX 1, THE ANGLE: the four one-half-push sides against each other (middle bit of the bit-by-bit differences)')
    for a_, b_ in (('S120', 'S0'), ('S240', 'S0'), ('S240', 'S120'), ('S180', 'S0')):
        print(f'   {a_} minus {b_}:   6.7: {med(kept[a_][1] - kept[b_][1]):+.4f} +- {wmid(kept[a_][1] - kept[b_][1]):.4f}     20: {med(kept[a_][2] - kept[b_][2]):+.4f} +- {wmid(kept[a_][2] - kept[b_][2]):.4f}')
    # three sides fix a wave around the ring: offset, size, direction (per bit, then the middle; and from the middle values)
    for j, lab in ((1, '6.7'), (2, '20 ')):
        y = np.array([E[s][j - 1] for s in ('S0', 'S120', 'S240')]); th = np.radians([0, 120, 240])[:, None]
        off = y.mean(0); a = (2 / 3) * (y * np.cos(th)).sum(0); b = (2 / 3) * (y * np.sin(th)).sum(0); amp = np.hypot(a, b)
        am, bm = (2 / 3) * sum(med(E[s][j - 1]) * np.cos(np.radians(ANG[s])) for s in ('S0', 'S120', 'S240')), (2 / 3) * sum(med(E[s][j - 1]) * np.sin(np.radians(ANG[s])) for s in ('S0', 'S120', 'S240'))
        pred180 = np.mean([med(E[s][j - 1]) for s in ('S0', 'S120', 'S240')]) - am
        print(f'   around the ring at {lab} us: shared offset {med(off):+.4f}; wave size from the middle values {np.hypot(am, bm):.4f} at {np.degrees(np.arctan2(bm, am)) % 360:.0f} deg; bit by bit middle size {med(amp):.4f} (noise alone gives a positive size too);  what the three sides say S180 should read: {pred180:+.4f}; it reads {med(E["S180"][j - 1]):+.4f}')
    print('\n== BOX 2, THE PATH: FAR (full push + half-push) against S180 (same side by angle, one half-push), and against S0')
    for a_, b_ in (('FAR', 'S180'), ('FAR', 'S0')):
        print(f'   {a_} minus {b_}:   6.7: {med(kept[a_][1] - kept[b_][1]):+.4f} +- {wmid(kept[a_][1] - kept[b_][1]):.4f}     20: {med(kept[a_][2] - kept[b_][2]):+.4f} +- {wmid(kept[a_][2] - kept[b_][2]):.4f}     level at none: {med(lev[a_][0] - lev[b_][0]):+.4f} +- {wmid(lev[a_][0] - lev[b_][0]):.4f}')
    print('\n== BESIDE IT, the half-push run two hours earlier (3 reads): one-half-push minus ON -0.016 / -0.027;  far side minus ON +0.025 / +0.020;  far minus one-half-push +0.035 / +0.042')
    json.dump({s: {'lev': [med(x) for x in lev[s]], 'kept_minus_ON': [med(x) for x in E[s]] if s != 'ON' else None} for s in ST}, open(os.path.join(HERE, 'data', 'reads', f'sides_read{k}.json'), 'w'), indent=1)
