import re,sys,html,json
from urllib.parse import urljoin,urldefrag
pages={'qia':'https://indahl.ai/qia','qia_list':'https://indahl.ai/qia/list','qia_key':'https://indahl.ai/qia/key'}
out={}
for n,u in pages.items():
    t=open(n+'.html',encoding='utf-8').read()
    for m in re.finditer(r'(?:href|src)="([^"]+)"',t):
        h=html.unescape(m.group(1))
        if h.startswith(('mailto:','javascript:','tel:','data:')) : 
            out.setdefault(h,set()).add(n); continue
        a=urldefrag(urljoin(u,h))[0]
        out.setdefault(a,set()).add(n)
json.dump({k:sorted(v) for k,v in out.items()},open('links.json','w'),indent=0)
print(len(out))
