import json,re,unicodedata
S='/Users/heuremen/bones-forge/stan'
def norm(t):
    t=unicodedata.normalize('NFKC',t).lower().replace('−','-').replace('–','-').replace('—','-')
    t=re.sub(r'-\s*\n\s*','',t); t=re.sub(r'[‘’“”]',"'",t)
    return re.sub(r'\s+',' ',t)
def cands(note):
    q=[m for m in re.findall(r'"([^"]{10,300})"|“([^”]{10,300})”',note)]
    q=[a or b for a,b in q]
    q+= [m for m in re.findall(r"'([^']{12,200})'",note)]
    nums=re.findall(r'(?<![\w.])\d+(?:\.\d+)?(?:\s*(?:±|\+/-)\s*\d+(?:\.\d+)?)?%?',note)
    nums=[n for n in dict.fromkeys(nums) if len(n.replace(' ',''))>=3 or '.' in n]
    return q,nums

def sq(t): return re.sub(r'[^0-9a-z]','',norm(t))
def numfind(n,t):
    pat=re.escape(norm(n)).replace(r'\ ',r'\s*')
    return [m.start() for m in re.finditer(r'(?<![\d.])'+pat+r'(?![\d])',t)]
def build():
    r=json.load(open(S+'/ceiling_ft/retrieval.json')); C=json.load(open(S+'/ceiling_ft/chunks.json'))
    J=[json.loads(l) for l in open(S+'/ceiling/judgments.jsonl')]; J=[j for j in J if j['id'] in r]
    TX={i:open(S+'/ceiling_ft/text/%s.txt'%i).read() for i in r}
    T={i:sq(t) for i,t in TX.items()}; TN={i:norm(t) for i,t in TX.items()}
    CN={i:{c['id']:(sq(c['text']),norm(c['text'])) for c in C[i]} for i in r}
    for j in J:
        i,code=j['id'],j['code']; top={x['chunk'] for x in r[i][code]}; q,nums=cands(j['note_used']); res=[]
        for s in q+nums:
            isn=s in nums
            if isn:
                full=bool(numfind(s,TN[i])); ch=[c for c,(a,b) in CN[i].items() if numfind(s,b)]
            else:
                piece=max(s.split('...'),key=len); ns=sq(piece.strip(' .,;'))
                if not ns: continue
                full=ns in T[i]; ch=[c for c,(a,b) in CN[i].items() if ns in a]
            res.append({'s':s,'full':full,'top':[c for c in ch if c in top],'other':[c for c in ch if c not in top],'num':isn})
        j['res']=res
    return J
