# Data for the Page-Wootters field

Page and Wootters 1983, Moreva et al. 2014, Diaz et al. 2025, Coppo et al. 2024.

## The question in your paper

A stationary clock-system state shows ordinary evolution when the system is conditioned on the clock. The ideal constraint has no term for the clock being read by something nearby. What does a real processor do to the history state?

## What was run

A history state of two clock qubits and one system qubit, four ticks, 27-setting tomography. A 39-qubit pack beside it is read out four times mid-build (the look). Arms: idle D, idle plus echo DE, look M, look plus the 21 October table MC, look plus a table measured minutes earlier MF, look plus echo ME. Both chips, 31 October 2026. Kingston qubits 3, 16, 23, jobs dbj3p3onceqs73aj79k0 and dbj3prt6p51s73ck1v30. Marrakesh qubits 104, 105, 106, jobs dbj3p4hffo6c73b8sc5g and dbj3pthkdqps738vqbqg. The 24 October run on kingston put the readouts at the end, jobs dbe9nf7pc3tc739lar8g and dbe9ru7gdj9s73fle000.

## What it shows

Kingston fidelity change against idle (C1, results_keystone_ibm_kingston.text): M -0.5550 [-0.5764, -0.5371] BELOW, MC -0.1516 [-0.1712, -0.1291] BELOW, MF -0.0045 [-0.0238, +0.0155] CONSISTENT, ME -0.0038 [-0.0234, +0.0160] CONSISTENT.
Kingston share of the look's distance given back, against 0.5 (C4): MC +0.7591 [+0.7344, +0.7840] ABOVE, MF +1.0007 [+0.9965, +1.0047] ABOVE, ME +0.9998 [+0.9960, +1.0037] ABOVE.
Kingston F per arm, pooled, no interval printed: D 0.7195, DE 0.8595, M 0.1645, MC 0.5679, MF 0.715, ME 0.8556.
Marrakesh C1 (results_keystone_ibm_marrakesh.text): M -0.1308 [-0.1516, -0.1105] BELOW, MC -0.0762 [-0.0951, -0.0560] BELOW, MF -0.0749 [-0.0934, -0.0554] BELOW, ME -0.0713 [-0.0912, -0.0523] BELOW.
Marrakesh C4: MC -0.5118 [-1.1330, -0.0918] BELOW, MF +0.7703 [+0.6458, +0.8819] CANNOT_TELL, ME +0.8479 [+0.7134, +0.9416] CANNOT_TELL.
Marrakesh F per arm: D 0.7317, DE 0.7408, M 0.6009, MC 0.6555, MF 0.6568, ME 0.6695.
The 24 October look at the end took the history fidelity from 0.665 to 0.158, change -0.507 [-0.524, -0.494] BELOW (RESULT_POOTERS.md.text).

## What it does not show

Three qubits per chip, picked for a large kick contrast, so the readings describe those qubits and not a chip average. Nothing here says why the phase appears.

## Files

- [results kingston](../run/results/results_keystone_ibm_kingston.text), [results marrakesh](../run/results/results_keystone_ibm_marrakesh.text), [24 October result](../earlier_runs/2026-10-24-page-wootters/RESULT_POOTERS.md.text)
- Raw 31 October: [run/data](../run/data/) holds raw_keystone_ibm_CHIP_A, B, C.npz and circuits_keystone_ibm_CHIP_main.qpy. Circuit order and calibration job ids are in [run/records](../run/records/).
- Raw 24 October: [shots_pooters_J1.npz](../earlier_runs/2026-10-24-page-wootters/shots_pooters_J1.npz), [J2](../earlier_runs/2026-10-24-page-wootters/shots_pooters_J2.npz), [circuits_pooters.qpy](../earlier_runs/2026-10-24-page-wootters/circuits_pooters.qpy)
- Loading: run/data .npz arrays are IBM BitArray bytes. Bit k of a register is (a[:, nby-1-k//8] >> (k%8)) & 1. Keys are fin_i and m0_i to m3_i, i the circuit index. The 24 October arrays are bit strings. Circuits load with qiskit.qpy.

Heuremen LLC
