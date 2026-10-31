# Data for Santos and Uzdin (arXiv 2506.11270)

## The question in your paper

Your scheme scales the delay for the measured and the spectator qubits, so the degradation from that delay is "automatically mitigated" for the spectators. A phase on a spectator is invisible to a computational-basis check. The question here is what repeated readouts do to the phase of untouched qubits beyond an equal delay.

## What was run

On 24 October 2026 on ibm_fez, your 20-qubit set 0-19 was read out N = 1, 3, 5, 7, 13 times, against an equal idle and with your 1 us delay between rounds. Eleven untouched neighbours were prepared in |+> and read in X and Y. Jobs dbebthfgdj9s73flgpqg and dbebu70m94ac738rhstg, 74 s each.
On 31 October 2026 on ibm_kingston and ibm_marrakesh, a 39-qubit pack was read out 8 times beside 117 untouched qubits, against an equal idle (arms D and M). The same readout was run with a per-qubit virtual-Z correction, MC from the 21 October table and MF from a table measured minutes earlier, and with an echo, ME. Jobs dbj3p3onceqs73aj79k0 and dbj3prt6p51s73ck1v30 (kingston), dbj3p4hffo6c73b8sc5g and dbj3pthkdqps738vqbqg (marrakesh).

## What it shows

Fez, degrees per readout (RESULT_HEBREW.md.text): readout minus equal idle -2.369 [-5.807, -1.134] BELOW. With your 1 us delay -2.266 [-5.617, -1.026] BELOW. Delay effect -0.093 [-0.190, +0.070] CONSISTENT. Coherence per readout +0.0003 [-0.0021, +0.0021] CANNOT_TELL. P(1) of the |1> qubits at N = 13: M 0.807, D 0.806.
31 October, M kick, readout minus equal idle (results files): kingston -2.4240 [-3.9835, -1.9317] BELOW, marrakesh -1.6830 [-2.3377, -1.0173] BELOW.
Share of that kick given back, against 0.5: kingston MC +0.9221 [+0.8734, +0.9479] ABOVE, MF +0.9281 [+0.8738, +0.9538] ABOVE, ME +0.9495 [+0.9119, +0.9713] ABOVE. Marrakesh MC +0.2426 [-0.1420, +0.4365] BELOW, MF +0.7952 [+0.6656, +0.8764] ABOVE, ME +0.9059 [+0.8375, +0.9450] ABOVE.

## What it does not show

The coherence change per readout is not decided at this resolution. The 20-qubit set and the 39-qubit pack differ in layout, so no dose curve is drawn between them. No cause is named.

## Files

- Fez: [result](../earlier_runs/2026-10-24-hebrew-university-set/RESULT_HEBREW.md.text), [raw_hebrew_J0.npz](../earlier_runs/2026-10-24-hebrew-university-set/raw_hebrew_J0.npz), [raw_hebrew_J1.npz](../earlier_runs/2026-10-24-hebrew-university-set/raw_hebrew_J1.npz), [circuits_hebrew.qpy](../earlier_runs/2026-10-24-hebrew-university-set/circuits_hebrew.qpy), [job_hebrew.json](../earlier_runs/2026-10-24-hebrew-university-set/job_hebrew.json)
- 31 October: [kingston](../run/results/results_keystone_ibm_kingston.text) and [marrakesh](../run/results/results_keystone_ibm_marrakesh.text) results, raw arrays in [run/data](../run/data/)
- Loading: the fez .npz arrays are boolean, fin_i has shots by bits, column k is bit k, with meta[i] in job_hebrew.json giving arm, N and setting. The run/data .npz arrays are IBM BitArray bytes, bit k at byte nby-1-k//8, position k%8. Circuits load with qiskit.qpy.

Heuremen LLC
