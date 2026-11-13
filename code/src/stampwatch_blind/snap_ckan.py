#!/usr/bin/env python3
"""snap_ckan.py (13 Nov 2026): stampwatch blind feed 2, COLLECT ONLY. A decoupled stamp: open.canada.ca CKAN metadata_modified (data.gov's CKAN API answered 404 on 13 Nov 2026, so the Canadian federal portal, same CKAN shape) and each
resource's last_modified, beside a sha256 of the resource bytes we fetch ourselves. The sample is fixed by rule: package_search for
datasets with a CSV resource, sorted by metadata_created ascending, first 1000; 50 drawn with random.Random(seed) where seed is the
public plan commit f570f1fa8fa2b631fbd0e068ff3fffdc09b44aa9. Resources over 20 MB are recorded as dropped (too_large, size from the resource metadata)."""
import json, gzip, hashlib, os, sys, time, random, urllib.request, datetime as dt
D = os.path.dirname(os.path.abspath(__file__)); UA = {'User-Agent': 'heuremen-stampwatch/1.0'}; SEED = 'f570f1fa8fa2b631fbd0e068ff3fffdc09b44aa9'
API = 'https://open.canada.ca/data/api/3/action/'; CAP = 20 * 1024 * 1024
def get(u, raw=False, cap=None):
    r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60)
    b = r.read(cap + 1) if cap else r.read()
    return b if raw else json.loads(b)
def freeze():
    res = get(API + 'package_search?fq=res_format:CSV&sort=metadata_created%20asc&rows=1000')['result']['results']
    pick = random.Random(SEED).sample([p['name'] for p in res], 50)
    json.dump({'frozen_at': dt.datetime.now(dt.timezone.utc).isoformat(), 'rule': __doc__.split('\n')[1:5], 'seed': SEED, 'datasets': pick},
              open(os.path.join(D, 'ckan_datasets.json'), 'w'), indent=0)
def snap():
    names = json.load(open(os.path.join(D, 'ckan_datasets.json')))['datasets']; out = {}; miss = []
    for n in names:
        try: p = get(API + 'package_show?id=' + n)['result']
        except Exception as e: miss.append([n, 'package', type(e).__name__]); continue
        rs = {}
        for r in p.get('resources', []):
            if (r.get('format') or '').upper() != 'CSV' or not r.get('url'): continue
            e = {'last_modified': r.get('last_modified'), 'metadata_modified': r.get('metadata_modified'), 'url': r['url']}
            try:
                b = get(r['url'], raw=True, cap=CAP)
                if len(b) > CAP: e['dropped'] = 'too_large'; e['size_metadata'] = r.get('size')   # v4: our choice not to fetch is dropped material (REQ-09), not NOTHING_RETURNED
                else:
                    e['sha256'] = hashlib.sha256(b).hexdigest(); e['bytes'] = len(b)
                    # v5 (Sage FIX 3): every fetched resource is stored by its own sha, so any pair can be diffed a-sha against b-sha
                    st = os.path.join(D, 'store'); os.makedirs(st, exist_ok=True)
                    fp = os.path.join(st, f"{r.get('id')}__{e['sha256'][:12]}.csv.gz")
                    if not os.path.exists(fp): open(fp, 'wb').write(gzip.compress(b))
            except Exception as x: e['nothing_returned'] = type(x).__name__
            rs[r.get('id')] = e; time.sleep(0.5)
        out[n] = {'metadata_modified': p.get('metadata_modified'), 'resources': rs}
    t = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    raw = json.dumps({'read_at': t, 'datasets': out, 'nothing_returned': miss}, sort_keys=True).encode()
    pth = os.path.join(D, 'snapshots_ckan', f'ckan_{t}.json.gz'); os.makedirs(os.path.dirname(pth), exist_ok=True); open(pth, 'wb').write(gzip.compress(raw))
    with open(os.path.join(D, 'manifest_ckan.jsonl'), 'a') as f: f.write(json.dumps({'file': os.path.basename(pth), 'read_at': t, 'sha256_raw': hashlib.sha256(raw).hexdigest(), 'n': len(out), 'nothing_returned': len(miss)}) + '\n')
def frame():   # v3: save the sample frame with its sha256 and check the draw repeats
    res = get(API + 'package_search?fq=res_format:CSV&sort=metadata_created%20asc&rows=1000')['result']['results']
    names = [p['name'] for p in res]; raw = json.dumps(names).encode()
    pick = random.Random(SEED).sample(names, 50); saved = json.load(open(os.path.join(D, 'ckan_datasets.json')))['datasets']
    json.dump({'saved_at': dt.datetime.now(dt.timezone.utc).isoformat(), 'frame': names, 'sha256': hashlib.sha256(raw).hexdigest(),
               'draw_repeats': pick == saved}, open(os.path.join(D, 'ckan_frame.json'), 'w'), indent=0)
    print('frame', len(names), hashlib.sha256(raw).hexdigest()[:16], 'draw repeats:', pick == saved)
if __name__ == '__main__':
    a = sys.argv[1:]
    freeze() if a == ['freeze'] else frame() if a == ['frame'] else snap()
