"""Circuit builders for the Qiskit ZNE validation pipeline."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from qiskit import QuantumCircuit

from zne_qiskit_validation import config

Edge = tuple[int, int]


def _validate_n_qubits(n_qubits: int) -> int:
    if int(n_qubits) != n_qubits or int(n_qubits) < 1:
        raise ValueError("n_qubits must be a positive integer")
    return int(n_qubits)


def _validate_edges(n_qubits: int, edges: Sequence[Edge]) -> list[Edge]:
    clean_edges: list[Edge] = []
    for edge in edges:
        if len(edge) != 2:
            raise ValueError("each edge must contain exactly two vertices")
        u, v = int(edge[0]), int(edge[1])
        if u == v:
            raise ValueError("self-loops are not supported")
        if not (0 <= u < n_qubits and 0 <= v < n_qubits):
            raise ValueError("edge vertex out of range")
        clean_edges.append((u, v))
    if not clean_edges:
        raise ValueError("at least one edge is required")
    return clean_edges


def ring_edges(n_qubits: int) -> list[Edge]:
    """Return nearest-neighbor ring edges for ``n_qubits`` vertices."""

    n_qubits = _validate_n_qubits(n_qubits)
    if n_qubits < 3:
        raise ValueError("ring graph requires at least 3 qubits")
    return [(idx, (idx + 1) % n_qubits) for idx in range(n_qubits)]


def random_graph_edges(
    n_qubits: int,
    edge_probability: float = config.QAOA_RANDOM_EDGE_PROBABILITY,
    seed: int = config.SEED,
) -> list[Edge]:
    """Generate deterministic Erdos-Renyi graph edges for QAOA robustness."""

    n_qubits = _validate_n_qubits(n_qubits)
    if not (0.0 < float(edge_probability) <= 1.0):
        raise ValueError("edge_probability must be in (0, 1]")

    rng = np.random.default_rng(seed)
    edges = [
        (u, v)
        for u in range(n_qubits)
        for v in range(u + 1, n_qubits)
        if rng.random() < edge_probability
    ]
    if not edges:
        # Deterministic fallback so downstream MaxCut observables remain valid.
        edges = ring_edges(n_qubits)
    return edges


def qaoa_parameters(depth: int) -> tuple[list[float], list[float]]:
    """Return the fixed QAOA parameters specified in the validation plan."""

    if int(depth) not in config.QAOA_PARAMS:
        raise ValueError(f"unsupported QAOA depth: {depth}")
    params = config.QAOA_PARAMS[int(depth)]
    return list(params["gammas"]), list(params["betas"])


def ghz_circuit(
    n_qubits: int,
    *,
    measure: bool = True,
    x_basis: bool = True,
) -> QuantumCircuit:
    """Build a GHZ circuit, optionally measured in X or Z basis."""

    n_qubits = _validate_n_qubits(n_qubits)
    circuit = QuantumCircuit(n_qubits, n_qubits if measure else 0)
    circuit.h(0)
    for idx in range(n_qubits - 1):
        circuit.cx(idx, idx + 1)

    if x_basis:
        for qubit in range(n_qubits):
            circuit.h(qubit)

    if measure:
        circuit.measure(range(n_qubits), range(n_qubits))
    return circuit


def ghz_x_measurement_circuit(n_qubits: int) -> QuantumCircuit:
    """Build the main GHZ circuit for measuring X^n."""

    return ghz_circuit(n_qubits, measure=True, x_basis=True)


def ghz_z_measurement_circuit(n_qubits: int) -> QuantumCircuit:
    """Build the GHZ control circuit for Z-basis observables."""

    return ghz_circuit(n_qubits, measure=True, x_basis=False)


def qaoa_maxcut_circuit(
    n_qubits: int,
    edges: Sequence[Edge] | None = None,
    *,
    depth: int = 1,
    gammas: Sequence[float] | None = None,
    betas: Sequence[float] | None = None,
    measure: bool = True,
) -> QuantumCircuit:
    """Build a QAOA MaxCut circuit with RX mixer and RZZ cost layers."""

    n_qubits = _validate_n_qubits(n_qubits)
    clean_edges = ring_edges(n_qubits) if edges is None else _validate_edges(n_qubits, edges)

    if gammas is None or betas is None:
        default_gammas, default_betas = qaoa_parameters(depth)
        gammas = default_gammas if gammas is None else gammas
        betas = default_betas if betas is None else betas

    gamma_values = [float(value) for value in gammas]
    beta_values = [float(value) for value in betas]
    if len(gamma_values) != len(beta_values):
        raise ValueError("gammas and betas must have the same length")
    if len(gamma_values) != int(depth):
        raise ValueError("depth must match the number of QAOA parameter layers")

    circuit = QuantumCircuit(n_qubits, n_qubits if measure else 0)
    for qubit in range(n_qubits):
        circuit.h(qubit)

    for gamma, beta in zip(gamma_values, beta_values):
        for u, v in clean_edges:
            circuit.rzz(gamma, u, v)
        for qubit in range(n_qubits):
            circuit.rx(2.0 * beta, qubit)

    if measure:
        circuit.measure(range(n_qubits), range(n_qubits))
    return circuit

