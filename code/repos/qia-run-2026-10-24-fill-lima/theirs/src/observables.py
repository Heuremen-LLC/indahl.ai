"""Observable utilities for counts and noiseless statevector expectations."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from zne_qiskit_validation.analysis import compute_moments
from zne_qiskit_validation.circuits import Edge

ObservableFn = Callable[[str], float]


def qiskit_bitstring_to_bits(bitstring: str) -> list[int]:
    """Convert a Qiskit count key into bits indexed by qubit number."""

    if not bitstring:
        raise ValueError("bitstring must not be empty")
    if any(bit not in "01" for bit in bitstring):
        raise ValueError("bitstring must contain only 0 and 1")
    return [int(bit) for bit in bitstring[::-1]]


def ghz_x_parity_value(bitstring: str) -> float:
    """Return the X^n parity value after GHZ X-basis measurement."""

    bits = qiskit_bitstring_to_bits(bitstring)
    return 1.0 if sum(bits) % 2 == 0 else -1.0


def z0_value(bitstring: str) -> float:
    """Return the Z0 eigenvalue using Qiskit's little-endian qubit mapping."""

    bits = qiskit_bitstring_to_bits(bitstring)
    return 1.0 if bits[0] == 0 else -1.0


def zz_value(bitstring: str, qubit_a: int = 0, qubit_b: int = 1) -> float:
    """Return the Z_a Z_b eigenvalue."""

    bits = qiskit_bitstring_to_bits(bitstring)
    for qubit in (qubit_a, qubit_b):
        if not (0 <= int(qubit) < len(bits)):
            raise ValueError("qubit index out of range")
    return 1.0 if bits[int(qubit_a)] == bits[int(qubit_b)] else -1.0


def maxcut_raw_value(bitstring: str, edges: Sequence[Edge]) -> float:
    """Return the unnormalized MaxCut value for a measured bitstring."""

    bits = qiskit_bitstring_to_bits(bitstring)
    cut = 0
    for u, v in edges:
        if not (0 <= int(u) < len(bits) and 0 <= int(v) < len(bits)):
            raise ValueError("edge vertex out of range for bitstring")
        cut += bits[int(u)] ^ bits[int(v)]
    return float(cut)


def maxcut_normalized_value(bitstring: str, edges: Sequence[Edge]) -> float:
    """Return centered MaxCut value normalized to approximately [-1, 1]."""

    if not edges:
        raise ValueError("edges must not be empty")
    raw = maxcut_raw_value(bitstring, edges)
    half_edges = len(edges) / 2.0
    return float((raw - half_edges) / half_edges)


def make_maxcut_observable(edges: Sequence[Edge], *, normalized: bool = True) -> ObservableFn:
    """Create a MaxCut observable function bound to a fixed graph."""

    clean_edges = [(int(u), int(v)) for u, v in edges]
    if not clean_edges:
        raise ValueError("edges must not be empty")

    if normalized:
        return lambda bitstring: maxcut_normalized_value(bitstring, clean_edges)
    return lambda bitstring: maxcut_raw_value(bitstring, clean_edges)


def moments_from_probabilities(
    probabilities: Mapping[str, float],
    observable_fn: ObservableFn,
) -> tuple[float, float]:
    """Compute exact mean and variance from a probability dictionary."""

    if not probabilities:
        raise ValueError("probabilities must not be empty")

    mean = 0.0
    values: list[tuple[float, float]] = []
    for bitstring, probability in probabilities.items():
        probability = float(probability)
        if probability < -1e-15:
            raise ValueError("probabilities must be non-negative")
        value = float(observable_fn(bitstring))
        values.append((probability, value))
        mean += probability * value

    total_probability = sum(probability for probability, _ in values)
    if not np.isclose(total_probability, 1.0, atol=1e-9):
        values = [(probability / total_probability, value) for probability, value in values]
        mean = sum(probability * value for probability, value in values)

    variance = sum(probability * (value - mean) ** 2 for probability, value in values)
    return float(mean), float(max(0.0, variance))


def ideal_moments_from_statevector(
    circuit_no_measure: QuantumCircuit,
    observable_fn: ObservableFn,
) -> tuple[float, float]:
    """Compute noiseless observable moments from a Qiskit statevector."""

    if circuit_no_measure.num_clbits != 0:
        raise ValueError("statevector circuit must not contain classical bits")
    statevector = Statevector.from_instruction(circuit_no_measure)
    return moments_from_probabilities(statevector.probabilities_dict(), observable_fn)


def moments_from_counts(
    counts: Mapping[str, int],
    observable_fn: ObservableFn,
) -> tuple[float, float]:
    """Convenience wrapper around the analysis-layer count moments."""

    return compute_moments(counts, observable_fn)

