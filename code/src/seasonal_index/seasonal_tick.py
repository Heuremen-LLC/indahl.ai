#!/usr/bin/env python3
"""seasonal_tick.py: SEASONAL rider (see PLAN.md). Rerunnable. Installs no timer. Reads CPC's 0.5-month-lead 3-month outlook archive and observed
categories on the 2 by 2 degree grid (refreshed at most once a day), and CPC's stated Heidke scores. Sets each stated category chance beside the
observed category (reliability by bin) and recomputes CPC's Heidke score against the score CPC states.
Writes data/seasonal.json, summary_seasonal.json, data/seasonal_live.json, data/seasonal_history.jsonl.
--offline: no network. --publish: put data/seasonal_live.json in the site KV as seasonal_live, served at /seasonal/live.json. --selftest: rule checks only."""
import os, sys, json, time, math, hashlib, subprocess, urllib.request, collections as C
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
import heuremen_kit as K
OFF = '--offline' in sys.argv; PUB = '--publish' in sys.argv
UA = 'heuremen-seasonal/0.1 (+https://indahl.ai/seasonal)'; RAW = 'data/raw/cpc_verif_grid'
BASE = 'https://www.cpc.ncep.noaa.gov/products/predictions/long_range/tools/briefing/verification/'
VARS = {'temp': 'temperature', 'prec': 'precipitation'}
FILES = [v + s for v in VARS for s in ('01_forecast_above.bi', '01_forecast_below.bi', '01_forecast.bi', '_seas_verif.bi', '01.heidke.txt')]
NX, NY = 36, 19; NREC = NX * NY
BINS = ((0, 25, 'under 25'), (25, 31, '25 to under 31'), (31, 36, '31 to under 36'), (36, 40, '36 to under 40'), (40, 50, '40 to under 50'), (50, 60, '50 to under 60'), (60, 101, '60 and over'))   # labels state the edges (referee R4)
MIN_ROWS = 30; MIN_SEAS = 24; MAX_W = 0.10; BLOCK = 12; REPS = 2000; SEED = 20261110; HSS_TOL = 2.0
NOW = time.time(); STAMP = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(NOW)); STALE = []
def log(*a): print('seasonal:', *a, file=sys.stderr)
def season_name(i):
    m = i % 12; y = 1995 + i // 12; L = 'JFMAMJJASONDJF'; return '%s %d' % (L[m:m + 3], y)
def first_month(i): return '%04d%02d01' % (1995 + i // 12, i % 12 + 1)
def lonlat(j): return 130 - 2 * (j % NX), 20 + 2 * (j // NX)   # west longitude, north latitude

# ---------------- the rule (PLAN.md, Rules) ----------------
# 12 Nov 2026: Faults and Guards 2.0 outcome rule (PLAN_ADDENDUM_std2.md). Returns (outcome, reason). The 0.10 width cap is retired: a point figure with no tolerance has no CONSISTENT.
def cell_outcome(lo, hi, stated, n, seasons):
    if not n or lo is None or stated is None: return K.CANNOT_TELL, K.NO_INTERVAL_FORMABLE
    if n < MIN_ROWS or seasons < MIN_SEAS: return K.CANNOT_TELL, K.TOO_WIDE_TO_RESOLVE
    return K.read(lo, hi, bound=stated, edge='closed')
def hss_outcome(lo, hi):
    return K.read(lo, hi, band=(-HSS_TOL, HSS_TOL), edge='closed')
def heidke(cat, obs, w=None):
    """cat: CPC categories (1, 2, 3, 0) for cells with an observation, obs: -1, 0, 1. -> (non-EC, all, coverage) in percent, or None."""
    w = np.ones(len(cat)) if w is None else w
    fc = cat > 0; T = w[fc].sum()
    if T <= 0: return None, 0.0, 0.0   # every cell equal chances: no non-EC score, coverage 0, so the all score (non-EC x coverage) is 0, as CPC lists it (referee R2)
    Hh = w[fc & ((cat - 2) == obs)].sum(); E = T / 3; ne = 100 * (Hh - E) / (T - E); cov = 100 * T / w.sum()
    return ne, ne * cov / 100, cov
def draws(S, reps=REPS, seed=SEED):
    rng = np.random.default_rng(seed); M = np.zeros((reps, S))
    if S < BLOCK: return M
    nb = math.ceil(S / BLOCK); st = rng.integers(0, S - BLOCK + 1, size=(reps, nb))
    for j in range(BLOCK): np.add.at(M, (np.repeat(np.arange(reps), nb), (st + j).ravel()), 1)
    return M
def boot_ratio(num, den, M):
    a = M @ num; b = M @ den; ok = b > 0
    if ok.sum() < 100: return None, None
    r = a[ok] / b[ok]; return float(np.percentile(r, 2.5)), float(np.percentile(r, 97.5))
def rule_selftest():
    t = [cell_outcome(0.5, 0.6, 0.4, 100, 50) == (K.ABOVE, None), cell_outcome(0.2, 0.3, 0.4, 100, 50) == (K.BELOW, None), cell_outcome(0.36, 0.44, 0.4, 100, 50) == (K.CANNOT_TELL, K.STRADDLES_EDGE),
         cell_outcome(0.2, 0.6, 0.4, 100, 50) == (K.CANNOT_TELL, K.STRADDLES_EDGE), cell_outcome(0.36, 0.44, 0.4, 20, 50) == (K.CANNOT_TELL, K.TOO_WIDE_TO_RESOLVE), cell_outcome(0.36, 0.44, 0.4, 100, 10) == (K.CANNOT_TELL, K.TOO_WIDE_TO_RESOLVE),
         cell_outcome(None, None, 0.4, 0, 0) == (K.CANNOT_TELL, K.NO_INTERVAL_FORMABLE),
         hss_outcome(-1, 1) == (K.CONSISTENT, None), hss_outcome(3, 4) == (K.ABOVE, None), hss_outcome(-4, -3) == (K.BELOW, None), hss_outcome(-1, 3) == (K.CANNOT_TELL, K.STRADDLES_EDGE)]
    o = np.array([-1, 0, 1, 1, 0, -1]); t.append(abs(heidke(o + 2, o)[0] - 100) < 1e-9)
    c3 = np.array([1, 2, 3, 1, 2, 3]); ob3 = np.array([-1, 0, -1, 1, -1, 0]); t.append(abs(heidke(c3, ob3)[0] - 0) < 1e-9)   # 2 of 6 right = chance
    # planted: 4 non-EC cells, 3 right, 2 EC cells -> HSS = 100*(3-4/3)/(4-4/3) = 62.5, coverage 66.67, all 41.67
    r = heidke(np.array([1, 2, 3, 3, 0, 0]), np.array([-1, 0, 1, -1, 0, 1])); t.append(abs(r[0] - 62.5) < 1e-9 and abs(r[2] - 66.6667) < 1e-3 and abs(r[1] - 41.6667) < 1e-3)
    rng = np.random.default_rng(9); S = 200; M = draws(S, 500, 3)
    for p_true, want in ((0.5, (K.CANNOT_TELL, K.STRADDLES_EDGE)), (0.35, (K.BELOW, None))):
        hits = (rng.random((S, 40)) < p_true).sum(1).astype(float); lo, hi = boot_ratio(hits, np.full(S, 40.0), M); t.append(cell_outcome(lo, hi, 0.5, S * 40, S) == want)
    return all(t), t
if '--selftest' in sys.argv:
    ok, t = rule_selftest(); print('rule selftest', 'PASSED' if ok else 'FAILED', t); sys.exit(0 if ok and K.selftest() else 1)

# ---------------- 0. refresh at most once a day ----------------
os.makedirs(RAW, exist_ok=True)
stamp_f = os.path.join(RAW, 'last_fetch')
if not OFF and (not os.path.exists(stamp_f) or NOW - os.path.getmtime(stamp_f) > 86400):
    okall = True
    for n in FILES:
        try:
            with urllib.request.urlopen(urllib.request.Request(BASE + n, headers={'User-Agent': UA}), timeout=120) as r: b = r.read()
            open(os.path.join(RAW, n + '.part'), 'wb').write(b); os.replace(os.path.join(RAW, n + '.part'), os.path.join(RAW, n)); time.sleep(1.0)
        except Exception as e: log('fetch FAILED', n, repr(e)[:120]); STALE.append(n); okall = False
    if okall: open(stamp_f, 'w').write(STAMP)

# ---------------- 1. read ----------------
def rd(n): a = np.fromfile(os.path.join(RAW, n), dtype='<f4'); return a, a.size % NREC == 0
def heidke_txt(n):
    out = {}
    for line in open(os.path.join(RAW, n)):
        p = line.split()
        if len(p) == 4 and p[0].isdigit():
            try: out[p[0]] = dict(non_ec=float(p[1]), all=float(p[2]), coverage=float(p[3]))
            except ValueError: pass
    return out
kg = {}; fmt = True; orient = True; align = True; D = {}
for v in VARS:
    A, a1 = rd(v + '01_forecast_above.bi'); Bv, a2 = rd(v + '01_forecast_below.bi'); Cc, a3 = rd(v + '01_forecast.bi'); O, a4 = rd(v + '_seas_verif.bi')
    fmt &= a1 and a2 and a3 and a4
    A = A.reshape(-1, NREC); Bv = Bv.reshape(-1, NREC); Cc = Cc.reshape(-1, NREC); O = O.reshape(-1, NREC)
    fmt &= A.shape[0] >= O.shape[0] and Bv.shape[0] >= O.shape[0] and Cc.shape[0] >= O.shape[0] and set(np.unique(O).tolist()) <= {-1.0, 0.0, 1.0, -9999.0}
    land = O > -9000; mask0 = land[0]
    orient &= bool((land == mask0).all())
    j = lambda lon, lat: (lat - 20) // 2 * NX + (130 - lon) // 2
    orient &= bool(mask0[j(82, 28)]) and not mask0[j(128, 22)] and not mask0[j(62, 54)]
    hs = heidke_txt(v + '01.heidke.txt'); align &= len(hs) == O.shape[0] and min(hs) == '19950101' if hs else False
    D[v] = dict(A=A, B=Bv, C=Cc, O=O, mask=mask0, hs=hs)
kg['format'] = bool(fmt); kg['orientation'] = bool(orient); kg['alignment'] = bool(align); kg['rule'] = rule_selftest()[0]
GATE = all(kg.values())

# ---------------- 2. reliability rows (vectorised) ----------------
summary_cells = []; hss_rows = []; hss_cells = []; pending = {}; unreadable = {}
for v, d in D.items():
    S = d['O'].shape[0]; m = d['mask']; idx = np.where(m)[0]; lat = np.array([lonlat(j)[1] for j in idx])
    A = d['A'][:S][:, idx]; Bv = d['B'][:S][:, idx]; O = d['O'][:S][:, idx]; N = 100 - A - Bv
    pending[v] = int(d['A'].shape[0] - S)
    bad = (A < 0) | (Bv < 0) | (N < 0) | (N > 100) | ~np.isfinite(A) | ~np.isfinite(Bv)
    unreadable[v] = int(bad.sum())
    M = draws(S)
    cats = (('above', A, 1), ('near', N, 0), ('below', Bv, -1))
    def cell(name, sel_fn):
        num = np.zeros(S); den = np.zeros(S); ssum = 0.0; n = 0
        for cname, P, code in cats:
            sel = sel_fn(cname, P) & ~bad
            num += (sel & (O == code)).sum(1); den += sel.sum(1); ssum += float(P[sel].sum()); n += int(sel.sum())
        seasons = int((den > 0).sum()); stated = ssum / n / 100 if n else None
        lo, hi = boot_ratio(num, den, M) if n else (None, None)
        k = int(num.sum())
        oc = cell_outcome(lo, hi, stated, n, seasons) if GATE else (K.CANNOT_TELL, K.NO_INTERVAL_FORMABLE)
        return dict(variable=v, cell=name, rows=n, seasons=seasons, mean_stated=None if stated is None else round(stated, 4), observed=round(k / n, 4) if n else None, hits=k,
                    lo=None if lo is None else round(lo, 4), hi=None if hi is None else round(hi, 4), outcome=oc[0], reason=oc[1])
    summary_cells.append(dict(cell(VARS[v] + ', leaning', lambda c, P: P >= 40), category='any'))
    for cname, P, code in cats:
        for lo_, hi_, bn in BINS:
            r = cell('%s, %s, stated %s percent' % (VARS[v], cname, bn), lambda c, PP, cn=cname, a=lo_, b=hi_: (PP >= a) & (PP < b) if c == cn else np.zeros_like(PP, dtype=bool))
            r.update(category=cname, bin=bn); summary_cells.append(r)
    # ---------------- 3. Heidke recompute ----------------
    Cc = d['C'][:S][:, idx]; integral = np.isclose(Cc, np.round(Cc)) & (np.round(Cc) >= 0) & (np.round(Cc) <= 3)
    w = np.cos(np.radians(lat))
    diffs_ne = np.full(S, np.nan); diffs_all = np.full(S, np.nan)
    for i in range(S):
        ok = integral[i]; cat = np.round(Cc[i][ok]).astype(int); ob = O[i][ok].astype(int)
        r0 = heidke(cat, ob); rw = heidke(cat, ob, w[ok]); st = d['hs'].get(first_month(i))
        row = dict(variable=v, season=season_name(i), first_month=first_month(i), cells=int(ok.sum()), left_out=int((~ok).sum()))
        if r0: row.update(ours_non_ec=None if r0[0] is None else round(r0[0], 2), ours_all=round(r0[1], 2), ours_coverage=round(r0[2], 2))
        if rw and rw[0] is not None: row.update(weighted_non_ec=round(rw[0], 2), weighted_all=round(rw[1], 2))
        if st: row.update(cpc_non_ec=st['non_ec'], cpc_all=st['all'], cpc_coverage=st['coverage'])
        if r0 and st:
            if r0[0] is not None and math.isfinite(st['non_ec']): diffs_ne[i] = r0[0] - st['non_ec']
            if math.isfinite(st['all']): diffs_all[i] = r0[1] - st['all']
        hss_rows.append(row)
    for nm, dd in (('non-EC score', diffs_ne), ('all score', diffs_all)):
        okd = np.isfinite(dd); num = np.where(okd, dd, 0.0); den = okd.astype(float)
        lo, hi = boot_ratio(num, den, M); mean = float(dd[okd].mean()) if okd.any() else None
        hss_cells.append(dict(variable=v, score=nm, seasons=int(okd.sum()), mean_difference=None if mean is None else round(mean, 3), lo=None if lo is None else round(lo, 3), hi=None if hi is None else round(hi, 3),
                              within_1_point=int((np.abs(dd[okd]) <= 1).sum()), median_abs_difference=round(float(np.median(np.abs(dd[okd]))), 3) if okd.any() else None,
                              outcome=(hss_outcome(lo, hi) if GATE else (K.CANNOT_TELL, K.NO_INTERVAL_FORMABLE))[0], reason=(hss_outcome(lo, hi) if GATE else (K.CANNOT_TELL, K.NO_INTERVAL_FORMABLE))[1]))

# 10 Nov 2026, outside referee (seasonal_index_referee/REFEREE.md R1, R3, R5): display only, added after the data, never used for an outcome.
after = dict(note='Added on 10 Nov 2026 at the outside referee. Display only. No outcome uses them.', observed_shares={}, leaning_split={}, largest_heidke_gap={})
for v, d in D.items():
    S_ = d['O'].shape[0]; idx = np.where(d['mask'])[0]; O_ = d['O'][:S_][:, idx]; A_ = d['A'][:S_][:, idx]; B_ = d['B'][:S_][:, idx]; N_ = 100 - A_ - B_
    after['observed_shares'][v] = dict(above=round(float((O_ == 1).mean()), 4), near=round(float((O_ == 0).mean()), 4), below=round(float((O_ == -1).mean()), 4))
    sp = {}
    for cname, P, code in (('above', A_, 1), ('near', N_, 0), ('below', B_, -1)):
        sel = P >= 40
        if sel.any(): sp[cname] = dict(rows=int(sel.sum()), mean_stated=round(float(P[sel].mean()) / 100, 4), observed=round(float((O_[sel] == code).mean()), 4))
    after['leaning_split'][v] = sp
    rs = [r for r in hss_rows if r['variable'] == v and r.get('ours_non_ec') is not None and r.get('cpc_non_ec') is not None and math.isfinite(r['cpc_non_ec'])]
    if rs:
        w_ = max(rs, key=lambda r: abs(r['ours_non_ec'] - r['cpc_non_ec'])); after['largest_heidke_gap'][v] = dict(season=w_['season'], difference=round(w_['ours_non_ec'] - w_['cpc_non_ec'], 2), cells_left_out=w_['left_out'])
    after['cpc_all_ec_seasons_' + v] = sum(1 for r in hss_rows if r['variable'] == v and r.get('cpc_coverage') == 0)

# ---------------- 4. output ----------------
seal_f = 'data/plan_seal.json'
def g(*a): return subprocess.run(['git'] + list(a), cwd=H, capture_output=True, text=True).stdout.strip()
if not os.path.exists(seal_f) and K.plan_committed('PLAN.md', NOW):
    json.dump(dict(plan_commit=g('log', '-1', '--format=%H', '--', 'PLAN.md'), plan_commit_time=g('log', '-1', '--format=%cI', '--', 'PLAN.md'),
                   plan_sha256=hashlib.sha256(open('PLAN.md', 'rb').read()).hexdigest(), first_comparison=STAMP), open(seal_f, 'w'), indent=1)
seal = json.load(open(seal_f)) if os.path.exists(seal_f) else None
S0 = D['temp']['O'].shape[0]
# REQ-13 (standard 6.7, PLAN_ADDENDUM_std2.md): every reading of the desk. Failed reads (forecasts still waiting, failed fetches) are listed apart and are outside the counts.
NR = ['forecast record waiting, %s' % v for v, k in pending.items() for _ in range(k)] + ['fetch failed, %s' % n for n in STALE if n != 'publish']
REQ13 = K.req13(summary_cells + hss_cells, nothing_returned=NR)
summary = dict(desk='SEASONAL', publisher='Heuremen LLC', generated=STAMP, plan='PLAN.md', plan_seal=seal, plan_unchanged_since_commit=K.plan_committed('PLAN.md'),
    claim=dict(source='NOAA Climate Prediction Center, 3-month outlooks at 0.5-month lead, 2 by 2 degree grid', stated='chance of above, near and below normal; Heidke skill score per season',
               delivered='observed tercile per grid cell and season (CPC verification archive)'),
    frame=dict(bins=[b[2] for b in BINS], min_rows=MIN_ROWS, min_seasons=MIN_SEAS, max_width=MAX_W, block_seasons=BLOCK, replicates=REPS, seed=SEED, hss_tolerance_points=HSS_TOL, rule='PLAN_ADDENDUM_std2.md', width_cap_retired=True),
    gates=dict(kg, passed=GATE),
    sources=dict(seasons_scored=S0, first_season=season_name(0), last_season=season_name(S0 - 1), forecasts_waiting=pending, unreadable_rows=unreadable,
                 land_cells=int(D['temp']['mask'].sum()), fetched=open(stamp_f).read() if os.path.exists(stamp_f) else None, stale=STALE),
    cells=summary_cells, heidke=hss_cells, req13=dict(REQ13, failed_reads=NR), after_data=after)
summary['forecasters'] = dict(rows=[dict(kind='probability', item='%s, any category stated at forty percent or more' % VARS[c['variable']], counts='share of grid cells where the leaning category was observed',
                                         stated=c['mean_stated'], n=c['hits'], of=c['rows'], delivered=c['observed'], lo=c['lo'], hi=c['hi'], outcome=c['outcome'], reason=c['reason'], req13=REQ13,
                                         interval='moving-block bootstrap over seasons, as the desk gives it') for c in summary_cells if c['cell'].endswith('leaning') and c['lo'] is not None])
json.dump(dict(generated=STAMP, heidke_rows=hss_rows), open('data/seasonal.json.tmp', 'w')); os.replace('data/seasonal.json.tmp', 'data/seasonal.json')
json.dump(summary, open('summary_seasonal.json.tmp', 'w'), indent=1); os.replace('summary_seasonal.json.tmp', 'summary_seasonal.json')
json.dump(dict(summary, updated=STAMP), open('data/seasonal_live.json.tmp', 'w'), separators=(',', ':')); os.replace('data/seasonal_live.json.tmp', 'data/seasonal_live.json')
if PUB:
    env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
    p = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'seasonal_live', '--path', os.path.join(H, 'data', 'seasonal_live.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'],
                       cwd=os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'), env=env, capture_output=True, text=True)
    log('seasonal_live', 'published' if p.returncode == 0 else 'publish FAILED ' + (p.stderr or '')[-200:])
    if p.returncode: STALE.append('publish')
with open('data/seasonal_history.jsonl', 'a') as f: f.write(json.dumps(dict(t=STAMP, gate=GATE, seasons=S0, lean=[(c['variable'], c['rows'], c['observed'], c['outcome'], c['reason']) for c in summary_cells if c['cell'].endswith('leaning')], stale=STALE)) + '\n')
log('gates', kg, 'seasons', S0, 'pending', pending, 'unreadable', unreadable)
for c in summary_cells: log('%-52s rows %6d seasons %3d stated %s observed %s [%s, %s] %s' % (c['cell'], c['rows'], c['seasons'], c['mean_stated'], c['observed'], c['lo'], c['hi'], c['outcome'] + (' (%s)' % c['reason'] if c['reason'] else '')))
for c in hss_cells: log('HSS %s %-12s seasons %d mean diff %s [%s, %s] within 1 pt %d median |d| %s %s' % (c['variable'], c['score'], c['seasons'], c['mean_difference'], c['lo'], c['hi'], c['within_1_point'], c['median_abs_difference'], c['outcome']))
