import csv,re,sys,collections
D=sys.argv[1]
for fn,glab in [('Faculty-focus_data.csv','Compare label'),('Student-focus_data.csv','Compare label (student)')]:
    rows=list(csv.DictReader(open(D+'/'+fn,encoding='utf-8-sig')))
    print('=====',fn,len(rows),'rows; fields',list(rows[0].keys()))
    Q=collections.OrderedDict()
    for r in rows: Q.setdefault((r['Question display 1'][:70],r['Question display 2'][:50]),[]).append(r)
    print('questions x sub-items:',len(Q))
    for (q1,q2),rs in list(Q.items()):
        groups=collections.defaultdict(list)
        for r in rs: groups[r[glab]].append(r)
        gn={}; bad=0
        for g,gr in groups.items():
            m=re.search(r'\(n=([\d,]+)\)',g); n=int(m.group(1).replace(',','')) if m else None
            tot=sum(int(float(x['count d emplid'] or 0)) for x in gr); gn[g]=(n,tot)
            for x in gr:
                p=float(x['% of Total valid response'].rstrip('%') or 0); c=int(float(x['count d emplid'] or 0))
                if tot and abs(100*c/tot-p)>0.5: bad+=1
        sum_n=sum(v[0] for v in gn.values() if v[0]); sum_counts=sum(v[1] for v in gn.values())
        print(f'  [{q1[:45]}|{q2[:25]}] groups {len(gn)} sum(n=)={sum_n} sum(counts)={sum_counts} pct_mismatch>0.5pt={bad} | label n vs counts differ in {sum(1 for v in gn.values() if v[0] and v[0]!=v[1])} groups')
