"""send_guarded.py (5 Nov 2026, Wayfinder: "be careful and try not to flag us"). Sends queue.jsonl through Cloudflare Email Sending
(heuremen.com: DKIM, SPF and DMARC pass, bounces return to cf-bounce.heuremen.com, never to the Gmail mailbox), one email at a time.
Guards: --cap N emails this run (default 60); 25-75 s apart; after every 20 sends, reads Cloudflare's own delivery records for today and
STOPS if more than 2 of the last 20 bounced; stops on throttle, auth failure or any error (no retry through a throttle).
Progress in sent.progress (key per line, never re-sent), log in send.log. Run: python3 -I send_guarded.py [--cap N] [--dry]"""
import json, os, random, re, subprocess, sys, time, urllib.request, datetime as D
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door')
CAP = int(sys.argv[sys.argv.index('--cap') + 1]) if '--cap' in sys.argv else 60; DRY = '--dry' in sys.argv
PROG, LOG = H + '/sent.progress', H + '/send.log'
done = set(open(PROG).read().split()) if os.path.exists(PROG) else set()
todo = [it for it in (json.loads(l) for l in open(H + '/queue.jsonl')) if it['key'] not in done]
HOLD = json.load(open(H + '/PREFLIGHT_HOLD.json')) if os.path.exists(H + '/PREFLIGHT_HOLD.json') else {}   # 6 Nov: preflight.py holds (bounced / no mail server / already sent)
todo = [it for it in todo if it['key'] not in HOLD]
def log(s):
    with open(LOG, 'a') as f: f.write(time.strftime('%Y-%m-%d %H:%M:%S ') + s + '\n')
def statuses(addrs):
    subprocess.run(['npx', 'wrangler', 'whoami'], cwd=W, capture_output=True, timeout=120)   # refreshes the hour-long sign-in token
    tok = re.search(r'oauth_token\s*=\s*"([^"]+)"', open(os.path.expanduser('~/Library/Preferences/.wrangler/config/default.toml')).read()).group(1)
    def api(u, b=None):
        r = urllib.request.Request(u, data=json.dumps(b).encode() if b else None, headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json'})
        return json.load(urllib.request.urlopen(r, timeout=60))
    z = api('https://api.cloudflare.com/client/v4/zones?name=heuremen.com')['result'][0]['id']
    s = D.datetime.now(D.timezone.utc).strftime('%Y-%m-%dT00:00:00Z'); e = D.datetime.now(D.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    q = 'query($z: string!, $s: Time!, $e: Time!) { viewer { zones(filter: {zoneTag: $z}) { emailSendingAdaptive(filter: {datetime_geq: $s, datetime_leq: $e}, limit: 10000) { to status errorDetail } } } }'
    for _ in range(2):   # the analytics API has a rolling query budget: wait 5 min and try once more
        res = api('https://api.cloudflare.com/client/v4/graphql', {'query': q, 'variables': {'z': z, 's': s, 'e': e}})
        if res.get('data'): break
        time.sleep(310)
    ev = res['data']['viewer']['zones'][0]['emailSendingAdaptive']
    st = {}
    for x in ev:
        for a in x['to'].split(','): st[a.strip().lower()] = (x['status'], (x.get('errorDetail') or '')[:120])
    return {a: st.get(a, ('no record yet', '')) for a in addrs}
print(f'{len(todo)} left in the queue; this run sends at most {CAP}'); recent = []
for n, it in enumerate(todo[:CAP], 1):
    to = it['to']
    if DRY: print('DRY', it['key'], to, it['subject'][:80]); continue
    cmd = ['npx', 'wrangler', 'email', 'sending', 'send', '--from', 'Indahl@heuremen.com', '--from-name', 'K. Indahl', '--subject', it['subject'], '--text', it['body']]
    for a in to: cmd += ['--to', a]
    r = subprocess.run(cmd, cwd=W, capture_output=True, text=True, timeout=120); out = re.sub(r'\x1b\[[0-9;]*m', '', r.stdout + r.stderr)
    if 'Authentication error' in out:
        subprocess.run(['npx', 'wrangler', 'whoami'], cwd=W, capture_output=True, timeout=120); time.sleep(5)
        r = subprocess.run(cmd, cwd=W, capture_output=True, text=True, timeout=120); out = re.sub(r'\x1b\[[0-9;]*m', '', r.stdout + r.stderr)
    if r.returncode == 0 and 'Queued for' in out:
        with open(PROG, 'a') as f: f.write(it['key'] + '\n')
        log(f'ok {it["key"]} {",".join(to)}'); recent += to
    else:
        err = ' '.join(l.strip() for l in out.splitlines() if 'email.sending' in l or 'ERROR' in l or 'code:' in l)[:300]
        log(f'STOPPED {it["key"]} {",".join(to)} {err}'); print('STOPPED at', it['key'], err); sys.exit(2)
    if n % 20 == 0:
        time.sleep(90)
        try: st = statuses(recent[-20:])
        except Exception as ex: log(f'STOPPED: delivery check failed ({ex})'); print('STOPPED: delivery check failed', ex); sys.exit(4)
        bad = {a: v for a, v in st.items() if v[0] not in ('delivered', 'no record yet', 'queued', 'sent', 'pending')}
        log(f'CHECK last 20: ' + json.dumps({k: sum(1 for v in st.values() if v[0] == k) for k in {v[0] for v in st.values()}}) + (f' bad {json.dumps(bad)[:400]}' if bad else ''))
        if len(bad) > 2: print('STOPPED: more than 2 of the last 20 bounced', bad); log('STOPPED on bounce guard'); sys.exit(3)
    time.sleep(random.uniform(25, 75))
log(f'run end: {min(CAP, len(todo))} sent this run') if not DRY else print('dry run: nothing sent, nothing logged'); print('run end')
