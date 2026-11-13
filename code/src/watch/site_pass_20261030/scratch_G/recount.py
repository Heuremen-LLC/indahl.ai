# independent recount of schools.json from raw crawl files (read-only; writes only to scratch)
import csv,json,re,os,collections
O='/Users/heuremen/bones-forge/oy_index/'
D=O+'smallpass/'
roster=[]
for f,cls in (('ROSTER.csv','Arts & Sciences focus'),('ROSTER22.csv','Diverse fields')):
    for r in csv.reader(l for l in open(D+f) if not l.startswith('#')):
        if r[2]!='domain': roster.append(dict(school=r[0],state=r[1],domain=r[2],unitid=r[3],carnegie=cls))
# coverage: take the logs independently, record every line to see what the build picked
cov_all=collections.defaultdict(list)
for lf in ('run3a.log','run_fast.log','run_www.log','run_retry.log'):
    for l in open(D+lf):
        m=re.match(r'^([\w.-]+\.\w+) (\d+) (\d+) (\d+) (\d+)$',l.strip())
        if m: cov_all[re.sub(r'^www\.','',m.group(1))].append((lf,)+tuple(int(m.group(i)) for i in range(2,6)))
hits=collections.defaultdict(list)
for hf in ('hits_p3a.jsonl','hits_fast.jsonl','hits_www.jsonl','hits_retry.jsonl'):
    for l in open(D+hf):
        try: x=json.loads(l)
        except Exception: continue
        hits[re.sub(r'^www\.','',x['domain'])].append((hf,x['url'],x['s']))
json.dump(dict(cov=cov_all,hits={k:v for k,v in hits.items()}),open('recount_raw.json','w'))
S={s['unitid']:s for s in json.load(open(O+'schools.json'))}
bad=[]
for r in roster:
    s=S[r['unitid']]
    for k in ('school','state','domain','carnegie'):
        if s[k]!=r[k]: bad.append((r['unitid'],k,s[k],r[k]))
print('roster mismatches',bad[:10],len(roster),len(S))
# coverage check
cb=[]
for u,s in S.items():
    d=s['domain']; L=cov_all.get(d)
    if L is None:
        if s['pages_fetched'] is not None: cb.append((u,'cov missing in logs but pages_fetched set',s['pages_fetched']))
        continue
    best=None
    for e in L:
        if best is None or not (best[2]>e[2]): best=e
    if s['pages_fetched']!=best[2] or s['ai_urls']!=best[1]: cb.append((u,s['school'],s['pages_fetched'],s['ai_urls'],L))
print('coverage mismatches',len(cb)); 
for x in cb[:20]: print(x)
# hit check
hb=[]
for u,s in S.items():
    d=s['domain']; seen=set(); hs=[]
    for hf,url,sen in hits.get(d,[]):
        k=sen[:320][:80]
        if k in seen: continue
        seen.add(k); hs.append((url,sen[:320]))
    got=[(x['url'],x['sentence']) for x in s['sentences']]
    if got!=hs[:6] or s['sentences_total']!=len(hs): hb.append((u,s['school'],len(got),s['sentences_total'],len(hs)))
print('hit mismatches',len(hb),hb[:10])
