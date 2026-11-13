"""2026-09-29 RAW RE-PULL, Braket (Wayfinder: "go back more so we can go forward"). Every COMPLETED task since 2026-09-01 on our account:
the task record (created/ended, device, shots, metadata) + the full results.json from our own S3 output, saved gzipped and untouched --
every measured qubit column, every shot, in shot order. Skips tasks already saved. One task at a time."""
import boto3, json, gzip, os, sys
OUT = os.path.expanduser('~/bones-forge/standoff/raw_repull'); s = boto3.Session(profile_name='braket', region_name='us-west-1')
b = s.client('braket'); s3 = s.client('s3'); log = open(os.path.join(OUT, 'repull.log'), 'a')
def P(*a):
    t = ' '.join(str(x) for x in a); print(t, flush=True); log.write(t + '\n'); log.flush()
tasks, tok = [], None
while True:
    kw = dict(filters=[{'name': 'createdAt', 'operator': 'GT', 'values': ['2026-09-01T00:00:00Z']}], maxResults=100)
    if tok: kw['nextToken'] = tok
    r = b.search_quantum_tasks(**kw); tasks += r['quantumTasks']; tok = r.get('nextToken')
    if not tok: break
P('tasks listed', len(tasks))
done = fail = 0
for t in tasks:
    tid = t['quantumTaskArn'].split('/')[-1]; f = os.path.join(OUT, tid + '.json.gz')
    if os.path.exists(f): continue
    try:
        d = b.get_quantum_task(quantumTaskArn=t['quantumTaskArn'])
        rec = {k: (v.isoformat() if hasattr(v, 'isoformat') else v) for k, v in d.items() if k != 'ResponseMetadata'}
        res = None
        if d.get('status') == 'COMPLETED':
            key = d['outputS3Directory'].rstrip('/') + '/results.json'
            res = json.loads(s3.get_object(Bucket=d['outputS3Bucket'], Key=key)['Body'].read())
        with gzip.open(f, 'wt') as fh: json.dump({'task': rec, 'results': res}, fh)
        done += 1
        if done % 25 == 0: P('saved', done)
    except Exception as e:
        fail += 1; P(tid, 'FAILED', str(e)[:160])
P('DONE saved', done, 'failed', fail)
