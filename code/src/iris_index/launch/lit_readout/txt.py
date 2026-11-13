import sys,re,html
t=open(sys.argv[1]).read()
t=re.sub(r'<(script|style|math)[^>]*>.*?</\1>','',t,flags=re.S)
t=re.sub(r'<(br|p|div|h\d|li|section|header)[^>]*>','\n',t)
t=re.sub(r'<[^>]+>',' ',t); t=html.unescape(t)
t=re.sub(r'[ \t]+',' ',t); t=re.sub(r'\n\s*\n+','\n',t)
open(sys.argv[1]+'.txt','w').write(t)
