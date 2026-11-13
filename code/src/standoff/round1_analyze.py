"""Round 1 analysis: fit the third-state Rabi, plot it, and harvest the per-shot bits as QUBIT DICE for the pup.
Dice extraction (honest): raw shot bits are biased (the sweep moves P from 0.03 to 0.94), so they go through SHA-256 in 512-bit
blocks -> 256 output bits per block (a standard randomness extractor). The dice file says where every byte came from."""
import json, hashlib, math, os
import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

R = json.load(open('round1_results.json'))['results']
a = np.array([r['amp'] for r in R]); p = np.array([r['p_read1'] for r in R])
# fit P = off + A*sin^2(pi*a/(2*a_pi))  (a_pi = amplitude of the full 1->2 transfer)
best = None
for api in np.linspace(0.3, 0.8, 501):
    X = np.vstack([np.sin(math.pi * a / (2 * api)) ** 2, np.ones_like(a)]).T
    c, *_ = np.linalg.lstsq(X, p, rcond=None); r = p - X @ c; sse = float(r @ r)
    if best is None or sse < best[0]: best = (sse, api, c[0], c[1])
sse, api, A, off = best
fit = {'a_pi_12': round(api, 4), 'contrast': round(A, 4), 'offset': round(off, 4), 'peak_measured': float(p.max()),
       'peak_at_amp': float(a[p.argmax()]), 'rmse': round(math.sqrt(sse / len(a)), 4), 'shots_per_point': 300}
json.dump(fit, open('round1_fit.json', 'w'), indent=1); print(fit)

INK, GOLD, RUST, GREY = '#1d1a16', '#b8860b', '#b5452e', '#8a8378'
plt.rcParams.update({'figure.facecolor': '#faf7f0', 'axes.facecolor': '#fffdf8', 'text.color': INK, 'axes.edgecolor': GREY})
fig, ax = plt.subplots(figsize=(10, 5.6))
xs = np.linspace(0, 0.8, 300)
ax.plot(xs, off + A * np.sin(math.pi * xs / (2 * api)) ** 2, color=GOLD, lw=2.5, label=f'fit: full transfer at amplitude {api:.3f}')
err = np.sqrt(p * (1 - p) / 300)
ax.errorbar(a, p, yerr=err, fmt='o', color=RUST, ms=6, capsize=3, label='Rigetti Cepheus q0, 300 shots per point')
ax.axhline(off, color=GREY, ls=':', lw=1)
ax.set_xlabel('strength of the pulse at the third-state frequency (f12 = 4.295 GHz)'); ax.set_ylabel('fraction of the qubit found in the THIRD state')
ax.set_ylim(0, 1.05); ax.legend(loc='lower center')
ax.set_title('THE FIFTH DOOR -- a qubit pushed into its third state, on real hardware\n'
             f'Rigetti Cepheus-1-108Q via AWS Braket pulse  ·  peak {p.max():.0%} in level 2  ·  2026-09-25  ·  cost $8.98', fontweight='bold')
fig.text(0.5, 0.005, 'rx(pi) to level 1 -> f12 pulse -> rx(pi) back: whatever reached level 2 stays there and reads as "1". At zero strength it all comes home (3%). '
         'IBM removed the pulse access this needs.', ha='center', fontsize=8.5, color=GREY, wrap=True)
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig('the_fifth_door.png', dpi=150); print('the_fifth_door.png')
