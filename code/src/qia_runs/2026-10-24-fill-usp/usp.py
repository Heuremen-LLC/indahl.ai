"""usp.py -- free calibration run for arXiv 2609.33255 (Univ. Sao Paulo + UFSCar), ibm_kingston. Own code; their files are read as data only.
Their question (v1): "Repeating the batches showed that the ibm_kingston result did not hold." / "three later batches, each on a new calibration and a
different set of qubits, removed the gap". By their released manifests the kingston batches are 3 stated records on 3 qubit sets, perfectly confounded:
A = batch 0 on (138,151,152,153), B = batches 1-3 on (143,142,141,140), C = batches 4-6 on (82,83,96,103). This run holds the calibration FIXED (one job)
and varies the qubit set and the builder: their exact submitted (ISA) circuits for all three sets, 20 non-mutant entries each (12 control = 3 builders x
4 cases, 4 null duplicates, 4 readout rows), in one job, two copies (G1, then G2 in reversed order), bracketed by our Part 0 sweep before and after.

  usp.py --known-good          their Table II and the per-record gaps reproduced from THEIR released counts
  usp.py --synth               planted worlds through the same analysis (false-call rate)
  usp.py --real                our hardware jobs
"""
import ast, glob, json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SETS = {'A': 'daimhhr9k43c73ag8js0', 'B': 'daj1asomhr3c73e8cbj0', 'C': 'daj6c9vi3e6s738psv0g'}   # one manifest per stated record / qubit set
CASES4 = ('0110', '0111'); CASES = ('10', '11', '0111', '0110'); BUILDERS = ('Qiskit', 'PennyLane', 'Cirq')
LEVEL = 0.99                         # band for every reading (fixed before any job)
B_BOOT = 4000

# ---------------- their files (data) ----------------
def manifest(tag): return json.load(open(f'{HERE}/theirs/{SETS[tag]}.manifest.json'))
def entries(tag):
    """the 20 non-mutant entries of a set's batch: (label, kind, builder, case, isa_qasm)"""
    out = []
    for e in manifest(tag)['entries']:
        if e['kind'] in ('control', 'null', 'readout'):
            a = e['attributes']; out.append((e['label'], e['kind'], a['grover.builder'], a['grover.marked_state'], a['grover.expected'], e['isa_qasm']))
    assert len(out) == 20, len(out)
    return out

def _num(s):
    """safe arithmetic on a QASM parameter: numbers, pi, + - * / and parentheses only"""
    t = ast.parse(s.replace('pi', str(math.pi)), mode='eval')
    def ev(n):
        if isinstance(n, ast.Expression): return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)): return float(n.value)
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd)): return -ev(n.operand) if isinstance(n.op, ast.USub) else ev(n.operand)
        if isinstance(n, ast.BinOp) and isinstance(n.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
            a, b = ev(n.left), ev(n.right)
            return {ast.Add: a + b, ast.Sub: a - b, ast.Mult: a * b, ast.Div: a / b}[type(n.op)]
        raise ValueError('refused expression: ' + s)
    return ev(t)

def parse_isa(src):
    """own line reader for their submitted OPENQASM 2 (ops: rz, sx, x, cz, measure, barrier, delay*). Returns a QuantumCircuit on 156 qubits."""
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    from qiskit.circuit import Delay
    import re
    qr = None; cr = None; qc = None; ops = []
    for line in src.split('\n'):
        l = line.strip()
        if not l or l.startswith('//') or l.startswith('OPENQASM') or l.startswith('include') or l.startswith('opaque'): continue
        m = re.match(r'qreg\s+q\[(\d+)\];', l)
        if m: qr = QuantumRegister(int(m.group(1)), 'q'); continue
        m = re.match(r'creg\s+(\w+)\[(\d+)\];', l)
        if m: cr = ClassicalRegister(int(m.group(2)), m.group(1)); continue
        ops.append(l)
    qc = QuantumCircuit(qr, cr); qi = lambda t: int(re.match(r'q\[(\d+)\]', t.strip()).group(1))
    for l in ops:
        l = l.rstrip(';')
        m = re.match(r'measure\s+q\[(\d+)\]\s*->\s*\w+\[(\d+)\]', l)
        if m: qc.measure(int(m.group(1)), int(m.group(2))); continue
        m = re.match(r'([a-z_0-9]+)(?:\(([^)]*)\))?\s+(.+)', l)
        if not m: raise ValueError('unparsed: ' + l)
        name, par, args = m.group(1), m.group(2), [qi(a) for a in m.group(3).split(',')]
        if name == 'rz': qc.rz(_num(par), args[0])
        elif name == 'sx': qc.sx(args[0])
        elif name == 'x': qc.x(args[0])
        elif name == 'cz': qc.cz(args[0], args[1])
        elif name == 'barrier': qc.barrier(args)
        elif name.startswith('delay'): qc.append(Delay(int(round(_num(par))), 'dt'), [args[0]])
        else: raise ValueError('op not allowed: ' + name)
    return qc

def success(counts, expected):
    """their definition: keys are q0-right, expected is written q0-left; success = counts of the reversed key / total"""
    tot = sum(counts.values()); return sum(c for k, c in counts.items() if k[::-1] == expected) / tot, tot

# ---------------- the readings ----------------
def table(rows):
    """rows: list of dict(set, copy, kind, builder, case, expected, counts) -> P[(set, copy, kind, builder, case)] = (p, n)"""
    return {(r['set'], r['copy'], r['kind'], r['builder'], r['case']): success(r['counts'], r['expected']) for r in rows}

def excess_var(P, sets, copies):
    """within-job variance beyond shot noise, from their built-in duplicate (Qiskit control vs Qiskit null), pooled over sets, cases, copies"""
    d2, vb = [], []
    for s in sets:
        for c in copies:
            for case in CASES:
                (p1, n1), (p2, n2) = P[(s, c, 'control', 'Qiskit', case)], P[(s, c, 'null', 'Qiskit', case)]
                d2.append((p1 - p2) ** 2); vb.append(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    return max(0.0, float(np.mean(d2) - np.mean(vb))), float(np.sqrt(np.mean(d2))), len(d2)

def boot_gap(P, s, copies, ev, rng, B=B_BOOT, b1='Qiskit', b2='PennyLane'):
    """gap_s = mean over the 4q cases of p(b1) - p(b2), pooled over copies. Parametric bootstrap: binomial shots plus the measured
    per-circuit excess variance ev/2 (half of the duplicate-pair excess goes to each circuit)."""
    draws = np.zeros(B); point = 0.0
    for case in CASES4:
        for c in copies:
            for sign, b in ((1, b1), (-1, b2)):
                p, n = P[(s, c, 'control', b, case)]
                point += sign * p
                x = rng.binomial(n, p, B) / n + rng.normal(0, math.sqrt(ev / 2), B)
                draws += sign * x
    k = len(CASES4) * len(copies)
    return point / k, draws / k

def four(lo, hi):
    return 'ABOVE' if lo > 0 else 'BELOW' if hi < 0 else 'CONSISTENT'

def readings(P, copies=(1, 2), rng=None, quiet=False):
    rng = rng or np.random.default_rng(20261024); a = (1 - LEVEL) / 2
    ev, rms, npair = excess_var(P, 'ABC', copies)
    out = {'excess_var': ev, 'dup_rms': rms, 'npair': npair}
    if not quiet: print(f'  within-job duplicate check (Qiskit control vs null, {npair} pairs): rms difference {rms:.4f}; excess variance beyond shots {ev:.2e}')
    G = {}
    for s in 'ABC':
        pt, dr = boot_gap(P, s, copies, ev, rng); lo, hi = np.quantile(dr, [a, 1 - a]); o = four(lo, hi)
        if len(copies) == 2:
            p1, d1 = boot_gap(P, s, (copies[0],), ev, rng); p2, d2 = boot_gap(P, s, (copies[1],), ev, rng)
            gl, gh = np.quantile(d1 - d2, [a, 1 - a])
            if gl > 0 or gh < 0: o = 'CANNOT_TELL'
            cg = (p1 - p2, gl, gh)
        else: cg = None
        G[s] = (pt, lo, hi, o, cg, dr)
        if not quiet:
            print(f'  R1 set {s}: Qiskit - PennyLane, mean of 4q cases {pt:+.3f} [{lo:+.3f}, {hi:+.3f}] -> {o}' + (f'   (copy gap {cg[0]:+.3f} [{cg[1]:+.3f}, {cg[2]:+.3f}])' if cg else ''))
    for x, y in (('A', 'C'), ('B', 'C'), ('A', 'B')):
        d = G[x][5] - G[y][5]; lo, hi = np.quantile(d, [a, 1 - a])
        G[f'{x}-{y}'] = (G[x][0] - G[y][0], lo, hi, four(lo, hi))
        if not quiet: print(f'  R2 contrast gap_{x} - gap_{y} {G[x][0] - G[y][0]:+.3f} [{lo:+.3f}, {hi:+.3f}] -> {four(lo, hi)}')
    dall = (G['A'][5] + G['B'][5] + G['C'][5]) / 3; lo, hi = np.quantile(dall, [a, 1 - a])
    G['ALL'] = ((G['A'][0] + G['B'][0] + G['C'][0]) / 3, lo, hi, four(lo, hi))
    if not quiet: print(f'  R2 pooled gap over the three sets {G["ALL"][0]:+.3f} [{lo:+.3f}, {hi:+.3f}] -> {G["ALL"][3]}')
    ct = ''.join(s for s in 'ABC' if G[s][3] == 'CANNOT_TELL'); cA, cB, cAB = G['A-C'][3], G['B-C'][3], G['A-B'][3]
    pat = ''.join(s for s in 'ABC' if G[s][3] == 'ABOVE')
    # set dependence is claimed ONLY from a resolved contrast; a uniform gap is read from the pooled value (fixed before any job, after synth v1)
    if ct: verdict = 'CANNOT_TELL: copies disagree on set(s) ' + ct; cls = 'CANNOT_TELL'
    elif cA == 'ABOVE' and cB == 'ABOVE':
        cls = 'BOTH' if G['C'][3] == 'ABOVE' else 'SET'
        verdict = ('BOTH: a gap on every set plus extra on A and B (calibration fixed)' if cls == 'BOTH' else
                   'SET: A and B carry the gap and C does not, with the calibration fixed -- the qubit set (with their placement) explains their batches; no calibration change needed')
    elif 'ABOVE' in (cA, cB, cAB) or 'BELOW' in (cA, cB, cAB):
        cls = 'OTHER_SET'; verdict = f'SET-DEPENDENT, not their A,B-vs-C split: contrasts A-C {cA}, B-C {cB}, A-B {cAB}'
    elif G['ALL'][3] == 'ABOVE':
        cls = 'BUILDER'; verdict = f'BUILDER: one gap common to all three sets ({G["ALL"][0]:+.3f} [{G["ALL"][1]:+.3f}, {G["ALL"][2]:+.3f}]), no set difference resolved -- "calibration/qubit choice removed it" is BELOW for today'
    elif G['ALL'][3] == 'BELOW':
        cls = 'REVERSED'; verdict = 'REVERSED: PennyLane ahead on the pooled sets, no set difference resolved'
    else:
        cls = 'NONE'; verdict = f'NONE: no gap and no set difference resolved (pooled {G["ALL"][0]:+.3f} [{G["ALL"][1]:+.3f}, {G["ALL"][2]:+.3f}]) -- CONSISTENT with the gap being tied to their past record/placement; CANNOT_TELL between calibration and qubit choice'
    out['G'] = {k: v[:5] for k, v in G.items()}; out['pattern'] = pat; out['cls'] = cls; out['verdict'] = verdict
    if not quiet: print('  R1/R2 PATTERN:', verdict)
    return out

# ---------------- known-good: their released counts ----------------
PRINTED = {('readout', '10'): 0.975, ('readout', '11'): 0.983, ('readout', '0111'): 0.942, ('readout', '0110'): 0.955,
           ('Qiskit', '10'): 0.958, ('Qiskit', '11'): 0.963, ('Qiskit', '0111'): 0.523, ('Qiskit', '0110'): 0.543,
           ('PennyLane', '10'): 0.954, ('PennyLane', '11'): 0.952, ('PennyLane', '0111'): 0.451, ('PennyLane', '0110'): 0.384,
           ('Cirq', '10'): 0.958, ('Cirq', '11'): 0.944, ('Cirq', '0111'): 0.481, ('Cirq', '0110'): 0.457}   # their Table II, ibm_kingston
def their_rows():
    rows = []; jobs = sorted((json.load(open(f)) for f in glob.glob(f'{HERE}/theirs/polled/*.polled.json')), key=lambda d: d['submitted_at'])
    rec = {0: 'A', 1: 'B', 2: 'B', 3: 'B', 4: 'C', 5: 'C', 6: 'C'}
    for j, d in enumerate(jobs):
        for e in d['entries']:
            if e['kind'] in ('control', 'null', 'readout'):
                a = e['attributes']; rows.append(dict(set=rec[j], copy=j, kind=e['kind'], builder=a['grover.builder'], case=a['grover.marked_state'],
                                                      expected=a['grover.expected'], counts=e['counts']))
    return rows, jobs

def known_good():
    rows, jobs = their_rows(); P = table(rows); fails = 0
    print('KNOWN-GOOD: their Table II (first valid batch, ibm_kingston) from their released counts through this code')
    for (b, c), pv in PRINTED.items():
        kind = 'readout' if b == 'readout' else 'control'; v = P[('A', 0, kind, b, c)][0]; ok = abs(round(v, 3) - pv) < 0.0006; fails += not ok
        print(f'   {b:9s} {c:5s} printed {pv:.3f} ours {v:.4f} {"PASS" if ok else "FAIL"}')
    print(f'   Table II cells: {16 - fails}/16 PASS')
    g = lambda s, cs: np.mean([P[(s, c, 'control', 'Qiskit', '0110')][0] - P[(s, c, 'control', 'PennyLane', '0110')][0] for c in cs])
    print(f'   their own text: Qiskit - PennyLane on 0110, batch 1 = {g("A", [0]):+.3f} (printed 0.16)')
    for s, cs in (('A', [0]), ('B', [1, 2, 3]), ('C', [4, 5, 6])):
        gg = np.mean([np.mean([P[(s, c, 'control', 'Qiskit', k)][0] - P[(s, c, 'control', 'PennyLane', k)][0] for k in CASES4]) for c in cs])
        print(f'   record/set {s} (their batches {cs}): Qiskit - PennyLane, mean of 4q cases {gg:+.3f}')
    print('KNOWN-GOOD:', 'PASS' if fails == 0 else 'FAIL'); return fails == 0

# ---------------- synthetic ----------------
def synth(ndraw=60, shots=2048, seed=11):
    """planted worlds on THEIR Table II baselines; per-circuit drift between copies sd 0.008 (not modelled by the binomial part: the
    duplicate-based excess term must absorb it). Worlds: NEITHER (no gap), BUILDER (gap 0.10 all sets), SET (0.10 on A,B only),
    BOTH (0.05 all + 0.08 extra on A,B), SMALL (0.015 all: below resolution)."""
    rng = np.random.default_rng(seed)
    base = {(b, c): PRINTED[(b, c)] for b in BUILDERS for c in CASES}; base.update({('readout', c): PRINTED[('readout', c)] for c in CASES})
    worlds = {'NEITHER': dict(A=0, B=0, C=0), 'BUILDER': dict(A=.10, B=.10, C=.10), 'SET': dict(A=.10, B=.10, C=0),
              'BOTH': dict(A=.13, B=.13, C=.05), 'SMALL': dict(A=.015, B=.015, C=.015)}
    tally = {}
    for w, gap in worlds.items():
        false = miss = ncall = 0; pats = {}; ncls = cls_false = cls_wrong = 0; clsc = {}
        for k in range(ndraw):
            rows = []
            for s in 'ABC':
                off = rng.normal(0, 0.03)                                   # set-level offset (qubit quality), same for all builders
                for c in (1, 2):
                    for case in CASES:
                        for kind, b in [('control', x) for x in BUILDERS] + [('null', 'Qiskit'), ('readout', 'readout')]:
                            p = base[(b, case)] + (off if b != 'readout' else 0)
                            mid = (base[('Qiskit', case)] + base[('PennyLane', case)]) / 2
                            if case in CASES4 and b in ('Qiskit', 'PennyLane'):  # replace their gap by the planted one, around the pair mean
                                p = mid + off + (gap[s] / 2 if b == 'Qiskit' else -gap[s] / 2)
                            p = float(np.clip(p + rng.normal(0, 0.008), 0.01, 0.99))
                            exp = '1' * len(case) if False else case
                            n1 = rng.binomial(shots, p)
                            rows.append(dict(set=s, copy=c, kind=kind, builder=b, case=case, expected=case, counts={case[::-1]: int(n1), 'x' * len(case): int(shots - n1)}))
            r = readings(table(rows), rng=np.random.default_rng(k), quiet=True)
            pats[r['pattern']] = pats.get(r['pattern'], 0) + 1
            for s in 'ABC':
                o = r['G'][s][3]; ncall += 1
                if gap[s] == 0 and o in ('ABOVE', 'BELOW'): false += 1
                if gap[s] >= 0.05 and o != 'ABOVE': miss += 1
                if gap[s] > 0 and o == 'BELOW': false += 1
            for x, y in (('A', 'C'), ('B', 'C'), ('A', 'B')):
                o = r['G'][f'{x}-{y}'][3]; ncall += 1; dlt = gap[x] - gap[y]
                if dlt == 0 and o != 'CONSISTENT': false += 1
            ok_cls = {'NEITHER': ('NONE',), 'BUILDER': ('BUILDER',), 'SET': ('SET',), 'BOTH': ('BOTH',), 'SMALL': ('NONE', 'BUILDER')}[w]
            ncls += 1; cls_false += r['cls'] not in ok_cls and r['cls'] not in ('NONE', 'BUILDER') if w == 'SMALL' else 0
            cls_wrong += r['cls'] not in ok_cls; clsc[r['cls']] = clsc.get(r['cls'], 0) + 1
        tally[w] = (false, miss, ncall, pats, cls_wrong, ncls)
        print(f'  world {w:8s} planted gaps {gap}: per-reading false calls {false}/{ncall}, misses {miss}; VERDICT wrong {cls_wrong}/{ncls} {clsc}')
    F = sum(t[0] for t in tally.values()); N = sum(t[2] for t in tally.values())
    W = sum(t[4] for t in tally.values()); NW = sum(t[5] for t in tally.values())
    print(f'  SYNTHETIC per-reading false-call rate {F}/{N} = {100 * F / N:.1f}%; VERDICT wrong {W}/{NW} = {100 * W / NW:.1f}%  (band {LEVEL:.0%}, {ndraw} draws per world, {shots} shots per circuit per copy)')
    return F / N

# ---------------- real ----------------
def real():
    rows = []
    for c, tag in ((1, 'G1'), (2, 'G2')):
        f = f'{HERE}/raw_usp_{tag}.json'
        if not os.path.exists(f): print('INCOMPLETE: missing', tag); return
        for r in json.load(open(f)): r['copy'] = c; rows.append(r)
    P = table(rows)
    print('== ibm_kingston, our jobs (calibration fixed within each job; their exact submitted circuits on sets A, B, C)')
    for s in 'ABC':
        line = []
        for case in CASES:
            v = [np.mean([P[(s, c, 'control', b, case)][0] for c in (1, 2)]) for b in BUILDERS]; ro = np.mean([P[(s, c, 'readout', 'readout', case)][0] for c in (1, 2)])
            line.append(f'{case}: Q {v[0]:.3f} P {v[1]:.3f} C {v[2]:.3f} ro {ro:.3f}')
        print(f'  set {s}: ' + ' | '.join(line))
    res = readings(P)
    json.dump({k: v for k, v in res.items() if k != 'G'} | {'G': {k: [float(x) if not isinstance(x, (str, tuple)) else x for x in v[:4]] for k, v in res['G'].items()}},
              open(f'{HERE}/readings_usp.json', 'w'), indent=1, default=str)
    stated_vs_delivered()

def stated_vs_delivered():
    """R3 (supporting, descriptive): delivered vs stated on the 12 qubits and the path couplers, from our committed Part 0 sweep run before (usp_pre)
    and after (usp_post) the G jobs (sweep_run/fire_sweep_rep.py, sweep.py unchanged)."""
    SW = os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'); sys.path.insert(0, SW); import sweep
    units = {}
    for s in 'ABC':
        qs = set(); cz = set()
        for lab, kind, b, case, exp, src in entries(s):
            qc = parse_isa(src)
            for ins in qc.data:
                if ins.operation.name == 'cz': cz.add(tuple(sorted(qc.find_bit(q).index for q in ins.qubits)))
                if ins.operation.name == 'measure': qs.add(qc.find_bit(ins.qubits[0]).index)
        units[s] = (sorted(qs), sorted(cz))
    for tag in ('usp_pre', 'usp_post'):
        jf = f'{SW}/job_sweep_ibm_kingston_{tag}.json'
        if not os.path.exists(f'{SW}/raw_sweep_ibm_kingston_{tag}.npz'): print('  R3', tag, 'not available'); continue
        rec = json.load(open(jf)); z = np.load(f'{SW}/raw_sweep_ibm_kingston_{tag}.npz'); props = json.load(open(f'{SW}/props_sweep_ibm_kingston_{tag}.json'))
        st_q, st_g = sweep.stated(props); data = [{r: z[f'{r}_{i}'] for r in ('a', 'b', 'c') if f'{r}_{i}' in z} for i in range(len(rec['meta']))]
        import io, contextlib
        with contextlib.redirect_stdout(io.StringIO()): res = sweep.analyze(rec['meta'], data, rec['n'], rec['pulses'], st_q, st_g, tag)
        print(f'  R3 {tag} (IBM record {props["last_update_date"]}):')
        for s in 'ABC':
            qs, cz = units[s]
            sg = lambda e: st_g.get(('cz', e), st_g.get(('cz', e[::-1])))
            czr = [(e, res['epl'].get(e) or res['epl'].get(e[::-1]), sg(e)) for e in cz]
            sxr = [(q, res['epg'].get(q), st_g.get(('sx', (q,)))) for q in qs]
            fmt = lambda v: 'nofit' if v is None else f'{v:.2e}'
            print(f'     set {s}: CZ ' + ', '.join(f'{e[0]}-{e[1]} delivered {fmt(d)} stated {fmt(t)}' for e, d, t in czr)
                  + f' | mean delivered {np.mean([d for _, d, _ in czr if d]) if any(d for _, d, _ in czr) else float("nan"):.2e} stated {np.mean([t for _, _, t in czr if t]):.2e}')
            print(f'            sx delivered/stated ' + ', '.join(f'q{q} {d / t:.2f}' if d and t else f'q{q} n/a' for q, d, t in sxr))

if __name__ == '__main__':
    a = sys.argv
    if '--known-good' in a: known_good()
    elif '--synth' in a: synth()
    elif '--real' in a: real()
    else: print(__doc__)
