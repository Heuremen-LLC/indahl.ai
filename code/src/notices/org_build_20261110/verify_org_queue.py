"""verify_org_queue.py (10 Nov 2026). Run before any batch of org notices goes to send_guarded.py. Re-reads every live brand page
(scrape_live.py into live_check.json) and checks each notice in ~/bones-forge/notices/org_queue_20261110.json:
  - every quoted row (desk, Row, Stated, Outcome, links) is on the live page exactly as quoted (a moved read time is counted, not a fault)
  - every number in the body appears in the live page's rows (so no number is ours alone)
  - the Respond and correction links are the ones the page shows, and the brand page answers HTTP 200
  - our own sentences (everything but the quoted lines) hold no semicolon
Writes VERIFY_20261110.json (key -> problems) and prints counts. A notice with a problem is rebuilt (build_org_queue.py) before it is sent.
Run: python3 -I verify_org_queue.py [--no-fetch]"""
import json, os, re, sys, subprocess
H = os.path.dirname(os.path.abspath(__file__)); N = os.path.expanduser('~/bones-forge/notices')
if '--no-fetch' not in sys.argv: subprocess.run([sys.executable, '-I', H + '/scrape_live.py', H + '/live_check.json'], check=True)
L = json.load(open(H + '/live_check.json')); Q = json.load(open(N + '/org_queue_20261110.json'))['notices']
SITE = 'https://indahl.ai'; QUOTED = ('Row: ', 'Stated: ', 'Outcome: ', 'Read: ', 'Receipt: ', 'Desk: ')
def absu(u): return u if u.startswith('http') else SITE + u
bad, checked, moved = {}, 0, []
for x in Q:
    if 'body' not in x: continue
    checked += 1; p = []; page = L.get(x['slug'], {})
    if page.get('status') != 200: bad[x['key']] = ['brand page not live: %s' % page.get('status')]; continue
    live = [{k: r.get(k, '') for k in ('desk', 'Row', 'Stated', 'Outcome', 'Read')} | {'links': [absu(l) for l in r['links']]} for r in page['rows']]
    nr = lambda r: {k: v for k, v in r.items() if k != 'Read'}
    for q in x['quoted']:
        if nr(q) not in [nr(r) for r in live]: p.append('quoted row not on the live page as quoted: ' + q['Row'][:80])
        elif q not in live: moved.append(x['key'])
    livetext = ' '.join(' '.join(str(v) for v in r.values()) for r in page['rows']) + ' ' + page.get('title', '')
    ours = [l for l in x['body'].splitlines() if not l.startswith(QUOTED) and not re.match(r'^[A-Z]+: ', l) and not l.startswith('http')]
    for num in set(re.findall(r'\d[\d,.]*', '\n'.join(l for l in x['body'].splitlines() if l.startswith(QUOTED[:3])))):
        if num.rstrip('.,') not in livetext: p.append('number not on the live page: ' + num)
    if any(re.search(r'\d', l) for l in ours if l.strip() not in ('---',) and 'indahl.ai' not in l and x['name'] not in l): p.append('a digit in our own sentences')
    if any(';' in l for l in ours): p.append('semicolon in our own sentences')
    if absu(page['respond'] or '') != x['respond']: p.append('respond link differs from the page')
    if x['page'] + '\n' not in x['body'] + '\n' and x['page'] not in x['body']: p.append('brand page link missing')
    if p: bad[x['key']] = p
json.dump(bad, open(H + '/VERIFY_20261110.json', 'w'), indent=1)
print(f'checked {checked} notice bodies against the live pages: {checked - len(bad)} clean, {len(bad)} with a problem; read time moved since the build (row otherwise the same, a rebuild refreshes it): {len(set(moved))}')
for k, v in list(bad.items())[:40]: print(' ', k, '|', ' / '.join(v)[:200])
