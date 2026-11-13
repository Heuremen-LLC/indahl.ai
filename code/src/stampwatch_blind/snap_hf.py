#!/usr/bin/env python3
"""snap_hf.py (13 Nov 2026): stampwatch blind feed, COLLECT ONLY. Per pass, for the fixed model list in models.json (the 200 most
downloaded Hugging Face models as listed at list-freeze time), saves the API's lastModified, sha and every file's blob id into one
gzip snapshot with its read time and sha256. Nothing here reads the snapshots for the fault; stampwatch does that only after its code
and plan are referee'd (plans/stampwatch/PLAN.md in Heuremen-LLC/claude-plugins)."""
import json, gzip, hashlib, os, sys, time, urllib.request, datetime as dt
D = os.path.dirname(os.path.abspath(__file__)); UA = {'User-Agent': 'heuremen-stampwatch/1.0'}
def get(u):
    return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read())
def freeze():
    L = get('https://huggingface.co/api/models?sort=downloads&direction=-1&limit=200')
    json.dump({'frozen_at': dt.datetime.now(dt.timezone.utc).isoformat(), 'source': 'huggingface.co/api/models?sort=downloads&limit=200',
               'models': [m['id'] for m in L]}, open(os.path.join(D, 'models.json'), 'w'), indent=0)
def snap():
    ids = json.load(open(os.path.join(D, 'models.json')))['models']; out = {}; miss = []
    for i in ids:
        try:
            m = get(f'https://huggingface.co/api/models/{i}?blobs=true')
            out[i] = {'lastModified': m.get('lastModified'), 'sha': m.get('sha'),
                      'files': {s['rfilename']: s.get('blobId') for s in m.get('siblings', [])}}
        except Exception as e: miss.append([i, type(e).__name__])
        time.sleep(0.3)
    t = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    raw = json.dumps({'read_at': t, 'models': out, 'nothing_returned': miss}, sort_keys=True).encode()
    p = os.path.join(D, 'snapshots', f'hf_{t}.json.gz'); open(p, 'wb').write(gzip.compress(raw))
    with open(os.path.join(D, 'manifest.jsonl'), 'a') as f: f.write(json.dumps({'file': os.path.basename(p), 'read_at': t, 'sha256_raw': hashlib.sha256(raw).hexdigest(), 'n': len(out), 'nothing_returned': len(miss)}) + '\n')
if __name__ == '__main__':
    if sys.argv[1:] == ['freeze']: freeze()
    else: snap()
