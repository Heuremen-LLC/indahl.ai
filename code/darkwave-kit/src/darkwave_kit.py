#!/usr/bin/env python3
"""darkwave_kit.py -- Darkwave Correction Kit, Heuremen LLC (https://indahl.ai/darkwave).

A mid-circuit readout can turn the phase of the untouched qubits next to it. This kit measures that turn on your own IBM Quantum account,
one value per untouched qubit in degrees per readout, and adds the matching virtual-Z correction to your own circuits. The method is the
one in "A Readout's Kick Is a Turn" (doi:10.5281/zenodo.23843468). It names no mechanism for the turn.

  SELF-TEST   python darkwave_kit.py selftest                                     (simulator only, needs qiskit-aer)
  MEASURE     python darkwave_kit.py measure --backend ibm_kingston --readout 5,6,7 --targets 4,8,9 --check
              python darkwave_kit.py measure --backend ibm_kingston --readout 5,6,7 --targets 4,8,9 --yes
  APPLY       python darkwave_kit.py apply --table kicks/kick_table_ibm_kingston_....json my_circuit.qpy corrected.qpy

measure: 8 circuits in one job. Each puts the target qubits on the equator, then runs a block of N steps (N = 1 and N = 4) in which the
readout qubits are either measured (arm M) or idle for exactly the readout duration (arm D, the comparison built for M). The targets are
then read in the X and Y bases. The phase difference M minus D, divided by N, is the kick per readout. N = 1 places the N = 4 value on the
right turn of the circle. A 95 % band comes from 2,000 resamples of the counts (binomial, seed 41). Each qubit gets one of four outcomes
against zero: ABOVE, BELOW, CONSISTENT (band inside plus or minus --margin degrees, default 0.5) or CANNOT_TELL. The coherence kept
(M against D) is printed beside it, because a phase correction cannot give back lost coherence.
The table holds for the readout set, backend and calibration it was measured with. IBM recalibrates during the day, so measure it close
to your run and keep it with your data.

apply: after each group of mid-circuit measurements on the table's readout qubits, adds rz(-kick) to each target qubit in the table.
A group is a run of consecutive measure instructions (barriers allowed between them) in which no qubit is read twice. A qubit read again
starts a new group. The table assumes the whole readout set is measured together in each group, as when it was measured. Measurements at the very end of a circuit get no correction. Circuits must be
on physical qubit numbers (transpiled with the layout the table was measured on). Readouts inside if/else or loop blocks are not
corrected and are counted in a warning. The input file is opened read-only and the output is written to a new file.
Your account: qiskit-ibm-runtime's saved account (QiskitRuntimeService.save_account). Python 3.10 or later.
Free to run and cite with attribution to Heuremen LLC. See LICENSE.txt."""
import argparse, json, os, sys, hashlib, datetime as dt
import numpy as np
NAME = 'Darkwave Correction Kit'; ORG = 'Heuremen LLC'; SITE = 'https://indahl.ai/darkwave'
NS = (1, 4); ARMS = ('D', 'M'); BASES = ('X', 'Y')
def wrapd(x): return (x + 180.0) % 360.0 - 180.0
def near(x, ref): return x + 360.0 * np.round((ref - x) / 360.0)
def build(n, readout, targets, L_dt, N, arm, basis, synth=None):
    """synth: {qubit: deg} adds that rz after each step in arm M (self-test only, stands in for a readout's turn)"""
    from qiskit import QuantumCircuit, ClassicalRegister
    qc = QuantumCircuit(n); regs = [ClassicalRegister(len(readout), f'm{k}') for k in range(N)]; fin = ClassicalRegister(len(targets), 'fin')
    for r in regs: qc.add_register(r)
    qc.add_register(fin)
    for q in targets: qc.sx(q)
    qc.barrier()
    for k in range(N):
        if arm == 'D':
            for q in readout: qc.delay(L_dt, q, unit='dt')
        else:
            qc.measure(readout, regs[k])
            if synth:
                for q in targets: qc.rz(np.radians(synth.get(q, 0.0)), q)
        qc.barrier()
    for q in targets:
        if basis == 'X': qc.h(q)
        else: qc.sdg(q); qc.h(q)
    qc.measure(targets, fin)
    return qc
def keys(): return [(N, a, b) for N in NS for a in ARMS for b in BASES]
def p1_from(bitstrings, m):
    c = np.zeros(m); t = 0
    for s, v in bitstrings.items():
        s = s.replace(' ', '')[::-1]; t += v
        for i in range(m):
            if s[i] == '1': c[i] += v
    return c, t
def analyse(counts, targets, margin, seed=41, B=2000):
    """counts: {(N, arm, basis): (ones per target, shots)} -> per-target kick, band, outcome, coherence kept"""
    rng = np.random.default_rng(seed); m = len(targets)
    def kick(P):
        ph = {}; r = {}
        for N in NS:
            for a in ARMS:
                x = 1 - 2 * P[(N, a, 'X')]; y = 1 - 2 * P[(N, a, 'Y')]
                ph[(N, a)] = np.degrees(np.arctan2(y, x)); r[(N, a)] = np.hypot(x, y)
        t1 = wrapd(ph[(1, 'M')] - ph[(1, 'D')]); t4 = near(wrapd(ph[(4, 'M')] - ph[(4, 'D')]), 4 * t1)
        return t4 / 4, t1, r[(4, 'M')] / np.where(r[(4, 'D')] > 0, r[(4, 'D')], np.nan), r[(4, 'D')]
    P = {k: c / s for k, (c, s) in counts.items()}
    k4, k1, keep, rD = kick(P)
    bs = []
    for _ in range(B):
        Pb = {k: rng.binomial(s, np.clip(c / s, 0, 1)) / s for k, (c, s) in counts.items()}
        bs.append(kick(Pb)[0])
    bs = np.array(bs); lo, hi = np.percentile(bs, 2.5, axis=0), np.percentile(bs, 97.5, axis=0)
    out = {}
    for i, q in enumerate(targets):
        oc = 'ABOVE' if lo[i] > 0 else 'BELOW' if hi[i] < 0 else 'CONSISTENT' if (lo[i] >= -margin and hi[i] <= margin) else 'CANNOT_TELL'
        out[int(q)] = dict(deg_per_readout=round(float(k4[i]), 4), band95=[round(float(lo[i]), 4), round(float(hi[i]), 4)], outcome=oc,
                           deg_per_readout_n1=round(float(k1[i]), 4), coherence_kept=None if not np.isfinite(keep[i]) else round(float(keep[i]), 4), coherence_idle=round(float(rD[i]), 4))
    return out
def ints(s, name):
    try: v = [int(x) for x in s.split(',') if x.strip()]
    except ValueError: sys.exit(f'{name} takes qubit numbers separated by commas, for example 4,8,9')
    if not v: sys.exit(f'{name} is empty')
    if len(set(v)) != len(v): sys.exit(f'{name} lists a qubit twice')
    return v
def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()
def save_table(out_dir, backend, readout, targets, L_dt, shots, job_id, table, margin, extra=None):
    os.makedirs(out_dir, exist_ok=True); t = dt.datetime.now(dt.timezone.utc)
    p = os.path.join(out_dir, f'kick_table_{backend}_{t:%Y%m%dT%H%M%SZ}.json')
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(dict(kit=NAME, by=ORG, site=SITE, backend=backend, measured_utc=t.isoformat(), job_id=job_id, readout=readout, targets=targets,
                       readout_duration_dt=L_dt, shots=shots, margin_deg=margin, steps=list(NS),
                       note='Kick per readout in degrees for this readout set, backend and calibration. Correction = rz(-kick) on each target after each readout.',
                       kicks=table, **(extra or {})), f, indent=1)
    return p
def cmd_measure(a):
    readout, targets = ints(a.readout, '--readout'), ints(a.targets, '--targets')
    if set(readout) & set(targets): sys.exit('a qubit cannot be in both --readout and --targets')
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    from qiskit import transpile
    svc = QiskitRuntimeService(); b = svc.backend(a.backend); n = b.num_qubits
    bad = [q for q in readout + targets if q >= n]
    if bad: sys.exit(f'{a.backend} has {n} qubits, these are out of range: {bad}')
    L_dt = max(int(round(b.target['measure'][(q,)].duration / b.dt)) for q in readout)
    circs = {k: build(n, readout, targets, L_dt, *k) for k in keys()}
    tc = {k: transpile(c, b, optimization_level=1, initial_layout=list(range(n)), seed_transpiler=31) for k, c in circs.items()}
    for k, t in tc.items():
        if t.layout is not None and list(t.layout.final_index_layout()) != list(range(n)): sys.exit(f'transpiler moved the qubits in {k}, nothing submitted')
    for N in NS:   # the two arms must take the same time on every target, or the comparison is not like for like
        dur = {}
        for arm in ARMS:
            sc = transpile(tc[(N, arm, 'X')], b, optimization_level=0, scheduling_method='alap', initial_layout=list(range(n)))
            dur[arm] = [sc.qubit_duration(q) for q in targets]
        if dur['D'] != dur['M']: sys.exit(f'N={N}: idle and readout arms differ in time on the targets ({dur}), nothing submitted')
        print(f'N={N}: idle and readout arms take {dur["D"][0]} dt on every target')
    print(f'{NAME} | {ORG} | {SITE}')
    print(f'{a.backend}: {len(tc)} circuits x {a.shots} shots, readout {readout}, targets {targets}, readout duration {L_dt} dt.')
    if a.check or not a.yes:
        print('Checks passed. Nothing has been submitted. Add --yes to submit one job. IBM bills it by its quantum seconds, shown on your plan after the job.')
        return
    print('Submitting one job.')
    smp = SamplerV2(mode=b)   # no dynamical decoupling and no twirling: either would change what happens during the idle arm's wait
    smp.options.dynamical_decoupling.enable = False; smp.options.twirling.enable_gates = False; smp.options.twirling.enable_measure = False
    job = smp.run([tc[k] for k in keys()], shots=a.shots); print('job', job.job_id()); res = job.result()
    counts = {}
    for k, r in zip(keys(), res):
        c, s = p1_from(r.data.fin.get_counts(), len(targets)); counts[k] = (c, s)
    tab = analyse(counts, targets, a.margin)
    p = save_table(a.out, a.backend, readout, targets, L_dt, a.shots, job.job_id(), tab, a.margin)
    for q, v in tab.items(): print(f'q{q}: {v["deg_per_readout"]:+.3f} deg per readout [{v["band95"][0]:+.3f}, {v["band95"][1]:+.3f}] {v["outcome"]}, coherence kept {v["coherence_kept"]:.3f}')
    print('table:', p)
def corrected(qc, readout, kicks, notes=None):
    R = set(readout); out = qc.copy_empty_like(); pending = set()
    idx = {q: i for i, q in enumerate(qc.qubits)}
    bad = [q for q in kicks if q >= qc.num_qubits]
    if bad: raise ValueError(f'the circuit has {qc.num_qubits} qubits and the table corrects qubits {bad}. Transpile the circuit to physical qubits first, with the layout the table was measured on')
    notes = notes if notes is not None else {}
    def flush():
        if pending != R: notes['partial'] = notes.get('partial', 0) + 1
        for q, k in kicks.items(): out.rz(-np.radians(k), q)
    def nested(op):
        return any(i.operation.name == 'measure' and {idx.get(x, -1) for x in i.qubits} & R for blk in getattr(op, 'blocks', ()) for i in blk.data)
    data = list(qc.data)
    for j, ins in enumerate(data):
        name = ins.operation.name; qs = [idx[x] for x in ins.qubits]
        if getattr(ins.operation, 'blocks', None) and nested(ins.operation): notes['nested'] = notes.get('nested', 0) + 1
        if name == 'measure' and set(qs) <= R:
            if set(qs) & pending: flush(); pending = set()   # a qubit read again starts a new readout: its group ends here
            pending |= set(qs); out.append(ins); continue
        if name == 'barrier' and pending: out.append(ins); continue
        if pending:
            if any(d.operation.name not in ('measure', 'barrier') for d in data[j:]): flush()
            pending = set()
        out.append(ins)
    return out
def cmd_apply(a):
    from qiskit import qpy
    import tempfile
    try: T = json.load(open(a.table, encoding='utf-8'))
    except (OSError, ValueError) as e: sys.exit(f'could not read the table {a.table}: {e}')
    if not isinstance(T, dict) or 'kicks' not in T or 'readout' not in T or 'deg_per_readout' not in next(iter(T['kicks'].values()), {}):
        sys.exit(a.table + ' is not a kick table from this kit (the study tables in examples/ use another format)')
    use = {int(q): v for q, v in T['kicks'].items() if not a.only_resolved or v.get('outcome') in ('ABOVE', 'BELOW')}
    kicks = {q: v['deg_per_readout'] for q, v in use.items()}
    unres = sorted(int(q) for q, v in T['kicks'].items() if v.get('outcome') == 'CANNOT_TELL')
    if not os.path.exists(a.input): sys.exit('no such file: ' + a.input)
    if os.path.exists(a.output):
        if os.path.samefile(a.input, a.output): sys.exit('the output is the input file. Write the corrected circuits to a new file')
        if not a.force: sys.exit(a.output + ' exists. Add --force to replace it')
    h0 = sha(a.input)
    with open(a.input, 'rb') as f: circs = qpy.load(f)
    notes = {}
    try: outc = [corrected(c, T['readout'], kicks, notes) for c in circs]
    except ValueError as e: sys.exit(str(e))
    d = os.path.dirname(os.path.abspath(a.output))
    if not os.path.isdir(d): sys.exit('no such folder: ' + d)
    fd, tmp = tempfile.mkstemp(dir=d, suffix='.qpy')
    with os.fdopen(fd, 'wb') as f: qpy.dump(outc, f)
    os.replace(tmp, a.output)
    added = [o.count_ops().get('rz', 0) - c.count_ops().get('rz', 0) for o, c in zip(outc, circs)]
    print(f'{NAME} | {ORG} | {SITE}')
    print(f'{len(outc)} circuit(s) written to {a.output}. rz added per circuit: {added}. Table: {T.get("backend", "?")}, measured {T.get("measured_utc", "?")}.')
    if unres: print(f'Qubits whose turn read CANNOT_TELL: {unres}. ' + ('They were left uncorrected (--only-resolved).' if a.only_resolved else 'They were corrected with their measured value. Use --only-resolved to correct only ABOVE and BELOW.'))
    if notes.get('partial'): print(f'WARNING: {notes["partial"]} readout group(s) measured only part of the readout set the table was measured with, and still got the full correction.')
    if notes.get('nested'): print(f'WARNING: {notes["nested"]} if/else or loop block(s) hold readouts on the readout set. Those readouts were not corrected.')
    h1 = sha(a.input); print(f'input sha256 before {h0}\ninput sha256 after  {h1} ({"unchanged" if h0 == h1 else "CHANGED"})')
def cmd_selftest(a):
    """Known answer on the simulator: plant a turn per readout (rz after each readout step), measure it, correct it, measure again."""
    from qiskit_aer import AerSimulator
    from qiskit import transpile
    sim = AerSimulator(); n = 7; readout = [0, 1]; targets = [2, 3, 4, 5, 6]; plant = {2: 7.5, 3: -12.0, 4: 0.0, 5: 31.0, 6: 62.0}; shots = 20000
    def run(corr=None):
        counts = {}
        for k in keys():
            qc = build(n, readout, targets, 160, *k, synth=plant)
            if corr is not None and k[1] == 'M': qc = corrected(qc, readout, corr)
            r = sim.run(transpile(qc, sim, seed_transpiler=31), shots=shots, seed_simulator=7).result().get_counts()
            counts[k] = p1_from_full(r, len(targets))
        return analyse(counts, targets, 0.5)
    for N in NS:   # the kit's own readout circuit, barriers between readouts and no planted rz: one correction per readout per target
        base = build(n, readout, targets, 160, N, 'M', 'X'); add = corrected(base, readout, {q: 1.0 for q in targets}).count_ops().get('rz', 0) - base.count_ops().get('rz', 0)
        good = add == N * len(targets); print(f'apply on a {N}-readout circuit: {add} rz added, want {N * len(targets)} {"ok" if good else "WRONG"}')
        if not good: print('SELFTEST FAILED'); sys.exit(1)
    tab = run(); ok = True
    for q in targets:
        v = tab[q]; good = abs(v['deg_per_readout'] - plant[q]) < 1.0; ok &= good
        print(f'q{q}: planted {plant[q]:+.2f}, measured {v["deg_per_readout"]:+.3f} [{v["band95"][0]:+.3f}, {v["band95"][1]:+.3f}] {v["outcome"]} {"ok" if good else "WRONG"}')
    tab2 = run({q: tab[q]['deg_per_readout'] for q in targets})
    for q in targets:
        v = tab2[q]; good = abs(v['deg_per_readout']) < 1.0; ok &= good
        print(f'q{q} after the correction: {v["deg_per_readout"]:+.3f} [{v["band95"][0]:+.3f}, {v["band95"][1]:+.3f}] {v["outcome"]} {"ok" if good else "WRONG"}')
    print('SELFTEST', 'PASSED' if ok else 'FAILED'); sys.exit(0 if ok else 1)
def p1_from_full(r, m):
    """Aer counts keys hold every register, last register first, space separated. fin is the last register added, so it comes first."""
    c = np.zeros(m); t = 0
    for s, v in r.items():
        fin = s.split(' ')[0][::-1]; t += v
        for i in range(m):
            if fin[i] == '1': c[i] += v
    return c, t
def main():
    ap = argparse.ArgumentParser(description=f'{NAME}, {ORG}'); sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('selftest')
    m = sub.add_parser('measure'); m.add_argument('--backend', required=True); m.add_argument('--readout', required=True); m.add_argument('--targets', required=True)
    m.add_argument('--shots', type=int, default=4000); m.add_argument('--margin', type=float, default=0.5); m.add_argument('--check', '--estimate', dest='check', action='store_true'); m.add_argument('--yes', action='store_true')
    m.add_argument('--out', default='kicks')
    p = sub.add_parser('apply'); p.add_argument('--table', required=True); p.add_argument('--only-resolved', action='store_true'); p.add_argument('--force', action='store_true'); p.add_argument('input'); p.add_argument('output')
    a = ap.parse_args(); {'selftest': cmd_selftest, 'measure': cmd_measure, 'apply': cmd_apply}[a.cmd](a)
if __name__ == '__main__': main()
