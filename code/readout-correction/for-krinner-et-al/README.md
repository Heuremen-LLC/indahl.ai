# Data for Krinner et al. (Nature 605, 669, 2022)

## The question in your paper

Your appendix reports a coherent phase rotation on qubits that were not read out and expects it could be corrected with virtual-Z "rotations of equal magnitude and opposite sign". The question here is how much of the phase that correction gives back on a current device, from a table ten days old and from a table minutes old, beside an echo.

## What was run

On 31 October 2026 on ibm_kingston and ibm_marrakesh, a 39-qubit pack was read out beside 117 untouched qubits (8 readouts), 48 Bell pairs (4 readouts) and a three-qubit clock (4 readouts mid-build). After every readout step each untouched qubit got a Z rotation of minus its measured kick, with no qubit dropped. MC uses the 21 October table, MF a table measured minutes earlier in the same session, ME the readout plus an echo. Kingston jobs dbj3p3onceqs73aj79k0 and dbj3prt6p51s73ck1v30, marrakesh jobs dbj3p4hffo6c73b8sc5g and dbj3pthkdqps738vqbqg.

## What it shows

Share given back, against 0.5, from results_keystone_ibm_kingston.text and results_keystone_ibm_marrakesh.text.
Kingston spectators: MC +0.9221 [+0.8734, +0.9479] ABOVE, MF +0.9281 [+0.8738, +0.9538] ABOVE, ME +0.9495 [+0.9119, +0.9713] ABOVE.
Kingston pair phase: MC +0.9266 [+0.8362, +0.9627] ABOVE, MF +0.9619 [+0.9175, +0.9749] ABOVE, ME +0.9856 [+0.9715, +0.9912] ABOVE.
Kingston clock: MC +0.7591 [+0.7344, +0.7840] ABOVE, MF +1.0007 [+0.9965, +1.0047] ABOVE, ME +0.9998 [+0.9960, +1.0037] ABOVE.
Marrakesh spectators: MC +0.2426 [-0.1420, +0.4365] BELOW, MF +0.7952 [+0.6656, +0.8764] ABOVE, ME +0.9059 [+0.8375, +0.9450] ABOVE.
Marrakesh pair phase: MC +0.3958 [+0.1553, +0.6416] CONSISTENT, MF +0.9167 [+0.8310, +0.9605] ABOVE, ME +0.9588 [+0.9223, +0.9824] ABOVE.
Marrakesh clock: MC -0.5118 [-1.1330, -0.0918] BELOW, MF +0.7703 [+0.6458, +0.8819] CANNOT_TELL, ME +0.8479 [+0.7134, +0.9416] CANNOT_TELL.
Marrakesh MC leaves a positive residual on the other side of the negative kick: spectators +0.8521 [+0.5537, +1.4545] degrees per readout ABOVE, pairs +3.1537 [+2.0017, +4.1771] degrees per step ABOVE.
What a frame change cannot return, MC minus idle on kingston: coherence -0.0094 [-0.0146, +0.0002] CANNOT_TELL, X-part concurrence -0.0136 [-0.0228, -0.0023] BELOW.

## What it does not show

These are shares of the phase, not of all the damage. One device per day, and no cause is named.

## Files

- Results: [kingston](../run/results/results_keystone_ibm_kingston.text), [marrakesh](../run/results/results_keystone_ibm_marrakesh.text), [plan](../run/PLAN_KEYSTONE.md.text)
- Tables: [committed_kicks_ibm_kingston.json](../run/data/committed_kicks_ibm_kingston.json), [fresh_kicks_ibm_kingston.json](../run/data/fresh_kicks_ibm_kingston.json), and the marrakesh pair in [run/data](../run/data/)
- Raw arrays and circuits: raw_keystone_ibm_CHIP_A, B, C.npz and circuits_keystone_ibm_CHIP_main.qpy in [run/data](../run/data/), arm order in [run/records](../run/records/)
- Loading: .npz arrays are IBM BitArray bytes. Bit k of a register is (a[:, nby-1-k//8] >> (k%8)) & 1. Keys are m0_i to m7_i and fin_i, i the circuit index. Circuits load with qiskit.qpy.

Heuremen LLC
