"""analyze_kumar.py -- reads raw_kumar_{A1,B1,B2,A2}.json, metas_kumar.json and props_kumar_before_*.json (written by fire_kumar.py), prints the four scored readings
DA, SET, BLM, DP with their outcomes (kumar.py) plus the descriptive lines, writes readings_kumar.json. Usage: analyze_kumar.py [dir]"""
import sys, os, json, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from kumar import *
D = sys.argv[1] if len(sys.argv) > 1 else H
UNIT = {'us': 1e-6, 'ms': 1e-3, 'ns': 1e-9, 's': 1.0, '': 1.0}
def qprop(props, q, name):
    for e in props['qubits'][q]:
        if e['name'] == name: return e['value'] * UNIT[e.get('unit', '')]
    raise KeyError(name)
metas = json.load(open(f'{D}/metas_kumar.json')); inst = {}; p = {}; rows = {}
m111 = {X: [m for m in metas[X] if m['setting'] == [1, 1, 1]][0] for X in 'AB'}
for l in LABELS:
    X = SET_OF[l]; raw = json.load(open(f'{D}/raw_kumar_{l}.json'))
    by = {(tuple(m['setting']), m['twirl']): m for m in metas[X]}
    recs = [dict(by[(tuple(r['setting']), r['twirl'])], counts_fin=r['counts_fin']) for r in raw]; inst[l] = inst_of(recs)
    props = json.load(open(f'{D}/props_kumar_before_{l}.json')); t2, ro = qprop(props, 6, 'T2'), qprop(props, 6, 'readout_error')
    wait = m111[X]['tau_w_s'] + m111[X]['pad_s']; p[l] = proj(t2, ro, wait)
    rows[l] = dict(q6_T2_us=t2 * 1e6, q6_readout_error=ro, wait_us=wait * 1e6, projection=p[l], baseline=float(inst[l][(1, 1, 1)].mean()))
r = readings(inst, p); r['per_job'] = rows
if os.path.exists(f'{D}/job_kumar.json'): r['job_times'] = [dict(label=j['label'], job_id=j['job_id'], timestamps=j.get('timestamps'), usage=j.get('usage')) for j in json.load(open(f'{D}/job_kumar.json'))['jobs']]   # times from IBM's job records (/q 30)
for l in LABELS: r.setdefault('per_job_delta', {})[l] = rows[l]['baseline'] - rows[l]['projection']
print(json.dumps(r, indent=1, default=float)); json.dump(r, open(f'{D}/readings_kumar.json', 'w'), indent=1, default=float)
