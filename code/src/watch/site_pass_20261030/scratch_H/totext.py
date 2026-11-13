import sys,re,html
from html.parser import HTMLParser
class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.out=[]; s.skip=0; s.inmain=False; s.row=[]; s.intable=False
    def handle_starttag(s,t,a):
        a=dict(a)
        if t in("script","style","svg","head","nav","footer","header"): s.skip+=1
        if t=="main": s.inmain=True
        if t in("p","h1","h2","h3","h4","div","section","li","br","table","ul") and s.skip==0: s.out.append("\n")
        if t=="tr": s.row=[]
        if t in("td","th"): s.out.append(" | ")
        if t=="a" and s.skip==0 and a.get("href"): s.out.append("[")
        if t=="a" and s.skip==0 and a.get("href"): s._href=a["href"]
    def handle_endtag(s,t):
        if t in("script","style","svg","head","nav","footer","header") and s.skip>0: s.skip-=1
        if t=="a" and s.skip==0: s.out.append("]("+getattr(s,"_href","")+")")
        if t=="tr": s.out.append("\n")
    def handle_data(s,d):
        if s.skip==0: s.out.append(d)
p=P(); p.feed(open(sys.argv[1],encoding="utf-8").read())
t="".join(p.out)
t=re.sub(r"[ \t]+"," ",t); t=re.sub(r"\n\s*\n+","\n",t)
print(t)
