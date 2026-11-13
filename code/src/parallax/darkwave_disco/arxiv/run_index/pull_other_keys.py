"""pull_other_keys.py -- job history seen by each IBM key file on disk (list calls only; tokens never printed). Adds jobs the run harness's key does not see."""
import json, os, datetime as dt
from qiskit_ibm_runtime import QiskitRuntimeService
H = os.path.expanduser('~/bones-forge'); SINCE = dt.datetime(2026, 9, 1, tzinfo=dt.timezone.utc); seen = {}
for f in ['.ibm_quantum_key', '.ibm_quantum_key_2', '.ibm_quantum_key_3', '.ibm_quantum_key_4', '.ibm_quantum_key_parallax']:
    try:
        svc = QiskitRuntimeService(channel='ibm_quantum_platform', token=open(os.path.join(H, f)).read().strip())
        js = list(svc.jobs(limit=None, created_after=SINCE)); n = 0
        for j in js:
            if j.job_id() in seen: continue
            n += 1; seen[j.job_id()] = {'job_id': j.job_id(), 'chip': j.backend().name if j.backend() else None, 'created': str(j.creation_date), 'status': str(j.status()), 'tags': list(j.tags or []), 'key': f}
        print(f, 'jobs', len(js), 'new', n)
    except Exception as e: print(f, 'no:', type(e).__name__)
json.dump(list(seen.values()), open('ibm_jobs_all_keys.json', 'w'), indent=1); print('total', len(seen))
