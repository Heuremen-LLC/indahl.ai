"""choose_qubits.py -- rule fixed BEFORE any job: on ibm_fez's record now, candidates = qubits with record T1, T2 and readout_error < 0.05. Rank by record
T2; take the best, then the 25th, 50th, 75th percentile, each at graph distance >= 3 from those already taken (no shared neighbours)."""
import sys, os, json, time
sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run')); from sweep import service
import rustworkx as rx
be = service().backend('ibm_fez'); pr = be.properties(refresh=True)
g = rx.PyGraph(); g.add_nodes_from(range(be.num_qubits))
for a, b in be.coupling_map.get_edges(): g.add_edge(a, b, None)
D = rx.distance_matrix(g)
c = []
for q in range(be.num_qubits):
    try: t1, t2, ro = pr.t1(q), pr.t2(q), pr.readout_error(q)
    except Exception: continue
    if ro < 0.05: c.append((t2, q, t1, ro))
c.sort(reverse=True); n = len(c); ch = []; out = {}
for name, f in (('best', 0.0), ('q25', 0.25), ('q50', 0.5), ('q75', 0.75)):
    i = int(f * (n - 1))
    while any(D[c[i][1]][x] < 3 for x in ch): i += 1
    t2, q, t1, ro = c[i]; ch.append(q); out[name] = dict(qubit=q, rank=i, T2_us=t2 * 1e6, T1_us=t1 * 1e6, readout=ro)
out['_meta'] = dict(candidates=n, record_last_update=str(pr.last_update_date), chosen_at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), dt=be.dt)
json.dump(out, open('qubits_chosen.json', 'w'), indent=1); print(json.dumps(out))
