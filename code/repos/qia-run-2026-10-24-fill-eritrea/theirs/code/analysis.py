"""Analysis routines for the teleportation benchmark.

All quantities are computed directly from the raw measurement counts collected
on ibm_fez; nothing here is hard-coded. The functions reproduce the fidelity
table, the reconstructed Bloch components, and the branch-resolved vectors
reported in the manuscript.

Conventions
-----------
A single-qubit Pauli expectation value is estimated from counts as
    <B> = (N0 - N1) / (N0 + N1),
and the teleported-state fidelity for an input prepared by RY(theta) is
    F(theta) = (1 + <X> sin(theta) + <Z> cos(theta)) / 2.
"""
from __future__ import annotations

import json
import math
from typing import Dict, Tuple

import numpy as np

# Six input angles swept in the experiment.
ANGLES: Tuple[Tuple[str, float], ...] = (
    ("0", 0.0),
    ("pi/6", math.pi / 6),
    ("pi/3", math.pi / 3),
    ("pi/2", math.pi / 2),
    ("2pi/3", 2 * math.pi / 3),
    ("pi", math.pi),
)
MODES = ("full", "no_entanglement", "no_feedforward")
SHOTS = 8192

# Bit ordering of the 3-bit strings in the branch-resolved counts, validated
# against Supplementary Table S1: leftmost char = output qubit (q2),
# middle = q1, rightmost = q0.
_OUT, _Q1, _Q0 = 0, 1, 2


def load_json(path: str) -> dict:
    """Load a JSON counts/metadata file."""
    with open(path) as fh:
        return json.load(fh)


def expectation_value(counts: Dict[str, int]) -> float:
    """Return <B> = (N0 - N1) / (N0 + N1) for single-bit counts."""
    n0 = counts.get("0", 0)
    n1 = counts.get("1", 0)
    total = n0 + n1
    return (n0 - n1) / total if total else 0.0


def shots_of(counts: Dict[str, int]) -> int:
    """Total shots actually recorded in a counts dict (do not assume 8192)."""
    return sum(int(v) for v in counts.values())


def shot_noise_se(expval: float, shots: int = SHOTS) -> float:
    """Standard error of a +/-1 expectation value under shot noise.

    Pass the actual shot count for the measurement; SHOTS is only a fallback.
    """
    return math.sqrt(max(0.0, 1.0 - expval ** 2) / shots)


def main_run_components(raw_counts: dict, mode: str, angle: str) -> Dict[str, float]:
    """Return {'X','Y','Z'} expectation values for a mode/angle of the main run."""
    return {b: expectation_value(raw_counts[f"{mode}|{angle}|{b}"]) for b in "XYZ"}


def main_run_shots(raw_counts: dict, mode: str, angle: str) -> Dict[str, int]:
    """Return {'X','Y','Z'} actual shot totals for a mode/angle of the main run."""
    return {b: shots_of(raw_counts[f"{mode}|{angle}|{b}"]) for b in "XYZ"}


def fidelity(theta: float, x: float, z: float) -> float:
    """Teleported-state fidelity for an RY(theta) input."""
    return (1.0 + x * math.sin(theta) + z * math.cos(theta)) / 2.0


def fidelity_table(raw_counts: dict) -> Dict[str, Dict[str, float]]:
    """Return {mode: {angle: (fidelity, standard_error)}} for all modes/angles."""
    out: Dict[str, Dict[str, float]] = {}
    for mode in MODES:
        row = {}
        for angle, theta in ANGLES:
            comp = main_run_components(raw_counts, mode, angle)
            n = main_run_shots(raw_counts, mode, angle)
            f = fidelity(theta, comp["X"], comp["Z"])
            se = 0.5 * math.sqrt(
                (math.sin(theta) ** 2) * (1 - comp["X"] ** 2) / n["X"]
                + (math.cos(theta) ** 2) * (1 - comp["Z"] ** 2) / n["Z"]
            )
            row[angle] = (f, se)
        out[mode] = row
    return out


def branch_vector(branch_counts: dict, angle: str, branch: str) -> Dict[str, float]:
    """Reconstruct {'X','Y','Z'} of the receiver qubit for one (q0,q1) branch.

    ``branch`` is the two-character string '(q0)(q1)', e.g. '01' = q0=0, q1=1.
    """
    comp: Dict[str, float] = {}
    for basis in "XYZ":
        counts = branch_counts[f"{angle}|{basis}"]
        n0 = n1 = 0
        for bitstring, c in counts.items():
            if bitstring[_Q0] == branch[0] and bitstring[_Q1] == branch[1]:
                if bitstring[_OUT] == "0":
                    n0 += c
                else:
                    n1 += c
        comp[basis] = (n0 - n1) / (n0 + n1) if (n0 + n1) else 0.0
    return comp


def apply_correction(branch: str, comp: Dict[str, float]) -> Tuple[float, float]:
    """Apply the branch-dependent Pauli correction in the (X, Z) plane."""
    x, z = comp["X"], comp["Z"]
    return {
        "00": (x, z),     # no correction
        "01": (x, -z),    # undo X  (flips Y, Z)
        "10": (-x, z),    # undo Z  (flips X, Y)
        "11": (-x, -z),   # undo X and Z
    }[branch]


def branch_fidelities(branch_counts: dict, angle: str) -> Dict[str, float]:
    """Post-correction fidelity of each of the four branches at one angle."""
    theta = dict(ANGLES)[angle]
    out = {}
    for branch in ("00", "01", "10", "11"):
        xc, zc = apply_correction(branch, branch_vector(branch_counts, angle, branch))
        out[branch] = fidelity(theta, xc, zc)
    return out


def bell_fidelity(bell_counts: dict) -> float:
    """State fidelity of the Phi+ Bell pair from X/Y/Z parity measurements.

    F = (1 + <XX> - <YY> + <ZZ>) / 4, with parities estimated from two-bit counts.
    """
    def parity(counts: Dict[str, int]) -> float:
        agree = counts.get("00", 0) + counts.get("11", 0)
        disagree = counts.get("01", 0) + counts.get("10", 0)
        total = agree + disagree
        return (agree - disagree) / total if total else 0.0

    xx = parity(bell_counts["X"])
    yy = parity(bell_counts["Y"])
    zz = parity(bell_counts["Z"])
    return (1.0 + xx - yy + zz) / 4.0
