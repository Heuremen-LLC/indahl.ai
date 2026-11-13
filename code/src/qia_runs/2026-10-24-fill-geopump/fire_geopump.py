"""fire_geopump.py -- the free calibration run for arXiv 2610.09062 (Caselli, Manuel, Arrachea, Cornaglia) on ibm_kingston, Darkwave Disco.
Design fixed in PLAN_GEOPUMP.md.text before any job. Two jobs (copies) of 200 circuits each, ABBA (job 2 = job 1's order reversed for the
shared A circuits, and its own fresh K=12 realizations for Ap/Bp, the same structure the synthetic test used):
  per tau in (20, 60), delta_B 0.45: A = their 4 circuits x 3000 shots; Ap and Bp = 4 branches x 12 realizations x 250 shots, Ap_k next to Bp_k.
Layout rule (fixed before looking): their (S, aL, aR) = (47, 48, 46) unless, in the record saved before the job, a CZ error on S-aL or S-aR
or a readout error on any of the three exceeds 3x the chip median, or a T1/T2 is missing -> then their own scoring rule (SM I.5) re-implemented.
Transpile: their settings (optimization_level 3, seed_transpiler 0, fixed initial layout). CHECK 8: for every k, the ASAP start times of every
operation on S (target durations) are identical in Ap_k and Bp_k, else optimization_level 1 for Ap and Bp, re-checked; if still unequal: STOP.
Usage: fire_geopump.py (dry run: build, checks, estimate) | fire_geopump.py --fire"""
import os, sys, json, time, hashlib, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
import geopump as G
from sweep import service
from qiskit import transpile, qpy
CHIP, TAUS, DB, K, SH_R, SH_A, CAP = 'ibm_kingston', (20.0, 60.0), 0.45, 12, 250, 3000, 220
THEIRS = (47, 48, 46)

def pick_layout(b):
    t = b.target; cz = [v.error for v in t['cz'].values() if v is not None and v.error is not None and v.error < 1]
    me = [t['measure'][(q,)].error for q in range(b.num_qubits) if t['measure'][(q,)] is not None and t['measure'][(q,)].error is not None]
    mcz, mme = np.median(cz), np.median(me); s, al, ar = THEIRS
    def e(a, c):
        for k in ((a, c), (c, a)):
            if k in t['cz'] and t['cz'][k] is not None and t['cz'][k].error is not None: return t['cz'][k].error
        return None
    bad = [x for x in (e(s, al), e(s, ar)) if x is None or x > 3 * mcz] + [q for q in THEIRS if t['measure'][(q,)].error > 3 * mme]
    bad += [q for q in THEIRS if not (t.qubit_properties[q].t1 and t.qubit_properties[q].t2)]
    return THEIRS, dict(cz_S_aL=e(s, al), cz_S_aR=e(s, ar), chip_median_cz=float(mcz), chip_median_readout=float(mme),
                        readout={q: t['measure'][(q,)].error for q in THEIRS}, failed=bad)

def build_all(rng):
    circs, meta = [], []
    for tau in TAUS:
        for d in ('fwd', 'rev'):
            sch = G.schedule(DB, tau, d == 'rev'); v0 = G.periodic(sch)
            for br, w, vec in G.branches(v0):
                circs.append(G.build(sch, vec, 'A', name=f'A_{tau:g}_{d}_{br}')); meta.append(dict(fam='A', tau=tau, d=d, b=br, w=w, shots=SH_A))
                for k in range(K):
                    bins = G.draw_bin(sch, rng)
                    for fam in ('Ap', 'Bp'):
                        circs.append(G.build(sch, vec, fam, bins, name=f'{fam}_{tau:g}_{d}_{br}_{k}'))
                        meta.append(dict(fam=fam, tau=tau, d=d, b=br, w=w, k=k, shots=SH_R, bins={x: bins[x].tolist() for x in 'LR'}))
    return circs, meta

def s_times(tc, b, S):
    from qiskit.transpiler import PassManager
    from qiskit.transpiler.passes import ASAPScheduleAnalysis
    from qiskit.converters import circuit_to_dag
    pm = PassManager([ASAPScheduleAnalysis(target=b.target)]); pm.run(tc); st = pm.property_set['node_start_time']
    out = []
    for node, t0 in st.items():
        qs = [tc.find_bit(q).index for q in getattr(node, 'qargs', [])]
        if S in qs: out.append((t0, node.op.name))
    return sorted(out)

def compile_copy(b, circs, meta, layout):
    tq = transpile(circs, b, optimization_level=3, seed_transpiler=0, initial_layout=list(layout))
    S = layout[0]; ok = True; lvl = 3
    def check(tq):
        idx = {(m['tau'], m['d'], m['b'], m.get('k'), m['fam']): i for i, m in enumerate(meta)}
        for (tau, d, br, k, fam), i in idx.items():
            if fam != 'Ap': continue
            j = idx[(tau, d, br, k, 'Bp')]
            if s_times(tq[i], b, S) != s_times(tq[j], b, S): return False, (tau, d, br, k)
        return True, None
    ok, where = check(tq)
    if not ok:
        print('CHECK 8 failed at optimization_level 3 for', where, '-> optimization_level 1 for Ap/Bp', flush=True); lvl = 1
        sel = [i for i, m in enumerate(meta) if m['fam'] != 'A']; t1 = transpile([circs[i] for i in sel], b, optimization_level=1, seed_transpiler=0, initial_layout=list(layout))
        for i, c in zip(sel, t1): tq[i] = c
        ok, where = check(tq)
    return tq, ok, lvl

if __name__ == '__main__':
    FIRE = '--fire' in sys.argv; s = service(); b = s.backend(CHIP); rem = s.usage().get('usage_remaining_seconds')
    props = b.properties(refresh=True).to_dict(); layout, why = pick_layout(b)
    print(f'{CHIP}: layout {layout} rule check {json.dumps(why, default=str)}; remaining {rem}', flush=True)
    if why['failed']: print('LAYOUT RULE: their triple fails the 3x rule -> STOP (re-run their scoring rule by addendum before any job)'); sys.exit(1)
    jobs = []
    for copy in (1, 2):
        rng = np.random.default_rng(20261024 + copy); circs, meta = build_all(rng)
        if copy == 2: circs, meta = circs[::-1], meta[::-1]          # ABBA
        t0 = time.time(); tq, ok, lvl = compile_copy(b, circs, meta, layout)
        dur = np.array([c.estimate_duration(b.target, 's') for c in tq]); shots = np.array([m['shots'] for m in meta])
        est = float(np.sum(shots * (dur + 250e-6)))
        print(f'copy {copy}: {len(tq)} circuits, CHECK 8 (S timeline Ap_k == Bp_k) {"PASS" if ok else "FAIL"} at optimization_level {lvl}, '
              f'circuit duration {dur.min()*1e3:.3f}-{dur.max()*1e3:.3f} ms, est {est:.0f} s, compile {time.time()-t0:.0f} s', flush=True)
        if not ok: print('STOP: CHECK 8 failed'); sys.exit(1)
        jobs.append((copy, tq, meta, est))
    tot = sum(j[3] for j in jobs); print(f'TOTAL estimate {tot:.0f} s (cap {CAP}), remaining {rem}', flush=True)
    if not FIRE: sys.exit(0)
    if tot > CAP or (rem is not None and rem < tot + 60): print('STOP: over cap or not enough seconds'); sys.exit(1)
    from qiskit_ibm_runtime import SamplerV2
    rec = dict(chip=CHIP, layout=layout, layout_check=why, jobs=[])
    for copy, tq, meta, est in jobs:
        for attempt in (1, 2):
            qpy.dump(tq, open(f'{HERE}/circuits_copy{copy}.qpy', 'wb')); h = hashlib.sha256(open(f'{HERE}/circuits_copy{copy}.qpy', 'rb').read()).hexdigest()
            json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_before_copy{copy}_try{attempt}.json', 'w'), default=str)
            json.dump(meta, open(f'{HERE}/meta_copy{copy}.json', 'w'))
            job = SamplerV2(mode=b).run([(c, None, m['shots']) for c, m in zip(tq, meta)])
            sub = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()); print(f'SUBMITTED copy {copy} try {attempt} {job.job_id()} {sub}', flush=True)
            rec['jobs'].append(dict(copy=copy, attempt=attempt, job_id=job.job_id(), submitted_utc=sub, circuit_hash=h)); json.dump(rec, open(f'{HERE}/job_geopump.json', 'w'), default=str)
            try:
                res = job.result()
            except Exception as ex:
                print(f'ERROR copy {copy} try {attempt}: {str(ex)[:160]}', flush=True); rec['jobs'][-1]['error'] = str(ex)[:300]
                json.dump(rec, open(f'{HERE}/job_geopump.json', 'w'), default=str)
                if attempt == 2: print('HOLD: second IBM-side failure; not refired'); sys.exit(2)
                continue
            out = {}
            for i, pr in enumerate(res):
                out[f'eL_{i}'] = pr.data.eL.to_bool_array(order='little').astype(np.uint8); out[f'eR_{i}'] = pr.data.eR.to_bool_array(order='little').astype(np.uint8)
            np.savez_compressed(f'{HERE}/raw_copy{copy}.npz', **out)
            m = job.metrics(); rec['jobs'][-1].update(usage=m.get('usage'), timestamps=m.get('timestamps')); json.dump(rec, open(f'{HERE}/job_geopump.json', 'w'), default=str)
            print(f'DONE copy {copy} usage {(m.get("usage") or {}).get("qpu_charge_time_seconds")} s', flush=True); break
    json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_after.json', 'w'), default=str); print('ALL DONE', flush=True)
