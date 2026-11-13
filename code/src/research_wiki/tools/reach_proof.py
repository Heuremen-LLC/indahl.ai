"""Proof run for the Wikimedia reach desk: stated homepage numbers against the
Wikimedia Analytics API (CC0) and each wiki's own statistics.

Writes JSON to research_wiki/samples/reach/. Paced at about 3 requests a second,
one request at a time, under the published 200 requests a minute limit for
unauthenticated clients with a compliant User-Agent.
"""
import json, os, sys, time, urllib.request, urllib.parse

UA = "HeuremenLLC-research/1.0 (https://indahl.ai)"
OUT = os.path.expanduser('~/bones-forge/research_wiki/samples/reach')
os.makedirs(OUT, exist_ok=True)
AQS = 'https://wikimedia.org/api/rest_v1/metrics'
PACE = 0.15
LOG = open(os.path.join(OUT, 'run.log'), 'a')


def get(url, tries=4):
    for i in range(tries):
        time.sleep(PACE)
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {'_status': 404}
            if e.code in (429, 503):
                wait = int(e.headers.get('Retry-After', '10') or 10)
                LOG.write(f'{e.code} wait {wait} {url}\n'); LOG.flush()
                time.sleep(max(wait, 5))
                continue
            LOG.write(f'HTTP {e.code} {url}\n'); LOG.flush()
            return {'_status': e.code}
        except Exception as e:  # network hiccup
            LOG.write(f'ERR {e} {url}\n'); LOG.flush()
            time.sleep(5)
    return {'_status': 'fail'}


def save(name, obj):
    with open(os.path.join(OUT, name), 'w') as f:
        json.dump(obj, f, indent=1)


# 1. site list
sm = get('https://meta.wikimedia.org/w/api.php?action=sitematrix&format=json&smsiteprop=url|dbname|code&smlangprop=code|site')
sites = []
for k, v in sm['sitematrix'].items():
    if k == 'count':
        continue
    if k == 'specials':
        for s in v:
            sites.append({'dbname': s['dbname'], 'url': s['url'], 'code': s.get('code'),
                          'closed': 'closed' in s, 'private': 'private' in s, 'fishbowl': 'fishbowl' in s})
    else:
        for s in v.get('site', []):
            sites.append({'dbname': s['dbname'], 'url': s['url'], 'code': s.get('code'),
                          'closed': 'closed' in s, 'private': False, 'fishbowl': False})
open_sites = [s for s in sites if not s['closed'] and not s['private'] and not s['fishbowl']]
wps = [s for s in open_sites if s['code'] == 'wiki' and s['url'].endswith('.wikipedia.org')]
save('sites.json', {'all': len(sites), 'open': len(open_sites), 'open_wikipedias': len(wps), 'sites': open_sites})
print('sites', len(sites), 'open', len(open_sites), 'open wikipedias', len(wps), flush=True)

START_M, END_M = '2025110100', '2026110100'   # Nov 2025 to Oct 2026
START_D, END_D = '20251101', '20261101'

# 2. Wikipedia-wide series that AQS serves directly
wide = {}
for et in ['all-editor-types', 'user', 'anonymous', 'group-bot', 'name-bot']:
    for pt in ['all-page-types', 'content']:
        wide[f'edits|{et}|{pt}'] = get(f'{AQS}/edits/aggregate/all-wikipedia-projects/{et}/{pt}/monthly/{START_D}/{END_D}')
wide['uniques|all-wikipedia-projects'] = get(f'{AQS}/unique-devices/all-wikipedia-projects/all-sites/monthly/20250801/20261031')
for fam in ['all-wikidata-projects', 'all-wikibooks-projects', 'all-wikivoyage-projects', 'all-wikisource-projects',
            'all-wiktionary-projects', 'all-wikiquote-projects', 'all-wikiversity-projects', 'all-wikinews-projects',
            'www.wikidata.org', 'commons.wikimedia.org', 'species.wikimedia.org']:
    wide[f'uniques|{fam}'] = get(f'{AQS}/unique-devices/{fam}/all-sites/monthly/20250801/20261031')
for ag in ['user', 'all-agents', 'automated', 'spider']:
    wide[f'pageviews|all-projects|{ag}'] = get(f'{AQS}/pageviews/aggregate/all-projects/all-access/{ag}/monthly/{START_M}/{END_M}')
for m in ['2026/01', '2026/02', '2026/03', '2026/04', '2026/05', '2026/06']:
    wide[f'topbycountry|all-projects|{m}'] = get(f'{AQS}/pageviews/top-by-country/all-projects/all-access/{m}')
save('wide.json', wide)
print('wide done', flush=True)

# 3. per-Wikipedia pageviews (user, all-agents) and article counts
per_wp = {}
for i, s in enumerate(wps):
    dom = s['url'].replace('https://', '')
    row = {}
    for ag in ['user', 'all-agents']:
        d = get(f'{AQS}/pageviews/aggregate/{dom}/all-access/{ag}/monthly/{START_M}/{END_M}')
        row[ag] = {it['timestamp']: it['views'] for it in d.get('items', [])}
    st = get(f'{s["url"]}/w/api.php?action=query&meta=siteinfo&siprop=statistics&format=json')
    row['stats'] = st.get('query', {}).get('statistics')
    per_wp[s['dbname']] = row
    if i % 25 == 0:
        print('wp', i, dom, flush=True)
        save('per_wikipedia.json', per_wp)
save('per_wikipedia.json', per_wp)
print('per wikipedia done', flush=True)

# 4. per-wiki editors, every open wiki: all activity levels, and 1..4 edits (so 5+ = all minus 1..4)
per_ed = {}
for i, s in enumerate(open_sites):
    dom = s['url'].replace('https://', '')
    row = {}
    for lvl in ['all-activity-levels', '1..4-edits']:
        d = get(f'{AQS}/editors/aggregate/{dom}/user/all-page-types/{lvl}/monthly/{START_D}/{END_D}')
        res = d.get('items', [{}])[0].get('results', []) if d.get('items') else []
        row[lvl] = {r['timestamp'][:7]: r['editors'] for r in res}
    per_ed[s['dbname']] = {'domain': dom, **row}
    if i % 50 == 0:
        print('ed', i, dom, flush=True)
        save('per_wiki_editors.json', per_ed)
save('per_wiki_editors.json', per_ed)

# 5. Commons file count
c = get('https://commons.wikimedia.org/w/api.php?action=query&meta=siteinfo&siprop=statistics&format=json')
save('commons_stats.json', c)
print('ALL DONE', flush=True)
