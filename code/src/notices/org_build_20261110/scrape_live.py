"""scrape_live.py (10 Nov 2026): reads every live /brand/<slug> page on indahl.ai and writes live_pages.json
(slug -> status, respond link, csv link, rows with desk, question, cells and links exactly as the page shows them). Run: python3 -I scrape_live.py"""
import json, os, re, sys, html, urllib.request, concurrent.futures as CF
H = os.path.dirname(os.path.abspath(__file__)); B = os.path.expanduser('~/bones-forge')
E = json.load(open(B + '/brands/entities.json'))['entities']
def txt(s): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', s))).strip()
def one(slug):
    u = 'https://indahl.ai/brand/' + slug
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'heuremen-notices/1'}), timeout=30); s = r.read().decode('utf-8'); st = r.status
    except urllib.error.HTTPError as e: return slug, {'status': e.code}
    except Exception as e: return slug, {'status': 'error ' + str(e)}
    m = re.search(r'<main.*?</main>', s, re.S); s = m.group(0) if m else s
    out = {'status': st, 'url': u, 'title': txt(re.search(r'<h1>(.*?)</h1>', open and r and s, re.S).group(1)) if re.search(r'<h1>', s) else '',
           'respond': (re.search(r'href="(/respond\?u=[^"]+)"', s) or [None, None])[1], 'correction': '/correction' if 'href="/correction"' in s else None, 'rows': []}
    for sec in re.finditer(r'<h2 id="([^"]+)">(.*?)</h2>(.*?)(?=<h2 id=|$)', s, re.S):
        desk = txt(sec.group(2))
        for blk in re.finditer(r'<h3>(.*?)</h3>(.*?)</table>', sec.group(3), re.S):
            q = txt(blk.group(1)); heads = [txt(h) for h in re.findall(r'<th>(.*?)</th>', blk.group(2), re.S)]
            for tr in re.findall(r'<tr>(.*?)</tr>', blk.group(2), re.S):
                tds = re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)
                if not tds: continue
                row = dict(zip(heads, [txt(t) for t in tds])); row['links'] = re.findall(r'href="([^"]+)"', tds[-1])
                row['desk'] = desk; row['question'] = q; out['rows'].append(row)
    return slug, out
with CF.ThreadPoolExecutor(12) as ex: res = dict(ex.map(one, [e['slug'] for e in E]))
json.dump(res, open(sys.argv[1] if len(sys.argv) > 1 else H + '/live_pages.json', 'w'), indent=1, ensure_ascii=False)
import collections; print(collections.Counter(str(v['status']) for v in res.values()), sum(len(v.get('rows', [])) for v in res.values()), 'rows')
