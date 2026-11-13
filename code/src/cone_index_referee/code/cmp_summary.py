import json
OUT='/Users/heuremen/bones-forge/cone_index_referee/out/'
S=json.load(open('/Users/heuremen/bones-forge/cone_index/summary_cone.json')); M=json.load(open(OUT+'cells_ref.json'))
bad=0; tab=[]
for c in S['cells']:
    k=('WP_%s'%c['basin']) if c['kind']=='whole path' else 'C_%s_%d'%(c['basin'],c['lead'])
    m=M[k]
    ok=(c['inside'],c['scored'],c['storms'],c['nothing_returned'],c['outcome'])==(m['inside'],m['scored'],m['storms'],m['nr'],m['out'])
    dl=max(abs(c['lo']-m['lo']),abs(c['hi']-m['hi']))
    tab.append((c['cell'],c['inside'],c['scored'],round(100*c['share'],1),(round(100*c['lo'],1),round(100*c['hi'],1)),c['outcome'],'|',m['inside'],m['scored'],round(100*m['share'],1),(round(100*m['lo'],1),round(100*m['hi'],1)),m['out'],ok,round(100*dl,2)))
    bad+=not ok
for t in tab: print(*t)
print('cell mismatches',bad)
# by season
bs=M['by_season_wp']; bad=0
for r in S['by_season']:
    w=r['whole_path']; m=bs.get('%s%d'%(r['basin'],r['season']))
    if m is None: print('no',r['basin'],r['season']); continue
    if (w['inside'],w['scored'],w['outcome'],w['nothing_returned'])!=(m['inside'],m['scored'],m['out'],m['nr']): bad+=1; print('diff',r['basin'],r['season'],w['inside'],w['scored'],w['outcome'],w['nothing_returned'],m)
print('by-season WP mismatches',bad,len(S['by_season']))
# 2026
bad=0
for r in S['current']:
    b=r['basin']; w=r['whole_path']; m=M['WP26_'+b]
    if (w['inside'],w['scored'],w['outcome'],w['nothing_returned'])!=(m['inside'],m['scored'],m['out'],m['nr']): bad+=1; print('wp26',b,w['inside'],w['scored'],w['outcome'],w['nothing_returned'],m)
    for L,c in r['circles'].items():
        m=M['C26_%s_%s'%(b,L)]
        if (c['inside'],c['scored'],c['outcome'],c['nothing_returned'])!=(m['inside'],m['scored'],m['out'],m['nr']): bad+=1; print('c26',b,L,c['inside'],c['scored'],c['outcome'],c['nothing_returned'],m['inside'],m['scored'],m['out'],m['nr'])
print('2026 mismatches',bad)
