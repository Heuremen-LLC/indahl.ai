# Aggregates the MLPerf Storage v3.0 results repository (github.com/mlcommons/storage_results_v3.0, Apache-2.0, cloned 28 Oct 2026) into storage/storage_v30_results.json.
# Rules (Rules.md 2.1.17): a training run directory holds 6 timestamp runs, the first is the warm-up, the reported value is the mean of the other five. python3 -I build_storage_v30.py
import os, json, glob, re, sys, hashlib, statistics as st
try: import yaml
except Exception: yaml = None
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, 'storage', 'v3.0')
def ysys(path):
    t = open(path, errors='ignore').read(); g = lambda k: (re.search(r'^\s*["\']?' + k + r'["\']?:\s*(.+?),?\s*$', t, re.M) or [None, ''])[1].strip().strip("'\"")
    uri = re.search(r'STORAGE_URI_SCHEME\W+value:\s*[\'"]?([\w-]+)', t)
    return dict(uri_scheme=uri.group(1) if uri else '', benchmark_API=g('benchmark_API'), product_API=g('product_API'), storage_location=g('storage_location'), deployment=g('deployment'), availability=g('availability'), submission_name=g('submission_name'))
rows = []
for div in ('closed', 'open'):
    for sub in sorted(os.listdir(os.path.join(ROOT, div))) if os.path.isdir(os.path.join(ROOT, div)) else []:
        rd = os.path.join(ROOT, div, sub, 'results')
        if not os.path.isdir(rd): continue
        for system in sorted(os.listdir(rd)):
            ymlp = os.path.join(ROOT, div, sub, 'systems', system + '.yaml'); sysinfo = ysys(ymlp) if os.path.exists(ymlp) else {}
            for cat in sorted(os.listdir(os.path.join(rd, system))):
                cd = os.path.join(rd, system, cat)
                for wl in sorted(os.listdir(cd)):
                    wd = os.path.join(cd, wl)
                    if cat == 'training':
                        runs = sorted(glob.glob(os.path.join(wd, 'run', '*', 'summary.json')))
                        S = [json.load(open(f)) for f in runs]
                        if len(S) < 2: rows.append(dict(division=div, submitter=sub, system=system, category=cat, workload=wl, runs=len(S), note='fewer than 2 runs')); continue
                        use = S[1:]; m = lambda k: st.fmean(s['metric'][k] for s in use)
                        rows.append(dict(division=div, submitter=sub, system=system, category=cat, workload=wl, runs=len(S), accelerators=S[0]['num_accelerators'], hosts=S[0]['num_hosts'],
                                         au_pct=m('train_au_mean_percentage'), samples_per_s=m('train_throughput_mean_samples_per_second'), io_MiB_per_s=m('train_io_mean_MB_per_second'), io_GiB_per_s=m('train_io_mean_MB_per_second') / 1024, **sysinfo))
                    elif cat == 'checkpointing':
                        runs = sorted(glob.glob(os.path.join(wd, '*', 'summary.json')))
                        S = [json.load(open(f)) for f in runs]
                        if not S: continue
                        m = lambda k: st.fmean(s['metric'][k] for s in S if k in s['metric'])
                        rows.append(dict(division=div, submitter=sub, system=system, category=cat, workload=wl, runs=len(S), accelerators=S[0]['num_accelerators'], hosts=S[0]['num_hosts'],
                                         write_GiB_per_s=m('save_checkpoint_io_mean_GB_per_second'), read_GiB_per_s=m('load_checkpoint_io_mean_GB_per_second'), checkpoint_GB=S[0]['metric'].get('checkpoint_size_GB'), **sysinfo))
                    else:
                        rows.append(dict(division=div, submitter=sub, system=system, category=cat, workload=wl, runs=len(glob.glob(os.path.join(wd, '**', 'summary.json'), recursive=True)), **sysinfo))
json.dump(dict(source='https://github.com/mlcommons/storage_results_v3.0', licence='Apache-2.0', rows=rows), open(os.path.join(HERE, 'storage', 'storage_v30_results.json'), 'w'), indent=1)
import collections
print(len(rows), 'rows', dict(collections.Counter((r['division'], r['category']) for r in rows)))
