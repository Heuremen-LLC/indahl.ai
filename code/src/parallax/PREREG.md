# THE PARALLAX RUN -- pre-registration (written 2026-09-28 before any shot; Bones)
Question (Wayfinder's rain tank): when a qubit reads "1" after we prepared "0", is the excitation IN THE TANK (the qubit really was
excited: heat, leftovers) or IN THE LENS (the readout misfiled it)? One look can't tell. Two looks can.
Fixed analysis (parallax_ibm.py analyze, unchanged after firing): cloud centers = medians of prepared-0 / prepared-1 raw dots per qubit;
project every shot on the 0->1 axis; threshold halfway.
 1. TANK vs LENS: e0 (one look) vs e0_heralded (second look, after the first said 0) vs excited_both_looks. If heralding lowers the
    rate on most qubits, part of "1 at rest" was really in the tank; what's left after heralding is the lens.
 2. LENS MEMORY: e0 with shots 20 us apart vs 1 ms apart. Higher when close together = the last shot's readout left the qubit excited.
 3. A THIRD PLACE: fraction of prepared-1 shots sitting off both clouds (5 widths off-axis or beyond the 1-cloud). Recorded per qubit.
 4. THE WATER MOVING: how far each cloud center moved between J1 and J4, in its own widths.
No numeric prediction is claimed; every number goes in the record whether or not it's interesting. Hardware: IBM Heron (156q),
every even qubit (~78), raw I/Q ("kerneled"), 4 jobs, max 60 QPU s each, refuses with <150 s left.
