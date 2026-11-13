#!/opt/homebrew/bin/python3
"""Referee recount of the TORNADO desk. Independent code (rshp, rgeo, rgrid, rasterize, this file). Writes out/recount.json."""
import sys, os, json, csv, math, time, calendar, pickle, collections as C
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rgeo, rshp, rgrid
RAW = rgrid.D; OUT = '/Users/heuremen/bones-forge/tornado_index_referee/out/'
RAD = 25 * 1.609344; SEED = 987654; NB = 2000
BN = ['under 2', '2 to 5', '5 to 10', '10 to 15', '15 to 30', '30 to 45', '45 to 60', '60 and over']
LV = np.array([0, .02, .05, .10, .15, .30, .45, .60]); BL = LV; BH = np.array([.02, .05, .10, .15, .30, .45, .60, 1.0])
def tt(s): return calendar.timegm(time.strptime(s, '%Y-%m-%d %H:%M:%S'))
# ---------- delivered side ----------
def load_db():
    T = []; cnt = C.Counter()
    for r in csv.DictReader(open(RAW + 'db/1950-2025_actual_tornadoes.csv', newline='')):
        if int(r['yr']) < 2006: continue
        if r['tz'] != '3': cnt['tz_not_3'] += 1; continue
        slat, slon = float(r['slat']), float(r['slon'])
        if slat == 0 or slon == 0: cnt['no_start'] += 1; continue
        elat, elon = float(r['elat']), float(r['elon'])
        if elat == 0 or elon == 0: elat, elon = slat, slon
        t0 = tt(r['date'] + ' ' + r['time']) + 6 * 3600
        try: t1 = tt(r['edat'] + ' ' + r['etime']) + 6 * 3600
        except Exception: t1 = None; cnt['no_end_time'] += 1
        if t1 is not None and t1 <= t0: cnt['end_le_start'] += 1
        T.append((t0, t1, slon, slat, elon, elat, int(r['mag']), int(r['yr'])))
    return T, cnt
def load_prelim():
    T = []; days = []
    d = calendar.timegm((2026, 1, 1, 0, 0, 0))
    for fn in sorted(os.listdir(RAW + 'prelim')):
        ds = fn[:8]; base = calendar.timegm(time.strptime(ds, '%Y%m%d'))
        days.append(ds)
        for r in csv.DictReader(open(RAW + 'prelim/' + fn, newline='', encoding='latin-1')):
            try: hh = int(r['Time']); lat = float(r['Lat']); lon = float(r['Lon'])
            except Exception: continue
            t = base + (hh // 100) * 3600 + (hh % 100) * 60 + (86400 if hh < 1200 else 0)
            T.append((t, None, lon, lat, lon, lat, -9, 2026))
    return T, days
def dstr(t, h): return time.strftime('%Y%m%d', time.gmtime(t - h * 3600))
# ---------- boot ----------
def pct(a): return float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))
def boot_days(num, den, seed, n=NB):
    """Resample integer day indices with replacement (rng.integers + bincount). num, den per-day arrays."""
    D = len(num)
    if D == 0 or den.sum() == 0: return None
    rng = np.random.default_rng(seed); out = np.empty(n)
    for i in range(n):
        w = np.bincount(rng.integers(0, D, D), minlength=D)
        d = w @ den; out[i] = (w @ num) / d if d > 0 else np.nan
    out = out[~np.isnan(out)]; return pct(out)
def boot_block(num, den, L, seed, n=NB):
    """Moving-block bootstrap over contiguous calendar days (num, den include zero days). Block length L."""
    D = len(num); cn = np.concatenate([[0], np.cumsum(num)]); cd = np.concatenate([[0], np.cumsum(den)])
    rng = np.random.default_rng(seed); k = int(math.ceil(D / L)); out = np.empty(n)
    for i in range(n):
        s = rng.integers(0, D - L + 1, k); a = (cn[s + L] - cn[s]).sum(); b = (cd[s + L] - cd[s]).sum(); out[i] = a / b if b > 0 else np.nan
    out = out[~np.isnan(out)]; return pct(out)
def boot_year(num, den, years, seed, n=NB):
    ys = sorted(set(years)); yi = np.array([ys.index(y) for y in years]); sn = np.bincount(yi, weights=num); sd = np.bincount(yi, weights=den)
    rng = np.random.default_rng(seed); out = np.empty(n)
    for i in range(n):
        s = rng.integers(0, len(ys), len(ys)); b = sd[s].sum(); out[i] = sn[s].sum() / b if b > 0 else np.nan
    out = out[~np.isnan(out)]; return pct(out)
def outcome(lo, hi, a, b, days):
    if lo is None or days < 30: return 'CANNOT_TELL'
    if lo > b: return 'ABOVE'
    if hi < a: return 'BELOW'
    if lo >= a and hi <= b: return 'CONSISTENT'
    return 'CANNOT_TELL'
# ---------- events ----------
def events(T, X, Y, days_set, closed):
    """EV[day] -> bool array over points, EV2 for mag>=2. Tornado in valid period 13Z..12Z (23 h) of its day."""
    EV = {d: np.zeros(len(X), bool) for d in days_set}; EV2 = {d: np.zeros(len(X), bool) for d in days_set}; cnt = C.Counter(); mag = C.Counter()
    for (t0, t1, lo0, la0, lo1, la1, m, yr) in T:
        d = dstr(t0, 13); y = int(d[:4])
        if y < 2007: continue
        if closed != (y <= 2025): continue
        base = calendar.timegm(time.strptime(d, '%Y%m%d')) + 13 * 3600
        if t0 - base >= 23 * 3600: cnt['start 12Z to 13Z gap'] += 1; continue
        if d not in EV: cnt['no outlook day'] += 1; continue
        ax, ay = rgeo.fwd(lo0, la0); bx, by = rgeo.fwd(lo1, la1)
        near = rgeo.seg_dist(X, Y, float(ax), float(ay), float(bx), float(by)) <= RAD
        EV[d] |= near
        if m >= 2: EV2[d] |= near
        cnt['placed'] += 1; mag['unrated(-9)' if m < 0 else ('ef2+' if m >= 2 else 'ef0-1')] += 1
    return EV, EV2, cnt, mag
# ---------- band reading ----------
def read_cells(days, B, S, EV, EV2, masks, clim, label=''):
    """days: list of day strings; B,S,EV,EV2 dict day->arrays. Returns dict cell -> reading, plus per-day arrays for block bootstraps."""
    out = {}
    for name, mk in masks.items():
        rows = np.zeros((len(days), 8)); ev = np.zeros((len(days), 8)); sr = np.zeros(len(days)); se = np.zeros(len(days)); bs = np.zeros(len(days)); bc = np.zeros(len(days)); n = 0
        for i, d in enumerate(days):
            b = B[d][mk]; e = EV[d][mk]
            rows[i] = np.bincount(b, minlength=8); ev[i] = np.bincount(b, weights=e, minlength=8)
            s = S[d][mk]; sr[i] = s.sum(); se[i] = (s & EV2[d][mk]).sum()
            o = e.astype(float); bs[i] = ((LV[b] - o) ** 2).sum(); c = clim[d][mk]; bc[i] = ((c - o) ** 2).sum(); n += len(b)
        bands = []
        for j in range(8):
            dj = rows[:, j] > 0; nd = int(dj.sum()); r = int(rows[:, j].sum()); e = int(ev[:, j].sum())
            if r == 0: bands.append(dict(band=BN[j], rows=0, days=0, events=0, freq=None, lo=None, hi=None, outcome='CANNOT_TELL')); continue
            ci = boot_days(ev[dj, j], rows[dj, j], SEED + j)
            bands.append(dict(band=BN[j], rows=r, days=nd, events=e, freq=e / r, lo=ci[0], hi=ci[1], outcome=outcome(ci[0], ci[1], BL[j], BH[j], nd)))
        dj = sr > 0; nd = int(dj.sum())
        if sr.sum() > 0:
            ci = boot_days(se[dj], sr[dj], SEED + 99); hat = dict(rows=int(sr.sum()), days=nd, events=int(se.sum()), freq=se.sum() / sr.sum(), lo=ci[0], hi=ci[1], outcome=outcome(ci[0], ci[1], .10, 1.0, nd))
        else: hat = dict(rows=0)
        # BSS bootstrap
        D = len(days); rng = np.random.default_rng(SEED + 7); r_ = np.empty(NB)
        for i in range(NB):
            w = np.bincount(rng.integers(0, D, D), minlength=D); r_[i] = 1 - (w @ bs) / (w @ bc)
        ci = pct(r_); bss = 1 - bs.sum() / bc.sum()
        out[name] = dict(days=len(days), points=int(mk.sum()), rows=n, bands=bands, hatched=hat, brier=dict(bs=bs.sum() / n, bs_clim=bc.sum() / n, bss=bss, lo=ci[0], hi=ci[1], outcome='ABOVE' if ci[0] > 0 else 'BELOW' if ci[1] < 0 else 'CANNOT_TELL'),
                         band_outcomes=dict(C.Counter(b['outcome'] for b in bands)))
        out[name]['_arrays'] = dict(rows=rows, ev=ev, sr=sr, se=se, bs=bs, bc=bc)
    return out
def climatology(days, EV):
    ym = C.defaultdict(lambda: [0, 0]); mon = C.defaultdict(lambda: [0, 0]); P = len(next(iter(EV.values())))
    S = {}; M = {}
    for d in days:
        k = (int(d[:4]), int(d[4:6])); S[k] = S.get(k, 0) + EV[d].astype(float); ym[k][1] += 1
    for (y, m), v in S.items(): M[m] = M.get(m, 0) + v
    N = {m: sum(ym[k][1] for k in ym if k[1] == m) for m in range(1, 13)}
    cl = {}
    for d in days:
        y, m = int(d[:4]), int(d[4:6]); e = M[m] - S[(y, m)]; n = N[m] - ym[(y, m)][1]; cl[d] = e / n if n else np.zeros(len(e))
    return cl
def strip(o):
    if isinstance(o, dict): return {k: strip(v) for k, v in o.items() if k != '_arrays'}
    if isinstance(o, list): return [strip(v) for v in o]
    if isinstance(o, (np.floating,)): return float(o)
    if isinstance(o, (np.integer,)): return int(o)
    return o
def run_grid(tag, T, variant, subset=None, want_blocks=False):
    P = pickle.load(open(OUT + 'cache/%s.pkl' % tag, 'rb')); X, Y, lon, lat, st = P['grid']; res = P['res'][variant]
    keep = np.ones(len(X), bool)
    if subset == 'desk':
        gx0, gy0 = rgeo.fwd(-125.0, 24.0); gx1, gy1 = rgeo.fwd(-66.5, 49.5); gxa, _ = rgeo.fwd(-125, 49.5); gxb, _ = rgeo.fwd(-66.5, 49.5)
        xmin = math.floor(min(gx0, gxa) / 80) * 80; xmax = max(gx1, gxb) + 80; ymin = math.floor(min(gy0, gy1) / 80) * 80; ymax = rgeo.fwd(-96, 50)[1] + 80
        keep = (X >= xmin) & (X <= xmax) & (Y >= ymin) & (Y <= ymax)
    X, Y, st = X[keep], Y[keep], st[keep]
    days = sorted(d for d in res if '20070101' <= d <= '20251231')
    B = {d: res[d][0][keep] for d in res}; S = {d: res[d][1][keep] for d in res}
    EV, EV2, cnt, mag = events(T, X, Y, set(days), True)
    masks = {'United States': np.ones(len(X), bool), 'Kansas': st == 'KS', 'Tornado Alley': np.isin(st, ['TX', 'OK', 'KS', 'NE', 'SD', 'IA'])}
    cl = climatology(days, EV)
    cells = read_cells(days, B, S, EV, EV2, masks, cl)
    return dict(points=int(len(X)), cell_points={k: int(v.sum()) for k, v in masks.items()}, days=len(days), placement=dict(cnt), mags=dict(mag), cells=cells), (days, B, S, EV, EV2, masks, cl, X, Y, st)
if __name__ == '__main__':
    t_start = time.time()
    T, dbc = load_db(); print('db', len(T), dict(dbc), file=sys.stderr)
    R = {'db_counts': dict(dbc)}
    which = sys.argv[1:] or ['desk', 'full', 'a1300', 'offsets']
    if 'desk' in which:
        r, ctx = run_grid('grid0', T, 'c13', subset='desk'); R['desk_grid_c13'] = r; print('desk done', time.time() - t_start, file=sys.stderr)
        days, B, S, EV, EV2, masks, cl, X, Y, st = ctx
        # block bootstraps on the US 10-15 band, Kansas 10-15, hatched, via calendar-day arrays
        alld = []; t = calendar.timegm((2007, 1, 1, 0, 0, 0))
        while t <= calendar.timegm((2025, 12, 31, 0, 0, 0)): alld.append(time.strftime('%Y%m%d', time.gmtime(t))); t += 86400
        pos = {d: i for i, d in enumerate(alld)}; idx = np.array([pos[d] for d in days]); yrs = [int(d[:4]) for d in days]
        bl = {}
        for cname in ('United States', 'Kansas', 'Tornado Alley'):
            a = r['cells'][cname] if False else None
        cc = read_cells  # noqa
        # recompute arrays for the cells
        arr = {}
        for cname in masks:
            rows = np.zeros((len(days), 8)); ev = np.zeros((len(days), 8)); se = np.zeros(len(days)); sr = np.zeros(len(days)); bs = np.zeros(len(days)); bc = np.zeros(len(days))
            for i, d in enumerate(days):
                mk = masks[cname]; b = B[d][mk]; e = EV[d][mk]; rows[i] = np.bincount(b, minlength=8); ev[i] = np.bincount(b, weights=e, minlength=8)
                s = S[d][mk]; sr[i] = s.sum(); se[i] = (s & EV2[d][mk]).sum(); o = e.astype(float); bs[i] = ((LV[b] - o) ** 2).sum(); bc[i] = ((cl[d][mk] - o) ** 2).sum()
            arr[cname] = (rows, ev, sr, se, bs, bc)
        def full(v):
            z = np.zeros(len(alld)); z[idx] = v; return z
        for cname, j, lab in (('United States', 3, '10 to 15'), ('Kansas', 3, '10 to 15'), ('Tornado Alley', 3, '10 to 15'), ('United States', 4, '15 to 30'), ('United States', 2, '5 to 10')):
            rows, ev = arr[cname][0], arr[cname][1]; key = '%s | %s' % (cname, lab)
            bl[key] = {'day': boot_days(ev[:, j][rows[:, j] > 0], rows[:, j][rows[:, j] > 0], SEED + 5)}
            for L in (7, 14, 30): bl[key]['block%d' % L] = boot_block(full(ev[:, j]), full(rows[:, j]), L, SEED + L)
            bl[key]['year'] = boot_year(ev[:, j], rows[:, j], yrs, SEED + 1)
        for cname in ('United States', 'Kansas', 'Tornado Alley'):
            sr, se = arr[cname][2], arr[cname][3]; key = '%s | hatched' % cname
            bl[key] = {'day': boot_days(se[sr > 0], sr[sr > 0], SEED + 6)}
            for L in (7, 14, 30): bl[key]['block%d' % L] = boot_block(full(se), full(sr), L, SEED + L)
            bl[key]['year'] = boot_year(se, sr, yrs, SEED + 2)
        # BSS block bootstrap: ratio of totals -> 1 - bs/bc ; reuse boot_block on (bs, bc) then transform
        for cname in ('United States', 'Kansas', 'Tornado Alley'):
            bs, bc = arr[cname][4], arr[cname][5]; key = '%s | BSS' % cname; bl[key] = {}
            for L in (7, 14, 30):
                lo, hi = boot_block(full(bs), full(bc), L, SEED + L); bl[key]['block%d' % L] = (1 - hi, 1 - lo)
            lo, hi = boot_year(bs, bc, yrs, SEED + 3); bl[key]['year'] = (1 - hi, 1 - lo)
        R['block_bootstrap'] = bl
        # per-year US table
        yr = []
        for y in range(2007, 2026):
            dd = [d for d in days if d.startswith(str(y))]
            c = read_cells(dd, B, S, EV, EV2, {'United States': masks['United States']}, cl)['United States']
            yr.append(dict(year=y, days=c['days'], rows=c['rows'], bands=[(b['rows'], b['events'], b['outcome']) for b in c['bands']], bss=c['brier']['bss'])); del c
        R['years_us'] = yr
        # nothing returned
        frame = alld; R['nothing_returned_c13'] = [d for d in frame if d not in set(days)]
        R['nothing_returned_c13'] = [d for d in alld if d not in set(days)]
    if 'full' in which:
        r, _ = run_grid('grid0', T, 'c13'); R['full_grid_c13'] = r; print('full done', time.time() - t_start, file=sys.stderr)
    if 'a1300' in which:
        r, _ = run_grid('grid0', T, 'a1300'); R['full_grid_a1300'] = r; print('a1300 done', file=sys.stderr)
    if 'offsets' in which:
        R['offsets'] = {}
        for tag in ('grid40', 'grid2060', 'gridm30'):
            r, _ = run_grid(tag, T, 'c13'); R['offsets'][tag] = r; print(tag, file=sys.stderr)
    fn = OUT + 'recount_%s.json' % ('_'.join(which)); json.dump(strip(R), open(fn, 'w'), indent=1)
    print('wrote', fn, time.time() - t_start)
