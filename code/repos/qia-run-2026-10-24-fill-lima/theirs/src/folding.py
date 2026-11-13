"""Gate folding helpers and audit records for Mitiq + Qiskit."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from mitiq.zne.scaling import fold_gates_at_random, fold_global
from qiskit import QuantumCircuit, transpile

LOCAL_RANDOM = "local_random"
GLOBAL = "global"
FOLDING_BASIS_GATES = ("rx", "rz", "cx", "measure")

_NON_UNITARY_OPS = {"measure", "barrier", "delay", "reset"}


@dataclass(frozen=True)
class FoldingAudit:
    """Audit metadata required by the validation plan."""

    folding_method: str
    scale_factor_requested: float
    scale_factor_effective_size: float
    scale_factor_effective_depth: float
    seed: int | None
    depth_orig: int
    depth_folded: int
    size_orig: int
    size_folded: int
    num_1q_orig: int
    num_1q_folded: int
    num_2q_orig: int
    num_2q_folded: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FoldResult:
    """Folded circuit plus audit metadata."""

    circuit: QuantumCircuit
    audit: FoldingAudit


def _canonical_method(method: str) -> str:
    normalized = method.lower().strip()
    if normalized in {LOCAL_RANDOM, "random", "fold_gates_at_random"}:
        return LOCAL_RANDOM
    if normalized in {GLOBAL, "fold_global"}:
        return GLOBAL
    raise ValueError(f"unknown folding method: {method}")


def _operation_arities(circuit: QuantumCircuit) -> tuple[int, int]:
    one_qubit = 0
    two_qubit = 0
    for instruction in circuit.data:
        operation = instruction.operation
        if operation.name in _NON_UNITARY_OPS:
            continue
        arity = len(instruction.qubits)
        if arity == 1:
            one_qubit += 1
        elif arity == 2:
            two_qubit += 1
    return one_qubit, two_qubit


def unitary_size(circuit: QuantumCircuit) -> int:
    """Return circuit size excluding measurements and other non-unitary ops."""

    return sum(_operation_arities(circuit))


def audit_folding(
    original: QuantumCircuit,
    folded: QuantumCircuit,
    *,
    method: str,
    scale_factor: float,
    seed: int | None = None,
) -> FoldingAudit:
    """Build a folding audit record for one original/folded pair."""

    method = _canonical_method(method)
    orig_1q, orig_2q = _operation_arities(original)
    folded_1q, folded_2q = _operation_arities(folded)
    size_orig = orig_1q + orig_2q
    size_folded = folded_1q + folded_2q
    depth_orig = int(original.depth() or 0)
    depth_folded = int(folded.depth() or 0)

    return FoldingAudit(
        folding_method=method,
        scale_factor_requested=float(scale_factor),
        scale_factor_effective_size=float(size_folded / size_orig) if size_orig else float("nan"),
        scale_factor_effective_depth=float(depth_folded / depth_orig) if depth_orig else float("nan"),
        seed=seed,
        depth_orig=depth_orig,
        depth_folded=depth_folded,
        size_orig=size_orig,
        size_folded=size_folded,
        num_1q_orig=orig_1q,
        num_1q_folded=folded_1q,
        num_2q_orig=orig_2q,
        num_2q_folded=folded_2q,
    )


def fold_circuit(
    circuit: QuantumCircuit,
    scale_factor: float,
    *,
    method: str = LOCAL_RANDOM,
    seed: int | None = None,
) -> QuantumCircuit:
    """Fold a Qiskit circuit with Mitiq."""

    if float(scale_factor) < 1.0:
        raise ValueError("scale_factor must be >= 1")

    method = _canonical_method(method)
    if method == LOCAL_RANDOM:
        return fold_gates_at_random(circuit, scale_factor=float(scale_factor), seed=seed)
    return fold_global(circuit, scale_factor=float(scale_factor))


def fold_and_audit(
    circuit: QuantumCircuit,
    scale_factor: float,
    *,
    method: str = LOCAL_RANDOM,
    seed: int | None = None,
) -> FoldResult:
    """Fold a circuit and return the folded circuit with audit metadata."""

    folded = fold_circuit(circuit, scale_factor, method=method, seed=seed)
    return FoldResult(
        circuit=folded,
        audit=audit_folding(
            circuit,
            folded,
            method=method,
            scale_factor=scale_factor,
            seed=seed,
        ),
    )


def canonicalize_for_folding(circuit: QuantumCircuit) -> QuantumCircuit:
    """Transpile to a stable basis before Mitiq folding.

    Mitiq may decompose higher-level Qiskit gates while folding. Canonicalizing
    first keeps the requested and effective scale factors aligned.
    """

    return transpile(circuit, basis_gates=list(FOLDING_BASIS_GATES), optimization_level=0)


def transpile_for_aer(circuit: QuantumCircuit, backend, *, optimization_level: int = 0) -> QuantumCircuit:
    """Transpile while preserving folding; default must stay optimization level 0."""

    return transpile(circuit, backend, optimization_level=optimization_level)
