#!/usr/bin/env python3
"""look_test_score.py -- scores look_test.v1 EXACTLY as registered in look_test_claim.v1.json.
Written and hashed 14 Oct before slot 31 closed (08:00), so the analysis exists before the data does (LA SUMA).
Per reading y: y = a + b*d + c*(her_cores - mean); P = -b/a; slots are the units; widths inflated by
sqrt((1+r1)/(1-r1)) when lag-1 r1 > 0.3. Apparatus decided FIRST and kept apart. Outcomes:
HOLDS / DOES_NOT_RESOLVE / NOT_A_LINE, plus APPARATUS. --selftest runs on synthetic rows, writes nothing."""
import json, sys, math, hashlib, os
W = os.path.dirname(os.path.abspath(__file__))
CLAIM = os.path.join(W, 'look_test_claim.v1.json'); LEDGER = os.path.join(W, 'look_test.jsonl')
DOSES = (0, 30, 120)

def arm_of(seed, k):
    return DOSES[int(hashlib.sha256(('%s|%d' % (seed, k)).encode()).hexdigest(), 16) % 3]

def inv3(m):
    a,b,c=m[0];d,e,f=m[1];g,h,i=m[2]
    det=a*(e*i-f*h)-b*(d*i-f*g)+c*(d*h-e*g)
    if abs(det)<1e-300: raise ZeroDivisionError('singular design')
    return [[(e*i-f*h)/det,(c*h-b*i)/det,(b*f-c*e)/det],[(f*g-d*i)/det,(a*i-c*g)/det,(c*d-a*f)/det],[(d*h-e*g)/det,(b*g-a*h)/det,(a*e-b*d)/det]]

def ols(X, y):
    n=len(y); k=3
    XtX=[[sum(X[r][i]*X[r][j] for r in range(n)) for j in range(k)] for i in range(k)]
    Xty=[sum(X[r][i]*y[r] for r in range(n)) for i in range(k)]
    V=inv3(XtX); beta=[sum(V[i][j]*Xty[j] for j in range(k)) for i in range(k)]
    res=[y[r]-sum(X[r][j]*beta[j] for j in range(k)) for r in range(n)]
    s2=sum(e*e for e in res)/max(1,n-k)
    cov=[[V[i][j]*s2 for j in range(k)] for i in range(k)]
    return beta, cov, res

def lag1(res):
    m=sum(res)/len(res); num=sum((res[i]-m)*(res[i-1]-m) for i in range(1,len(res))); den=sum((e-m)**2 for e in res)
    return num/den if den>0 else 0.0

def exclusions(r):
    why=[]
    if not r.get('miner_pids_same', True): why.append('xmrig pid changed inside the slot')
    if (r.get('xmrig_uptime') or 0) < 900: why.append('xmrig uptime < 900 s at the slot end')
    if r.get('paused_at_end') or (r.get('miner_cores') or 0) < 8: why.append('paused at the end, or miner_cores < 8')
    d=r['dose_per_min']; a=r.get('achieved_per_min') or 0.0
    if d>0 and abs(a-d)/d > 0.20: why.append('achieved dose off target by > 20%')
    if d==0 and a!=0: why.append('achieved dose off target by > 20%')
    if r.get('R15') in (None, 0): why.append('R15 unread')
    return why

def fit_reading(rows, key):
    hm=sum(r['her_cores'] for r in rows)/len(rows)
    rows=sorted(rows,key=lambda r:r['slot'])
    X=[[1.0, float(r['dose_per_min']), r['her_cores']-hm] for r in rows]; y=[r[key] for r in rows]
    (a,b,c),cov,res=ols(X,y); r1=lag1(res); infl=math.sqrt((1+r1)/(1-r1)) if r1>0.3 else 1.0
    P=-b/a
    # delta method on P=-b/a
    dPa=b/a**2; dPb=-1/a
    varP=dPa**2*cov[0][0]+dPb**2*cov[1][1]+2*dPa*dPb*cov[0][1]
    wP=math.sqrt(max(varP,0))*infl
    # line check: fit on the 0 and 120 arms only (with covariate), predict the 30 arm's covariate-adjusted mean
    ends=[r for r in rows if r['dose_per_min'] in (0,120)]; mid=[r for r in rows if r['dose_per_min']==30]
    Xe=[[1.0,float(r['dose_per_min']),r['her_cores']-hm] for r in ends]; ye=[r[key] for r in ends]
    (ae,be,ce),cove,rese=ols(Xe,ye)
    adj=[r[key]-ce*(r['her_cores']-hm) for r in mid]; mm=sum(adj)/len(adj)
    sm=math.sqrt(sum((v-mm)**2 for v in adj)/max(1,len(adj)-1)/len(adj))
    pred=ae+be*30; spred=math.sqrt(max(0,cove[0][0]+900*cove[1][1]+60*cove[0][1]))
    wline=math.sqrt(sm**2+spred**2)*infl; off=(mm-pred)/wline if wline>0 else float('inf')
    return dict(a=a,b=b,c=c,P=P,P_width=wP,P_widths=abs(P)/wP if wP>0 else float('inf'),r1=r1,inflation=infl,
                line_mid_mean=mm,line_pred=pred,line_off_widths=off,n=len(rows))

def outcome(f):
    resolves=f['P_widths']>=2; line=abs(f['line_off_widths'])<2
    if not line: return 'NOT_A_LINE'
    return 'HOLDS' if resolves else 'DOES_NOT_RESOLVE'

def score(rows, seed, nslots=32):
    out={'slots_in_ledger':len(rows)}
    bad=[r['slot'] for r in rows if r['dose_per_min']!=arm_of(seed,r['slot'])]
    out['arm_mismatch_slots']=bad
    usable=[];excl={}
    for r in rows:
        w=exclusions(r)
        if bad and r['slot'] in bad: w.append('dose differs from the registered arm')
        if w: excl[r['slot']]=w
        else: usable.append(dict(r))
    for r in usable:
        r['rate']=r['R15']; r['cores']=r['miner_cores']; r['hpcs']=r['R15']*900.0/(r['miner_cores']*r['dt'])
    per={d:sum(1 for r in usable if r['dose_per_min']==d) for d in DOSES}
    out.update(excluded=excl,usable_per_arm=per)
    app=[]
    if min(per.values())<7: app.append('fewer than 7 usable slots in an arm: %s'%per)
    if len(excl)>nslots/3: app.append('more than 1/3 of slots excluded: %d of %d'%(len(excl),nslots))
    if len(rows)<nslots: app.append('ledger holds %d of %d slots'%(len(rows),nslots))
    out['apparatus']=app
    if app: out['outcome']='APPARATUS'; return out
    fits={k:fit_reading(usable,k) for k in ('rate','hpcs','cores')}
    out['fits']=fits; out['outcome_by_reading']={k:outcome(f) for k,f in fits.items()}
    out['outcome']=out['outcome_by_reading']['rate']
    pr,ph,pc=fits['rate'],fits['hpcs'],fits['cores']
    out['product_vs_sum']=dict(P_rate=pr['P'],P_hpcs_plus_P_cores=ph['P']+pc['P'],
        diff=pr['P']-(ph['P']+pc['P']),width_if_independent=math.sqrt(pr['P_width']**2+ph['P_width']**2+pc['P_width']**2),
        note='hpcs and cores share R15 and the slot, so the independent width is an upper-ish guide, not exact')
    out['eps_look']=dict(value=pr['P']*6,width=pr['P_width']*6,bound_2w=(pr['P']+2*pr['P_width'])*6,
        meaning='cost of the routine 6 polls/min, as a fraction of the rate; the coin product carries (1 - eps_look)')
    return out

def selftest():
    import random
    random.seed(7); seed=json.load(open(CLAIM))['design']['seed']; ok=0
    def mk(Ptrue, bend=0.0):
        rows=[]
        for k in range(32):
            d=arm_of(seed,k); her=2.0+random.gauss(0,0.1)
            cores=11.0*(1-Ptrue*d*0.5)-0.3*(her-2); hp=550.0*(1-Ptrue*d*0.5)*(1+(bend if d==30 else 0))
            rate=hp*cores+random.gauss(0,15)
            rows.append(dict(slot=k,dose_per_min=d,achieved_per_min=float(d),R15=rate,dt=900.0,xmrig_uptime=99999,
                paused_at_end=False,miner_cores=cores,her_cores=her,miner_pids_same=True))
        return rows
    # the null is a RATE, not one draw: two 2-width tests -> about 9% of nulls leave DOES_NOT_RESOLVE by chance
    outs=[score(mk(0.0),seed)['outcome'] for _ in range(300)]; fr=1-outs.count('DOES_NOT_RESOLVE')/300.0
    print('null false-verdict rate %.3f (HOLDS %d, NOT_A_LINE %d of 300)'%(fr,outs.count('HOLDS'),outs.count('NOT_A_LINE')))
    assert 0.02<=fr<=0.20,fr; ok+=1
    o=score(mk(0.001),seed); assert o['outcome']=='HOLDS',o.get('outcome'); ok+=1
    o=score(mk(0.0005,bend=0.08),seed); assert o['outcome']=='NOT_A_LINE',o.get('outcome'); ok+=1
    r=mk(0.0); r=r[:20]; o=score(r,seed); assert o['outcome']=='APPARATUS'; ok+=1
    r=mk(0.0); r[3]['dose_per_min']=(r[3]['dose_per_min']+30)%150 or 30; o=score(r,seed); assert 3 in o['arm_mismatch_slots']; ok+=1
    print('selftest %d/5'%ok)

if __name__=='__main__':
    if '--selftest' in sys.argv: selftest(); sys.exit(0)
    claim=json.load(open(CLAIM)); seed=claim['design']['seed']
    rows=[json.loads(l) for l in open(LEDGER) if l.strip()]
    print(json.dumps(score(rows,seed),indent=1,default=str))
