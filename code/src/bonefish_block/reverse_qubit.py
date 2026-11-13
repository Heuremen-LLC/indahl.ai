"""reverse_qubit.py -- 6 Oct 2026, Wayfinder and Bones. Bitcoin read with the qubit steps ("a reverse qubit: shake the change out of its pockets").
THREE SEATS: OBSERVER = the maker's stated length (the protocol: 2016 blocks x 600 s per epoch). WITNESS = the miners' own timestamps (the chain's
inside clock), read by TWO RULERS: (1) the timestamp span between retargets, (2) the chain's own verdict, the difficulty change it applied (new/old,
clamped 1/4..4). TIME = all 467 epochs since 2009, read by era. Then The Bonefish both ways and the cheap-match rate for every hit. Raw, public data."""
import json, math, numpy as np
PHI = (1 + 5 ** .5) / 2
SEVEN = {'12/11': 12/11, '13/12': 13/12, 'phi': PHI, '1/phi': 1/PHI, 'phi*11/12': PHI*11/12, 'pi': math.pi, '1/pi': 1/math.pi, '9/12': .75, '10/12': 10/12,
         '11/12': 11/12, '4/3': 4/3, '3/2': 1.5, '1/ln(phi^2)': 1/math.log(PHI**2), '1.3': 1.3, '12/13': 12/13, '1/phi^2': 1/PHI**2, '1': 1.0}
A = sorted(json.load(open('adj.json')), key=lambda r: r[1])          # [time, height, difficulty, change]
A = [r for r in A if r[1] > 0]
span = np.array([(b[0] - a[0]) / ((b[1] - a[1]) * 600) for a, b in zip(A, A[1:])])   # ruler 1: actual / stated, from timestamps
verdict = np.array([1 / b[3] for b in A[1:] if b[3] > 0])                              # ruler 2: what the chain itself concluded
t = np.array([b[0] for b in A[1:]]); yr = 1970 + t / 31557600
def mw(x): return np.mean(x), np.std(x, ddof=1) / len(x) ** .5, np.median(x)
def bonefish(v, w, label):
    hits = sorted(((abs(v - s) / w, k, s) for k, s in SEVEN.items()), key=lambda h: h[0])[:3]
    print(f'   {label}: ' + ' | '.join(f'{k} {s:.4f} at {d:.1f} widths' for d, k, s in hits))
print(f'{len(span)} epochs (timestamp ruler), {len(verdict)} (chain-verdict ruler), {yr[0]:.1f}-{yr[-1]:.1f}')
for name, lo, hi in (('ALL', 0, 3000), ('CPU/GPU 2009-2012', 0, 2013), ('early ASIC 2013-2016', 2013, 2017), ('2017-2020', 2017, 2021), ('2021-now', 2021, 3000)):
    m = (yr >= lo) & (yr < hi); a = mw(span[m]); b = mw(verdict[:len(span)][m[:len(verdict)]])
    print(f'{name:22} n={m.sum():3d} | timestamps W/O mean {a[0]:.4f} +- {a[1]:.4f} (median {a[2]:.4f}) | chain verdict mean {b[0]:.4f} +- {b[1]:.4f} (median {b[2]:.4f})')
    bonefish(a[0], a[1], 'forward, timestamps')
r = span[:len(verdict)] / verdict[:len(span)]
print(f'RULER vs RULER (timestamps / verdict, same epochs): mean {r.mean():.6f}, median {np.median(r):.6f} -- the protocol counts 2015 gaps for a 2016-block epoch: 2016/2015 = {2016/2015:.6f}')
# backward: what would each Seven number predict for the epoch length, and how many epochs land within one width of it (vs a flat ruler)
print('BACKWARD (2021-now): share of epochs within +-0.3 % of each number, beside the share expected from the epochs\' own spread (shuffled offsets):')
m = yr >= 2021; x = span[m]; rng = np.random.default_rng(6)
for k in ('12/11', '11/12', '1', '12/13', '1/ln(phi^2)', '13/12'):
    s = SEVEN[k]; obs = np.mean(np.abs(x / s - 1) < .003)
    null = np.mean([np.mean(np.abs((x * rng.uniform(.9, 1.1)) / s - 1) < .003) for _ in range(400)])
    print(f'   {k:12} {obs:.3f} (flat-shift ruler {null:.3f})')
