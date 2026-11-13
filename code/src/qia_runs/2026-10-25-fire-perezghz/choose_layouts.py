"""choose_layouts.py -- rule fixed BEFORE any job. On ibm_fez's record at choice time: from every start qubit, depth-first search with neighbours
in ascending index order, keeping the first 40 simple 12-qubit paths per start; score = worst CZ error on its 11 edges + worst readout error of its
12 qubits (a record cz gate_error >= 1.0 or a missing value excludes the path). Take best, 25th, 50th, 75th percentile, each disjoint from those taken.
Logical qubit i -> path[i] (the CX chain runs along the path)."""
import sys, os, json, time
sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run')); from sweep import service
be = service().backend('ibm_fez'); pr = be.properties(refresh=True)
ro = {q: pr.readout_error(q) for q in range(be.num_qubits)}; cz = {}
for g in pr.gates:
    if g.gate == 'cz':
        e = [p.value for p in g.parameters if p.name == 'gate_error']
        if e: cz[frozenset(g.qubits)] = e[0]
adj = {}
for a, b in be.coupling_map.get_edges(): adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
paths = set()
for s in sorted(adj):
    found = []
    def walk(p):
        if len(found) >= 40: return
        if len(p) == 12: found.append(tuple(p)); return
        for n in sorted(adj[p[-1]]):
            if n not in p: walk(p + [n])
    walk([s]); paths |= set(found)
sc = []
for p in paths:
    es = [cz.get(frozenset((p[i], p[i + 1]))) for i in range(11)]; rs = [ro.get(q) for q in p]
    if any(e is None or e >= 1.0 for e in es) or any(r is None for r in rs): continue
    sc.append((max(es) + max(rs), p))
sc.sort(); n = len(sc); ch = {}; used = set()
for name, f in (('best', 0.0), ('q25', 0.25), ('q50', 0.5), ('q75', 0.75)):
    i = int(f * (n - 1))
    while set(sc[i][1]) & used: i += 1
    s, p = sc[i]; used |= set(p); ch[name] = dict(path=list(p), score=s, rank=i)
ch['_meta'] = dict(paths_scored=n, record_last_update=str(pr.last_update_date), chosen_at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
json.dump(ch, open('layouts_chosen.json', 'w'), indent=1); print(json.dumps({k: (v.get('path'), round(v.get('score', 0), 4), v.get('rank')) if k != '_meta' else v for k, v in ch.items()}))
