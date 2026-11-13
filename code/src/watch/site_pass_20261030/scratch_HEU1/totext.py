import re, os, html, sys
from html.parser import HTMLParser
class P(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True); s.out=[]; s.skip=0; s.href=None
    def handle_starttag(s,t,a):
        a=dict(a)
        if t in('script','style'): s.skip+=1
        if t in('p','div','li','h1','h2','h3','h4','tr','br','section','ul','ol','table','pre','header','footer','nav','details','summary','figure','figcaption','blockquote'):
            s.out.append('\n'+('#'*int(t[1])+' ' if t in('h1','h2','h3','h4') else ('- ' if t=='li' else '')))
        if t in('td','th'): s.out.append(' | ')
        if t=='a' and a.get('href'): s.out.append('['); s.href=a['href']
        if t=='img': s.out.append('[IMG %s alt=%r]'%(a.get('src'),a.get('alt')))
        if t=='script' and a.get('src'): s.out.append('[SCRIPT %s]'%a['src'])
    def handle_endtag(s,t):
        if t in('script','style'): s.skip-=1
        if t=='a' and s.href is not None: s.out.append('](%s)'%s.href); s.href=None
        if t in('p','h1','h2','h3','h4','div','li','tr','pre'): s.out.append('\n')
    def handle_data(s,d):
        if not s.skip: s.out.append(d)
for f in sorted(os.listdir('live')):
    raw=open('live/'+f,encoding='utf-8').read()
    title=re.search(r'<title>(.*?)</title>',raw,re.S)
    p=P(); p.feed(raw)
    t=''.join(p.out)
    t=re.sub(r'[ \t]+',' ',t); t=re.sub(r'\n\s*\n+','\n',t)
    open('txt/'+f.replace('.html','')+'.txt','w').write('TITLE: '+(title.group(1) if title else 'NONE')+'\n'+t)
