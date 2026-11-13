"""The other side of the tank. For every odd qubit: a half-and-half qubit, once read, should land as some mix of 'told 0' dots and
'told 1' dots. Subtract that mix from what actually landed (all 24 waits pooled). What's left over is the other side:
HOLES = places the dots should have gone and didn't (blue); EXTRAS = places nobody sent them (rust). Template noise included."""
import sys, os, json
import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
d = sys.argv[1]; M = json.load(open(os.path.join(d, 'meta.json'))); R = np.load(os.path.join(d, 'raw.npz')); Q = M['qubits']; W = M['waits_us']
KEYS = [f'{qd}_{w}' for w in W for qd in ('X', 'Y')]; NB = 14
def zmap(k):
    z0, z1 = R['P0_0'][:, k], R['P1_0'][:, k]; allz = np.concatenate([z0, z1] + [R[c][:, k] for c in KEYS])
    xe = np.linspace(*np.percentile(allz.real, [0.2, 99.8]), NB + 1); ye = np.linspace(*np.percentile(allz.imag, [0.2, 99.8]), NB + 1)
    H = lambda z: np.histogram2d(z.real, z.imag, [xe, ye])[0]
    H0, H1 = H(z0), H(z1); n0, n1 = len(z0), len(z1); h0, h1 = H0 / n0, H1 / n1
    A = np.zeros_like(H0); E = np.zeros_like(H0); S0 = S1 = 0.0
    for c in KEYS:
        Ac = H(R[c][:, k]); N = Ac.sum()
        a = np.clip(np.sum((Ac / N - h1) * (h0 - h1)) / max(np.sum((h0 - h1) ** 2), 1e-12), 0, 1)
        A += Ac; E += N * (a * h0 + (1 - a) * h1); S0 += N * a; S1 += N * (1 - a)
    var = E + S0 ** 2 * H0 / n0 ** 2 + S1 ** 2 * H1 / n1 ** 2 + 1
    return (A - E) / np.sqrt(var), xe, ye, H0, H1
Z = {}; out = []
for k, q in enumerate(Q):
    z, xe, ye, H0, H1 = zmap(k); Z[q] = (z, xe, ye, H0, H1); out.append({'q': q, 'deepest_hole': float(z.min()), 'biggest_extra': float(z.max())})
json.dump(out, open(os.path.join(d, 'other_side.json'), 'w'), indent=1)
cm = matplotlib.colors.LinearSegmentedColormap.from_list('bw', ['#1f5f8b', '#fbfaf6', '#8a3b12'])
fig, axs = plt.subplots(8, 10, figsize=(20, 16), facecolor='#fbfaf6')
for ax in axs.flat: ax.axis('off')
for n, q in enumerate(Q):
    z, xe, ye, H0, H1 = Z[q]; ax = axs.flat[n]; ax.axis('on')
    ax.imshow(np.clip(z.T, -6, 6), origin='lower', cmap=cm, vmin=-6, vmax=6, aspect='auto', interpolation='nearest')
    ax.contour((H0 + H1).T, levels=[max((H0 + H1).max() * .15, 1)], colors='#6b6b66', linewidths=.6)
    ax.set_title(f'q{q}', fontsize=9, color='#1d1d1b'); ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_color('#dcd9d0')
fig.suptitle('The other side of the tank (odd half, ibm_fez). Blue: dots should have landed here and did not. Rust: dots landed where nobody sent them.\nGrey rings: where "told 0" and "told 1" live. White: exactly as expected.', fontsize=13, color='#1d1d1b')
fig.savefig(os.path.join(d, 'other_side_wall.png'), dpi=90, facecolor=fig.get_facecolor(), bbox_inches='tight')
print('deepest holes', sorted([(round(o['deepest_hole'], 1), o['q']) for o in out])[:6]); print('biggest extras', sorted([(round(o['biggest_extra'], 1), o['q']) for o in out])[-6:])
