"""fire_ktn.py --dry | --fire : one fez job; arms default_a/default_b (their compile: opt 1, no layout), best/q50/q75 (rule-chosen 4-qubit chains, pinned);
each arm = woven Z/XX/YY + aligned Z/XX/YY, 4096 shots."""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
from ktn import woven, aligned, basis_circs, analyse, SHOTS
from sweep import service
from qiskit import transpile
CAP, RESERVE = 60, 300
s = service(); rem = s.usage().get('usage_remaining_seconds'); be = s.backend('ibm_fez'); st = be.status(); print('remaining', rem, 'fez', st.status_msg, st.pending_jobs, flush=True)
fire = '--fire' in sys.argv
if fire and (rem is None or rem - CAP < RESERVE or str(st.status_msg).lower() != 'active'): sys.exit('REFUSED')
P = be.properties(); adj = {}
for a, c in be.coupling_map.get_edges(): adj.setdefault(a, set()).add(c)
paths = set()
def go(p):
    if len(p) == 4: paths.add(tuple(p) if p[0] < p[-1] else tuple(p[::-1])); return
    for n in adj.get(p[-1], []):
        if n not in p: go(p + [n])
for q in range(be.num_qubits): go([q])
sc = []
for p in paths:
    try: sc.append((max(P.gate_error('cz', [a, b]) for a, b in zip(p, p[1:])) + max(P.readout_error(q) for q in p), list(p)))
    except Exception: pass
sc = [x for x in sorted(sc) if x[0] < 0.5]; n = len(sc)
lay, used = {}, set()
for k, idx in (('best', 0), ('q50', n // 2), ('q75', 3 * n // 4)):
    i = idx
    while set(sc[i][1]) & used: i += 1
    lay[k] = sc[i][1]; used |= set(sc[i][1])
print('rule-chosen chains', lay, flush=True)
pubs, tags = [], []
for arm in ('default_a', 'default_b', 'best', 'q50', 'q75'):
    for state, base in (('woven', woven()), ('aligned', aligned())):
        for qc in basis_circs(base):
            kw = dict(optimization_level=1, seed_transpiler=11) if arm.startswith('default') else dict(optimization_level=1, initial_layout=lay[arm], seed_transpiler=11)
            t = transpile(qc, be, **kw); pubs.append(t); tags.append((arm, state))
info = {}
for (arm, state), t in zip(tags, pubs): info.setdefault(arm, set()).add(tuple(sorted({t.find_bit(i.qubits[0]).index for i in t.data if i.operation.name == 'measure'})))
print('measured qubits', {k: list(v) for k, v in info.items()}, 'woven cz', pubs[0].count_ops().get('cz', 0), flush=True)
json.dump(dict(chains=lay, measured={k: [list(x) for x in v] for k, v in info.items()}), open(os.path.join(HERE, 'dry_run_ktn.text' if not fire else 'layouts_used.json'), 'w'), indent=1)
if not fire: sys.exit(0)
json.dump(P.to_dict(), open(os.path.join(HERE, 'props_before.json'), 'w'), default=str)
from qiskit_ibm_runtime import SamplerV2
job = SamplerV2(mode=be).run(pubs, shots=SHOTS); rec = dict(job_id=job.job_id(), submitted=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())); print('SUBMITTED', rec, flush=True)
res = job.result(); raw = {}
for (arm, state), r in zip(tags, res): raw.setdefault(arm, {}).setdefault(state, []).append(r.data.meas.get_counts())
m = job.metrics() or {}; rec.update(timestamps=m.get('timestamps')); json.dump(rec, open(os.path.join(HERE, 'job.json'), 'w'), default=str); json.dump(raw, open(os.path.join(HERE, 'raw_counts.json'), 'w'))
out = analyse(raw); open(os.path.join(HERE, 'results_ktn.text'), 'w').write(json.dumps(out, indent=1, default=float)); print(json.dumps(out['SUMMARY'], indent=1, default=float), out['KNOWN_GOOD'], flush=True)
