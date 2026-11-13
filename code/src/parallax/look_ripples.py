"""Look at the ripples: each pond qubit drawn as an arrow on a circle (where its superposition points, how long the arrow is),
split by what the stone showed (blue: stone read 0, rust: stone read 1). Top row: stone looked at FIRST. Bottom: LAST.
0/1 lines built on half the references, checked on the other half first (the Do)."""
import sys, os, json
import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
d = sys.argv[1]; M = json.load(open(os.path.join(d, 'meta.json'))); R = np.load(os.path.join(d, 'raw.npz')); pond = M['pond']; stone = M['stone']; H = M['shots'] // 2
def line(z0, z1):
    c0 = complex(np.median(z0[:H].real), np.median(z0[:H].imag)); c1 = complex(np.median(z1[:H].real), np.median(z1[:H].imag)); a = c1 - c0
    f = lambda z: ((z - c0) * np.conj(a)).real / abs(a) ** 2 > .5
    return f, (float(np.mean(f(z0[H:]))), float(np.mean(~f(z1[H:]))))
fs, chk_s = line(R['P0_0_-_s'][:, 0], R['P1_0_-_s'][:, 0]); fb, chk = [], [chk_s]
for k in range(6):
    f, c = line(R['P0_0_-_b'][:, k], R['P1_0_-_b'][:, k]); fb.append(f); chk.append(c)
print('cut check (misfiled told0, told1) stone first, then pond:', [(round(a, 3), round(b, 3)) for a, b in chk])
res = {}
for arm in ('first', 'last'):
    for w in M['waits_us']:
        s = fs(R[f'{arm}_{w}_X_s'][:, 0]), fs(R[f'{arm}_{w}_Y_s'][:, 0])
        for k, q in enumerate(pond):
            v = {}
            for sv in (0, 1):
                ex = [1 - 2 * np.mean(fb[k](R[f'{arm}_{w}_{qd}_b'][:, k])[s[n] == sv]) for n, qd in enumerate(('X', 'Y'))]
                v[sv] = ex
            allv = [1 - 2 * np.mean(fb[k](R[f'{arm}_{w}_{qd}_b'][:, k])) for qd in ('X', 'Y')]
            res[(arm, w, q)] = (v, allv)
dist = {q: abs(M['chain'].index(q) - M['chain'].index(stone)) for q in pond}
for w in M['waits_us']:
    fig, axs = plt.subplots(2, 6, figsize=(20, 7.6), facecolor='#fbfaf6')
    for i, arm in enumerate(('first', 'last')):
        for j, q in enumerate(pond):
            ax = axs[i, j]; ax.set_facecolor('#fbfaf6'); th = np.linspace(0, 2 * np.pi, 200); ax.plot(np.cos(th), np.sin(th), c='#dcd9d0', lw=1)
            v, allv = res[(arm, w, q)]
            for sv, col in ((0, '#1f5f8b'), (1, '#8a3b12')):
                ax.annotate('', xy=(v[sv][0], v[sv][1]), xytext=(0, 0), arrowprops=dict(arrowstyle='->', color=col, lw=2.2))
            ax.set_xlim(-1.15, 1.15); ax.set_ylim(-1.15, 1.15); ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([])
            for sp in ax.spines.values(): sp.set_color('#dcd9d0')
            ax.set_title(f'q{q}, {dist[q]} step{"s" if dist[q] > 1 else ""} from the stone', fontsize=10, color='#1d1d1b')
        axs[i, 0].set_ylabel('stone looked at FIRST' if arm == 'first' else 'stone looked at LAST', fontsize=12, color='#1d1d1b')
    fig.suptitle(f'Skip a stone: the pond around q{stone} (ibm_fez), {w} us after the stone moment. Blue arrow: the stone read 0. Rust: the stone read 1.\nArrows apart = the pond knows what the stone showed. Arrow shorter = the pond lost some of its superposition.', fontsize=13, color='#1d1d1b')
    fig.savefig(os.path.join(d, f'ripples_{w}us.png'), dpi=85, facecolor=fig.get_facecolor(), bbox_inches='tight')
for key, (v, allv) in res.items():
    ang = np.degrees(np.angle(complex(*v[1]) / complex(*v[0]))) if abs(complex(*v[0])) > 0.05 and abs(complex(*v[1])) > 0.05 else float('nan')
    print(key, 'dist', dist[key[2]], 'len s0 %.2f s1 %.2f all %.2f | split angle %5.1f deg' % (abs(complex(*v[0])), abs(complex(*v[1])), abs(complex(*allv)), ang))
