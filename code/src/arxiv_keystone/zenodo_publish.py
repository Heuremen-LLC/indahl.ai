"""zenodo_publish.py -- publishes the reserved Zenodo draft for 'A Readout's Kick Is a Turn' (DOI 10.5281/zenodo.23843468): sets the license
to CC BY 4.0 (as the earlier record), uploads the two zips in zenodo/, publishes, and prints the DOI and record URL. Token read from the
accounts folder inside this script, never printed. Run once, at the arXiv submission (his word, 31 Oct)."""
import json, os, urllib.request
H = os.path.dirname(os.path.abspath(__file__)); TOK = open(os.path.expanduser('~/Documents/Heuremen LLC/ACCOUNTS/zenodo-token')).read().strip()
RID = json.load(open(f'{H}/ZENODO_DRAFT.json'))['id']; API = f'https://zenodo.org/api/deposit/depositions/{RID}'
def call(url, method='GET', data=None, ctype='application/json'):
    req = urllib.request.Request(url, method=method, data=data, headers={'Authorization': 'Bearer ' + TOK, **({'Content-Type': ctype} if data is not None else {})})
    return json.load(urllib.request.urlopen(req, timeout=600))
d = call(API); assert d['state'] == 'unsubmitted', d['state']
m = d['metadata']; m['license'] = 'cc-by-4.0'
call(API, 'PUT', json.dumps({'metadata': m}).encode())
bucket = d['links']['bucket']
for fn in sorted(os.listdir(f'{H}/zenodo')):
    if fn.endswith('.zip'):
        call(f'{bucket}/{fn}', 'PUT', open(f'{H}/zenodo/{fn}', 'rb').read(), 'application/octet-stream'); print('uploaded', fn)
p = call(f'{API}/actions/publish', 'POST', b'')
print('published', p.get('state'), p['metadata'].get('doi') or p.get('doi'), p['links'].get('record_html') or p['links'].get('html'))
