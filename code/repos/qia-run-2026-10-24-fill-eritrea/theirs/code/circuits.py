"""Dynamic-circuit quantum-teleportation circuits used in the benchmark.

Three variants are constructed on three qubits (q0 = input, q1-q2 = resource):

    full              standard teleportation with shared entanglement and
                      classically conditioned (feed-forward) corrections;
    no_entanglement   the shared Bell pair is omitted, feed-forward retained;
    no_feedforward    the Bell pair is retained, the corrections omitted.

The input state is prepared by a single RY(theta) rotation. The two Bell-
measurement outcomes are written to classical registers c0 (q0) and c1 (q1),
and the teleported qubit q2 is read into c2.

Requires Qiskit >= 1.0.
"""
from __future__ import annotations

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister


def build_circuit(theta: float, *, entangle: bool = True,
                  feedforward: bool = True, basis: str = "Z") -> QuantumCircuit:
    """Return a teleportation circuit for input angle ``theta``.

    Parameters
    ----------
    theta : float
        Rotation angle of the RY gate that prepares the input qubit q0.
    entangle : bool
        If True, create the shared Bell pair on q1, q2 (set False for the
        no-entanglement control).
    feedforward : bool
        If True, apply the conditional X (on the q1 outcome) and Z (on the q0
        outcome) corrections to q2 (set False for the no-feedforward control).
    basis : {"X", "Y", "Z"}
        Measurement basis for the teleported qubit q2. The corresponding
        pre-measurement rotation is applied so that the readout estimates
        <X>, <Y>, or <Z>. "Z" (default) leaves the figure circuits unchanged.
    """
    q = QuantumRegister(3, "q")
    c0 = ClassicalRegister(1, "c0")
    c1 = ClassicalRegister(1, "c1")
    c2 = ClassicalRegister(1, "c2")
    qc = QuantumCircuit(q, c0, c1, c2)

    qc.ry(theta, 0)                     # prepare input state on q0
    if entangle:
        qc.h(1)
        qc.cx(1, 2)                     # shared Bell pair on q1, q2
    qc.barrier()

    qc.cx(0, 1)
    qc.h(0)                             # Bell measurement of q0, q1
    qc.measure(0, c0)
    qc.measure(1, c1)
    qc.barrier()

    if feedforward:
        with qc.if_test((c1, 1)):       # X correction when the q1 outcome is 1
            qc.x(2)
        with qc.if_test((c0, 1)):       # Z correction when the q0 outcome is 1
            qc.z(2)
        qc.barrier()

    # rotate q2 into the requested tomography basis before read-out
    if basis not in ("X", "Y", "Z"):
        raise ValueError(f"basis must be 'X', 'Y' or 'Z'; got {basis!r}")
    if basis == "X":
        qc.h(2)
    elif basis == "Y":
        qc.sdg(2)
        qc.h(2)
    qc.measure(2, c2)
    return qc


# Convenience constructors for the three benchmark modes.
def full_protocol(theta: float) -> QuantumCircuit:
    return build_circuit(theta, entangle=True, feedforward=True)


def no_entanglement(theta: float) -> QuantumCircuit:
    return build_circuit(theta, entangle=False, feedforward=True)


def no_feedforward(theta: float) -> QuantumCircuit:
    return build_circuit(theta, entangle=True, feedforward=False)


MODES = {
    "full": full_protocol,
    "no_entanglement": no_entanglement,
    "no_feedforward": no_feedforward,
}
