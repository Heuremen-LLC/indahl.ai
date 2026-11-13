import re, sys, html, urllib.request
for i in sys.argv[1:]:
    try:
        t=urllib.request.urlopen(urllib.request.Request(f'https://arxiv.org/abs/{i}',headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read().decode('utf8','ignore')
    except Exception as e:
        print(i,'ERR',e); continue
    title=html.unescape(re.search(r'<meta name="citation_title" content="([^"]*)"',t).group(1))
    jr=re.search(r'Journal reference:</td>\s*<td[^>]*>(.*?)</td>',t,re.S)
    jr=re.sub(r'<[^>]+>','',jr.group(1)).strip() if jr else None
    auth=re.findall(r'<meta name="citation_author" content="([^"]*)"',t)
    print(f'{i} | {title} | {jr} | first author: {auth[0] if auth else None} | n={len(auth)}')
