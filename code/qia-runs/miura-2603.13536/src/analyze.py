"""analyze.py -- reads raw_2603.13536.json under PLAN_2603.13536.md.text (readings.py, fixed before the job).  Writes results_2603.13536.text
and readings_2603.13536.json.  Scored: seat known-good, D1, D2, headline.  Everything else printed here is DESCRIPTIVE (not scored)."""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); RUN = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(HERE); sys.path.insert(0, HERE)   # argv[1]: a job folder (ADDENDUM_2)
import numpy as np
from assqd import Model, counts_from_bitstrings, merge, run, lerr, top_k, sample, K_INIT
from readings import analyze, interval, four
from circuits import trotter, ideal_probs, T0, T1, SH0, SH1, SHOTS
N = 12; SEEDS = list(range(100, 110)); out = []
def p(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); out.append(s)

raw = json.load(open(f'{RUN}/raw_2603.13536.json')); job = json.load(open(f'{RUN}/job_2603.13536.json')); ring = job['ring']
att = [a for a in job['attempts'] if a.get('usage')][-1]
props = json.load(open(f'{RUN}/props_2603.13536_before_{att["attempt"]}.json'))
p(f'job {att["job_id"]} attempt {att["attempt"]}, created {att["timestamps"].get("created")}, running {att["timestamps"].get("running")}, finished {att["timestamps"].get("finished")}; '
  f'usage {att["usage"].get("qpu_charge_time_seconds") if att["usage"] else None} s; record last_update_date {props.get("last_update_date")}; ring {ring}')

# --- seat known-good (in-job readout vs the stated record) ---
def stated_ro(q):
    d = {x['name']: x['value'] for x in props['qubits'][q]}; return d.get('readout_error'), d.get('prob_meas1_prep0'), d.get('prob_meas0_prep1')
s0 = counts_from_bitstrings([r for r in raw if r['kind'] == 'seat' and r['one'] == 0][0]['counts'])
s1 = counts_from_bitstrings([r for r in raw if r['kind'] == 'seat' and r['one'] == 1][0]['counts'])
n0, n1 = sum(s0.values()), sum(s1.values()); ratios = []
for i, q in enumerate(ring):
    p10 = sum(v for k, v in s0.items() if (k >> i) & 1) / n0; p01 = sum(v for k, v in s1.items() if not (k >> i) & 1) / n1
    e = (p10 + p01) / 2; st, a, b = stated_ro(q); ratios.append(e / st)
    p(f'  seat q{i}->phys {q}: P(1|0) {p10:.4f}  P(0|1) {p01:.4f}  mean {e:.4f}  stated readout_error {st:.4f} (p10 {a}, p01 {b})  ratio {e/st:.2f}')
mr = float(np.median(ratios)); kg = 0.5 <= mr <= 2.0
p(f'KNOWN-GOOD seat: median measured/stated readout error over the 12 ring qubits {mr:.2f} (rule [0.5, 2.0]) -> {"PASS" if kg else "FAIL (chip not decided: every reading CANNOT_TELL)"}; '
  f'exact |0..0> survival {s0.get(0, 0)/n0:.4f}, |1..1> survival {s1.get(4095, 0)/n1:.4f}')

# --- arms ---
trots, ctrls = [], []
for s in SEEDS:
    t = [counts_from_bitstrings(r['counts']) for r in raw if r['kind'] == 'trot' and r['seed'] == s]; trots.append(merge(*t))
    ctrls.append(counts_from_bitstrings([r for r in raw if r['kind'] == 'ctrl' and r['seed'] == s][0]['counts']))
Ms = [Model(N, s) for s in SEEDS]
R = analyze(Ms, trots, ctrls, seed=0)
o1, o2, head = (R['o1'], R['o2'], R['head']) if kg else ('CANNOT_TELL', 'CANNOT_TELL', 'CANNOT_TELL')
p(f'D1 = mean(log10 err AS-SQD - mean log10 err Random SQD), hardware trot samples, 10 instances: {R["D1"][0]:+.3f} [{R["D1"][1]:+.3f}, {R["D1"][2]:+.3f}] -> {o1}')
p(f'D2 = mean(log10 err AS-SQD trot - log10 err AS-SQD no-gate ctrl), 10 instances: {R["D2"][0]:+.3f} [{R["D2"][1]:+.3f}, {R["D2"][2]:+.3f}] -> {o2}  (M = 0.5 decade)')
p(f'HEADLINE (triage four outcomes): {head}')

# --- descriptive ---
p('DESCRIPTIVE (not scored):')
sz = np.array([bin(i).count('1') for i in range(1 << N)]); rng = np.random.default_rng(424242); desc = []
for i, (M, t, c) in enumerate(zip(Ms, trots, ctrls)):
    std = lerr(M, run(M, t, 'standard')[0]); i0 = ideal_probs(trotter(N, M.terms, T0)); i1 = ideal_probs(trotter(N, M.terms, T1))
    ideal = merge(sample(rng, i0, SH0), sample(rng, i1, SH1)); uni = sample(rng, np.ones(1 << N), SHOTS)
    a_id = lerr(M, run(M, ideal, 'en')[0]); a_un = lerr(M, run(M, uni, 'en')[0])
    r_c = float(np.mean([lerr(M, run(M, c, 'random', rng=np.random.default_rng(9000 + 10 * i + k))[0]) for k in range(5)]))
    w50t = float(sum(M.p0[b] for b in top_k(t))); w50c = float(sum(M.p0[b] for b in top_k(c)))
    jac = len(set(top_k(t)) & set(top_k(c))) / len(set(top_k(t)) | set(top_k(c)))
    f6t = sum(v for k, v in t.items() if sz[k] == 6) / sum(t.values()); f6c = sum(v for k, v in c.items() if sz[k] == 6) / sum(c.values())
    nd_t, nd_c = len(t), len(c)
    d = dict(seed=M.seed, E0=M.E0, AS_trot=R['a'][i], RND_trot=R['r'][i], AS_ctrl=R['c'][i], STD_trot=std, RND_ctrl=r_c, AS_ideal_sim=a_id, AS_uniform_sim=a_un,
             W50_trot=w50t, W50_ctrl=w50c, W50_uniform_expect=K_INIT / 4096, jaccard_top50=jac, frac6_trot=f6t, frac6_ctrl=f6c, distinct_trot=nd_t, distinct_ctrl=nd_c)
    desc.append(d)
    p(f'  seed {M.seed}: log10 err  AS trot {d["AS_trot"]:+.2f}  RND trot {d["RND_trot"]:+.2f}  STD trot {std:+.2f}  AS ctrl {d["AS_ctrl"]:+.2f}  RND ctrl {r_c:+.2f}  '
      f'AS ideal-sim {a_id:+.2f}  AS uniform-sim {a_un:+.2f} | top-50 ground weight trot {w50t:.4f} ctrl {w50c:.4f} (uniform expect {K_INIT/4096:.4f}) | '
      f'Jaccard top-50 {jac:.2f} | weight in 6-ones sector trot {f6t:.3f} ctrl {f6c:.3f} (binomial 0.226) | distinct strings {nd_t}/{nd_c}')
A = np.array([[d[k] for k in ('AS_trot', 'RND_trot', 'STD_trot', 'AS_ctrl', 'RND_ctrl', 'AS_ideal_sim', 'AS_uniform_sim')] for d in desc])
for lab, x in (('AS trot - STD trot', A[:, 0] - A[:, 2]), ('AS ctrl - RND ctrl (same contrast on no-gate samples)', A[:, 3] - A[:, 4]),
               ('AS trot - AS uniform-sim', A[:, 0] - A[:, 6]), ('AS ideal-sim - AS uniform-sim (zero QPU)', A[:, 5] - A[:, 6])):
    m, lo, hi = interval(x); p(f'  {lab}: {m:+.3f} [{lo:+.3f}, {hi:+.3f}] -> {four(lo, hi)} (descriptive)')
for lab, j in (('D1', (0, 1)), ('D2', (0, 3))):
    x = A[:5, j[0]] - A[:5, j[1]]; m, lo, hi = interval(x); p(f'  paper\'s 5 seeds only (100..104), {lab}: {m:+.3f} [{lo:+.3f}, {hi:+.3f}] t(4) -> {four(lo, hi)} (descriptive)')
p(f'  median abs energy error over 10 instances: AS trot {np.median(10**A[:,0]):.3f}, RND trot {np.median(10**A[:,1]):.3f}, STD trot {np.median(10**A[:,2]):.3f}, AS ctrl {np.median(10**A[:,3]):.3f}')
open(f'{RUN}/results_2603.13536.text', 'w').write('\n'.join(out) + '\n')
json.dump(dict(job=att, ring=ring, seat_median_ratio=mr, known_good=kg, D1=R['D1'], D2=R['D2'], o1=o1, o2=o2, headline=head, per_instance=desc), open(f'{RUN}/readings_2603.13536.json', 'w'), indent=1, default=str)
