import re, html, sys, os, glob
ROOT='/Users/heuremen/bones-forge/heuremen.org'
def visible(s):
    s = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', s, flags=re.S|re.I)
    s = re.sub(r'<(code|svg)[^>]*>.*?</\1>', ' ', s, flags=re.S|re.I)
    s = re.sub(r'<head>.*?</head>', ' ', s, flags=re.S|re.I)
    s = re.sub(r'<[^>]+>', ' ', s)
    return html.unescape(s)
def metas(s):
    return [html.unescape(m) for m in re.findall(r'<meta (?:name|property)="(?:description|og:description)" content="([^"]*)"', s)]
tot=0
files = sys.argv[1:] or sorted(glob.glob(ROOT+'/**/*.html', recursive=True))
for f in files:
    s=open(f).read(); v=visible(s); n=v.count(';'); m=sum(x.count(';') for x in metas(s))
    tot+=n
    if n or m or len(sys.argv)>1: print(f"{n:4d} {m:2d} {os.path.relpath(f,ROOT)}")
print('total', tot)
