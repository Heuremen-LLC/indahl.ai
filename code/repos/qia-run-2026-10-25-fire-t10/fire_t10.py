"""fire_t10.py --dry | --fire : job A (ibm_fez, 4,000 shots, opt 0, no runtime DD/twirling): free, cpmg, t10 at 8 delays on the four chosen qubits
in parallel (one circuit carries all four), T10 set twice (copies a, b) = 32 circuits, interleaved by delay; job B right after A returns: t10 and cpmg
again (16). Refuses if fez not active or remaining - CAP < RESERVE."""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
from t10 import circuit, DELAYS_US, SHOTS
from t10_fill import analyse
from sweep import service
from qiskit import transpile
CAP, RESERVE = 300, 300
Q = json.load(open(os.path.join(HERE, 'qubits_chosen.json'))); QB = [Q[k]['qubit'] for k in ('best', 'q25', 'q50', 'q75')]
s = service(); rem = s.usage().get('usage_remaining_seconds'); be = s.backend('ibm_fez'); st = be.status(); print('remaining', rem, 'fez', st.status_msg, st.pending_jobs, 'qubits', QB, flush=True)
fire = '--fire' in sys.argv
if fire and (rem is None or rem - CAP < RESERVE or str(st.status_msg).lower() != 'active'): sys.exit('REFUSED')
def build(arm, t): return transpile(circuit(arm, t, QB, be.dt), be, optimization_level=0, initial_layout=list(range(be.num_qubits)))
A = []
for i, t in enumerate(DELAYS_US):
    for arm, cp in (('free', 'a'), ('cpmg', 'a'), ('t10', 'a'), ('t10', 'b')): A.append(((arm, cp, i), build(arm, t)))
meas = sorted({A[0][1].find_bit(x.qubits[0]).index for x in A[0][1].data if x.operation.name == 'measure'})
dur = {k: (c.count_ops().get('x', 0), c.count_ops().get('delay', 0)) for k, c in A[:8]}; print('measured', meas, 'x/delay counts', {str(k): v for k, v in dur.items()}, flush=True)
if not fire: open(os.path.join(HERE, 'dry_run_t10.text'), 'w').write(json.dumps(dict(measured=meas, counts={str(k): v for k, v in dur.items()}), indent=1)); sys.exit(0)
from qiskit_ibm_runtime import SamplerV2
json.dump(be.properties(refresh=True).to_dict(), open(os.path.join(HERE, 'props_before.json'), 'w'), default=str)
def run(items):
    j = SamplerV2(mode=be).run([c for _, c in items], shots=SHOTS); rec = dict(job_id=j.job_id(), submitted=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())); print('SUBMITTED', rec, flush=True)
    res = j.result(); rec['metrics'] = j.metrics(); return rec, [r.data.c.get_counts() for r in res]
recA, cA = run(A)
raw = {}
for (k, _), c in zip(A, cA): raw.setdefault(k[0], {}).setdefault(k[1], [None] * len(DELAYS_US))[k[2]] = c
B = [((arm, 'jobB', i), build(arm, t)) for i, t in enumerate(DELAYS_US) for arm in ('cpmg', 't10')]
recB, cB = run(B)
for (k, _), c in zip(B, cB): raw.setdefault(k[0], {}).setdefault(k[1], [None] * len(DELAYS_US))[k[2]] = c
json.dump(dict(A=recA, B=recB), open(os.path.join(HERE, 'jobs_t10.json'), 'w'), default=str); json.dump(raw, open(os.path.join(HERE, 'raw_counts.json'), 'w'))
out = analyse(raw); open(os.path.join(HERE, 'results_t10.text'), 'w').write(json.dumps(out, indent=1, default=float)); print(json.dumps({k: out[k] for k in ('KNOWN_GOOD', 'LAYOUT', 'POOLED', 'RANK')}, indent=1, default=float), flush=True)
