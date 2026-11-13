"""THE PARALLAX RUN (IBM half) -- 2026-09-28, Bones. Wayfinder's rain tank: the tape "inside" the tank was behind it, seen through the
water. Qubit readout is the same: we never see the qubit, only a resonator's echo through the fridge. Step to two viewpoints; the
difference between them is the measurement.

Raw readout dots (meas_type="kerneled": one complex I/Q point per qubit per shot), ~78 qubits side by side (every even qubit).
  J1  default shot spacing, 4000 shots: P0 (measure), P1 (X, measure), D0 (measure, measure), D1 (X, measure, measure)
  J2  shot spacing 20 us (short),  2000 shots: P0, P1      -> does the last shot's readout leave the qubit excited? (lens memory)
  J3  shot spacing 1 ms (long),    2000 shots: P0, P1
  J4  default spacing again,       2000 shots: P0, P1      -> did the clouds move while we looked? (the water moving)
Every job has max_execution_time as a hard QPU brake; the run refuses to start with < 150 s left on the account.

  python parallax_ibm.py check  <key file> <backend>     build + transpile against the real chip, no QPU time
  python parallax_ibm.py run    <key file> <backend>     fire (writes out/<stamp>/*.npz + meta.json)
  python parallax_ibm.py analyze <out dir>              PARALLAX_RESULTS.md (the analysis in PREREG.md, fixed before firing)
"""
import json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SHORT, LONG = 20e-6, 1e-3


def circuits(nq):
    from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
    out = {}
    for name, flip, looks in (('P0', False, 1), ('P1', True, 1), ('D0', False, 2), ('D1', True, 2)):
        q = QuantumRegister(nq, 'q'); regs = [ClassicalRegister(nq, f'm{i + 1}') for i in range(looks)]
        qc = QuantumCircuit(q, *regs, name=name)
        if flip: qc.x(q)
        for r in regs: qc.measure(q, r)
        out[name] = qc
    return out


def chip(keyfile, backend):
    from qiskit_ibm_runtime import QiskitRuntimeService
    s = QiskitRuntimeService(channel='ibm_quantum_platform', token=open(keyfile).read().strip())
    return s, s.backend(backend)


def qubits(be):
    t = be.target
    return [q for q in range(0, be.num_qubits, 2) if t['measure'].get((q,)) is not None and t['x'].get((q,)) is not None]


def build(be):
    from qiskit import transpile
    Q = qubits(be); C = circuits(len(Q))
    T = {k: transpile(v, backend=be, initial_layout=Q, optimization_level=0) for k, v in C.items()}
    return Q, T


def run(keyfile, backend):
    from qiskit_ibm_runtime import SamplerV2
    s, be = chip(keyfile, backend)
    left = s.usage().get('usage_remaining_seconds', 0)
    if left < 150: sys.exit(f'BRAKE: only {left} s left on this account')
    Q, T = build(be)
    stamp = time.strftime('%Y%m%d_%H%M%S'); out = os.path.join(HERE, 'out', stamp); os.makedirs(out, exist_ok=True)
    plan = [('J1', ['P0', 'P1', 'D0', 'D1'], 4000, None), ('J2', ['P0', 'P1'], 2000, SHORT),
            ('J3', ['P0', 'P1'], 2000, LONG), ('J4', ['P0', 'P1'], 2000, None)]
    meta = {'backend': backend, 'qubits': Q, 'usage_before_s': left, 'started': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'jobs': []}
    jobs = []
    for tag, names, shots, rep in plan:
        sm = SamplerV2(mode=be)
        sm.options.execution.meas_type = 'kerneled'
        sm.options.max_execution_time = 60
        if rep is not None: sm.options.execution.rep_delay = rep
        j = sm.run([T[n] for n in names], shots=shots)
        jobs.append((tag, names, shots, rep, j)); print(tag, 'submitted', j.job_id(), flush=True)
        meta['jobs'].append({'tag': tag, 'pubs': names, 'shots': shots, 'rep_delay': rep, 'job_id': j.job_id()})
        json.dump(meta, open(os.path.join(out, 'meta.json'), 'w'), indent=1)
    for tag, names, shots, rep, j in jobs:
        res = j.result(); arrs = {}
        for n, pr in zip(names, res):
            for reg in ('m1', 'm2'):
                if hasattr(pr.data, reg): arrs[f'{n}_{reg}'] = np.asarray(getattr(pr.data, reg))
        np.savez_compressed(os.path.join(out, f'{tag}.npz'), **arrs)
        m = j.metrics(); print(tag, 'done', {k: arrs[k].shape for k in arrs}, 'usage', (m.get('usage') or {}), flush=True)
        for rec in meta['jobs']:
            if rec['tag'] == tag: rec['metrics_usage'] = m.get('usage'); rec['timestamps'] = m.get('timestamps')
    meta['usage_after_s'] = s.usage().get('usage_remaining_seconds'); meta['finished'] = time.strftime('%Y-%m-%dT%H:%M:%S%z')
    json.dump(meta, open(os.path.join(out, 'meta.json'), 'w'), indent=1, default=str)
    print('OUT', out, 'seconds left', meta['usage_after_s'])


def geometry(z0, z1):
    """Cloud centers from the two preparations (medians: robust to a few % of the other state), the 0->1 axis, and projections."""
    c0 = complex(np.median(z0.real), np.median(z0.imag)); c1 = complex(np.median(z1.real), np.median(z1.imag)); a = c1 - c0
    t = lambda z: ((z - c0) * np.conj(a)).real / abs(a) ** 2          # 0 at the 0-cloud, 1 at the 1-cloud
    p = lambda z: ((z - c0) * np.conj(a)).imag / abs(a)              # distance off the axis (same units as the I/Q plane)
    mad = lambda x: 1.4826 * np.median(np.abs(x - np.median(x)))
    return c0, c1, a, t, p, mad(t(z0)), mad(p(z0))


def analyze(out):
    D = {k: np.load(os.path.join(out, f'{k}.npz')) for k in ('J1', 'J2', 'J3', 'J4') if os.path.exists(os.path.join(out, f'{k}.npz'))}
    meta = json.load(open(os.path.join(out, 'meta.json'))); Q = meta['qubits']; rows = []
    J1 = D['J1']
    for k, q in enumerate(Q):
        z0, z1 = J1['P0_m1'][:, k], J1['P1_m1'][:, k]
        c0, c1, a, t, p, st, sp = geometry(z0, z1)
        e0 = float(np.mean(t(z0) > .5)); e1 = float(np.mean(t(z1) < .5))
        f1, f2 = t(J1['D0_m1'][:, k]), t(J1['D0_m2'][:, k]); g1, g2 = t(J1['D1_m1'][:, k]), t(J1['D1_m2'][:, k])
        e0h = float(np.mean(f2[f1 < .5] > .5)) if np.any(f1 < .5) else float('nan')      # second look, heralded 0 by the first
        both1 = float(np.mean((f1 > .5) & (f2 > .5)))                                         # excited in BOTH looks: in the tank
        e1h = float(np.mean(g2[g1 > .5] < .5)) if np.any(g1 > .5) else float('nan')
        far1 = float(np.mean((np.abs(p(z1)) > 5 * sp) | (t(z1) > 1 + 5 * st)))              # off both clouds: a third place
        far0 = float(np.mean((np.abs(p(z0)) > 5 * sp) | (t(z0) < -5 * st)))
        r = {'q': q, 'snr': round(1 / (2 * st), 2) if st > 0 else None, 'e0': e0, 'e1': e1, 'e0_heralded': e0h, 'excited_both_looks': both1,
             'e1_heralded': e1h, 'offcloud_P1': far1, 'offcloud_P0': far0}
        if 'J2' in D and 'J3' in D:
            r['e0_short'] = float(np.mean(t(D['J2']['P0_m1'][:, k]) > .5)); r['e0_long'] = float(np.mean(t(D['J3']['P0_m1'][:, k]) > .5))
        if 'J4' in D:
            c0b = complex(np.median(D['J4']['P0_m1'][:, k].real), np.median(D['J4']['P0_m1'][:, k].imag))
            c1b = complex(np.median(D['J4']['P1_m1'][:, k].real), np.median(D['J4']['P1_m1'][:, k].imag))
            r['drift0_sigma'] = abs(c0b - c0) / (st * abs(a)) if st > 0 else None; r['drift1_sigma'] = abs(c1b - c1) / (st * abs(a)) if st > 0 else None
        rows.append(r)
    json.dump(rows, open(os.path.join(out, 'per_qubit.json'), 'w'), indent=1)
    med = lambda key: float(np.nanmedian([r[key] for r in rows if r.get(key) is not None]))
    L = [f"# THE PARALLAX RUN -- {meta['backend']}, {len(Q)} qubits, {meta.get('started')}", '',
         f"QPU seconds: {meta.get('usage_before_s')} left before, {meta.get('usage_after_s')} after.", '',
         '| measure (median over qubits) | value |', '|---|---|']
    for key, label in (('e0', 'prepared 0, read as 1 (one look)'), ('e0_heralded', 'prepared 0, first look said 0, second said 1'),
                       ('excited_both_looks', 'prepared 0, read 1 in BOTH looks (in the tank)'), ('e1', 'prepared 1, read as 0 (one look)'),
                       ('e1_heralded', 'prepared 1, first look said 1, second said 0'), ('offcloud_P1', 'prepared 1, off both clouds'),
                       ('offcloud_P0', 'prepared 0, off both clouds'), ('e0_short', 'prepared 0 read 1, shots 20 us apart'),
                       ('e0_long', 'prepared 0 read 1, shots 1 ms apart'), ('drift0_sigma', '0-cloud moved (in its own widths)'),
                       ('drift1_sigma', '1-cloud moved (in its own widths)'), ('snr', 'cloud separation / width')):
        try: L.append(f'| {label} | {med(key):.4f} |')
        except Exception: pass
    for key, label in (('e0', 'most apparent excitation at rest'), ('excited_both_looks', 'most excitation that survives two looks'),
                       ('offcloud_P1', 'most shots off both clouds (prepared 1)')):
        top = sorted(rows, key=lambda r: -(r.get(key) or 0))[:8]
        L += ['', f'**{label}:** ' + ', '.join(f"q{r['q']} {r[key]:.3f}" for r in top)]
    open(os.path.join(out, 'PARALLAX_RESULTS.md'), 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'check':
        s, be = chip(sys.argv[2], sys.argv[3]); Q, T = build(be)
        print(len(Q), 'qubits:', Q[:6], '...', {k: (v.num_qubits, dict(v.count_ops())) for k, v in T.items()})
    elif cmd == 'run': run(sys.argv[2], sys.argv[3])
    elif cmd == 'analyze': analyze(sys.argv[2])
