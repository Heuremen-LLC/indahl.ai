# Parses MLPerf Training v6.0 result logs (raw/training_v60, github.com/mlcommons/training_results_v6.0) into per-system, per-benchmark times. python3 -I parse_training_v60.py
import os,re,json,glob,statistics
ROOT='raw/training_v60'; out=[]
for sub in sorted(os.listdir(ROOT)):
    rd=os.path.join(ROOT,sub,'results')
    if not os.path.isdir(rd): continue
    for system in sorted(os.listdir(rd)):
        sd=os.path.join(rd,system)
        if not os.path.isdir(sd): continue
        for bench in sorted(os.listdir(sd)):
            bd=os.path.join(sd,bench)
            if not os.path.isdir(bd): continue
            runs=[]; plat=None; bname=None
            for f in sorted(glob.glob(os.path.join(bd,'result_*.txt'))):
                rs=rp=None; ok=None
                for line in open(f,errors='ignore'):
                    if ':::MLLOG' not in line: continue
                    if '"key": "run_start"' in line: rs=int(re.search(r'"time_ms": (\d+)',line).group(1))
                    elif '"key": "run_stop"' in line:
                        rp=int(re.search(r'"time_ms": (\d+)',line).group(1)); m=re.search(r'"status": "(\w+)"',line); ok=m.group(1) if m else None
                    elif '"key": "submission_platform"' in line and plat is None: plat=re.search(r'"value": "([^"]*)"',line).group(1)
                    elif '"key": "submission_benchmark"' in line and bname is None: bname=re.search(r'"value": "([^"]*)"',line).group(1)
                if rs and rp: runs.append((rp-rs)/60000.0 if ok in (None,'success') else None)
            good=[r for r in runs if r is not None]
            sf=1.0; sp=os.path.join(bd,'scaling.json')
            if os.path.isfile(sp): sf=float(json.load(open(sp))['scaling_factor'])   # applied by the review committee, as the official summarizer does
            sysj=os.path.join(ROOT,sub,'systems',system+'.json'); gp=None; acc=None
            if os.path.isfile(sysj):
                d=json.load(open(sysj)); 
                try: gp=int(d['number_of_nodes'])*int(d['accelerators_per_node']); acc=d.get('accelerator_model_name')
                except Exception: pass
            if good: out.append(dict(submitter=sub,system=system,benchmark=bench,logged_benchmark=bname,platform=plat,runs_minutes=[round(r,3) for r in good],n=len(good),scaling_factor=sf,gpus=gp,accelerator=acc,official_style=(round(statistics.mean(sorted(good)[1:-1])*sf,3) if len(good)>=3 else None),mean=round(statistics.mean(good),3),median=round(statistics.median(good),3),olympic=(round(statistics.mean(sorted(good)[1:-1]),3) if len(good)>=3 else None)))
json.dump(out,open('training_v60_times.json','w'),indent=0)
print(len(out),'system-benchmark rows from',len({o['submitter'] for o in out}),'submitters')
