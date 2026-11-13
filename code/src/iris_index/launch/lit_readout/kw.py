import sys,re
t=re.sub(r'\n+','\n',open(sys.argv[1]).read())
for k in sys.argv[2:]:
    ms=list(re.finditer(k,t))
    print('##',k,len(ms))
    for m in ms[:2]: print('  >>',t[max(0,m.start()-250):m.start()+450].replace('\n',' '))
