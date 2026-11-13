"""Final IBM QAOA held-out 10-graph hardware replication."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from zne_qiskit_validation import config
from zne_qiskit_validation.analysis import richardson_coefficients
from zne_qiskit_validation.circuits import qaoa_maxcut_circuit, random_graph_edges
from zne_qiskit_validation.folding import canonicalize_for_folding, fold_and_audit
from zne_qiskit_validation.observables import (
    ideal_moments_from_statevector,
    make_maxcut_observable,
    moments_from_counts,
)
from zne_qiskit_validation.runners.run_ibm_mini_ghz import (
    DEFAULT_PLANS_PREFERENCE,
    DEFAULT_REGION,
    DRY_RUN,
    _circuit_metrics,
    _connect_service,
    _extract_pub_counts,
    _instance_from_env,
    _load_token,
    _select_backend,
    _transpile_for_backend,
)
from zne_qiskit_validation.runners.run_phase1_fast import FAIL, PASS, WARNING
from zne_qiskit_validation.zne_engine import append_checkpoint_row, stable_case_id, write_raw_counts, write_rows_csv

PHASE = "ibm_qaoa_heldout10"
SCALE_FACTORS = [1.0, 3.0]
GRAPH_SEEDS = [606, 707, 808, 909, 1001, 1102, 1203, 1304, 1405, 1506]
DEFAULT_N_QUBITS = 5
DEFAULT_DEPTH = 1
DEFAULT_SHOTS = 4000
ZNE_PHYSICAL_RANGE = (-1.2, 1.2)
DEGRADATION_TOLERANCE = 0.02
IMPROVEMENT_THRESHOLD = 7
DEGRADATION_THRESHOLD = 6


@dataclass(frozen=True)
class IbmQaoaHeldout10Result:
    status: str
    result_label: str
    backend_name: str | None
    job_id: str | None
    audit_rows: list[dict[str, Any]]
    ideal_rows: list[dict[str, Any]]
    measurement_rows: list[dict[str, Any]]
    per_graph_rows: list[dict[str, Any]]
    criteria_rows: list[dict[str, Any]]
    checkpoint_path: Path
    processed_path: Path
    log_path: Path


def _case_name(*, graph_seed: int, n_qubits: int, depth: int) -> str:
    return f"qaoa_heldout_seed_{int(graph_seed)}_n{int(n_qubits)}_r{int(depth)}"


def _build_circuits(*, n_qubits: int, depth: int, seed: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    circuits: list[dict[str, Any]] = []
    ideal_rows: list[dict[str, Any]] = []
    for graph_seed in GRAPH_SEEDS:
        edges = random_graph_edges(int(n_qubits), seed=int(graph_seed))
        observable_fn = make_maxcut_observable(edges, normalized=True)
        ideal_circuit = qaoa_maxcut_circuit(int(n_qubits), edges, depth=int(depth), measure=False)
        y_ideal, ideal_variance = ideal_moments_from_statevector(ideal_circuit, observable_fn)
        case = _case_name(graph_seed=int(graph_seed), n_qubits=int(n_qubits), depth=int(depth))
        ideal_rows.append(
            {
                "phase": PHASE,
                "row_type": "ideal",
                "status": PASS,
                "case": case,
                "graph_seed": int(graph_seed),
                "circuit": "qaoa_maxcut_random_graph",
                "n_qubits": int(n_qubits),
                "depth": int(depth),
                "edges": edges,
                "edge_count": len(edges),
                "y_ideal": float(y_ideal),
                "ideal_variance": float(ideal_variance),
            }
        )

        base = canonicalize_for_folding(qaoa_maxcut_circuit(int(n_qubits), edges, depth=int(depth), measure=True))
        for scale_factor in SCALE_FACTORS:
            folded = fold_and_audit(base, scale_factor, method=config.DEFAULT_FOLDING, seed=int(seed))
            circuits.append(
                {
                    "case": case,
                    "graph_seed": int(graph_seed),
                    "edges": edges,
                    "edge_count": len(edges),
                    "y_ideal": float(y_ideal),
                    "ideal_variance": float(ideal_variance),
                    "observable_fn": observable_fn,
                    "scale_factor": float(scale_factor),
                    "label": f"lambda_{int(scale_factor)}",
                    "circuit": folded.circuit,
                    "audit": folded.audit.to_dict(),
                }
            )
    return circuits, ideal_rows


def _evaluate(
    measurement_rows: list[dict[str, Any]],
    ideal_rows: list[dict[str, Any]],
) -> tuple[str, str, list[dict[str, Any]], list[dict[str, Any]]]:
    ideal_by_case = {str(row["case"]): float(row["y_ideal"]) for row in ideal_rows}
    per_graph_rows: list[dict[str, Any]] = []

    for case, y_ideal in ideal_by_case.items():
        rows = [row for row in measurement_rows if row.get("case") == case and row.get("row_type") == "measurement"]
        by_scale = {float(row["scale_factor"]): row for row in rows}
        if not all(scale in by_scale for scale in SCALE_FACTORS):
            return FAIL, FAIL, [], [
                {
                    "phase": PHASE,
                    "row_type": "criteria",
                    "criteria": "counts_complete",
                    "case": case,
                    "status": FAIL,
                    "reason": "missing lambda=1 or lambda=3 measurements",
                }
            ]

        y1 = float(by_scale[1.0]["mean"])
        y3 = float(by_scale[3.0]["mean"])
        coeffs = richardson_coefficients(SCALE_FACTORS)
        y_zne = float(coeffs[0] * y1 + coeffs[1] * y3)
        error_l1 = abs(y1 - y_ideal)
        error_l3 = abs(y3 - y_ideal)
        error_zne = abs(y_zne - y_ideal)
        lambda3_degrades = error_l3 + DEGRADATION_TOLERANCE >= error_l1
        zne_physical = ZNE_PHYSICAL_RANGE[0] <= y_zne <= ZNE_PHYSICAL_RANGE[1]
        zne_improves = error_zne < error_l1
        per_graph_rows.append(
            {
                "phase": PHASE,
                "row_type": "per_graph",
                "status": PASS if zne_physical else WARNING,
                "case": case,
                "graph_seed": int(by_scale[1.0]["graph_seed"]),
                "edge_count": int(by_scale[1.0]["edge_count"]),
                "backend_name": by_scale[1.0].get("backend_name", ""),
                "job_id": by_scale[1.0].get("job_id", ""),
                "y_ideal": y_ideal,
                "y_lambda_1": y1,
                "y_lambda_3": y3,
                "y_zne": y_zne,
                "error_lambda_1": error_l1,
                "error_lambda_3": error_l3,
                "error_zne": error_zne,
                "zne_improves": zne_improves,
                "lambda3_degrades": lambda3_degrades,
                "zne_physical_range": zne_physical,
                "zne_coefficients": coeffs,
            }
        )

    n_graphs = len(per_graph_rows)
    improvement_count = sum(1 for row in per_graph_rows if bool(row["zne_improves"]))
    degradation_count = sum(1 for row in per_graph_rows if bool(row["lambda3_degrades"]))
    physical_count = sum(1 for row in per_graph_rows if bool(row["zne_physical_range"]))
    mean_error_l1 = sum(float(row["error_lambda_1"]) for row in per_graph_rows) / n_graphs
    mean_error_zne = sum(float(row["error_zne"]) for row in per_graph_rows) / n_graphs
    mean_improves = mean_error_zne < mean_error_l1

    if improvement_count >= IMPROVEMENT_THRESHOLD and mean_improves:
        status = PASS
        result_label = "HELDOUT_PASS"
    elif improvement_count >= 6 and mean_improves:
        status = WARNING
        result_label = "MIXED"
    else:
        status = WARNING
        result_label = "WARNING"

    criteria_rows = [
        {
            "phase": PHASE,
            "row_type": "aggregate",
            "status": status,
            "result_label": result_label,
            "n_graphs": n_graphs,
            "improvement_count": improvement_count,
            "degradation_count": degradation_count,
            "physical_count": physical_count,
            "mean_error_lambda_1": mean_error_l1,
            "mean_error_zne": mean_error_zne,
            "mean_improves": mean_improves,
        },
        {
            "phase": PHASE,
            "row_type": "criteria",
            "criteria": "zne_improves_7_of_10",
            "status": PASS if improvement_count >= IMPROVEMENT_THRESHOLD else WARNING,
            "value": improvement_count,
            "threshold": IMPROVEMENT_THRESHOLD,
            "n_graphs": n_graphs,
        },
        {
            "phase": PHASE,
            "row_type": "criteria",
            "criteria": "zne_improves_mean_error",
            "status": PASS if mean_improves else WARNING,
            "value": mean_improves,
            "mean_error_lambda_1": mean_error_l1,
            "mean_error_zne": mean_error_zne,
        },
        {
            "phase": PHASE,
            "row_type": "criteria",
            "criteria": "lambda3_degrades_majority",
            "status": PASS if degradation_count >= DEGRADATION_THRESHOLD else WARNING,
            "value": degradation_count,
            "threshold": DEGRADATION_THRESHOLD,
            "n_graphs": n_graphs,
        },
        {
            "phase": PHASE,
            "row_type": "criteria",
            "criteria": "zne_physical_all",
            "status": PASS if physical_count == n_graphs else WARNING,
            "value": physical_count,
            "threshold": n_graphs,
            "range": ZNE_PHYSICAL_RANGE,
        },
    ]
    return status, result_label, per_graph_rows, criteria_rows


def _write_log(result: IbmQaoaHeldout10Result) -> None:
    lines = [
        "# IBM QAOA heldout10",
        "",
        f"status: {result.status}",
        f"result_label: {result.result_label}",
        f"backend_name: {result.backend_name or ''}",
        f"job_id: {result.job_id or ''}",
        f"audit_rows: {len(result.audit_rows)}",
        f"ideal_rows: {len(result.ideal_rows)}",
        f"measurement_rows: {len(result.measurement_rows)}",
        f"per_graph_rows: {len(result.per_graph_rows)}",
        f"criteria_rows: {len(result.criteria_rows)}",
        f"checkpoint: {result.checkpoint_path}",
        f"processed: {result.processed_path}",
    ]
    result.log_path.parent.mkdir(parents=True, exist_ok=True)
    result.log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_ibm_qaoa_heldout10(
    *,
    submit: bool = False,
    n_qubits: int = DEFAULT_N_QUBITS,
    depth: int = DEFAULT_DEPTH,
    shots: int = DEFAULT_SHOTS,
    seed: int = config.SEED,
    backend_name: str | None = None,
    token: str | None = None,
    api_key_json: Path | None = None,
    instance: str | None = None,
    region: str = DEFAULT_REGION,
    plans_preference: list[str] | None = None,
    optimization_level: int = 0,
    raw_dir: Path = config.RAW_DIR,
    checkpoint_path: Path | None = None,
    processed_path: Path | None = None,
    log_path: Path | None = None,
) -> IbmQaoaHeldout10Result:
    """Run or dry-run the fixed IBM QAOA held-out 10-graph replication."""

    if int(n_qubits) != 5:
        raise ValueError("IBM QAOA heldout10 is fixed to n=5")
    if int(depth) != 1:
        raise ValueError("IBM QAOA heldout10 is fixed to depth r=1")
    if int(shots) <= 0:
        raise ValueError("shots must be positive")

    if checkpoint_path is None:
        checkpoint_path = config.CHECKPOINTS_DIR / f"{PHASE}_counts.csv"
    if processed_path is None:
        processed_path = config.PROCESSED_DIR / f"{PHASE}_summary.csv"
    if log_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = config.LOGS_DIR / f"{PHASE}_{timestamp}.log"

    plans = list(DEFAULT_PLANS_PREFERENCE if plans_preference is None else plans_preference)
    circuits, ideal_rows = _build_circuits(n_qubits=int(n_qubits), depth=int(depth), seed=int(seed))
    selected_backend_name: str | None = None
    job_id: str | None = None
    audit_rows: list[dict[str, Any]] = []
    measurement_rows: list[dict[str, Any]] = []
    per_graph_rows: list[dict[str, Any]] = []
    criteria_rows: list[dict[str, Any]] = []
    result_status = DRY_RUN
    result_label = DRY_RUN

    try:
        if submit:
            resolved_token = _load_token(token=token, api_key_json=api_key_json)
            service = _connect_service(
                token=resolved_token,
                instance=_instance_from_env(instance),
                region=region,
                plans_preference=plans,
            )
            backend = _select_backend(service, backend_name=backend_name, n_qubits=int(n_qubits))
            selected_backend_name = backend.name
            _transpile_for_backend(circuits, backend, optimization_level=int(optimization_level))
        else:
            for item in circuits:
                item["transpiled_circuit"] = item["circuit"]
                item["transpiled_metrics"] = _circuit_metrics(item["circuit"])

        for item in circuits:
            metrics = item["transpiled_metrics"]
            audit_rows.append(
                {
                    "phase": PHASE,
                    "row_type": "audit",
                    "status": PASS,
                    "case": item["case"],
                    "graph_seed": item["graph_seed"],
                    "circuit": "qaoa_maxcut_random_graph",
                    "n_qubits": int(n_qubits),
                    "depth": int(depth),
                    "shots": int(shots),
                    "backend_name": selected_backend_name or "",
                    "optimization_level": int(optimization_level),
                    "scale_factor": item["scale_factor"],
                    "edges": item["edges"],
                    "edge_count": item["edge_count"],
                    **item["audit"],
                    "transpiled_depth": metrics["depth"],
                    "transpiled_size": metrics["size"],
                    "transpiled_cx_count": metrics["cx_count"],
                    "transpiled_ecr_count": metrics["ecr_count"],
                    "transpiled_two_qubit_count": metrics["two_qubit_count"],
                    "transpiled_operation_counts": metrics["operation_counts"],
                    "layout": metrics["layout"],
                }
            )

        if not submit:
            criteria_rows.append(
                {
                    "phase": PHASE,
                    "row_type": "criteria",
                    "criteria": "dry_run_only",
                    "status": DRY_RUN,
                    "reason": "hardware submission disabled",
                }
            )
        else:
            from qiskit_ibm_runtime import SamplerV2 as Sampler

            sampler = Sampler(mode=backend)
            job = sampler.run([item["transpiled_circuit"] for item in circuits], shots=int(shots))
            job_id = job.job_id()
            (config.LOGS_DIR / f"{PHASE}_submitted_job.txt").write_text(
                f"backend={selected_backend_name}\njob_id={job_id}\n",
                encoding="utf-8",
            )
            result = job.result()

            for item_index, item in enumerate(circuits):
                counts = _extract_pub_counts(result[item_index])
                mean, variance = moments_from_counts(counts, item["observable_fn"])
                case_id = stable_case_id(
                    PHASE,
                    item["case"],
                    item["label"],
                    selected_backend_name,
                    int(shots),
                )
                metadata = {
                    "phase": PHASE,
                    "case_id": case_id,
                    "case": item["case"],
                    "graph_seed": item["graph_seed"],
                    "circuit": "qaoa_maxcut_random_graph",
                    "n_qubits": int(n_qubits),
                    "depth": int(depth),
                    "edges": item["edges"],
                    "edge_count": item["edge_count"],
                    "shots": int(shots),
                    "seed": int(seed),
                    "backend_name": selected_backend_name,
                    "job_id": job_id,
                    "scale_factor": item["scale_factor"],
                    "optimization_level": int(optimization_level),
                    "transpiled_metrics": item["transpiled_metrics"],
                    "y_ideal": item["y_ideal"],
                    "ideal_variance": item["ideal_variance"],
                }
                raw_path, raw_md5 = write_raw_counts(
                    phase=PHASE,
                    case_id=case_id,
                    metadata=metadata,
                    counts=counts,
                    raw_dir=raw_dir,
                )
                row = {
                    "phase": PHASE,
                    "row_type": "measurement",
                    "status": "ok",
                    "case_id": case_id,
                    "case": item["case"],
                    "graph_seed": item["graph_seed"],
                    "circuit": "qaoa_maxcut_random_graph",
                    "n_qubits": int(n_qubits),
                    "depth": int(depth),
                    "edges": item["edges"],
                    "edge_count": item["edge_count"],
                    "backend_name": selected_backend_name,
                    "job_id": job_id,
                    "shots": int(shots),
                    "seed": int(seed),
                    "scale_factor": item["scale_factor"],
                    "mean": mean,
                    "variance": variance,
                    "y_ideal": item["y_ideal"],
                    "counts_path": raw_path,
                    "counts_md5": raw_md5,
                    "resumed": False,
                }
                append_checkpoint_row(row, checkpoint_path)
                measurement_rows.append(row)

            result_status, result_label, per_graph_rows, criteria_rows = _evaluate(measurement_rows, ideal_rows)

        processed_rows = [*audit_rows, *ideal_rows, *measurement_rows, *per_graph_rows, *criteria_rows]
        write_rows_csv(processed_rows, processed_path)
        result_obj = IbmQaoaHeldout10Result(
            status=result_status,
            result_label=result_label,
            backend_name=selected_backend_name,
            job_id=job_id,
            audit_rows=audit_rows,
            ideal_rows=ideal_rows,
            measurement_rows=measurement_rows,
            per_graph_rows=per_graph_rows,
            criteria_rows=criteria_rows,
            checkpoint_path=Path(checkpoint_path),
            processed_path=Path(processed_path),
            log_path=Path(log_path),
        )
        _write_log(result_obj)
        return result_obj
    except Exception as exc:
        error_row = {
            "phase": PHASE,
            "row_type": "error",
            "status": FAIL,
            "backend_name": selected_backend_name or backend_name or "",
            "job_id": job_id or "",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
        write_rows_csv([error_row], processed_path)
        failed = IbmQaoaHeldout10Result(
            status=FAIL,
            result_label=FAIL,
            backend_name=selected_backend_name,
            job_id=job_id,
            audit_rows=[],
            ideal_rows=ideal_rows,
            measurement_rows=[],
            per_graph_rows=[],
            criteria_rows=[error_row],
            checkpoint_path=Path(checkpoint_path),
            processed_path=Path(processed_path),
            log_path=Path(log_path),
        )
        _write_log(failed)
        return failed


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the IBM QAOA held-out 10-graph replication.")
    parser.add_argument("--submit", action="store_true", help="Submit the job to IBM hardware. Omit for dry-run.")
    parser.add_argument("--api-key-json", type=Path, default=None, help="Path to IBM Cloud API-key JSON.")
    parser.add_argument("--backend", default=None, help="Backend name. Defaults to least pending open backend.")
    parser.add_argument("--n-qubits", type=int, default=DEFAULT_N_QUBITS, choices=[5])
    parser.add_argument("--depth", type=int, default=DEFAULT_DEPTH, choices=[1])
    parser.add_argument("--shots", type=int, default=DEFAULT_SHOTS)
    parser.add_argument("--region", default=DEFAULT_REGION)
    parser.add_argument("--plans-preference", nargs="*", default=DEFAULT_PLANS_PREFERENCE)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    result = run_ibm_qaoa_heldout10(
        submit=bool(args.submit),
        n_qubits=args.n_qubits,
        depth=args.depth,
        shots=args.shots,
        backend_name=args.backend,
        api_key_json=args.api_key_json,
        region=args.region,
        plans_preference=list(args.plans_preference),
    )
    print(f"IBM QAOA heldout10 status: {result.status}")
    print(f"Result label: {result.result_label}")
    print(f"Backend: {result.backend_name or ''}")
    print(f"Job ID: {result.job_id or ''}")
    print(f"Processed: {result.processed_path}")
    print(f"Log: {result.log_path}")
    return 0 if result.status in {PASS, WARNING, DRY_RUN} else 1


if __name__ == "__main__":
    sys.exit(main())
