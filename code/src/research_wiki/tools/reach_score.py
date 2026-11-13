"""Score the Foundation homepage numbers against the delivered series pulled by reach_proof.py."""
import json, os, calendar, collections
B = os.path.expanduser('~/bones-forge/research_wiki/samples/reach/')
wide = json.load(open(B + 'wide.json'))
wp = json.load(open(B + 'per_wikipedia.json'))
ed = json.load(open(B + 'per_wiki_editors.json'))
sites = json.load(open(B + 'sites.json'))
months = [f'2025{m:02d}' for m in (11, 12)] + [f'2026{m:02d}' for m in range(1, 11)]

print('open Wikipedias read', len(wp), 'of', sites['open_wikipedias'], '; wikis with editor rows', len(ed), 'of', sites['open'])

# 1. views each month, Wikipedia only (sum over open editions)
print('\n1. "Wikipedia receives nearly 15 billion views each month."')
missing = [k for k, v in wp.items() if not v['user']]
print('   editions with no pageview rows:', len(missing))
for ag in ('user', 'all-agents'):
    row = []
    for m in months:
        s = sum(v[ag].get(m + '0100', 0) for v in wp.values())
        row.append(s)
    print(f'   {ag:10s}', ' '.join(f'{x/1e9:.2f}' for x in row), f' | 12-month mean {sum(row)/len(row)/1e9:.2f} bn, min {min(row)/1e9:.2f}, max {max(row)/1e9:.2f}')
ap = {ag: {it['timestamp'][:6]: it['views'] for it in wide[f'pageviews|all-projects|{ag}']['items']} for ag in ('user', 'all-agents', 'automated', 'spider')}
print('   all projects, user      ', ' '.join(f"{ap['user'][m]/1e9:.2f}" for m in months))
print('   all projects, all agents', ' '.join(f"{ap['all-agents'][m]/1e9:.2f}" for m in months))

# 2. volunteers each month: registered editors, summed over wikis (counts a person once per wiki)
print('\n2. "nearly 265,000 volunteers every month" and "nearly 250,000 volunteers"')
for scope, keep in (('all open wikis', lambda k: True), ('Wikipedias only', lambda k: k in wp)):
    a1, a5 = [], []
    for m in months:
        mm = f'{m[:4]}-{m[4:]}'
        s1 = sum(v['all-activity-levels'].get(mm, 0) for k, v in ed.items() if keep(k))
        s14 = sum(v['1..4-edits'].get(mm, 0) for k, v in ed.items() if keep(k))
        a1.append(s1); a5.append(s1 - s14)
    print(f'   {scope:16s} 1+ edits: mean {sum(a1)/12:,.0f} (min {min(a1):,}, max {max(a1):,}); 5+ edits: mean {sum(a5)/12:,.0f} (min {min(a5):,}, max {max(a5):,})')
top = sorted(((v['all-activity-levels'].get('2026-10', 0), k) for k, v in ed.items()), reverse=True)[:6]
print('   largest single wikis, Oct 2026, 1+ edits:', top)

# 3. edits per minute
print('\n3. "Every minute 324 new edits are made to Wikipedia."')
for key in ('edits|all-editor-types|all-page-types', 'edits|user|all-page-types', 'edits|anonymous|all-page-types',
            'edits|group-bot|all-page-types', 'edits|name-bot|all-page-types', 'edits|all-editor-types|content', 'edits|user|content'):
    res = wide[key]['items'][0]['results']
    per = []
    for r in res:
        y, mo = int(r['timestamp'][:4]), int(r['timestamp'][5:7])
        per.append(r['edits'] / (calendar.monthrange(y, mo)[1] * 1440))
    print(f'   {key:40s} per minute: mean {sum(per)/len(per):6.1f}  min {min(per):6.1f}  max {max(per):6.1f}  (months {len(per)})')
h = {}
for et in ('user', 'anonymous'):
    res = wide[f'edits|{et}|all-page-types']['items'][0]['results']
    h[et] = [r['edits'] / (calendar.monthrange(int(r['timestamp'][:4]), int(r['timestamp'][5:7]))[1] * 1440) for r in res]
hum = [a + b for a, b in zip(h['user'], h['anonymous'])]
print(f'   registered users plus anonymous (no bots)  per minute: mean {sum(hum)/len(hum):6.1f}  min {min(hum):6.1f}  max {max(hum):6.1f}')

# 4. articles
print('\n4. "With over 67 million articles, in 300+ languages"')
arts = sum((v['stats'] or {}).get('articles', 0) for v in wp.values())
nostat = [k for k, v in wp.items() if not v['stats']]
print(f'   sum of article counts over {len(wp)} open Wikipedias: {arts:,}  (editions with no stats: {len(nostat)})')
print(f'   open Wikipedias: {sites["open_wikipedias"]}')

# 5. Commons files
c = json.load(open(B + 'commons_stats.json'))['query']['statistics']
print('\n5. Commons: "114 million images, photographs, videos and music files and counting"')
print(f'   Commons file count (siteinfo images): {c["images"]:,}; content pages {c["articles"]:,}')
