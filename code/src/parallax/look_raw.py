"""Look at the odd-half raw dots without counting: one picture of every qubit's readout (the fishtank wall), plus close-ups of
the ones whose dots land where neither 0 nor 1 lives."""
import sys, os, json
import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
d = sys.argv[1]; M = json.load(open(os.path.join(d, 'meta.json'))); R = np.load(os.path.join(d, 'raw.npz')); Q = M['qubits']; W = M['waits_us']
BLUE, RUST, GREY = '#1f5f8b', '#8a3b12', '#6b6b66'
def geo(k):
    z0, z1 = R['P0_0'][:, k], R['P1_0'][:, k]; c0, c1 = np.median(z0), np.median(z1)
    c0 = complex(np.median(z0.real), np.median(z0.imag)); c1 = complex(np.median(z1.real), np.median(z1.imag)); a = c1 - c0
    t = lambda z: ((z - c0) * np.conj(a)).real / abs(a) ** 2; p = lambda z: ((z - c0) * np.conj(a)).imag / abs(a) ** 2
    mad = lambda x: 1.4826 * np.median(np.abs(x - np.median(x))); s = max(mad(t(z0)), mad(p(z0)), 1e-9)
    return t, p, s
def elsewhere(k, z):
    t, p, s = geo(k); tt, pp = t(z), p(z); return (np.abs(pp) > 6 * s) | (tt < -6 * s) | (tt > 1 + 6 * s)
score = []
for k, q in enumerate(Q):
    base = max(elsewhere(k, R['P0_0'][:, k]).mean(), elsewhere(k, R['P1_0'][:, k]).mean())
    ram = max(elsewhere(k, R[f'{qd}_{w}'][:, k]).mean() for w in W for qd in ('X', 'Y'))
    score.append((ram - base, q, k))
score.sort(reverse=True)
fig, axs = plt.subplots(8, 10, figsize=(20, 16), facecolor='#fbfaf6')
for ax in axs.flat: ax.axis('off')
for n, (k, q) in enumerate(zip(range(len(Q)), Q)):
    ax = axs.flat[n]; ax.set_facecolor('#fbfaf6'); z = R['X_5'][:, k]
    ax.scatter(R['P0_0'][:, k].real, R['P0_0'][:, k].imag, s=1, c=BLUE, alpha=.25, lw=0)
    ax.scatter(R['P1_0'][:, k].real, R['P1_0'][:, k].imag, s=1, c=RUST, alpha=.25, lw=0)
    ax.scatter(z.real, z.imag, s=1, c=GREY, alpha=.15, lw=0); ax.set_title(f'q{q}', fontsize=9, color='#1d1d1b'); ax.set_xticks([]); ax.set_yticks([]); ax.axis('on')
    for sp in ax.spines.values(): sp.set_color('#dcd9d0')
fig.suptitle('The odd half of ibm_fez, raw readout dots.  Blue: told to be 0.  Rust: told to be 1.  Grey: half-and-half, after a 5 us wait.', fontsize=14, color='#1d1d1b')
fig.savefig(os.path.join(d, 'fishtank_wall.png'), dpi=90, facecolor=fig.get_facecolor(), bbox_inches='tight')
top = [x for x in score[:4]]
fig, axs = plt.subplots(1, len(top), figsize=(5 * len(top), 5), facecolor='#fbfaf6')
for ax, (sc, q, k) in zip(np.atleast_1d(axs), top):
    ax.set_facecolor('#fbfaf6'); w = max(W, key=lambda w: elsewhere(k, R[f'X_{w}'][:, k]).mean()); z = R[f'X_{w}'][:, k]; e = elsewhere(k, z)
    ax.scatter(R['P0_0'][:, k].real, R['P0_0'][:, k].imag, s=2, c=BLUE, alpha=.3, lw=0, label='told 0')
    ax.scatter(R['P1_0'][:, k].real, R['P1_0'][:, k].imag, s=2, c=RUST, alpha=.3, lw=0, label='told 1')
    ax.scatter(z[~e].real, z[~e].imag, s=2, c=GREY, alpha=.2, lw=0, label=f'half-and-half, {w} us')
    ax.scatter(z[e].real, z[e].imag, s=6, c='#000000', alpha=.8, lw=0, label='landed nowhere')
    ax.set_title(f'q{q}', color='#1d1d1b'); ax.set_xticks([]); ax.set_yticks([]); ax.legend(fontsize=8, markerscale=4, frameon=False)
fig.savefig(os.path.join(d, 'nowhere_closeups.png'), dpi=100, facecolor=fig.get_facecolor(), bbox_inches='tight')
json.dump([{'q': q, 'excess_elsewhere': float(sc)} for sc, q, k in score], open(os.path.join(d, 'elsewhere.json'), 'w'), indent=1)
print('top', [(q, round(sc, 3)) for sc, q, k in score[:8]]); print('saved', d)
