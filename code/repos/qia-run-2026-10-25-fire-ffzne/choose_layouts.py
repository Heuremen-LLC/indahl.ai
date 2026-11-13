"""choose_layouts.py -- rule fixed BEFORE any job. Pool: from every start qubit on ibm_fez, depth-first search (neighbours ascending), first 6 simple
50-qubit paths per start; record cz error >= 1.0 on any edge, or any qubit with no record T1/T2, excludes a path. Score every path with THEIR cost_func on the record saved now
(props_choice.json). THEIR selection: sort; drop z < -3 (their filter keeps z > -3); s1 = best, mid = equidistant midpoint, worst = last.
OURS added for the linearity test: q25 and q75 of the same filtered list (nearest rank). Measured: their score is the x-axis of their extrapolation."""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
import numpy as np
from sweep import service
from ffzne import build_qic, cost_func, midpoint_index
be = service().backend('ibm_fez'); pr = be.properties(refresh=True); json.dump(pr.to_dict(), open('props_choice.json', 'w'), default=str)
cz = {}
for g in pr.gates:
    if g.gate == 'cz':
        e = [p.value for p in g.parameters if p.name == 'gate_error']
        if e: cz[frozenset(g.qubits)] = e[0]
adj = {}
for a, b in be.coupling_map.get_edges(): adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
pool = set()
for s in sorted(adj):
    found = []
    def walk(p):
        if len(found) >= 6: return
        if len(p) == 50:
            if all(cz.get(frozenset((p[i], p[i + 1])), 1.0) < 1.0 for i in range(49)): found.append(tuple(p))
            return
        for n in sorted(adj[p[-1]]):
            if n not in p: walk(p + [n])
            if len(found) >= 6: return
    walk([s]); pool |= set(found)
miss = set()
for q in range(be.num_qubits):
    try: pr.qubit_property(q, 'T1'); pr.qubit_property(q, 'T2')
    except Exception: miss.add(q)
pool = sorted(p for p in pool if not set(p) & miss); t0 = time.time()
sc = sorted(cost_func(build_qic(), [list(p) for p in pool], be, pr))
x = np.array([s for s, _ in sc]); z = (x - x.mean()) / x.std(); kept = [r for r, zz in zip(sc, z) if zz > -3]; L = [s for s, _ in kept]
mi = midpoint_index(L); q25 = int(round(0.25 * (len(L) - 1))); q75 = int(round(0.75 * (len(L) - 1)))
ch = dict(s1=dict(score=kept[0][0], layout=kept[0][1]), mid=dict(score=kept[mi][0], layout=kept[mi][1], rank=mi), worst=dict(score=kept[-1][0], layout=kept[-1][1]),
          q25=dict(score=kept[q25][0], layout=kept[q25][1], rank=q25), q75=dict(score=kept[q75][0], layout=kept[q75][1], rank=q75),
          _meta=dict(pool=len(pool), excluded_qubits_no_T1T2=sorted(miss), kept=len(kept), score_range=[L[0], L[-1]], record_last_update=str(pr.last_update_date), chosen_at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), scoring_s=round(time.time() - t0)))
json.dump(ch, open('layouts_chosen.json', 'w'), indent=1); print(json.dumps({k: (round(v['score'], 4), v.get('rank')) if k != '_meta' else v for k, v in ch.items()}))
