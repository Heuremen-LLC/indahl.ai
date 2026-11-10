#!/usr/bin/env python3
"""wayback.py: sends URLs to the Internet Archive's Save Page Now, one every 12 s, and appends each result to data/wayback.jsonl
(url, capture URL or null, time). A URL already captured by this file is skipped. Usage: python3 wayback.py urls.txt"""
import os, sys, json, time, urllib.request, urllib.error

H = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(H, 'data', 'wayback.jsonl'); UA = 'heuremen-now/1 (+https://indahl.ai)'; PACE = 12


def done():
    s = set()
    if os.path.exists(OUT):
        for l in open(OUT):
            try:
                r = json.loads(l)
                if r.get('capture'): s.add(r['url'])
            except ValueError: pass
    return s


def save(url):
    req = urllib.request.Request('https://web.archive.org/save/' + url, headers={'User-Agent': UA})
    try:
        r = urllib.request.urlopen(req, timeout=120)
        loc = r.headers.get('Content-Location') or ''
        cap = ('https://web.archive.org' + loc) if loc.startswith('/web/') else (r.geturl() if '/web/' in r.geturl() else None)
        return cap, r.status
    except urllib.error.HTTPError as e:
        return None, e.code
    except Exception as e:
        return None, str(e)[:80]


if __name__ == '__main__':
    have = done(); urls = [u.strip() for u in open(sys.argv[1]) if u.strip() and u.strip() not in have]
    for i, u in enumerate(urls):
        cap, st = save(u)
        if st == 429: time.sleep(120); cap, st = save(u)
        with open(OUT, 'a') as f: f.write(json.dumps(dict(url=u, capture=cap, status=st, at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))) + '\n')
        time.sleep(PACE)
