"""Full-text retrieval ceiling, step 1b: chunk (1200 Qwen3 tokens, 150 overlap), BM25, top 6 per code.
Text comes from scripts/ft_extract.py (pypdf 6.21.1, pages joined with form feed). Run with ~/bones-forge/venv/bin/python."""
import json,re,sys,os
sys.path.insert(0,'/Users/heuremen/bones-forge/stan/scripts')
from common import code_block,CODES
S='/Users/heuremen/bones-forge/stan'; OUT=S+'/ceiling_ft'
from transformers import AutoTokenizer
import transformers,rank_bm25,importlib.metadata as md
TOK=AutoTokenizer.from_pretrained('Qwen/Qwen3-1.7B')
CH,OV,K=1200,150,6
def chunks(text,pid):
    # token offsets over the whole text; page number = count of form feeds before chunk start
    enc=TOK(text,add_special_tokens=False,return_offsets_mapping=True)
    ids=enc['input_ids']; off=enc['offset_mapping']; n=len(ids); res=[]; s=0; k=0
    while s<n:
        e=min(s+CH,n); a=off[s][0]; b=off[e-1][1]
        res.append({'id':'%s_c%02d_p%d'%(pid,k,text.count('\f',0,a)+1),'start_tok':s,'text':text[a:b]})
        k+=1
        if e>=n: break
        s=e-OV
    return res
def toks(t): return re.findall(r'\w+',t.lower())
def query(code):
    cb=code_block(code); keep=[l for l in cb.split('\n') if l.startswith(('Test:','PRESENT when:','ABSENT when:'))]
    return '\n'.join(keep)
def retrieve(pid):
    text=open('%s/text/%s.txt'%(OUT,pid)).read(); cs=chunks(text,pid)
    bm=rank_bm25.BM25Okapi([toks(c['text']) for c in cs]); res={}
    for code in CODES:
        sc=bm.get_scores(toks(query(code)))
        top=sorted(range(len(cs)),key=lambda i:(-sc[i],i))[:K]
        res[code]=[{'chunk':cs[i]['id'],'score':float(sc[i])} for i in top]
    return cs,res
if __name__=='__main__':
    ex=json.load(open(OUT+'/extract_log.json'))
    meta={'pypdf':ex['pypdf'],'extract_python':ex['python'],'transformers':transformers.__version__,'rank_bm25':md.version('rank_bm25'),
          'tokenizer':'Qwen/Qwen3-1.7B','retrieve_python':sys.version.split()[0],'chunk_tokens':CH,'overlap':OV,'top_k':K,
          'bm25':'BM25Okapi default k1=1.5 b=0.75, tokens=\\w+ lowercase, no stopword removal'}
    json.dump(meta,open(OUT+'/versions.json','w'),indent=1)
    allc={}; allr={}
    for pid,v in ex['papers'].items():
        if 'chars' not in v or v['chars']<2000: continue
        cs,res=retrieve(pid); allc[pid]=cs; allr[pid]=res
    json.dump(allc,open(OUT+'/chunks.json','w')); json.dump(allr,open(OUT+'/retrieval.json','w'))
    print(len(allr),'papers',sum(len(c) for c in allc.values()),'chunks')
