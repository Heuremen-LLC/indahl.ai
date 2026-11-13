import json,collections
OUT='/Users/heuremen/bones-forge/cone_index_referee/out/'
D=json.load(open('/Users/heuremen/bones-forge/cone_index/data/cone.json'))
rows=json.load(open(OUT+'rows.json')); paths=json.load(open(OUT+'paths.json'))
mine={(r['storm'],r['dtg'],r['lead']):r for r in rows}
desk={(r['storm'],r['dtg'],r['lead']):r for r in D['rows']}
rep={}
rep['rows_mine']=len(mine);rep['rows_desk']=len(desk)
rep['only_mine']=[k for k in mine if k not in desk][:10];rep['n_only_mine']=len([k for k in mine if k not in desk])
rep['only_desk']=[k for k in desk if k not in mine][:10];rep['n_only_desk']=len([k for k in desk if k not in mine])
omap={'NR':'NOTHING_RETURNED'}
od=[];dd=[];other=[];tcd=[]
for k,m in mine.items():
    d=desk.get(k)
    if not d: continue
    mo=omap.get(m['outcome'],m['outcome'])
    if m['rad'] is None: mo=d['outcome']  # 2012: desk writes NO_RADII; compared on dist/tc only
    if mo!=d['outcome']: od.append((k,mo,d['outcome']))
    if m['dist'] is not None:
        if d['dist'] is None or abs(m['dist']-d['dist'])>0.01: dd.append((k,m['dist'],d['dist']))
    elif d['dist'] is not None: dd.append((k,None,d['dist']))
    if bool(m['tc'])!=bool(d.get('tc_both')): tcd.append(k)
    if m['rad'] is not None and m['why'] and d['why'] and ((m['why']=='no bt')!=('track ended' in str(d['why']) or 'no best' in str(d['why']))): other.append((k,m['why'],d['why']))
rep['outcome_diffs']=len(od);rep['outcome_diff_examples']=od[:10];rep['dist_diffs']=len(dd);rep['dist_diff_examples']=dd[:10];rep['tc_flag_diffs']=len(tcd);rep['why_diffs']=other[:5]
print(collections.Counter(r['why'] for r in D['rows'] if r['outcome']=='NOTHING_RETURNED'))
# fc / bt position check
pd=0
for k,d in desk.items():
    m=mine.get(k)
    if m is None: continue
pm={(p['storm'],p['dtg']):p for p in paths}; pdk={(p['storm'],p['dtg']):p for p in D['paths']}
rep['paths_mine']=len(pm);rep['paths_desk']=len(pdk)
rep['n_paths_only_mine']=len([k for k in pm if k not in pdk]);rep['n_paths_only_desk']=len([k for k in pdk if k not in pm])
pod=[(k,omap.get(pm[k]['outcome'],pm[k]['outcome']),pdk[k]['outcome']) for k in pm if k in pdk and omap.get(pm[k]['outcome'],pm[k]['outcome'])!=pdk[k]['outcome']]
rep['path_outcome_diffs']=len(pod);rep['path_diff_examples']=pod[:10]
fo=[(k,pm[k].get('first_out'),pdk[k].get('first_outside_h')) for k in pm if k in pdk and pm[k]['outcome']=='OUTSIDE' and pm[k].get('first_out')!=pdk[k].get('first_outside_h')]
rep['first_outside_diffs']=len(fo)
json.dump(rep,open(OUT+'diff_vs_desk.json','w'),indent=1,default=str)
print(json.dumps(rep,indent=1,default=str))
