import sys, glob
from html.parser import HTMLParser
VOID={'meta','link','br','img','input','hr','source','area','base','col','embed','param','track','wbr','circle','rect','line','polyline','path','text'}
class P(HTMLParser):
    def __init__(s): super().__init__(); s.st=[]; s.err=[]
    def handle_starttag(s,t,a):
        if t in VOID: return
        if t in ('p','li','td','th','tr') and s.st and s.st[-1]==t and t in ('li','td','th','tr'): s.st.pop()
        s.st.append(t)
    def handle_startendtag(s,t,a): pass
    def handle_endtag(s,t):
        if t in VOID: return
        if t in s.st:
            while s.st and s.st[-1]!=t:
                x=s.st.pop()
                if x not in ('p','li','td','th','tr'): s.err.append(f'unclosed {x} before </{t}>')
            s.st.pop()
        else: s.err.append(f'stray </{t}>')
for f in sys.argv[1:]:
    p=P(); p.feed(open(f).read())
    left=[x for x in p.st if x not in ('p','li','td','th','tr','html','body','head')]
    if p.err or left: print(f, p.err[:5], left)
print('done')
