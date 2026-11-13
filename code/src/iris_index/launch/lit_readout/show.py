import sys,re
t=open(sys.argv[1]).read()
t=re.sub(r'\n+','\n',t)
print('HEAD:',t[:int(sys.argv[2]) if len(sys.argv)>2 else 2200].replace('\n',' | '))
for m in re.finditer(r'(?i)\n\s*(acknowledg\w*|funding)\s*\n',t):
    print('\nACK:',t[m.start():m.start()+1200].replace('\n',' '))
print('\nIBM hits:',sorted(set(re.findall(r'ibm_\w+|ibm \w+|Heron|Eagle|Nighthawk|Qiskit',t)))[:15])
for m in list(re.finditer(r'(?i)spectator|crosstalk',t))[:0]: pass
