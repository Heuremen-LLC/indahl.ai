"""common.py - shared builders for Jobs 1-4 and sim (qiskit 2.x, qiskit-ibm-runtime 0.50.x)."""
import json, sys, argparse, datetime, zlib
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.classical import expr

TAU_FF_ASSUMED = 1.0e-6   # [DESIGN ASSUMPTION] feedforward latency; defines lambda_L units only
M_REF = 3                 # windows padded to M_REF measurement slots (duration-matched control)
FACTORIAL = [(g, l, m) for g in (1, 3) for l in (1, 3) for m in (1, 3)] + [(2, 2, 1), (2, 2, 3)]
N_MCM = {"probe": 1, "teleport": 4, "ghz": 3}
N_Q = {"probe": 3, "teleport": 6, "ghz": 8}
SPEC_Q = {"probe": 2, "teleport": 5, "ghz": 7}

def get_args():
    p = argparse.ArgumentParser()
    p.add_argument("--report", default="job0_report.json")
    p.add_argument("--backend"); p.add_argument("--chain", help="comma-separated physical qubits (>=8)")
    p.add_argument("--seed", type=int, default=20261003)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--fake", help="offline rehearsal against a qiskit_ibm_runtime fake backend, e.g. FakeKingston")
    p.add_argument("--no-wait", action="store_true", help="submit, write the manifest, exit; collect.py finishes")
    p.add_argument("--s-per-exec", type=float, default=QUICK_S_PER_EXEC,
                   help="QPU s per execution for the quota check (pipeline passes Job 1's measured rate)")
    p.add_argument("--outdir", default=".", help="where manifests/ids/results are written")
    p.add_argument("--mock", action="store_true",
                   help="with --fake: run the ISA circuits on Aer with the fake's noise (pipeline test only)")
    p.add_argument("--mock-shots", type=int, help="override shots in --mock runs")
    p.add_argument("--job-name", help="override the job name (e.g. job1c: the echoed pilot replicated on another backend)")
    return p.parse_args()

def out_path(args_or_dir, name):
    import os
    d = args_or_dir if isinstance(args_or_dir, str) else getattr(args_or_dir, "outdir", ".")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, name)

def resolve(args):
    rep = {}
    try:
        rep = json.load(open(args.report))
    except FileNotFoundError:
        print("job0_report.json not found -> using CLI arguments")
    # RUNTIME CHECK: key names depend on job0_capabilities.py; adjust here if they differ.
    name = args.backend or rep.get("backend_name") or rep.get("backend")
    chain = ([int(x) for x in args.chain.split(",")] if args.chain else
             rep.get("best_chain") or rep.get("best_9q_chain") or rep.get("chain"))
    if not name or not chain:
        sys.exit("Need backend name and qubit chain (job0_report.json or --backend/--chain).")
    return name, [int(q) for q in chain], rep

class Timing:
    """Durations in seconds from backend.target; in simulation, abstract time quanta.
    layout maps a circuit (virtual) qubit to its physical qubit; the target is keyed by physical qubits."""
    def __init__(self, target=None, use_mcm2=False, sim_quantum=None, layout=None):
        self.t, self.use_mcm2, self.sim_quantum = target, use_mcm2, sim_quantum
        self.layout = list(layout) if layout is not None else None
        if sim_quantum:
            self.dt, self.gran, self.minlen = sim_quantum, 1, 1
        else:
            self.dt = target.dt
            self.gran = int(getattr(target, "granularity", 1) or 1)   # RUNTIME CHECK
            self.minlen = int(getattr(target, "min_length", 1) or 1)
    def dur(self, name, qargs):
        if self.sim_quantum:
            return {"measure": 4, "x": 0}.get(name, 0) * self.sim_quantum
        try:
            d = self.t[name][tuple(qargs)].duration
            return float(d) if d else 0.0
        except KeyError:
            return 0.0
    def slot(self, q):
        if self.layout is not None and not self.sim_quantum:
            q = self.layout[q]
        return self.dur("measure_2" if self.use_mcm2 else "measure", [q]) + 2 * self.dur("x", [q])
    def to_dt(self, sec):
        n = int(round(sec / self.dt / self.gran)) * self.gran
        if 0 < n < self.minlen:
            n = int(np.ceil(self.minlen / self.gran)) * self.gran
        return n

ECHO = True   # (design, revised after Job 1) staggered echo in every feedforward window; see Ctx.echo_seq

class Ctx:
    def __init__(self, bench, lam, timing, rng, sim=False, pad=True, interaction=False, echo=ECHO):
        self.bench, (self.G, self.L, self.M) = bench, lam
        self.timing, self.rng, self.sim, self.pad, self.echo = timing, rng, sim, pad, echo
        self.spec, self.interaction = SPEC_Q[bench], interaction
        self.qc = QuantumCircuit(QuantumRegister(N_Q[bench], "q"))
        self.mreg = ClassicalRegister(N_MCM[bench] * self.M, "mcm"); self.qc.add_register(self.mreg)
        self.mi, self.unroll_xor = 0, False
        self.meta = {"bench": bench, "setting": list(lam), "cz_twirl": [], "folds": [], "mcm_twirl": []}
        self.fold_half = bool(rng.integers(2))       # lambda_G = 2: fold with prob 1/2 per instance
        self.slot = max(timing.slot(q) for q in range(N_Q[bench])) if sim else None
    def _p(self, p, q):
        if p == 1: self.qc.x(q)
        elif p == 2: self.qc.y(q)
        elif p == 3: self.qc.z(q)
    @staticmethod
    def _conj(pa, pb):   # CZ (Pa x Pb) CZ up to phase; codes I0 X1 Y2 Z3
        xb = lambda p: p in (1, 2); zb = lambda p: p in (2, 3)
        mk = lambda x, z: {(0, 0): 0, (1, 0): 1, (1, 1): 2, (0, 1): 3}[(int(x), int(z))]
        return mk(xb(pa), zb(pa) ^ xb(pb)), mk(xb(pb), zb(pb) ^ xb(pa))
    def cz(self, a, b):
        n = {1: 1, 3: 3, 5: 5}.get(self.G, 3 if self.fold_half else 1)
        self.meta["folds"].append(n)
        for _ in range(n):
            pa, pb = int(self.rng.integers(4)), int(self.rng.integers(4))
            self._p(pa, a); self._p(pb, b); self.qc.cz(a, b)
            ca, cb = self._conj(pa, pb); self._p(ca, a); self._p(cb, b)
            self.qc.barrier(a, b); self.meta["cz_twirl"].append([pa, pb])
    def cx(self, c, t):
        self.qc.h(t); self.cz(c, t); self.qc.h(t)
    def mcm(self, q, idle=()):
        bits, R = [], 0
        for _ in range(self.M):
            r = int(self.rng.integers(2)); R ^= r
            if r: self.qc.x(q)
            c = self.mreg[self.mi]; self.mi += 1
            if self.timing.use_mcm2 and not self.sim:
                from qiskit_ibm_runtime.circuit import MidCircuitMeasure
                self.qc.append(MidCircuitMeasure(), [q], [c])
            else:
                self.qc.measure(q, c)
            if r: self.qc.x(q)
            if self.sim:
                for _ in range(int(round(self.slot / self.timing.dt))):
                    for i in idle: self.qc.id(i)
            bits.append(c)
        self.meta["mcm_twirl"].append({"qubit": q, "R": R, "first_clbit": self.mi - self.M})
        return bits, R
    def cond(self, gate, q, bits, R):
        """Apply gate^(v), v = parity(bits) XOR R (manual-twirl correction)."""
        if R: getattr(self.qc, gate)(q)
        if self.unroll_xor:
            for c in bits:
                with self.qc.if_test((c, 1)): getattr(self.qc, gate)(q)
        else:
            e = expr.lift(bits[0])
            for c in bits[1:]: e = expr.bit_xor(e, expr.lift(c))
            with self.qc.if_test(e): getattr(self.qc, gate)(q)
    def window(self, qubits):
        slot = self.slot if self.sim else max(self.timing.slot(q) for q in qubits)
        if not slot > 0:
            raise RuntimeError("backend target reports no measurement duration; cannot size the window")
        tau_w = M_REF * slot + (2 * self.timing.dt if self.sim else TAU_FF_ASSUMED)
        pad = max(M_REF - self.M, 0) * slot if self.pad else 0.0
        total = pad + (self.L - 1) * tau_w
        self.meta.update({"pad_s": pad, "delta_s": (self.L - 1) * tau_w, "tau_w_s": tau_w, "echo": self.echo})
        self.qc.barrier(*qubits)
        if self.sim:
            k = int(round(total / self.timing.dt))
            if self.echo:
                for q in qubits:
                    for part in self.echo_seq(q, k, 1):
                        if part == "x": self.qc.x(q); self.qc.barrier(q)
                        else:
                            for _ in range(part): self.qc.id(q)
            else:
                for _ in range(k):
                    for q in qubits: self.qc.id(q)
            if self.interaction and self.M > 1:
                from qiskit.circuit.library import UnitaryGate
                nwin = int(round((self.L - 1) * tau_w / self.timing.dt))
                for _ in range(nwin * (self.M - 1) // 2):
                    self.qc.append(UnitaryGate(np.eye(2), label="idx"), [self.spec])
        else:
            n = self.timing.to_dt(total); self.meta["window_dt"] = n
            if self.echo:
                for q in qubits:
                    for part in self.echo_seq(q, n, self.timing.gran):
                        if part == "x": self.qc.x(q); self.qc.barrier(q)
                        elif part > 0: self.qc.delay(max(part, self.timing.minlen), q, unit="dt")
            elif n > 0:
                for q in qubits: self.qc.delay(n, q, unit="dt")
        self.qc.barrier(*qubits)

    @staticmethod
    def echo_seq(q, n, gran=1):
        """Staggered echo over a free-evolution window of n time units on chain position q:
        even positions  d(n/2) X d(n/2) X;   odd positions  d(n/4) X d(n/2) X d(n/4).
        Every qubit's static Z phase cancels, and so does static ZZ on every nearest-neighbour
        pair (the two frames' product is +,-,+,- in equal quarters). Each qubit gets exactly two
        X (net identity) at EVERY setting, including n = 0, so pulse count never co-scales with
        a knob; only free-evolution time scales with lambda_L. Added after Job 1 (DD off) showed
        the spectator rotating coherently, <X_s> = cos(~0.27 lambda_L)."""
        r = lambda v: (v // gran) * gran
        if q % 2 == 0:
            a = r(n // 2); return [a, "x", n - a, "x"]
        a, b = r(n // 4), r(n // 2); return [a, "x", b, "x", n - a - b]
    def final(self, spec):
        fin = ClassicalRegister(len(spec), "fin"); self.qc.add_register(fin); fmap = {}
        for i, (q, b, lab) in enumerate(spec):
            if b == "X": self.qc.h(q)
            r = int(self.rng.integers(2))
            if r: self.qc.x(q)
            self.qc.measure(q, fin[i]); fmap[lab] = [i, r]
        self.meta["fin_map"] = fmap

def probe(ctx):
    t, a, s = 0, 1, 2; qc = ctx.qc
    qc.h(s); qc.h(a); ctx.cz(a, t)
    bits, R = ctx.mcm(a, idle=[t, s]); ctx.window([t, a, s])
    ctx.cond("x", t, bits, R)
    ctx.final([(s, "X", "s"), (t, "Z", "t"), (a, "Z", "a")])

def teleport(ctx, theta=np.pi / 3):
    qc = ctx.qc; qc.ry(theta, 0); qc.h(5)
    for x, y in [(1, 2), (3, 4)]: qc.h(x); ctx.cx(x, y)
    for src, b1, b2 in [(0, 1, 2), (2, 3, 4)]:
        ctx.cx(src, b1); qc.h(src)
        idle = [q for q in range(6) if q not in (src, b1)]
        bz, Rz = ctx.mcm(src, idle); bx, Rx = ctx.mcm(b1, idle)
        ctx.window(list(range(6)))
        ctx.cond("x", b2, bx, Rx); ctx.cond("z", b2, bz, Rz)
    qc.ry(-theta, 4)
    ctx.final([(4, "Z", "out"), (5, "X", "s")])

def ghz(ctx):
    qc = ctx.qc; data, anc, sp = [0, 2, 4, 6], [1, 3, 5], 7
    qc.h(sp)
    for d in data: qc.h(d)
    for i, a in enumerate(anc): ctx.cx(data[i], a); ctx.cx(data[i + 1], a)
    par = [ctx.mcm(a, idle=data + [sp]) for a in anc]
    ctx.window(list(range(8)))
    bits, R = [], 0
    for k in range(1, 4):
        bits = bits + par[k - 1][0]; R ^= par[k - 1][1]
        ctx.cond("x", data[k], bits, R)
    ctx.final([(d, "X", f"d{i}") for i, d in enumerate(data)] + [(sp, "X", "s")])

BENCH = {"probe": probe, "teleport": teleport, "ghz": ghz}

def build(bench, settings, K, timing, seed, sim=False, interaction=False, pad=True, unroll=False, echo=ECHO):
    out, bid = [], zlib.crc32(bench.encode())          # deterministic (not Python hash())
    for si, lam in enumerate(settings):
        for k in range(K):
            rng = np.random.default_rng([seed, bid, si, k])
            ctx = Ctx(bench, lam, timing, rng, sim=sim, pad=pad, interaction=interaction, echo=echo)
            ctx.unroll_xor = unroll; BENCH[bench](ctx)
            ctx.meta.update({"twirl": k, "seed": [seed, bid, si, k], "pad_on": pad})
            out.append((ctx.qc, ctx.meta))
    return out

def _err(t, name, qargs):
    try:
        p = t[name][tuple(qargs)]; return None if p is None else p.error
    except KeyError:
        return None

def calib_snapshot(backend, phys, target=None, when=None):
    t = target or backend.target; qp = t.qubit_properties or [None] * t.num_qubits
    when = when or datetime.datetime.now(datetime.timezone.utc)
    snap = {"utc": when.isoformat(), "backend": backend.name, "qubits": {}, "cz": {}}
    for q in phys:
        p = qp[q]
        snap["qubits"][str(q)] = {"t1": getattr(p, "t1", None), "t2": getattr(p, "t2", None),
            "freq": getattr(p, "frequency", None), "meas_err": _err(t, "measure", (q,)),
            "measure_2_err": _err(t, "measure_2", (q,)), "x_err": _err(t, "x", (q,))}
    for a, b in zip(phys, phys[1:]):
        snap["cz"][f"{a}-{b}"] = _err(t, "cz", (a, b)) or _err(t, "cz", (b, a))
    return snap

def layout_for(bench, chain):
    return chain[:N_Q[bench]]

QUICK_S_PER_SUBJOB, QUICK_S_PER_EXEC = 2.0, 0.00035   # IBM "Workload usage" quick formula (cited)
QUOTA_MARGIN = 1.15                                     # submit only if remaining quota >= 1.15 x estimate

def get_service():
    from qiskit_ibm_runtime import QiskitRuntimeService
    return QiskitRuntimeService()

def get_backend(args, name):
    """The real backend; with --fake NAME, an offline fake of it (rehearsal only, never results)."""
    if getattr(args, "fake", None):
        from qiskit_ibm_runtime import fake_provider
        return getattr(fake_provider, args.fake)()
    return get_service().backend(name)

def quick_cost(n_circ, shots, n_sub=1, s_per_exec=QUICK_S_PER_EXEC):
    return QUICK_S_PER_SUBJOB * n_sub + s_per_exec * n_circ * shots

def check_isa(logical, isa, bench):
    """Fail loudly if transpilation changed what the experiment means: inserted SWAPs, dropped
    conditionals, measurements or window delays."""
    lo, io = logical.count_ops(), isa.count_ops()
    two_q = sum(n for g, n in io.items() if g in ("cz", "ecr", "cx", "swap", "rzz"))
    problems = []
    if two_q != lo.get("cz", 0):
        problems.append(f"2q gates {two_q} != logical CZs {lo.get('cz', 0)} (routing inserted gates?)")
    if io.get("if_else", 0) != lo.get("if_else", 0):
        problems.append(f"if_else {io.get('if_else', 0)} != {lo.get('if_else', 0)}")
    meas = lambda o: o.get("measure", 0) + o.get("measure_2", 0)
    if meas(io) != meas(lo):
        problems.append(f"measurements {meas(io)} != {meas(lo)}")
    if io.get("delay", 0) != lo.get("delay", 0):
        problems.append(f"delays {io.get('delay', 0)} != {lo.get('delay', 0)} (window or echo segments changed)")
    if problems:
        raise RuntimeError(f"{bench}: transpiled circuit is not the designed experiment: " + "; ".join(problems))

def quota_remaining(service):
    """Remaining Open Plan seconds and a copy of the usage record that is safe to save: IBM's record
    carries the instance CRN (instance_id), which must never be written to a results file."""
    u = service.usage()
    rem = u.get("usage_remaining_seconds")
    if rem is None and u.get("usage_limit_seconds") is not None:
        rem = u["usage_limit_seconds"] - (u.get("usage_consumed_seconds") or 0)
    safe = {k: v for k, v in u.items()
            if k != "instance_id" and not (isinstance(v, str) and v.lower().startswith("crn:"))}
    return rem, safe

def run_job(job_name, groups, args, shots, s_per_exec=QUICK_S_PER_EXEC):
    """groups: list of (bench, [(circ, meta), ...], layout).
    Transpiles and checks every circuit; with --dry-run stops there. Otherwise checks the quota,
    submits one sub-job per benchmark in a Batch, and writes <job>_manifest.json (job ids + the
    twirl metadata needed to decode counts) straight after each submission, so a crash or a long
    queue never loses data. Then waits and collects, unless --no-wait."""
    from qiskit.transpiler import generate_preset_pass_manager
    name, chain, rep = resolve(args)
    backend = get_backend(args, name)
    assert "if_else" in backend.target.operation_names, "backend target lacks if_else"
    isa_groups, n_exec = [], 0
    for bench, items, layout in groups:
        pm = generate_preset_pass_manager(backend=backend, optimization_level=1, initial_layout=layout)
        isa = [pm.run(c) for c, _ in items]
        for (c, _), ic in zip(items, isa):
            check_isa(c, ic, bench)
        isa_groups.append((bench, isa, [m for _, m in items], layout))
        n_exec += len(isa) * shots
        print(f"{bench}: {len(isa)} circuits, max depth {max(c.depth() for c in isa)}, "
              f"cost estimate {quick_cost(len(isa), shots, 1, s_per_exec):.1f} s")
    est = quick_cost(n_exec // shots, shots, len(isa_groups), s_per_exec)
    print(f"{job_name}: {n_exec:.3g} executions, {len(isa_groups)} sub-jobs, estimate {est:.1f} QPU s")
    if getattr(args, "fake", None) and getattr(args, "mock", False) and not args.dry_run:
        return mock_run(job_name, isa_groups, backend, chain, args.mock_shots or shots, args, est)
    if args.dry_run or getattr(args, "fake", None):
        print("dry run: nothing submitted"); return {"estimate_s": est, "executions": n_exec}
    from qiskit_ibm_runtime import SamplerV2, Batch
    service = get_service()
    rem, usage = quota_remaining(service)
    print(f"quota remaining: {rem} s (needs {QUOTA_MARGIN} x {est:.1f} s)")
    if rem is not None and rem < QUOTA_MARGIN * est:
        sys.exit(f"QUOTA: {rem:.0f} s left < {QUOTA_MARGIN} x {est:.0f} s needed. Nothing submitted.")
    man = {"job": job_name, "backend": name, "chain": chain, "shots": shots,
           "measure_2_used": "measure_2" in backend.target.operation_names,
           "estimate_s": est, "quota_before": usage,
           "submitted_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "calibration_before": calib_snapshot(backend, chain), "subjobs": []}
    with Batch(backend=backend) as batch:
        sampler = SamplerV2(mode=batch)
        sampler.options.default_shots = shots
        sampler.options.twirling.enable_gates = False       # manual twirling instead
        sampler.options.twirling.enable_measure = False     # conditional MCMs cannot be auto-twirled
        sampler.options.dynamical_decoupling.enable = False # design choice: DD off
        for bench, isa, metas, layout in isa_groups:
            job = sampler.run([(c,) for c in isa], shots=shots)
            print(job_name, bench, "job id:", job.job_id(), "usage_estimation:", job.usage_estimation)
            man["subjobs"].append({"bench": bench, "job_id": job.job_id(), "layout": layout,
                                   "usage_estimation": job.usage_estimation, "metas": metas})
            json.dump(man, open(out_path(args, f"{job_name}_manifest.json"), "w"), default=str)
        json.dump({"job_ids": [s["job_id"] for s in man["subjobs"]]}, open(out_path(args, f"{job_name}_ids.json"), "w"))
    if getattr(args, "no_wait", False):
        print(f"submitted; collect later with: python collect.py {job_name}"); return man
    return collect(job_name, service, outdir=args.outdir)

def split_counts(counts, cregs):
    """Aer joins registers with spaces, last-created register first. -> {creg_name: counts}."""
    out = {r.name: {} for r in cregs}
    for key, n in counts.items():
        for r, part in zip(cregs[::-1], key.split(" ")):
            out[r.name][part] = out[r.name].get(part, 0) + n
    return out

def mock_run(job_name, isa_groups, backend, chain, shots, args, est):
    """Pipeline test only: Aer with the fake backend's noise model. Output is marked mock_aer and
    goes to --outdir; it is never a hardware result."""
    from qiskit_aer import AerSimulator
    if "rehearsal" not in str(args.outdir):
        sys.exit("--mock output must go to a rehearsal directory (--outdir rehearsal/...)")
    sim = AerSimulator.from_backend(backend)
    out = {"job": job_name, "backend": backend.name, "chain": chain, "shots": shots, "mock_aer": True,
           "measure_2_used": "measure_2" in backend.target.operation_names, "estimate_s": est,
           "submitted_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "calibration_before": calib_snapshot(backend, chain), "subjobs": []}
    for si, (bench, isa, metas, layout) in enumerate(isa_groups):
        res = sim.run(isa, shots=shots, seed_simulator=args.seed + si).result()
        recs = []
        for i, c in enumerate(isa):
            regs = split_counts(res.get_counts(i), c.cregs)
            rec = dict(metas[i]); rec["layout"] = layout
            rec["counts_fin"], rec["counts_mcm"] = regs["fin"], regs.get("mcm")
            recs.append(rec)
        n_exec = len(isa) * shots
        out["subjobs"].append({"bench": bench, "job_id": f"mock-{job_name}-{bench}",
                               "usage_s": QUICK_S_PER_SUBJOB + QUICK_S_PER_EXEC * n_exec,
                               "metrics": {"mock": True}, "records": recs})
        print(f"mock {job_name}/{bench}: {len(isa)} circuits x {shots} shots on Aer", flush=True)
    out["calibration_after"] = out["calibration_before"]
    json.dump(out, open(out_path(args, f"{job_name}_results.json"), "w"), default=str)
    print("saved", out_path(args, f"{job_name}_results.json"))
    return out

def collect(job_name, service=None, poll_s=60, outdir="."):
    """Rebuild <job>_results.json (the format analysis.py reads) from <job>_manifest.json.
    Blocks until every sub-job is final; raises if any sub-job failed."""
    import time
    man = json.load(open(out_path(outdir, f"{job_name}_manifest.json")))
    service = service or get_service()
    backend = service.backend(man["backend"])
    out = {k: man[k] for k in ("job", "backend", "chain", "shots", "measure_2_used", "estimate_s",
                               "submitted_utc", "calibration_before")}
    out["subjobs"] = []
    for sj in man["subjobs"]:
        job = service.job(sj["job_id"])
        while not job.in_final_state():
            print(f"{job_name}/{sj['bench']} {sj['job_id']}: {job.status()}", flush=True)
            time.sleep(poll_s)
        if str(job.status()) != "DONE":
            raise RuntimeError(f"{job_name}/{sj['bench']} {sj['job_id']} ended {job.status()}: "
                               f"{getattr(job, 'error_message', lambda: '')()}")
        res = job.result(); recs = []
        for i, pub in enumerate(res):
            d = pub.data; rec = dict(sj["metas"][i]); rec["layout"] = sj["layout"]
            rec["counts_fin"] = d.fin.get_counts()
            rec["counts_mcm"] = d.mcm.get_counts() if hasattr(d, "mcm") else None
            recs.append(rec)
        usage = 0
        for _ in range(10):                      # usage() reads 0 until IBM finishes accounting
            try:
                usage = job.usage()
            except Exception:
                usage = None
            if usage: break
            time.sleep(30)
        try:
            metrics = job.metrics()
        except Exception as e:
            metrics = {"error": str(e)}
        out["subjobs"].append({"bench": sj["bench"], "job_id": sj["job_id"], "usage_s": usage,
                               "metrics": metrics, "records": recs})
    end = None
    try:
        end = datetime.datetime.fromisoformat(str(out["subjobs"][-1]["metrics"]["timestamps"]["finished"]).replace("Z", "+00:00"))
        out["calibration_after"] = calib_snapshot(backend, man["chain"], backend.target_history(end), end)
    except Exception:
        out["calibration_after"] = calib_snapshot(backend, man["chain"])
    json.dump(out, open(out_path(outdir, f"{job_name}_results.json"), "w"), default=str)
    print("saved", out_path(outdir, f"{job_name}_results.json"))
    return out
