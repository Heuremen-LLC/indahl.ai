#!/usr/bin/env python3
"""RANK live feed: data/rank_live.json from the desk's own results (data/rank.json, data/checks.json, data/checks_nj.json, data/checks_grad.json, data/claims_scored.json),
served at indahl.ai/rank/live.json (worker route reads KV key rank_live). The US News lists are read by hand in a browser, so this rider does not
read US News. It republishes the current results with a fresh 'updated' stamp and keeps 'read_at' (the date the lists were read).
  python3 rank_tick.py [--publish]     --publish puts the file in the site KV (wrangler), as the WIKI and NEO riders do.
Standard library only. Heuremen LLC."""
import json, os, sys, time, subprocess
from collections import Counter
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H)
D = json.load(open('data/rank.json', encoding='utf-8'))
CK = json.load(open('data/checks.json', encoding='utf-8'))['checks']
NJ = json.load(open('data/checks_nj.json', encoding='utf-8'))
CL = json.load(open('data/claims_scored.json', encoding='utf-8'))
GR = json.load(open('data/checks_grad.json', encoding='utf-8'))['checks'] if os.path.exists('data/checks_grad.json') and 'Business schools' in open('rank_body.html', encoding='utf-8').read() else []   # only once the shipped page carries them
allc = [c for c in CK + NJ['checks'] + GR if c['outcome'] != 'DISPLAY']
by = Counter((c['list'], c['outcome']) for c in allc)
NAMES = {'hs': 'High schools (national)', 'nu': 'National Universities', 'nlac': 'National Liberal Arts Colleges', 'law': 'Law schools', 'mba': 'Business schools (full-time MBA)',
         'eng': 'Engineering schools', 'edu': 'Education schools', 'med': 'Medical schools, research, Tier 1', 'nj_hs': 'New Jersey high schools',
         'nj_k8': 'New Jersey elementary and middle schools', 'nj_col': 'New Jersey colleges'}
checks = [dict(key=k, name=n, match=by[(k, 'MATCH')], mismatch=by[(k, 'MISMATCH')], cannot_tell=by[(k, 'CANNOT_TELL')],
               outcomes=[dict(school=c['school'], figure=c['field'], usnews=c['usn'], public=c['pub'], public_year=c['pub_year'], outcome=c['outcome'], reason=c['reason'])
                         for c in allc if c['list'] == k])
          for k, n in NAMES.items() if any(c['list'] == k for c in allc)]
lists = [dict(key=l['key'], title=l['title'], edition=l['edition'], scope=l['scope'], list_url=l['list_url'], method_url=l['method_url'], schools_listed=len(l['rows']),
              no_national_list=(l['scope'] == 'none'), tiers_only=(l['scope'] == 'tiers')) for l in D['lists']]
m = sum(x['match'] for x in checks); x_ = sum(x['mismatch'] for x in checks); t = sum(x['cannot_tell'] for x in checks)
mm = [f"{c['school']}, {c['field']}" for c in allc if c['outcome'] == 'MISMATCH']
live = dict(desk='RANK', updated=time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime()), read_at=D['read'], page='https://indahl.ai/rank',
            headline=dict(big=f'{x_} of {m + x_}', line=f'US News figures that differ from the public record after rounding, among those that could be compared for the same year ({t} more read cannot tell). ' + ('Differs: ' + '; '.join(mm) + '.' if mm else '')),
            lists=lists, checks=checks, claims=dict(match=sum(1 for c in CL if c['outcome'] == 'MATCH'), mismatch=sum(1 for c in CL if c['outcome'] == 'MISMATCH'), cannot_tell=sum(1 for c in CL if c['outcome'] == 'CANNOT_TELL')),
            participation_nj=NJ['participation'], note='Rankings, list names and method text belong to US News & World Report. This feed carries only our readings and the figures checked.')
os.makedirs('data', exist_ok=True)
json.dump(live, open('data/rank_live.json', 'w'), indent=1, ensure_ascii=False)
print('rank_live', live['updated'], live['headline']['big'], flush=True)
if '--publish' in sys.argv:
    env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
    p = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'rank_live', '--path', os.path.join(H, 'data', 'rank_live.json'),
                        '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'), env=env, capture_output=True, text=True)
    print('rank: ' + live['updated'] + (' published' if p.returncode == 0 else ' publish FAILED ' + p.stderr[-200:]), flush=True)
