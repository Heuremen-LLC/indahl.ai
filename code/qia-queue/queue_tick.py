#!/usr/bin/env python3
"""queue.py: reads IBM's pending-job count for every processor the paid instance sees, plus the waits our own jobs saw (created to running).
Runs on the HST tick bus every 9 ticks. Saves every read to data/history.jsonl, writes summary.json, pushes KV qia_queue. No QPU seconds."""
import os, sys, json, time, statistics as S, datetime as D, subprocess, fcntl
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.expanduser('~/bones-forge')
lock = open(os.path.join(H, 'data', '.lock'), 'w')
try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
except OSError: sys.exit(0)
now = D.datetime.now(D.timezone.utc)
def ts(x): return D.datetime.fromisoformat(x.replace('Z', '+00:00')) if x else None
rows = []; err = None; waits = {}; queued = {}; jobs_seen = []
try:
    from qiskit_ibm_runtime import QiskitRuntimeService
    s = QiskitRuntimeService(channel='ibm_cloud', token=open(os.path.join(ROOT, '.ibm_quantum_key_3')).read().strip(), instance=open(os.path.join(ROOT, '.ibm_quantum_instance_crn')).read().strip())
    for b in s.backends():
        st = b.status(); rows.append({'backend': b.name, 'pending': st.pending_jobs, 'operational': bool(st.operational), 'outcome': 'COMMITTED'})
    for j in s.jobs(limit=200):
        try:
            n = j.backend().name; m = j.metrics().get('timestamps', {}); c = ts(m.get('created')); r = ts(m.get('running'))
            if c and r: waits.setdefault(n, []).append((c, (r - c).total_seconds()))
            if c and r: jobs_seen.append({'id': j.job_id(), 'backend': n, 'created': m.get('created'), 'wait_s': (r - c).total_seconds()})
            elif c and not r and str(j.status()) in ('QUEUED', 'JobStatus.QUEUED'): queued.setdefault(n, []).append((now - c).total_seconds())
        except Exception: pass
except Exception as e: err = type(e).__name__
if not rows: rows = [{'backend': 'all', 'pending': None, 'outcome': 'NOTHING_RETURNED', 'error': err}]
T = now.strftime('%Y-%m-%dT%H:%M:%SZ')
jp = os.path.join(H, 'data', 'jobs.jsonl'); have = {json.loads(l)['id'] for l in open(jp)} if os.path.exists(jp) else set()
with open(jp, 'a') as f:
    for jb in jobs_seen:
        if jb['id'] not in have: f.write(json.dumps(jb) + '\n')
hp = os.path.join(H, 'data', 'history.jsonl')
with open(hp, 'a') as f:
    for r in rows: f.write(json.dumps(dict(r, t=T)) + '\n')
hist = [json.loads(l) for l in open(hp)]
def fmt(sec): return None if sec is None else (('%d s' % sec) if sec < 120 else ('%.0f min' % (sec / 60)) if sec < 7200 else ('%.1f h' % (sec / 3600)))
out = []
for r in rows:
    n = r['backend']; w = sorted(waits.get(n, []), key=lambda x: x[0])[-20:]; v = [x[1] for x in w]
    old = [h for h in hist if h['backend'] == n and h.get('pending') is not None and (now - ts(h['t'])).total_seconds() <= 86400]
    first = old[0]['pending'] if old else None
    out.append({'backend': n, 'pending': r.get('pending'), 'change_24h': (r['pending'] - first) if (first is not None and r.get('pending') is not None and len(old) > 1) else None,
                'our_jobs': len(v), 'our_median_wait': fmt(S.median(v)) if len(v) >= 3 else None, 'our_longest_wait': fmt(max(v)) if len(v) >= 3 else None,
                'our_queued_now': len(queued.get(n, [])), 'our_oldest_queued': fmt(max(queued[n])) if queued.get(n) else None, 'outcome': r['outcome']})
out.sort(key=lambda x: (x['pending'] is None, x['pending'] if x['pending'] is not None else 0))
summ = {'updated': now.strftime('%d %b %H:%M UTC'), 'reads_held': len(hist), 'processors': out}
json.dump(summ, open(os.path.join(H, 'summary.json'), 'w'), indent=1)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
r = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'qia_queue', '--path', os.path.join(H, 'summary.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=ROOT + '/cloudflare-workers/heuremen-door', env=env, capture_output=True, text=True)
PUB = ROOT + '/public_mirror/indahl.ai/code/qia-queue'
if os.path.isdir(PUB):
    import shutil
    for f, d in (('PLAN.md', 'PLAN.md'), ('queue_tick.py', 'queue_tick.py'), ('summary.json', 'summary.json'), ('data/history.jsonl', 'history.jsonl'), ('data/jobs.jsonl', 'jobs.jsonl')): shutil.copy(os.path.join(H, f), os.path.join(PUB, d))
print('qia_queue published' if r.returncode == 0 else 'qia_queue publish FAILED', len(out), 'processors')
