#!/usr/bin/env python3
"""tiktok_tick.py: SOCIAL section 3, TikTok's quarterly enforcement report against its statements of reasons in the EU DSA
Transparency Database. Rules: PLAN.md and its addenda (read them first). Rerunnable. Installs no timer.

  .venv/bin/python -I tiktok_tick.py            fetch what changed (tiktok_fetch.py), then rebuild every output
  .venv/bin/python -I tiktok_tick.py --no-fetch rebuild from files on disk only

Outputs: data/tiktok.json (every row), summary_tiktok.json, section_tiktok.html (fragment for /social), data/components.json.
"""
import os, sys, csv, json, glob, time, math, hashlib, datetime as D, html as HT

H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H)
sys.path.insert(0, H)
import heuremen_kit as K

RAW = os.path.join(H, 'data', 'raw')
EU = {'Austria': 'AT', 'Belgium': 'BE', 'Bulgaria': 'BG', 'Croatia': 'HR', 'Cyprus': 'CY', 'Czech Republic': 'CZ', 'Czechia': 'CZ',
      'Denmark': 'DK', 'Estonia': 'EE', 'Finland': 'FI', 'France': 'FR', 'Germany': 'DE', 'Greece': 'GR', 'Hungary': 'HU',
      'Ireland': 'IE', 'Italy': 'IT', 'Latvia': 'LV', 'Lithuania': 'LT', 'Luxembourg': 'LU', 'Malta': 'MT', 'Netherlands': 'NL',
      'Poland': 'PL', 'Portugal': 'PT', 'Romania': 'RO', 'Slovakia': 'SK', 'Slovenia': 'SI', 'Spain': 'ES', 'Sweden': 'SE'}
EFTA = {'Norway': 'NO', 'Iceland': 'IS', 'Liechtenstein': 'LI'}
EU_NAMES = sorted(set(n for n in EU if n != 'Czechia'))
CODE_NAME = {v: k for k, v in list(EU.items()) + list(EFTA.items()) if k != 'Czechia'}
LAB = {1: 'Jan-Mar', 2: 'Apr-Jun', 3: 'Jul-Sep', 4: 'Oct-Dec'}
QUARTERS = ['2023Q3', '2023Q4', '2024Q1', '2024Q2', '2024Q3', '2024Q4', '2025Q1', '2025Q2', '2025Q3', '2025Q4', '2026Q1', '2026Q2', '2026Q3', '2026Q4']
MEASURES = ['videos_removed', 'automated_removals', 'automated_share', 'proactive_rate', 'within_24h_rate']
SHARE = {'automated_share', 'proactive_rate', 'within_24h_rate'}
M_COUNT, M_SHARE, ROUND = 0.05, 0.01, 0.0005
DB_OPEN = D.date(2023, 9, 25)   # first statements; checked against the data in known_good_db
MNAME = {'videos_removed': 'Videos removed', 'automated_removals': 'Automated removals', 'automated_share': 'Automated share of removals',
         'proactive_rate': 'Removed before any report', 'within_24h_rate': 'Removed within 24 hours of posting'}


def qinfo(q):
    y, n = int(q[:4]), int(q[5])
    a = D.date(y, 3 * n - 2, 1)
    b = (D.date(y + (n == 4), (3 * n) % 12 + 1, 1) - D.timedelta(days=1))
    return dict(q=q, period='%s %d' % (LAB[n], y), a=a, b=b, label='%s to %s %d' % (LAB[n][:3], LAB[n][4:], y))


def fnum(x):
    return '{:,}'.format(int(round(x))) if x is not None else ''


def fpct(x, d=1):
    return ('%.' + str(d) + 'f%%') % (100 * x) if x is not None else ''


# ------------------------------------------------------------------ stated side
def load_releases():
    rel = {}
    for d in sorted(glob.glob(os.path.join(RAW, 'tiktok_cger', 'x_*'))):
        q = os.path.basename(d)[2:]
        fs = [f for f in glob.glob(os.path.join(d, '*.csv'))]
        if not fs:
            continue
        rows = list(csv.DictReader(open(fs[0], encoding='utf-8-sig')))
        iss = 'Issue' if 'Issue' in rows[0] else 'Issue policy'
        rel[q] = dict(q=q, file=os.path.basename(fs[0]), zip=q + '.zip', rows=rows, iss=iss)
    return rel


def stated_cells(R, period):
    """All cells PLAN.md reads from one release for one period: per market and global."""
    iss = R['iss']; out = {}
    for r in R['rows']:
        if r['Period'] != period or r['Policy type'] != 'All' or r[iss] != 'All':
            continue
        met, tt, t, loc, mk = r['Metric'], r['Task type'], r['Task'], r['Location'], r['Market']
        try:
            v = float(r['Result'])
        except ValueError:
            continue
        key = None
        if met == 'Total videos removed' and tt == 'All' and t == 'All': key = 'T'
        elif met == 'Total videos removed' and t == 'Automation': key = 'AUTO'
        elif met == 'Total videos removed' and t == 'AI Moderation': key = 'AI'
        elif met == 'Proactive removal rate' and t == 'All': key = 'PRO'
        elif met == 'Removal rate within 24 hours' and t == 'All': key = 'W24'
        if key is None:
            continue
        m = 'GLOBAL' if (loc == 'All' and mk == 'All') else (mk if loc == 'Market' else None)
        if m is None:
            continue
        if (m, key) in out and out[(m, key)] != v:
            out[(m, key, 'dup')] = v
        out[(m, key)] = v
    return out


def market_values(cells):
    mk = {}
    for k, v in cells.items():
        if len(k) == 2 and k[0] != 'GLOBAL':
            mk.setdefault(k[0], {})[k[1]] = v
    return mk


def stated_eu(cells, q, rel_file):
    """Stated EU total (point and interval) for all measures, per PLAN.md rows 1 and Addendum 1."""
    mk = market_values(cells)
    listed_all = {m: v['T'] for m, v in mk.items() if 'T' in v}
    g = cells.get(('GLOBAL', 'T'))
    yr = int(q[:4])
    B = 49999 if yr >= 2026 else (min(listed_all.values()) if listed_all else None)
    remainder = (g - sum(listed_all.values())) if g is not None else None
    pops = {'EU': EU_NAMES, 'EEA': EU_NAMES + sorted(EFTA)}
    res = {}
    for pop, names in pops.items():
        L = [n for n in names if n in listed_all]
        U = [n for n in names if n not in listed_all]
        cap = len(U) * B if B is not None else None
        if remainder is not None and cap is not None:
            cap = min(cap, max(0.0, remainder))
        T = sum(mk[n]['T'] for n in L)
        auto_lo = sum(mk[n].get('AUTO', 0) + mk[n].get('AI', 0) for n in L if 'AUTO' in mk[n])
        auto_hi = sum((mk[n].get('AUTO', 0) + mk[n].get('AI', 0)) if 'AUTO' in mk[n] else mk[n]['T'] for n in L)
        r = dict(listed=L, unlisted=U, B=B, U_cap=cap, T=T, auto_lo=auto_lo, auto_hi=auto_hi)
        for key, nm in (('PRO', 'proactive_rate'), ('W24', 'within_24h_rate')):
            Kpt = sum(mk[n][key] * mk[n]['T'] for n in L if key in mk[n]); Tk = sum(mk[n]['T'] for n in L if key in mk[n])
            Klo = sum(max(0, mk[n][key] - ROUND) * mk[n]['T'] for n in L if key in mk[n])
            Khi = sum(min(1, mk[n][key] + ROUND) * mk[n]['T'] for n in L if key in mk[n])
            Tn = sum(mk[n]['T'] for n in L if key not in mk[n])
            r[nm] = dict(point=Kpt / Tk if Tk else None, lo=Klo / (Tk + Tn + cap) if (Tk + Tn + cap) else None,
                         hi=(Khi + Tn + cap) / (Tk + Tn + cap) if (Tk + Tn + cap) else None)
        apt = sum(mk[n].get('AUTO', 0) + mk[n].get('AI', 0) for n in L)
        r['automated_share'] = dict(point=apt / T if T else None, lo=auto_lo / (T + cap) if (T + cap) else None,
                                    hi=(auto_hi + cap) / (T + cap) if (T + cap) else None)
        res[pop] = r
    e, x = res['EU'], res['EEA']
    out = {
        'videos_removed': dict(point=e['T'], lo=e['T'], hi=x['T'] + x['U_cap']),
        'automated_removals': dict(point=sum(mk[n].get('AUTO', 0) + mk[n].get('AI', 0) for n in e['listed']), lo=e['auto_lo'], hi=x['auto_hi'] + x['U_cap']),
    }
    for nm in SHARE:
        out[nm] = dict(point=e[nm]['point'], lo=min(e[nm]['lo'], x[nm]['lo']), hi=max(e[nm]['hi'], x[nm]['hi']))
    detail = dict(file=rel_file, listed_eu={n: mk[n] for n in e['listed']}, unlisted_eu=e['unlisted'],
                  efta={n: mk.get(n, {}) for n in EFTA}, B=B, global_total=g, listed_all_sum=sum(listed_all.values()),
                  n_listed_all=len(listed_all), unlisted_cap_eu=e['U_cap'], unlisted_cap_eea=x['U_cap'])
    return out, detail


# ------------------------------------------------------------------ delivered side
SETS = {
    'lower': "dv_removed and ct_video and not ct_ad and decision_ground = 'DECISION_GROUND_INCOMPATIBLE_CONTENT'",
    'point': "dv_removed and ct_video and not ct_ad",
    'upper': ("dv_removed and not ct_ad and (ct_video or ct_image or ct_synthetic_media or (ct_other and not "
              "(ct_account or ct_ad or ct_link or ct_sticker or ct_hashtag or ct_product or ct_app or ct_text or ct_audio)))"),
}


def windows(qi):
    a, b = qi['a'], qi['b']; d1 = D.timedelta(days=1)
    return {'application': ("application_day between DATE '%s' and DATE '%s'" % (a, b)),
            'application_minus_1d': ("application_day between DATE '%s' and DATE '%s'" % (a - d1, b - d1)),
            'application_plus_1d': ("application_day between DATE '%s' and DATE '%s'" % (a + d1, b + d1)),
            'created': ("created_day between DATE '%s' and DATE '%s'" % (a, b))}


def db():
    import duckdb
    con = duckdb.connect()
    fs = sorted(glob.glob(os.path.join(RAW, 'dsa_tiktok', 'complete_*.parquet')))
    ss = sorted(glob.glob(os.path.join(RAW, 'dsa_tiktok', 'simple_*.parquet')))
    con.execute("create view c as select * from read_parquet([%s], union_by_name=true)" % ','.join("'%s'" % f for f in fs))
    con.execute("create view s as select * from read_parquet([%s], union_by_name=true)" % ','.join("'%s'" % f for f in ss))
    return con, fs, ss


def agg(con, where):
    r = con.execute("""select coalesce(sum(n),0), coalesce(sum(n) filter (where automated_decision='AUTOMATED_DECISION_FULLY'),0),
        coalesce(sum(n) filter (where source_type='SOURCE_VOLUNTARY'),0), coalesce(sum(n) filter (where dd=0),0),
        coalesce(sum(n) filter (where dd between 0 and 1),0), coalesce(sum(n) filter (where dd is null or dd<0),0) from c where """ + where).fetchone()
    return dict(n=int(r[0]), fully=int(r[1]), voluntary=int(r[2]), d0=int(r[3]), d01=int(r[4]), dbad=int(r[5]))


def delivered_eu(con, qi):
    W = windows(qi); grid = {}
    for sn, sw in SETS.items():
        for wn, ww in W.items():
            grid[(sn, wn)] = agg(con, '(%s) and (%s)' % (sw, ww))
    out = ranges(grid, ('application', 'application_minus_1d', 'application_plus_1d'))          # Addendum 2.3: decision date only
    out_sub = ranges(grid, ('application', 'application_minus_1d', 'application_plus_1d', 'created'))  # plan as committed
    S = grid[('point', 'created')]
    by_sub = dict(videos_removed=S['n'], automated_removals=S['fully'], automated_share=S['fully'] / S['n'] if S['n'] else None,
                  proactive_rate=S['voluntary'] / S['n'] if S['n'] else None, within_24h_rate=None)
    # Addendum 2.2: statements created on 1-2 Nov 2026 are not in the database; allowance on the upper end
    allow = {}
    if qi['b'] < D.date(2026, 11, 1):
        for key in ('n', 'fully'):
            nb = [agg(con, "(%s) and application_day between DATE '%s' and DATE '%s' and created_day = DATE '%s'" % (SETS['upper'], qi['a'] - D.timedelta(days=1), qi['b'] + D.timedelta(days=1), d))[key]
                  for d in ('2026-10-31', '2026-11-03')]
            allow[key] = 2 * max(nb)
        out['videos_removed']['hi'] += allow['n']; out['automated_removals']['hi'] += allow['fully']
        out_sub['videos_removed']['hi'] += allow['n']; out_sub['automated_removals']['hi'] += allow['fully']
    return out, out_sub, by_sub, allow, {'%s|%s' % k: v for k, v in grid.items()}


def ranges(grid, wins):
    P = grid[('point', 'application')]
    def share(g, k):
        return g[k] / g['n'] if g['n'] else None
    G = {k: v for k, v in grid.items() if k[1] in wins}
    out = {
        'videos_removed': dict(point=P['n'], lo=min(G[('lower', w)]['n'] for w in wins), hi=max(G[('upper', w)]['n'] for w in wins)),
        'automated_removals': dict(point=P['fully'], lo=min(G[('lower', w)]['fully'] for w in wins), hi=max(G[('upper', w)]['fully'] for w in wins)),
    }
    for nm, k in (('automated_share', 'fully'), ('proactive_rate', 'voluntary')):
        vals = [share(g, k) for g in G.values() if g['n']]
        out[nm] = dict(point=share(P, k), lo=min(vals) if vals else None, hi=max(vals) if vals else None)
    v0 = [g['d0'] / g['n'] for g in G.values() if g['n']]; v1 = [g['d01'] / g['n'] for g in G.values() if g['n']]
    out['within_24h_rate'] = dict(point=None, lo=min(v0) if v0 else None, hi=max(v1) if v1 else None,
                                  bad_share=(P['dbad'] / P['n']) if P['n'] else None, same_day=share(P, 'd0'), next_day=share(P, 'd01'))
    return out


def components(con, qi):
    """Item by item, before any netting: the point set split every way PLAN.md names, plus neighbours that are not added."""
    a, b = qi['a'], qi['b']; aw = "application_day between DATE '%s' and DATE '%s'" % (a, b)
    def q(sql):
        return [list(x) for x in con.execute(sql).fetchall()]
    pt = SETS['point']
    return dict(
        by_application_month=q("select strftime(application_day, '%%Y-%%m') m, sum(n) from c where %s and %s group by 1 order by 1" % (pt, aw)),
        filed_after_quarter=q("select strftime(created_day, '%%Y-%%m') m, sum(n) from c where %s and %s and created_day > DATE '%s' group by 1 order by 1" % (pt, aw, b))[:24],
        filed_in_quarter_decided_before=q("select sum(n) from c where %s and created_day between DATE '%s' and DATE '%s' and application_day < DATE '%s'" % (pt, a, b, a)),
        content_types_removed=q("""select case when ct_ad then 'ad' when ct_video and ct_image then 'video and image' when ct_video then 'video'
            when ct_image then 'image' when ct_synthetic_media then 'synthetic media' when ct_text then 'text' when ct_account then 'account'
            when ct_audio then 'audio' when ct_other then 'other' else 'rest' end k, sum(n) from c where dv_removed and %s group by 1 order by 2 desc""" % aw),
        video_disabled_not_removed=q("select sum(n) from c where ct_video and not ct_ad and dv_disabled and not dv_removed and %s" % aw),
        ground=q("select decision_ground, sum(n) from c where %s and %s group by 1 order by 2 desc" % (pt, aw)),
        territorial_scope=q("""select case when territorial_scope in ('EEA','EEA_no_IS','EU') then territorial_scope when territorial_scope='' then 'blank'
            when length(territorial_scope)=2 then 'one country' else 'other list' end k, sum(n) from c where %s and %s group by 1 order by 2 desc""" % (pt, aw)),
        automated_decision=q("select automated_decision, sum(n) from c where %s and %s group by 1 order by 2 desc" % (pt, aw)),
        automated_detection=q("select automated_detection, sum(n) from c where %s and %s group by 1 order by 2 desc" % (pt, aw)),
        source_type=q("select source_type, sum(n) from c where %s and %s group by 1 order by 2 desc" % (pt, aw)),
        days_posted_to_decision=q("select coalesce(cast(dd as varchar),'missing') k, sum(n) from c where %s and %s group by 1 order by 1" % (pt, aw)),
        content_language=q("select coalesce(content_language,'missing'), sum(n) from c where %s and %s group by 1 order by 2 desc limit 5" % (pt, aw)),
        filing_lag_months=q("select date_diff('month', date_trunc('month', application_day), date_trunc('month', created_day)) k, sum(n) from c where %s and %s group by 1 order by 1" % (pt, aw)),
    )


def delivered_market(con, qi, code):
    """Statements placed in one market: territorial scope exactly that country (PLAN.md Markets)."""
    W = windows(qi)
    single = agg(con, "(%s) and (%s) and territorial_scope = '%s'" % (SETS['point'], W['application'], code))
    unplaced = agg(con, "(%s) and (%s) and territorial_scope <> '%s'" % (SETS['point'], W['application'], code))
    if single['n'] == 0:
        return None, single, unplaced
    lo = min(agg(con, "(%s) and (%s) and territorial_scope = '%s'" % (SETS['lower'], w, code))['n'] for w in W.values())
    hi = max(agg(con, "(%s) and (%s) and (territorial_scope in ('EEA','EU','') or (territorial_scope='EEA_no_IS' and '%s'<>'IS') or list_contains(string_split(territorial_scope,'_'),'%s'))" % (SETS['upper'], w, code, code))['n'] for w in W.values())
    return dict(point=single['n'], lo=lo, hi=hi), single, unplaced


# ------------------------------------------------------------------ post hoc (DEFINED AFTER THE DATA, 10 Nov 2026)
def posthoc_load():
    f = os.path.join(H, 'data', 'posthoc_daycheck.json')
    return json.load(open(f)) if os.path.exists(f) else None


def posthoc_delivered(con, qi, ph, agg_days):
    """TikTok's own published daily totals (download page, platform filter) in place of the committed day check. Days where the aggregate
    holds more than TikTok's published total can come off the lower end (capped at matched statements created that day); days where it
    holds fewer add their shortfall to the upper end; days with no published total can come off the lower end in full."""
    pub = ph['published']; a = qi['a']; z = add_months(qi['b'], 3)
    days = [str(a + D.timedelta(days=i)) for i in range((z - a).days + 1)]
    exc = {d: agg_days.get(d, 0) - pub[d] for d in days if d in pub and agg_days.get(d, 0) > pub[d]}
    short = {d: pub[d] - agg_days.get(d, 0) for d in days if d in pub and agg_days.get(d, 0) < pub[d] and d <= str(max(agg_days))}
    unver = [d for d in days if d not in pub and agg_days.get(d, 0) > 0]
    U = sum(short.values())
    W = {k: v for k, v in windows(qi).items() if k != 'created'}
    flag = sorted(set(exc) | set(unver))
    res = {}
    for sn, sw in SETS.items():
        for wn, ww in W.items():
            base = agg(con, '(%s) and (%s)' % (sw, ww))
            X = dict(n=0, fully=0, voluntary=0, d0=0, d01=0, n_nonfully=0, n_nonvol=0, n_nond0=0, n_nond01=0)
            if flag:
                per = con.execute("""select strftime(created_day,'%%Y-%%m-%%d') d, coalesce(sum(n),0), coalesce(sum(n) filter (where automated_decision='AUTOMATED_DECISION_FULLY'),0),
                    coalesce(sum(n) filter (where source_type='SOURCE_VOLUNTARY'),0), coalesce(sum(n) filter (where dd=0),0), coalesce(sum(n) filter (where dd between 0 and 1),0)
                    from c where (%s) and (%s) and strftime(created_day,'%%Y-%%m-%%d') in (%s) group by 1""" % (sw, ww, ','.join("'%s'" % d for d in flag))).fetchall()
                for d, n, fu, vo, d0, d01 in per:
                    cap = exc.get(d, n)
                    X['n'] += min(cap, n); X['fully'] += min(cap, fu); X['voluntary'] += min(cap, vo); X['d0'] += min(cap, d0); X['d01'] += min(cap, d01)
                    X['n_nonfully'] += min(cap, n - fu); X['n_nonvol'] += min(cap, n - vo); X['n_nond0'] += min(cap, n - d0); X['n_nond01'] += min(cap, n - d01)
            res[(sn, wn)] = (base, X)
    def cnt(key, setname, hi):
        vals = [(b[key] + U) if hi else (b[key] - x[key]) for (sn, wn), (b, x) in res.items() if sn == setname]
        return max(vals) if hi else min(vals)
    def share_rng(kk, nonkk_key, kk_hi=None, nonkk_hi_key=None):
        los, his = [], []
        for (b, x) in res.values():
            if not b['n']:
                continue
            k, n = b[kk], b['n']
            los.append(max(0, k - x[kk]) / (n - x[kk] + U))
            kh = b[kk_hi] if kk_hi else k
            nh = x[nonkk_hi_key] if nonkk_hi_key else x[nonkk_key]
            his.append(min(1.0, (kh + U) / (n - nh + U)))
        return (min(los) if los else None, max(his) if his else None)
    out = {'videos_removed': dict(lo=cnt('n', 'lower', False), hi=cnt('n', 'upper', True)),
           'automated_removals': dict(lo=cnt('fully', 'lower', False), hi=cnt('fully', 'upper', True))}
    lo, hi = share_rng('fully', 'n_nonfully'); out['automated_share'] = dict(lo=lo, hi=hi)
    lo, hi = share_rng('voluntary', 'n_nonvol'); out['proactive_rate'] = dict(lo=lo, hi=hi)
    lo, hi = share_rng('d0', 'n_nond0', 'd01', 'n_nond01'); out['within_24h_rate'] = dict(lo=lo, hi=hi)
    note = dict(excess_days={d: exc[d] for d in sorted(exc)}, shortfall_days={d: short[d] for d in sorted(short)}, unverified_days=unver, shortfall_total=U)
    return out, note


# ------------------------------------------------------------------ outcome
def outcome(S, Dl, share):
    """PLAN.md Outcomes: gap interval [D_lo - S_hi, D_hi - S_lo] against zero and the material size m."""
    if S is None or Dl is None or None in (S.get('lo'), S.get('hi'), Dl.get('lo'), Dl.get('hi')) or S.get('point') is None:
        return K.CANNOT_TELL, None, None, None
    g_lo, g_hi = Dl['lo'] - S['hi'], Dl['hi'] - S['lo']
    m = M_SHARE if share else M_COUNT * S['point']
    if g_lo > 0:
        oc, mat = K.ABOVE, ('yes' if g_lo > m else ('no' if g_hi <= m else 'cannot tell'))
    elif g_hi < 0:
        oc, mat = K.BELOW, ('yes' if g_hi < -m else ('no' if g_lo >= -m else 'cannot tell'))
    elif g_lo >= -m and g_hi <= m:
        oc, mat = K.CONSISTENT, 'no'
    else:
        oc, mat = K.CANNOT_TELL, None
    return oc, g_lo, g_hi, mat


# ------------------------------------------------------------------ known-good
def known_good_tiktok(rel):
    out = []
    c2 = stated_cells(rel['2026Q2'], 'Apr-Jun 2026') if '2026Q2' in rel else {}
    t, a, i = c2.get(('GLOBAL', 'T')), c2.get(('GLOBAL', 'AUTO')), c2.get(('GLOBAL', 'AI'))
    ok1 = bool(t) and round((a + i) / t, 3) == 0.974
    out.append(dict(check='Apr-Jun 2026 global (Automation + AI Moderation) / total rounds to 97.4%, as TikTok\'s report page states',
                    value=(a + i) / t if t else None, passed=ok1, source='2026Q2_raw_data_cger_English.csv'))
    vals = [stated_cells(rel[q], 'Jan-Mar 2026').get(('GLOBAL', 'T')) for q in ('2026Q1', '2026Q2') if q in rel]
    ok2 = len(vals) == 2 and all(v == 184012576 for v in vals)
    out.append(dict(check='Jan-Mar 2026 global total is 184,012,576 in the 2026Q1 and 2026Q2 releases', value=vals, passed=ok2,
                    source='2026Q1_raw_data_cger_English.csv, 2026Q2_raw_data_cger_English.csv'))
    return out


PUBLISHED_OWN = os.path.join(H, 'data', 'published_daily_totals.json')
PUBLISHED = PUBLISHED_OWN if os.path.exists(PUBLISHED_OWN) else os.path.expanduser('~/bones-forge/social_index/dsa/data/raw/docs/download_page/daily_totals_published.json')


def known_good_db(con):
    out = []
    cm = dict(con.execute("select strftime(created_day,'%Y-%m'), sum(n) from c group by 1").fetchall())
    sm = dict(con.execute("select strftime(created_day,'%Y-%m'), sum(n) from s group by 1").fetchall())
    months = sorted(set(cm) | set(sm))
    bad = [(m, cm.get(m), sm.get(m)) for m in months if cm.get(m) != sm.get(m)]
    out.append(dict(check='KG3 as committed: TikTok statements per month, complete aggregates equal simple aggregates (the dashboard feed), every month read',
                    value=dict(months=len(months), mismatched=bad[:12]), passed=len(months) > 0 and not bad, as_committed=True, superseded_by='KG3-days (Addendum 2.1)'))
    # KG3-days (a): per day, complete equals simple, or simple is an exact 2x or 3x (a repeated append)
    cd = dict(con.execute("select created_day, sum(n) from c group by 1").fetchall())
    sd = dict(con.execute("select created_day, sum(n) from s group by 1").fetchall())
    reps, fail_a = [], []
    for d in sorted(set(cd) | set(sd)):
        x, y = cd.get(d), sd.get(d)
        if x == y:
            continue
        if x and y and any(y == k * x for k in (2, 3)):
            reps.append((str(d), int(x), int(y)))
        else:
            fail_a.append((str(d), x, y))
    # KG3-days (b): every platform's per-day total in the complete aggregate against the Commission's published daily totals
    mine = {}
    for f in glob.glob(os.path.join(RAW, 'dsa_tiktok', 'complete_*_alldays.json')):
        mine.update(json.load(open(f)))
    pub = json.load(open(PUBLISHED)) if os.path.exists(PUBLISHED) else {}
    lo_day = min(mine) if mine else None
    fail_b, checked, extra_fail, extra_checked = [], 0, [], 0
    for d, v in sorted(pub.items()):
        if lo_day is None or d < lo_day or d > max(mine):
            continue
        m = mine.get(d)
        bad = m is None or abs(m - v) > 0.01 * v
        if d < '2024-02-11':        # Addendum 2.1 commits (b) to the days section 1's file covers, from 11 February 2024
            extra_checked += 1
            if bad:
                extra_fail.append((d, m, v))
            continue
        checked += 1
        if bad:
            fail_b.append((d, m, v))
    failed_days = sorted(set([x[0] for x in fail_a] + [x[0] for x in fail_b]))
    out.append(dict(check='KG3-days (a): TikTok statements per day, complete equals simple, or simple holds an exact 2x or 3x (repeated append)',
                    value=dict(repeated_append_days=reps, failed=fail_a[:20]), passed=not fail_a, local=True))
    out.append(dict(check='KG3-days (b): all platforms per day, complete aggregate within 1% of the Commission\'s published daily total, days from 11 February 2024',
                    value=dict(days_checked=checked, failed=fail_b[:20], published_file=PUBLISHED if pub else 'not found'), passed=bool(pub) and checked > 0 and not fail_b, local=True))
    out.append(dict(check='Defined after the data, informational only: the same comparison for 25 September 2023 to 10 February 2024 (our own copy of the published totals reaches back that far)',
                    value=dict(days_checked=extra_checked, failed=extra_fail[:20]), passed=not extra_fail, info=True, defined_after_the_data=True))
    octo = None
    f = os.path.expanduser('~/bones-forge/research_social/samples/dsa_agg/sor_platform_day_2026-10.csv')
    if os.path.exists(f):
        rows = list(csv.DictReader(open(f)))
        pk = [k for k in rows[0] if 'platform' in k.lower()][0]; nk = [k for k in rows[0] if k.lower() in ('count', 'n', 'statements', 'sum')]
        nk = nk[0] if nk else list(rows[0])[-1]
        octo = sum(int(float(r[nk])) for r in rows if r[pk] == 'TikTok')
    ok = cm.get('2026-10') == 17056103 and octo == 17056103
    out.append(dict(check='October 2026 TikTok statements equal 17,056,103 (sor_platform_day_2026-10.csv)', value=dict(complete=cm.get('2026-10'), csv=octo), passed=ok))
    first = con.execute("select min(created_day) from c").fetchone()[0]
    out.append(dict(check='First TikTok statement in the database', value=str(first), passed=True, info=True))
    return out, cm, failed_days


# ------------------------------------------------------------------ build
def build(fetch=True):
    if fetch:
        import subprocess
        subprocess.run([sys.executable, '-I', os.path.join(H, 'tiktok_fetch.py')], check=False)
        subprocess.run([sys.executable, '-I', os.path.join(H, 'posthoc_daycheck.py')], check=False)   # defined after the data, see PLAN.md Addendum 3
    rel = load_releases()
    con, cfiles, sfiles = db()
    kg_t = known_good_tiktok(rel); kg_d, cm, failed_days = known_good_db(con)
    ph = posthoc_load()
    agg_days = {str(d): int(n) for d, n in con.execute("select created_day, sum(n) from c group by 1").fetchall()}
    gate = all(k['passed'] for k in kg_t + kg_d if not k.get('as_committed') and not k.get('local') and not k.get('info'))
    gate_as_committed = all(k['passed'] for k in kg_t + kg_d if not k.get('local') and not k.get('info'))
    last_day = con.execute("select max(created_day) from c").fetchone()[0]
    last_month = max(cm) if cm else None
    latest = max(rel)
    rows, revisions, comps, stated_detail = [], [], {}, {}
    rev_checked = [0]
    plan_hash = hashlib.sha256(open(os.path.join(H, 'PLAN.md'), 'rb').read()).hexdigest()
    for q in QUARTERS:
        qi = qinfo(q)
        own = q if q in rel else next((r for r in sorted(rel) if r > q and stated_cells(rel[r], qi['period']).get(('GLOBAL', 'T')) is not None), None)
        if own is None:
            continue   # TikTok has not published this quarter yet
        R = rel[own]; cells = stated_cells(R, qi['period'])
        if not market_values(cells):
            continue
        S, sdet = stated_eu(cells, q, R['file']); stated_detail[q] = sdet
        Lc = stated_cells(rel[latest], qi['period']) if latest != own else None
        S_latest = stated_eu(Lc, q, rel[latest]['file'])[0] if Lc else None
        if last_day < add_months(qi['b'], 3):     # Addendum 2.4: three full months after the quarter
            continue
        Dd, Dsub, bysub, allow, grid = delivered_eu(con, qi); comps[q] = dict(components=components(con, qi), grid=grid, nov_allowance=allow)
        partial_db = qi['a'] < DB_OPEN
        bad_days = [d for d in failed_days if str(qi['a']) <= d <= str(add_months(qi['b'], 3))]
        PH, PHnote = (posthoc_delivered(con, qi, ph, agg_days) if ph else (None, None))
        if PH:
            for ms in ('videos_removed', 'automated_removals'):
                PH[ms]['hi'] += allow.get('n' if ms == 'videos_removed' else 'fully', 0)
        for ms in MEASURES:
            sh = ms in SHARE
            oc, glo, ghi, mat = outcome(S[ms], Dd[ms], sh)
            oc_sub = outcome(S[ms], Dsub[ms], sh)[0]
            reason = []
            if bad_days:
                oc = K.CANNOT_TELL; mat = None; oc_sub = K.CANNOT_TELL
                reason.append('The database files fail our day check on %s, inside the window this quarter is read from.' % ', '.join(bad_days[:5]))
            if partial_db:
                oc_before = oc; oc = K.CANNOT_TELL; mat = None; oc_sub = K.CANNOT_TELL
                reason.append('The database opened in late September 2023, so it holds the last days of this quarter only.')
            if ms == 'within_24h_rate' and (Dd[ms].get('bad_share') or 0) > 0.01:
                oc = K.CANNOT_TELL; mat = None; oc_sub = K.CANNOT_TELL
                reason.append('More than 1% of matched statements have no posting date or a posting date after the decision.')
            row = dict(quarter=q, period=qi['period'], market='EU', market_code='EU', measure=ms,
                       stated=S[ms]['point'], stated_interval=[S[ms]['lo'], S[ms]['hi']],
                       stated_source=dict(file=R['file'], zip=R['zip'], release=own, url=rel_url(own),
                                          what='sum over the %d EU markets the release lists' % len(sdet['listed_eu'])),
                       delivered=Dd[ms].get('point'), delivered_interval=[Dd[ms]['lo'], Dd[ms]['hi']],
                       delivered_query=dict(source='DSA Transparency Database, complete monthly aggregates', platform='TikTok',
                                            point=SETS['point'] + ' and application_day in quarter',
                                            range='lower, point and upper content sets (PLAN.md) crossed with the decision day as is and shifted one day either way; submission day printed apart (Addendum 2.3)',
                                            months_read='2023-09 to %s' % last_month),
                       ratio=(Dd[ms]['point'] / S[ms]['point']) if (not sh and Dd[ms].get('point') is not None and S[ms]['point']) else None,
                       difference_pp=(100 * (Dd[ms]['point'] - S[ms]['point'])) if (sh and Dd[ms].get('point') is not None and S[ms]['point'] is not None) else None,
                       gap_interval=[glo, ghi], interval_kind='range across the matching choices fixed in PLAN.md, not a statistical interval',
                       material=mat, outcome=oc, reason=' '.join(reason),
                       delivered_by_submission_date=bysub[ms], delivered_interval_with_submission_date=[Dsub[ms]['lo'], Dsub[ms]['hi']],
                       outcome_range_with_submission_date=oc_sub,
                       outcome_plan_as_committed=(oc_sub if gate_as_committed else K.CANNOT_TELL))
            if partial_db:
                row['outcome_rule_without_coverage_limit'] = oc_before
            if sh:
                row['complement'] = dict(stated=(1 - S[ms]['point']) if S[ms]['point'] is not None else None,
                                         delivered=(1 - Dd[ms]['point']) if Dd[ms].get('point') is not None else None)
                if ms == 'within_24h_rate':
                    row['complement'] = dict(stated=1 - S[ms]['point'] if S[ms]['point'] is not None else None, delivered_range=[1 - Dd[ms]['hi'], 1 - Dd[ms]['lo']])
            if S_latest and any(abs((S_latest[ms][k] or 0) - (S[ms][k] or 0)) > 1e-9 for k in ('point', 'lo', 'hi')):
                oc2 = outcome(S_latest[ms], Dd[ms], sh)[0]
                row['latest_release'] = dict(release=latest, stated=S_latest[ms]['point'], stated_interval=[S_latest[ms]['lo'], S_latest[ms]['hi']], outcome=oc2)
                if oc2 != oc and not partial_db:
                    row['reason'] = (row['reason'] + ' Under the figure in the latest release the outcome reads %s.' % oc2.replace('_', ' ').lower()).strip()
            row['reason'] = (row['reason'] + ' ' + eu_reason(row, sdet, Dd[ms], ms)).strip()
            if PH:
                poc, plo, phi, pmat = outcome(S[ms], PH[ms], sh)
                if partial_db:
                    poc, pmat = K.CANNOT_TELL, None
                row['defined_after_the_data'] = dict(what='the committed day check replaced by TikTok\'s own published daily totals (DSA database download page, platform filter)',
                                                     delivered_interval=[PH[ms]['lo'], PH[ms]['hi']], gap_interval=[plo, phi], outcome=poc, material=pmat, days=PHnote)
            rows.append(row)
        # market rows
        mk = market_values(cells)
        for name in EU_NAMES:
            code = EU[name]
            if name not in mk or 'T' not in mk[name]:
                rows.append(dict(quarter=q, period=qi['period'], market=name, market_code=code, measure='videos_removed', stated=None,
                                 stated_interval=None, stated_source=dict(file=R['file'], release=own, url=rel_url(own)), delivered=None,
                                 delivered_interval=None, delivered_query=None, ratio=None, gap_interval=None, material=None,
                                 interval_kind=None, outcome=K.NOTHING_RETURNED, outcome_plan_as_committed=(K.NOTHING_RETURNED if gate_as_committed else K.CANNOT_TELL),
                                 reason=('TikTok does not break out %s in this release. Markets with fewer than 50,000 removals in the quarter are not listed.' % name)
                                 if int(q[:4]) >= 2026 else ('TikTok does not break out %s in this release, which lists the 50 markets with the most removals (the smallest listed had %s).' % (name, fnum(sdet['B'])))))
                continue
            v = mk[name]
            dm, single, unpl = delivered_market(con, qi, code)
            st = {'videos_removed': v.get('T'), 'automated_removals': (v.get('AUTO', 0) + v.get('AI', 0)) if 'AUTO' in v else None,
                  'automated_share': ((v.get('AUTO', 0) + v.get('AI', 0)) / v['T']) if 'AUTO' in v else None,
                  'proactive_rate': v.get('PRO'), 'within_24h_rate': v.get('W24')}
            for ms in MEASURES:
                base = dict(quarter=q, period=qi['period'], market=name, market_code=code, measure=ms, stated=st[ms],
                            stated_interval=([st[ms] - ROUND, st[ms] + ROUND] if (ms in ('proactive_rate', 'within_24h_rate') and st[ms] is not None) else [st[ms], st[ms]]),
                            stated_source=dict(file=R['file'], zip=R['zip'], release=own, url=rel_url(own)),
                            delivered_query=dict(source='DSA Transparency Database, complete monthly aggregates', platform='TikTok',
                                                 point=SETS['point'] + " and application_day in quarter and territorial_scope = '%s'" % code),
                            interval_kind='range across the matching choices fixed in PLAN.md, not a statistical interval')
                if dm is None:
                    base.update(delivered=None, delivered_interval=None, ratio=None, gap_interval=None, material=None, outcome=K.NOTHING_RETURNED,
                                reason=('The database holds no TikTok video removal filed for %s alone in this quarter. TikTok filed %s video removals in the quarter, '
                                        'none for this market alone. Their territorial scope says where the removal applies (every EEA country, or every one but Iceland), not which market the content came from.') % (name, fnum(unpl['n'])))
                elif ms == 'videos_removed':
                    oc, glo, ghi, mat = outcome(dict(point=st[ms], lo=st[ms], hi=st[ms]), dm, False)
                    base.update(delivered=dm['point'], delivered_interval=[dm['lo'], dm['hi']], ratio=dm['point'] / st[ms] if st[ms] else None,
                                gap_interval=[glo, ghi], material=mat, outcome=oc,
                                reason='Only removals filed for %s alone can be placed in the market (%s). Removals filed for every EEA country, every one but Iceland, or a list of countries could belong to it, so they set the upper end.' % (name, fnum(dm['point'])))
                else:
                    base.update(delivered=None, delivered_interval=None, ratio=None, gap_interval=None, material=None, outcome=K.CANNOT_TELL,
                                reason='Only %s removals were filed for %s alone. A share among them is not the market\'s share.' % (fnum(single['n']), name))
                base['outcome_plan_as_committed'] = base['outcome'] if gate_as_committed else K.CANNOT_TELL
                rows.append(base)
        # revisions: own release against latest release
        if Lc:
            for name in EU_NAMES + sorted(EFTA):
                for key in ('T', 'AUTO', 'AI', 'PRO', 'W24'):
                    a1, a2 = cells.get((name, key)), Lc.get((name, key))
                    if a1 is not None and a2 is not None and abs(a1 - a2) > 1e-9:
                        revisions.append(dict(quarter=q, market=name, cell=key, own_release=own, own=a1, latest_release=latest, latest=a2))
                    if a1 is not None and a2 is not None:
                        rev_checked[0] += 1
            for key in ('T', 'AUTO', 'AI'):
                a1, a2 = cells.get(('GLOBAL', key)), Lc.get(('GLOBAL', key))
                if a1 is not None and a2 is not None and abs(a1 - a2) > 1e-9:
                    revisions.append(dict(quarter=q, market='Global', cell=key, own_release=own, own=a1, latest_release=latest, latest=a2))
                if a1 is not None and a2 is not None:
                    rev_checked[0] += 1
    rows = K.apply_gate(gate, rows)
    # The simple aggregate repeats whole days (Addendum 2.1). Reconcile the scout's proof-run filter (video and removed, by submission date) on both files.
    simple_check = {}
    for q in sorted(set(r['quarter'] for r in rows if r['market'] == 'EU'))[-2:]:
        qi = qinfo(q); w = "created_day between DATE '%s' and DATE '%s' and ct_video and dv_removed" % (qi['a'], qi['b'])
        sv = con.execute('select coalesce(sum(n),0) from s where ' + w).fetchone()[0]; cv = con.execute('select coalesce(sum(n),0) from c where ' + w).fetchone()[0]
        simple_check[q] = dict(filter='video and removed, by submission date (the scout proof-run filter)', simple_aggregate=int(sv), complete_aggregate=int(cv), difference=int(sv - cv))
    meta = dict(updated=time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime()), plan_sha256=plan_hash, known_good=kg_t + kg_d, gate_passed=gate,
                gate_passed_as_committed=gate_as_committed, failed_days=failed_days, last_day_read=str(last_day),
                database_months_read=[os.path.basename(f)[9:16] for f in cfiles], latest_release=latest,
                sources=load_sources(), materiality=dict(count='5% of the stated point', share='1 percentage point'), revision_cells_checked=rev_checked[0],
                posthoc=posthoc_summary(ph), simple_file_check=simple_check, day_check_quarters=sorted(set(r['quarter'] for r in rows if r['market'] == 'EU' and 'day check' in (r.get('reason') or ''))))
    json.dump(dict(meta=meta, rows=rows, revisions=revisions, stated_detail=stated_detail), open(os.path.join(H, 'data', 'tiktok.json'), 'w'), indent=1, default=str)
    json.dump(comps, open(os.path.join(H, 'data', 'components.json'), 'w'), indent=1, default=str)
    summ = summarize(rows, revisions, meta, stated_detail, comps)
    json.dump(summ, open(os.path.join(H, 'summary_tiktok.json'), 'w'), indent=1, default=str)
    open(os.path.join(H, 'section_tiktok.html'), 'w').write(render(rows, summ, meta, stated_detail))
    print('tiktok: %d rows, gate %s, outcomes %s' % (len(rows), 'passed' if gate else 'FAILED', summ['outcomes']))


def add_months(d, k):
    y, m = d.year + (d.month - 1 + k) // 12, (d.month - 1 + k) % 12 + 1
    import calendar
    return D.date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def posthoc_summary(ph):
    if not ph:
        return None
    diffs = ph.get('differing_days', [])
    pos = max((r for r in diffs if r['diff'] > 0 and r['published']), key=lambda r: r['diff'], default=None)
    neg = max((r for r in diffs if r['diff'] < 0 and r['aggregate']), key=lambda r: -r['diff'], default=None)
    return dict(days=ph.get('days'), exact=ph.get('exact'), first=ph.get('first'), last=ph.get('last'),
                biggest_excess=(pos['day'], pos['diff']) if pos else None, biggest_shortfall=(neg['day'], -neg['diff']) if neg else None)


def day_words(days):
    """['2026-02-11','2026-09-30','2026-10-01','2026-10-02'] -> '11 February 2026 and 30 September to 2 October 2026'."""
    ds = sorted(D.date.fromisoformat(d) for d in days)
    runs = []
    for d in ds:
        if runs and (d - runs[-1][1]).days == 1:
            runs[-1][1] = d
        else:
            runs.append([d, d])
    fmt = lambda d: '%d %s %d' % (d.day, d.strftime('%B'), d.year)
    parts = [fmt(a) if a == b else ('%d %s to %s' % (a.day, a.strftime('%B'), fmt(b)) if a.year == b.year else '%s to %s' % (fmt(a), fmt(b))) for a, b in runs]
    return ' and '.join([', '.join(parts[:-1]), parts[-1]]) if len(parts) > 1 else (parts[0] if parts else '')


def rel_url(q):
    s = load_sources().get('tiktok', {}).get(q, {})
    return s.get('url')


def load_sources():
    try:
        return json.load(open(os.path.join(H, 'data', 'sources.json')))
    except Exception:
        return {}


def eu_reason(row, sdet, Dm, ms):
    """One plain sentence on what sets the range, so the outcome can be read without the plan."""
    nl = len(sdet['listed_eu']); nu = len(sdet['unlisted_eu'])
    s = 'TikTok lists %d of the 27 EU markets in this release' % nl
    if nu:
        s += ', and the %d it does not list could hold up to %s more removals by TikTok\'s own listing rule' % (nu, fnum(sdet['unlisted_cap_eu']))
    s += '.'
    if row['outcome'] == K.CANNOT_TELL and row['gap_interval'][0] is not None and not row['reason']:
        s += ' The gap range reaches zero and passes the material size, so the two filings neither agree nor disagree on this rule.'
    return s


def summarize(rows, revisions, meta, sdet, comps=None):
    from collections import Counter
    eu = [r for r in rows if r['market'] == 'EU']
    lq = max(r['quarter'] for r in eu) if eu else None
    ph = Counter(r['defined_after_the_data']['outcome'] for r in eu if r.get('defined_after_the_data'))
    scope = (comps or {}).get(lq, {}).get('components', {}).get('territorial_scope') if lq else None
    return dict(updated=meta['updated'], gate_passed=meta['gate_passed'], gate_passed_as_committed=meta['gate_passed_as_committed'],
                failed_days=meta['failed_days'], rows=len(rows), outcomes=dict(Counter(r['outcome'] for r in rows)),
                outcomes_plan_as_committed=dict(Counter(r.get('outcome_plan_as_committed') for r in rows)),
                eu_rows_outcomes=dict(Counter(r['outcome'] for r in eu)), eu_rows_outcomes_defined_after_the_data=dict(ph),
                market_rows_outcomes=dict(Counter(r['outcome'] for r in rows if r['market'] != 'EU')),
                quarters=sorted(set(r['quarter'] for r in rows)), latest_quarter=lq,
                eu_markets_listed={q: len(v['listed_eu']) for q, v in sdet.items()},
                eu_markets_not_listed_latest=(sdet[lq]['unlisted_eu'] if lq in sdet else None),
                revisions=len(revisions), revision_cells_checked=meta.get('revision_cells_checked'), latest_release=meta['latest_release'],
                latest_scope=scope, posthoc=meta.get('posthoc'), simple_file_check=meta.get('simple_file_check'),
                eu_rows=[dict(quarter=r['quarter'], measure=r['measure'], stated=r['stated'], stated_interval=r['stated_interval'],
                              delivered=r['delivered'], delivered_interval=r['delivered_interval'], delivered_by_submission_date=r.get('delivered_by_submission_date'),
                              ratio=r['ratio'], difference_pp=r.get('difference_pp'), gap=r['gap_interval'], outcome=r['outcome'], material=r['material'],
                              outcome_plan_as_committed=r.get('outcome_plan_as_committed'),
                              defined_after_the_data=(dict(outcome=r['defined_after_the_data']['outcome'], material=r['defined_after_the_data']['material'],
                                                           gap=r['defined_after_the_data']['gap_interval']) if r.get('defined_after_the_data') else None),
                              reason=r['reason']) for r in eu])


# ------------------------------------------------------------------ the public fragment
def e(s):
    return HT.escape(str(s), quote=True)


OUT_WORD = {'ABOVE': 'Above', 'BELOW': 'Below', 'CONSISTENT': 'Consistent', 'CANNOT_TELL': 'Cannot tell', 'NOTHING_RETURNED': 'Nothing returned'}


def cellv(ms, v):
    if v is None:
        return ''
    return fpct(v) if ms in SHARE else fnum(v)


def rng(ms, iv):
    if not iv or iv[0] is None:
        return ''
    if ms in SHARE:
        return '%s to %s' % (fpct(iv[0]), fpct(iv[1]))
    return '%s to %s' % (fnum(iv[0]), fnum(iv[1]))


def gapcell(ms, g, S):
    if not g or g[0] is None:
        return ''
    if ms in SHARE:
        return '%+.1f to %+.1f points' % (100 * g[0], 100 * g[1])
    return '%+.1f%% to %+.1f%%' % (100 * g[0] / S, 100 * g[1] / S) if S else ''


def fshare(v):
    if v is None:
        return ''
    return ('%.2f%%' % (100 * v)) if v >= 0.995 else ('%.1f%%' % (100 * v))


def cellv2(ms, v):
    if v is None:
        return ''
    return fshare(v) if ms in SHARE else fnum(v)


def rng2(ms, iv):
    if not iv or iv[0] is None:
        return ''
    return ('%s to %s' % (fshare(iv[0]), fshare(iv[1]))) if ms in SHARE else ('%s to %s' % (fnum(iv[0]), fnum(iv[1])))


def ph_word(r):
    p = r.get('defined_after_the_data')
    return OUT_WORD[p['outcome']] if p else ''


def render(rows, summ, meta, sdet):
    eu = [r for r in rows if r['market'] == 'EU']
    qs = sorted(set(r['quarter'] for r in eu))
    lq = qs[-1] if qs else None
    lqi = qinfo(lq) if lq else None
    src = meta['sources'].get('tiktok', {})
    get = lambda q, ms: next((x for x in eu if x['quarter'] == q and x['measure'] == ms), None)
    out = ['<section id="social-tiktok">', '<h2>TikTok: the quarterly report against its EU filings</h2>']
    out.append('<p>Every quarter TikTok publishes how many videos it removed in each market and how many of those removals were automated. '
               'TikTok also files its EU moderation decisions, one statement of reasons each, to the EU\'s DSA Transparency Database. '
               'We read the two filings against each other for every quarter since the database opened in September 2023, and we print where they agree as well as where they do not.</p>')
    if lq:
        out.append('<h3>EU total, %s</h3>' % e(lqi['label']))
        out.append('<p>TikTok\'s figure is the sum over the EU markets its report lists. Luxembourg and Malta are not broken out. The database figure counts TikTok statements for video content with a removal decision, dated by the day the decision was applied.</p>')
        out.append('<div class="scroll"><table class="mtx"><thead><tr><th>Measure</th><th>TikTok report</th><th>Database</th><th>Report range</th><th>Database range</th><th>Gap range</th><th>Outcome</th><th>Reading defined after the data</th></tr></thead><tbody>')
        for ms in MEASURES:
            r = get(lq, ms)
            if not r:
                continue
            dv = cellv2(ms, r['delivered']) if r['delivered'] is not None else 'see range'
            out.append('<tr><td>%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td>%s</td><td>%s</td></tr>' % (
                e(MNAME[ms]), cellv2(ms, r['stated']), dv, rng2(ms, r['stated_interval']), rng2(ms, r['delivered_interval']),
                gapcell(ms, r['gap_interval'], r['stated']), OUT_WORD[r['outcome']], ph_word(r)))
        out.append('</tbody></table></div>')
    # every quarter, one table per measure that carries a reading
    def quarter_table(ms, title, intro, extra_sub=False, listed=False):
        out.append('<h3>%s</h3>' % e(title))
        if intro:
            out.append('<p>%s</p>' % intro)
        hdr = '<tr><th>Quarter</th>' + ('<th>EU markets listed</th>' if listed else '') + '<th>TikTok report</th><th>Database, by decision date</th>' + \
              ('<th>Database, by submission date</th>' if extra_sub else '') + '<th>Gap range</th><th>Outcome</th><th>Reading defined after the data</th></tr>'
        out.append('<div class="scroll"><table class="mtx"><thead>%s</thead><tbody>' % hdr)
        for q in qs:
            r = get(q, ms)
            if not r:
                continue
            cells = ['<td>%s</td>' % e(qinfo(q)['label'])]
            if listed:
                cells.append('<td class="n">%d</td>' % len(sdet[q]['listed_eu']))
            cells += ['<td class="n">%s</td>' % cellv2(ms, r['stated']), '<td class="n">%s</td>' % cellv2(ms, r['delivered'])]
            if extra_sub:
                cells.append('<td class="n">%s</td>' % cellv2(ms, r.get('delivered_by_submission_date')))
            cells += ['<td class="n">%s</td>' % gapcell(ms, r['gap_interval'], r['stated']), '<td>%s</td>' % OUT_WORD[r['outcome']], '<td>%s</td>' % ph_word(r)]
            out.append('<tr>%s</tr>' % ''.join(cells))
        out.append('</tbody></table></div>')
    quarter_table('videos_removed', 'Videos removed, EU total, every quarter',
                  'Before 2026 TikTok listed only the 50 markets with the most removals, between 4 and 8 of them in the EU, so the report range is wide for those quarters. '
                  'The database opened on 25 September 2023, so Jul to Sep 2023 cannot be read.', extra_sub=True, listed=True)
    quarter_table('automated_share', 'Automated share of video removals, EU total, every quarter',
                  'TikTok\'s report counts removals by automation and, from 2026, by AI moderation as automated. The database figure is the share of statements marked fully automated.')
    quarter_table('proactive_rate', 'Removed before any report, EU total, every quarter',
                  'TikTok\'s report gives the share of videos removed before anyone reported them. The database figure is the share of statements TikTok filed as its own voluntary initiative.')
    if lq:
        mrows = [r for r in rows if r['quarter'] == lq and r['market'] != 'EU']
        names = sorted(set(r['market'] for r in mrows))
        tot = get(lq, 'videos_removed')
        out.append('<h3>By market, %s</h3>' % e(lqi['label']))
        sc = dict((k, v) for k, v in (summ.get('latest_scope') or []))
        wide = sum(v for k, v in sc.items() if k in ('EEA', 'EEA_no_IS', 'EU'))
        if tot and sc and wide == tot['delivered']:
            out.append('<p>TikTok places each removal in the market where the content was published. The database records where a restriction applies. '
                       'TikTok filed all %s of its video removal statements for this quarter with a territorial scope covering every EEA country, or every one but Iceland, '
                       'so the database cannot place any of them in one member state.</p>' % fnum(tot['delivered']))
        elif tot:
            out.append('<p>TikTok places each removal in the market where the content was published. The database records where a restriction applies. '
                       'Of TikTok\'s %s video removal statements for this quarter, %s carry a territorial scope covering every EEA country or every one but Iceland, which does not place them in one member state.</p>' % (fnum(tot['delivered']), fnum(wide)))
        out.append('<div class="scroll"><table class="mtx"><thead><tr><th>Market</th><th>Videos removed, report</th><th>Automated share, report</th><th>Removed before any report, report</th><th>Database, filed for this market alone</th><th>Outcome</th></tr></thead><tbody>')
        for nm in names:
            rr = {r['measure']: r for r in mrows if r['market'] == nm}
            v = rr.get('videos_removed')
            if v and v['stated'] is None:
                out.append('<tr><td>%s</td><td colspan="3">Not broken out by TikTok in this quarter</td><td class="n"></td><td>%s</td></tr>' % (e(nm), OUT_WORD[v['outcome']]))
                continue
            dvv = fnum(v['delivered']) if v and v['delivered'] is not None else '0'
            out.append('<tr><td>%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td>%s</td></tr>' % (
                e(nm), fnum(v['stated']), fshare(rr['automated_share']['stated']), fshare(rr['proactive_rate']['stated']), dvv, OUT_WORD[v['outcome']]))
        out.append('</tbody></table></div>')
    out.append('<h3>How we read it</h3>')
    out.append('<p>The report side is TikTok\'s own figure, summed over the EU markets it lists. Its range runs from that sum to the sum plus what the unlisted EU markets, Norway, Iceland and Liechtenstein could hold under TikTok\'s own listing rule. '
               'We do not know whether TikTok files statements for users in Norway, Iceland or Liechtenstein, so the range allows both. Rates in the report are printed to three decimals, and the range carries that rounding.</p>')
    out.append('<p>The database side counts TikTok statements with video content and a removal decision, not ads, dated by the day the decision was applied. Its range runs across that day shifted one day either way, '
               'and across a narrow and a wide reading of video. The narrow reading keeps removals for breaking TikTok\'s rules only. The wide reading adds images, synthetic media and other content, because TikTok counts photo posts and stories as videos.</p>')
    out.append('<p>No range on this page is a statistical interval. Both sides are full counts, and each range shows how far a figure moves across the matching choices we fixed before reading the data. '
               'The gap range is the database range minus the report range, as a share of the report figure for counts and in percentage points for shares. Above means the database figure is higher than the report allows under every choice. Below means it is lower under every choice. '
               'Consistent means the gap range includes zero and stays within 5% for counts or 1 percentage point for shares. Cannot tell means the gap range includes zero and reaches past that size, or a check on the files failed. '
               'Nothing returned means one side holds no figure for the row. We measure gaps and name no cause.</p>')
    out.append('<p>Removed within 24 hours is compared with the days between the posting date and the decision date. The database keeps both as whole days, so its side is a range.</p>')
    out.append('<p>Our plan first let the submission date set one end of the database range. Before we set any figure against another, the files showed that TikTok filed no statement on some days and, from July 2025 to January 2026, '
               'filed up to 94% of a month\'s removal statements one to three months after the decision. TikTok\'s report counts cases closed in the quarter, so we date by the decision and print the count by submission date beside it. '
               'The data file keeps the outcome under the first rule for every row.</p>')
    ph = meta.get('posthoc'); dq = meta.get('day_check_quarters') or []
    if meta.get('failed_days') and dq:
        lab = [qinfo(q)['label'] for q in dq]
        out.append('<p>Our committed check on the database files failed on %s, so %s read Cannot tell. ' % (day_words(meta['failed_days']), ' and '.join([', '.join(lab[:-1]), lab[-1]]) if len(lab) > 1 else lab[0]) +
                   ('The column marked defined after the data replaces that check with TikTok\'s own daily totals, published on the database\'s download page. They match the files exactly on %s of %s days. ' % (fnum(ph['exact']), fnum(ph['days'])) if ph else '') +
                   ('Where the files hold more statements than TikTok\'s total, the excess can come off the low end of the database range (the largest is %s, by %s). ' % (day_words([ph['biggest_excess'][0]]), fnum(ph['biggest_excess'][1])) if ph and ph.get('biggest_excess') else '') +
                   ('Where they hold fewer, the shortfall is added to the high end (the largest is %s, by %s).' % (day_words([ph['biggest_shortfall'][0]]), fnum(ph['biggest_shortfall'][1])) if ph and ph.get('biggest_shortfall') else '') + '</p>')
    out.append('<p>TikTok\'s figures for each quarter are the same in that quarter\'s own release and in the latest release, for every EU market we read.</p>')
    out.append('<p class="meta">Sources: TikTok Community Guidelines Enforcement Report data, one zip per quarter, file YYYYQn_raw_data_cger_English.csv (<a href="https://www.tiktok.com/safety/en/transparency/cg-report">report page</a>')
    for q in sorted(src):
        if src[q].get('url'):
            out.append(', <a href="%s">%s</a>' % (e(src[q]['url']), e(q)))
    out.append('). EU DSA Transparency Database, complete monthly aggregates of statements of reasons, CC BY 4.0 '
               '(<a href="https://transparency.dsa.ec.europa.eu/explore-data/download">download page</a>, '
               '<a href="https://dsa.pages.code.europa.eu/transparency-database/dsa-tdb/data_sources.html">aggregate files</a>). '
               'Database months read: %s to %s. Updated %s.</p>' % (meta['database_months_read'][0], meta['database_months_read'][-1], e(meta['updated'])))
    out.append('</section>')
    return '\n'.join(x for x in out if x) + '\n'


if __name__ == '__main__':
    build(fetch='--no-fetch' not in sys.argv)
