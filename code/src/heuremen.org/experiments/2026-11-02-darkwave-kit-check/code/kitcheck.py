"""kitcheck.py CHIP [--fire] -- the Darkwave Correction Kit's known-good run on IBM hardware (PLAN_KITCHECK.md.text). 2 Nov 2026.
Job 1: the kit's 8 circuits (darkwave_kit.build, N = 1 and 4) and the study's 8 calibration circuits (keystone.circ_S, keys_cal, N = 4 and 8),
in one job, on the study's readout pack E (39) and untouched qubits S (117). Two codes read the same turn in the same session.
Job 2, right after: the kit's N = 4 circuits again, arms D and M, plus M with the kit's correction applied (darkwave_kit.corrected, the job-1
kit table). No dynamical decoupling, no twirling, trivial layout, seed 31, 4,000 shots per circuit. Raw arrays and records saved before reading."""
import json, sys, os, time, warnings; warnings.filterwarnings('ignore')
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
KS = os.path.join(HERE, '..', '..', 'keystone'); sys.path.insert(0, KS)
import darkwave_kit as DK
import keystone as K
SHOTS = 4000; SEED = 31; MARGIN_R1 = 0.5; MARGIN_R2 = 0.5
def wrapd(x): return (np.asarray(x) + 180.0) % 360.0 - 180.0
def nearr(x, ref): return x + 2 * np.pi * np.round((ref - x) / (2 * np.pi))
def p1_packed(arr, m): return np.array([K.bits(arr, k).mean() for k in range(m)]), arr.shape[0]
def kit_counts(arrs, S):
    """arrs: {(N, arm, basis): packed fin array} -> the kit's own counts format {key: (ones per target, shots)}"""
    return {k: (p1_packed(a, len(S))[0] * a.shape[0], a.shape[0]) for k, a in arrs.items()}
def kit_table(arrs, S): return DK.analyse(kit_counts(arrs, S), S, 0.5)
def study_table(chip, cal_arrs, S):
    """the study's own code: keystone.fresh_from_cal on the study's calibration circuits"""
    Z = {k: [a] for k, a in cal_arrs.items()}; return K.fresh_from_cal(chip, Z, S)
def boot_median(x, B=2000, seed=41):
    x = np.asarray([v for v in x if np.isfinite(v)]); rng = np.random.default_rng(seed)
    bs = np.median(rng.choice(x, (B, len(x))), axis=1); return float(np.median(x)), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)), len(x)
def four(lo, hi, margin):
    return 'ABOVE' if lo > 0 else 'BELOW' if hi < 0 else 'CONSISTENT' if (lo >= -margin and hi <= margin) else 'CANNOT_TELL'
def r1(kt, st, S):
    d = [kt[q]['deg_per_readout'] - st[q]['k4'] for q in S]; m, lo, hi, n = boot_median(d)
    return dict(reading='R1 kit minus study, deg per readout, median over targets', median=m, band=[lo, hi], n=n, outcome=four(lo, hi, MARGIN_R1),
                share_abs_over_1deg=float(np.mean(np.abs(d) > 1.0)), corr=float(np.corrcoef([kt[q]['deg_per_readout'] for q in S], [st[q]['k4'] for q in S])[0, 1]))
def phases(arrs, S, keyf):
    out = {}
    for a in ('D', 'M', 'MC'):
        if keyf(a, 'X') not in arrs: continue
        x = 1 - 2 * p1_packed(arrs[keyf(a, 'X')], len(S))[0]; y = 1 - 2 * p1_packed(arrs[keyf(a, 'Y')], len(S))[0]
        out[a] = (np.arctan2(y, x), np.hypot(x, y))
    return out
def r2(arrs2, S, kt, N=4):
    ph = phases(arrs2, S, lambda a, b: (N, a, b)); res, kick, share = [], [], []
    for i, q in enumerate(S):
        k = nearr(np.radians(float(wrapd(np.degrees(ph['M'][0][i] - ph['D'][0][i])))), np.radians(N * kt[q]['deg_per_readout'])) / N
        r = np.radians(float(wrapd(np.degrees(ph['MC'][0][i] - ph['D'][0][i])))) / N
        res.append(np.degrees(r)); kick.append(np.degrees(k)); share.append(1 - r / k if abs(k) > np.radians(0.25) else np.nan)
    mr, lr, hr, n = boot_median(res); ms, ls, hs, ns = boot_median(share)
    return dict(residual=dict(median=mr, band=[lr, hr], n=n, outcome=four(lr, hr, MARGIN_R2)),
                share_given_back=dict(median=ms, band=[ls, hs], n=ns, outcome=('ABOVE' if ls > 0.5 else 'BELOW' if hs < 0.5 else 'CANNOT_TELL'), note='against 0.5, targets with |turn| above 0.25 deg/readout'),
                kick_job2=dict(median=float(np.median(kick))), per_qubit=dict(residual=res, kick=kick))
def build_job1(n, E, S, L_kit, L_st):
    kit = {('KIT',) + k: DK.build(n, E, S, L_kit, *k) for k in DK.keys()}
    cal = {k: K.circ_S(n, E, S, k[1], k[2], {}, L_st, N=k[3]) for k in K.keys_cal()}
    return kit, cal
def build_job2(n, E, S, L_kit, kt, N=4):
    c = {}
    for b in DK.BASES:
        c[(N, 'D', b)] = DK.build(n, E, S, L_kit, N, 'D', b); c[(N, 'M', b)] = DK.build(n, E, S, L_kit, N, 'M', b)
        c[(N, 'MC', b)] = DK.corrected(c[(N, 'M', b)], E, {q: kt[q]['deg_per_readout'] for q in S})
    return c
if __name__ == '__main__':
    CHIP = sys.argv[1]; FIRE = '--fire' in sys.argv; assert CHIP == 'ibm_kingston'
    sys.path.insert(0, '<local helper folder>')
    from sweep import service
    from qiskit import transpile, qpy
    from qiskit_ibm_runtime import SamplerV2
    T = K.table(CHIP); E = [int(q) for q in T['E']]; S = [int(q) for q in T['S']]; L_st = int(T['L_dt'])
    s = service(); b = s.backend(CHIP); n = b.num_qubits
    L_kit = max(int(round(b.target['measure'][(q,)].duration / b.dt)) for q in E)
    kit, cal = build_job1(n, E, S, L_kit, L_st)
    keys1 = list(kit) + list(cal); circ1 = {**kit, **cal}
    tp = lambda c: transpile(c, b, optimization_level=1, initial_layout=list(range(n)), seed_transpiler=SEED)
    TC1 = {k: tp(c) for k, c in circ1.items()}
    for k, t in TC1.items(): assert t.layout is None or list(t.layout.final_index_layout()) == list(range(n)), ('layout moved', k)
    dur = {}
    for N in DK.NS:
        for arm in DK.ARMS:
            sc = transpile(TC1[('KIT', N, arm, 'X')], b, optimization_level=0, scheduling_method='alap', initial_layout=list(range(n)))
            dur[(N, arm)] = sorted({sc.qubit_duration(q) for q in S})
        assert dur[(N, 'D')] == dur[(N, 'M')], ('kit arms differ in time', N, dur)
    print('checks PASS: layout unmoved; kit D and M equal on targets', {f'N{N}': dur[(N, 'D')] for N in DK.NS}, '| L_kit', L_kit, 'L_study', L_st, flush=True)
    try: u = s.usage(); print('instance seconds remaining:', u.get('usage_remaining_seconds'), 'of', u.get('usage_limit_seconds'), flush=True)
    except Exception as ex: print('usage read failed:', type(ex).__name__, flush=True)
    if not FIRE: print('dry run: nothing submitted'); sys.exit(0)
    rec = dict(chip=CHIP, E=E, S=S, L_kit=L_kit, L_study=L_st, shots=SHOTS, seed_transpiler=SEED, dd='off', twirling='off', keys1=[list(map(str, k)) for k in keys1], jobs=[])
    def save_rec(): json.dump(rec, open(f'{HERE}/job_kitcheck_{CHIP}.json', 'w'), default=str, indent=1)
    def run(label, circs):
        json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_{CHIP}_before_{label}.json', 'w'), default=str)
        smp = SamplerV2(mode=b); smp.options.dynamical_decoupling.enable = False; smp.options.twirling.enable_gates = False; smp.options.twirling.enable_measure = False
        job = smp.run([(c, None, SHOTS) for c in circs]); sub = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        print(f'SUBMITTED {label} job {job.job_id()} {sub}', flush=True); rec['jobs'].append(dict(label=label, job_id=job.job_id(), submitted_utc=sub, status='SUBMITTED')); save_rec()
        for tries in range(400):
            try: res = job.result(); break
            except Exception as ex:
                st = str(job.status()); print(f'WAIT {label}: {type(ex).__name__}; IBM status {st}', flush=True)
                if 'ERROR' in st or 'CANCEL' in st: rec['jobs'][-1]['status'] = 'IBM ' + st; save_rec(); print('HOLD: not resubmitted'); sys.exit(2)
                time.sleep(20)
        m = job.metrics(); rec['jobs'][-1].update(status='DONE', usage=m.get('usage'), timestamps=m.get('timestamps')); save_rec()
        print(f'DONE {label} usage {m.get("usage")}', flush=True); return res
    qpy.dump([TC1[k] for k in keys1], open(f'{HERE}/circuits_job1_{CHIP}.qpy', 'wb'))
    res1 = run('job1', [TC1[k] for k in keys1])
    arrs = {k: np.asarray(r.data.fin.array) for k, r in zip(keys1, res1)}
    np.savez_compressed(f'{HERE}/raw_job1_{CHIP}.npz', **{'|'.join(map(str, k)): v for k, v in arrs.items()})
    kit_arrs = {k[1:]: v for k, v in arrs.items() if k[0] == 'KIT'}
    gc = {k[1:]: r.data.fin.get_counts() for k, r in zip(keys1, res1) if k[0] == 'KIT'}   # the kit's own path, to check it gives the same table
    kt = kit_table(kit_arrs, S); kt2 = DK.analyse({k: DK.p1_from(v, len(S)) for k, v in gc.items()}, S, 0.5)
    rec['kit_paths_agree'] = all(abs(kt[q]['deg_per_readout'] - kt2[q]['deg_per_readout']) < 1e-9 for q in S); save_rec()
    DK.save_table(HERE, CHIP, E, S, L_kit, SHOTS, rec['jobs'][-1]['job_id'], kt, 0.5)
    TC2 = {k: tp(c) for k, c in build_job2(n, E, S, L_kit, kt).items()}; keys2 = list(TC2)
    qpy.dump([TC2[k] for k in keys2], open(f'{HERE}/circuits_job2_{CHIP}.qpy', 'wb'))
    res2 = run('job2', [TC2[k] for k in keys2])
    arrs2 = {k: np.asarray(r.data.fin.array) for k, r in zip(keys2, res2)}
    np.savez_compressed(f'{HERE}/raw_job2_{CHIP}.npz', **{'|'.join(map(str, k)): v for k, v in arrs2.items()})
    print('raw saved. Read with analyze_kitcheck.py', flush=True)
