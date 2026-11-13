"""yf_meta_fetch.py -- authors and titles for the 288 fresh and 540 trained papers, read-only, from each paper's own record:
Zenodo API (zenodo DOIs), arXiv API (ax: ids, batched), Crossref (other DOIs). Cached in contam/meta_cache.json; reruns fetch only misses.
Inputs only; nothing here reads a model output."""
import json, os, re, sys, time, urllib.request, urllib.parse, xml.etree.ElementTree as ET
H = os.path.expanduser('~/bones-forge/yo/read/fresh'); C = H + '/contam/meta_cache.json'
src = open(H + '/yf_primary.py').read().split('\n'); exec('\n'.join(src[5:14]).replace('__file__', repr(H + '/yf_primary.py')))
fresh = {json.loads(l)['paper'] for l in open(H + '/data/test_items_fresh.jsonl')}
trained = {k for k in USED if yd.split(k) in ('TRAIN', 'VALID')}; testsplit = {k for k in USED if yd.split(k) == 'TEST'}
cache = json.load(open(C)) if os.path.exists(C) else {}
UA = {'User-Agent': 'Heuremen-LLC-research/1.0 (mailto:heuremen@heuremen.com)'}
def get(url, tries=7):
    for t in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r: return r.read()
        except Exception as e:
            if t == tries - 1: raise
            time.sleep(30 * (t + 1))
def save(): json.dump(cache, open(C, 'w'), indent=0)
todo = sorted((fresh | trained | testsplit) - set(cache))
print(f'{len(todo)} to fetch ({len(cache)} cached)', flush=True)
for k in [k for k in todo if k.startswith('doi:')]:
    doi = k[4:]
    try:
        if 'zenodo.' in doi:
            d = json.loads(get('https://zenodo.org/api/records/' + doi.rsplit('zenodo.', 1)[1])); m = d.get('metadata', {})
            cache[k] = dict(title=m.get('title'), authors=[c.get('name') for c in m.get('creators', [])], src='zenodo')
        else:
            m = json.loads(get('https://api.crossref.org/works/' + urllib.parse.quote(doi)))['message']
            cache[k] = dict(title=(m.get('title') or [None])[0], authors=[' '.join(filter(None, (a.get('given'), a.get('family')))) or a.get('name') for a in m.get('author', [])], src='crossref')
    except Exception as e: cache[k] = dict(title=None, authors=[], src=f'error:{type(e).__name__}')
    save(); time.sleep(0.8)
ax = [k for k in todo if k.startswith('ax:')]
for i in range(0, len(ax), 20):
    ids = [k[3:] for k in ax[i:i + 20]]
    try: x = ET.fromstring(get('http://export.arxiv.org/api/query?' + urllib.parse.urlencode({'id_list': ','.join(ids), 'max_results': 30})))
    except Exception as e: print(f'arxiv batch {i} failed ({e}); left for a rerun', flush=True); time.sleep(60); continue
    ns = {'a': 'http://www.w3.org/2005/Atom'}
    got = {}
    for e in x.findall('a:entry', ns):
        aid = re.sub(r'v\d+$', '', e.find('a:id', ns).text.rsplit('/abs/', 1)[-1])
        got[aid] = dict(title=' '.join(e.find('a:title', ns).text.split()), authors=[a.find('a:name', ns).text for a in e.findall('a:author', ns)], src='arxiv')
    for k in ax[i:i + 20]: cache[k] = got.get(k[3:], dict(title=None, authors=[], src='arxiv:missing'))
    save(); print(f'arxiv {i + len(ids)}/{len(ax)}', flush=True); time.sleep(20)
print('done', len(cache), 'missing authors:', sum(1 for k in fresh | trained | testsplit if not cache.get(k, {}).get('authors')), flush=True)
