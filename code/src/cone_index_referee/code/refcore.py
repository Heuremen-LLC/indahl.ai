# Referee core readers and geometry. Written independently of cone_tick.py / heuremen_kit.py.
import gzip, glob, os, re, json, math, datetime as dt, collections
import numpy as np
ROOT='/Users/heuremen/bones-forge/cone_index/data/raw/'
R_NM=3440.065
TC={'TD','TS','HU','SD','SS'}
LEADS=[12,24,36,48,72,96,120]

def pos(s_lat,s_lon):
    s_lat=s_lat.strip(); s_lon=s_lon.strip()
    la=int(s_lat[:-1])/10.0*(1 if s_lat[-1]=='N' else -1)
    lo=int(s_lon[:-1])/10.0*(1 if s_lon[-1]=='E' else -1)
    return la,lo
def ptime(s): return dt.datetime.strptime(s,'%Y%m%d%H')
def addh(s,h): return (ptime(s)+dt.timedelta(hours=h)).strftime('%Y%m%d%H')

def gc(a,b):
    la1,lo1,la2,lo2=map(math.radians,(a[0],a[1],b[0],b[1]))
    h=math.sin((la2-la1)/2)**2+math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2*R_NM*math.asin(min(1.0,math.sqrt(h)))
def bearing(a,b):
    la1,lo1,la2,lo2=map(math.radians,(a[0],a[1],b[0],b[1]))
    y=math.sin(lo2-lo1)*math.cos(la2)
    x=math.cos(la1)*math.sin(la2)-math.sin(la1)*math.cos(la2)*math.cos(lo2-lo1)
    return math.atan2(y,x)

def read_adecks(stats):
    """returns dict[(basin,season,num)] -> dict[dtg] -> dict[tau]->(lat,lon); first OFCL per (dtg,tau)"""
    out={}
    files=[]
    for y in range(2010,2026):
        files+=sorted(glob.glob(ROOT+'adeck/%d/a*%d.dat.gz'%(y,y)))
    files+=sorted(glob.glob(ROOT+'current/a*2026.dat.gz'))
    stats['adeck_files']=len(files); stats['dup_diff']=0; stats['bad_lines']=0; stats['ofcl_lines']=0
    for f in files:
        m=re.match(r'a(al|ep)(\d\d)(\d{4})\.dat\.gz',os.path.basename(f))
        if not m: stats['bad_lines']+=1; continue
        basin=m.group(1).upper(); num=int(m.group(2)); season=int(m.group(3))
        if num>=90: continue
        key=(basin,season,num); d=out.setdefault(key,{})
        with gzip.open(f,'rt',errors='replace') as fh:
            for line in fh:
                p=[x.strip() for x in line.split(',')]
                if len(p)<11 or p[4]!='OFCL': continue
                stats['ofcl_lines']+=1
                try:
                    tau=int(p[5]); ll=pos(p[6],p[7])
                except Exception:
                    stats['bad_lines']+=1; continue
                if int(p[1])!=num or p[0]!=basin: stats['mismatch_id']=stats.get('mismatch_id',0)+1
                dd=d.setdefault(p[2],{})
                if tau in dd:
                    if dd[tau]!=ll: stats['dup_diff']+=1
                    continue
                dd[tau]=ll
    return out

def read_hurdat(path,prefix_ok):
    """dict[id] -> dict[YYYYMMDDHH] -> (lat,lon,status); synoptic only"""
    out={}; cur=None; dups=0
    for line in open(path):
        p=[x.strip() for x in line.split(',')]
        if re.fullmatch(r'[A-Z]{2}\d{6}',p[0]):
            cur=p[0]; out[cur]={} if cur[:2] in prefix_ok else None; continue
        if cur is None or out[cur] is None: continue
        hhmm=p[1]
        if hhmm not in ('0000','0600','1200','1800'): continue
        t=p[0]+hhmm[:2]
        la=p[4]; lo=p[5]
        la=float(la[:-1])*(1 if la[-1]=='N' else -1); lo=float(lo[:-1])*(1 if lo[-1]=='E' else -1)
        if t in out[cur]: dups+=1; continue
        out[cur][t]=(la,lo,p[3])
    out['_dups']=dups
    return out

def read_bdecks(stats):
    out={}
    for f in sorted(glob.glob(ROOT+'current/b*2026.dat')):
        m=re.match(r'b(al|ep)(\d\d)2026\.dat',os.path.basename(f))
        basin=m.group(1).upper(); num=int(m.group(2))
        d={}
        for line in open(f):
            p=[x.strip() for x in line.split(',')]
            if len(p)<11 or p[4]!='BEST': continue
            t=p[2]
            if t[8:] not in ('00','06','12','18'): continue
            if t in d: continue
            la,lo=pos(p[6],p[7]); d[t]=(la,lo,p[10])
        out['%s%02d2026'%(basin,num)]=d
    return out

# ---------------- geometry ----------------
def proj(P,c):
    d=gc(P,c); th=bearing(P,c)
    return np.array([d*math.sin(th),d*math.cos(th)])
def seg_margin(p0,r0,p1,r1):
    """min over t in [0,1] of |c(t)|-r(t), origin = tested point. <=0 means inside hull of the two discs. Exact (convex in t)."""
    dv=p1-p0; dr=r1-r0
    # g(t)=|p0+t dv| - (r0+t dr) convex; minimize by closed form on |.|^2 - r^2 root and by ternary
    lo,hi=0.0,1.0
    f=lambda t: math.hypot(*(p0+t*dv))-(r0+t*dr)
    for _ in range(60):
        m1=lo+(hi-lo)/3; m2=hi-(hi-lo)/3
        if f(m1)<f(m2): hi=m2
        else: lo=m1
    return min(f((lo+hi)/2),f(0.0),f(1.0))
def cone_margin(P,centers,radii):
    pts=[proj(P,c) for c in centers]
    return min(seg_margin(pts[i],radii[i],pts[i+1],radii[i+1]) for i in range(len(pts)-1))
def seg_inside_exact(p0,r0,p1,r1):
    # exact quadratic: exists t in [0,1], r(t)>=0, |p0+t dv|^2 <= (r0+t dr)^2
    dv=p1-p0; dr=r1-r0
    a=dv@dv-dr*dr; b=2*(p0@dv-r0*dr); c=p0@p0-r0*r0
    cand=[0.0,1.0]
    if abs(a)>1e-12:
        t=-b/(2*a)
        if 0<t<1: cand.append(t)
    return any((p0+t*dv)@(p0+t*dv)<=(r0+t*dr)**2+1e-9 for t in cand) or seg_margin(p0,r0,p1,r1)<=0
