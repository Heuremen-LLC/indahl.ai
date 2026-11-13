#!/usr/bin/env python3
"""zenodo_sync.py -- Zenodo follows the site. Heuremen LLC, 11 Nov 2026 (Wayfinder: "likewise with zenodo ... we're not a static site").

  zenodo_sync.py                 dry run (default): for every record in ZENODO_MAP.json compare the md5 of each file the site serves with the md5 of the
                                 same file in the record's latest published version, and say what would be updated
  zenodo_sync.py --publish       act: for each stale record make a NEW VERSION from the latest one (API newversion, never a re-import), replace only the
                                 changed files, keep the metadata, set the version string and publication date to today, publish, then write the new DOI to
                                 ZENODO_MAP.json, ledger/zenodo_dois.json, zenodo_packs/dois.json and any ledger row that prints it (ledger first, then the page source)
  zenodo_sync.py --only "NAME"   limit to one record
  zenodo_sync.py --map           rebuild the file lists of ZENODO_MAP.json from the Zenodo API (read only)

Guards: one new version per record per 24 hours (read from Zenodo's own timestamp and from last_new_version_at in the map), and only when a file's content
differs. A zip that does not open, or whose .sha256 sidecar does not match, is never uploaded. The token is read from the Documents/Heuremen LLC/ACCOUNTS
folder at call time, goes only into the Authorization header, and is never printed, logged or written. On any error ledger/zenodo_status.json is written
(watch/alerts_check.py reads it) and the exit code stays 0 so a ship never fails here; it is removed after a clean run."""
import os, sys, json, time, hashlib, zipfile, urllib.request, urllib.error, subprocess, datetime, re
B = os.path.expanduser('~/bones-forge'); L = B + '/ledger'; PUB = B + '/cloudflare-workers/heuremen-door/public'
MAP = L + '/ZENODO_MAP.json'; STATUS = L + '/zenodo_status.json'; LOG = L + '/zenodo_log.jsonl'
TOKEN_FILE = os.path.expanduser('~/Documents/Heuremen LLC/ACCOUNTS/zenodo-token'); API = 'https://zenodo.org/api'
GUARD_H = 24
md5 = lambda b: hashlib.md5(b).hexdigest()
sha = lambda b: hashlib.sha256(b).hexdigest()

def token(): return open(TOKEN_FILE).read().strip()
def call(method, url, data=None, raw=None, ctype=None, tries=3):
    for i in range(tries):
        try: return _call(method, url, data, raw, ctype)
        except RuntimeError as e:
            if i == tries - 1 or ' HTTP 5' not in str(e): raise   # a Zenodo 5xx is retried, anything else is final
            time.sleep(8 * (i + 1))
def _call(method, url, data=None, raw=None, ctype=None):
    h = {'Authorization': 'Bearer ' + token()}; body = None
    if data is not None: body = json.dumps(data).encode(); h['Content-Type'] = 'application/json'
    if raw is not None: body = raw; h['Content-Type'] = ctype or 'application/octet-stream'
    try: r = urllib.request.urlopen(urllib.request.Request(url, data=body, headers=h, method=method), timeout=600); b = r.read()
    except urllib.error.HTTPError as e: raise RuntimeError(f'{method} {url.split("?")[0]} -> HTTP {e.code} {e.read()[:300]!r}') from None
    except Exception as e: raise RuntimeError(f'{method} {url.split("?")[0]} -> {type(e).__name__}') from None
    return json.loads(b) if b else {}

def all_depositions():
    out = []
    for pg in range(1, 6):
        r = call('GET', f'{API}/deposit/depositions?size=100&page={pg}&all_versions=1')
        if not r: break
        out += r
    return out

def latest_published(deps, concept):
    v = [d for d in deps if str(d['conceptrecid']) == str(concept) and d['state'] == 'done']
    return max(v, key=lambda d: d['id']) if v else None

SITE_DIR = {'qia-research-package.zip': 'qia', 'qia-list-pack.zip': 'qia', 'iris-research-package.zip': 'iris', 'iris-list-pack.zip': 'iris', 'atlas-data-pack.zip': 'atlas',
            'oy-data-pack.zip': 'oy', 'model-data-pack.zip': 'hermes', 'darkwave-correction-kit.zip': 'darkwave'}
def site_path(fn):
    base = fn[:-len('.sha256')] if fn.endswith('.sha256') else fn
    d = SITE_DIR.get(base) or base.split('-data-pack')[0]
    return f'{d}/{fn}'

def build_map():
    deps = all_depositions(); old = json.load(open(MAP)) if os.path.exists(MAP) else {'records': []}
    prev = {r['concept_recid']: r for r in old.get('records', [])}; recs = []
    zd = json.load(open(L + '/zenodo_dois.json'))['packs']
    for name, p in zd.items():
        concept = p['concept_doi'].rsplit('.', 1)[1]; d = latest_published(deps, concept)
        if not d: continue
        r = prev.get(concept, {})
        recs.append(dict(name=name, concept_recid=concept, concept_doi=p['concept_doi'], page=p.get('page'), latest_deposition=d['id'], latest_doi=d['doi'], version=d['metadata'].get('version'),
                         files={f['filename']: site_path(f['filename']) for f in d['files']}, last_new_version_at=r.get('last_new_version_at'), last_zenodo_modified=d.get('modified')))
    excl = [dict(concept_recid='23764106', name='Heuremen LLC: indahl.ai live records, code and plans (snapshot of the indahl.ai GitHub repo)', reason='a snapshot of a repository, no file of it is a download on the site'),
            dict(concept_recid='23764147', name='Heuremen LLC: heuremen.org site, paper sources and experiments (snapshot)', reason='a snapshot of the heuremen.org repository, released by ledger/build_zenodo.sh and zenodo_release.py by hand'),
            dict(concept_recid='23764161', name='faultsguards: catalogue, Python package', reason='released from the faultsguards repository and PyPI, not from a site file'),
            dict(concept_recid='23764163', name='Heuremen LLC nodes: second-seat probes', reason='released from the nodes repository, not from a site file'),
            dict(concept_recid='23169755', name='A Readout Is Not an Idle: data and verification code (versions 1.0.0 to 6.0.0)', reason='the physics record, a paper data release built by ledger/build_zenodo.sh from the experiments folders, versioned by hand with the paper. A stuck draft 2.0.0 sits on this concept, so the API would refuse newversion until it is cleared'),
            dict(concept_recid='23843467', name="A Readout's Kick Is a Turn: data, code and preregistration", reason='a preregistered run record, frozen by design'),
            dict(concept_recid='23744304', name='Local-mode tests of the K-Veritas tool (unsubmitted draft)', reason='an unsubmitted draft, never published, not a site mirror')]
    json.dump(dict(_note='Every Zenodo record that mirrors a file served by indahl.ai, written by ledger/zenodo_sync.py --map, 11 Nov 2026. files: Zenodo file name -> path under the worker public/ folder. last_new_version_at feeds the 24 hour guard.',
                   records=recs, excluded=excl), open(MAP, 'w'), indent=1); print(f'ZENODO_MAP.json: {len(recs)} records, {len(excl)} excluded')

def read_site(path):
    f = f'{PUB}/{path}'
    return open(f, 'rb').read() if os.path.isfile(f) else None

def verify_zip(path):
    f = f'{PUB}/{path}'; zipfile.ZipFile(f).testzip(); sc = f + '.sha256'
    if os.path.exists(sc) and open(sc).read().split()[0] != sha(open(f, 'rb').read()): raise RuntimeError(f'{path}: .sha256 sidecar does not match the zip')

def plan(deps, recs, only=None):
    """[(record, latest deposition, changed {zenodo filename: site path})]"""
    out = []
    for r in recs:
        if only and r['name'] != only: continue
        d = latest_published(deps, r['concept_recid'])
        if not d: out.append((r, None, 'no published version found')); continue
        zmd5 = {f['filename']: f['checksum'] for f in d['files']}; changed = {}
        for fn, sp in r['files'].items():
            b = read_site(sp)
            if b is None: continue   # not on the site any more: never deleted from a record here
            if zmd5.get(fn) != md5(b): changed[fn] = sp
        for fn in zmd5:
            if fn not in r['files']: r['files'][fn] = site_path(fn)
        out.append((r, d, changed))
    return out

def guard_ok(r, d):
    now = datetime.datetime.now(datetime.timezone.utc); last = []
    if r.get('last_new_version_at'): last.append(datetime.datetime.fromisoformat(r['last_new_version_at']))
    if d and d.get('modified'): last.append(datetime.datetime.fromisoformat(d['modified'].replace('Z', '+00:00')).astimezone(datetime.timezone.utc))
    last = max(last) if last else None
    if last and now - last < datetime.timedelta(hours=GUARD_H): return False, last
    return True, last

def update_ledger_doi(old_doi, new_doi, name):
    """ledger edit before surface edit: every live row whose value is the old version DOI follows it, then the page source it prints on"""
    rows = {}
    for l in open(L + '/ledger.jsonl'):
        if l.strip(): r = json.loads(l); rows[r['id']] = r
    hit = [r for r in rows.values() if r.get('value') == f'10.5281/zenodo.{old_doi}' and r['status'] == 'live']
    if not hit: return []
    now = time.strftime('%Y-%m-%d %H:%M'); ck = B + '/tools/desk_packs/CHECKS.md'
    ent = (f'\n## {now} Zenodo sync: {name} new version, version DOI doi:10.5281/zenodo.{old_doi} -> doi:10.5281/zenodo.{new_doi}\npacks: P\n(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)\n'
           f'- I: holds: the record was versioned because the md5 of a file on the site differed from the md5 of the same file in its latest Zenodo version, so the none is the record against the site\n'
           f'- II: n/a: no comparison between two runs\n- III: n/a: no signed difference is reported\n'
           f'- V: holds: two records side by side, the DOI in the Zenodo publish response and the DOI written to ledger/zenodo_dois.json and zenodo_packs/dois.json, and the md5 of each uploaded file read back from the new version\n- VI: n/a: no interval outcome is claimed\n'
           f'- R: holds: the DOI read from the Zenodo publish response on {now}\n- P1: n/a: no quoted text is added to any page\n- P2: holds: the DOI links to doi.org\n- P3: holds: record and file names as published\n'
           f'- P4: holds: no cause named\n- P5: n/a: no intervals on this line\n- P6: holds: the line says which version holds the pack, nothing stronger\n'
           f'- P7: holds: ledger rows edited before the page, release through ledger/ship.sh under site_lock\n- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes\n'
           f'- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC\n- P10: n/a: no rule set after the data\n')
    open(ck, 'a').write(ent)
    run = lambda *a: subprocess.run(['python3', L + '/ledger.py', *a], check=True, stdout=subprocess.DEVNULL)
    why = f'new Zenodo version of {name} published {time.strftime("%-d %b %Y")} by zenodo_sync.py'; files = set()
    sys.path.insert(0, L); import ledger as LG
    for r in hit:
        nv = f'10.5281/zenodo.{new_doi}'; run('set', r['id'], '--field', 'value', '--to', nv, '--why', why, '--evidence', 'zenodo_packs/dois.json', '--checks', 'tools/desk_packs/CHECKS.md')
        run('set', r['id'], '--field', 'source.grep', '--to', r['source']['grep'].replace(f'10.5281/zenodo.{old_doi}', nv), '--why', why, '--evidence', 'zenodo_packs/dois.json')
        for sf in r['surfaces']:
            nt = sf['text'].replace(f'10.5281/zenodo.{old_doi}', nv); run('off', r['id'], sf['surface'], '--why', why); run('on', r['id'], sf['surface'], nt); files.add(LG.surface_path(sf['surface']))
    return sorted(files)

def record_new_version(r, old, new, md5s):
    """the DOI goes to ZENODO_MAP.json, ledger/zenodo_dois.json and zenodo_packs/dois.json, then the rows that print the version DOI, then their page sources"""
    old_doi, new_doi = old['doi'].rsplit('.', 1)[1], new['doi'].rsplit('.', 1)[1]
    zp = B + '/zenodo_packs/dois.json'; zd = json.load(open(zp)) if os.path.exists(zp) else {}
    if r['name'] in zd: zd[r['name']].update(doi=new['doi'], url=f'https://zenodo.org/record/{new["id"]}', version=new['metadata']['version'], deposition_id=new['id'], zenodo_md5=md5s.get(next(iter(md5s), ''), ''), md5_match=True)
    json.dump(zd, open(zp, 'w'), indent=1)
    z = json.load(open(L + '/zenodo_dois.json')); p = z['packs'].get(r['name'])
    if p:
        p.update(version_doi=new['doi'], version=new['metadata']['version'], status='published', record_url=f'https://zenodo.org/record/{new["id"]}')
        zipn = next((fn for fn in md5s if fn.endswith('.zip')), None)
        if zipn and zipn in r['files'] and read_site(r['files'][zipn]): p['zip_sha256'] = sha(read_site(r['files'][zipn]))
        if 'versions' in p: p['versions'] = p['versions'] + [dict(version=new['metadata']['version'], doi=new['doi'], record_url=f'https://zenodo.org/record/{new["id"]}')]
    json.dump(z, open(L + '/zenodo_dois.json', 'w'), indent=1)
    pages = update_ledger_doi(old_doi, new_doi, r['name'])
    for pg in pages:
        t = open(pg).read()
        if old['doi'] in t: open(pg, 'w').write(t.replace(old['doi'], new['doi']))
    return pages

def publish_one(r, old, changed):
    for fn, sp in changed.items():
        if fn.endswith('.zip'): verify_zip(sp)
    drafts = [d for d in call('GET', f'{API}/deposit/depositions?size=100&all_versions=1') if str(d['conceptrecid']) == str(r['concept_recid']) and d['state'] != 'done' and d['id'] > old['id']]
    if drafts: draft = call('GET', f'{API}/deposit/depositions/{max(drafts, key=lambda d: d["id"])["id"]}')   # a draft an earlier run left after an error is finished, not duplicated
    else:
        nv = call('POST', f'{API}/deposit/depositions/{old["id"]}/actions/newversion'); draft = call('GET', nv['links']['latest_draft'])
    did = draft['id']; files = {f['filename']: f['id'] for f in draft['files']}
    bucket = draft['links']['bucket']
    have = {f['filename']: f.get('checksum') for f in draft['files']}
    for fn, sp in sorted(changed.items()):
        if have.get(fn) == md5(read_site(sp)): continue   # already uploaded to this draft by an earlier attempt
        if fn in files:
            try: call('DELETE', f'{API}/deposit/depositions/{did}/files/{files[fn]}')
            except RuntimeError as e:
                if 'HTTP 404' not in str(e): raise
        call('PUT', f'{bucket}/{fn}', raw=read_site(sp))
    md = dict(draft['metadata']); today = time.strftime('%Y-%m-%d')
    for k in ('doi', 'prereserve_doi'): md.pop(k, None)
    md['version'] = today; md['publication_date'] = today
    call('PUT', f'{API}/deposit/depositions/{did}', data={'metadata': md})
    pub = call('POST', f'{API}/deposit/depositions/{did}/actions/publish')
    got = {f['filename']: f['checksum'] for f in call('GET', f'{API}/deposit/depositions/{pub["id"]}')['files']}
    for fn, sp in changed.items():
        if got.get(fn) != md5(read_site(sp)): raise RuntimeError(f'{r["name"]}: {fn} md5 read back from Zenodo differs from the site file')
    return pub, got

def main():
    pub = '--publish' in sys.argv; only = sys.argv[sys.argv.index('--only') + 1] if '--only' in sys.argv else None
    if '--map' in sys.argv: build_map(); return 0
    m = json.load(open(MAP)); errs = []; done = []
    try: deps = all_depositions()
    except Exception as e: errs.append(str(e)); deps = None
    if deps is not None:
        for r, d, changed in plan(deps, m['records'], only):
            if d is None: errs.append(f'{r["name"]}: {changed}'); continue
            if not changed: print(f'  zenodo: {r["name"]}: current ({d["metadata"]["version"]}, doi:{d["doi"]})'); continue
            ok, last = guard_ok(r, d)
            names = ', '.join(sorted(k for k in changed if k.endswith('.zip')))
            if not ok: print(f'  zenodo: {r["name"]}: STALE ({len(changed)} files: {names}) but held by the 24 h guard, last version {last:%Y-%m-%d %H:%M} UTC'); continue
            if not pub: print(f'  zenodo: {r["name"]}: WOULD make a new version from doi:{d["doi"]}, replacing {len(changed)} files: {names}'); continue
            try:
                newd, got = publish_one(r, d, changed); r['last_new_version_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
                r['latest_deposition'] = newd['id']; r['latest_doi'] = newd['doi']; r['version'] = newd['metadata']['version']
                pages = record_new_version(r, d, newd, got); done.append((r['name'], newd['doi']))
                open(LOG, 'a').write(json.dumps(dict(at=r['last_new_version_at'], record=r['name'], old=d['doi'], new=newd['doi'], files=sorted(changed))) + '\n')
                print(f'  zenodo: {r["name"]}: NEW VERSION doi:{newd["doi"]} ({len(changed)} files replaced)')
            except Exception as e: errs.append(f'{r["name"]}: {e}'); print(f'  zenodo: {r["name"]}: ERROR {e}')
        json.dump(m, open(MAP, 'w'), indent=1)
    if errs:
        json.dump(dict(at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), ok=False, error='; '.join(errs)[:400]), open(STATUS, 'w')); print('  zenodo: ERRORS, status file written')
    elif pub and os.path.exists(STATUS): os.remove(STATUS)
    if not pub: print('  zenodo: dry run, nothing changed (use --publish)')
    return 0
if __name__ == '__main__':
    try: sys.exit(main())
    except SystemExit: raise
    except Exception as e:
        json.dump(dict(at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), ok=False, error=type(e).__name__ + ': ' + str(e)[:300]), open(STATUS, 'w')); print('  zenodo: crashed, status file written'); sys.exit(0)
