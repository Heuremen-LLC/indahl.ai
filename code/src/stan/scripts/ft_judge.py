"""Apply scripts/ft_keys.py to the retrieval; write ceiling_ft/judgments.jsonl, summary.json, SUMMARY.md, bones_sample_20.json."""
import json,re,sys,random,math,collections
sys.path.insert(0,'/Users/heuremen/bones-forge/stan/scripts')
from ft_worklist import *
from ft_keys import K
O=S+'/ceiling_ft'
r=json.load(open(O+'/retrieval.json')); C=json.load(open(O+'/chunks.json')); ex=json.load(open(O+'/extract_log.json'))['papers']
J=[json.loads(l) for l in open(S+'/ceiling/judgments.jsonl')]; J=[j for j in J if j['id'] in r]
assert len(J)==196
TX={i:open(O+'/text/%s.txt'%i).read() for i in r}
TN={i:norm(t) for i,t in TX.items()}; TS={i:sq(t) for i,t in TX.items()}
CS={i:{c['id']:(sq(c['text']),norm(c['text']),c['text']) for c in C[i]} for i in r}
def find(i,key):
    """returns (in_full, [chunk ids])"""
    if key.startswith('n:'):
        n=key[2:]; vs=[n]
        m=n.rstrip('%')
        if m!=n: vs.append(m)
        if '.' in m and m.endswith('0'): vs.append(m.rstrip('0').rstrip('.'))
        return any(numfind(v,TN[i]) for v in vs), [c for c,v in CS[i].items() if any(numfind(w,v[1]) for w in vs)]
    alts=[a for a in key.split('|')]; ch=set(); full=False
    for a in alts:
        s=sq(a)
        if s in TS[i]: full=True
        ch|={c for c,v in CS[i].items() if s in v[0]}
    return full, sorted(ch)
rows=[]
for idx,j in enumerate(J):
    i,code=j['id'],j['code']; k=K[idx]; top=[x['chunk'] for x in r[i][code]]
    row={'idx':idx,'pair':'%s_%s'%(i,code),'id':i,'code':code,'note':j['note_used'],'top6':top}
    if k is None:
        row.update(verdict='CANNOT_TELL',reason='NO_NOTE' if not j['note_used'] else 'NO_FINDABLE_EVIDENCE',evidence=None,chunks_in_top6=[],chunks_elsewhere=[],why='note names no figure, phrase or table that can be searched')
    elif isinstance(k,str):
        row.update(verdict='NOT_IN_TEXT',reason=None,evidence=k[3:],chunks_in_top6=[],chunks_elsewhere=[],why=k[3:])
    else:
        res=[(s,)+find(i,s) for s in k]
        intop=[c for s,f,ch in res for c in ch if c in top]; el=[c for s,f,ch in res for c in ch if c not in top]
        if not all(f for s,f,ch in res): v='NOT_IN_TEXT'; why='not in extracted text: '+'; '.join(s for s,f,ch in res if not f)
        elif all(any(c in top for c in ch) for s,f,ch in res): v='IN'; why='every key string is in a top-6 chunk'
        else: v='OUT'; why='in text but not in top 6: '+'; '.join(s for s,f,ch in res if not any(c in top for c in ch))
        row.update(verdict=v,reason=None,evidence=k,chunks_in_top6=sorted(set(intop)),chunks_elsewhere=sorted(set(el)),why=why,per_key=[{'key':s,'in_text':f,'chunks':ch} for s,f,ch in res])
    rows.append(row)
with open(O+'/judgments.jsonl','w') as f:
    for x in rows: f.write(json.dumps(x)+'\n')
# scrambled share
def numrun_share(t):
    tot=0;bad=0
    for ln in t.replace('\f','\n').split('\n'):
        tot+=len(ln); tk=ln.split()
        if len(tk)>=6 and sum(1 for w in tk if re.fullmatch(r'[-+−(]?[\d.,%)±eE]+',w))/len(tk)>=0.7: bad+=len(ln)
    return bad/max(tot,1)
paper={i:{'chars':ex[i]['chars'],'pages':ex[i]['pages'],'numrun_share':round(numrun_share(TX[i]),4)} for i in r}
for i in paper: paper[i]['scrambled']=paper[i]['numrun_share']>=0.08
def wilson(k,n,z=1.96):
    if n==0: return (None,None)
    p=k/n; d=1+z*z/n; c=p+z*z/(2*n); h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)); return (round((c-h)/d,3),round((c+h)/d,3))
summ={'pass_line':0.60,'min_decided':10,'codes':{}}
for code in ['F1','F2','F3','F4','F5','F6','F7','ALL']:
    R=[x for x in rows if code=='ALL' or x['code']==code]; c=collections.Counter(x['verdict'] for x in R)
    d=c['IN']+c['OUT']; lo,hi=wilson(c['IN'],d)
    st='untested' if d<10 else ('pass' if (c['IN']/d)>=0.60 else 'fail (retrieval-limited)')
    ct=collections.Counter(x['reason'] for x in R if x['verdict']=='CANNOT_TELL')
    ps=[x['id'] for x in R]; up=set(ps)
    summ['codes'][code]={'pairs':len(R),'IN':c['IN'],'OUT':c['OUT'],'NOT_IN_TEXT':c['NOT_IN_TEXT'],'CANNOT_TELL':c['CANNOT_TELL'],'decided':d,
        'IN_over_decided':round(c['IN']/d,3) if d else None,'wilson95':[lo,hi],'reading':st,
        'papers':len(up),'chars_median':int(sorted(paper[p]['chars'] for p in up)[len(up)//2]),'chars_min':min(paper[p]['chars'] for p in up),
        'scrambled_papers':sum(paper[p]['scrambled'] for p in up),'scrambled_pair_share':round(sum(paper[p]['scrambled'] for p in ps)/len(ps),3)}
chars=[v['chars'] for v in paper.values()]
summ['extraction']={'papers':len(paper),'chars_total':sum(chars),'chars_median':sorted(chars)[len(chars)//2],'chars_min':min(chars),'chars_max':max(chars),
  'scrambled_papers':sum(v['scrambled'] for v in paper.values()),'scrambled_def':'paper flagged when lines of >=6 tokens with >=70% numeric tokens hold >=8% of its characters (operational definition set while writing the script)',
  'per_paper':paper}
json.dump(summ,open(O+'/summary.json','w'),indent=1)
# seeded sample
dec=[x for x in rows if x['verdict'] in ('IN','OUT')]
seed=int('92cfe944',16); samp=random.Random(seed).sample(dec,20)
out=[]
for x in samp:
    out.append({'pair':x['pair'],'code':x['code'],'note':x['note'],'evidence':x['evidence'],'judge_verdict':x['verdict'],'chunks_in_top6_with_evidence':x['chunks_in_top6'],
      'top6':[{'chunk':c,'text':CS[x['id']][c][2][:1500]} for c in x['top6']]})
json.dump({'seed':seed,'seed_source':"int('92cfe944',16)",'n':20,'sample':out},open(O+'/bones_sample_20.json','w'),indent=1)
print(json.dumps({k:{kk:vv for kk,vv in v.items()} for k,v in summ['codes'].items()},indent=0)[:3500])
print(summ['extraction']['papers'],summ['extraction']['chars_median'],summ['extraction']['scrambled_papers'])

# sensitivity: IN if ANY key is in top 6 (descriptive only, not the pre-registered reading)
sens={}
for code in ['F1','F2','F3','F4','F5','F6','F7','ALL']:
    R=[x for x in rows if (code=='ALL' or x['code']==code) and x['verdict'] in ('IN','OUT')]
    a=sum(1 for x in R if x['verdict']=='IN' or any(any(c in x['top6'] for c in k['chunks']) for k in x['per_key']))
    sens[code]={'decided':len(R),'IN_any_key':a,'share':round(a/len(R),3) if R else None,'wilson95':list(wilson(a,len(R)))}
summ['sensitivity_any_key']=sens
json.dump(summ,open(O+'/summary.json','w'),indent=1)
L=['# STAN A full-text retrieval ceiling (dev only)','',
'Pre-registered in PLAN_A_CEILING.md. Settings frozen (pypdf 6.21.1, 1,200-token Qwen3 chunks, 150 overlap, BM25 rank_bm25 0.2.2, query = Test + PRESENT + ABSENT lines, top 6). Pass line IN/(IN+OUT) >= 0.60, Wilson 95% lower bound beside it, untested under 10 decided pairs.',
'Judge: Claude Sonnet 5.5, same model family as the abstract-ceiling judge, one reader who sees the note (not blind to the label). Prompt: ceiling_ft/judge_prompt.txt. Bones second read on the seeded 20 (bones_sample_20.json) is NOT yet done, so no disagreement count exists.',
'Unit: 196 (dev paper, code) pairs from ceiling/judgments.jsonl whose paper has full text of at least 2,000 characters (92 papers). 4 of the 200 abstract-ceiling pairs have no usable full text and are out. Test split not read.','',
'| Code | Pairs | IN | OUT | NOT_IN_TEXT | CANNOT_TELL | IN/(IN+OUT) | Wilson 95% | Reading | Scrambled-paper share of pairs |','|---|---|---|---|---|---|---|---|---|---|']
for c,v in summ['codes'].items():
    L.append('| %s | %d | %d | %d | %d | %d | %s | %s | %s | %.3f |'%(c,v['pairs'],v['IN'],v['OUT'],v['NOT_IN_TEXT'],v['CANNOT_TELL'],v['IN_over_decided'],v['wilson95'],v['reading'],v['scrambled_pair_share']))
e=summ['extraction']
L+=['','NOT_IN_TEXT is the extraction ceiling per code (column above): evidence in a table, figure, released file or the recount own run that the PDF text does not hold. Many are by construction (released files, recount own runs, digitized figure values).','',
'## Extraction','','%d papers, %d characters total, median %d per paper, min %d, max %d. Papers flagged scrambled (%s): %d of %d. Per paper numbers in summary.json.'%(e['papers'],e['chars_total'],e['chars_median'],e['chars_min'],e['chars_max'],e['scrambled_def'],e['scrambled_papers'],e['papers']),'',
'## Sensitivity (descriptive, not the pre-registered reading)','','IN if any one key string (not all) is in the top 6:','','| Code | decided | IN any key | share | Wilson 95% |','|---|---|---|---|---|']
for c,v in sens.items(): L.append('| %s | %d | %d | %s | %s |'%(c,v['decided'],v['IN_any_key'],v['share'],v['wilson95']))
L+=['','## Limits','','CANNOT_TELL is large for F4 because most F4 notes are pure absences (run dates not printed, no circuits released) that name nothing to search. Per the file, those are CANNOT_TELL, so F4 is untested. Several keys were chosen by the judge reading the note (scripts/ft_keys.py); the Bones read on the seeded 20 is the check. Scrambled-text flag is an operational definition set while writing the script.']
open(O+'/SUMMARY.md','w').write('\n'.join(L)+'\n')
