#!/usr/bin/env python3
"""ledger_rows.py SLUG [--dry]: adds the shipped ledger rows of a forecaster desk (FLU, STEO, SEASONAL, 10 Nov 2026) with ledger/ledger.py add.
Each row's value comes from the desk summary, its snippet is cut from the desk page draft (<slug>_index/<slug>.html, the body build_site.py serves),
its source grep is a line of the desk CHECKS.md. Run while holding ledger/.site_edit.lock, after wire_desk.py added the desk_<slug> surface."""
import os, re, sys, json, html, subprocess
B = os.path.expanduser('~/bones-forge'); SLUG = sys.argv[1]; DRY = '--dry' in sys.argv; D = os.path.join(B, SLUG + '_index')
S = json.load(open(os.path.join(D, 'summary_%s.json' % SLUG)))
def norm(s):
    s = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', s, flags=re.S); s = re.sub(r'<[^>]+>', ' ', s); s = html.unescape(s)
    s = s.replace('−', '-').replace('–', '-').replace('—', '-').replace(' ', ' ').replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', s).strip()
T = open(os.path.join(D, SLUG + '.html')).read(); T = T[T.index('</section>', T.index('hl-slot')):]   # body below the headline slot (the slot is live)
PAGE = norm(T)
def snip(start, end_words=('below', 'above', 'consistent', 'cannot tell')):
    i = PAGE.index(start); k = i + len(start); j = min((PAGE.index(w, k) + len(w) for w in end_words if w in PAGE[k:k + 400]), default=k); return PAGE[i:j]
def pc(x): return '%.1f' % (100 * x)
def f(n): return '{:,}'.format(int(n))
rows = []
if SLUG == 'flu':
    cell = lambda nm, L, side='final': next(c for c in S['cells'] if c['cell'] == nm and c['level'] == L and c['side'] == side)
    for key, nm, L, label in (('all95', 'all horizons', '95', 'All horizons'), ('all50', 'all horizons', '50', 'All horizons'), ('h0_95', 'horizon 0', '95', 'Horizon 0'),
                              ('h1_95', 'horizon 1', '95', 'Horizon 1'), ('h2_95', 'horizon 2', '95', 'Horizon 2'), ('h3_95', 'horizon 3', '95', 'Horizon 3')):
        c = cell(nm, L)
        rows.append(dict(id='flu.cell.' + key, claim='FLU, %s: latest reported weekly flu admissions inside the CDC FluSight ensemble stated %s percent interval (block bootstrap 95%% interval over target weeks, plan rule)' % (nm, L),
                         value=str(c['share']), lo=str(c['lo']), hi=str(c['hi']), unit='%s of %s' % (f(c['inside']), f(c['scored'])), outcome=c['outcome'],
                         snippet=snip('%s %s %s %s %s to %s' % (label, f(c['scored']), f(c['inside']), pc(c['share']), pc(c['lo']), pc(c['hi'])))))
    c = cell('all horizons', '95', 'first')
    rows.append(dict(id='flu.first.all95', claim='FLU, all horizons: first reported count inside the stated 95 percent interval', value=str(c['share']), lo=str(c['lo']), hi=str(c['hi']), unit='%s of %s' % (f(c['inside']), f(c['scored'])), outcome=c['outcome'],
                     snippet=snip('All horizons %s %s %s %s to %s' % (f(c['scored']), f(c['inside']), pc(c['share']), pc(c['lo']), pc(c['hi'])))))
    w = next(x for x in S['wis'] if x['cell'] == 'all horizons' and x['side'] == 'final')
    rows.append(dict(id='flu.wis.all', claim='FLU, all horizons: ensemble WIS over FluSight-baseline WIS on the same rows (our ruler against 1)', value=str(w['ratio']), lo=str(w['lo']), hi=str(w['hi']), unit='%s rows' % f(w['rows']), outcome=w['outcome'],
                     snippet=snip('All horizons latest %s' % f(w['rows']))))
    a = S['after_data']['wis_without_us']
    rows.append(dict(id='flu.wis.no_us', claim='FLU: WIS ratio without the United States row, after the data, decides nothing', value=str(a['ratio']), lo=str(a['lo']), hi=str(a['hi']), unit='%s rows' % f(a['rows']), outcome='LEVEL',
                     snippet='Without it the ratio is %.2f (%.2f to %.2f)' % (a['ratio'], a['lo'], a['hi'])))
    nb = sum(1 for b in S['by_location'] for x in b['cells'] if x['level'] == '95' and x['side'] == 'final' and x['outcome'] == 'BELOW')
    rows.append(dict(id='flu.places95.below', claim='FLU: places whose outer interval reads below, all horizons, latest count', value=str(nb), lo=None, hi=None, unit='of %d places' % len(S['by_location']), outcome='COUNT',
                     snippet='For the stated 95 percent interval, %d places read below' % nb))
    grep = 'all horizons outer latest: 16,416 inside, 1,858 above, 270 below of 18,544'
elif SLUG == 'steo':
    NM = {'WTI': 'WTI crude oil', 'HH': 'Henry Hub natural gas'}
    for tab, pre in (('cells', 'steo.cell.'), ('cells_addendum1', 'steo.add1.')):
        for c in S[tab]:
            if c['cell'] not in ('all leads', '1 to 2 months', '13 months or more'): continue
            k = {'all leads': 'all', '1 to 2 months': 'lead1_2', '13 months or more': 'lead13'}[c['cell']]
            rows.append(dict(id=pre + c['series'].lower() + '.' + k, claim='STEO, %s, %s%s: monthly average spot price inside the 95 percent interval EIA stated (block bootstrap over outcome months)' % (NM[c['series']], c['cell'], ', Addendum 1 reading, after the data' if 'add1' in pre else ', plan reading'),
                             value=str(c['share']), lo=str(c['lo']), hi=str(c['hi']), unit='%s of %s' % (f(c['inside']), f(c['scored'])), outcome=c['outcome'],
                             snippet=snip('%s %s %s %s %s %s to %s' % (NM[c['series']], c['cell'], f(c['scored']), f(c['inside']), pc(c['share']), pc(c['lo']), pc(c['hi'])))))
    grep = 'primary WTI all leads'
elif SLUG == 'seasonal':
    VN = {'temp': 'Temperature', 'prec': 'Precipitation'}
    for c in S['cells']:
        if c['cell'].endswith('leaning'):
            rows.append(dict(id='seasonal.lean.' + c['variable'], claim='SEASONAL, %s: share of grid cells where a category stated at 40 percent or more was observed, against the mean stated chance (block bootstrap over seasons)' % c['cell'].split(',')[0],
                             value=str(c['observed']), lo=str(c['lo']), hi=str(c['hi']), unit='%s of %s rows, stated %s' % (f(c['hits']), f(c['rows']), c['mean_stated']), outcome=c['outcome'],
                             snippet=snip('%s %s %s %s %s %s to %s' % (VN[c['variable']], f(c['rows']), f(c['seasons']), pc(c['mean_stated']), pc(c['observed']), pc(c['lo']), pc(c['hi'])))))
    for c in S['cells']:
        if c['variable'] == 'temp' and c.get('category') == 'above' and c.get('bin') in ('40 to under 50', '50 to under 60'):
            rows.append(dict(id='seasonal.temp.above.' + c['bin'].split()[0], claim='SEASONAL, temperature, above normal stated %s percent: observed frequency against mean stated chance' % c['bin'],
                             value=str(c['observed']), lo=str(c['lo']), hi=str(c['hi']), unit='%s rows, stated %s' % (f(c['rows']), c['mean_stated']), outcome=c['outcome'],
                             snippet=snip('above %s %s %s %s %s %s to %s' % (c['bin'], f(c['rows']), f(c['seasons']), pc(c['mean_stated']), pc(c['observed']), pc(c['lo']), pc(c['hi'])))))
    for h in S['heidke']:
        k = 'seasonal.hss.%s.%s' % (h['variable'], 'nonec' if h['score'].startswith('non') else 'all')
        rows.append(dict(id=k, claim='SEASONAL: our recompute of CPC Heidke %s minus CPC stated, %s, mean over seasons (block bootstrap)' % (h['score'], h['variable']), value=str(h['mean_difference']), lo=str(h['lo']), hi=str(h['hi']),
                         unit='points, %s of %s seasons within 1 point' % (f(h['within_1_point']), f(h['seasons'])), outcome=h['outcome'],
                         snippet=snip('%s %s %s %+.3f' % (VN[h['variable']], h['score'], f(h['seasons']), h['mean_difference']))))
    grep = 'temperature leaning ABOVE'
chk = '%s_index/CHECKS.md' % SLUG
for r in rows:
    assert r['snippet'] in PAGE, r
    cmd = [sys.executable, os.path.join(B, 'ledger', 'ledger.py'), 'add', r['id'], '--claim', r['claim'], '--value', r['value'], '--unit', r['unit'], '--outcome', r['outcome'],
           '--source', chk, '--grep', grep, '--on', 'desk_' + SLUG, r['snippet'], '--checks', chk]
    if r['lo'] not in (None, 'None'): cmd += ['--lo', r['lo'], '--hi', r['hi']]
    L = [sys.executable, os.path.join(B, 'ledger', 'ledger.py')]
    if '--live' in sys.argv:   # flip held -> live, inside the site lock with the page edit and ship
        p = subprocess.run(L + ['set', r['id'], '--field', 'status', '--to', 'live', '--why', 'page block in build_site.py, released by ship.sh', '--evidence', chk], capture_output=True, text=True, cwd=B)
        print(r['id'], (p.stdout + p.stderr).strip()[-120:]); continue
    print(r['id'], r['outcome'], '|', r['snippet'][:110])
    if not DRY:
        p = subprocess.run(cmd, capture_output=True, text=True, cwd=B); print('  ', (p.stdout + p.stderr).strip()[-160:] or 'added')
        q = subprocess.run(L + ['set', r['id'], '--field', 'status', '--to', 'held', '--why', 'held until the page block is in build_site.py (site lock protocol, 10 Nov 2026)', '--evidence', chk], capture_output=True, text=True, cwd=B)
        print('  ', (q.stdout + q.stderr).strip()[-120:])
