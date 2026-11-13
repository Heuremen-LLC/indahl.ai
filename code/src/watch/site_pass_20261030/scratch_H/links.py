import re,sys,glob,json,html
from urllib.parse import urljoin
out={}
for f in sorted(glob.glob("dom/*.html")):
    h=open(f,encoding="utf-8").read()
    # strip head, header, footer, nav
    h2=re.sub(r'<head>.*?</head>','',h,flags=re.S)
    h2=re.sub(r'<header class="top">.*?</header>','',h2,flags=re.S)
    h2=re.sub(r'<footer.*?</footer>','',h2,flags=re.S)
    h2=re.sub(r'<nav class="tabbar".*?</nav>','',h2,flags=re.S)
    page=f.split("/")[-1][:-5].replace("_","/")
    for m in re.finditer(r'<a\s[^>]*href="([^"]+)"',h2):
        u=html.unescape(m.group(1))
        if u.startswith(("#","mailto:","javascript:")): continue
        full=urljoin("https://indahl.ai/"+page,u)
        out.setdefault(full,[]).append(page)
json.dump(out,open("links.json","w"),indent=0)
print(len(out))
