import json, subprocess, re, sys, time, concurrent.futures as cf
links = json.load(open('links.json'))
res = {}
def chk(u):
    base = 'https://indahl.ai' if u.startswith('/') else ''
    full = base + u.split('#')[0]
    if u.startswith('/respond'): full = base + u
    ua = 'Mozilla/5.0 (compatible; heuremen-site-pass/1.0)'
    for attempt in range(3):
        try:
            out = subprocess.run(['curl', '-s', '-L', '-o', '/dev/null', '-A', ua, '--max-time', '40', '-w', '%{http_code} %{url_effective} %{size_download}', full], capture_output=True, text=True, timeout=60).stdout
            code = out.split()[0]
            if code in ('429', '503', '000') and attempt < 2: time.sleep(3 * (attempt + 1)); continue
            return u, out
        except Exception as e:
            err = str(e)
    return u, 'ERR ' + err
ext = [u for u in links if u.startswith('http')]
internal = [u for u in links if not u.startswith('http') and not u.startswith('/respond')]
internal = sorted({u.split('#')[0] for u in internal})
todo = internal + [u for u in links if u.startswith('/respond')][:3]
# arxiv at lower concurrency
with cf.ThreadPoolExecutor(6) as ex:
    for u, out in ex.map(chk, todo): res[u] = out
with cf.ThreadPoolExecutor(3) as ex:
    for u, out in ex.map(chk, ext): res[u] = out
json.dump(res, open('linkcheck.json', 'w'), indent=1)
bad = {u: o for u, o in res.items() if not o.startswith('200')}
print('checked', len(res), 'non-200', len(bad))
for u, o in bad.items(): print(u, '->', o)
