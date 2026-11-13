"""fire_tele.py --dry | --fire : job A (ibm_kingston, SamplerV2, no DD, no twirling, opt 1, seed 7): for L in theirs, best, q50:
native / N1none / N1corr x product_HT / bell_30_70 x 9 bases (3000 shots), then TOMO-9 fingerprint probes (9 x 2000); then the known-good copy
'kg' = their chain native product_HT, 9 bases, 3000 (last in the job). Job B, submitted when job A returns: their chain, the 3 blocks x 2 messages.
Refuses unless kingston is active and remaining - (CAP_A + CAP_B) >= RESERVE."""
import sys, os, json, time, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
from tele import block_circuits, probe_circuits, ROLE_ORDER
from tele_fill import analyse, MSGS, LAYS, BLOCKS
from qiskit import transpile
SH, SHP, RATE = 3000, 2000, 0.000264          # RATE = their Round 1 usage per shot (117 s / 436,000 + overheads ~ circuit time)
CAP_A, CAP_B, RESERVE = 240, 80, 300
L = json.load(open(os.path.join(HERE, 'layouts_chosen.json')))
def lay(name): p = L[name]['path']; return [p[ROLE_ORDER.index(f'q{i}')] for i in range(6)]
fire = '--fire' in sys.argv
from sweep import service
s = service(); rem = s.usage().get('usage_remaining_seconds'); be = s.backend('ibm_kingston'); st = be.status()
print('remaining', rem, 'kingston', st.status_msg, st.pending_jobs, flush=True)
def build(lname, items):
    return [(f'{lname}|{lab}', transpile(c, be, optimization_level=1, initial_layout=lay(lname if lname in L else 'theirs'), seed_transpiler=7), sh) for lab, c, sh in items]
blocks = [(l, c, SH) for b in BLOCKS for m in MSGS for l, c in block_circuits(b, m)]
probes = [(l, c, SHP) for l, c in probe_circuits()]
A = []
for name in LAYS: A += build(name, blocks + probes)
A += [(f'kg|{l}', transpile(c, be, optimization_level=1, initial_layout=lay('theirs'), seed_transpiler=7), SH) for l, c, _ in [(l, c, SH) for l, c in block_circuits('native', 'product_HT')]]
B = [(f'jobB|{l}', transpile(c, be, optimization_level=1, initial_layout=lay('theirs'), seed_transpiler=7), sh) for l, c, sh in blocks]
def phys(t): return sorted({t.find_bit(i.qubits[0]).index for i in t.data if i.operation.name == 'measure'})
info = {}
for k, t, sh in A + B:
    key = k.split('|')[0] + '|' + '_'.join(k.split('|')[1].split('_')[:-1])
    info.setdefault(key, dict(cz=set(), depth=set(), qubits=None, n=0, shots=0))
    info[key]['cz'].add(int(t.count_ops().get('cz', 0))); info[key]['depth'].add(t.depth()); info[key]['qubits'] = phys(t); info[key]['n'] += 1; info[key]['shots'] += sh
shA, shB = sum(x[2] for x in A), sum(x[2] for x in B)
summ = dict(jobA_circuits=len(A), jobA_shots=shA, jobA_est_s=round(shA * RATE, 1), jobB_circuits=len(B), jobB_shots=shB, jobB_est_s=round(shB * RATE, 1),
            blocks={k: dict(cz=sorted(v['cz']), depth=sorted(v['depth']), qubits=v['qubits'], n=v['n']) for k, v in info.items()})
print(json.dumps({k: v for k, v in summ.items() if k != 'blocks'}), flush=True)
if not fire:
    open(os.path.join(HERE, 'dry_run_tele.text'), 'w').write(json.dumps(summ, indent=1)); sys.exit(0)
if rem is None or rem - CAP_A - CAP_B < RESERVE or str(st.status_msg).lower() != 'active' or not st.operational: sys.exit('REFUSED')
from qiskit_ibm_runtime import SamplerV2
def run(arms, tag, cap):
    sm = SamplerV2(mode=be); sm.options.dynamical_decoupling.enable = False
    sm.options.twirling.enable_gates = False; sm.options.twirling.enable_measure = False; sm.options.max_execution_time = cap
    json.dump(be.properties(refresh=True).to_dict(), open(os.path.join(HERE, f'props_before_{tag}.json'), 'w'), default=str)
    job = sm.run([(t, None, sh) for _, t, sh in arms]); jid = job.job_id(); t0 = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    J = json.load(open(os.path.join(HERE, 'jobs_tele.json'))) if os.path.exists(os.path.join(HERE, 'jobs_tele.json')) else {}
    J[tag] = dict(job_id=jid, submitted=t0, cap=cap, circuits=len(arms)); json.dump(J, open(os.path.join(HERE, 'jobs_tele.json'), 'w'), indent=1)
    print('SUBMITTED', tag, jid, t0, flush=True)
    res = job.result(); raw = {}
    for (k, _, _), r in zip(arms, res):
        raw[k] = ([int(b, 2) for b in r.data.alice.get_bitstrings()], [int(b, 2) for b in r.data.bob.get_bitstrings()])
    m = job.metrics() or {}; J[tag].update(usage=m.get('usage'), timestamps=m.get('timestamps')); json.dump(J, open(os.path.join(HERE, 'jobs_tele.json'), 'w'), indent=1, default=str)
    json.dump(be.properties(refresh=True).to_dict(), open(os.path.join(HERE, f'props_after_{tag}.json'), 'w'), default=str)
    print('DONE', tag, 'usage', m.get('usage'), flush=True); return raw
rawA = run(A, 'A', CAP_A); json.dump(rawA, open(os.path.join(HERE, 'raw_jobA.json'), 'w'))
rawB = run(B, 'B', CAP_B); json.dump(rawB, open(os.path.join(HERE, 'raw_jobB.json'), 'w'))
out = analyse({**rawA, **rawB}); open(os.path.join(HERE, 'results_tele.text'), 'w').write(json.dumps(out, indent=1, default=float)); print('ANALYSED', flush=True)
