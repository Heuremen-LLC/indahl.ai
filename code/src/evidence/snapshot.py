"""snapshot.py: builds a dated evidence snapshot of our reservation (27 Oct 2026). Fetches the live reservation files and key pages from both sites, records status, headers and sha256,
writes manifest.json, asks the Wayback Machine to save the key URLs, timestamps the manifest hash with OpenTimestamps, rebuilds REGISTRY.csv and appends the crawler counts from Cloudflare.
Output is private: ~/Documents/Heuremen LLC/EVIDENCE/. Never prints the key or any token."""
import os, sys, json, hashlib, datetime, urllib.request, subprocess, csv, glob, re, time
sys.path.insert(0, os.path.expanduser('~/bones-forge/indahl-ai')); from hlcref import ref
E = os.path.expanduser('~/Documents/Heuremen LLC/EVIDENCE/'); B = os.path.expanduser('~/bones-forge/')
now = datetime.datetime.now(datetime.timezone.utc); stamp = now.strftime('%Y%m%dT%H%M%SZ'); D = f'{E}snapshots/{stamp}/'; os.makedirs(D)
UA = {'User-Agent': 'Mozilla/5.0 (compatible; HeuremenEvidence/1.0)'}
URLS = ['https://indahl.ai/robots.txt', 'https://indahl.ai/.well-known/tdmrep.json', 'https://indahl.ai/llms.txt', 'https://indahl.ai/sitemap.xml', 'https://indahl.ai/terms', 'https://indahl.ai/', 'https://indahl.ai/qia', 'https://indahl.ai/iris', 'https://indahl.ai/qia/list.json', 'https://indahl.ai/iris/list.json',
        'https://heuremen.org/robots.txt', 'https://heuremen.org/.well-known/tdmrep.json', 'https://heuremen.org/llms.txt', 'https://heuremen.org/sitemap.xml', 'https://heuremen.org/', 'https://heuremen.org/TERMS.txt']
man = dict(taken=now.isoformat(), files=[])
for u in URLS:
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40); body = r.read(); h = {k.lower(): v for k, v in r.headers.items()}
        keep = {k: h[k] for k in ('tdm-reservation', 'tdm-policy', 'content-type', 'x-robots-tag', 'last-modified', 'etag') if k in h}
        name = re.sub(r'[^A-Za-z0-9._-]+', '_', u.split('://')[1]) or 'root'; open(D + name, 'wb').write(body)
        man['files'].append(dict(url=u, status=r.status, sha256=hashlib.sha256(body).hexdigest(), bytes=len(body), headers=keep, saved=name))
    except Exception as e: man['files'].append(dict(url=u, error=str(e)[:100]))
# crawler behaviour as served
tests = {}
for bot in ('GPTBot', 'ClaudeBot', 'CCBot', 'Bytespider', 'Amazonbot', 'Googlebot', 'bingbot', 'OAI-SearchBot', 'PerplexityBot', 'Claude-SearchBot'):
    try: tests[bot] = urllib.request.urlopen(urllib.request.Request('https://indahl.ai/', headers={'User-Agent': f'Mozilla/5.0 (compatible; {bot})'}), timeout=30).status
    except urllib.error.HTTPError as e: tests[bot] = e.code
    except Exception as e: tests[bot] = str(e)[:40]
man['indahl_crawler_status_for_user_agents'] = tests
json.dump(man, open(D + 'manifest.json', 'w'), indent=1)
mh = hashlib.sha256(open(D + 'manifest.json', 'rb').read()).hexdigest(); open(D + 'manifest.sha256', 'w').write(mh + '  manifest.json\n')
# Wayback saves
saved = []
for u in [x for x in URLS if x.endswith(('robots.txt', 'tdmrep.json', 'llms.txt', '/terms', 'indahl.ai/', 'heuremen.org/', 'TERMS.txt'))]:
    try:
        r = urllib.request.urlopen(urllib.request.Request('https://web.archive.org/save/' + u, headers=UA), timeout=90); saved.append((u, r.status))
    except Exception as e: saved.append((u, str(getattr(e, 'code', e))[:30]))
    time.sleep(6)
json.dump(saved, open(D + 'wayback.json', 'w'))
# OpenTimestamps
ots = os.path.expanduser('~/bones-forge/evidence/otsenv/bin/ots')
pass   # no OpenTimestamps since 13 Nov 2026 (Wayfinder); the manifest and its sha256 are kept
# registry
rows = [('indahl.ai page', p, ref('page:' + p)) for p in sorted(set(re.findall(r"'(/[^']*)': P\d+", open(B + 'indahl-ai/pages.js').read())))]
for d in ('qia', 'iris'):
    for z in sorted(glob.glob(B + f'cloudflare-workers/heuremen-door/public/{d}/runs/*.zip')): rows.append(('data zip', f'{d}/runs/' + os.path.basename(z), ref(f'zip:{d}/' + os.path.basename(z))))
rows += [('list json', 'qia', ref('list:qia')), ('list json', 'iris', ref('list:iris'))]
for f in ('index.html', 'correlations.html', 'technical-summary.html', 'what-we-measured.html'): rows.append(('heuremen.org page', f, ref('heuremen:' + f)))
with open(E + 'REGISTRY.csv', 'w', newline='') as f: w = csv.writer(f); w.writerow(['surface type', 'surface', 'reference code']); w.writerows(rows)
os.chmod(E + 'REGISTRY.csv', 0o600)
print('snapshot', stamp, '| files', len([x for x in man['files'] if 'error' not in x]), 'of', len(URLS), '| wayback', [s for _, s in saved], '| registry rows', len(rows), '| ots', os.path.exists(D + 'manifest.json.ots'))
