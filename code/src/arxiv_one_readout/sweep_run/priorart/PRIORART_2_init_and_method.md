# Prior art 2 (init/readout memory) and 3 (IBM's RB method), searchers 23 Oct 2026
INIT: no one has tested IBM's init_error or prob_meas fields; not published as such (1, 2, 3 all NO; 3 CANNOT_TELL vs full text of
  arXiv:2610.20810 Zheng et al. 14 Oct 2026, conditions readout on previous readout, fluxonium/transmon, not IBM fields; and GitHub
  ondrejch/qubit-deja-vu 15-16 Oct 2026, kingston+fez reset-free readout memory, no init_error). IBM docs define init_error (prior shot |1>,
  default rep_delay) but give no protocol; repetition-rate page: lower rep_delay raises state-prep error (qualitative).
  A GitHub dataset note lists init_error missing for ~77% of rows (third party, unverified).
METHOD (IBM docs, verbatim): sx = "Average gate fidelity of the sqrt(X) (SX) gate from randomized benchmarking, measured simultaneously on
  all qubits"; "The randomized benchmarking sequence includes SX, ID, and X gates, and it is assumed their errors are the same"; "The ID
  gate is a delay of duration equal to the duration of the sqrt(X) and X gates." 2Q = "Average gate fidelity ... from randomized
  benchmarking. Measured in 'isolation': batches with a minimum separation of two qubits between edges ... includes the error of the layer
  of single-qubit Cliffords." No gates-per-Clifford count is published anywhere. qiskit-experiments default ratio: sx 1, x 1, id 0, rz 0.
  McKay arXiv:2311.05933 quotes backend 2Q values as PROCESS error eps_p = (d+1)/d eps_g (x1.25 for d=4).
READING FOR THE BILL:
  - SX line wording: "measured error per SX/X pulse (simultaneous RB, all qubits) is 1.31-1.45x the stated sx error". If IBM counts ID
    slots as error-bearing gates (its own 'assumed equal' sentence), that is HOW its figure comes out low, not a defence: the field is
    labelled the SX gate's error.
  - CZ line: IBM's docs say average gate fidelity (our 3/4(1-p) is average gate error). If the field were process error instead (McKay),
    like-for-like would raise our ratio by 1.25 (1.55-2.0x), not lower it. Either convention: ABOVE.
  - Cite IBM tutorial 'refresh backend properties' (kingston: 2Q measured above reported, attributed to simultaneous vs isolated; ours is isolated).
