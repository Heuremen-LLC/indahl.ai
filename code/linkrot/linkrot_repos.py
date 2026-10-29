#!/usr/bin/env python3
"""linkrot_repos.py: LINKROT second question per PLAN_REPOS.md. For GitHub links that read LIVE, asks the GitHub GraphQL API (through the gh sign-in) whether the repository holds code.
Reads data/links.json, writes data/repos.json and summary_repos.json. Each repository is read again after 30 days. Known-good controls run first."""
import os, sys, re, json, time, subprocess, collections as C
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H); import heuremen_kit as K
if not K.plan_committed(os.path.join(H, 'PLAN_REPOS.md')): print('repos: plan not committed'); sys.exit(0)
FIELDS = 'isEmpty isArchived isFork pushedAt diskUsage licenseInfo { spdxId } defaultBranchRef { target { ... on Commit { history { totalCount } } } }'
def q(pairs):
    body = ' '.join('r%d: repository(owner:"%s", name:"%s") { %s }' % (i, o, n, FIELDS) for i, (o, n) in enumerate(pairs))
    r = subprocess.run(['gh', 'api', 'graphql', '-f', 'query={ ' + body + ' }'], capture_output=True, text=True)
    try: d = json.loads(r.stdout).get('data') or {}
    except Exception: return None
    return [d.get('r%d' % i) for i in range(len(pairs))]
def state(x, now):
    if x is None: return 'NOT_FOUND', {}
    commits = ((((x.get('defaultBranchRef') or {}).get('target') or {}).get('history') or {}).get('totalCount')) or 0
    info = dict(archived=bool(x['isArchived']), fork=bool(x['isFork']), commits=commits, pushed=x.get('pushedAt'), license=(x.get('licenseInfo') or {}).get('spdxId'))
    if x['isEmpty'] or commits == 0: return 'EMPTY', info
    return ('STUB' if commits <= 3 else 'CODE'), info
now = time.time(); repos = json.load(open('data/repos.json')) if os.path.exists('data/repos.json') else {}
ctl = q([('torvalds', 'linux'), ('Heuremen-LLC', 'linkrot-empty-control')]); gate_ok = False
if ctl:
    a, b = state(ctl[0], now)[0], state(ctl[1], now)[0]; gate_ok = (a == 'CODE' and b == 'EMPTY'); print('repos: controls', a, b)
links = json.load(open('data/links.json')) if os.path.exists('data/links.json') else {}
todo = []
for u, e in links.items():
    m = re.match(r'https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)$', u)
    if m and e['hist'] and e['hist'][-1][1] == 'LIVE' and (u not in repos or now - repos[u]['read'] > 30 * 86400): todo.append((u, m.group(1), m.group(2)))
n = 0
if gate_ok:
    for i in range(0, len(todo), 50):
        chunk = todo[i:i + 50]; res = q([(o, nm) for _, o, nm in chunk])
        if res is None: print('repos: NOTHING_RETURNED for a batch'); continue
        for (u, o, nm), x in zip(chunk, res):
            st, info = state(x, now); repos[u] = dict(read=now, state=st, **info); n += 1
        time.sleep(1)
    json.dump(repos, open('data/repos.json.tmp', 'w')); os.replace('data/repos.json.tmp', 'data/repos.json')
def cell(rs):
    c = C.Counter(r['state'] for r in rs); read = c['EMPTY'] + c['STUB'] + c['CODE']; lo, hi = K.wilson(c['EMPTY'], read)
    oc = K.CANNOT_TELL if (read < 30 or not gate_ok) else (K.ABOVE if lo > 0.10 else (K.CONSISTENT if hi < 0.05 else K.CANNOT_TELL))
    stale = sum(1 for r in rs if r['state'] != 'NOT_FOUND' and r.get('pushed') and time.mktime(time.strptime(r['pushed'][:10], '%Y-%m-%d')) < now - 365 * 86400)
    nolic = sum(1 for r in rs if r['state'] in ('CODE', 'STUB') and not r.get('license')); nl_lo, nl_hi = K.wilson(nolic, read)   # addendum 1, descriptive
    return dict(no_license=nolic, no_license_share=round(nolic / read, 4) if read else None, no_license_share_lo=round(nl_lo, 4), no_license_share_hi=round(nl_hi, 4), repos=read, empty=c['EMPTY'], stub=c['STUB'], code=c['CODE'], not_found=c['NOT_FOUND'], archived=sum(1 for r in rs if r.get('archived')), stale=stale, empty_share=round(c['EMPTY'] / read, 4) if read else None, lo=round(lo, 4), hi=round(hi, 4), outcome=oc)
yrs = {}
for u, r in repos.items():
    for y in {min(links[u]['years'])} if u in links else []: yrs.setdefault(str(y), []).append(r)
out = dict(gate='passed' if gate_ok else 'FAILED', all=cell(list(repos.values())), by_year={y: cell(v) for y, v in sorted(yrs.items())}, read_this_round=n)
json.dump(out, open('summary_repos.json', 'w'), indent=1); print('repos:', n, 'read,', out['all'])
