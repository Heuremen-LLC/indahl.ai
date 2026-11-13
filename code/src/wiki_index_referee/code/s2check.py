#!/usr/bin/env python3
"""Referee: recompute Section 2 delivered values from data/raw/s2 with own code."""
import os, gzip, json, calendar, collections as C, math
R2 = '/Users/heuremen/bones-forge/wiki_index/data/raw/s2'
def jl(p):
    with gzip.open(p, 'rt') as f: return json.load(f)
sm = jl(os.path.join(R2, 'sitematrix.json.gz'))['sitematrix']
sites = []
for k, v in sm.items():
    if k == 'count': continue
    for s in (v if k == 'specials' else v.get('site', [])):
        sites.append(dict(db=s['dbname'], url=s['url'], code=s.get('code'), closed='closed' in s, private='private' in s, fishbowl='fishbowl' in s))
wps = [s for s in sites if s['code'] == 'wiki' and s['url'].endswith('.wikipedia.org') and not s['private']]
print('wikipedias (not private):', len(wps), 'open:', sum(not s['closed'] for s in wps), 'closed:', sum(s['closed'] for s in wps))
LAST12 = [f'{y}{m:02d}' for y, m in [(2025, 11), (2025, 12)] + [(2026, i) for i in range(1, 11)]]
FY = [f'{y}{m:02d}' for y, m in [(2024, i) for i in range(7, 13)] + [(2025, i) for i in range(1, 7)]]
def pv_series(agent):
    tot = C.Counter(); missing = C.Counter()
    for s in wps:
        dom = s['url'].replace('https://', '')
        p = os.path.join(R2, 'pv', f'{dom}_{agent}.json.gz')
        d = jl(p) if os.path.exists(p) else {}
        got = {it['timestamp'][:6]: it['views'] for it in d.get('items', [])}
        for m in LAST12 + FY:
            if m in got: tot[m] += got[m]
            else: missing[m] += 1
    return tot, missing
def stats(series, months):
    vals = [series.get(m) for m in months]
    if any(v is None for v in vals): return None
    return (min(vals), max(vals), sum(vals) / len(vals))
V1, miss1 = pv_series('user'); V2, miss2 = pv_series('all-agents')
ap = {ag: {it['timestamp'][:6]: it['views'] for it in jl(os.path.join(R2, f'pv_allprojects_{ag}.json.gz'))['items']} for ag in ('user', 'all-agents')}
for name, ser in (('V1 Wikipedia human', V1), ('V2 Wikipedia all agents', V2), ('V3 all projects human', ap['user']), ('V4 all projects all agents', ap['all-agents'])):
    a = stats(ser, LAST12); b = stats(ser, FY)
    print(f'{name}: last12 {a[0]/1e9:.2f}-{a[1]/1e9:.2f} mean {a[2]/1e9:.2f} bn | FY24-25 {b[0]/1e9:.2f}-{b[1]/1e9:.2f} mean {b[2]/1e9:.2f} bn')
print('editions with no pv rows per month (last12):', {m: miss1[m] for m in LAST12})
def edits(et, pt):
    d = jl(os.path.join(R2, f'edits_{et}_{pt}.json.gz'))
    return {r['timestamp'][:7].replace('-', ''): r['edits'] for r in d['items'][0]['results']}
def per_min(d): return {m: v / (calendar.monthrange(int(m[:4]), int(m[4:]))[1] * 1440) for m, v in d.items()}
E = {'E1 all types all pages': per_min(edits('all-editor-types', 'all-page-types')),
     'E2 user+anon all pages': per_min({m: edits('user', 'all-page-types')[m] + edits('anonymous', 'all-page-types').get(m, 0) for m in edits('user', 'all-page-types')}),
     'E3 all types content': per_min(edits('all-editor-types', 'content')),
     'E4 user+anon content': per_min({m: edits('user', 'content')[m] + edits('anonymous', 'content').get(m, 0) for m in edits('user', 'content')})}
for k, s in E.items():
    a = stats(s, LAST12); b = stats(s, FY)
    print(f'{k}: last12 {a[0]:.1f}-{a[1]:.1f} mean {a[2]:.1f} | FY {b[0]:.1f}-{b[1]:.1f} mean {b[2]:.1f}')
# bots: check all = user + anon + group-bot + name-bot
al = edits('all-editor-types', 'all-page-types'); u = edits('user', 'all-page-types'); an = edits('anonymous', 'all-page-types'); gb = edits('group-bot', 'all-page-types'); nb = edits('name-bot', 'all-page-types')
print('all minus (user+anon+group-bot+name-bot), sample months:', {m: al[m] - u[m] - an[m] - gb[m] - nb[m] for m in LAST12[:4]})
# articles and files
arts_open = arts_all = 0; n_open = n_all = 0; nost = []
for s in wps:
    p = os.path.join(R2, 'siteinfo', f"{s['db']}.json.gz")
    st = jl(p).get('query', {}).get('statistics') if os.path.exists(p) else None
    if not st: nost.append(s['db']); continue
    arts_all += st['articles']; n_all += 1
    if not s['closed']: arts_open += st['articles']; n_open += 1
print('articles open', arts_open, 'all', arts_all, 'editions open', n_open, 'all', n_all, 'no stats', nost)
cm = jl(os.path.join(R2, 'siteinfo', 'commonswiki.json.gz'))['query']['statistics']
print('commons images', cm['images'])
# volunteers bounds
opn = [s for s in sites if not s['closed'] and not s['private'] and not s['fishbowl']]
def bounds(months, wp_only):
    out = {}
    for lvl in ('1+', '5+'):
        lows, highs = [], []
        for m in months:
            mm = f'{m[:4]}-{m[4:]}'; vals = []
            for s in opn:
                dom = s['url'].replace('https://', '')
                if wp_only and not (s['code'] == 'wiki' and dom.endswith('.wikipedia.org')): continue
                pa = os.path.join(R2, 'editors', f'{dom}_all-activity-levels.json.gz'); pb = os.path.join(R2, 'editors', f'{dom}_1..4-edits.json.gz')
                if not os.path.exists(pa): continue
                da = jl(pa); a = {r['timestamp'][:7]: r['editors'] for r in (da.get('items') or [{}])[0].get('results', [])} if da.get('items') else {}
                db = jl(pb) if os.path.exists(pb) else {}; b = {r['timestamp'][:7]: r['editors'] for r in (db.get('items') or [{}])[0].get('results', [])} if db.get('items') else {}
                if mm not in a: continue
                vals.append(a[mm] if lvl == '1+' else a[mm] - b.get(mm, 0))
            lows.append(max(vals)); highs.append(sum(vals))
        out[lvl] = (round(sum(lows) / len(lows)), round(sum(highs) / len(highs)), min(highs), max(highs))
    return out
print('open sites', len(opn))
print('bounds last12 all wikis', bounds(LAST12, False)); print('bounds last12 wikipedias', bounds(LAST12, True))
print('bounds FY all wikis', bounds(FY, False)); print('bounds FY wikipedias', bounds(FY, True))
