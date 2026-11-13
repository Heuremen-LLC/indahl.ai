#!/usr/bin/env python3
"""Generate every numerical table in the manuscript, in ONE script.

Each table is printed to the console and written as a CSV in processed_data/.

  Table 1   device calibration              <- raw_data/main_calibration.json
  Table 2   fidelity F(theta) per mode       <- raw_data/raw_counts.json
  Table 3   ideal / noise-sim / hardware      <- analytic + qiskit-aer sim (needs qiskit)
  Table 4   Bell-pair verification            <- raw_data/bell_counts.json
  Table 6   circuit resource counts           <- qiskit transpile (needs qiskit)
  Table S1  post-correction branch fidelity   <- raw_data/branch_counts.json
  Table S2  run provenance                     <- raw_data/job_metadata.json

Table 5 is a literature comparison (Baur 2012, Steffen 2013, Kang 2025, this
work). It is NOT computed from data and is therefore not generated here; keep it
as the hand-written table in the manuscript.

Version notes: Tables 1, 2, 4, S1, S2 are exact and reproduce the manuscript
bit-for-bit (they come from the counts / metadata). Table 3's noise-model column
and Table 6's "representative" gate/depth rows depend on the installed
qiskit / qiskit-aer version and transpiler seed; their last digit can move a
little. The count- and structure-derived numbers (ideal column, hardware column,
measurements, conditional blocks, shots) are exact. Simulation numbers are never
reported as hardware.

    python make_all_tables.py           # every table
    python make_all_tables.py --fast    # skip Table 3 and Table 6 (the qiskit steps)
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
from decimal import Decimal, ROUND_HALF_UP

import analysis as an

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "raw_data")
OUT = os.path.join(HERE, "..", "processed_data")
QUBITS = [0, 1, 2]


def rhu(x: float, n: int) -> float:
    """Round half up to n decimals (matches the manuscript's rounding)."""
    return float(Decimal(str(x)).quantize(Decimal("1." + "0" * n), rounding=ROUND_HALF_UP))


def _hdr(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


# ----------------------------------------------------------------------------
# Table 1 - device calibration (from make_calibration_table.py)
# ----------------------------------------------------------------------------
def _qprop(cal, qidx, name):
    for p in cal["qubits"][qidx]:
        if p["name"] == name:
            v = p["value"]
            if name in ("T1", "T2"):
                unit = str(p.get("unit", "")).lower()
                return v if unit in ("us", "\u00b5s") else (v * 1e6 if unit == "s" else v)
            return v
    return None


def _gate_err(cal, gate, qubits):
    want = set(qubits)
    for g in cal["gates"]:
        if g["gate"] == gate and set(g["qubits"]) == want:
            for par in g["parameters"]:
                if par["name"] == "gate_error":
                    return par["value"]
    return None


def table1_calibration() -> None:
    cal = json.load(open(os.path.join(DATA, "main_calibration.json")))
    _hdr("Table 1. Device calibration for ibm_fez (physical qubits 0, 1, 2)")
    print(f"{'Qubit':>5s}{'T1 (us)':>10s}{'T2 (us)':>10s}{'Readout err':>13s}{'sqrtX err':>11s}")
    rows = []
    for q in QUBITS:
        t1 = _qprop(cal, q, "T1"); t2 = _qprop(cal, q, "T2")
        ro = _qprop(cal, q, "readout_error"); sx = _gate_err(cal, "sx", [q])
        print(f"{q:>5d}{t1:>10.1f}{t2:>10.1f}{ro:>13.4f}{sx:>11.5f}")
        rows.append([q, f"{t1:.1f}", f"{t2:.1f}", f"{ro:.4f}", f"{sx:.5f}"])
    cz01 = _gate_err(cal, "cz", (0, 1)); cz12 = _gate_err(cal, "cz", (1, 2))
    print(f"Two-qubit gate errors:  CZ(0,1) = {cz01:.4f}   CZ(1,2) = {cz12:.4f}")
    with open(os.path.join(OUT, "Table1_calibration.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["physical_qubit", "T1_us", "T2_us", "readout_error", "sqrtX_error"])
        w.writerows(rows)
        w.writerow([]); w.writerow(["pair", "gate", "gate_error"])
        w.writerow(["0-1", "cz", f"{cz01:.5f}"]); w.writerow(["1-2", "cz", f"{cz12:.5f}"])


# ----------------------------------------------------------------------------
# Table 2 - teleportation fidelity F per mode per angle (from analysis.fidelity_table)
# ----------------------------------------------------------------------------
def table2_fidelity(raw) -> None:
    _hdr("Table 2. Teleportation fidelity F per mode per angle (F +/- shot-noise SE)")
    table = an.fidelity_table(raw)                       # table[mode][angle] = (F, SE)
    print(f"{'theta':>6s}" + "".join(f"{a:>20s}" for a in ("full", "no_entanglement", "no_feedforward")))
    means = {m: [] for m in an.MODES}
    csv_rows = []
    for a, _ in an.ANGLES:
        cells = []
        row = [a]
        for m in an.MODES:
            F, SE = table[m][a]
            F4 = rhu(F, 4); SE4 = rhu(SE, 4)             # 4-dp intermediates (source_data_full.csv)
            means[m].append(F4)
            cells.append(f"{rhu(F4, 3):.3f} +/- {rhu(SE4, 3):.3f}")
            row += [f"{rhu(F4, 3):.3f}", f"{rhu(SE4, 3):.3f}"]
        print(f"{a:>6s}" + "".join(f"{c:>20s}" for c in cells))
        csv_rows.append(row)
    mean_cells = [f"{rhu(sum(means[m]) / len(means[m]), 3):.3f}" for m in an.MODES]
    print(f"{'mean':>6s}" + "".join(f"{c:>20s}" for c in mean_cells))
    with open(os.path.join(OUT, "Table2_fidelity.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["theta", "full_F", "full_SE", "noent_F", "noent_SE", "noff_F", "noff_SE"])
        w.writerows(csv_rows)
        w.writerow(["mean", mean_cells[0], "", mean_cells[1], "", mean_cells[2], ""])


# ----------------------------------------------------------------------------
# Table 4 - Bell-resource verification (correlations + fidelity, from bell counts)
# ----------------------------------------------------------------------------
def _parity(counts):
    agree = counts.get("00", 0) + counts.get("11", 0)
    disagree = counts.get("01", 0) + counts.get("10", 0)
    tot = agree + disagree
    return (agree - disagree) / tot if tot else 0.0


def _se_expval(v, n):
    return math.sqrt((1 - v * v) / n)


def table4_bell(bell) -> None:
    _hdr("Table 4. Bell-resource verification of the q1-q2 pair (job d8pa1cmkodhs7381h880)")
    xx, yy, zz = _parity(bell["X"]), _parity(bell["Y"]), _parity(bell["Z"])
    nx, ny, nz = (sum(bell[b].values()) for b in ("X", "Y", "Z"))
    F = (1.0 + xx - yy + zz) / 4.0
    sx, sy, sz = _se_expval(xx, nx), _se_expval(yy, ny), _se_expval(zz, nz)
    se_F = 0.25 * math.sqrt(sx ** 2 + sy ** 2 + sz ** 2)
    print(f"{'Observable':>18s}{'Measured':>16s}{'Ideal (Phi+)':>14s}")
    print(f"{'<XX>':>18s}{xx:>+11.3f} +/- {sx:.3f}{'+1':>10s}")
    print(f"{'<YY>':>18s}{yy:>+11.3f} +/- {sy:.3f}{'-1':>10s}")
    print(f"{'<ZZ>':>18s}{zz:>+11.3f} +/- {sz:.3f}{'+1':>10s}")
    print(f"{'Bell fidelity':>18s}{F:>11.3f} +/- {se_F:.3f}{'1':>10s}")
    with open(os.path.join(OUT, "Table4_bell.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["observable", "measured", "se", "ideal"])
        w.writerow(["XX", f"{xx:+.3f}", f"{sx:.3f}", "+1"])
        w.writerow(["YY", f"{yy:+.3f}", f"{sy:.3f}", "-1"])
        w.writerow(["ZZ", f"{zz:+.3f}", f"{sz:.3f}", "+1"])
        w.writerow(["bell_fidelity", f"{F:.3f}", f"{se_F:.3f}", "1"])


# ----------------------------------------------------------------------------
# Table S1 - post-correction per-branch fidelity (from analysis.branch_fidelities)
# ----------------------------------------------------------------------------
def tableS1_branches(branch) -> None:
    _hdr("Table S1. Post-correction per-branch fidelity (branch-resolved run)")
    print("(the mean is the unweighted average of the four branch fidelities)")
    print(f"{'theta':>6s}{'00':>9s}{'01':>9s}{'10':>9s}{'11':>9s}{'mean':>9s}")
    csv_rows = []
    for angle, _ in an.ANGLES:
        bf = an.branch_fidelities(branch, angle)
        mean = sum(bf.values()) / 4
        print(f"{angle:>6s}" + "".join(f"{bf[b]:>9.3f}" for b in ("00", "01", "10", "11")) + f"{mean:>9.3f}")
        csv_rows.append([angle] + [f"{bf[b]:.3f}" for b in ("00", "01", "10", "11")] + [f"{mean:.3f}"])
    with open(os.path.join(OUT, "TableS1_branch_fidelity.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["theta", "branch_00", "branch_01", "branch_10", "branch_11",
                    "mean_unweighted"])
        w.writerows(csv_rows)


# ----------------------------------------------------------------------------
# Table S2 - run provenance (from the combined raw_data/job_metadata.json)
# ----------------------------------------------------------------------------
def tableS2_provenance() -> None:
    _hdr("Table S2. Run provenance (job IDs, dates, qubit layouts, calibration timestamps)")
    meta = json.load(open(os.path.join(DATA, "job_metadata.json")))
    labels = {"main_tomography": "Main tomography", "branch_resolved": "Branch-resolved",
              "bell_resource": "Bell resource"}
    print(f"{'Run':>16s}{'Backend':>9s}{'Job ID':>22s}{'Submitted (UTC)':>22s}{'Qubits':>10s}{'Shots':>7s}")
    csv_rows = []
    for m in meta["runs"]:
        label = labels.get(m.get("run"), m.get("run", "?"))
        q = m.get("physical_qubits") or m.get("final_index_layout") or m.get("requested_physical_qubits")
        qs = ",".join(str(x) for x in q)
        sub = m.get("submitted_utc", "")[:19]
        print(f"{label:>16s}{m['backend']:>9s}{m['job_id']:>22s}{sub:>22s}{qs:>10s}{m['shots']:>7d}")
        csv_rows.append([label, m["backend"], m["job_id"], sub, qs, m["shots"],
                         m.get("calibration_last_update", "")])
    print("(calibration last-update timestamps written to the CSV)")
    with open(os.path.join(OUT, "TableS2_provenance.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["run", "backend", "job_id", "submitted_utc", "physical_qubits",
                    "shots", "calibration_last_update"])
        w.writerows(csv_rows)


# ----------------------------------------------------------------------------
# Table 3 - analytic ideal vs noise-model sim vs hardware  (needs qiskit + aer)
# ----------------------------------------------------------------------------
def table3_simulation() -> None:
    _hdr("Table 3. Mean fidelity per mode: ideal (analytic) / noise-model (sim) / hardware")
    try:
        import numpy as np
        from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
        from qiskit_aer import AerSimulator
        from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError
    except Exception as exc:
        print(f"[skipped] qiskit / qiskit-aer not available ({exc}).")
        print("This is the only table needing a simulator; all others are done.")
        return

    SEED = 1234
    cal = json.load(open(os.path.join(DATA, "main_calibration.json")))
    sx_err = {q: _gate_err(cal, "sx", [q]) for q in QUBITS}
    cz_err = {(0, 1): _gate_err(cal, "cz", (0, 1)), (1, 2): _gate_err(cal, "cz", (1, 2))}
    ro_err = {q: _qprop(cal, q, "readout_error") for q in QUBITS}
    raw_hw = an.load_json(os.path.join(DATA, "raw_counts.json"))
    _tbl = an.fidelity_table(raw_hw)
    HW = {m: sum(_tbl[m][a][0] for a, _ in an.ANGLES) / len(an.ANGLES) for m in an.MODES}
    BASIS = ["rz", "sx", "x", "cz"]; SH = an.shots_of(raw_hw["full|0|Z"])

    nm = NoiseModel()
    for q, e in sx_err.items():
        nm.add_quantum_error(depolarizing_error(e, 1), ["sx", "x"], [q])
    for (a, b), e in cz_err.items():
        nm.add_quantum_error(depolarizing_error(e, 2), "cz", [a, b])
        nm.add_quantum_error(depolarizing_error(e, 2), "cz", [b, a])
    for q, p in ro_err.items():
        nm.add_readout_error(ReadoutError([[1 - p, p], [p, 1 - p]]), [q])

    def ideal_fidelity(mode, theta):
        if mode == "full":
            return 1.0
        if mode == "no_entanglement":
            return (1 + math.cos(theta) ** 2) / 2
        return 0.5

    def build(mode, theta, meas):
        q = QuantumRegister(3, "q"); a = ClassicalRegister(2, "a"); o = ClassicalRegister(1, "o")
        qc = QuantumCircuit(q, a, o)
        qc.ry(theta, q[0])
        if mode != "no_entanglement":
            qc.h(q[1]); qc.cx(q[1], q[2])
        qc.cx(q[0], q[1]); qc.h(q[0]); qc.measure(q[1], a[1]); qc.measure(q[0], a[0])
        if mode != "no_feedforward":
            with qc.if_test((a[1], 1)):
                qc.x(q[2])
            with qc.if_test((a[0], 1)):
                qc.z(q[2])
        if meas == "X":
            qc.h(q[2])
        elif meas == "Y":
            qc.sdg(q[2]); qc.h(q[2])
        qc.measure(q[2], o[0])
        return qc

    def ev(c):
        n0 = sum(v for k, v in c.items() if k.split(" ")[0] == "0")
        n1 = sum(v for k, v in c.items() if k.split(" ")[0] == "1")
        return (n0 - n1) / (n0 + n1) if (n0 + n1) else 0

    sn = AerSimulator(noise_model=nm, seed_simulator=SEED)
    print(f"{'Mode':16s}{'Ideal (sim)':>13s}{'Noise-model (sim)':>19s}{'Hardware':>10s}")
    print("(ideal column is analytic; noise column is version-dependent to ~0.005)")
    rows = []
    for mode in ["full", "no_entanglement", "no_feedforward"]:
        Fi, Fn = [], []
        for th in [0.0, math.pi/6, math.pi/3, math.pi/2, 2*math.pi/3, math.pi]:
            e = {m: ev(sn.run(transpile(build(mode, th, m), basis_gates=BASIS,
                                        initial_layout=[0, 1, 2], seed_transpiler=SEED),
                              shots=SH).result().get_counts()) for m in "XYZ"}
            Fn.append((1 + e["X"] * math.sin(th) + e["Z"] * math.cos(th)) / 2)
            Fi.append(ideal_fidelity(mode, th))
        mi, mn = sum(Fi) / len(Fi), sum(Fn) / len(Fn)
        label = {"full": "Full", "no_entanglement": "No-entanglement", "no_feedforward": "No-feedforward"}[mode]
        print(f"{label:16s}{mi:>13.3f}{mn:>19.3f}{HW[mode]:>10.3f}")
        rows.append([label, f"{mi:.3f}", f"{mn:.3f}", f"{HW[mode]:.3f}"])
    with open(os.path.join(OUT, "Table3_simulation.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["mode", "ideal_analytic", "noise_model_sim", "hardware"])
        w.writerows(rows)


# ----------------------------------------------------------------------------
# Table 6 - circuit resource counts  (needs qiskit)
# ----------------------------------------------------------------------------
def table6_resources(raw) -> None:
    _hdr("Table 6. Executed-circuit metrics (representative transpilation + exact counts)")
    try:
        from qiskit import transpile
        from qiskit.transpiler.passes import RemoveBarriers
        import circuits as C
    except Exception as exc:
        print(f"[skipped] qiskit not available ({exc}).")
        return

    BASIS = ["rz", "sx", "x", "cz", "if_else", "measure"]
    MODES = [("Full", dict(entangle=True, feedforward=True)),
             ("No-entanglement", dict(entangle=False, feedforward=True)),
             ("No-feedforward", dict(entangle=True, feedforward=False))]
    rows = {}
    for name, flags in MODES:
        qc = C.build_circuit(1.0471975512, basis="Z", **flags)   # theta = pi/3 (matches Figure 1)
        meas = sum(1 for inst in qc.data if inst.operation.name == "measure")
        cond = sum(1 for inst in qc.data if inst.operation.name == "if_else")
        t = transpile(RemoveBarriers()(qc), basis_gates=BASIS, optimization_level=1, seed_transpiler=11)
        ops = t.count_ops()
        oneq = sum(ops.get(g, 0) for g in ("rz", "sx", "x"))
        rows[name] = dict(depth=t.depth(), oneq=oneq, twoq=ops.get("cz", 0), meas=meas, cond=cond)

    print(f"{'Quantity':36s}{'Full':>8s}{'No-ent':>10s}{'No-ff':>8s}")

    def line(label, key):
        print(f"{label:36s}" + "".join(f"{rows[n][key]:>{w}d}"
              for n, w in [("Full", 8), ("No-entanglement", 10), ("No-feedforward", 8)]))
    print("-- representative (transpiler/coupling-map dependent) --")
    line("Transpiled depth (representative)", "depth")
    line("Single-qubit gates (representative)", "oneq")
    line("Two-qubit CZ gates (representative)", "twoq")
    print("-- exact --")
    line("Measurements", "meas")
    line("Conditional feed-forward blocks", "cond")
    sh = {m: an.shots_of(raw[f"{m}|0|Z"]) for m in an.MODES}
    print(f"{'Shots':36s}{sh['full']:>8d}{sh['no_entanglement']:>10d}{sh['no_feedforward']:>8d}")
    with open(os.path.join(OUT, "Table6_resources.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["quantity", "full", "no_entanglement", "no_feedforward"])
        for lab, key in [("transpiled_depth_representative", "depth"),
                         ("single_qubit_gates_representative", "oneq"),
                         ("two_qubit_cz_gates_representative", "twoq"),
                         ("measurements", "meas"),
                         ("conditional_feedforward_blocks", "cond")]:
            w.writerow([lab, rows["Full"][key], rows["No-entanglement"][key], rows["No-feedforward"][key]])
        w.writerow(["shots", sh["full"], sh["no_entanglement"], sh["no_feedforward"]])


def table_values(raw, bell) -> None:
    """Write a tidy machine-readable dump of the exact (data-derived) table numbers."""
    rows = [["table", "series", "angle", "quantity", "value"]]
    tbl = an.fidelity_table(raw)
    for m in an.MODES:
        vals = []
        for a, _ in an.ANGLES:
            F, SE = tbl[m][a]
            rows.append(["T2", m, a, "F", f"{rhu(rhu(F, 4), 3):.3f}"])
            rows.append(["T2", m, a, "SE", f"{rhu(rhu(SE, 4), 3):.3f}"])
            vals.append(rhu(F, 4))
        rows.append(["T2", m, "mean", "F", f"{rhu(sum(vals) / len(vals), 3):.3f}"])
    F_bell = an.bell_fidelity(bell)
    rows.append(["T4", "bell", "", "fidelity", f"{F_bell:.3f}"])
    with open(os.path.join(OUT, "table_values.csv"), "w", newline="") as f:
        csv.writer(f).writerows(rows)
    print("wrote table_values.csv")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--fast", action="store_true", help="skip Table 3 and Table 6 (the qiskit steps)")
    args = p.parse_args()
    os.makedirs(OUT, exist_ok=True)

    raw = an.load_json(os.path.join(DATA, "raw_counts.json"))
    branch = an.load_json(os.path.join(DATA, "branch_counts.json"))
    bell = an.load_json(os.path.join(DATA, "bell_counts.json"))

    table1_calibration()
    table2_fidelity(raw)
    table4_bell(bell)
    tableS1_branches(branch)
    tableS2_provenance()
    table_values(raw, bell)
    if args.fast:
        print("\n[--fast] skipped Table 3 and Table 6 (the qiskit steps).")
    else:
        table6_resources(raw)
        print("\nNote: Table 3 runs a noise-model simulation and takes a few minutes ...")
        table3_simulation()

    print("\nDone. Table 5 is the literature comparison (hand-written, not generated).")
    print(f"All CSVs written to: {OUT}")


if __name__ == "__main__":
    main()
