import re, urllib.request, urllib.error, concurrent.futures as cf, json, html
sm=re.findall(r'<loc>([^<]*)</loc>',open('sitemap.xml').read())
def g(u):
    try:
        r=urllib.request.urlopen(urllib.request.Request(u+'?w=1',headers={'User-Agent':'site-pass-A'}),timeout=40); b=r.read().decode('utf8','replace'); return r.status,len(b),b
    except urllib.error.HTTPError as e: return e.code,0,''
    except Exception as e: return 'ERR',0,''
out={}
with cf.ThreadPoolExecutor(8) as ex:
    for u,(s,n,b) in zip(sm,ex.map(g,sm)):
        t=re.search(r'<title>(.*?)</title>',b,re.S); h1=re.search(r'<h1[^>]*>(.*?)</h1>',b,re.S)
        can=re.search(r'<link rel="canonical" href="([^"]*)"',b); rob=re.search(r'<meta name="robots" content="([^"]*)"',b)
        # raw template markers
        junk=[m for m in ('undefined','NaN','__','{{','}}','[object') if m in re.sub(r'<script.*?</script>|<style.*?</style>','',b,flags=re.S)]
        out[u]=dict(status=s,n=n,title=html.unescape(t.group(1)) if t else None,h1=html.unescape(re.sub('<[^>]+>','',h1.group(1))) if h1 else None,canon=can.group(1) if can else None,robots=rob.group(1)[:20] if rob else None,junk=junk)
json.dump(out,open('sitemap_sweep.json','w'),indent=0)
bad=[(u,v['status']) for u,v in out.items() if v['status']!=200]
print(len(out),'urls; not 200:',bad[:20])
nc=[u for u,v in out.items() if v['canon']!=u and v['canon']!=u.rstrip('/')+'/' ]
print('canonical != url:',[(u,out[u]['canon']) for u in nc][:20], len(nc))
print('robots not index:',[(u,v['robots']) for u,v in out.items() if v['robots'] and not v['robots'].startswith('index')][:20])
print('junk:',[(u,v['junk']) for u,v in out.items() if v['junk']][:30])
print('no title:',[u for u,v in out.items() if not v['title']][:10],'no h1:',[u for u,v in out.items() if not v['h1']][:10])
import collections
c=collections.Counter(v['title'] for v in out.values()); print('dup titles:',[(t,n) for t,n in c.items() if n>1][:15])
