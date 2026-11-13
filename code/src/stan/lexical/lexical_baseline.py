"""Lexical baseline, PLAN_A_v2 section 4. Cues = content words of the code's PRESENT line (lowercased, stop words removed).
PRESENT when any cue appears in the top 6 retrieved chunks for that code, else ABSENT. Run on gold dev, codes F1 F2 F6 F3."""
import json,re,sys,math
sys.path.insert(0,'/Users/heuremen/bones-forge/stan/scripts'); from common import S,STD
STOP=set("a an the of or and to in on at by for from with as is are was were be been it its this that these those than then which who whom whose when where what not no nor but if so such each every any all one at least same".split())
def wil(k,n):
    if n==0: return None
    z=1.96;p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [max(0.0,round(c-h,3)),min(1.0,round(c+h,3))]
def cues(code):
    c=[x for x in STD['claim_codes'] if x['code']==code][0]
    return sorted({w for w in re.findall(r"[a-z]+",c['present_when'].lower()) if w not in STOP and len(w)>2})
ret=json.load(open(S+'/ceiling_ft/retrieval.json')); ch=json.load(open(S+'/ceiling_ft/chunks.json'))
gold={x['id']:x for x in json.load(open(S+'/data/gold_items.json'))}
out={}
for code in ['F1','F2','F6','F3']:
    cu=cues(code); fl=un=pf=pu=0
    for pid in sorted(ret):
        cm={c['id']:c['text'].lower() for c in ch[pid]}
        words=set(re.findall(r"[a-z]+",' '.join(cm[r['chunk']] for r in ret[pid][code])))
        pres=any(w in words for w in cu)
        if code in gold[pid]['codes']: fl+=1; pf+=pres
        else: un+=1; pu+=pres
    out[code]={'cues':cu,'recall_flagged':[pf,fl,wil(pf,fl)],'false_flag_unflagged':[pu,un,wil(pu,un)]}
    print(code,'cues',cu); print('   PRESENT on flagged %d/%d %s | on unflagged %d/%d %s'%(pf,fl,wil(pf,fl),pu,un,wil(pu,un)))
json.dump(out,open(S+'/lexical/dev_result.json','w'),indent=1)
