"""THE STANDOFF poster -- one page, five doors, every number from standoff_results.json. Light theme. SIMULATION stamped."""
import json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import textwrap
def W(t, n=62): return '\n'.join(textwrap.wrap(t, n))

R = json.load(open('standoff_results.json'))
I, N = R['doors']['ideal'], R['doors'].get('fez-noise', R['doors']['ideal'])
INK, GOLD, RUST, TEAL, GREY = '#1d1a16', '#b8860b', '#b5452e', '#2e7d7a', '#8a8378'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'text.color': INK, 'axes.labelcolor': INK, 'xtick.color': INK, 'ytick.color': INK,
                     'axes.edgecolor': GREY, 'figure.facecolor': '#faf7f0', 'axes.facecolor': '#fffdf8'})
fig = plt.figure(figsize=(16, 10))
fig.suptitle('THE STANDOFF  --  three bodies, four ways out, and the answer sheet that cannot exist',
             fontsize=19, fontweight='bold', y=0.985)
fig.text(0.5, 0.945, "Wayfinder's four solutions to the Mexican standoff, run as qubit experiments.   "
         "SIMULATION: ideal + IBM Fez noise model  |  hardware run pre-registered  |  receipts: standoff_results.json",
         ha='center', fontsize=10.5, color=GREY)
gs = fig.add_gridspec(2, 3, hspace=0.55, wspace=0.28, left=0.05, right=0.98, top=0.9, bottom=0.09)

# Door 0
ax = fig.add_subplot(gs[0, 0])
vals = [2, I['door0_standoff']['M'], N['door0_standoff']['M']]
bars = ax.bar(['classical\nanswer sheet\n(max)', 'quantum\n(ideal)', 'IBM Fez\nnoise model'], vals, color=[GREY, GOLD, RUST])
ax.axhline(2, color=GREY, ls='--', lw=1); ax.set_ylim(0, 4.6)
for b, v in zip(bars, vals): ax.text(b.get_x() + b.get_width() / 2, v + 0.08, f'{v:.2f}', ha='center', fontweight='bold')
ax.set_title('DOOR 0 · THE STANDOFF\n"what if there is no outcome?"', fontweight='bold', fontsize=11)
ax.set_ylabel('Mermin score')
ax.text(0.5, -0.36, W(f"Above 2 = no pre-written answers exist.  No-outcome floor (forbidden results): "
        f"{I['door0_standoff']['forbidden_fraction']:.1%} ideal, {N['door0_standoff']['forbidden_fraction']:.1%} noisy"),
        transform=ax.transAxes, ha='center', fontsize=8.5, color=GREY, wrap=True)

# Door 1
ax = fig.add_subplot(gs[0, 1])
x = np.arange(3); w = 0.36
iv = [I['door1_blondie'][b]['found_in_box_given_kept'] for b in 'ABC']
nv = [N['door1_blondie'][b]['found_in_box_given_kept'] for b in 'ABC']
ax.bar(x - w / 2, iv, w, color=GOLD, label='ideal'); ax.bar(x + w / 2, nv, w, color=RUST, label='Fez noise')
ax.set_xticks(x); ax.set_xticklabels(['look in A', 'look in B', 'look in C']); ax.set_ylim(0, 1.15)
for i, (a, b) in enumerate(zip(iv, nv)):
    ax.text(i - w / 2, a + 0.02, f'{a:.2f}', ha='center', fontsize=8.5); ax.text(i + w / 2, b + 0.02, f'{b:.2f}', ha='center', fontsize=8.5)
ax.set_title('DOOR 1 · BLONDIE\nrig the ending, keep it looking like a standoff', fontweight='bold', fontsize=11)
ax.set_ylabel('ball found in that box (rigged runs)'); ax.legend(fontsize=8, loc='upper right')
ax.text(0.5, -0.36, W(f"Look in A: always there. Look in B: always there. Price of the rig: only "
        f"{N['door1_blondie']['A']['kept_fraction']:.0%} of runs survive -- published, not hidden. Three boxes in two qubits."),
        transform=ax.transAxes, ha='center', fontsize=8.5, color=GREY)

# Door 2
ax = fig.add_subplot(gs[0, 2])
lab = ['in tune\n(ideal)', 'in tune\n(Fez)', 'by force\n(ideal)', 'by force\n(Fez)']
v2 = [I['door2_recruit']['in_tune']['bell_fidelity'], N['door2_recruit']['in_tune']['bell_fidelity'],
      I['door2_recruit']['by_force']['bell_fidelity'], N['door2_recruit']['by_force']['bell_fidelity']]
bars = ax.bar(lab, v2, color=[GOLD, RUST, GREY, '#b9b2a6']); ax.axhline(0.5, color=INK, ls='--', lw=1); ax.set_ylim(0, 1.15)
for b, v in zip(bars, v2): ax.text(b.get_x() + b.get_width() / 2, v + 0.02, f'{v:.2f}', ha='center', fontsize=9)
ax.set_title('DOOR 2 · RECRUIT\nmatch the frequency, take one with you', fontweight='bold', fontsize=11)
ax.set_ylabel('the two left behind: pair fidelity')
ax.text(0.5, -0.36, W('Above the dashed line = the two remaining bodies are locked together. Measure the third IN TUNE and they pair; by FORCE and they split.'),
        transform=ax.transAxes, ha='center', fontsize=8.5, color=GREY)

# Door 3
ax = fig.add_subplot(gs[1, 0:2])
c = N['door3_pinata']['curves']; ci = I['door3_pinata']['curves']
th = np.array(c['theta'])
ax.plot(th, ci['standoff'], color=GOLD, lw=2, label='the standoff (3 bodies), ideal')
ax.plot(th, c['standoff'], 'o', color=RUST, ms=5, label='the standoff, Fez noise')
ax.plot(th, ci['lone'], color=TEAL, lw=2, ls='--', label='one lone qubit (control), ideal')
ax.set_xlabel('the nudge (same phase turn on every body)'); ax.set_ylabel('signal')
ax.set_xticks([0, math.pi / 2, math.pi, 3 * math.pi / 2, 2 * math.pi]); ax.set_xticklabels(['0', 'π/2', 'π', '3π/2', '2π'])
ax.set_title(f"DOOR 3 · PIÑATA  --  change the frequency: the standoff swings {N['door3_pinata']['standoff']['frequency']}× as fast as one lone qubit",
             fontweight='bold', fontsize=11)
ax.legend(fontsize=8.5, loc='lower left', ncol=3)

# Door 4
ax = fig.add_subplot(gs[1, 2])
v4 = [I['door4_six_bodies']['fidelity'], N['door4_six_bodies']['fidelity']]
bars = ax.bar(['6 bodies\n(ideal)', '6 bodies\n(Fez noise)'], v4, color=[GOLD, RUST]); ax.axhline(0.5, color=INK, ls='--', lw=1)
ax.set_ylim(0, 1.15)
for b, v in zip(bars, v4): ax.text(b.get_x() + b.get_width() / 2, v + 0.02, f'{v:.2f}', ha='center', fontweight='bold')
ax.set_title('DOOR 4 · THREE MORE BODIES\nbinary\'s little bitch, no longer', fontweight='bold', fontsize=11)
ax.set_ylabel('6-body standoff fidelity')
ax.text(0.5, -0.36, W('Above 0.5 = a genuine six-way standoff, certified -- not two threes faking it.'),
        transform=ax.transAxes, ha='center', fontsize=8.5, color=GREY)

fig.text(0.5, 0.008, W("The third state -- a qubit's third energy level -- is the one door not built: IBM removed the pulse access it needs. "
         "Door 1 fakes three states with two qubits. Give us pulse access and the fifth door opens.   Heurémen · Bones & Wayfinder · 2026-09-25", 170),
         ha='center', fontsize=9.5, style='italic', color=INK)
fig.savefig('the_standoff.png', dpi=150)
print('the_standoff.png')
