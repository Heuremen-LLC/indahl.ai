#!/usr/bin/env python3
"""zenodo_release.py: prepares a Zenodo record from a folder of files. The token comes from the ZENODO_TOKEN environment variable for one run and is never written anywhere.
  draft   --title T --description-file F --files A B ... [--license ID] [--type dataset|software] [--keywords k1,k2] [--version V]   creates a private draft and uploads the files, prints the draft link
  publish ID --yes-publish                                                                                                           mints the DOI. Permanent. Only on his word for that release.
  status  ID
Creators match the physics record: Indahl, Wayfinder and Bones, both Heuremen LLC."""
import os, sys, json, argparse, urllib.request, urllib.error
API = 'https://zenodo.org/api'; TOK = os.environ.get('ZENODO_TOKEN', '')
def call(method, url, data=None, raw=None, ctype='application/json'):
    h = {'Authorization': 'Bearer ' + TOK}
    body = raw if raw is not None else (json.dumps(data).encode() if data is not None else None)
    if body is not None: h['Content-Type'] = ctype
    try: return json.load(urllib.request.urlopen(urllib.request.Request(url, data=body, method=method, headers=h), timeout=600))
    except urllib.error.HTTPError as e:
        print('HTTP', e.code, e.read()[:600].decode('utf8', 'ignore'), file=sys.stderr); sys.exit(1)
ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest='cmd')
d = sub.add_parser('draft'); d.add_argument('--title', required=True); d.add_argument('--description-file', required=True); d.add_argument('--files', nargs='+', required=True)
d.add_argument('--license', default='cc-by-4.0'); d.add_argument('--type', default='dataset'); d.add_argument('--keywords', default=''); d.add_argument('--version', default='1.0.0'); d.add_argument('--related', default='https://indahl.ai')
p = sub.add_parser('publish'); p.add_argument('id'); p.add_argument('--yes-publish', action='store_true')
s = sub.add_parser('status'); s.add_argument('id')
a = ap.parse_args()
if not TOK: sys.exit('ZENODO_TOKEN is not set')
if a.cmd == 'draft':
    dep = call('POST', API + '/deposit/depositions', {})
    for f in a.files:
        call('PUT', dep['links']['bucket'] + '/' + os.path.basename(f), raw=open(f, 'rb').read(), ctype='application/octet-stream'); print('uploaded', os.path.basename(f))
    md = dict(title=a.title, upload_type=a.type, description=open(a.description_file).read(), creators=[{'name': 'Indahl, Wayfinder', 'affiliation': 'Heuremen LLC'}, {'name': 'Bones', 'affiliation': 'Heuremen LLC'}],
              access_right='open', license=a.license, version=a.version, language='eng', keywords=[k for k in a.keywords.split(',') if k],
              related_identifiers=[{'identifier': a.related, 'relation': 'isDocumentedBy', 'resource_type': 'other', 'scheme': 'url'}])
    call('PUT', API + '/deposit/depositions/%d' % dep['id'], {'metadata': md})
    print('DRAFT', dep['id'], 'https://zenodo.org/deposit/%d' % dep['id'], '(private, not published)')
elif a.cmd == 'publish':
    if not a.yes_publish: sys.exit('refusing: publishing mints a permanent DOI. Pass --yes-publish on his word for this release.')
    r = call('POST', API + '/deposit/depositions/%s/actions/publish' % a.id); print('PUBLISHED', r.get('doi'), r.get('links', {}).get('html'))
elif a.cmd == 'status':
    r = call('GET', API + '/deposit/depositions/%s' % a.id); print(r['id'], r['state'], r.get('doi'), r['metadata'].get('title'), [f['filename'] for f in r.get('files', [])])
