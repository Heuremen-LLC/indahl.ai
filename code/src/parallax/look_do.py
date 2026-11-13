"""Look at THE DO: two looks per shot, drawn as a picture. x = where the first look put the dot (0 side -> 1 side),
y = where the second look put it. Both-say-1 (top right) = really there (the tank). Looks disagree (off the diagonal) = the lens.
The 0/1 line is built on HALF the references and checked on the other half before it's used for anything."""
import sys, os, json
import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
d = sys.argv[1]; M = json.load(open(os.path.join(d, 'meta.json'))); R = np.load(os.path.join(d, 'raw.npz')); QS = M['qubits']; H = M['shots'] // 2
BLUE, RUST, GREY = '#1f5f8b', '#8a3b12', '#6b6b66'
fig, axs = plt.subplots(len(QS), 4, figsize=(18, 4.6 * len(QS)), facecolor='#fbfaf6'); checks = []
names = {113: 'seat 113 (cursed)', 72: 'seat 72 (cursed)', 27: 'seat 27 (clean)'}
for i, q in enumerate(QS):
    z0, z1 = R['P0_0_m1'][:, i], R['P1_0_m1'][:, i]
    c0 = complex(np.median(z0[:H].real), np.median(z0[:H].imag)); c1 = complex(np.median(z1[:H].real), np.median(z1[:H].imag)); a = c1 - c0
    t = lambda z: ((z - c0) * np.conj(a)).real / abs(a) ** 2
    checks.append((q, float(np.mean(t(z0[H:]) > .5)), float(np.mean(t(z1[H:]) < .5))))   # the check, on the half the line never saw
    ax = axs[i, 0]; ax.scatter(z0.real, z0.imag, s=2, c=BLUE, alpha=.3, lw=0, label='told 0'); ax.scatter(z1.real, z1.imag, s=2, c=RUST, alpha=.3, lw=0, label='told 1')
    ax.set_title(f'{names[q]}: raw dots, first look', fontsize=11); ax.legend(frameon=False, markerscale=4, fontsize=9)
    for j, (key, lab, col) in enumerate((('P0_0', 'told 0', BLUE), ('P1_0', 'told 1', RUST), ('X_5', 'half-and-half, 5 us', GREY))):
        ax = axs[i, j + 1]; x, y = t(R[f'{key}_m1'][:, i]), t(R[f'{key}_m2'][:, i])
        ax.scatter(x, y, s=3, c=col, alpha=.35, lw=0); ax.axvline(.5, c='#dcd9d0', lw=1); ax.axhline(.5, c='#dcd9d0', lw=1)
        ax.set_xlim(-1, 2); ax.set_ylim(-1, 2); ax.set_title(f'{names[q]}: {lab}', fontsize=11)
        ax.set_xlabel('first look  (0 side -> 1 side)', fontsize=9); ax.set_ylabel('second look', fontsize=9)
        ax.text(1.95, 1.95, 'both looks say 1\n(the tank)', ha='right', va='top', fontsize=8, color='#1d1d1b')
        ax.text(1.95, -0.95, 'first 1, second 0\n(lens, or it fell)', ha='right', va='bottom', fontsize=8, color='#1d1d1b')
        ax.text(-0.95, 1.95, 'first 0, second 1\n(lens, or it jumped)', ha='left', va='top', fontsize=8, color='#1d1d1b')
    for ax in axs[i]:
        ax.set_facecolor('#fbfaf6'); ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values(): sp.set_color('#dcd9d0')
fig.suptitle('THE DO, ibm_fez, 2026-09-28: every shot looked at twice. Order pinned, no guess, no fit, same-size rulers, cut checked first.', fontsize=14, color='#1d1d1b')
fig.savefig(os.path.join(d, 'the_do.png'), dpi=85, facecolor=fig.get_facecolor(), bbox_inches='tight')
json.dump([{'q': q, 'cut_check_told0_read1': a, 'cut_check_told1_read0': b} for q, a, b in checks], open(os.path.join(d, 'cut_check.json'), 'w'), indent=1)
print('cut check (on the half the line never saw):', [(q, round(a, 3), round(b, 3)) for q, a, b in checks])
