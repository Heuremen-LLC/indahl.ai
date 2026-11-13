import sys,re,html
s=open(sys.argv[1],errors='ignore').read()
s=re.sub(r'(?s)<(script|style).*?</\1>','',s)
s=re.sub(r'<(br|/p|/tr|/li|/h\d|/div)[^>]*>','\n',s);s=re.sub(r'</t[dh]>',' | ',s)
s=re.sub(r'<[^>]+>','',s);s=html.unescape(s)
print(re.sub(r'\n\s*\n+','\n',s))
