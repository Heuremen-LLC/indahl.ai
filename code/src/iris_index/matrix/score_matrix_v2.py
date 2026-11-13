"""score_matrix_v2.py [dir]: v2 cells per model. Positive control gates the order carrier; letter bias printed beside it."""
import json, os, sys, re, collections, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); L='ABCD'
M4={q['id']:q for q in json.load(open(os.path.join(HERE,'inputs/mcq4_200.json')))}; PC={q['id']:q for q in json.load(open(os.path.join(HERE,'inputs/mcq4_poscontrol.json')))}
import re as _re
def parse_letter(ans,shown,n):
    # addendum 3a: bare letter, letter + . ) : or space, or exact option text (shown order); else None
    s=str(ans).strip()
    m=_re.fullmatch(r'([A-Za-z])(?:[.):]\s*.*|\s+.*)?',s,_re.S)
    if m and m.group(1).upper() in L[:n]: return m.group(1).upper()
    low=[str(t).strip().lower() for t in shown]
    if s.lower() in low and low.count(s.lower())==1: return L[low.index(s.lower())]
    return None
def ci(x,B=2000):
    rng=np.random.default_rng(20261025)   # addendum 3e
    x=np.asarray([v for v in x if v==v],float)
    if not len(x): return (float('nan'),)*3+(0,)
    i=rng.integers(0,len(x),(B,len(x))); m=x[i].mean(1); lo,hi=np.percentile(m,[2.5,97.5]); return (x.mean(),lo,hi,len(x))
def oc(t):
    if t[3]==0: return 'CANNOT_TELL'
    s='ABOVE' if t[1]>0 else 'BELOW' if t[2]<0 else 'CONSISTENT'; return s+(' MARGINAL' if s!='CONSISTENT' and min(abs(t[1]),abs(t[2]))<0.01 else '')
def obj(raw):
    m=re.search(r'\{.*?\}',raw or '',re.S)
    if not m: return None,'NO_JSON'
    try: return json.loads(m.group(0)),'PARSED'
    except Exception:
        m=re.search(r'\{.*\}',raw,re.S)
        try: return json.loads(m.group(0)),'PARSED'
        except Exception: return None,'UNPARSED'
def content(r):
    if r.get('error'): return None,'ERROR'
    if not (r.get('raw') or '').strip(): return None,'EMPTY'
    o,st=obj(r['raw'])
    if st!='PARSED' or not isinstance(o,dict): return None,st
    if 'answer' not in o: return None,'NO_ANSWER_FIELD'
    it=M4.get(r['id']) or PC.get(r['id'])
    a=parse_letter(o['answer'],[it['options'][i] for i in r['order']] if it else [],len(r['order']))
    if a is None: return None,'UNPARSED'
    return r['order'][L.index(a)],'PARSED'
def arm(d,a):
    p=os.path.join(d,a+'.jsonl'); return {r['id']:r for r in map(json.loads,open(p))} if os.path.exists(p) else {}
def score(d):
    R={a:arm(d,a) for a in ('mcq4_A','mcq4_A_copy','mcq4_rev','mcq4_rot','mcq4_B','pc_A','pc_rev','mcq4_batch8')}
    C={a:{k:content(r) for k,r in v.items()} for a,v in R.items() if a!='mcq4_batch8'}
    term={a:dict(collections.Counter(st for _,st in v.values())) for a,v in C.items()}
    V={a:{k:c for k,(c,st) in v.items() if st=='PARSED'} for a,v in C.items()}
    A,Ac=V['mcq4_A'],V['mcq4_A_copy']; out={'terminations':term}
    acc=lambda M,Q,k: float(M[k]==Q[k]['gold']) if k in M else float('nan')
    out['acc_A']=ci([acc(A,M4,k) for k in M4]); out['copy_disagree']=ci([float(A[k]!=Ac[k]) for k in A if k in Ac])
    pcacc=lambda a: [float(V[a][k]==R[a][k]['order'][0]) if k in V[a] else float('nan') for k in PC]   # correct = the option shown first
    out['pc_acc_A']=ci(pcacc('pc_A')); out['pc_acc_rev']=ci(pcacc('pc_rev'))
    out['pc_flip']=ci([float(V['pc_A'][k]!=V['pc_rev'][k]) for k in PC if k in V['pc_A'] and k in V['pc_rev']])
    letters=collections.Counter(L[R['mcq4_A'][k]['order'].index(c)] for k,c in A.items())
    out['top_letter_share']=max(letters.values())/max(1,sum(letters.values())); out['letters']=dict(letters)
    for car in ('mcq4_rev','mcq4_rot','mcq4_B'):
        X=V[car]; out[car+'_flip_minus_floor']=ci([float(A[k]!=X[k])-float(A[k]!=Ac[k]) for k in A if k in X and k in Ac])
        out[car+'_acc_change']=ci([acc(X,M4,k)-acc(A,M4,k) for k in M4 if k in X and k in A])
    kg=out['copy_disagree'][3]>=150 and out['copy_disagree'][0]<=0.05
    pcok=out['pc_acc_A'][0]>=0.8 and out['pc_acc_rev'][0]>=0.8
    na=term['mcq4_A'].get('NO_ANSWER_FIELD',0)/max(1,sum(term['mcq4_A'].values()))
    out['known_good']=bool(kg); out['positive_control_ok']=bool(pcok); out['no_answer_share']=na
    o={k:oc(out[k]) for k in ('mcq4_rev_flip_minus_floor','mcq4_rot_flip_minus_floor','mcq4_B_flip_minus_floor')}
    if not pcok: o['mcq4_rev_flip_minus_floor']=o['mcq4_rot_flip_minus_floor']='CANNOT_TELL (positive control < 80%)'
    if not kg or na>0.10: o={k:'CANNOT_TELL (known-good or answer field failed)' for k in o}
    out['outcomes']=o
    d4=[];d6=[];wl=0;nb=0
    for b in R['mcq4_batch8'].values():
        nb+=1; ob,st=obj(b.get('raw','')); ans=ob.get('answers') if isinstance(ob,dict) else None
        if isinstance(ans,dict):   # addendum v2-2: item-keyed answers accepted in item order (granite, v1)
            ks=sorted(ans,key=lambda k: int(''.join(ch for ch in str(k) if ch.isdigit()) or 0)); ans=[ans[k] for k in ks]; out.setdefault('M6c_dict_answers',0); out['M6c_dict_answers']+=1
        if not isinstance(ans,list): continue
        if len(ans)!=len(b['items']): wl+=1; continue
        let=[parse_letter(x,M4[q]['options'] if q in M4 else [],4) or '?' for x,q in zip(ans,b['items'])]; per=[]
        for q,lt in zip(b['items'],let):
            if q in A and q in Ac and lt in L: per.append(float(L.index(lt)!=A[q])-float(A[q]!=Ac[q]))
        if per: d4.append(np.mean(per))
        try: d6.append(float(int(ob.get('count_A'))!=let.count('A')))
        except Exception: d6.append(float('nan'))
    out['M4_batch_flip_minus_floor']=ci(d4); out['M6_selfcount_wrong_rightlength']=ci(d6); out['M6b_wrong_length']=(wl,nb)
    return out

def trunc_share(d,arm='mcq4_A'):
    p=os.path.join(d,arm+'.jsonl')
    if not os.path.exists(p): return (0,0)
    rs=[json.loads(l) for l in open(p)]; return (sum(1 for r in rs if r.get('done_reason')=='length'),len(rs))
if __name__=='__main__':
    base=sys.argv[1] if len(sys.argv)>1 else os.path.join(HERE,'results_v2')
    res={m:score(os.path.join(base,m)) for m in sorted(os.listdir(base)) if os.path.isdir(os.path.join(base,m))}
    for m,v in res.items():
        k,n=trunc_share(os.path.join(base,m)); v['truncated_A']=(k,n)
        if n and k/n>0.10: v['outcomes']={c:'CANNOT_TELL (truncated under our settings: %d of %d replies hit the length limit)'%(k,n) for c in v['outcomes']}
    json.dump(res,open(os.path.join(HERE,'matrix_v2_'+os.path.basename(base)+'.json'),'w'),indent=1,default=float)
    for m,v in res.items(): print(m,'trunc %s'%(v['truncated_A'],),'kg',v['known_good'],'pc',v['positive_control_ok'],'pc_flip %.2f'%v['pc_flip'][0],'top_letter %.2f'%v['top_letter_share'],v['outcomes'],'M6b',v['M6b_wrong_length'])
