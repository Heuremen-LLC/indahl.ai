"""Contamination matcher: is a candidate record a duplicate of a gold record? Signals: DOI family, title, authors, abstract text.
Python 3.9 compatible, stdlib only. Thresholds are fixed in PLAN.md."""
import re,math,collections
TH={'title':0.80,'abs':0.50,'auth':0.60,'title_with_auth':0.45,'abs_with_auth':0.30}
def norm(t): return re.sub(r'[^a-z0-9 ]+',' ',(t or '').lower().replace('-',' ')).split()
def tri(t):
    s=' '.join(norm(t)); return {s[i:i+3] for i in range(max(0,len(s)-2))}
def jac(a,b): return len(a&b)/len(a|b) if a and b else 0.0
def title_sim(a,b): return max(jac(set(norm(a)),set(norm(b))),jac(tri(a),tri(b)))
def surname(n): 
    p=re.sub(r'[^a-z ]+','',(n or '').lower()).split(); return p[-1] if p else ''
def auth_overlap(a,b):
    A={surname(x) for x in a if x}-{''}; B={surname(x) for x in b if x}-{''}
    return len(A&B)/min(len(A),len(B)) if A and B else 0.0
STOP=set('the a an of and or in on for to with by is are we this that from as at be it its which our can using use based show results paper'.split())
def toks(t):
    w=[x for x in norm(t) if x not in STOP]; return w+[w[i]+'_'+w[i+1] for i in range(len(w)-1)]
class Idf:
    def __init__(self,docs):
        df=collections.Counter(); 
        for d in docs: df.update(set(toks(d)))
        self.n=len(docs); self.df=df
    def vec(self,t):
        c=collections.Counter(toks(t)); v={k:(1+math.log(x))*math.log((self.n+1)/(self.df.get(k,0)+1)+1) for k,x in c.items()}
        nr=math.sqrt(sum(x*x for x in v.values())) or 1.0; return {k:x/nr for k,x in v.items()}
def cos(u,v):
    if len(u)>len(v): u,v=v,u
    return sum(x*v.get(k,0) for k,x in u.items())
def compare(a,b,idf,use_family=True):
    """a,b dict(title,abstract,authors,family). Returns (flag,reasons,scores)."""
    ts=title_sim(a.get('title'),b.get('title')); au=auth_overlap(a.get('authors') or [],b.get('authors') or [])
    ab=cos(idf.vec(a.get('abstract') or ''),idf.vec(b.get('abstract') or '')) if a.get('abstract') and b.get('abstract') else 0.0
    why=[]
    if use_family and set(a.get('family') or [])&set(b.get('family') or []): why.append('doi_family')
    if ts>=TH['title']: why.append('title')
    if ab>=TH['abs']: why.append('abstract')
    if au>=TH['auth'] and ts>=TH['title_with_auth']: why.append('authors+title')
    if au>=TH['auth'] and ab>=TH['abs_with_auth']: why.append('authors+abstract')
    return bool(why),why,{'title':round(ts,3),'authors':round(au,3),'abstract':round(ab,3)}
