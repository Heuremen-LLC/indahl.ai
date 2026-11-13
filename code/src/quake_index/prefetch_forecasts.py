#!/usr/bin/env python3
"""prefetch_forecasts.py: one-time bulk read of every archived oaf forecast.json named in data/raw/detail (stated side only, no catalog).
Four connections at most, each pausing 0.25 s between requests. Files are immutable product versions, kept in data/raw/forecast. quake_tick.py
reads the same files and fetches any new version itself, one request at a time."""
import os, json, glob, time, threading, queue, urllib.request, sys
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H)
UA = 'heuremen-quake/0.1 (+https://indahl.ai/quake)'
q = queue.Queue(); done = [0]; fail = []
for f in sorted(glob.glob('data/raw/detail/*.json')):
    d = json.load(open(f))
    for v in d['properties']['products'].get('oaf', []):
        co = v.get('contents')
        if v.get('status') == 'DELETE' or not isinstance(co, dict): continue
        c = co.get('forecast.json') or co.get('')
        out = 'data/raw/forecast/%s_%s_%d.json' % (v['code'], v['source'], v['updateTime'])
        if os.path.exists(out) or not c: continue
        if c.get('bytes') is not None: open(out, 'w').write(c['bytes']); continue
        q.put((c['url'], out))
total = q.qsize(); print('to fetch', total, flush=True)
def work():
    while True:
        try: u, out = q.get_nowait()
        except queue.Empty: return
        for a in range(3):
            try:
                b = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA}), timeout=120).read(); json.loads(b)
                open(out + '.tmp', 'wb').write(b); os.replace(out + '.tmp', out); break
            except Exception as e:
                if a == 2: fail.append((u, repr(e)[:80]))
                time.sleep(3 * (a + 1))
        done[0] += 1
        if done[0] % 500 == 0: print('done', done[0], 'of', total, flush=True)
        time.sleep(0.25)
ts = [threading.Thread(target=work) for _ in range(4)]
[t.start() for t in ts]; [t.join() for t in ts]
print('finished', done[0], 'failed', len(fail), fail[:5], flush=True)
