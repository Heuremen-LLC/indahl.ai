import re, sys, html, urllib.request, json, os
ids = sys.argv[1:]
for i in ids:
    try:
        req=urllib.request.Request(f'https://arxiv.org/abs/{i}', headers={'User-Agent':'Mozilla/5.0'})
        t=urllib.request.urlopen(req, timeout=30).read().decode('utf8','ignore')
    except Exception as e:
        print(i,'ERR',e); continue
    title=re.search(r'<meta name="citation_title" content="([^"]*)"',t)
    auth=re.findall(r'<meta name="citation_author" content="([^"]*)"',t)
    date=re.search(r'<meta name="citation_date" content="([^"]*)"',t)
    ab=re.search(r'<meta name="citation_abstract" content="([^"]*)"',t, re.S)
    out={'id':i,'title':html.unescape(title.group(1)) if title else None,'authors':[html.unescape(a) for a in auth],'date':date.group(1) if date else None,'abstract':html.unescape(ab.group(1)).replace('\n',' ') if ab else None}
    json.dump(out, open(f'arx/{i}.json','w'), indent=1)
    print(i, out['title'], '|', out['date'], '|', ', '.join(out['authors'][:3]), '...', len(out['authors']))
