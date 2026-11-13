"""choose_layouts.py -- rule fixed BEFORE any job: on ibm_fez's record at choice time, enumerate every simple 5-qubit path; score = worst CZ error on its
4 edges + worst readout error of its 5 qubits (record cz gate_error = 1.0 or any missing value excludes the path). Take the best, then the 25th, 50th
and 75th percentile paths, each disjoint from those already taken. Logical order on a path [p0..p4] -> logical qubits [1, 0, 2, 3, 4] (q0 between q1 and q2)."""
import sys, os, json, time
sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run')); from sweep import service
be = service().backend('ibm_fez'); pr = be.properties(refresh=True); cm = be.coupling_map
ro = {q: pr.readout_error(q) for q in range(be.num_qubits)}
cz = {}
for g in pr.gates:
    if g.gate == 'cz':
        a, b = g.qubits; e = [p.value for p in g.parameters if p.name == 'gate_error']
        if e: cz[frozenset((a, b))] = e[0]
adj = {}
for a, b in cm.get_edges(): adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
paths = set()
def walk(p):
    if len(p) == 5:
        t = tuple(p) if p[0] < p[-1] else tuple(reversed(p)); paths.add(t); return
    for n in adj.get(p[-1], ()):
        if n not in p: walk(p + [n])
for q in adj: walk([q])
sc = []
for p in paths:
    es = [cz.get(frozenset((p[i], p[i + 1]))) for i in range(4)]; rs = [ro.get(q) for q in p]
    if any(e is None or e >= 1.0 for e in es) or any(r is None for r in rs): continue
    sc.append((max(es) + max(rs), p))
sc.sort(); n = len(sc); chosen = {}; used = set()
for name, f in (('best', 0.0), ('q25', 0.25), ('q50', 0.50), ('q75', 0.75)):
    i = int(f * (n - 1))
    while set(sc[i][1]) & used: i += 1
    s, p = sc[i]; used |= set(p); chosen[name] = dict(path=list(p), score=s, rank=i, layout=[p[1], p[0], p[2], p[3], p[4]])
chosen['_meta'] = dict(paths_scored=n, record_last_update=str(pr.last_update_date), chosen_at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
json.dump(chosen, open('layouts_chosen.json', 'w'), indent=1); print(json.dumps(chosen, indent=1))
