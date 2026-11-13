import re,html,sys
for f in sys.argv[1:]:
    t=open(f).read()
    body=t[t.find('<body'):] if '<body' in t else t
    s=re.sub(r'<script.*?</script>','[SCRIPT]',body,flags=re.S)
    s=re.sub(r'<style.*?</style>','',s,flags=re.S)
    s=re.sub(r'<a [^>]*href="([^"]*)"[^>]*>',lambda m:'<<'+m.group(1)+'>> ',s)
    s=re.sub(r'</(p|div|li|tr|h\d|section|table|ul|details|summary|pre)>','\n',s)
    s=re.sub(r'</t[dh]>',' | ',s)
    s=re.sub(r'<br\s*/?>','\n',s)
    s=re.sub(r'<[^>]+>','',s)
    s=html.unescape(s)
    s=re.sub(r'\n\s*\n+','\n',s)
    open(f.replace('.html','.txt'),'w').write(s)
