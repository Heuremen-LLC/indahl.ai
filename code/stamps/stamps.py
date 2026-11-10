#!/usr/bin/env python3
"""stamps.py: outside timestamps for every indahl.ai release (10 Nov 2026).

Proof for anyone, without trusting us, of what we published and when:
  manifest  run by ship.sh step 5 right after a worker deploy: sha256 of every file that deploy sent, with the URL each one is served at
            -> ledger/stamps/deployed_manifest.json (the changed-file list comes from comparing this with the last release, never a guess)
  release   run by ship.sh after VERIFY: writes ledger/stamps/release_<commit>.json (commit, sha256 of ledger.jsonl, the manifest and its
            sha256, the changed files, the previous release's sha256 so the releases chain), stamps it with OpenTimestamps, queues the
            changed public URLs for the Internet Archive and starts the paced Wayback run in the background
  wayback   Save Page Now, one request every 12 s, at most 50 per release, 429 backs off, the rest stays queued for the next release
            -> ledger/stamps/wayback.jsonl (capture URL and timestamp per URL)
  upgrade   ots upgrade on every pending release stamp (tick-bus rider), status in ledger/stamps/ots_status.json
  publish   copies releases, stamps and the index the page reads to the worker's public/receipts/stamps/ (served from the next deploy)
Every mode logs and exits 0: a stamp problem never fails a release.
Python 3.9 compatible (the tick bus runs the system python)."""
import os, sys, json, glob, time, hashlib, subprocess, fcntl, shutil, urllib.request, urllib.error, re

B = os.path.expanduser('~/bones-forge'); L = B + '/ledger'; S = L + '/stamps'; W = B + '/cloudflare-workers/heuremen-door'; I = B + '/indahl-ai'
OTS = B + '/archive/venv/bin/ots'; SITE = 'https://indahl.ai'; PUB = W + '/public/receipts/stamps'
UA = 'heuremen-archive/0.1 (+https://indahl.ai)'
PACE = 12; CAP = 50; MAX_TRIES = 3
FIRST = ['/', '/qia', '/iris', '/oy', '/atlas', '/hermes', '/social', '/darkwave', '/receipts/stamps', '/tape', '/changes']   # archived ahead of the rest
NOARCHIVE = {'/404', '/inquire-ok', '/inquire-error', '/inquiry', '/agree', '/request', '/respond'}   # the pages the sitemap leaves out
os.makedirs(S, exist_ok=True)


def log(*a):
    line = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()) + ' ' + ' '.join(str(x) for x in a)
    print('  stamps:', *a)
    try:
        with open(S + '/stamps.log', 'a') as f: f.write(line + '\n')
    except OSError: pass


def sha_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()


def sha_json(o):
    return hashlib.sha256(json.dumps(o, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def jload(p, d):
    try:
        with open(p) as f: return json.load(f)
    except (OSError, ValueError): return d


def jdump(p, o):
    t = p + '.tmp'
    with open(t, 'w') as f: json.dump(o, f, sort_keys=True, indent=1)
    os.replace(t, p)


def lock(name):
    f = open(S + '/.' + name + '.lock', 'w')
    try: fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError: return None
    return f


# ---- manifest: the same file set ship.sh hashes to decide a deploy (its NOW line), plus the JS modules wrangler bundles from indahl-ai
def deployed_files():
    fs = [W + '/worker.js', W + '/wrangler.toml', I + '/style.css'] + sorted(glob.glob(I + '/*.js')) + sorted(glob.glob(I + '/*.html'))
    for d in [I + '/' + x for x in ('oy', 'atlas', 'iris', 'qia', 'hermes', 'darkwave', 'media', 'receipts')] + [W + '/public']:
        for root, dirs, files in os.walk(d):
            for n in files: fs.append(os.path.join(root, n))
    out = []
    for p in sorted(set(fs)):
        if not os.path.isfile(p): continue
        if re.search(r'\.(bak|pre)[-.]|\.bak$|\.tmp$|/\.|\.pre-', p.replace(B, '')): continue   # backups beside sources are not served
        out.append(p)
    return out


def page_urls():
    """html file -> served path, read from pages.js (the map the worker imports)."""
    try: src = open(I + '/pages.js').read()
    except OSError: return {}
    imp = dict(re.findall(r"^import (P\d+) from '\./([^']+)';", src, re.M))
    m = re.search(r'export const PAGES = \{(.*?)\n\};', src, re.S)
    out = {}
    if m:
        for path, var in re.findall(r"'([^']+)': (P\d+)", m.group(1)):
            if var in imp: out[I + '/' + imp[var]] = path
    return out


def manifest():
    pages = page_urls(); files = {}
    for p in deployed_files():
        if p.startswith(W + '/public/'): key = p[len(W + '/public'):]; url = SITE + key
        elif p in pages: key = pages[p]; url = SITE + key
        elif p == I + '/style.css': key = '/style.css'; url = SITE + key
        else: key = 'code:' + os.path.relpath(p, B); url = None
        if key in files and not key.startswith('code:'): key = 'code:' + os.path.relpath(p, B); url = None
        files[key] = {'sha256': sha_file(p), 'bytes': os.path.getsize(p)}
        if url: files[key]['url'] = url
    m = {'at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'files': files}
    jdump(S + '/deployed_manifest.json', m)
    log('manifest', len(files), 'files, sha256', sha_json(files)[:16])


# ---- release
def git_head(repo):
    r = subprocess.run(['git', '-C', repo, 'rev-parse', 'HEAD'], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else 'unknown'


def releases():
    out = []
    try:
        for l in open(S + '/releases.jsonl'):
            l = l.strip()
            if l: out.append(json.loads(l))
    except OSError: pass
    return out


def ots_state(p):
    """'bitcoin <block>' once anchored, 'pending' while only calendar attestations, 'missing' or 'unreadable' otherwise."""
    if not os.path.exists(p): return 'missing'
    try: r = subprocess.run([OTS, 'info', p], capture_output=True, text=True, timeout=60)
    except Exception: return 'unreadable'
    if r.returncode: return 'unreadable'
    blocks = re.findall(r'BitcoinBlockHeaderAttestation\((\d+)\)', r.stdout)
    return ('bitcoin ' + min(blocks, key=int)) if blocks else 'pending'


def release():
    lk = lock('release')
    if not lk: log('release: another release step is running'); return
    m = jload(S + '/deployed_manifest.json', None)
    if not m: log('release: no deployed manifest yet (written at the next worker deploy)'); return
    rs = releases(); prev = rs[-1] if rs else None
    prev_doc = jload(S + '/' + prev['file'], {}) if prev else {}
    files = m['files']; msha = sha_json(files); lsha = sha_file(L + '/ledger.jsonl')
    if prev and prev.get('manifest_sha256') == msha and prev.get('ledger_sha256') == lsha:
        log('release: nothing deployed and no ledger change since', prev['id']); return
    old = prev_doc.get('manifest', {}).get('files', {})
    changed = sorted(k for k, v in files.items() if old.get(k, {}).get('sha256') != v['sha256'])
    removed = sorted(set(old) - set(files))
    commit = git_head(B + '/public_mirror/indahl.ai'); source = git_head(I); rid = commit[:12]
    if any(r['id'] == rid for r in rs): rid = rid + '-' + time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    doc = {'id': rid, 'site': SITE, 'publisher': 'Heuremen LLC', 'commit': commit,
           'repository': 'https://github.com/Heuremen-LLC/indahl.ai', 'source_commit': source, 'released_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
           'deployed_at': m['at'], 'ledger': {'file': 'ledger/ledger.jsonl', 'sha256': lsha, 'bytes': os.path.getsize(L + '/ledger.jsonl')},
           'manifest': {'sha256': msha, 'files': files}, 'changed': changed, 'removed': removed,
           'previous': ({'id': prev['id'], 'sha256': prev['sha256']} if prev else None)}
    fn = 'release_%s.json' % rid; fp = S + '/' + fn
    with open(fp, 'w') as f: json.dump(doc, f, sort_keys=True, indent=1)
    fsha = sha_file(fp)
    try:
        r = subprocess.run([OTS, 'stamp', fp], capture_output=True, text=True, timeout=120); ok = r.returncode == 0 and os.path.exists(fp + '.ots')
        if not ok: log('release: ots stamp FAILED', (r.stdout + r.stderr).strip()[-200:])
    except Exception as e: ok = False; log('release: ots stamp FAILED', e)
    row = {'id': rid, 'file': fn, 'sha256': fsha, 'commit': commit, 'released_at': doc['released_at'], 'manifest_sha256': msha,
           'ledger_sha256': lsha, 'files': len(files), 'changed': len(changed), 'removed': len(removed), 'ots': 'pending' if ok else 'failed'}
    with open(S + '/releases.jsonl', 'a') as f: f.write(json.dumps(row, sort_keys=True) + '\n')
    st = jload(S + '/ots_status.json', {}); st[rid] = row['ots']; jdump(S + '/ots_status.json', st)
    # queue every changed public URL (pages first, then data files), newest release ahead of older leftovers
    q = jload(S + '/wayback_queue.json', [])
    urls = [files[k]['url'] for k in changed if files[k].get('url') and k not in NOARCHIVE]
    urls.sort(key=lambda u: (FIRST.index(u[len(SITE):] or '/') if (u[len(SITE):] or '/') in FIRST else len(FIRST), 0 if not re.search(r'\.[a-z0-9]{1,6}$', u) else 1, u.count('/'), u))
    fresh = set(urls)
    jdump(S + '/wayback_queue.json', [{'url': u, 'release': rid, 'added': doc['released_at'], 'tries': 0} for u in urls] + [x for x in q if x['url'] not in fresh])
    log('release', rid, 'manifest', msha[:16], 'file', fsha[:16], 'changed', len(changed), 'removed', len(removed), 'ots', row['ots'], 'queued', len(urls))
    publish()
    # the Wayback run takes minutes at the polite pace, so it runs on its own and the release goes on
    try:
        lf = open(S + '/wayback_run.log', 'a')
        subprocess.Popen([sys.executable, '-I', os.path.abspath(__file__), 'wayback'], stdout=lf, stderr=lf, stdin=subprocess.DEVNULL, start_new_session=True, cwd=S)
        log('wayback: started in the background (log ledger/stamps/wayback_run.log)')
    except Exception as e: log('wayback: could not start', e)


# ---- wayback
def http(url, method='GET', timeout=120):
    req = urllib.request.Request(url, method=method, headers={'User-Agent': UA})

    class NoRedir(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k): return None
    op = urllib.request.build_opener(NoRedir)
    try:
        r = op.open(req, timeout=timeout); return r.status, dict(r.headers), r.read(200000)
    except urllib.error.HTTPError as e: return e.code, dict(e.headers or {}), b''
    except Exception as e: return 0, {'error': str(e)[:200]}, b''


def capture_of(url, headers, body):
    for h in ('Location', 'location', 'Content-Location', 'content-location'):
        v = headers.get(h)
        if v and '/web/' in v:
            v = v if v.startswith('http') else 'https://web.archive.org' + v
            m = re.search(r'/web/(\d{14})', v)
            return v, (m.group(1) if m else None)
    m = re.search(rb'/web/(\d{14})/', body or b'')
    if m: ts = m.group(1).decode(); return 'https://web.archive.org/web/%s/%s' % (ts, url), ts
    return None, None


def wayback():
    lk = lock('wayback')
    if not lk: log('wayback: a run is already going'); return
    q = jload(S + '/wayback_queue.json', [])
    if not q: log('wayback: queue empty'); return
    q.sort(key=lambda x: 0 if x.get('release') == (releases() or [{}])[-1].get('id') else 1)
    done, sent, keep, backoff, stopped, skipped = 0, 0, [], 60, False, 0
    for i, x in enumerate(q):
        if stopped or sent >= CAP: keep.append(x); continue   # the cap counts requests to the Archive, not queue entries
        u = x['url']
        st, _, _ = http(u, timeout=30)
        if st != 200:
            skipped += 1; log('wayback: skip', u, 'live answers', st); continue
        if sent: time.sleep(PACE)
        while True:
            st, hd, body = http('https://web.archive.org/save/' + u)
            if st == 429:
                if backoff > 600: log('wayback: 429 again after backing off, stopping; the rest waits for the next release'); stopped = True; break
                log('wayback: 429, waiting', backoff, 's'); time.sleep(backoff); backoff *= 2; continue
            break
        if stopped: keep.append(x); continue
        sent += 1
        cap, ts = capture_of(u, hd, body)
        row = {'at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'release': x.get('release'), 'url': u, 'status': st, 'capture': cap, 'timestamp': ts}
        if cap:
            with open(S + '/wayback.jsonl', 'a') as f: f.write(json.dumps(row, sort_keys=True) + '\n')
            done += 1
        else:
            x['tries'] = x.get('tries', 0) + 1
            if x['tries'] < MAX_TRIES: keep.append(x)
            log('wayback: no capture for', u, 'status', st, 'try', x['tries'])
    # a release may have queued more while this run went on: merge with the file as it is now, never write back a stale copy
    key = lambda x: (x['url'], x.get('release'))
    kept = dict((key(x), x) for x in keep); gone = set(key(x) for x in q) - set(kept)
    final = [kept.get(key(x), x) for x in jload(S + '/wayback_queue.json', []) if key(x) not in gone]
    jdump(S + '/wayback_queue.json', final)
    log('wayback: captured', done, 'of', sent, 'sent, skipped (not live)', skipped, 'queued for the next release', len(final))
    publish()


# ---- upgrade (tick-bus rider)
def upgrade():
    lk = lock('upgrade')
    if not lk: return
    st = jload(S + '/ots_status.json', {}); n = 0
    for p in sorted(glob.glob(S + '/release_*.json.ots')):
        rid = os.path.basename(p)[len('release_'):-len('.json.ots')]
        if str(st.get(rid, '')).startswith('bitcoin'): continue
        try: subprocess.run([OTS, 'upgrade', p], capture_output=True, text=True, timeout=120)
        except Exception as e: log('upgrade:', rid, e); continue
        s = ots_state(p)
        if s != st.get(rid): n += 1
        st[rid] = s
    jdump(S + '/ots_status.json', st)
    for b in glob.glob(S + '/release_*.json.ots.bak'): os.remove(b)   # ots upgrade keeps the old proof beside the new one
    if n: log('upgrade: changed', n); publish()


# ---- publish: what the page reads
def publish():
    try:
        os.makedirs(PUB, exist_ok=True)
        st = jload(S + '/ots_status.json', {}); caps = {}
        try:
            for l in open(S + '/wayback.jsonl'):
                r = json.loads(l); caps.setdefault(r.get('release'), []).append({'url': r['url'], 'capture': r['capture'], 'timestamp': r['timestamp']})
        except OSError: pass
        q = jload(S + '/wayback_queue.json', [])
        rows = []
        for r in releases()[::-1]:
            fp = S + '/' + r['file']
            for src in (fp, fp + '.ots'):
                if os.path.exists(src) and (not os.path.exists(PUB + '/' + os.path.basename(src)) or sha_file(src) != sha_file(PUB + '/' + os.path.basename(src))):
                    shutil.copy2(src, PUB + '/' + os.path.basename(src))
            rows.append({'id': r['id'], 'commit': r['commit'], 'released_at': r['released_at'], 'sha256': r['sha256'], 'manifest_sha256': r['manifest_sha256'],
                         'ledger_sha256': r['ledger_sha256'], 'files': r['files'], 'changed': r['changed'], 'json': '/receipts/stamps/' + r['file'],
                         'ots': ('/receipts/stamps/' + r['file'] + '.ots') if os.path.exists(fp + '.ots') else None, 'ots_status': st.get(r['id'], r.get('ots')),
                         'wayback': caps.get(r['id'], []), 'wayback_waiting': sum(1 for x in q if x.get('release') == r['id'])})
        idx = {'site': SITE, 'publisher': 'Heuremen LLC', 'built_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'releases': rows}
        old = jload(PUB + '/index.json', {})
        if {k: v for k, v in old.items() if k != 'built_utc'} != {k: v for k, v in idx.items() if k != 'built_utc'}:
            jdump(PUB + '/index.json', idx)
    except Exception as e: log('publish FAILED', e)


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    try:
        {'manifest': manifest, 'release': release, 'wayback': wayback, 'upgrade': upgrade, 'publish': publish}[mode]()
    except KeyError: print(__doc__); sys.exit(0)
    except Exception as e: log(mode, 'FAILED', repr(e)[:300])
    sys.exit(0)
