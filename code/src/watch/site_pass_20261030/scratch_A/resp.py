import re, urllib.request, concurrent.futures as cf, collections, json
sm=re.findall(r'<loc>([^<]*)</loc>',open('sitemap.xml').read())
OK=re.compile(r'^(model|oy|qia|iris|atlas|time|coin|cada|uptime|forecast|cadence|trials|launch|linkrot|arxivdrift|support|pkglicense|hflicense|hfsize|change|secrecords|seat|pkginstall|stack|revise|fedsep|airline|weights|hpt|ailuminate|airq|campus|hosts|tape)-[a-z0-9._-]{1,70}$')
def g(u):
    try: b=urllib.request.urlopen(urllib.request.Request(u+'?w=1',headers={'User-Agent':'site-pass-A'}),timeout=40).read().decode('utf8','replace')
    except Exception as e: return u,[],[]
    r=re.findall(r'href="/respond\?u=([^"]*)"',b)
    # also footers: terms/privacy/forms
    return u,r,re.findall(r'(?:src|href)="(/[^"#?]*\.(?:js|json|css|png|svg|zip|csv))',b)
bad=[];cnt=0;assets=collections.Counter()
with cf.ThreadPoolExecutor(8) as ex:
    for u,r,a in ex.map(g,sm):
        for x in r:
            cnt+=1
            if not OK.match(x): bad.append((u,x))
        for y in a: assets[y]+=1
print('respond links',cnt,'bad',bad[:20],len(bad))
json.dump(assets,open('assets.json','w'))
print(len(assets),'distinct local assets referenced')
