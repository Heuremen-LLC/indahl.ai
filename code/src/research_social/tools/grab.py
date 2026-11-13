import sys,re,html,subprocess
url,out=sys.argv[1],sys.argv[2]; keys=sys.argv[3:]
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
h=subprocess.run(['curl','-sL','-A',UA,'-m','30',url],capture_output=True).stdout.decode('utf8','ignore')
open(out+'.html','w').write(h)
t=re.sub(r'<script.*?</script>|<style.*?</style>',' ',h,flags=re.S)
t=html.unescape(re.sub(r'<[^>]+>',' ',t)); t=re.sub(r'\s+',' ',t)
open(out+'.txt','w').write(t)
print('chars',len(t))
links=set(re.findall(r'https?:[^"\'\\ <>]+?\.(?:csv|zip|xlsx)\b[^"\'\\ <>]*',h.replace('\\u002F','/').replace('\\/','/')))
print('data links:',sorted(links)[:15])
for k in keys:
    for m in list(re.finditer(k,t,re.I))[:3]:
        print('>>',k,'|',t[max(0,m.start()-220):m.start()+380]); print()
