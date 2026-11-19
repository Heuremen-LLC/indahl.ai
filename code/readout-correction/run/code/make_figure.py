"""make_figure.py -- Fig. 1 of the paper: per untouched qubit, the residual phase per readout of each corrected arm against the look's kick,
pooled copies, both chips. Plots the same per-qubit values the committed readers use (keystone.read_S); no new reading."""
import sys, os, json, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import keystone as K
rng = np.random.default_rng(0)
fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.2), sharey=True)
style = {'MC': ('ten-day table', 'o', '#d95f02'), 'MF': ('fresh table', 's', '#1b9e77'), 'ME': ('echo', '^', '#7570b3')}
for ax, chip in zip(axes, ('ibm_kingston', 'ibm_marrakesh')):
    job = json.load(open(f'{HERE}/job_keystone_{chip}.json')); keys = [tuple(k) for k in job['keys']]
    Z = {lab: np.load(f'{HERE}/raw_keystone_{chip}_{lab}.npz') for lab in ('A', 'B')}
    S = [int(q) for q in K.table(chip)['S']]
    Zc = {(k[1], k[2]): [Z['A'][f'fin_{keys.index(k)}'], Z['B'][f'fin_{keys.index(k)}']] for k in keys if k[0] == 'S'}
    r = K.read_S(Zc, S, rng); x = r['M']['kick']
    lim = 23
    ax.plot([-lim, lim], [-lim, lim], color='0.6', lw=0.8, ls='--', label='no correction (residual = kick)')
    ax.axhline(0, color='0.3', lw=0.6)
    for a, (lab, m, c) in style.items():
        ax.scatter(x, r[a]['kick'], s=9, marker=m, facecolors='none', edgecolors=c, linewidths=0.7, label=lab)
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_xlabel('kick of the look (deg per readout)')
    ax.set_title(chip, fontsize=9)
axes[0].set_ylabel('residual after correction (deg per readout)')
axes[0].legend(fontsize=6.5, loc='upper left', frameon=False)
fig.tight_layout(); fig.savefig(os.path.expanduser('~/bones-forge/arxiv_keystone/paper/fig1.pdf')); fig.savefig(f'{HERE}/fig1.png', dpi=150)
outside = {chip: None for chip in ()}
print('ok')
