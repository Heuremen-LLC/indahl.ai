#!/usr/bin/env python3
"""uptime_tick.py: one UPTIME round for the HST tick bus. Probe from this Mac, from the Pi, pull the runner seat's saved rounds, ask the runner for the next, score, publish."""
import os, subprocess, sys, json, urllib.request
import os as _pg_os, sys as _pg_sys, subprocess as _pg_sp   # 10 Nov 2026 (publish guard): the site KV is written only by a run the tick bus or the house clock started
_PUBLISH = '--publish' in _pg_sys.argv or _pg_os.environ.get('HEUREMEN_PUBLISH') == '1'   # (they export HEUREMEN_PUBLISH=1) or a run given --publish. A copy run for a reproduce kit or a test never publishes
if _PUBLISH: _pg_os.environ['HEUREMEN_PUBLISH'] = '1'   # passed on to the scripts this one starts, and kept across a detach or re-exec
def _kv_put(cmd, **kw):
    if _PUBLISH: return _pg_sp.run(cmd, **kw)
    print('publish guard: %s not put to the site KV (run with --publish, or from the tick bus)' % cmd[5], file=_pg_sys.stderr)
    return _pg_sp.CompletedProcess(cmd, 0, '' if kw.get('text') or kw.get('universal_newlines') else b'', '' if kw.get('text') or kw.get('universal_newlines') else b'')
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'); os.chdir(H)
def sh(c, to=240): return subprocess.run(c, capture_output=True, text=True, timeout=to)
sh([sys.executable, 'status_probe.py', 'mac', 'data/probe_mac.jsonl'])
try:
    sh(['ssh', '-o', 'ConnectTimeout=10', 'flock-pi', 'cd status_index && python3 status_probe.py pi data/probe_pi.jsonl >/dev/null && tail -n 12000 data/probe_pi.jsonl > data/pi.tmp && mv data/pi.tmp data/probe_pi.jsonl']); sh(['scp', '-q', 'flock-pi:status_index/data/probe_pi.jsonl', 'data/probe_pi.jsonl'])
except Exception as e: print('pi step', type(e).__name__)
try:
    urllib.request.urlretrieve('https://raw.githubusercontent.com/Heuremen-LLC/nodes/main/data/status/rounds.jsonl', 'data/probe_runner.jsonl')
    sh(['/opt/homebrew/bin/gh', 'api', 'repos/Heuremen-LLC/nodes/dispatches', '-f', 'event_type=status-probe'], 60)
except Exception as e: print('runner step', type(e).__name__)
# incidents (latest three per vendor) from the same status APIs, mac side
inc = {}
for v in json.load(open('vendors.json')):
    if not v.get('status'): continue
    try:
        d = json.loads(urllib.request.urlopen(urllib.request.Request(v['status'] + '/api/v2/incidents.json', headers={'User-Agent': 'heuremen-uptime/0.1 (+https://indahl.ai/uptime)'}), timeout=15).read())
        inc[v['name']] = [dict(name=i['name'], impact=i['impact'], started=i['created_at'], resolved=i.get('resolved_at')) for i in d['incidents'][:3]]
    except Exception: pass
json.dump(inc, open('incidents.json', 'w'))
sh([sys.executable, 'uptime_summary.py'], 120)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
p = _kv_put(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'uptime_live', '--path', os.path.join(H, 'summary_uptime.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
print('uptime_live published' if p.returncode == 0 else 'uptime_live publish FAILED')
