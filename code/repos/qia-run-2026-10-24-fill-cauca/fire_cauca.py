"""fire_cauca.py -- free calibration run for arXiv:2605.30676 on ibm_kingston (Darkwave Disco, via sweep_run/sweep.py's service()).
Design fixed in PLAN_CAUCA.md.text: their SUBMITTED transpiled circuits (theirs/job_metadata_L2.json, _L0.json), unchanged, N=2..9, first 12 of 20 identical reps,
2048 shots, default SamplerV2 options (theirs were {}), four jobs in the order A B B A (A = L2, B = L0), each after the previous finishes; the backend record is saved
before every job and after the last. Cap 300 QPU s. Usage: fire_cauca.py (dry run: checks the target, prints estimate and remaining seconds) | fire_cauca.py --fire"""
import json, sys, time, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
from sweep import service
import twin_cauca as T
CHIP = 'ibm_kingston'; SHOTS = 2048; REPS = 12; ORDER = ['A', 'B', 'B', 'A']; LEVEL = {'A': 'L2', 'B': 'L0'}; EST_PER_JOB = 52; CAP = 300
circ = {a: T.load_circuits(LEVEL[a]) for a in 'AB'}
sel = [i * T.NREP + j for i in range(8) for j in range(REPS)]
pubs = {a: [circ[a][i] for i in sel] for a in 'AB'}
s = service(); b = s.backend(CHIP); tg = b.target
assert 'cz' in tg.operation_names and 'ecr' not in tg.operation_names, ('kingston native 2q gate is not CZ', sorted(tg.operation_names))
bad = []
for a in 'AB':
    for c in pubs[a]:
        for ins in c.data:
            if ins.operation.name in ('barrier',): continue
            qs = tuple(c.find_bit(q).index for q in ins.qubits)
            if ins.operation.name not in tg.operation_names or not tg.instruction_supported(ins.operation.name, qs): bad.append((ins.operation.name, qs))
rem = s.usage().get('usage_remaining_seconds')
nshots = 4 * len(sel) * SHOTS
print(f'{CHIP}: native 2q = cz (ops {sorted(tg.operation_names)}); 4 jobs x {len(sel)} circuits x {SHOTS} shots = {nshots} shots; unsupported ops now: {len(set(bad))}; est {EST_PER_JOB * 4} s (cap {CAP}), remaining {rem}', flush=True)
if '--fire' not in sys.argv: sys.exit(0)
if bad: print('STOP: an op of their circuits is not supported by the current kingston target', sorted(set(bad))[:5]); sys.exit(1)
if rem is not None and (rem < EST_PER_JOB * 4 + 30): print('STOP: not enough seconds'); sys.exit(1)
from qiskit_ibm_runtime import SamplerV2
rec = dict(chip=CHIP, order=ORDER, jobs=[]); spent = 0
for k, arm in enumerate(ORDER, 1):
    if spent + EST_PER_JOB > CAP: print('STOP: cap'); break
    json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_cauca_before_{k}.json', 'w'), default=str)
    job = SamplerV2(mode=b).run([(c, None, SHOTS) for c in pubs[arm]])
    sub = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()); print(f'SUBMITTED job {k} {arm} {job.job_id()} {sub}', flush=True)
    res = job.result(); ents = []
    for idx, pr in zip(sel, res): ents.append(dict(N=idx // T.NREP + 2, rep=idx % T.NREP, counts=pr.data.c.get_counts()))
    json.dump(ents, open(f'{HERE}/raw_cauca_{k}.json', 'w'))
    m = job.metrics(); u = (m.get('usage') or {}).get('qpu_charge_time_seconds') or EST_PER_JOB; spent += u
    rec['jobs'].append(dict(label=str(k), arm=arm, level=LEVEL[arm], job_id=job.job_id(), submitted_utc=sub, usage=m.get('usage'), timestamps=m.get('timestamps')))
    json.dump(rec, open(f'{HERE}/job_cauca.json', 'w'), default=str); print(f'DONE job {k} {arm} usage {m.get("usage")} spent {spent}', flush=True)
json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_cauca_after.json', 'w'), default=str)
print('ALL DONE', flush=True)
