"""known_good.py -- GATE: reproduce his published numbers from his stored counts (theirs/job2_results.json, job4_results.json; data only, his code never run) with kumar.py,
and (with --circuits, needs the IBM service read-only) rebuild all 400 circuits with my builder and check the twirl metadata equals his manifests.
Targets (printed in his paper): baseline <Xs>(1,1,1) 0.9058 main (job2) / 0.9619 repeat (job4); b_LM +0.0007 main / -0.0031 repeat; stated-T2 projection of the baseline
(from his own calibration_before snapshots) 0.9079 job2 / 0.9451 job4 (the zero-QPU reading in the qualification). Usage: known_good.py [--circuits]"""
import sys, os, json, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from kumar import *
def load(job):
    r = json.load(open(f'{H}/theirs/{job}_results.json')); return r, [s for s in r['subjobs'] if s['bench'] == 'probe'][0]['records']
out = {}; ok = True
for job, pb, pbl in (('job2', 0.9058, 0.0007), ('job4', 0.9619, -0.0031)):
    r, recs = load(job); inst = inst_of(recs); mu = {s: inst[s].mean() for s in FACT}
    b, bl = float(mu[(1, 1, 1)]), float(blm_of(mu)); good = abs(b - pb) < 5e-5 and abs(bl - pbl) < 5e-5; ok &= good
    out[job] = dict(baseline=b, published_baseline=pb, bLM=bl, published_bLM=pbl, agree_to_printed_digits=bool(good))
    print(f'{job}: baseline mine {b:.4f} pub {pb:.4f} | b_LM mine {bl:+.4f} pub {pbl:+.4f} -> {"agree" if good else "DISAGREE"}')
    cb = r['calibration_before']['qubits']['6']; r0 = [x for x in recs if x['setting'] == [1, 1, 1] and x['twirl'] == 0][0]
    tt = r0['tau_w_s'] + r0['pad_s']; out[job]['projection'] = proj(cb['t2'], cb['meas_err'], tt); out[job]['wait_us'] = tt * 1e6
for job, pp in (('job2', 0.9079), ('job4', 0.9451)):
    good = abs(out[job]['projection'] - pp) < 5e-5; ok &= good
    print(f'{job}: stated-T2 projection mine {out[job]["projection"]:.4f} (wait {out[job]["wait_us"]:.2f} us) qualification {pp:.4f} -> {"agree" if good else "DISAGREE"}')
print('KNOWN-GOOD (data):', 'PASS' if ok else 'FAIL'); out['data_pass'] = bool(ok)
if '--circuits' in sys.argv:
    sys.path.insert(0, os.path.expanduser('<local helper folder>')); from sweep import service
    b = service().backend('ibm_marrakesh'); tim = Timing(b.target); res = {}
    for X, seed, job in (('A', SEED_A, 'job2'), ('B', SEED_B, 'job4')):
        hm = his_probe_metas(f'{H}/theirs/{job}_manifest.json'); mine = build_set(seed, tim, hm)
        eq = sum(meta_equal(m, h) for (qc, m), h in zip(mine, hm))
        live = sum(m['window_dt'] == next(x['window_dt'] for x in hm if x['setting'] == m['setting'] and x['twirl'] == m['twirl']) for _, m in build_set(seed, tim))
        res[X] = dict(instances=len(hm), metadata_equal=eq, live_target_window_dt_equal=live)
        print(f"set {X} (his {job}, seed {seed}): rebuilt metadata equals his manifest in {eq}/{len(hm)}; window_dt from TODAY's target equals his in {live}/{len(hm)}")
    out['circuits'] = res; out['circuits_pass'] = all(v['metadata_equal'] == v['instances'] for v in res.values())
    print('KNOWN-GOOD (circuits):', 'PASS' if out['circuits_pass'] else 'FAIL')
json.dump(out, open(f'{H}/known_good_kumar.json', 'w'), indent=1, default=float)
