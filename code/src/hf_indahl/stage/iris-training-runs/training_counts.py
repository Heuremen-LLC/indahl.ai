"""training_counts.py: metrics from our own LoRA training runs (27 Oct 2026). Reads the MLX training log, the run configs and the eval result files. Writes summary.json.
Numbers only: no training data, no weights, no item text. Run names are adapter folder names (adapters_heavy_v50 and so on)."""
import re, os, json, glob, math, collections, datetime
H = os.path.expanduser('~/bones-forge/')
FIX_DATE = '2026-08-26'   # train_continuous.sh, comment dated 2026-08-26: before this fix every validation check scored a random 100 of the 489 examples, a different 100 each time; after it every check scores 488 of 489
VT = re.compile(r'^Iter \d+: Val loss [\w.+-]+, Val took ([\d.]+)s')
IT = re.compile(r'^Iter (\d+): Train loss ([\w.+-]+), Learning Rate ([\d.e+-]+), It/sec ([\d.]+), Tokens/sec ([\d.]+), Trained Tokens (\d+), Peak mem ([\d.]+) GB')
VL = re.compile(r'^Iter (\d+): Val loss ([\w.+-]+)')
SV = re.compile(r'Saved adapter weights to (adapters[\w]*)/')
segs = []; cur = None
for l in open(H + 'train_continuous.log', errors='replace'):
    l = l.strip()
    m = VL.match(l)
    if m and m.group(1) == '1': cur = dict(name=None, train=[], val=[], tok=0, peak=0.0, tps=[]); segs.append(cur)
    if cur is None: continue
    if m: cur['val'].append((int(m.group(1)), float(m.group(2))))
    vt = VT.match(l)
    if vt: cur.setdefault('val_secs', []).append(float(vt.group(1)))
    t = IT.match(l)
    if t: cur['train'].append((int(t.group(1)), float(t.group(2)))); cur['tok'] = max(cur['tok'], int(t.group(6))); cur['peak'] = max(cur['peak'], float(t.group(7))); cur['tps'].append(float(t.group(5)))
    s = SV.search(l)
    if s and cur['name'] is None: cur['name'] = s.group(1)
runs = []
for s in segs:
    if not s['val']: continue
    tr = s['train']; va = s['val']
    nan_tr = [i for i, v in tr if not math.isfinite(v)]; nan_va = [i for i, v in va if not math.isfinite(v)]
    trf = [(i, v) for i, v in tr if math.isfinite(v)]; vaf = [(i, v) for i, v in va if math.isfinite(v)]
    runs.append(dict(name=s['name'] or 'unsaved', iters=max([i for i, _ in tr] + [i for i, _ in va]), val_first=vaf[0][1] if vaf else None, val_last=vaf[-1][1] if vaf else None, val_min=min(v for _, v in vaf) if vaf else None, val_n=len(va), nan_train=len(nan_tr), nan_val=len(nan_va), first_nan_iter=min(nan_tr + nan_va) if (nan_tr or nan_va) else None,
                     train_first=trf[0][1] if trf else None, train_last=trf[-1][1] if trf else None, trained_tokens=s['tok'], peak_mem_gb=s['peak'], tokens_per_sec_mean=round(sum(s['tps']) / len(s['tps']), 1) if s['tps'] else None,
                     curve=vaf))
# 30 Oct 2026: split the sessions by the validation fix. A session counts as after the fix when its adapter folder was last written after FIX_DATE (the log has no dates).
# Cross-check from the log itself: the full-set validation takes several times longer per check, so the median "Val took" is 40 s or more only in those sessions.
for r, sg in zip(runs, [x for x in segs if x['val']]):
    p_ = H + r['name']; r['last_written'] = datetime.date.fromtimestamp(os.stat(p_).st_mtime).isoformat() if os.path.isdir(p_) else None
    vs = sorted(sg.get('val_secs', [])); r['val_secs_median'] = vs[len(vs) // 2] if vs else None
    r['after_fix'] = bool(r['last_written'] and r['last_written'] > FIX_DATE)
    r['after_fix_by_val_time'] = bool(r['val_secs_median'] is not None and r['val_secs_median'] >= 40)
cfg = {}
for f in sorted(glob.glob(H + 'lora_*.yaml')):
    t = open(f).read(); g = lambda k: (re.search(r'^\s*' + k + r':\s*([^\n#]+)', t, re.M) or [None, None])[1]
    nm = re.search(r'adapter_path:\s*\./(\w+)', t)
    if nm: cfg[nm.group(1)] = dict(model=(g('model') or '').strip(), rank=g('rank'), lr=g('learning_rate'), iters=g('iters'), num_layers=g('num_layers'), batch_size=g('batch_size'), scale=g('scale'), save_every=g('save_every'), steps_per_eval=g('steps_per_eval'))
for r in runs: r['config'] = cfg.get(r['name'])
ad = collections.defaultdict(lambda: dict(dirs=0, checkpoints=0, first=None, last=None))
for p in glob.glob(H + 'adapters*'):
    if not os.path.isdir(p): continue
    k = re.sub(r'_?v\d+$', '', re.sub(r'_good\d+$', '', os.path.basename(p))); a = ad[k]; a['dirs'] += 1; a['checkpoints'] += len(glob.glob(p + '/0*_adapters.safetensors'))
    d = datetime.date.fromtimestamp(os.stat(p).st_mtime).isoformat(); a['first'] = min(a['first'] or d, d); a['last'] = max(a['last'] or d, d)
ev = []
for f in sorted(glob.glob(H + 'eval_results/*_vs_live.json')):
    d = json.load(open(f)); a = d['aggregate']
    ev.append(dict(file=os.path.basename(f), candidate=d['candidate'], live=d['live'], run_at=d['run_at'], scenarios=a['total_scenarios'], scored=a['scored_scenarios'], skipped=a['skipped_scenarios'], judge_failures=len(a.get('skipped_detail', [])),
                   axis_majority_wins=a['scenarios_where_candidate_won_axis_majority'], axis_majority_fraction=a['scenario_axis_majority_fraction'], per_axis=a['per_axis_win_counts'], promoted=d['promotion_bar']['passed']))
tot_it = sum(r['iters'] for r in runs)
def period(rs):
    fin = [r for r in rs if r['val_last'] is not None]
    return dict(runs=len(rs), runs_with_finite_val=len(fin), runs_val_improved=sum(1 for r in fin if r['val_last'] < r['val_first']), runs_val_min_before_last=sum(1 for r in fin if r['val_min'] < r['val_last'] - 1e-9))
by_period = dict(before_fix=period([r for r in runs if not r['after_fix']]), after_fix=period([r for r in runs if r['after_fix']]), sessions_where_date_and_val_time_disagree=sum(1 for r in runs if r['after_fix'] != r['after_fix_by_val_time']), fix_date=FIX_DATE)
out = dict(runs=runs, adapter_families=ad, evals=ev, by_period=by_period, totals=dict(runs_with_curves=len(runs), iterations=tot_it, trained_tokens=sum(r['trained_tokens'] for r in runs), val_loss_lines=sum(r['val_n'] for r in runs),
           runs_val_improved=sum(1 for r in runs if r['val_last'] is not None and r['val_last'] < r['val_first']), runs_val_min_before_last=sum(1 for r in runs if r['val_last'] is not None and r['val_min'] < r['val_last'] - 1e-9), runs_with_finite_val=sum(1 for r in runs if r['val_last'] is not None), runs_with_nan=sum(1 for r in runs if r['first_nan_iter'] is not None), nan_val_lines=sum(r['nan_val'] for r in runs), nan_train_lines=sum(r['nan_train'] for r in runs),
           adapter_dirs=sum(a['dirs'] for a in ad.values()), checkpoints=sum(a['checkpoints'] for a in ad.values()), configs=len(cfg), evals=len(ev), evals_promoted=sum(1 for e in ev if e['promoted'])))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'summary.json'), 'w'))
print(json.dumps(out['totals'], indent=1)); print('by period', json.dumps(by_period)); print('adapter families', {k: v['dirs'] for k, v in ad.items()});  print('evals', [(e['file'], e['scored'], e['axis_majority_wins'], e['promoted']) for e in ev])
