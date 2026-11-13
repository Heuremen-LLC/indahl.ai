#!/usr/bin/env python3
"""zen_20261110.py: Zenodo records for the Heuremen LLC packs, 10 Nov 2026. Token read from the private file, never printed.
  drafts    create the drafts named in zenodo_packs_PLAN.json (new version for an existing concept, new deposition otherwise), no files,
            and write their ids and concept DOIs to zenodo_packs/drafts_20261110.json
  publish   for each draft: remove carried files, upload the listed files after checking each sha256 against the live site, set the
            metadata from the plan, publish, check the md5 Zenodo stores against the local file, write zenodo_packs/dois.json and ledger/zenodo_dois.json
"""
import hashlib, json, os, sys, urllib.request, urllib.error
B = '/Users/heuremen/bones-forge'; API = 'https://zenodo.org/api'
TOK = open('/Users/heuremen/Documents/Heuremen LLC/ACCOUNTS/zenodo-token').read().strip()
PLAN = B + '/ledger/zenodo_packs_PLAN.json'; DR = B + '/zenodo_packs/drafts_20261110.json'
def call(method, url, data=None, raw=None):
    h = {'Authorization': 'Bearer ' + TOK}; body = None
    if data is not None: body = json.dumps(data).encode(); h['Content-Type'] = 'application/json'
    if raw is not None: body = raw; h['Content-Type'] = 'application/octet-stream'
    try: b = urllib.request.urlopen(urllib.request.Request(url if url.startswith('http') else API + url, data=body, headers=h, method=method), timeout=1800).read()
    except urllib.error.HTTPError as e: raise RuntimeError(f'{method} {url.split("?")[0]} -> {e.code} {e.read()[:800]!r}')
    return json.loads(b) if b else {}
def live_sha(u):
    return urllib.request.urlopen(urllib.request.Request(u + '.sha256', headers={'User-Agent': 'curl/8'}), timeout=60).read().decode().split()[0]
plan = json.load(open(PLAN)); drafts = json.load(open(DR)) if os.path.exists(DR) else {}
cmd = sys.argv[1]
if cmd == 'drafts':
    for r in plan['records']:
        k = r['key']
        if k in drafts: print('have', k, drafts[k]); continue
        if r.get('parent_record'):
            p = call('POST', f"/deposit/depositions/{r['parent_record']}/actions/newversion")
            did = int(p['links']['latest_draft'].rstrip('/').split('/')[-1]); dep = call('GET', f'/deposit/depositions/{did}')
            for f in dep.get('files', []): call('DELETE', f"/deposit/depositions/{did}/files/{f['id']}")
        else:
            dep = call('POST', '/deposit/depositions', {'metadata': {'prereserve_doi': True}}); did = dep['id']
        dep = call('GET', f'/deposit/depositions/{did}')
        crid = dep.get('conceptrecid'); vdoi = (dep['metadata'].get('prereserve_doi') or {}).get('doi')
        drafts[k] = {'draft': did, 'concept_doi': f'10.5281/zenodo.{crid}', 'version_doi': vdoi, 'files_left': len(dep.get('files', []))}
        json.dump(drafts, open(DR, 'w'), indent=1); print('draft', k, drafts[k])
elif cmd == 'publish':
    only = sys.argv[2:]
    out = json.load(open(B + '/zenodo_packs/dois.json'))
    for r in plan['records']:
        k = r['key']
        if only and k not in only: continue
        d = drafts[k]; did = d['draft']; dep = call('GET', f'/deposit/depositions/{did}')
        if dep['state'] == 'done' or dep.get('submitted'): print('already published', k); continue
        for f in dep.get('files', []): call('DELETE', f"/deposit/depositions/{did}/files/{f['id']}")
        md5s = {}
        for f in r['files']:
            b = open(B + '/' + f['local'], 'rb').read(); s = hashlib.sha256(b).hexdigest()
            assert s == f['sha256'], f'local sha changed since the plan: {f["local"]}'
            if f.get('live'): assert live_sha(f['live']) == s, f'live sha differs: {f["live"]}'
            call('PUT', dep['links']['bucket'] + '/' + f['name'], raw=b); md5s[f['name']] = hashlib.md5(b).hexdigest()
        md = dict(r['metadata']); md['prereserve_doi'] = True
        call('PUT', f'/deposit/depositions/{did}', {'metadata': md})
        pub = call('POST', f'/deposit/depositions/{did}/actions/publish')
        got = {f['filename']: f['checksum'] for f in call('GET', f'/deposit/depositions/{did}/files')}
        ok = all(got.get(n) == m for n, m in md5s.items()) and len(got) == len(md5s)
        main = r['files'][0]
        out[k] = {'doi': pub['doi'], 'concept_doi': pub.get('conceptdoi') or d['concept_doi'], 'url': pub['links']['record_html'], 'zip_sha256': main['sha256'],
                  'zenodo_md5': got.get(main['name']), 'md5_match': ok, 'version': md['version'], 'deposition_id': did, 'files': len(md5s)}
        json.dump(out, open(B + '/zenodo_packs/dois.json', 'w'), indent=1); print('PUBLISHED', k, pub['doi'], 'concept', out[k]['concept_doi'], 'md5 ok' if ok else 'MD5 MISMATCH')
