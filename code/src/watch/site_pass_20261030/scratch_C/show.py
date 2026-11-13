import sys,re
sys.path.insert(0,'.')
import parse as P
for n in sys.argv[1:]:
    p=P.parse('pages/%s.html'%n)
    s=p['sections']
    print('=====',n,'|',p['title'])
    print('H1:',P.text(p['h1']))
    for k in ('Work','Published','Measured or recounted','QIA Calibration','How'):
        v=s[k]
        if k=='How': v=re.sub(r'<p class="meta">.*','',v,flags=re.S)
        codes=re.findall(r'class="code"[^>]*>([^<]+)<',v)
        print('['+k+']',('codes='+','.join(codes)+' ' if codes else ''),P.text(v))
    print('links:',[h for h in re.findall(r'href="([^"]*)"',p['body']) if 'respond' not in h and 'contact' not in h and h not in ('/qia','/qia/key')])
    print()
