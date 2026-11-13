#!/usr/bin/env python3
"""Independent recount. Reads the desk's data/raw copies read-only. Own code, no import from the desk."""
import json, re, math
R='/Users/heuremen/bones-forge/census_coverage/data/raw/'
f=lambda x: None if x is None else float(x.replace('–','-').replace('*',''))
G=json.load(open(R+'pes_g_states.json'))
rows=[r for r in G[1:] if r[-1]!='72']
print('G rows',len(G)-1,'frame',len(rows),'PR rows',[r[0] for r in G[1:] if r[-1]=='72'])
Z=1.645
out={}
for r in rows:
    n,cnt,e,se=r[0],int(r[3]),f(r[5]),f(r[7])
    lo,hi=e-Z*se,e+Z*se
    o='BELOW' if hi<0 else 'ABOVE' if lo>0 else 'CONSISTENT'
    out[n]=(cnt,e,se,o,abs(e)/se)
from collections import Counter
print(Counter(v[3] for v in out.values()))
print('BELOW',sorted(k for k,v in out.items() if v[3]=='BELOW'));print('ABOVE',sorted(k for k,v in out.items() if v[3]=='ABOVE'))
print('closest to 1.645 (|z|):',sorted(((round(v[4],3),k) for k,v in out.items()),key=lambda t:abs(t[0]-1.645))[:6])
# PDF
t=open(R+'census-coverage-estimates-for-people-in-the-united-states-by-state-and-census-operations.txt').read()
i=t.find('Appendix Table 3.\nNet'); j=t.find('Source:',i)
L=[x.strip() for x in t[i:j].split('\n')]
pdf={};k=0
while k<len(L)-4:
    if re.fullmatch(r'\d{1,3}(,\d{3})*',L[k+1]) and re.search(r'[A-Za-z]',L[k]) and re.fullmatch(r'\*?[–-]?\d+\.\d+',L[k+2]):
        nm=re.sub(r'[\s.]+$','',L[k]); pdf[nm]=(int(L[k+1].replace(',','')),f(L[k+2]),f(L[k+3]),'*' in L[k+2]);k+=4
    else:k+=1
print('pdf rows',len(pdf))
bad=[n for n in out if pdf.get(n,(0,))[:3]!=out[n][:3]]
print('API vs PDF mismatches',bad)
stars=sorted(n for n,v in pdf.items() if v[3] and n!='Total')
mine=sorted(n for n,v in out.items() if v[3]!='CONSISTENT')
print('asterisk set == my flagged set:',stars==mine,len(stars))
# US
A=json.load(open(R+'pes_A_TOTUS.json'));a=dict(zip(A[0],A[1]))
e,se=f(a['A_TOTUS_COL4_R1']),f(a['A_TOTUS_COL5_R1']);print('US',e,se,e-Z*se,e+Z*se)
# DA
rel=open(R+'census_release_20220310.html').read();txt=re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',rel))
m=txt.find('Table 1. Post-Enumeration');print(txt[m:m+700])
# components
H=json.load(open(R+'pes_H_STATES.json'));h=H[0]
Hd={}
for r in H[1:]:
    d=dict(zip(h,r))
    if d['state']!='72': Hd.setdefault(d['NAME'],{})[d['H_STATES_001']]=d
B=json.load(open(R+'pes_B_TOTUS.json'));b=dict(zip(B[0],B[1]))
nat={'omissions':('H_STATES_010','R13'),'duplication':('H_STATES_006','R8'),'other':('H_STATES_007','R9')}
for c,(fld,rr) in nat.items():
    p=f(b['B_TOTUS_COL3_'+rr]);s=f(b['B_TOTUS_COL4_'+rr])
    cc=Counter();who={'BELOW':[],'ABOVE':[]};zero=0;sent=0
    for n in out:
        e=f(Hd[n]['COUNT'][fld]);se=f(Hd[n]['SE'][fld])
        if se is None or se==-9999.9: cc['CANNOT_TELL']+=1;sent+=1;continue
        if se<=0: zero+=1; cc['CANNOT_TELL']+=1;continue
        lo,hi=e-Z*se,e+Z*se
        o='BELOW' if hi<p else 'ABOVE' if lo>p else 'CONSISTENT';cc[o]+=1
        if o in who: who[o].append(n)
    print(c,'nat',p,s,dict(cc),'sentinel',sent,'se<=0',zero,who)
    # also: rounding-aware: state SE of 0.0 rows
    print('   se==0.0 states:',[n for n in out if f(Hd[n]['SE'][fld])==0.0])
# NCE join
print('join mismatch',[n for n in out if f(Hd[n]['COUNT']['H_STATES_011'])!=out[n][1]])
# SE consistency: national duplic vs state
