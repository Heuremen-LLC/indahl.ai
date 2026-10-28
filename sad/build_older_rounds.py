# Reads system description files from the public MLCommons result repositories for v3.1, v4.0 and v4.1 (no summary file exists for them).
# Writes raw/older_rounds_systems.json: submitters per round, the RedHat, Azure and AMD system files, and every system file with GH200 or Grace in its name. python3 -I build_older_rounds.py
import json,re,subprocess,os
HERE=os.path.dirname(os.path.abspath(__file__))
def get(u): return subprocess.run(['curl','-sL','-m','60',u],capture_output=True,text=True).stdout
out={}
for r in ('3.1','4.0','4.1'):
    T=json.loads(get(f'https://api.github.com/repos/mlcommons/inference_results_v{r}/git/trees/main?recursive=1')); P=[x['path'] for x in T['tree']]
    sysf=[p for p in P if re.match(r'(closed|open)/[^/]+/systems/[^/]+\.json$',p)]
    subs=sorted({p.split('/')[1] for p in sysf}); keep=[p for p in sysf if p.split('/')[1] in('RedHat','Azure','AMD') or 'GH200' in p or 'Grace' in p]
    rows=[]
    for p in keep:
        try: j=json.loads(get(f'https://raw.githubusercontent.com/mlcommons/inference_results_v{r}/main/{p}'))
        except Exception: continue
        rows.append(dict(path=p,division=p.split('/')[0],submitter=p.split('/')[1],nodes=j.get('number_of_nodes'),accelerators_per_node=j.get('accelerators_per_node'),accelerator=j.get('accelerator_model_name'),operating_system=j.get('operating_system'),framework=j.get('framework')))
    out['v'+r]=dict(repository=f'https://github.com/mlcommons/inference_results_v{r}',tree_truncated=bool(T.get('truncated')),system_files=len(sysf),submitters=subs,selected_systems=rows)
json.dump(out,open(os.path.join(HERE,'raw','older_rounds_systems.json'),'w'),indent=1); print({k:(v['system_files'],len(v['submitters']),len(v['selected_systems'])) for k,v in out.items()})
