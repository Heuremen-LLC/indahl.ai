"""choose_layouts.py -- rule fixed BEFORE any job. On ibm_kingston's record at choice time: every simple 6-qubit path (depth-first from every
start, neighbours ascending, first 60 per start); score = worst CZ error on its 5 edges + worst readout error of its 6 qubits (missing value or
cz error >= 1.0 excludes). 'theirs' = their chain 21-36-41-42-43-44 (budget.py CHAIN_ORDER). Take best and 50th percentile, each disjoint from
theirs and from each other. Path position i -> logical role ROLE_ORDER[i] = (q4, q2, q0, q1, q3, q5), as their chain."""
import sys, os, json, time
sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run')); from sweep import service
be = service().backend('ibm_kingston'); pr = be.properties(refresh=True)
ro = {q: pr.readout_error(q) for q in range(be.num_qubits)}; cz = {}
for g in pr.gates:
    if g.gate == 'cz':
        e = [p.value for p in g.parameters if p.name == 'gate_error']
        if e: cz[frozenset(g.qubits)] = e[0]
adj = {}
for a, b in be.coupling_map.get_edges(): adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
def score(p):
    es = [cz.get(frozenset((p[i], p[i + 1]))) for i in range(5)]; rs = [ro.get(q) for q in p]
    if any(e is None or e >= 1.0 for e in es) or any(r is None for r in rs): return None
    return max(es) + max(rs)
paths = set()
for s in sorted(adj):
    found = []
    def walk(p):
        if len(found) >= 60: return
        if len(p) == 6: found.append(tuple(p)); return
        for n in sorted(adj[p[-1]]):
            if n not in p: walk(p + [n])
    walk([s]); paths |= set(found)
sc = sorted((v, p) for p in paths if (v := score(p)) is not None); n = len(sc)
THEIRS = (21, 36, 41, 42, 43, 44)
ch = {'theirs': dict(path=list(THEIRS), score=score(THEIRS), rank=[i for i, (_, p) in enumerate(sc) if p in (THEIRS, THEIRS[::-1])][:1])}
used = set(THEIRS)
for name, f in (('best', 0.0), ('q50', 0.5)):
    i = int(f * (n - 1))
    while set(sc[i][1]) & used: i += 1
    s_, p = sc[i]; used |= set(p); ch[name] = dict(path=list(p), score=s_, rank=i)
ch['_meta'] = dict(paths_scored=n, record_last_update=str(pr.last_update_date), chosen_at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
json.dump(ch, open('layouts_chosen.json', 'w'), indent=1); print(json.dumps({k: (v.get('path'), round(v.get('score') or 0, 4), v.get('rank')) if k != '_meta' else v for k, v in ch.items()}))
