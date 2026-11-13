import json,csv,sys,os,re,html
D=os.path.expanduser('~/bones-forge/rank_index/')
R=os.path.dirname(os.path.abspath(__file__))+'/../out/'
desk=json.load(open(D+'data/rank.json'))
mine={}
for r in csv.DictReader(open(R+'usnews_read_20261110.tsv'),delimiter='\t'):
    mine.setdefault(r['list'],[]).append(r)
diffs=[]
for L in desk['lists']:
    k=L['key']; rows=L['rows']; m=mine.get(k,[])
    if k in('elem','middle'): continue
    if len(rows)!=len(m): diffs.append((k,'count',len(rows),len(m)))
    from collections import Counter
    rk=Counter(r.get('rank') for r in rows)
    for a,b in zip(rows,m):
        rank='T1' if a.get('rank') is None else str(a['rank'])
        if rank!=b['rank']: diffs.append((k,a['name'],'rank',rank,b['rank']))
        tie_exp = (Counter(x['rank'] for x in m)[b['rank']]>1) if b['rank']!='T1' else False
        if bool(a.get('tie'))!=tie_exp: diffs.append((k,a['name'],'tie',a.get('tie'),tie_exp))
        if a['name']!=b['name']: diffs.append((k,a['name'],'name',a['name'],b['name']))
        if (a.get('place') or '')!=b['place']: diffs.append((k,a['name'],'place',a.get('place'),b['place']))
        if k=='hs':
            for f,v in (('grad',b['fig1']),('college_readiness',b['fig2']),('enrollment',b['fig3'])):
                if a.get(f)!=v: diffs.append((k,a['name'],f,a.get(f),v))
        if k in('nu','nlac') and a.get('enrollment')!=b['fig1']: diffs.append((k,a['name'],'enrollment',a.get('enrollment'),b['fig1']))
for d in diffs: print('\t'.join(map(str,d)))
print('TOTAL',len(diffs))
