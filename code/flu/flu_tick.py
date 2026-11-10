#!/usr/bin/env python3
"""flu_tick.py: FLU rider (see PLAN.md). Rerunnable. Installs no timer. Reads the CDC FluSight Forecast Hub through git (sparse checkout in
data/raw/hub, pulled at most once per 6 hours), sets the FluSight-ensemble's stated 50 and 95 percent intervals beside the reported weekly
flu admissions (final and first-reported releases), and the ensemble's weighted interval score beside the FluSight-baseline's.
Writes data/flu.json, summary_flu.json, data/flu_live.json and data/flu_history.jsonl.
--offline: no git pull. --publish: also put data/flu_live.json in the site KV as flu_live, served at /flu/live.json. --selftest: rule checks only."""
import os, sys, json, time, math, csv, glob, hashlib, subprocess, collections as C
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
import heuremen_kit as K
OFF = '--offline' in sys.argv; PUB = '--publish' in sys.argv
HUB = os.path.join(H, 'data', 'raw', 'hub'); ENS = os.path.join(HUB, 'model-output', 'FluSight-ensemble'); BASE = os.path.join(HUB, 'model-output', 'FluSight-baseline')
TS = os.path.join(HUB, 'target-data', 'time-series.csv'); SNAP = os.path.join(HUB, 'target-data', 'target-hospital-admissions.csv')
TARGET = 'wk inc flu hosp'; HORIZONS = (0, 1, 2, 3)
QS = ('0.01', '0.025', '0.05', '0.1', '0.15', '0.2', '0.25', '0.3', '0.35', '0.4', '0.45', '0.5', '0.55', '0.6', '0.65', '0.7', '0.75', '0.8', '0.85', '0.9', '0.95', '0.975', '0.99')
LEVELS = {'50': ('0.25', '0.75', 0.50), '95': ('0.025', '0.975', 0.95)}
EARLY_DAYS = 14; MIN_ROWS = 30; MIN_WEEKS = 8; MAX_W_COV = 0.10; MAX_W_WIS = 0.20; BLOCK = 4; REPS = 2000; SEED = 20261110; PULL_HOURS = 6
NOW = time.time(); STAMP = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(NOW)); STALE = []
os.makedirs('data', exist_ok=True)
def log(*a): print('flu:', *a, file=sys.stderr)
def fnum(x):
    try:
        v = float(x); return v if math.isfinite(v) else None
    except Exception: return None
def qf(s):
    """quantile level text -> canonical text ('0.10' and '0.1' are the same level)."""
    v = fnum(s); return None if v is None else ('%g' % v)

# ---------------- the rule (PLAN.md, Rules) ----------------
def row_outcome(lo, hi, y, unreadable=False):
    if unreadable or lo is None or hi is None or lo > hi: return K.CANNOT_TELL, 'unreadable'
    if y is None: return K.NOTHING_RETURNED, None
    if y > hi: return K.ABOVE, None
    if y < lo: return K.BELOW, None
    return K.CONSISTENT, None
def wis(q, y):
    """q: dict level text -> value (all 23). y: reported. (0.5|y-m| + sum (alpha/2) IS_alpha) / 11.5 over the 11 central intervals."""
    m = q['0.5']; tot = 0.5 * abs(y - m)
    for i in range(11):
        l, u = q[QS[i]], q[QS[22 - i]]; alpha = 2 * float(QS[i])
        s = (u - l) + (2 / alpha) * max(0.0, l - y) + (2 / alpha) * max(0.0, y - u)
        tot += alpha / 2 * s
    return tot / 11.5
def cov_outcome(lo, hi, p, n, weeks):
    if n < MIN_ROWS or weeks < MIN_WEEKS or lo is None: return K.CANNOT_TELL
    if hi < p: return K.BELOW
    if lo > p: return K.ABOVE
    if hi - lo <= MAX_W_COV: return K.CONSISTENT
    return K.CANNOT_TELL
def wis_outcome(lo, hi, n, weeks):
    if n < MIN_ROWS or weeks < MIN_WEEKS or lo is None: return K.CANNOT_TELL
    if hi < 1: return K.BELOW
    if lo > 1: return K.ABOVE
    if hi - lo <= MAX_W_WIS: return K.CONSISTENT
    return K.CANNOT_TELL
def draws(W, reps=REPS, seed=SEED):
    """Moving-block bootstrap over W sorted target weeks: a (reps x W) matrix of how often each week enters a replicate."""
    rng = np.random.default_rng(seed); M = np.zeros((reps, W), dtype=np.int32)
    if W < BLOCK: return M
    nb = math.ceil(W / BLOCK); starts = rng.integers(0, W - BLOCK + 1, size=(reps, nb))
    for j in range(BLOCK): np.add.at(M, (np.repeat(np.arange(reps), nb), (starts + j).ravel()), 1)
    return M
def boot_ratio(num_w, den_w, M):
    """num_w, den_w: per-week sums (length W). Returns (lo, hi) percentile interval of sum(num)/sum(den) over replicates."""
    a = M @ num_w; b = M @ den_w; ok = b > 0
    if ok.sum() < 100: return None, None
    r = a[ok] / b[ok]; return float(np.percentile(r, 2.5)), float(np.percentile(r, 97.5))
def rule_selftest():
    t = [row_outcome(10, 20, 25) == (K.ABOVE, None), row_outcome(10, 20, 5) == (K.BELOW, None), row_outcome(10, 20, 20) == (K.CONSISTENT, None),
         row_outcome(0, 0, 0) == (K.CONSISTENT, None), row_outcome(20, 10, 15) == (K.CANNOT_TELL, 'unreadable'), row_outcome(None, 10, 5) == (K.CANNOT_TELL, 'unreadable'),
         row_outcome(10, 20, None) == (K.NOTHING_RETURNED, None)]
    # WIS on paper: quantiles all equal to 10 except the median 10, y = 12 -> 0.5*2 + sum_k alpha_k/2 * (2/alpha_k)*2 = 1 + 11*2 = 23, / 11.5 = 2
    q = {k: 10.0 for k in QS}; t.append(abs(wis(q, 12) - 2.0) < 1e-12); t.append(abs(wis(q, 10) - 0.0) < 1e-12)
    # planted worlds: normal(0,1) outcomes, calibrated intervals vs half-width intervals; weeks of 50 rows, 120 weeks
    rng = np.random.default_rng(7); W = 120; M = draws(W, 500, 3); y = rng.standard_normal((W, 50))
    for half, want in ((1.0, K.CONSISTENT), (0.5, K.BELOW)):
        z = 1.959964 * half; ins = (np.abs(y) <= z).sum(1).astype(float); n = np.full(W, 50.0)
        lo, hi = boot_ratio(ins, n, M); t.append(cov_outcome(lo, hi, 0.95, W * 50, W) == want)
    t += [cov_outcome(0.90, 0.99, 0.95, 20, 20) == K.CANNOT_TELL, cov_outcome(0.90, 0.99, 0.95, 100, 5) == K.CANNOT_TELL, cov_outcome(0.80, 0.99, 0.95, 100, 20) == K.CANNOT_TELL,
          cov_outcome(0.96, 0.99, 0.95, 100, 20) == K.ABOVE, wis_outcome(0.6, 0.9, 100, 20) == K.BELOW, wis_outcome(1.1, 1.2, 100, 20) == K.ABOVE, wis_outcome(0.9, 1.05, 100, 20) == K.CONSISTENT]
    return all(t), t
if '--selftest' in sys.argv:
    ok, t = rule_selftest(); print('rule selftest', 'PASSED' if ok else 'FAILED', t); sys.exit(0 if ok and K.selftest() else 1)

# ---------------- 0. pull the hub (at most once per 6 hours) ----------------
def git(*a, cwd=HUB): return subprocess.run(['git'] + list(a), cwd=cwd, capture_output=True, text=True)
pull_f = 'data/last_pull'
if not OFF and (not os.path.exists(pull_f) or NOW - os.path.getmtime(pull_f) > PULL_HOURS * 3600):
    p = git('pull', '-q', '--ff-only')
    if p.returncode: log('git pull FAILED', p.stderr[-200:]); STALE.append('hub pull')
    else: open(pull_f, 'w').write(STAMP)
HUB_COMMIT = git('log', '-1', '--format=%H %cI').stdout.strip()

# ---------------- 1. stated side and baseline ----------------
NEED = ('reference_date', 'location', 'horizon', 'target', 'target_end_date', 'output_type', 'output_type_id', 'value')
fmt_ok = True; files = sorted(glob.glob(os.path.join(ENS, '*-FluSight-ensemble.csv')))
def read_q(path, check=False):
    """-> {(location, horizon): {'ted': date, 'q': {level: value or None}}} for the target, quantile rows."""
    global fmt_ok
    out = {}
    with open(path, newline='') as f:
        rd = csv.DictReader(f)
        if check and any(n not in (rd.fieldnames or []) for n in NEED): fmt_ok = False; return out
        for r in rd:
            if r.get('target') != TARGET or r.get('output_type') != 'quantile': continue
            try: h = int(r['horizon'])
            except Exception: continue
            lv = qf(r['output_type_id']); k = (r['location'], h)
            d = out.setdefault(k, dict(ted=r['target_end_date'], q={}))
            d['q'][lv] = fnum(r['value'])
    return out
stated = {}; base = {}; ref_dates = []; minus1 = 0
for f in files:
    rd = os.path.basename(f)[:10]; ref_dates.append(rd); s = read_q(f, check=True)
    lv = set(); [lv.update(v['q']) for v in s.values()]
    if not {'0.025', '0.25', '0.5', '0.75', '0.975'} <= lv: fmt_ok = False
    for (loc, h), v in s.items():
        if h == -1: minus1 += 1
        if h in HORIZONS: stated[(rd, loc, h)] = v
    bf = os.path.join(BASE, '%s-FluSight-baseline.csv' % rd)
    if os.path.exists(bf):
        for (loc, h), v in read_q(bf).items():
            if h in HORIZONS: base[(rd, loc, h)] = v

# ---------------- 2. delivered side: final and first-reported releases ----------------
vals = C.defaultdict(dict)   # (location, week) -> {as_of: value or 'CONFLICT'}
ts_ok = True
with open(TS, newline='') as f:
    rd = csv.DictReader(f)
    if any(n not in (rd.fieldnames or []) for n in ('as_of', 'target', 'target_end_date', 'location', 'observation')): ts_ok = False
    else:
        for r in rd:
            if r['target'] != TARGET: continue
            k = (r['location'], r['target_end_date']); v = fnum(r['observation']); d = vals[k]; a = r['as_of']
            if v is None: v = 'UNREADABLE'   # 10 Nov 2026, referee R2: a held but non-numeric value ('NA') is unreadable (plan: CANNOT_TELL), not missing
            if a in d and d[a] != v: d[a] = 'CONFLICT'
            else: d[a] = v
fmt_ok = fmt_ok and ts_ok
def days(a, b): return (time.mktime(time.strptime(a, '%Y-%m-%d')) - time.mktime(time.strptime(b, '%Y-%m-%d'))) / 86400
def delivered(loc, ted):
    d = vals.get((loc, ted))
    if not d: return dict(final=None, final_asof=None, first=None, first_asof=None, first_why=None)
    a1 = max(d); a0 = min(d); fv = d[a1]; ev = d[a0]
    out = dict(final=fv, final_asof=a1, first=ev, first_asof=a0, first_why=None)
    if days(a0, ted) > EARLY_DAYS: out['first'] = None; out['first_why'] = 'no early release'
    return out

# ---------------- 3. rows ----------------
def season(rd):
    y = int(rd[:4]); m = int(rd[5:7]); s = y if m >= 8 else y - 1; return '%d-%02d' % (s, (s + 1) % 100)
rows = []
for (rd, loc, h), v in sorted(stated.items()):
    q = v['q']; d = delivered(loc, v['ted'])
    row = dict(ref=rd, loc=loc, h=h, week=v['ted'], season=season(rd), median=q.get('0.5'), final=d['final'], final_asof=d['final_asof'], first=d['first'], first_asof=d['first_asof'])
    for L, (a, b, p) in LEVELS.items():
        lo, hi = q.get(a), q.get(b); row['lo' + L], row['hi' + L] = lo, hi
        for side in ('final', 'first'):
            y = d[side]; bad = y in ('CONFLICT', 'UNREADABLE')
            if side == 'first' and d['first_why'] and d['final'] is not None: o, why = K.CANNOT_TELL, d['first_why']
            else: o, why = row_outcome(lo, hi, None if bad else y, unreadable=bad)
            row['o%s_%s' % (L, side)] = o
            if why: row['why%s_%s' % (L, side)] = why
    allq = all(q.get(k) is not None for k in QS) and all(q[QS[i]] <= q[QS[i + 1]] for i in range(22)) if all(q.get(k) is not None for k in QS) else False
    bq = (base.get((rd, loc, h)) or {}).get('q', {})
    ball = all(bq.get(k) is not None for k in QS) and all(bq[QS[i]] <= bq[QS[i + 1]] for i in range(22)) if all(bq.get(k) is not None for k in QS) else False
    for side in ('final', 'first'):
        y = d[side]
        if allq and ball and isinstance(y, float):
            row['wis_ens_' + side] = round(wis(q, y), 4); row['wis_base_' + side] = round(wis(bq, y), 4)
    row['has_baseline'] = ball
    rows.append(row)

# ---------------- 4. known-good gates ----------------
kg = {'format': fmt_ok and bool(rows)}
ok2 = []
for want in (json.load(open('data/known_good_rows.json')) if os.path.exists('data/known_good_rows.json') else []):
    raw = None
    for line in open(os.path.join(ENS, want['file'])):
        p = line.rstrip('\n').split(',')
        if len(p) >= 8 and p[1] == want['location'] and p[2] == str(want['horizon']) and p[3] == TARGET and p[5] == 'quantile' and p[6] == want['q']: raw = p[7]; break
    k = (want['file'][:10], want['location'], int(want['horizon']))
    ok2.append(raw == want['value'] and k in stated and stated[k]['q'].get(qf(want['q'])) == float(want['value']))
kg['reader'] = len(ok2) >= 3 and all(ok2)
agree = tot = 0
if os.path.exists(SNAP):
    for r in csv.DictReader(open(SNAP, newline='')):
        d = vals.get((r['location'], r['date']))
        if not d: continue
        tot += 1; agree += d[max(d)] == fnum(r['value'])
kg['join'] = tot >= 100 and agree / tot >= 0.99
kg['rule'] = rule_selftest()[0]
GATE = all(kg.values())
if not GATE:
    for r in rows:
        for k in [k for k in r if k.startswith('o') and '_' in k and r[k] in K.OUTCOMES]: r[k + '_before_gate'] = r[k]; r[k] = K.CANNOT_TELL

# ---------------- 5. cells ----------------
weeks = sorted({r['week'] for r in rows if r['o95_final'] in (K.CONSISTENT, K.ABOVE, K.BELOW) or r['o95_first'] in (K.CONSISTENT, K.ABOVE, K.BELOW)})
WI = {w: i for i, w in enumerate(weeks)}; W = len(weeks); M = draws(W).astype(np.float64)
def per_week(rs, f):
    a = np.zeros(W)
    for r in rs:
        if r['week'] in WI: a[WI[r['week']]] += f(r)
    return a
def cov_cell(name, rs, L, side):
    key = 'o%s_%s' % (L, side); p = LEVELS[L][2]; cnt = C.Counter(r[key] for r in rs)
    why = C.Counter(r.get('why%s_%s' % (L, side)) for r in rs if r[key] == K.CANNOT_TELL)
    sc = [r for r in rs if r[key] in (K.CONSISTENT, K.ABOVE, K.BELOW)]; n = len(sc); k = cnt[K.CONSISTENT]; wk = len({r['week'] for r in sc})
    lo, hi = boot_ratio(per_week(sc, lambda r: r[key] == K.CONSISTENT), per_week(sc, lambda r: 1.0), M) if n else (None, None)
    zw = sum(1 for r in sc if r['lo50'] is not None and r['lo50'] == r['hi50'])
    return dict(cell=name, level=L, side=side, stated=p, rows=len(rs), scored=n, inside=k, above=cnt[K.ABOVE], below=cnt[K.BELOW], cannot_tell=cnt[K.CANNOT_TELL], cannot_tell_why={str(a): b for a, b in why.items()},
                nothing_returned=cnt[K.NOTHING_RETURNED], weeks=wk, share=round(k / n, 4) if n else None, share_above=round(cnt[K.ABOVE] / n, 4) if n else None, share_below=round(cnt[K.BELOW] / n, 4) if n else None,
                lo=None if lo is None else round(lo, 4), hi=None if hi is None else round(hi, 4), zero_width_50=zw, outcome=cov_outcome(lo, hi, p, n, wk) if GATE else K.CANNOT_TELL)
def wis_cell(name, rs, side):
    sc = [r for r in rs if ('wis_ens_' + side) in r]; n = len(sc); wk = len({r['week'] for r in sc})
    e = sum(r['wis_ens_' + side] for r in sc); b = sum(r['wis_base_' + side] for r in sc)
    lo, hi = boot_ratio(per_week(sc, lambda r: r['wis_ens_' + side]), per_week(sc, lambda r: r['wis_base_' + side]), M) if n else (None, None)
    return dict(cell=name, side=side, rows=n, weeks=wk, ens_wis_mean=round(e / n, 3) if n else None, base_wis_mean=round(b / n, 3) if n else None, ratio=round(e / b, 4) if b else None,
                lo=None if lo is None else round(lo, 4), hi=None if hi is None else round(hi, 4), outcome=wis_outcome(lo, hi, n, wk) if GATE else K.CANNOT_TELL)
groups = [('all horizons', rows)] + [('horizon %d' % h, [r for r in rows if r['h'] == h]) for h in HORIZONS]
seasons = sorted({r['season'] for r in rows}); sgroups = [('season ' + s, [r for r in rows if r['season'] == s]) for s in seasons]
cells = [cov_cell(nm, rs, L, side) for nm, rs in groups + sgroups for L in ('95', '50') for side in ('final', 'first')]
LOCN = {}
lf = os.path.join(HUB, 'auxiliary-data', 'locations.csv')
if os.path.exists(lf):
    for r in csv.DictReader(open(lf, newline='')): LOCN[r.get('location')] = r.get('location_name')
locs = sorted({r['loc'] for r in rows}, key=lambda l: (l != 'US', LOCN.get(l, l)))
by_loc = [dict(loc=l, name=LOCN.get(l, l), cells=[cov_cell(LOCN.get(l, l), [r for r in rows if r['loc'] == l], L, side) for L in ('95', '50') for side in ('final', 'first')]) for l in locs]
wis_cells = [wis_cell(nm, rs, side) for nm, rs in groups + sgroups for side in ('final', 'first')]
# described, not scored
def med(xs): return round(float(np.median(xs)), 4) if xs else None
desc = []
for h in HORIZONS:
    xs = [(r['final'] - r['median']) / (r['hi95'] - r['lo95']) for r in rows if r['h'] == h and isinstance(r['final'], float) and r['median'] is not None and r['hi95'] is not None and r['lo95'] is not None and r['hi95'] > r['lo95']]
    desc.append(dict(horizon=h, rows=len(xs), median_offset_over_width95=med(xs)))
both = [r for r in rows if isinstance(r['final'], float) and isinstance(r['first'], float)]
diff = [abs(r['final'] - r['first']) for r in both]
revisions = dict(rows=len(both), differ=sum(d > 0 for d in diff), median_abs_change=med(diff), median_abs_change_where_differ=med([d for d in diff if d > 0]),
                 share_differ=round(sum(d > 0 for d in diff) / len(both), 4) if both else None)

# 10 Nov 2026, outside referee (flu_index_referee/REFEREE.md R3, R5, R7, R8): display only, added after the data, never used for an outcome.
# (a) the headline cell read again with blocks of 8 and 13 weeks (same seed). (b) the WIS ratio without the United States row, and per place.
# (c) the longest gap between kept releases.
def _sens():
    out = []
    for bl in (BLOCK, 8, 13):
        global BLOCK_
        rng = np.random.default_rng(SEED); Mb = np.zeros((REPS, W))
        nb = math.ceil(W / bl); st = rng.integers(0, W - bl + 1, size=(REPS, nb))
        for j in range(bl): np.add.at(Mb, (np.repeat(np.arange(REPS), nb), (st + j).ravel()), 1)
        for L in ('95', '50'):
            key = 'o%s_final' % L; sc = [r for r in rows if r[key] in (K.CONSISTENT, K.ABOVE, K.BELOW)]
            lo, hi = boot_ratio(per_week(sc, lambda r: r[key] == K.CONSISTENT), per_week(sc, lambda r: 1.0), Mb)
            out.append(dict(block_weeks=bl, level=L, lo=round(lo, 4), hi=round(hi, 4), outcome=cov_outcome(lo, hi, LEVELS[L][2], len(sc), len({r['week'] for r in sc})) if GATE else K.CANNOT_TELL))
    return out
sensitivity = _sens()
_nus = [r for r in rows if r['loc'] != 'US' and 'wis_ens_final' in r]
wis_no_us = dict(rows=len(_nus), ratio=round(sum(r['wis_ens_final'] for r in _nus) / sum(r['wis_base_final'] for r in _nus), 4) if _nus else None)
if _nus:
    lo_, hi_ = boot_ratio(per_week(_nus, lambda r: r['wis_ens_final']), per_week(_nus, lambda r: r['wis_base_final']), M); wis_no_us.update(lo=round(lo_, 4), hi=round(hi_, 4))
_us = [r for r in rows if r['loc'] == 'US' and 'wis_ens_final' in r]; _all = [r for r in rows if 'wis_ens_final' in r]
wis_no_us['us_share_of_ensemble_total'] = round(sum(r['wis_ens_final'] for r in _us) / sum(r['wis_ens_final'] for r in _all), 4) if _all else None
wis_by_loc = []
for l in locs:
    rs = [r for r in rows if r['loc'] == l and 'wis_ens_final' in r]
    if rs: wis_by_loc.append(dict(loc=l, name=LOCN.get(l, l), rows=len(rs), ratio=round(sum(r['wis_ens_final'] for r in rs) / sum(r['wis_base_final'] for r in rs), 4)))
_rel = sorted({a for d in vals.values() for a in d})
release_gap_days = max((days(_rel[i + 1], _rel[i]) for i in range(len(_rel) - 1)), default=None)
latest_only = sum(1 for r in rows if isinstance(r['final'], float) and r['final_asof'] == r['first_asof'])

# ---------------- 6. plan seal and output ----------------
seal_f = 'data/plan_seal.json'
def g(*a): return subprocess.run(['git'] + list(a), cwd=H, capture_output=True, text=True).stdout.strip()
if not os.path.exists(seal_f) and K.plan_committed('PLAN.md', NOW):
    json.dump(dict(plan_commit=g('log', '-1', '--format=%H', '--', 'PLAN.md'), plan_commit_time=g('log', '-1', '--format=%cI', '--', 'PLAN.md'),
                   plan_sha256=hashlib.sha256(open('PLAN.md', 'rb').read()).hexdigest(), first_comparison=STAMP), open(seal_f, 'w'), indent=1)
seal = json.load(open(seal_f)) if os.path.exists(seal_f) else None
cnt_all = C.Counter(r['o95_final'] for r in rows)
summary = dict(
    desk='FLU', publisher='Heuremen LLC', generated=STAMP, plan='PLAN.md', plan_seal=seal, plan_unchanged_since_commit=K.plan_committed('PLAN.md'),
    claim=dict(source='CDC FluSight Forecast Hub, FluSight-ensemble, target wk inc flu hosp', stated='quantiles 0.025 and 0.975 (95 percent interval) and 0.25 and 0.75 (50 percent interval)',
               delivered='NHSN weekly confirmed flu admissions in target-data/time-series.csv, final release (primary) and first release within 14 days'),
    frame=dict(horizons=list(HORIZONS), early_days=EARLY_DAYS, min_rows=MIN_ROWS, min_weeks=MIN_WEEKS, max_width_coverage=MAX_W_COV, max_width_wis=MAX_W_WIS, block_weeks=BLOCK, replicates=REPS, seed=SEED),
    gates=dict(kg, passed=GATE, join_rows=tot, join_agree=agree),
    sources=dict(hub_commit=HUB_COMMIT, ensemble_files=len(files), first_reference_date=min(ref_dates) if ref_dates else None, last_reference_date=max(ref_dates) if ref_dates else None,
                 baseline_files=len(glob.glob(os.path.join(BASE, '*-FluSight-baseline.csv'))), releases=len({a for d in vals.values() for a in d}),
                 latest_release=max((a for d in vals.values() for a in d), default=None), horizon_minus1_rows_not_scored=minus1, stale=STALE),
    rows=dict(total=len(rows), locations=len(locs), weeks_scored=W, outcomes_95_final=dict(cnt_all), with_baseline=sum(r['has_baseline'] for r in rows)),
    cells=cells, wis=wis_cells, by_location=by_loc, described=dict(offset_by_horizon=desc, revisions=revisions),
    after_data=dict(note='Added on 10 Nov 2026 at the outside referee (flu_index_referee/REFEREE.md). Display only. No outcome uses them.',
                    block_sensitivity=sensitivity, wis_without_us=wis_no_us, wis_by_location=wis_by_loc, wis_places_under_1=sum(1 for x in wis_by_loc if x['ratio'] < 1),
                    longest_release_gap_days=release_gap_days, rows_with_one_release=latest_only))
# the block indahl.ai/forecasters reads (indahl-ai/forecasters.py, rows 'feed'). Text holds no digit. Display only, the cells above decide.
HW = {'all horizons': 'all horizons', 'horizon 0': 'the current week', 'horizon 1': 'one week ahead', 'horizon 2': 'two weeks ahead', 'horizon 3': 'three weeks ahead'}
def fc_row(c, label):
    return dict(kind='coverage', item=label, counts='share of reported weekly flu admissions inside the stated interval', stated=c['stated'], n=c['inside'], of=c['scored'],
                delivered=c['share'], lo=c['lo'], hi=c['hi'], outcome=c['outcome'], interval='moving-block bootstrap over target weeks, as the desk gives it')
_fc = [fc_row(next(c for c in cells if c['cell'] == nm and c['level'] == L and c['side'] == 'final'), '%s interval, %s, final count' % ('outer' if L == '95' else 'middle', HW[nm]))
       for L in ('95', '50') for nm in ('all horizons', 'horizon 0', 'horizon 1', 'horizon 2', 'horizon 3')]
summary['forecasters'] = dict(rows=[r for r in _fc if r['lo'] is not None])
json.dump(dict(generated=STAMP, rows=rows), open('data/flu.json.tmp', 'w')); os.replace('data/flu.json.tmp', 'data/flu.json')
json.dump(summary, open('summary_flu.json.tmp', 'w'), indent=1); os.replace('summary_flu.json.tmp', 'summary_flu.json')
json.dump(dict(summary, updated=STAMP), open('data/flu_live.json.tmp', 'w'), separators=(',', ':')); os.replace('data/flu_live.json.tmp', 'data/flu_live.json')
if PUB:
    env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
    p = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'flu_live', '--path', os.path.join(H, 'data', 'flu_live.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'],
                       cwd=os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'), env=env, capture_output=True, text=True)
    log('flu_live', 'published' if p.returncode == 0 else 'publish FAILED ' + (p.stderr or '')[-200:])
    if p.returncode: STALE.append('publish')
with open('data/flu_history.jsonl', 'a') as f: f.write(json.dumps(dict(t=STAMP, gate=GATE, hub=HUB_COMMIT, rows=len(rows), cells=[(c['cell'], c['level'], c['side'], c['scored'], c['inside'], c['outcome']) for c in cells[:8]], stale=STALE)) + '\n')
log('gates', kg, 'rows', len(rows))
for c in cells[:20]: log('%-16s %s %-5s scored %5d inside %5d above %4d below %4d ct %3d nr %3d [%s, %s] %s' % (c['cell'], c['level'], c['side'], c['scored'], c['inside'], c['above'], c['below'], c['cannot_tell'], c['nothing_returned'], c['lo'], c['hi'], c['outcome']))
for c in wis_cells[:10]: log('WIS %-16s %-5s rows %5d ratio %s [%s, %s] %s' % (c['cell'], c['side'], c['rows'], c['ratio'], c['lo'], c['hi'], c['outcome']))
