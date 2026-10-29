#!/usr/bin/env python3
"""zenodo_newversion.py: publishes a new version of each Zenodo record made on 29 Oct 2026 from the current public repositories, so every record keeps one concept DOI.
Per record: New version, remove the files the draft copied from the old version, upload the new snapshot zip, set the version and date, publish.
--test creates each draft, checks it, and deletes it without publishing. Token read from the private file, never printed."""
import os, sys, json, subprocess, urllib.request, urllib.error, datetime as D
H = os.path.dirname(os.path.abspath(__file__)); TOK = open(os.path.expanduser('~/Documents/Heuremen LLC/ACCOUNTS/zenodo-token')).read().strip(); API = 'https://zenodo.org/api'
recs = dict((s, i) for s, i, d in json.load(open(os.path.join(H, 'zenodo', 'records.json'))))
today = D.date.today().isoformat(); R = os.path.expanduser('~/bones-forge/public_mirror'); TEST = '--test' in sys.argv
def call(method, url, data=None, ctype='application/json', raw=False):
    req = urllib.request.Request(url if url.startswith('http') else API + url, data=data, method=method, headers={'Authorization': 'Bearer ' + TOK, 'Content-Type': ctype})
    r = urllib.request.urlopen(req, timeout=1800); b = r.read(); return json.loads(b) if b and not raw else b
for slug, rid in recs.items():
    name = '%s-v%s.zip' % (slug, today.replace('-', '.')); zp = os.path.join(H, 'zenodo', name)
    if slug in ('indahl.ai', 'heuremen.org'): subprocess.run(['git', '-C', '%s/%s' % (R, slug), 'archive', '--format=zip', '--prefix=%s-%s/' % (slug, today), '-o', zp, 'HEAD'], check=True)
    else:
        subprocess.run(['rm', '-rf', '/tmp/zn_' + slug]); subprocess.run(['/opt/homebrew/bin/gh', 'repo', 'clone', 'Heuremen-LLC/' + slug, '/tmp/zn_' + slug, '--', '-q'], check=True)
        subprocess.run(['git', '-C', '/tmp/zn_' + slug, 'archive', '--format=zip', '--prefix=%s-%s/' % (slug, today), '-o', zp, 'HEAD'], check=True)
    d = call('POST', '/deposit/depositions/%d/actions/newversion' % rid); draft = int(d['links']['latest_draft'].rstrip('/').split('/')[-1]); dep = call('GET', '/deposit/depositions/%d' % draft)
    for f in dep.get('files', []): call('DELETE', '/deposit/depositions/%d/files/%s' % (draft, f['id']), raw=True)
    md = dep['metadata']; md['version'] = today; md['publication_date'] = today; md.pop('doi', None); md.pop('prereserve_doi', None)
    if TEST:
        print(slug, 'draft', draft, 'ready, zip', os.path.getsize(zp), 'bytes, files removed from draft'); call('DELETE', '/deposit/depositions/%d' % draft, raw=True); continue
    with open(zp, 'rb') as f: call('PUT', dep['links']['bucket'] + '/' + name, f.read(), 'application/octet-stream', raw=True)
    call('PUT', '/deposit/depositions/%d' % draft, json.dumps({'metadata': md}).encode()); pub = call('POST', '/deposit/depositions/%d/actions/publish' % draft); print('published', slug, pub['id'], pub['doi'], flush=True)
