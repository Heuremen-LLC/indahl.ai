#!/usr/bin/env python3
"""Written-off anomalies -> IBM job metadata (read-only: job.metrics(), no submits, no runtime).
Qubits come from dark_floor_runs/energy_ledger_timing.json (compiled layouts) or the run files. Writes anomaly_jobs.json."""
import json, os
from qiskit_ibm_runtime import QiskitRuntimeService
H = os.path.dirname(os.path.abspath(__file__))
DF = os.path.expanduser('~/bones-forge/dark_floor_runs')
timing = json.load(open(os.path.join(DF, 'energy_ledger_timing.json')))
qs = lambda k: sorted({m['q'] for p in timing[k]['pubs'] for m in p['meas']})
A = {
 'first-look dip (dark_link, 16/16 pairs)': [(timing[k]['job'], k) for k in timing if k.startswith('dark_link')],
 'empty corner 11 positive (three_box, 3 chips)': [(timing[k]['job'], k) for k in timing if k.startswith('three_box')],
 't=30 excess (dark_floor run 1, z~2.2)': [('daqlf73t55cs738rtfv0', None), ('daqljjqkqcdc73aau0n0', None)],
 'Kingston q1 false-1 33% (arrow BASE/REV)': [(timing['arrow/ibm_kingston']['job'], 'arrow/ibm_kingston')],
}
dfq = {}
for f in ('dark_floor_real_20260924_131028.json', 'dark_floor_real_20260924_135201.json'):
    d = json.load(open(os.path.join(DF, f)))
    for c in d['chips']:
        dfq[c['job_id']] = sorted({q for p in c['pairs'] for q in (p if isinstance(p, list) else [p.get('a'), p.get('b')])})
# the 9/24 jobs are spread across the three held keys (same as energy_ledger_fetch.py); try each, read-only
svcs = [QiskitRuntimeService(channel='ibm_quantum_platform', token=open(os.path.expanduser('~/bones-forge/' + k)).read().strip())
        for k in ('.ibm_quantum_key', '.ibm_quantum_key_2', '.ibm_quantum_key_3') if os.path.exists(os.path.expanduser('~/bones-forge/' + k))]


def getjob(jid):
    for s in svcs:
        try:
            return s.job(jid)
        except Exception:
            pass
    raise SystemExit('job not visible to any key: ' + jid)
out = []
for anom, jobs in A.items():
    for jid, key in jobs:
        cp = os.path.join(H, 'cache', 'ibm_jobs', jid + '.json')
        if os.path.exists(cp):
            m = json.load(open(cp))
        else:
            j = getjob(jid)
            m = {'backend': j.backend().name, 'metrics': j.metrics()}
            json.dump(m, open(cp, 'w'), default=str)
        ts = m['metrics'].get('timestamps', {})
        out.append({'anomaly': anom, 'job': jid, 'label': key, 'backend': m['backend'],
                    'qubits': qs(key) if key else dfq.get(jid), 'created': ts.get('created'),
                    'running': ts.get('running'), 'finished': ts.get('finished'),
                    'quantum_s': m['metrics'].get('usage', {}).get('quantum_seconds')})
        print(out[-1])
json.dump(out, open(os.path.join(H, 'anomaly_jobs.json'), 'w'), indent=1)
