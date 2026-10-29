#!/usr/bin/env python3
"""digest.py: ARCHIVE per PLAN.md. Hashes the live corners' records into a manifest, chains the digest, stamps it with OpenTimestamps, copies the chain to the public repo.
Modes: (default) append a digest; --upgrade only upgrades stamps; --verify recomputes the last manifest and checks the chain."""
import os, sys, json, glob, hashlib, time, subprocess, fcntl
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.expanduser('~/bones-forge'); os.chdir(H); os.makedirs('manifests', exist_ok=True); os.makedirs('stamps', exist_ok=True)
PUB = R + '/public_mirror/indahl.ai/code/archive'; OTS = H + '/venv/bin/ots'
_l = open('.lock', 'w')
try: fcntl.flock(_l, fcntl.LOCK_EX | fcntl.LOCK_NB)
except OSError: sys.exit(0)
def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()
PATTERNS = ['*_index/PLAN*.md', '*_index/data/history*.jsonl', '*_index/data/changes.jsonl', '*_index/data/rows.json', '*_index/data/cancelled.json', '*_index/data/hand_checked.json', '*_index/data/repos.json', '*_index/data/projects.json', '*_index/data/domains.json',
            '*_index/summary*.json', 'qia_mirror/AUDIT_PLAN.md', 'qia_mirror/STABILITY_PLAN.md', 'qia_mirror/changes.jsonl', 'qia_mirror/polls.jsonl', 'qia_mirror/summary.json', 'qia_mirror/audit.json', 'qia_mirror/records/*', 'qia_queue/PLAN.md', 'qia_queue/data/*.jsonl',
            't1t2_check/PLAN.md', 't1t2_check/runs/*.json', 'coin_index/PROGRESS.md', 'coin_index/summary_trends.json', 'trials_index/PLAN.md', 'trials_index/data/summary.json', 'archive/PLAN.md', 'replies/PLAN.md',
            'ledger/ledger.jsonl', 'qia_leads/THE_BOOK.md']
INTERNAL = {'ledger/ledger.jsonl', 'qia_leads/THE_BOOK.md'}
def manifest():
    files = {}
    for pat in PATTERNS:
        for p in sorted(glob.glob(os.path.join(R, pat))):
            if os.path.isfile(p): files[os.path.relpath(p, R)] = dict(sha256=sha(p), bytes=os.path.getsize(p))
    return files
chain = [json.loads(l) for l in open('chain.jsonl')] if os.path.exists('chain.jsonl') else []
def stamp(path):
    r = subprocess.run([OTS, 'stamp', path], capture_output=True, text=True, timeout=180); return r.returncode == 0
def upgrade():
    n = 0
    for p in sorted(glob.glob('stamps/*.ots')):
        r = subprocess.run([OTS, 'upgrade', p], capture_output=True, text=True, timeout=180)
        if 'Success' in (r.stdout + r.stderr) or 'upgraded' in (r.stdout + r.stderr).lower(): n += 1
    return n
def publish():
    os.makedirs(PUB + '/manifests', exist_ok=True); os.makedirs(PUB + '/stamps', exist_ok=True)
    subprocess.run(['cp', 'chain.jsonl', PUB + '/chain.jsonl']); subprocess.run('cp manifests/* %s/manifests/ 2>/dev/null; cp stamps/* %s/stamps/ 2>/dev/null; cp PLAN.md digest.py %s/' % (PUB, PUB, PUB), shell=True)
def internal_marked(m):
    return {k: (dict(sha256=v['sha256'], bytes=v['bytes'], internal=True) if k in INTERNAL else v) for k, v in m.items()}
if '--verify' in sys.argv:
    ok = True; prev = '0' * 64
    for e in chain:
        mp = 'manifests/%s.json' % e['id']; msha = sha(mp) if os.path.exists(mp) else None
        d = hashlib.sha256((prev + (msha or '')).encode()).hexdigest()
        if msha != e['manifest_sha256'] or d != e['digest'] or e['prev'] != prev: ok = False; print('BROKEN at', e['id'])
        prev = e['digest']
    print('chain', 'OK' if ok else 'BROKEN', len(chain), 'entries'); sys.exit(0 if ok else 1)
if '--upgrade' in sys.argv: print('upgraded', upgrade()); publish(); sys.exit(0)
m = internal_marked(manifest()); t = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()); prev = chain[-1]['digest'] if chain else '0' * 64
old = json.load(open('manifests/%s.json' % chain[-1]['id'])) if chain else {'files': {}}
removed = sorted(set(old['files']) - set(m)); changed = sum(1 for k, v in m.items() if old['files'].get(k, {}).get('sha256') != v['sha256'])
mf = dict(id=t, prev_digest=prev, files=m, removed=removed)
mp = 'manifests/%s.json' % t; json.dump(mf, open(mp, 'w'), sort_keys=True, indent=0)
msha = sha(mp); digest = hashlib.sha256((prev + msha).encode()).hexdigest()
entry = dict(id=t, prev=prev, manifest_sha256=msha, digest=digest, files=len(m), changed=changed, removed=len(removed))
with open('chain.jsonl', 'a') as f: f.write(json.dumps(entry) + '\n')
open('stamps/%s.digest' % t, 'w').write(digest + '\n'); ok = stamp('stamps/%s.digest' % t)
n = upgrade(); publish()
print('archive: digest', digest[:16], 'files', len(m), 'changed', changed, 'removed', len(removed), 'stamp', 'ok' if ok else 'FAILED', 'upgraded', n)
