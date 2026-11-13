import json,math,random,collections,sys
from common import *
def wilson(k,n,z=1.96):
    if n==0: return [None,None]
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d; return [round(c-h,3),round(c+h,3)]
def gold():
    g=json.load(open(S+'/data/gold_items.json')); return {i['id']:i for i in g}
def agree_vec(rows,G,split):
    """per code: dict id->(agree 0/1, status, reason, flag)"""
    R={r['id']:r for r in rows if r['set']=='gold'}
    V={c:{} for c in CODES}
    for i,g in G.items():
        if g['split']!=split or not g.get('text') or i not in R: continue
        for c in CODES:
            l=R[i]['labels'][c]; V[c][i]=(int((l['status']=='PRESENT')==(c in g['codes'])),l['status'],l['reason'],l['flag'])
    return V
def table(V,G,split):
    out={}
    for c in CODES:
        v=V[c]; n=len(v); k=sum(x[0] for x in v.values()); prev=sum(1 for i in v if c in G[i]['codes'])
        ct=collections.Counter(x[2] for x in v.values() if x[1]=='CANNOT_TELL' and x[3]=='ok'); 
        out[c]={'n':n,'agree':k,'rate':round(k/n,3) if n else None,'wilson95':wilson(k,n),'gold_present':prev,'majority_class_rate':round(max(prev,n-prev)/n,3) if n else None,
         'decided_share':round(sum(1 for x in v.values() if x[1] in('PRESENT','ABSENT'))/n,3) if n else None,
         'status_counts':dict(collections.Counter(x[1] for x in v.values())),'cannot_tell_by_reason':dict(ct),
         'ungrounded_to_CT_METHOD_UNSTATED':sum(1 for x in v.values() if x[3]=='ungrounded'),'parse_failed':sum(1 for x in v.values() if x[3]=='parse_failed')}
    return out
def paired(Va,Vb,B=2000,seed=7):
    """a minus b; returns per-code and pooled"""
    rng=random.Random(seed); ids=sorted(set.intersection(*[set(Va[c])&set(Vb[c]) for c in CODES]))
    res={}
    D={c:[Va[c][i][0]-Vb[c][i][0] for i in ids] for c in CODES}
    for c in CODES:
        d=D[c]; res[c]={'n':len(d),'mean_diff':round(sum(d)/len(d),4),'a_right_b_wrong':sum(1 for x in d if x==1),'a_wrong_b_right':sum(1 for x in d if x==-1)}
    pooled=[sum(D[c][k] for c in CODES)/7 for k in range(len(ids))]
    bs={c:[] for c in CODES}; bp=[]
    for _ in range(B):
        idx=[rng.randrange(len(ids)) for _ in ids]
        for c in CODES: bs[c].append(sum(D[c][k] for k in idx)/len(idx))
        bp.append(sum(pooled[k] for k in idx)/len(idx))
    q=lambda a:[round(sorted(a)[int(.025*B)],4),round(sorted(a)[int(.975*B)-1],4)]
    for c in CODES: res[c]['ci95']=q(bs[c])
    res['pooled']={'n':len(ids),'mean_diff':round(sum(pooled)/len(pooled),4),'ci95':q(bp),'flips_a_right_b_wrong':sum(res[c]['a_right_b_wrong'] for c in CODES),'flips_a_wrong_b_right':sum(res[c]['a_wrong_b_right'] for c in CODES)}
    return res
def pooled_rate(V): 
    k=sum(x[0] for c in CODES for x in V[c].values()); n=sum(len(V[c]) for c in CODES); return {'agree':k,'n':n,'rate':round(k/n,3) if n else None,'wilson95':wilson(k,n)}
