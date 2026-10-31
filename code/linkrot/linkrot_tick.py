#!/usr/bin/env python3
"""linkrot_tick.py: LINKROT rider for the HST tick bus (every 6 ticks). Per PLAN.md + Addendum 1: known-good gate first, then checks links that are due (never read, or last read over 7 days ago),
at most 600 per round, one request at a time per host with a pause, then rewrites summary_linkrot.json and publishes it to KV linkrot_live."""
import os, sys, re, json, time, socket, ssl, subprocess, threading, urllib.request, urllib.error, urllib.parse, collections as C
from concurrent.futures import ThreadPoolExecutor
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
import heuremen_kit as K, fcntl
_lock = open(os.path.join(H, 'data', '.lock'), 'w')
try: fcntl.flock(_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
except OSError: print('linkrot: another run holds the lock, skipping'); sys.exit(0)   # 29 Oct: two writers corrupted links.json once
W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'); UA = 'heuremen-linkrot/0.1 (+https://indahl.ai/linkrot)'
if not K.plan_committed(os.path.join(H, 'PLAN.md')): print('linkrot: plan not committed, refusing to read'); sys.exit(0)
LIVE_CTL = ['https://github.com/torvalds/linux', 'https://www.python.org', 'https://arxiv.org/abs/1706.03762', 'https://example.com', 'https://zenodo.org']
DEAD_CTL = ['https://github.com/this-owner-does-not-exist-7q2/none', 'https://example.com/no-such-page-7q2', 'https://made-up-host-7q2.invalid', 'https://raw.githubusercontent.com/torvalds/linux/master/no-such-file-7q2', 'https://zenodo.org/records/99999999999']
locks = C.defaultdict(threading.Lock); lastreq = {}
def probe(u):
    """returns (status, final_url)"""
    host = urllib.parse.urlparse(u).netloc
    with locks[host]:
        wait = 1.2 - (time.time() - lastreq.get(host, 0))
        if wait > 0: time.sleep(wait)
        try:
            for method in ('HEAD', 'GET'):
                try:
                    r = urllib.request.urlopen(urllib.request.Request(u, method=method, headers={'User-Agent': UA}), timeout=20); code = r.status; fin = r.geturl(); break
                except urllib.error.HTTPError as e:
                    if method == 'HEAD' and e.code in (403, 405, 501): continue
                    code = e.code; fin = e.geturl(); break
            if 200 <= code < 300: return 'LIVE', fin
            if code in (404, 410, 451): return 'GONE', fin
            return 'BLOCKED', fin
        except urllib.error.URLError as e:
            r = getattr(e, 'reason', None)
            if isinstance(r, socket.gaierror): return 'DNS_FAIL', u
            if isinstance(r, (socket.timeout, TimeoutError)) or 'timed out' in str(r): return 'TIMEOUT', u
            return 'BLOCKED', u
        except (socket.timeout, TimeoutError): return 'TIMEOUT', u
        except Exception: return 'BLOCKED', u
        finally: lastreq[host] = time.time()
# gate
ctl = {u: probe(u)[0] for u in LIVE_CTL + DEAD_CTL}
gate_ok, msg = K.known_good(lambda c: all(c[u] == 'LIVE' for u in LIVE_CTL) and all(c[u] in ('GONE', 'DNS_FAIL') for u in DEAD_CTL), ctl)
print('linkrot: gate', msg, {u.split('//')[1][:28]: s for u, s in ctl.items()} if not gate_ok else '')
papers = [json.loads(l) for l in open('data/papers.jsonl')] if os.path.exists('data/papers.jsonl') else []
links = json.load(open('data/links.json')) if os.path.exists('data/links.json') else {}
for p in papers:
    for u in p['urls']:
        e = links.setdefault(u, dict(host=urllib.parse.urlparse(u).netloc.replace('www.', ''), years=[], hist=[]))
        if p['year'] not in e['years']: e['years'].append(p['year'])
now = time.time(); due = [u for u, e in links.items() if not e['hist'] or now - e['hist'][-1][0] > 7 * 86400][:600]
def one(u):
    s, fin = probe(u); return u, s, fin
n = 0
if gate_ok and due:
    with ThreadPoolExecutor(8) as ex:
        for u, s, fin in ex.map(one, due):
            e = links[u]; moved = False
            m = re.match(r'https://(?:www\.)?(github|gitlab)\.com/([^/]+)/([^/?#]+)', u); f = re.match(r'https://(?:www\.)?(github|gitlab)\.com/([^/]+)/([^/?#]+)', fin or '')
            if s == 'LIVE' and m and f and (m.group(2).lower(), m.group(3).lower()) != (f.group(2).lower(), f.group(3).lower()): moved = True
            e['hist'].append([now, s]); e['moved'] = moved; n += 1
    json.dump(links, open('data/links.json.tmp', 'w')); os.replace('data/links.json.tmp', 'data/links.json')
# second seat (PLAN.md Addendum 2): push the list to the nodes repository and dispatch its workflow every 7 days, merge the results it committed
NODES = os.path.expanduser('~/bones-forge/nodes_repo'); S2 = 'data/seat2.json'; st2 = json.load(open(S2)) if os.path.exists(S2) else {}
def seat2():
    if not os.path.isdir(NODES): return
    if time.time() - st2.get('dispatched', 0) > 7 * 86400 and len(links) > 0:
        subprocess.run(['git', 'pull', '-q'], cwd=NODES, capture_output=True); open(os.path.join(NODES, 'data/linkrot/urls.txt'), 'w').write('\n'.join(sorted(links)) + '\n')
        subprocess.run(['git', 'add', 'data/linkrot/urls.txt'], cwd=NODES, capture_output=True)
        c = subprocess.run(['git', '-c', 'user.name=Bones', '-c', 'user.email=268764679+claude-wayfinder@users.noreply.github.com', 'commit', '-qm', 'LINKROT list from the first seat'], cwd=NODES, capture_output=True, text=True)
        subprocess.run(['git', 'push', '-q'], cwd=NODES, capture_output=True)
        d = subprocess.run(['/opt/homebrew/bin/gh', 'api', 'repos/Heuremen-LLC/nodes/dispatches', '-f', 'event_type=linkrot-probe'], capture_output=True, text=True)
        if d.returncode == 0: st2['dispatched'] = time.time(); json.dump(st2, open(S2, 'w'))
    try: raw = urllib.request.urlopen(urllib.request.Request('https://raw.githubusercontent.com/Heuremen-LLC/nodes/main/data/linkrot/results.jsonl', headers={'User-Agent': UA}), timeout=60).read().decode()
    except Exception: return
    n = 0
    for l in raw.splitlines():
        try: r = json.loads(l)
        except Exception: continue
        e = links.get(r['url'])
        if e is not None and r['t'] > (e.get('seat2') or [0])[0]: e['seat2'] = [r['t'], r['status']]; n += 1
    if n: json.dump(links, open('data/links.json.tmp', 'w')); os.replace('data/links.json.tmp', 'data/links.json')
try: seat2()
except Exception as ex: print('linkrot: seat 2 step failed', type(ex).__name__)
if gate_ok: subprocess.run([sys.executable, '-I', os.path.join(H, 'linkrot_repos.py')], capture_output=True, timeout=1500)   # second question, PLAN_REPOS.md
# summary
def cell(rows):
    c = C.Counter(r for r in rows); live, gone, dns = c['LIVE'], c['GONE'], c['DNS_FAIL']; rd = live + gone + dns; rot = gone + dns
    lo, hi = K.wilson(rot, rd)
    oc = K.CANNOT_TELL if (rd < 30 or not gate_ok) else (K.ABOVE if lo > 0.10 else (K.CONSISTENT if hi < 0.05 else K.CANNOT_TELL))
    return dict(links=len(rows), live=live, gone=gone, dns_fail=dns, blocked=c['BLOCKED'], timeout=c['TIMEOUT'], rot_share=round(rot / rd, 4) if rd else None, lo=round(lo, 4), hi=round(hi, 4), outcome=oc)
def combined(e):
    a = e['hist'][-1]; b = e.get('seat2'); bad = ('GONE', 'DNS_FAIL')
    if b and abs(a[0] - b[0]) <= 14 * 86400:
        if (a[1] == 'LIVE' and b[1] in bad) or (a[1] in bad and b[1] == 'LIVE'): return 'BLOCKED'
    return a[1]
cur = {u: combined(e) for u, e in links.items() if e['hist']}
by_year = {}; by_host = {}
for y in sorted({y for e in links.values() for y in e['years']}):
    by_year[str(y)] = cell([cur[u] for u, e in links.items() if u in cur and min(e['years']) == y])
for hname in sorted({e['host'] for e in links.values()}):
    by_host[hname] = cell([cur[u] for u, e in links.items() if u in cur and e['host'] == hname])
ret = sum(1 for e in links.values() if len(e['hist']) > 1 and e['hist'][-1][1] == 'LIVE' and any(s in ('GONE', 'DNS_FAIL') for _, s in e['hist'][:-1]))
newly = sum(1 for e in links.values() if len(e['hist']) > 1 and e['hist'][-1][1] in ('GONE', 'DNS_FAIL') and e['hist'][-2][1] == 'LIVE')
out = dict(updated=time.strftime('%d %b %H:%M', time.gmtime(now)), gate='passed' if gate_ok else 'FAILED', papers=len(papers), links=len(links), read=len(cur), due=len([u for u, e in links.items() if not e['hist'] or now - e['hist'][-1][0] > 7 * 86400]),
           all=cell(list(cur.values())), by_year=by_year, by_host=by_host, returned=ret, newly_gone=newly, seat2_links=sum(1 for e in links.values() if e.get('seat2') and e['hist'] and abs(e['hist'][-1][0] - e['seat2'][0]) <= 14 * 86400), seat_disagreements=sum(1 for e in links.values() if e['hist'] and e.get('seat2') and combined(e) == 'BLOCKED' and e['hist'][-1][1] != 'BLOCKED'), moved=sum(1 for e in links.values() if e.get('moved')))
if os.path.exists('summary_repos.json'): out['repos'] = json.load(open('summary_repos.json'))
json.dump(out, open('summary_linkrot.json', 'w'), indent=1)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
p = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'linkrot_live', '--path', os.path.join(H, 'summary_linkrot.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
print('linkrot:', n, 'checked,', len(links), 'links,', out['all']['outcome'], 'published' if p.returncode == 0 else 'publish FAILED')
