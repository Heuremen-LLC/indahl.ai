"""score_matrix.py [results_dir]: one row per model, six failure-mode cells, four outcomes each against the cell's own floor."""
import json, os, sys, csv, re, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); L='ABCD'
GOLD=list(csv.DictReader(open(os.path.join(HERE,'inputs/nep_gold.csv'))))
GNP={r['comment_id']:r['is_no_persona_gold'].strip().lower()=='true' for r in GOLD}
MCQ={q['id']:q for q in json.load(open(os.path.join(HERE,'inputs/mcq_200.json')))}
def rows(d,arm):
    p=os.path.join(d,arm+'.jsonl'); return {r['id']:r for r in map(json.loads,open(p))} if os.path.exists(p) else {}
def jparse(raw):
    if not raw or not raw.strip(): return None,'EMPTY'
    m=re.search(r'\{.*\}',raw,re.S)
    try: return json.loads(m.group(0) if m else raw),'PARSED'
    except Exception: return None,'UNPARSED'
def outcome(r):
    if r.get('error'): return None,'ERROR'
    return jparse(r.get('raw',''))
def nep_label(o):
    if not isinstance(o,dict): return None
    np_=o.get('no_persona') is True or str(o.get('intent','')).strip().lower() in ('no-persona','no persona','none','null')
    return ('NP',) if np_ else tuple(str(o.get(k,'')).strip().lower() for k in ('intent','primary_driver','value_orientation','affect'))
def content(r):
    o,st=outcome(r)
    if st!='PARSED' or not isinstance(o,dict): return None,st
    if 'answer' not in o: return None,'NO_ANSWER_FIELD'
    a=parse_letter(o.get('answer',''),[MCQ[r['id']]['options'][i] for i in r['order']],len(r['order']))
    if a is None: return None,'UNPARSED'
    return r['order'][L.index(a)],st
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
    rng=np.random.default_rng(20261025)   # addendum 3e: reseeded per call
    x=np.asarray(x,float); x=x[~np.isnan(x)]
    if len(x)==0: return (np.nan,np.nan,np.nan,0)
    i=rng.integers(0,len(x),(B,len(x))); m=x[i].mean(1); lo,hi=np.percentile(m,[2.5,97.5]); return (x.mean(),lo,hi,len(x))
def oc(lo,hi,floor_hi=0.0):
    if np.isnan(lo): return 'CANNOT_TELL'
    s='ABOVE' if lo>0 else 'BELOW' if hi<0 else 'CONSISTENT'
    return s+(' MARGINAL' if s!='CONSISTENT' and min(abs(lo),abs(hi))<0.01 else '')
def score(d):
    R={a:rows(d,a) for a in ('nep_abstain','nep_abstain_copy','mcq_A','mcq_A_copy','mcq_A_rev','mcq_B','mcq_batch8')}
    term={a:{} for a in R}
    for a,v in R.items():
        for r in v.values():
            st=outcome(r)[1]
            if st=='PARSED' and a.startswith('mcq') and a!='mcq_batch8': st=content(r)[1]
            term[a][st]=term[a].get(st,0)+1
    out={'terminations':term}
    # M1 over-attribution and false abstention (abstain arm)
    lab={k:nep_label(outcome(r)[0]) for k,r in R['nep_abstain'].items()}
    oa=[float(lab[k]!=('NP',)) if lab[k] is not None else np.nan for k in lab if GNP.get(k)]
    fa=[float(lab[k]==('NP',)) if lab[k] is not None else np.nan for k in lab if GNP.get(k) is False]
    out['M1_over_attribution']=ci(oa); out['M1_false_abstention']=ci(fa)
    # M2 copy floors
    c1={k:nep_label(outcome(r)[0]) for k,r in R['nep_abstain_copy'].items()}
    nd=[float(lab[k]!=c1[k]) for k in lab if k in c1 and lab[k] is not None and c1[k] is not None]
    A={k:content(r)[0] for k,r in R['mcq_A'].items()}; Ac={k:content(r)[0] for k,r in R['mcq_A_copy'].items()}
    md=[float(A[k]!=Ac[k]) for k in A if k in Ac and A[k] is not None and Ac[k] is not None]
    out['M2_copy_disagree_nep']=ci(nd); out['M2_copy_disagree_mcq']=ci(md)
    kg=(len(md)>=150 and np.mean(md)<=0.05) if md else False; out['known_good']=bool(kg)
    out['known_good_reason']='ok' if kg else ('too few usable copy pairs: %d of %d (<150)'%(len(md),len(A)) if len(md)<150 else 'copy disagreement %.3f > 0.05'%np.mean(md))
    # addendum 3b: NepPlural drop share
    nep_bad=sum(1 for r in R['nep_abstain'].values() if outcome(r)[1]!='PARSED' or r.get('done_reason')=='length')
    out['nep_drop_share']=nep_bad/max(1,len(R['nep_abstain']))
    out['M1_n']='%d of %d gold no-persona, %d of %d persona'%(out['M1_over_attribution'][3],sum(1 for k in lab if GNP.get(k)),out['M1_false_abstention'][3],sum(1 for k in lab if GNP.get(k) is False))
    # M3 option order: flip minus copy disagreement, per item
    Rv={k:content(r)[0] for k,r in R['mcq_A_rev'].items()}
    d3=[float(A[k]!=Rv[k])-float(A[k]!=Ac[k]) for k in A if k in Rv and k in Ac and None not in (A[k],Rv[k],Ac[k])]
    out['M3_order_flip_minus_floor']=ci(d3)
    acc=lambda M,k: float(M.get(k)==MCQ[k]['gold']) if k in M else np.nan
    out['M3_acc_rev_minus_A']=ci([acc(Rv,k)-acc(A,k) for k in A if k in Rv])
    # M5 format
    Bm={k:content(r)[0] for k,r in R['mcq_B'].items()}
    out['M5_acc_B_minus_A']=ci([acc(Bm,k)-acc(A,k) for k in A if k in Bm])
    out['M5_flip_minus_floor']=ci([float(A[k]!=Bm[k])-float(A[k]!=Ac[k]) for k in A if k in Bm and k in Ac and None not in (A[k],Bm[k],Ac[k])])
    # M4 batch and M6 self-count (cluster = batch)
    d4=[]; d6=[]; dict4=[]; dict6=[]; drop={'not_parsed':0,'no_answer_list':0,'wrong_length':0}
    for b in R['mcq_batch8'].values():
        o,st=outcome(b); ans=o.get('answers') if isinstance(o,dict) else None
        if st!='PARSED': drop['not_parsed']+=1; continue
        if isinstance(ans,dict):
            drop['item_keyed_dict']=drop.get('item_keyed_dict',0)+1
            vals=list(ans.values())
            if len(vals)==len(b['items']):
                lt=[parse_letter(x,MCQ[q]['options'],2) or '?' for x,q in zip(vals,b['items'])]
                per=[float(l!=L[A[q]])-float(A[q]!=Ac[q]) for q,l in zip(b['items'],lt) if l in 'AB' and A.get(q) is not None and Ac.get(q) is not None]
                if per: dict4.append(np.mean(per))
                try: dict6.append(float(int(o.get('count_A'))!=sum(1 for x in lt if x=='A')))
                except Exception: pass
            continue
        if not isinstance(ans,list): drop['no_answer_list']+=1; continue
        if len(ans)!=len(b['items']): drop['wrong_length']+=1; continue
        letters=[parse_letter(x,[MCQ[q]['options'][0],MCQ[q]['options'][1]],2) or '?' for x,q in zip(ans,b['items'])]
        per=[]
        for q,lt in zip(b['items'],letters):
            if lt not in 'AB' or A.get(q) is None or Ac.get(q) is None: continue
            per.append(float(lt!=L[A[q]] if A[q] is not None else 0)-float(A[q]!=Ac[q]))   # single order = identity order
        if per: d4.append(np.mean(per))
        try: d6.append(float(int(o.get('count_A'))!=sum(1 for x in letters if x=='A')))
        except Exception: d6.append(np.nan)
    out['M4_M6_batches_dropped']=drop
    if dict4: out['dict_bound']={'M4':ci(dict4),'M6':ci(dict6)}   # addendum 3d: labelled bound, not a resolved cell
    out['M4_batch_flip_minus_floor']=ci(d4); out['M6_selfcount_wrong']=ci(d6)
    out['outcomes']={k:oc(v[1],v[2]) for k,v in out.items() if isinstance(v,tuple) and k not in ('M1_over_attribution','M1_false_abstention','M2_copy_disagree_nep','M2_copy_disagree_mcq','M6_selfcount_wrong')}
    if not kg: out['outcomes']={k:'CANNOT_TELL (known-good failed)' for k in out['outcomes']}
    na=term['mcq_A'].get('NO_ANSWER_FIELD',0)/max(1,sum(term['mcq_A'].values()))
    out['mcq_no_answer_share']=na
    if na>0.10: out['outcomes']={k:'CANNOT_TELL (no answer field in %.0f%% of MCQ replies under our settings)'%(100*na) for k in out['outcomes']}; out['known_good']=False
    out['M6b_wrong_length_batches']=drop['wrong_length']
    nd=sum(drop.values())
    if nd>5 and 'M4_batch_flip_minus_floor' in out['outcomes']: out['outcomes']['M4_batch_flip_minus_floor']='CANNOT_TELL (%d of 25 batches dropped)'%nd   # addendum 3e
    return out
if __name__=='__main__':
    base=sys.argv[1] if len(sys.argv)>1 else os.path.join(HERE,'results')
    allr={m:score(os.path.join(base,m)) for m in sorted(os.listdir(base)) if os.path.isdir(os.path.join(base,m))}
    json.dump(allr,open(os.path.join(base,'..','matrix_'+os.path.basename(base)+'.json'),'w'),indent=1,default=float)
    for m,v in allr.items():
        print(m,'known-good',v['known_good'],{k:('%.3f [%.3f, %.3f] n%d'%v[k]) for k in v if k.startswith('M') and isinstance(v[k],tuple)},'dropped',v['M4_M6_batches_dropped']); print('   ',v['outcomes'])
