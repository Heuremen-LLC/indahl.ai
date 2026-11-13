"""pull_history.py -- every quantum job/task this account has on record since 1 September 2026, as the vendors' own services list them.
IBM: QiskitRuntimeService.jobs (the history the service retains) + per-job metrics (quantum seconds). Braket: search_quantum_tasks.
No chip time is used; list calls only. Account numbers are blanked. Output: ibm_jobs.json, braket_tasks.json (raw lists)."""
import json, os, re, sys, datetime as dt
os.environ.setdefault('AWS_PROFILE', 'braket')
sys.path.insert(0, os.path.expanduser('~/bones-forge/parallax/out/qubit_fifth_run'))
HERE = os.path.dirname(os.path.abspath(__file__)); SINCE = dt.datetime(2026, 9, 1, tzinfo=dt.timezone.utc)
blank = lambda s: re.sub(r'(arn:aws:braket:[a-z0-9-]+:)[0-9]{12}:', r'\1ACCOUNT:', s)

def ibm():
    import live
    svc, _ = live.open_service('run index: job history (list only)')
    out = []
    for j in svc.jobs(limit=None, created_after=SINCE):
        try: m = j.metrics()
        except Exception as e: m = {'error': type(e).__name__}
        u = (m.get('usage') or {}) if isinstance(m, dict) else {}; ts = (m.get('timestamps') or {}) if isinstance(m, dict) else {}
        out.append({'job_id': j.job_id(), 'chip': j.backend().name if j.backend() else None, 'created': str(j.creation_date), 'status': str(j.status()),
                    'tags': list(j.tags or []), 'quantum_seconds': u.get('quantum_seconds'), 'running': ts.get('running'), 'finished': ts.get('finished')})
    json.dump(out, open(os.path.join(HERE, 'ibm_jobs.json'), 'w'), indent=1); print('ibm jobs', len(out))

def braket():
    import boto3
    c = boto3.client('braket', region_name='us-west-1'); out = []; tok = None
    for region in ('us-west-1', 'us-east-1', 'eu-north-1'):
        c = boto3.client('braket', region_name=region); tok = None
        while True:
            kw = {'filters': [{'name': 'createdAt', 'operator': 'GTE', 'values': [SINCE.strftime('%Y-%m-%dT%H:%M:%SZ')]}], 'maxResults': 100}
            if tok: kw['nextToken'] = tok
            r = c.search_quantum_tasks(**kw)
            for t in r['quantumTasks']:
                out.append({'task': blank(t['quantumTaskArn']), 'device': t['deviceArn'].split('/')[-1], 'region': region, 'status': t['status'], 'shots': t.get('shots'),
                            'created': str(t['createdAt']), 'ended': str(t.get('endedAt'))})
            tok = r.get('nextToken')
            if not tok: break
    json.dump(out, open(os.path.join(HERE, 'braket_tasks.json'), 'w'), indent=1); print('braket tasks', len(out))

if __name__ == '__main__':
    for f in sys.argv[1:] or ['ibm', 'braket']: globals()[f]()
