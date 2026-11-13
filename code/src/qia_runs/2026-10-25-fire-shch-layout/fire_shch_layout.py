"""fire_shch_layout.py --dry | --fire : one fez job, 5 layout arms x 8 circuits (4 singlet + 4 product), 8000 shots, opt 1, layouts from layouts_chosen.json."""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
from shch import circuits, SHOTS
from shch_layout import analyse, ARMS
from sweep import service
from qiskit import transpile
CAP, RESERVE = 120, 300
LAY = json.load(open(os.path.join(HERE, 'layouts_chosen.json'))); LMAP = {'best_a': LAY['best']['triple'], 'best_b': LAY['best']['triple'], 'q25': LAY['q25']['triple'], 'q50': LAY['q50']['triple'], 'q75': LAY['q75']['triple']}
s = service(); rem = s.usage().get('usage_remaining_seconds'); be = s.backend('ibm_fez'); st = be.status(); print('remaining', rem, 'fez', st.status_msg, st.pending_jobs, flush=True)
fire = '--fire' in sys.argv
if fire and (rem is None or rem - CAP < RESERVE or str(st.status_msg).lower() != 'active'): sys.exit('REFUSED')
pubs, tags = [], []
for a in ARMS:
    for i, c in enumerate(circuits()):
        t = transpile(c, be, optimization_level=1, initial_layout=LMAP[a], seed_transpiler=3); pubs.append(t); tags.append(a)
chk = {a: sorted({t.find_bit(i.qubits[0]).index for t, g in zip(pubs, tags) if g == a for i in t.data if i.operation.name == 'measure'}) for a in ARMS}
print('measured qubits per arm', chk, flush=True)
if not fire: open(os.path.join(HERE, 'dry_run_shch_layout.text'), 'w').write(json.dumps(chk)); sys.exit(0)
json.dump(be.properties(refresh=True).to_dict(), open(os.path.join(HERE, 'props_before.json'), 'w'), default=str)
from qiskit_ibm_runtime import SamplerV2
job = SamplerV2(mode=be).run(pubs, shots=SHOTS); rec = dict(job_id=job.job_id(), submitted=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())); print('SUBMITTED', rec, flush=True)
res = job.result(); raw = {a: [] for a in ARMS}
for g, r in zip(tags, res): raw[g].append(r.data.c.get_counts())
m = job.metrics() or {}; rec.update(timestamps=m.get('timestamps')); json.dump(rec, open(os.path.join(HERE, 'job.json'), 'w'), default=str); json.dump(raw, open(os.path.join(HERE, 'raw_counts.json'), 'w'))
out = analyse(raw); open(os.path.join(HERE, 'results_shch_layout.text'), 'w').write(json.dumps(out, indent=1, default=float)); print(json.dumps(out, indent=1, default=float), flush=True)
