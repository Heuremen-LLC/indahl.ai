import json,re,html,subprocess,hashlib,os,sys,time,collections
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
B='/Users/heuremen/bones-forge/'
ids=[l.strip().rsplit('/',1)[1] for l in open(B+'watch/site_pass_20261030/lane_F_urls.txt')]
links=collections.defaultdict(set)   # url -> set of page ids
kind={}
for i in ids:
    raw=open(f'pages/{i}.html',encoding='utf-8').read()
    main=re.search(r'<main class="wrap">(.*?)</main>',raw,re.S).group(1)
    for h in re.findall(r'href="(.*?)"',main):
        h=html.unescape(h)
        if h.startswith('http'): links[h].add(i)
        else:
            u='https://indahl.ai'+h; links[u].add(i)
    # header/footer/nav links once
    for h in re.findall(r'href="(.*?)"',raw):
        h=html.unescape(h)
        if h.startswith('/') : links['https://indahl.ai'+h].add('chrome')
        elif h.startswith('http'): links[h].add('chrome')
print('unique links',len(links))
UA1='Mozilla/5.0 (research crawler; contact via heuremen.org)'
UA2='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
def get(u,ua):
    f='src/'+hashlib.md5((u+ua).encode()).hexdigest()
    r=subprocess.run(['curl','-sL','-m','30','--max-redirs','8','--max-filesize','25000000','-A',ua,'-o',f,'-w','%{http_code}|%{url_effective}|%{content_type}|%{size_download}|%{num_redirects}',u],capture_output=True,text=True)
    parts=r.stdout.split('|')
    return dict(code=parts[0] if parts else '',eff=parts[1] if len(parts)>1 else '',ctype=parts[2] if len(parts)>2 else '',size=parts[3] if len(parts)>3 else '',redir=parts[4] if len(parts)>4 else '',rc=r.returncode,file=f)
def check(u):
    r=get(u,UA1); r['ua']=1
    if r['code'] in ('403','401','406','429','000','503','999') and r['rc'] in (0,):
        r2=get(u,UA2); r2['ua']=2; r2['first']=r['code']; r=r2
    return r
byhost=collections.defaultdict(list)
for u in links: byhost[urlparse(u).netloc].append(u)
def runhost(h):
    out={}
    for u in byhost[h]:
        out[u]=check(u); time.sleep(0.3)
    return out
res={}
with ThreadPoolExecutor(16) as ex:
    for o in ex.map(runhost,list(byhost)): res.update(o)
for u in res: res[u]['pages']=sorted(links[u])[:5]; res[u]['npages']=len(links[u])
json.dump(res,open('part3_links.json','w'),indent=0)
print(collections.Counter(r['code'] for r in res.values()).most_common(), collections.Counter(r['rc'] for r in res.values()))
