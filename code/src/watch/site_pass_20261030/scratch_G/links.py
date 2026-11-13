import re,os,json,collections,html
from urllib.parse import urljoin
links=collections.defaultdict(set)   # url -> set of pages
for f in sorted(os.listdir('pages')):
    t=open('pages/'+f,encoding='utf-8').read()
    base='https://indahl.ai/oy/school/'+f[:-5] if f!='oy.html' else 'https://indahl.ai/oy'
    for m in re.finditer(r'(?:href|src)="([^"]+)"',t):
        u=html.unescape(m.group(1))
        if u.startswith(('mailto:','tel:','javascript:','#','data:')): continue
        links[urljoin(base,u)].add(f)
ext={u:p for u,p in links.items() if not u.startswith('https://indahl.ai')}
internal={u:p for u,p in links.items() if u.startswith('https://indahl.ai')}
print(len(links),len(ext),len(internal))
json.dump({u:sorted(p) for u,p in ext.items()},open('ext_links.json','w'))
json.dump({u:sorted(p) for u,p in internal.items()},open('int_links.json','w'))
# internal classification
c=collections.Counter()
for u in internal:
    c[re.sub(r'/\d+$','/N',re.sub(r'\?.*','',u))]+=1
for k,v in c.most_common(60): print(v,k)
# host counts for external
h=collections.Counter(re.match(r'https?://([^/]+)',u).group(1) for u in ext)
print(len(h)); print(h.most_common(15))
