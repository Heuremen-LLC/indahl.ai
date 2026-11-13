import re,math,collections
L=open('gridsong/resonance_output.log',errors='ignore').read().split('\n')
echo=[];delta=[];cyc=[]
for l in L:
    if 'Echo at 6pi:' in l: echo.append(l)
    elif l.strip().startswith('Deltas:'): delta.append(l)
    m=re.search(r'CYCLE (\d+) — (\d\d:\d\d:\d\d)',l)
    if m: cyc.append((int(m.group(1)),m.group(2)))
print('cycle',cyc[-1], 'lines',len(echo),len(delta))
E=echo[-400:];D=delta[-400:]
vals=[];star=0;tot=0
for l in E:
    for m in re.finditer(r'(\d+)Hz:([+-]\d+\.\d)(\*?)',l):
        vals.append(float(m.group(2)));tot+=1;star+=bool(m.group(3))
for l in D:
    for m in re.finditer(r'(\d+):([+-]\d+\.\d)',l): vals.append(float(m.group(2)))
print('starred',star,'of',tot,'n',len(vals),'W',max(abs(v) for v in vals))
last3=[l.split('Echo at 6pi:')[1].strip() for l in echo[-3:]]
print(last3[::-1])
N=len(vals);W=39
T={'phi':1.618034,'pi':math.pi,'12/11':12/11,'11/12':11/12,'2.65':2.65,'2pi':2*math.pi,'3pi':3*math.pi,'1/phi':1/1.618034,'1/pi':1/math.pi,'1/12':1/12}
av=[abs(v) for v in vals]
for k,t in T.items():
    lo,hi=t*.98,t*1.02
    h=sum(lo<=a<=hi for a in av)
    flat=N*2*(hi-lo)/(2*31)
    pts=sum(1 for g in range(0,400) if lo<=g/10<=hi)*2 if True else 0
    gridexp=pts*N/781
    nb=[]
    for d in (-1,-.5,.5,1):
        c=t+d
        if c<=0: continue
        nb.append(sum(c*.98<=a<=c*1.02 for a in av))
    dens=h/(sum(nb)/len(nb)) if nb and sum(nb)>0 else None
    print(k,h,'flat %.1f'%flat,'grid %.1f'%gridexp,'dens',None if dens is None else round(dens,2),'ptsingrid',pts//2)
