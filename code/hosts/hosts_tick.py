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
import sys as _sys, os as _os; _sys.path.insert(0, _os.path.expanduser('~/bones-forge/watch')); import desk_progress as DP
for i, m in enumerate(hf):
    DP.report('hosts', i, len(hf), m.get('id', ''))   # 31 Oct: live progress bar on the page
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
# 30 Oct (site pass H-5): the list is, as PLAN.md Display says, endpoints with a status other than 0 OR a 5-minute uptime below 100. The page now says so, shows the status, rounds the uptimes and lists every row (it was cut to 60 with the count left whole).
r1 = lambda x: round(x, 1) if x is not None else None
problems = {k: dict(quantization=e['q'] or '-', status=e['s'], uptime_5m=r1(e['u5']), uptime_30m=r1(e['u30']), uptime_1d=r1(e['u1']), url='https://openrouter.ai/' + e['m']) for k, e in cur.items() if (e['s'] not in (0, None)) or (e['u5'] is not None and e['u5'] < 100)}
below_100_now = sum(1 for e in cur.values() if e['u5'] is not None and e['u5'] < 100); flagged_now = sum(1 for e in cur.values() if e['s'] not in (0, None))
qt = collections.defaultdict(lambda: [0, 0, set()])
for p in polls:
    for e in p['eps']:
        if e['u5'] is None: continue
        q = e['q'] or 'not stated'; qt[q][0] += 1; qt[q][1] += 1 if e['u5'] >= 100 else 0; qt[q][2].add(key(e))
quant = {q: dict(endpoints=len(v[2]), readings=v[0], at_100='%.1f%%' % (100 * v[1] / v[0])) for q, v in sorted(qt.items(), key=lambda kv: kv[0])}
perm = collections.Counter(e['m'] for e in eps); b = collections.Counter('1 host' if n == 1 else ('2 to 4 hosts' if n <= 4 else ('5 to 9 hosts' if n <= 9 else '10 or more hosts')) for n in perm.values())
# 10 Nov 2026 (cold read row 6): PLAN.md compares at "a 24-hour span ending at a poll" with at least 100 polls, "taking the latest qualifying
# poll". The code only tried the span ending now, so when the poll cadence fell below 100 a day (62 in the 24 h to 10 Nov 11:00) the test
# returned nothing. It now takes the latest kept poll whose 24-hour span holds at least 100 polls, and the feed says when that span ended.
# No rule changed: same threshold, same tolerance, same absence limit.
import re as _re, bisect as _bi
_ts = sorted(float(m.group(1)) for f in glob.glob('data/polls/*.jsonl') for m in (_re.match(r'\{"t": ([0-9.]+)', l) for l in open(f)) if m)
_q = [t for i, t in enumerate(_ts) if i - _bi.bisect_left(_ts, t - 86400) + 1 >= 100]
wend = _q[-1] if _q else None
if wend is not None and wend < now - 1:
    wpolls = []
    for f in sorted(glob.glob('data/polls/*.jsonl')):
        if os.path.getmtime(f) < wend - 86400: continue
        for l in open(f):
            _m = _re.match(r'\{"t": ([0-9.]+)', l)
            if _m and wend - 86400 <= float(_m.group(1)) <= wend:
                try: wpolls.append(json.loads(l))
                except Exception: pass
    wpolls.sort(key=lambda p: p['t'])
else: wpolls = polls
wcur = {key(e): e for e in wpolls[-1]['eps']} if wpolls else {}
hist = collections.defaultdict(list)
for p in wpolls:
    present = {key(e): e for e in p['eps']}
    for k in set(wcur) | set(present): hist[k].append(present.get(k))
rows = {}
for k in wcur:
    h = hist[k]; polls_n = len(h); absent = sum(1 for x in h if x is None) / polls_n if polls_n else 1
    u5 = [x['u5'] for x in h if x and x['u5'] is not None]
    if polls_n >= 100 and wcur[k]['u1'] is not None and u5: rows[k] = (agree(wcur[k]['u1'], sum(u5) / len(u5), polls_n, absent), wcur[k]['u1'], sum(u5) / len(u5), polls_n)
    else: rows[k] = ('NOT_COMPARABLE', wcur[k]['u1'], None, polls_n)
cmp = [k for k, v in rows.items() if v[0] in ('AGREE', 'DISAGREE')]; nd = [k for k in cmp if rows[k][0] == 'DISAGREE']
lo, hi = K.wilson(len(nd), len(cmp)) if cmp else (0, 1)
oc = 'NOTHING_RETURNED' if not cmp else (K.ABOVE if lo > 0.05 else (K.CONSISTENT if hi < 0.15 else K.CANNOT_TELL))
hc = json.load(open('data/hand_checked.json')) if os.path.exists('data/hand_checked.json') else {}
samp = random.Random(7).sample(sorted(nd), min(10, len(nd))) if nd else []
json.dump(dict(sample_seed7=samp, disagree=sorted(nd)), open('data/hand_check.json', 'w'), indent=1)
out = dict(updated=time.strftime('%d %b %H:%M', time.gmtime(now)), gate='passed', polls_kept=allp, first_poll=time.strftime('%d %b %H:%M UTC', time.gmtime(first)), models=len({e['m'] for e in eps}), hosts=len({e['h'] for e in eps}), endpoints=len(eps), failed_models=len(failed),
           problems_now=len(problems), below_100_now=below_100_now, flagged_now=flagged_now, problems=problems, quantization=quant, models_by_hosts=dict(b),
           headline=dict(of=len(cmp), n=len(nd), share=round(len(nd) / len(cmp), 4) if cmp else None, share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=oc, span_end=time.strftime('%d %b %H:%M', time.gmtime(wend)) if wend else None, span_polls=len(wpolls) if wend else len(polls), polls_24h=len(polls)), headline_n=len(nd), headline_of=len(cmp),
           top_line='%d endpoints on %d hosts for %d open-weight models. %d are flagged by OpenRouter or show a 5-minute uptime below 100 now.' % (len(eps), len({e['h'] for e in eps}), len({e['m'] for e in eps}), len(problems)))
json.dump(out, open('summary_hosts.json', 'w'), indent=1)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
pr = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'hosts_live', '--path', os.path.join(H, 'summary_hosts.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
with open('history.jsonl', 'a') as f: f.write(json.dumps(dict(t=out['updated'], endpoints=len(eps), problems=len(problems), failed=len(failed))) + '\n')
print('hosts:', out['top_line'], 'test', out['headline']['outcome'], 'published' if pr.returncode == 0 else 'publish FAILED', flush=True)
# 10 Nov 2026 (cold read row 5): rebuild the headlines from this read now, so the headline and the page body come from the same read
try: subprocess.Popen([sys.executable, '-I', os.path.expanduser('~/bones-forge/watch/headlines.py')], stdout=open(os.path.expanduser('~/bones-forge/watch/novatime_jobs.log'), 'a'), stderr=subprocess.STDOUT, start_new_session=True)
except Exception as e: print('headlines restart failed', type(e).__name__)
