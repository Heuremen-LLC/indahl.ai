import re,glob,subprocess,sys,urllib.parse,json
pages=sorted(glob.glob('iris*.html'))
links={}
for f in pages:
    t=open(f).read()
    for m in re.finditer(r'(?:href|src)="([^"#][^"]*)"',t):
        u=m.group(1)
        if u.startswith(('mailto:','tel:','data:','javascript:')): continue
        links.setdefault(u,set()).add(f)
print(len(links),'distinct links')
import concurrent.futures as cf
def chk(u):
    full=u if u.startswith('http') else urllib.parse.urljoin('https://indahl.ai/',u)
    if full.startswith('//'): full='https:'+full
    try:
        r=subprocess.run(['curl','-s','-o','/dev/null','-L','-A','Mozilla/5.0 (site-pass)','-m','25','-w','%{http_code} %{url_effective}',full],capture_output=True,text=True,timeout=40)
        return u,full,r.stdout
    except Exception as e:
        return u,full,'ERR '+str(e)
with cf.ThreadPoolExecutor(8) as ex:
    res=list(ex.map(chk,sorted(links)))
for u,full,out in res:
    code=out.split()[0] if out else '?'
    if code!='200': print(code,u,'<-',sorted(links[u])[:3],out[4:100])
print('done')
