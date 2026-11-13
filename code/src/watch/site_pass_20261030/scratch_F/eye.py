import re,html,sys
for i in sys.argv[1:]:
    raw=open(f'pages/{i}.html',encoding='utf-8').read()
    h1=re.search(r'<h1>(.*?)</h1>',raw).group(1)
    m=re.search(r'<main class="wrap">(.*?)</main>',raw,re.S).group(1)
    m=re.sub(r'<h2>(.*?)</h2>',r'\n## \1\n',m); m=re.sub(r'<li>',r'\n  - ',m); m=re.sub(r'<a href="(.*?)">(.*?)</a>',r'[\2](\1)',m)
    m=re.sub(r'<[^>]+>','',m)
    print('=====',i,html.unescape(h1)); print(html.unescape(m).strip()[:2500]); print()
