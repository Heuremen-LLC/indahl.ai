#!/usr/bin/env python3
"""hosts_tick.py: HOSTS per PLAN.md. Every open-weight model on OpenRouter, every host serving it, polled and kept."""
import os, sys, json, time, glob, collections, subprocess, urllib.request, urllib.error, fcntl, random
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H); os.makedirs('data/polls', exist_ok=True)
import heuremen_kit as K
if not K.plan_committed(os.path.join(H, 'PLAN.md')): print('hosts: plan not committed'); sys.exit(0)
_l = open('data/.lock', 'w')
try: fcntl.flock(_l, fcntl.LOCK_EX | fcntl.LOCK_NB)
except OSError: print('hosts: another run holds the lock'); sys.exit(0)
UA = {'User-Agent': 'heuremen-hosts/0.1 (+https://indahl.ai/hosts)'}; W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'); B = 'https://openrouter.ai/api/v1/'
def get(u, n=3, to=40):
    for i in range(n):
        try: return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=to).read())
        except urllib.error.HTTPError as e:
            if e.code in (404, 400): return None
            time.sleep(3 * (i + 1))
        except Exception: time.sleep(3 * (i + 1))
def parse_ep(e):
    pr = e.get('pricing') or {}
    return dict(h=e.get('provider_name'), t=e.get('tag'), q=e.get('quantization'), s=e.get('status'), u5=e.get('uptime_last_5m'), u30=e.get('uptime_last_30m'), u1=e.get('uptime_last_1d'), mc=e.get('max_completion_tokens'), cl=e.get('context_length'), pp=pr.get('prompt'), cp=pr.get('completion'))
def agree(stated, mean, polls, absent_share):
    if polls < 100 or absent_share > 0.10: return 'NOT_COMPARABLE'
    return 'AGREE' if abs(stated - mean) <= 2.0 + 1e-9 else 'DISAGREE'
def gate():
    e = parse_ep({'provider_name': 'X', 'tag': 'x/fp4', 'quantization': 'fp4', 'status': 0, 'uptime_last_5m': 100, 'uptime_last_30m': 99.5, 'latency_last_30m': None, 'pricing': {'prompt': '0.1', 'completion': '0.2'}})
    ok = e['u5'] == 100 and e['mc'] is None and e['pp'] == '0.1' and parse_ep({})['u1'] is None
    ok &= agree(90.0, 92.0, 200, 0) == 'AGREE' and agree(90.0, 92.01, 200, 0) == 'DISAGREE' and agree(90.0, 90.0, 99, 0) == 'NOT_COMPARABLE' and agree(90.0, 90.0, 200, 0.2) == 'NOT_COMPARABLE'
    m = get(B + 'models'); ok &= bool(m and m.get('data'))
    hf = [x for x in (m or {}).get('data', []) if x.get('hugging_face_id')]
    if hf:
        d = get(B + 'models/%s/endpoints' % hf[0]['id']); ok &= bool(d and d['data']['endpoints'])
    else: ok = False
    print('hosts: gate', 'passed' if ok else 'FAILED', flush=True); return bool(ok), hf
ok, hf = gate()
if not ok: sys.exit(1)
now = time.time(); eps = []; failed = []
for i, m in enumerate(hf):
    d = get(B + 'models/%s/endpoints' % m['id']); time.sleep(0.4)
    if d is None: failed.append(m['id']); continue
    for e in d['data']['endpoints']: r = parse_ep(e); r['m'] = m['id']; eps.append(r)
day = time.strftime('%Y%m%d', time.gmtime(now))
poll = dict(t=now, models=len(hf), failed=failed, eps=eps)
open('data/polls/%s.jsonl' % day, 'a').write(json.dumps(poll) + '\n')
for f in glob.glob('data/polls/*.jsonl'):
    if os.path.getmtime(f) < now - 14 * 86400: os.remove(f)
print('hosts: poll', len(hf), 'models', len(eps), 'endpoints,', len(failed), 'failed', flush=True)
# ---- summary over the last 24 hours of polls
polls = []
for f in sorted(glob.glob('data/polls/*.jsonl'))[-3:]:
    for l in open(f):
        try: p = json.loads(l)
        except Exception: continue
        if p['t'] >= now - 86400: polls.append(p)
allp = sum(1 for f in glob.glob('data/polls/*.jsonl') for _ in open(f)); first = min(float(json.loads(open(f).readline())['t']) for f in glob.glob('data/polls/*.jsonl'))
key = lambda e: '%s | %s | %s' % (e['m'], e['h'], e['t'])
cur = {key(e): e for e in eps}
problems = {k: dict(quantization=e['q'] or '-', uptime_5m=e['u5'], uptime_30m=round(e['u30'], 1) if e['u30'] is not None else None, uptime_1d=round(e['u1'], 1) if e['u1'] is not None else None) for k, e in cur.items() if (e['s'] not in (0, None)) or (e['u5'] is not None and e['u5'] < 100)}
qt = collections.defaultdict(lambda: [0, 0, set()])
for p in polls:
    for e in p['eps']:
        if e['u5'] is None: continue
        q = e['q'] or 'not stated'; qt[q][0] += 1; qt[q][1] += 1 if e['u5'] >= 100 else 0; qt[q][2].add(key(e))
quant = {q: dict(endpoints=len(v[2]), readings=v[0], at_100='%.1f%%' % (100 * v[1] / v[0])) for q, v in sorted(qt.items(), key=lambda kv: kv[0])}
perm = collections.Counter(e['m'] for e in eps); b = collections.Counter('1 host' if n == 1 else ('2 to 4 hosts' if n <= 4 else ('5 to 9 hosts' if n <= 9 else '10 or more hosts')) for n in perm.values())
hist = collections.defaultdict(list)
for p in polls:
    present = {key(e): e for e in p['eps']}
    for k in set(cur) | set(present): hist[k].append(present.get(k))
rows = {}
for k in cur:
    h = hist[k]; polls_n = len(h); absent = sum(1 for x in h if x is None) / polls_n if polls_n else 1
    u5 = [x['u5'] for x in h if x and x['u5'] is not None]
    if polls_n >= 100 and cur[k]['u1'] is not None and u5: rows[k] = (agree(cur[k]['u1'], sum(u5) / len(u5), polls_n, absent), cur[k]['u1'], sum(u5) / len(u5), polls_n)
    else: rows[k] = ('NOT_COMPARABLE', cur[k]['u1'], None, polls_n)
cmp = [k for k, v in rows.items() if v[0] in ('AGREE', 'DISAGREE')]; nd = [k for k in cmp if rows[k][0] == 'DISAGREE']
lo, hi = K.wilson(len(nd), len(cmp)) if cmp else (0, 1)
oc = 'NOTHING_RETURNED' if not cmp else (K.ABOVE if lo > 0.05 else (K.CONSISTENT if hi < 0.15 else K.CANNOT_TELL))
hc = json.load(open('data/hand_checked.json')) if os.path.exists('data/hand_checked.json') else {}
samp = random.Random(7).sample(sorted(nd), min(10, len(nd))) if nd else []
json.dump(dict(sample_seed7=samp, disagree=sorted(nd)), open('data/hand_check.json', 'w'), indent=1)
out = dict(updated=time.strftime('%d %b %H:%M', time.gmtime(now)), gate='passed', polls_kept=allp, first_poll=time.strftime('%d %b %H:%M UTC', time.gmtime(first)), models=len({e['m'] for e in eps}), hosts=len({e['h'] for e in eps}), endpoints=len(eps), failed_models=len(failed),
           problems_now=len(problems), problems=dict(list(problems.items())[:60]), quantization=quant, models_by_hosts=dict(b),
           headline=dict(of=len(cmp), n=len(nd), share=round(len(nd) / len(cmp), 4) if cmp else None, share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=oc), headline_n=len(nd), headline_of=len(cmp),
           top_line='%d endpoints on %d hosts for %d open-weight models. %d with a 5-minute uptime below 100 now.' % (len(eps), len({e['h'] for e in eps}), len({e['m'] for e in eps}), len(problems)))
json.dump(out, open('summary_hosts.json', 'w'), indent=1)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
pr = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'hosts_live', '--path', os.path.join(H, 'summary_hosts.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
with open('history.jsonl', 'a') as f: f.write(json.dumps(dict(t=out['updated'], endpoints=len(eps), problems=len(problems), failed=len(failed))) + '\n')
print('hosts:', out['top_line'], 'test', out['headline']['outcome'], 'published' if pr.returncode == 0 else 'publish FAILED', flush=True)
