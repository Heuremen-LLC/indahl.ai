#!/usr/bin/env python3
"""linkrot_collect.py: the LINKROT census per PLAN.md. Reads the arXiv API (public, one request per 3 seconds), extracts code-host links from abstract and comment, writes data/papers.jsonl. Resumable per (year, token)."""
import os, sys, re, json, time, urllib.request, urllib.parse, datetime as D
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); os.makedirs('data', exist_ok=True)
UA = 'heuremen-linkrot/0.1 (+https://indahl.ai/linkrot)'; CATS = '(cat:cs.LG+OR+cat:cs.CL+OR+cat:cs.CV+OR+cat:quant-ph+OR+cat:stat.ML)'; TOKENS = ['github', 'gitlab', 'huggingface', 'zenodo', 'bitbucket']
HOSTS = r'(?:github\.com|gitlab\.com|huggingface\.co|zenodo\.org|bitbucket\.org)'
URLRE = re.compile(r'https?://(?:www\.)?' + HOSTS + r'/[^\s<>"\)\]\}]*|https?://(?:www\.)?' + HOSTS + r'\b', re.I)
def norm(u):
    u = u.rstrip('.,;:!?\'"*'); m = re.match(r'(https?://)(?:www\.)?(github\.com|gitlab\.com)/([^/\s]+)/([^/\s?#]+)', u, re.I)
    if m: return 'https://%s/%s/%s' % (m.group(2).lower(), m.group(3), re.sub(r'\.git$', '', m.group(4)))
    return u.replace('http://', 'https://')
def get(u):
    for a in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA}), timeout=60) as r: return r.read().decode('utf8', 'replace')
        except Exception as e: time.sleep(5 * (a + 1))
done = set(json.load(open('data/census_done.json'))) if os.path.exists('data/census_done.json') else set()
seen = set(); out = open('data/papers.jsonl', 'a')
for l in open('data/papers.jsonl'):
    try: seen.add(json.loads(l)['id'])
    except Exception: pass
yr_now = D.date.today().year
for y in range(2018, yr_now + 1):
    for tok in TOKENS:
        key = '%d|%s' % (y, tok)
        if key in done: continue
        start = 0; got = 0
        while True:
            q = 'search_query=%s+AND+abs:%s+AND+submittedDate:%%5B%d01010000+TO+%d12312359%%5D&start=%d&max_results=100&sortBy=submittedDate' % (CATS, tok, y, y, start)
            t = get('https://export.arxiv.org/api/query?' + q); time.sleep(3)
            if t is None: print('NOTHING_RETURNED', key, start, flush=True); break
            total = int(re.findall(r'<opensearch:totalResults[^>]*>(\d+)<', t)[0]); es = t.split('<entry>')[1:]
            for e in es:
                pid = re.findall(r'<id>http://arxiv.org/abs/([^<]+)</id>', e)[0]
                if pid in seen: continue
                seen.add(pid); summ = re.sub(r'\s+', ' ', re.findall(r'<summary>(.*?)</summary>', e, re.S)[0]); com = ' '.join(re.findall(r'<arxiv:comment[^>]*>(.*?)</arxiv:comment>', e, re.S))
                urls = sorted({norm(u) for u in URLRE.findall(summ + ' ' + com)})
                cat = (re.findall(r'<arxiv:primary_category[^>]*term="([^"]+)"', e) or [''])[0]
                out.write(json.dumps(dict(id=pid, year=int(re.findall(r'<published>(\d{4})', e)[0]), cat=cat, urls=urls)) + '\n'); got += 1
            out.flush(); start += 100
            if start >= total or not es: break
        done.add(key); json.dump(sorted(done), open('data/census_done.json', 'w')); print(key, 'new papers', got, 'of', total if 'total' in dir() else '?', flush=True)
out.close(); print('census done', len(seen), 'papers')
