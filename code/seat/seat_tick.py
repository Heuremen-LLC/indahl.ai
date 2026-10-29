#!/usr/bin/env python3
"""seat_tick.py: SEAT rider. Asks the GitHub runner for a new probe (repository_dispatch) and publishes the runner's saved probes as the SEAT page, per PLAN.md.
The Mac only relays what the runner wrote to Heuremen-LLC/nodes; it adds no reading of its own."""
import os, sys, json, time, subprocess, urllib.request, datetime as D
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
import heuremen_kit as K
if not K.plan_committed(os.path.join(H, 'PLAN.md')): print('seat: plan not committed'); sys.exit(0)
W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'); FIRST = '2026-10-29T11:57:00Z'
# keep the seat's target list in step with the site: every page in the menu is a page target, every corner with a live feed is a feed target (limit 40 hours unless set)
import re
NODES = os.path.expanduser('~/bones-forge/nodes_repo'); TJ = NODES + '/drift/targets.json'
try:
    src = open(os.path.expanduser('~/bones-forge/indahl-ai/build_site.py')).read(); slugs = sorted(set(re.findall(r"\('/([a-z0-9]+)', '[A-Z0-9]+'[,)]", src)))   # 29 Oct: read the whole file (menu, desks), not one line
    T = json.load(open(TJ)); have = set(T['pages']); hf = {f[0] for f in T['feeds']}; ch = False
    for sl in slugs:
        if sl not in have: T['pages'].append(sl); ch = True
        if sl in ('qia', 'iris', 'oy', 'atlas', 'sad'): continue
        if sl + '/live.json' not in hf: T['feeds'].append([sl + '/live.json', 40]); ch = True
    if ch:
        json.dump(T, open(TJ, 'w')); ID = subprocess.run(['/opt/homebrew/bin/gh', 'api', 'user', '--jq', '.id'], capture_output=True, text=True).stdout.strip()
        g = lambda *a: subprocess.run(['git', '-C', NODES, '-c', 'user.name=Bones', '-c', 'user.email=%s+indahl-ai@users.noreply.github.com' % ID] + list(a), capture_output=True, text=True)
        g('pull', '-q'); g('add', 'drift/targets.json'); g('commit', '-q', '-m', 'DRIFT seat: targets follow the site'); g('push', '-q')
except Exception as e: print('seat: targets not updated', type(e).__name__)
subprocess.run(['/opt/homebrew/bin/gh', 'api', 'repos/Heuremen-LLC/nodes/dispatches', '-f', 'event_type=drift-probe'], capture_output=True, text=True)
raw = urllib.request.urlopen(urllib.request.Request('https://raw.githubusercontent.com/Heuremen-LLC/nodes/main/data/drift/history.jsonl?x=%d' % time.time(), headers={'User-Agent': 'heuremen-seat/0.1'}), timeout=60).read().decode()
rows = [json.loads(l) for l in raw.splitlines() if l.strip()]; rows = [r for r in rows if r['t'] >= FIRST]
if not rows: print('seat: no runner probes yet'); sys.exit(0)
good = [r for r in rows if r['control'] == 'PASSED']; last = good[-1] if good else rows[-1]
def bad(r):
    if r['control'] != 'PASSED': return None
    pg = r['pages']; return dict(drift=[p for p in pg if pg[p] != 'MATCH'], feeds=[f for f, v in r['feeds'].items() if v['state'] != 'FRESH'], chain=r['chain']['state'] != 'OK')
# a page is DRIFT only when it differs in two consecutive probes
def drift_pages(i):
    a = good[i]['pages']; b = good[i - 1]['pages'] if i else {}
    return [p for p in a if a[p] != 'MATCH' and b.get(p, 'MATCH') != 'MATCH']
win = good[-24:]; flags = []
for k, r in enumerate(win):
    idx = len(good) - len(win) + k; flags.append(bool(drift_pages(idx)) or any(v['state'] != 'FRESH' for v in r['feeds'].values()) or r['chain']['state'] != 'OK')
# 29 Oct (internal audit, Addendum 1): a standing fault is one incident however many probes see it, so the count is runs of consecutive flagged probes
nflag = sum(1 for k, f in enumerate(flags) if f and (k == 0 or not flags[k - 1]))
import datetime as _D
age_h = (_D.datetime.now(_D.timezone.utc) - _D.datetime.strptime(last['t'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=_D.timezone.utc)).total_seconds() / 3600
oc = K.CANNOT_TELL if (len(win) < 24 or age_h > 3) else (K.CONSISTENT if nflag == 0 else (K.ABOVE if nflag >= 3 else K.CANNOT_TELL))
pg = last['pages']; fd = last['feeds']
out = dict(updated=time.strftime('%d %b %H:%M', time.gmtime()), probes=len(good), failed_controls=len(rows) - len(good), last_probe=last['t'].replace('T', ' ').replace('Z', ' UTC'),
           rolling={'Last 24 probes, counted as incidents': dict(of=len(win), n=nflag, outcome=oc, newest_probe_hours=round(age_h, 1))},
           now={'Pages matching the public repository': dict(n=sum(1 for v in pg.values() if v == 'MATCH'), of=len(pg)), 'Feeds younger than their limit': dict(n=sum(1 for v in fd.values() if v['state'] == 'FRESH'), of=len(fd)),
                'Archive chain': dict(n=last['chain']['entries'], of=last['chain']['entries'], state=last['chain']['state'])},
           feeds=[dict(feed='/' + f, age_h=v.get('age_h'), limit_h=v.get('limit_h'), state=v['state']) for f, v in fd.items()],
           not_matching=[dict(page='/' + p, state=v) for p, v in pg.items() if v != 'MATCH'])
json.dump(out, open('summary_seat.json', 'w'), indent=1)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
pr = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'seat_live', '--path', os.path.join(H, 'summary_seat.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
print('seat:', len(good), 'probes;', 'last', last['t'], 'published' if pr.returncode == 0 else 'publish FAILED', flush=True)
