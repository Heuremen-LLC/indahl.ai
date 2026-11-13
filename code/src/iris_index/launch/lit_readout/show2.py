import sys,re
t=re.sub(r'\n+','\n',open(sys.argv[1]).read())
i=t.find('arXiv:'+sys.argv[2])
print('HEAD:',t[i:i+int(sys.argv[3])].replace('\n',' | '))
for m in re.finditer(r'\n\s*(Acknowledg\w*|Funding|ACKNOWLEDG\w*)[.:]?\s*\n',t):
    print('\nACK@',m.start(),':',t[m.start():m.start()+900].replace('\n',' '))
print('\nHW:',sorted(set(re.findall(r'ibm_\w+|ibm\w* \w+|Heron|Eagle|Nighthawk|Falcon|Rigetti|IQM|Google|Zuchongzhi|trapped',t)))[:15])
