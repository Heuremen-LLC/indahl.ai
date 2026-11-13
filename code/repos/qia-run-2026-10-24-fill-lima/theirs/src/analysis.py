"""Statistical analysis utilities for finite-shot ZNE validation.

This module is intentionally independent from Qiskit and Mitiq. It only works
with counts, observable functions, moments, and numeric grids so it can be
tested before any long simulator run.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any

import numpy as np

Counts = Mapping[str, int]
ObservableFn = Callable[[str], float]


def _as_1d_float_array(values: Sequence[float] | np.ndarray, name: str) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional")
    if arr.size == 0:
        raise ValueError(f"{name} must not be empty")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} must contain only finite values")
    return arr


def _coerce_rng(rng: np.random.Generator | None) -> np.random.Generator:
    return rng if rng is not None else np.random.default_rng()


def _validate_counts(counts: Counts) -> tuple[list[str], np.ndarray, int]:
    if not counts:
        raise ValueError("counts must not be empty")

    keys: list[str] = []
    values: list[int] = []
    for bitstring, count in counts.items():
        if not isinstance(bitstring, str):
            raise TypeError("counts keys must be bitstrings")
        if int(count) != count:
            raise ValueError("counts values must be integers")
        if count < 0:
            raise ValueError("counts values must be non-negative")
        keys.append(bitstring)
        values.append(int(count))

    weights = np.asarray(values, dtype=np.int64)
    total = int(weights.sum())
    if total <= 0:
        raise ValueError("counts must contain at least one shot")
    return keys, weights, total


def resample_counts(counts: Counts, rng: np.random.Generator | None = None) -> dict[str, int]:
    """Bootstrap-resample counts while preserving the total shot count.

    The empirical distribution represented by ``counts`` is treated as the
    population. The returned dictionary omits bitstrings sampled zero times, so
    its keys are always a subset of the input keys.
    """

    keys, weights, total = _validate_counts(counts)
    rng = _coerce_rng(rng)
    probabilities = weights.astype(float) / float(total)
    sampled = rng.multinomial(total, probabilities)
    return {key: int(count) for key, count in zip(keys, sampled) if count > 0}


def compute_moments(counts: Counts, observable_fn: ObservableFn) -> tuple[float, float]:
    """Compute empirical mean and single-shot variance from bitstring counts."""

    keys, weights, total = _validate_counts(counts)
    values = np.asarray([float(observable_fn(bitstring)) for bitstring in keys], dtype=float)
    if not np.all(np.isfinite(values)):
        raise ValueError("observable_fn returned a non-finite value")

    probabilities = weights.astype(float) / float(total)
    mean = float(np.sum(probabilities * values))
    variance = float(np.sum(probabilities * (values - mean) ** 2))
    return mean, max(0.0, variance)


def richardson_coefficients(scale_factors: Sequence[float] | np.ndarray) -> np.ndarray:
    """Return Richardson extrapolation coefficients for zero-noise limit.

    Coefficients ``c_k`` satisfy ``sum(c_k * lambda_k**m) = 0`` for
    ``m = 1, ..., K - 1`` and ``sum(c_k) = 1``.
    """

    lambdas = _as_1d_float_array(scale_factors, "scale_factors")
    if np.any(lambdas <= 0):
        raise ValueError("scale_factors must be positive")
    if np.unique(lambdas).size != lambdas.size:
        raise ValueError("scale_factors must be distinct")

    vandermonde = np.vstack([lambdas**power for power in range(lambdas.size)])
    target = np.zeros(lambdas.size, dtype=float)
    target[0] = 1.0
    return np.linalg.solve(vandermonde, target)


def _integer_allocation(total: int, weights: np.ndarray) -> np.ndarray:
    if total < weights.size:
        raise ValueError("B must be at least the number of scale factors")

    if not np.all(np.isfinite(weights)):
        raise ValueError("allocation weights must be finite")
    if np.any(weights < 0):
        raise ValueError("allocation weights must be non-negative")

    if float(weights.sum()) <= 0.0:
        weights = np.ones_like(weights, dtype=float)

    allocation = np.ones(weights.size, dtype=int)
    remaining = int(total) - weights.size
    if remaining == 0:
        return allocation

    proportions = weights.astype(float) / float(weights.sum())
    raw_extra = remaining * proportions
    extra = np.floor(raw_extra).astype(int)
    allocation += extra

    leftover = int(total) - int(allocation.sum())
    if leftover > 0:
        order = np.argsort(-(raw_extra - extra))
        for idx in order[:leftover]:
            allocation[idx] += 1

    return allocation


def shot_allocation(
    B: int,
    coeffs: Sequence[float] | np.ndarray,
    sigmas: Sequence[float] | np.ndarray,
    mode: str,
) -> np.ndarray:
    """Allocate a finite shot budget across ZNE scale factors."""

    if int(B) != B:
        raise ValueError("B must be an integer")
    B = int(B)
    coeff_arr = _as_1d_float_array(coeffs, "coeffs")
    sigma_arr = _as_1d_float_array(sigmas, "sigmas")
    if coeff_arr.size != sigma_arr.size:
        raise ValueError("coeffs and sigmas must have the same length")
    if np.any(sigma_arr < 0):
        raise ValueError("sigmas must be non-negative")

    normalized_mode = mode.lower()
    if normalized_mode == "uniform":
        weights = np.ones(coeff_arr.size, dtype=float)
    elif normalized_mode == "optimal":
        weights = np.abs(coeff_arr) * sigma_arr
        if float(weights.sum()) <= 0.0:
            weights = np.abs(coeff_arr)
    else:
        raise ValueError(f"unknown allocation mode: {mode}")

    return _integer_allocation(B, weights)


def compute_delta_mse(
    y_lambdas: Sequence[float] | np.ndarray,
    var_lambdas: Sequence[float] | np.ndarray,
    y0: float,
    B: int,
    scale_factors: Sequence[float] | np.ndarray,
    allocation: str | Sequence[int] | np.ndarray = "uniform",
) -> dict[str, Any]:
    """Compute noisy and ZNE MSE estimates from calibrated moments.

    ``var_lambdas`` are single-shot variances. The noisy estimator uses the
    scale factor equal to 1.0 and the full budget ``B``. The ZNE estimator uses
    Richardson coefficients and the requested per-scale allocation.
    """

    y_arr = _as_1d_float_array(y_lambdas, "y_lambdas")
    var_arr = _as_1d_float_array(var_lambdas, "var_lambdas")
    lambdas = _as_1d_float_array(scale_factors, "scale_factors")
    if not np.isfinite(float(y0)):
        raise ValueError("y0 must be finite")
    if int(B) != B or int(B) <= 0:
        raise ValueError("B must be a positive integer")
    B = int(B)
    if y_arr.size != var_arr.size or y_arr.size != lambdas.size:
        raise ValueError("y_lambdas, var_lambdas, and scale_factors must have the same length")
    if np.any(var_arr < 0):
        raise ValueError("var_lambdas must be non-negative")

    baseline_matches = np.where(np.isclose(lambdas, 1.0, rtol=0.0, atol=1e-12))[0]
    if baseline_matches.size != 1:
        raise ValueError("scale_factors must contain exactly one baseline value equal to 1")
    baseline_idx = int(baseline_matches[0])

    coeffs = richardson_coefficients(lambdas)
    if isinstance(allocation, str):
        sigmas = np.sqrt(np.maximum(var_arr, 0.0))
        n_alloc = shot_allocation(B, coeffs, sigmas, allocation)
    else:
        n_alloc = np.asarray(allocation, dtype=int)
        if n_alloc.ndim != 1 or n_alloc.size != lambdas.size:
            raise ValueError("explicit allocation must match the number of scale factors")
        if np.any(n_alloc < 1):
            raise ValueError("explicit allocation must assign at least one shot per scale factor")
        if int(n_alloc.sum()) != B:
            raise ValueError("explicit allocation must sum to B")

    y_noisy = float(y_arr[baseline_idx])
    var_noisy = float(var_arr[baseline_idx] / B)
    mse_noisy = float((y_noisy - y0) ** 2 + var_noisy)

    y_zne = float(np.dot(coeffs, y_arr))
    var_zne = float(np.sum((coeffs**2) * var_arr / n_alloc))
    mse_zne = float((y_zne - y0) ** 2 + var_zne)

    return {
        "mse_noisy": mse_noisy,
        "mse_zne": mse_zne,
        "delta_mse": mse_noisy - mse_zne,
        "y_noisy": y_noisy,
        "y_zne": y_zne,
        "var_noisy": var_noisy,
        "var_zne": var_zne,
        "coefficients": coeffs,
        "shot_allocation": n_alloc,
    }


def find_crossing(eps_grid: Sequence[float] | np.ndarray, delta_mse: Sequence[float] | np.ndarray) -> float:
    """Find epsilon* at the first lower MSE-boundary crossing.

    The manuscript defines the lower boundary as the first transition from
    ``Delta MSE <= 0`` to ``Delta MSE > 0``. Interpolation is linear in
    ``Delta MSE`` and logarithmic in epsilon. Returns ``np.nan`` when the finite
    positive grid contains no such transition.
    """

    eps = _as_1d_float_array(eps_grid, "eps_grid")
    delta = _as_1d_float_array(delta_mse, "delta_mse")
    if eps.size != delta.size:
        raise ValueError("eps_grid and delta_mse must have the same length")

    mask = (eps > 0) & np.isfinite(delta)
    eps = eps[mask]
    delta = delta[mask]
    if eps.size < 2:
        return float("nan")

    order = np.argsort(eps)
    eps = eps[order]
    delta = delta[order]

    for idx in range(eps.size - 1):
        d1 = float(delta[idx])
        d2 = float(delta[idx + 1])
        if d1 <= 0.0 and d2 > 0.0:
            if d1 == 0.0:
                return float(eps[idx])
            x1 = float(np.log(eps[idx]))
            x2 = float(np.log(eps[idx + 1]))
            x_star = x1 - d1 * (x2 - x1) / (d2 - d1)
            return float(np.exp(x_star))

    return float("nan")


def fit_loglog(B_values: Sequence[float] | np.ndarray, eps_star: Sequence[float] | np.ndarray) -> dict[str, float]:
    """Fit ``epsilon* = C * B**s`` and return slope, prefactor, and R2."""

    B_arr = _as_1d_float_array(B_values, "B_values")
    eps_arr = _as_1d_float_array(eps_star, "eps_star")
    if B_arr.size != eps_arr.size:
        raise ValueError("B_values and eps_star must have the same length")

    mask = (B_arr > 0) & (eps_arr > 0) & np.isfinite(B_arr) & np.isfinite(eps_arr)
    B_arr = B_arr[mask]
    eps_arr = eps_arr[mask]
    if B_arr.size < 2:
        raise ValueError("at least two finite positive points are required for log-log fit")

    x = np.log(B_arr)
    y = np.log(eps_arr)
    slope, intercept = np.polyfit(x, y, 1)
    predicted = slope * x + intercept
    ss_res = float(np.sum((y - predicted) ** 2))
    ss_tot = float(np.sum((y - float(np.mean(y))) ** 2))
    if ss_tot <= 1e-30:
        r2 = 1.0 if ss_res <= 1e-30 else float("nan")
    else:
        r2 = 1.0 - ss_res / ss_tot

    return {
        "s": float(slope),
        "C": float(np.exp(intercept)),
        "r2": float(r2),
        "n_points": float(B_arr.size),
    }


def bootstrap_exponent(
    counts_grid: Mapping[float, Mapping[float, Counts]],
    observable_fn: ObservableFn,
    y0: float,
    B_values: Sequence[int] | np.ndarray,
    scale_factors: Sequence[float] | np.ndarray,
    allocation: str = "uniform",
    n_bootstrap: int = 1000,
    rng: np.random.Generator | None = None,
    ci_level: float = 0.95,
) -> dict[str, Any]:
    """Bootstrap counts through crossings and return the exponent distribution.

    ``counts_grid`` is indexed as ``counts_grid[epsilon][scale_factor]``. Each
    leaf is a counts dictionary from a high-shot calibration run.
    """

    if int(n_bootstrap) != n_bootstrap or int(n_bootstrap) <= 0:
        raise ValueError("n_bootstrap must be a positive integer")
    n_bootstrap = int(n_bootstrap)
    if not (0.0 < float(ci_level) < 1.0):
        raise ValueError("ci_level must be between 0 and 1")

    eps_values = np.asarray(sorted(float(eps) for eps in counts_grid.keys()), dtype=float)
    if eps_values.size < 2 or np.any(eps_values <= 0):
        raise ValueError("counts_grid must contain at least two positive epsilon values")

    lambdas = _as_1d_float_array(scale_factors, "scale_factors")
    B_arr = np.asarray(B_values, dtype=int)
    if B_arr.ndim != 1 or B_arr.size < 2 or np.any(B_arr <= 0):
        raise ValueError("B_values must contain at least two positive integers")

    for eps in eps_values:
        if float(eps) not in counts_grid:
            raise ValueError("counts_grid epsilon keys must be float-compatible")
        scale_map = counts_grid[float(eps)]
        for scale in lambdas:
            if float(scale) not in scale_map:
                raise ValueError(f"missing counts for epsilon={eps}, scale_factor={scale}")

    rng = _coerce_rng(rng)
    exponent_samples: list[float] = []
    crossing_samples: list[np.ndarray] = []

    for _ in range(n_bootstrap):
        deltas_by_B = {int(B): [] for B in B_arr}

        for eps in eps_values:
            scale_map = counts_grid[float(eps)]
            y_values: list[float] = []
            var_values: list[float] = []

            for scale in lambdas:
                sampled_counts = resample_counts(scale_map[float(scale)], rng)
                mean, variance = compute_moments(sampled_counts, observable_fn)
                y_values.append(mean)
                var_values.append(variance)

            for B in B_arr:
                estimate = compute_delta_mse(
                    y_values,
                    var_values,
                    y0,
                    int(B),
                    lambdas,
                    allocation=allocation,
                )
                deltas_by_B[int(B)].append(float(estimate["delta_mse"]))

        crossings = np.asarray(
            [find_crossing(eps_values, deltas_by_B[int(B)]) for B in B_arr],
            dtype=float,
        )
        finite = np.isfinite(crossings) & (crossings > 0)
        if int(finite.sum()) >= 2:
            fit = fit_loglog(B_arr[finite], crossings[finite])
            exponent_samples.append(float(fit["s"]))
            crossing_samples.append(crossings)

    if not exponent_samples:
        raise ValueError("bootstrap produced no valid exponent samples")

    samples = np.asarray(exponent_samples, dtype=float)
    alpha = (1.0 - float(ci_level)) / 2.0
    ci_low, ci_high = np.quantile(samples, [alpha, 1.0 - alpha])

    result: dict[str, Any] = {
        "samples": samples,
        "median": float(np.median(samples)),
        "mean": float(np.mean(samples)),
        "ci_low": float(ci_low),
        "ci_high": float(ci_high),
        "ci_level": float(ci_level),
        "n_valid": int(samples.size),
        "n_bootstrap": int(n_bootstrap),
    }
    if crossing_samples:
        result["crossings"] = np.vstack(crossing_samples)
    return result


def bootstrap_delta_mse(
    counts_by_scale: Mapping[float, Counts],
    observable_fn: ObservableFn,
    y0: float,
    B: int,
    scale_factors: Sequence[float] | np.ndarray,
    allocation: str = "uniform",
    n_bootstrap: int = 1000,
    rng: np.random.Generator | None = None,
    ci_level: float = 0.95,
) -> dict[str, Any]:
    """Bootstrap one Delta MSE point from calibrated counts."""

    if int(n_bootstrap) != n_bootstrap or int(n_bootstrap) <= 0:
        raise ValueError("n_bootstrap must be a positive integer")
    if not (0.0 < float(ci_level) < 1.0):
        raise ValueError("ci_level must be between 0 and 1")

    lambdas = _as_1d_float_array(scale_factors, "scale_factors")
    for scale in lambdas:
        if float(scale) not in counts_by_scale:
            raise ValueError(f"missing counts for scale_factor={scale}")

    rng = _coerce_rng(rng)
    samples: list[float] = []
    for _ in range(int(n_bootstrap)):
        y_values: list[float] = []
        var_values: list[float] = []
        for scale in lambdas:
            sampled_counts = resample_counts(counts_by_scale[float(scale)], rng)
            mean, variance = compute_moments(sampled_counts, observable_fn)
            y_values.append(mean)
            var_values.append(variance)

        estimate = compute_delta_mse(
            y_values,
            var_values,
            y0,
            B,
            lambdas,
            allocation=allocation,
        )
        samples.append(float(estimate["delta_mse"]))

    sample_array = np.asarray(samples, dtype=float)
    alpha = (1.0 - float(ci_level)) / 2.0
    ci_low, ci_high = np.quantile(sample_array, [alpha, 1.0 - alpha])
    return {
        "samples": sample_array,
        "median": float(np.median(sample_array)),
        "mean": float(np.mean(sample_array)),
        "ci_low": float(ci_low),
        "ci_high": float(ci_high),
        "ci_level": float(ci_level),
        "n_bootstrap": int(n_bootstrap),
    }
