// Figure 1(c) - No-feedforward control (corrections omitted)
OPENQASM 2.0;
include "qelib1.inc";

// 3-qubit teleportation: q0 input, q1/q2 Bell pair, q2 receiver
qreg q[3];
creg c0_[1];   // q0 Bell-measurement bit -> controls Z
creg c1_[1];   // q1 Bell-measurement bit -> controls X
creg c2_[1];   // receiver readout

h q[1];                 // Bell pair
ry(1.0471975512) q[0];   // input state on q0 (representative theta = pi/3 shown; theta is swept over 0, pi/6, pi/3, pi/2, 2pi/3, pi)
cx q[1], q[2];
barrier q;
cx q[0], q[1];           // Bell measurement
h q[0];
measure q[1] -> c1_[0];
measure q[0] -> c0_[0];
barrier q;
// feed-forward corrections omitted for the no-feedforward control
measure q[2] -> c2_[0];  // receiver readout