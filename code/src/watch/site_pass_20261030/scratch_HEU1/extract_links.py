import re, os, sys, json, html
from urllib.parse import urljoin, urldefrag
base=os.getcwd()
urls=[l.strip() for l in open('html_urls.txt') if l.strip()]
links={}  # target -> set(pages)
for u in urls:
    path=u.replace('https://heuremen.org/','')
    loc = path if path else 'index.html'
    if loc.endswith('/'): loc+='index.html'
    f=os.path.join(base,'live',loc.replace('/','__'))
    raw=open(f,encoding='utf-8').read()
    for m in re.finditer(r'''(?:href|src|content|action|data-src)\s*=\s*(["'])(.*?)\1''',raw,re.S):
        v=html.unescape(m.group(2)).strip()
        if not v or v.startswith(('mailto:','javascript:','tel:','data:','#')): continue
        if not re.match(r'^(https?:)?//|^/|^[\w./-]',v): continue
        if ' ' in v and not v.startswith('http'): continue
        t=urldefrag(urljoin(u,v))[0]
        links.setdefault(t,set()).add(u)
json.dump({k:sorted(v) for k,v in links.items()},open('links.json','w'),indent=0)
print(len(links))
